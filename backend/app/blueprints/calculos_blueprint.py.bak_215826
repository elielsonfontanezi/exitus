from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Ativo
#from app.services.portfolio_service import get_portfolio_metrics
from app.services.portfolio_service import PortfolioService
from app.services.parametros_macro_service import get_parametros_macro

calculosbp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculosbp.route('/portfolio', methods=['GET'])
@jwt_required()
def calcular_portfolio():
    """Endpoint principal - métricas reais + AVANÇADAS do portfólio"""
    usuario_id = get_jwt_identity()
    #metrics = get_portfolio_metrics(usuario_id)
    metrics = PortfolioService.get_portfolio_metrics(usuario_id)

    if "erro" in metrics:
        return jsonify(metrics), 404

    resultado = {
        "portfolio_info": metrics["portfolio_info"],
        "rentabilidade": {
            "YTD": metrics["rentabilidade_ytd"],
            "1A": 0.12,
            "3A": 0.36
        },
        "alocacao": metrics["alocacao"],
        "dividend_yield_medio": metrics["dividend_yield_medio"],
        "risco": {
            "volatilidade_anualizada": round(metrics["volatilidade_anualizada"], 4),
            "sharpe_ratio": round(metrics["sharpe_ratio"], 2),
            "max_drawdown": f"{metrics['max_drawdown']*100:.1f}%",
            "beta_ibov": round(metrics["beta_ibov"], 2)
        },
        "correlacao_ativos": metrics["correlacao_ativos"]
    }
    return jsonify(resultado), 200


@calculosbp.route('/preco_teto/<string:ticker>', methods=['GET'])
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
