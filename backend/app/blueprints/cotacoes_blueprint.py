"""M7.5 - Cotacoes Blueprint CONFORME PROMPT MESTRE"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Ativo
from app.services.cotacoes_service import CotacoesService
from app.services.anomaly_service import AnomalyService
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
cotacoes_bp = Blueprint('cotacoes', __name__, url_prefix='/api/cotacoes')

@cotacoes_bp.route('/<ticker>', methods=['GET'])
@jwt_required()
def obter_cotacao(ticker):
    """
    PROMPT MESTRE: Dados com atraso até 15min
    SÓ atualiza quando usuário acessa tela + última atualização > 15min
    """
    try:
        ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
        if not ativo:
            return jsonify({'error': f'Ativo {ticker} não encontrado'}), 404
        
        # TTL 15 MINUTOS conforme Prompt Mestre
        TTL_SECONDS = 900  # 15min
        now = datetime.now()
        
        # Se última atualização < 15min, usar dados do banco (SEM chamar API)
        if ativo.data_ultima_cotacao:
            delta = now - ativo.data_ultima_cotacao.replace(tzinfo=None)
            if delta.total_seconds() < TTL_SECONDS:
                logger.info(f"✅ Cache {ticker} válido ({int(delta.total_seconds()/60)}min atrás)")
                return jsonify({
                    'success': True,
                    'data': {
                        'ticker': ticker,
                        'preco_atual': float(ativo.preco_atual or 0),
                        'dy_12m': float(ativo.dividend_yield or 0),
                        'pl': float(ativo.p_l or 0),
                        'provider': 'database_cache',
                        'cache_age_minutes': int(delta.total_seconds() / 60),
                        'cache_valid_until': (ativo.data_ultima_cotacao + timedelta(seconds=TTL_SECONDS)).isoformat(),
                    },
                    'message': f'Cotação {ticker} (cache)'
                })
        
        # Cache expirou OU primeira consulta → Buscar API externa
        logger.info(f"📡 Buscando {ticker} via API externa (cache expirado ou inexistente)")
        cotacao = CotacoesService.obter_cotacao(ticker, ativo.mercado)
        
        if cotacao.get('success'):
            preco_novo = cotacao['preco_atual']
            # Verificar anomalia antes de persistir (ANOMALY-001)
            anomalia = None
            if ativo.preco_atual and ativo.preco_atual > 0:
                anomalia = AnomalyService.verificar_ativo(
                    ativo_id=ativo.id,
                    preco_novo=Decimal(str(preco_novo)),
                    data_novo=date.today(),
                )

            # Atualizar banco
            ativo.preco_atual = preco_novo
            ativo.dividend_yield = cotacao.get('dy_12m', ativo.dividend_yield or 0)
            ativo.p_l = cotacao.get('pl', ativo.p_l or 0)
            ativo.data_ultima_cotacao = now
            db.session.commit()

            logger.info(f"✅ {ticker}: R${preco_novo} via {cotacao['provider']}")
            cotacao.pop('success', None)
            cotacao['cache_ttl_minutes'] = 15
            if anomalia:
                cotacao['anomalia'] = anomalia
            return jsonify({'success': True, 'data': cotacao, 'message': f'Cotação {ticker} atualizada'})
        
        # Fallback: usar dados antigos (mesmo se > 15min)
        logger.warning(f"⚠️ APIs falharam {ticker} - usando dados antigos do banco")
        return jsonify({
            'success': True,
            'data': {
                'ticker': ticker,
                'preco_atual': float(ativo.preco_atual or 0),
                'dy_12m': float(ativo.dividend_yield or 0),
                'pl': float(ativo.p_l or 0),
                'provider': 'database_fallback',
                'warning': 'APIs indisponíveis - dados podem estar desatualizados',
                'last_update': ativo.data_ultima_cotacao.isoformat() if ativo.data_ultima_cotacao else None,
            },
            'message': f'Cotação {ticker} (fallback - dados podem estar desatualizados)'
        })
    
    except Exception as e:
        logger.error(f"❌ Erro {ticker}: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@cotacoes_bp.route('/batch', methods=['GET'])
@jwt_required()
def cotacoes_batch():
    """Batch com TTL 15min por ativo"""
    tickers = request.args.get('symbols', 'PETR4,VALE3').split(',')
    resultados = {}

    for ticker in tickers[:10]:
        ticker = ticker.strip().upper()
        try:
            # ✅ CORRETO: Chamar service diretamente
            ativo = Ativo.query.filter_by(ticker=ticker).first()
            if not ativo:
                resultados[ticker] = {
                    'error': f'Ativo {ticker} não encontrado',
                    'success': False
                }
                continue
            
            # Usar lógica do service
            cotacao = CotacoesService.obter_cotacao(ticker, ativo.mercado)
            resultados[ticker] = cotacao
            
        except Exception as e:
            logger.error(f"❌ Batch {ticker}: {e}")
            resultados[ticker] = {'error': str(e), 'success': False}

    return jsonify(resultados)


@cotacoes_bp.route('/anomalias', methods=['GET'])
@jwt_required()
def listar_anomalias():
    """
    ANOMALY-001: Detecção on-demand de preços anômalos.

    Query params:
      limiar   — percentual mínimo de variação (padrão: 20). Ex: ?limiar=15
      ativo_id — filtrar por ativo específico (UUID)
      data_ref — data de referência ISO (padrão: hoje). Ex: ?data_ref=2025-03-01
    """
    try:
        limiar_raw = request.args.get('limiar', '20')
        try:
            limiar = Decimal(str(limiar_raw)) / 100
            if limiar <= 0 or limiar > 10:
                return jsonify({'success': False, 'error': 'limiar deve estar entre 0 e 1000%'}), 400
        except Exception:
            return jsonify({'success': False, 'error': 'limiar inválido'}), 400

        ativo_id = request.args.get('ativo_id')

        data_ref_raw = request.args.get('data_ref')
        data_ref = None
        if data_ref_raw:
            try:
                data_ref = date.fromisoformat(data_ref_raw)
            except ValueError:
                return jsonify({'success': False, 'error': 'data_ref inválida (use YYYY-MM-DD)'}), 400

        anomalias = AnomalyService.detectar_anomalias(
            limiar=limiar,
            ativo_id=ativo_id,
            data_ref=data_ref,
        )

        return jsonify({
            'success': True,
            'data': {
                'anomalias':  anomalias,
                'total':      len(anomalias),
                'limiar_pct': float(limiar * 100),
                'data_ref':   (data_ref or date.today()).isoformat(),
            },
            'message': f'{len(anomalias)} anomalia(s) detectada(s)',
        })

    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@cotacoes_bp.route('/health', methods=['GET'])
def cotacoes_health():
    return jsonify({
        'status': 'ok',
        'module': 'cotacoes_m7.5',
        'cache_ttl': '15 minutos (Prompt Mestre)',
        'providers': ['brapi.dev (FREE tier)', 'yfinance', 'alphavantage', 'database_cache'],
        'update_trigger': 'on_demand (somente quando usuário acessa tela)',
        'anomaly_detection': 'EXITUS-ANOMALY-001 — GET /api/cotacoes/anomalias',
    })
