"""M7.5 - Cotacoes Blueprint CONFORME PROMPT MESTRE"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Ativo
from app.services.cotacoes_service import CotacoesService
from datetime import datetime, timedelta
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
                    'ticker': ticker,
                    'preco_atual': float(ativo.preco_atual or 0),
                    'dy_12m': float(ativo.dividend_yield or 0),
                    'pl': float(ativo.p_l or 0),
                    'provider': 'database_cache',
                    'cache_age_minutes': int(delta.total_seconds() / 60),
                    'cache_valid_until': (ativo.data_ultima_cotacao + timedelta(seconds=TTL_SECONDS)).isoformat(),
                    'success': True
                })
        
        # Cache expirou OU primeira consulta → Buscar API externa
        logger.info(f"📡 Buscando {ticker} via API externa (cache expirado ou inexistente)")
        cotacao = CotacoesService.obter_cotacao(ticker, ativo.mercado)
        
        if cotacao.get('success'):
            # Atualizar banco
            ativo.preco_atual = cotacao['preco_atual']
            ativo.dividend_yield = cotacao.get('dy_12m', ativo.dividend_yield or 0)
            ativo.p_l = cotacao.get('pl', ativo.p_l or 0)
            ativo.data_ultima_cotacao = now
            db.session.commit()
            
            logger.info(f"✅ {ticker}: R${cotacao['preco_atual']} via {cotacao['provider']}")
            cotacao['cache_ttl_minutes'] = 15
            return jsonify(cotacao)
        
        # Fallback: usar dados antigos (mesmo se > 15min)
        logger.warning(f"⚠️ APIs falharam {ticker} - usando dados antigos do banco")
        return jsonify({
            'ticker': ticker,
            'preco_atual': float(ativo.preco_atual or 0),
            'dy_12m': float(ativo.dividend_yield or 0),
            'pl': float(ativo.p_l or 0),
            'provider': 'database_fallback',
            'warning': 'APIs indisponíveis - dados podem estar desatualizados',
            'last_update': ativo.data_ultima_cotacao.isoformat() if ativo.data_ultima_cotacao else None,
            'success': True
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
            # Reusar lógica individual
            resp = obter_cotacao(ticker)
            resultados[ticker] = resp[0].get_json()
        except Exception as e:
            logger.error(f"❌ Batch {ticker}: {e}")
            resultados[ticker] = {'error': str(e), 'success': False}
    
    return jsonify(resultados)

@cotacoes_bp.route('/health', methods=['GET'])
def cotacoes_health():
    return jsonify({
        'status': 'ok',
        'module': 'cotacoes_m7.5',
        'cache_ttl': '15 minutos (Prompt Mestre)',
        'providers': ['brapi.dev (FREE tier)', 'yfinance', 'alphavantage', 'database_cache'],
        'update_trigger': 'on_demand (somente quando usuário acessa tela)'
    })
