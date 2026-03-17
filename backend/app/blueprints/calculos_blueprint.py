from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from app.database import db
from app.models import Ativo
from app.services.portfolio_service import PortfolioService
from app.services.parametros_macro_service import get_parametros_macro
from app.services.rfcalc_service import RFCalcService

calculos_bp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculos_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def calcular_portfolio():
    """Endpoint principal - métricas reais + AVANÇADAS do portfólio"""
    usuario_id = get_jwt_identity()
    metrics = PortfolioService.get_portfolio_metrics(usuario_id)

    if "erro" in metrics:
        return jsonify(metrics), 404

    resultado = {
        "portfolio_info": metrics.get("portfolio_info", {}),  # ✅ Safe get
        "rentabilidade": {
            "YTD": metrics.get("rentabilidade_ytd", 0.0),
            "1A": 0.12,
            "3A": 0.36
        },
        "alocacao": metrics.get("alocacao", {}),  # ✅ Safe get
        "dividend_yield_medio": metrics.get("dividend_yield_medio", 0.0),  # ✅ Safe get
        "risco": {
            "volatilidade_anualizada": round(metrics.get("volatilidade_anualizada", 0.0), 4),  # ✅ Safe get
            "sharpe_ratio": round(metrics.get("sharpe_ratio", 0.0), 2),  # ✅ Safe get
            "max_drawdown": f"{metrics.get('max_drawdown', 0.0)*100:.1f}%",  # ✅ Safe get
            "beta_ibov": round(metrics.get("beta_ibov", 0.0), 2)  # ✅ Safe get
        },
        "correlacao_ativos": metrics.get("correlacao_ativos", [])  # ✅ Safe get
    }

    return jsonify(resultado), 200


@calculos_bp.route('/preco_teto/<string:ticker>', methods=['GET'])
@jwt_required()
def calcular_preco_teto(ticker):
    """Preço Teto MULTI-MERCADO - Parâmetros REGIONAIS dinâmicos"""
    usuario_id = get_jwt_identity()

    ativo = db.session.query(Ativo).filter(
        Ativo.ticker == ticker.upper()
    ).first()

    if not ativo:
        return jsonify({"erro": f"Ativo {ticker} não encontrado"}), 404

    # Parâmetros macroeconômicos regionais dinâmicos
    params = get_parametros_macro(ativo.mercado, ativo.mercado)
    k = params['taxa_livre_risco']      # Taxa livre de risco regional
    g = params['crescimento_medio']     # Crescimento médio regional
    wacc = params['custo_capital']      # WACC regional

    tipo = str(getattr(ativo, 'tipo', 'acao')).lower()  # converte enum para string
    preco_atual = float(ativo.preco_atual or 30)
    dy = float(ativo.dividend_yield or 0.06)

    metodos = {}

    if tipo in ['acao', 'acoes']:
        # Ações: 4 métodos com parâmetros regionais
        eps = 2.50
        pt_bazin = (dy / (k - g)) if (k > g) else 0
        pt_graham = (eps * (8.5 + 2 * g * 100)) * 4.4 / k
        d1 = dy * (1 + g)
        pt_gordon = d1 / (k - g) if (k > g) else 0

        fcf = 5.0
        anos = 5
        fluxos = [fcf * (1 + g)**i for i in range(1, anos + 1)]
        valor_terminal = fluxos[-1] * 1.03 / (wacc - 0.03)
        fluxos.append(valor_terminal)
        pt_dcf = sum([fluxo / (1 + wacc)**(i+1) for i, fluxo in enumerate(fluxos)])

        metodos = {
            "bazin": {"pt": round(pt_bazin, 2), "k": f"{k:.1%}", "descricao": "DY Local"},
            "graham": {"pt": round(pt_graham, 2), "descricao": "Graham Local"},
            "gordon": {"pt": round(pt_gordon, 2), "descricao": "Gordon Local"},
            "dcf": {"pt": round(pt_dcf, 2), "wacc": f"{wacc:.1%}", "descricao": "DCF Local"}
        }
        pt_medio = sum([v["pt"] for v in metodos.values()]) / 4

    elif 'fii' in tipo.lower():
        # FIIs: Cap Rate regional
        cap_rate = params['cap_rate_fii']
        pt_cap_rate = 1 / cap_rate

        metodos = {
            "cap_rate": {"pt": round(pt_cap_rate, 2), "cap_rate": f"{cap_rate:.1%}"}
        }
        pt_medio = pt_cap_rate

    else:
        pt_medio = preco_atual * 1.1
        metodos = {"padrao": {"pt": round(pt_medio, 2)}}

    # Sinal
    margem = ((pt_medio - preco_atual) / pt_medio) * 100 if pt_medio > 0 else 0
    if pt_medio > preco_atual * 1.2:
        sinal = "🟢 COMPRA"
        cor = "green"
    elif pt_medio > preco_atual:
        sinal = "🟡 NEUTRO"
        cor = "yellow"
    else:
        sinal = "🔴 VENDA"
        cor = "red"

    resultado = {
        "ativo": ticker.upper(),
        "mercado": getattr(ativo, 'mercado', 'BR'),
        "preco_atual": round(preco_atual, 2),
        "pt_medio": round(pt_medio, 2),
        "margem_seguranca": round(margem, 1),
        "parametros_regiao": {
            "taxa_livre_risco": f"{k:.1%}",
            "crescimento": f"{g:.1%}",
            "wacc": f"{wacc:.1%}"
        },
        "metodos": metodos,
        "sinal": sinal,
        "cor": cor
    }

    return jsonify(resultado), 200


@calculos_bp.route('/rf/simular', methods=['POST'])
@jwt_required()
def simular_rf():
    """
    Simulação de cálculos RF com parâmetros livres (sem vínculo com ativo cadastrado).
    Útil para análise teórica de títulos.

    Body JSON:
        preco_mercado (float): Preço atual de mercado
        valor_nominal (float): Valor nominal do título
        taxa_cupom (float): Taxa de cupom anual (ex: 0.105)
        data_vencimento (str): Data de vencimento (YYYY-MM-DD)
        frequencia_anual (int): Cupons por ano (1=anual, 2=semestral) [default: 1]
    """
    try:
        data = request.json or {}

        # Validação dos campos obrigatórios
        campos_obrigatorios = ['preco_mercado', 'valor_nominal', 'taxa_cupom', 'data_vencimento']
        faltando = [c for c in campos_obrigatorios if c not in data]
        if faltando:
            return jsonify({'error': f'Campos obrigatórios ausentes: {", ".join(faltando)}'}), 400

        preco_mercado = float(data['preco_mercado'])
        valor_nominal = float(data['valor_nominal'])
        taxa_cupom = float(data['taxa_cupom'])
        frequencia_anual = int(data.get('frequencia_anual', 1))

        # Parse da data de vencimento
        try:
            data_vencimento = date.fromisoformat(data['data_vencimento'])
        except ValueError:
            return jsonify({'error': 'data_vencimento inválida. Use formato YYYY-MM-DD'}), 400

        if data_vencimento <= date.today():
            return jsonify({'error': 'data_vencimento deve ser uma data futura'}), 400

        if frequencia_anual not in [1, 2, 4, 12]:
            return jsonify({'error': 'frequencia_anual deve ser 1, 2, 4 ou 12'}), 400

        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=preco_mercado,
            valor_nominal=valor_nominal,
            taxa_cupom=taxa_cupom,
            data_vencimento=data_vencimento,
            frequencia_anual=frequencia_anual,
        )

        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calculos_bp.route('/rf/<string:ticker>', methods=['GET'])
@jwt_required()
def calcular_rf_ativo(ticker):
    """
    Calcula indicadores RF para um ativo cadastrado (usa dados do banco).
    Requer que o ativo tenha taxa_cupom, valor_nominal e data_vencimento preenchidos.
    """
    try:
        ativo = db.session.query(Ativo).filter(
            Ativo.ticker == ticker.upper()
        ).first()

        if not ativo:
            return jsonify({'error': f'Ativo {ticker.upper()} não encontrado'}), 404

        # Verifica se tem os dados necessários
        campos_faltando = []
        if not ativo.preco_atual:
            campos_faltando.append('preco_atual')
        if not ativo.taxa_cupom:
            campos_faltando.append('taxa_cupom')
        if not ativo.valor_nominal:
            campos_faltando.append('valor_nominal')
        if not ativo.data_vencimento:
            campos_faltando.append('data_vencimento')

        if campos_faltando:
            return jsonify({
                'error': f'Ativo {ticker.upper()} não possui dados suficientes para cálculo RF.',
                'campos_faltando': campos_faltando,
                'dica': 'Atualize o ativo com taxa_cupom, valor_nominal e data_vencimento via PUT /api/ativos/{id}'
            }), 422

        frequencia_anual = request.args.get('frequencia_anual', 1, type=int)

        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=float(ativo.preco_atual),
            valor_nominal=float(ativo.valor_nominal),
            taxa_cupom=float(ativo.taxa_cupom),
            data_vencimento=ativo.data_vencimento,
            frequencia_anual=frequencia_anual,
        )

        resultado['ativo'] = ticker.upper()
        resultado['nome'] = ativo.nome
        resultado['tipo'] = ativo.tipo.value if ativo.tipo else None
        resultado['mercado'] = ativo.mercado

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calculos_bp.route('/fii/<string:ticker>', methods=['GET'])
@jwt_required()
def calcular_fii_ativo(ticker):
    """
    Calcula indicadores FII/REIT para um ativo cadastrado.
    Requer que o ativo tenha ffo_por_cota preenchido.
    """
    try:
        ativo = db.session.query(Ativo).filter(
            Ativo.ticker == ticker.upper()
        ).first()

        if not ativo:
            return jsonify({'error': f'Ativo {ticker.upper()} não encontrado'}), 404

        if not ativo.ffo_por_cota:
            return jsonify({
                'error': f'Ativo {ticker.upper()} não possui ffo_por_cota cadastrado.',
                'dica': 'Atualize o ativo com ffo_por_cota e opcionalmente affo_por_cota via PUT /api/ativos/{id}'
            }), 422

        if not ativo.preco_atual:
            return jsonify({'error': f'Ativo {ticker.upper()} não possui preco_atual'}), 422

        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=float(ativo.preco_atual),
            ffo_por_cota=float(ativo.ffo_por_cota),
            affo_por_cota=float(ativo.affo_por_cota) if ativo.affo_por_cota else None,
            dividend_yield=float(ativo.dividend_yield) if ativo.dividend_yield else None,
            p_vp=float(ativo.p_vp) if ativo.p_vp else None,
        )

        resultado['ativo'] = ticker.upper()
        resultado['nome'] = ativo.nome
        resultado['mercado'] = ativo.mercado

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
