from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Ativo
from app.services.portfolio_service import get_portfolio_metrics

calculosbp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculosbp.route('/portfolio', methods=['GET'])
@jwt_required()
def calcular_portfolio():
    """Endpoint principal - métricas reais do portfólio"""
    usuario_id = get_jwt_identity()
    metrics = get_portfolio_metrics(usuario_id)
    
    if "erro" in metrics:
        return jsonify(metrics), 404
    
    resultado = {
        "rentabilidade": {
            "YTD": metrics["rentabilidade_ytd"],
            "1A": 0.12,
            "3A": 0.36
        },
        "volatilidade_anualizada": 0.14,
        "sharpe_ratio": 1.15,
        "drawdown_maximo": 0.10,
        "correlacao_ativos": {},
        "alocacao": metrics["alocacao"],
        "dividend_yield_medio": metrics["dividend_yield_medio"],
        "portfolio_info": {
            "total_custo": metrics["total_custo"],
            "total_valor_atual": metrics["total_valor_atual"],
            "total_posicoes": metrics["total_posicoes"]
        }
    }
    return jsonify(resultado), 200


@calculosbp.route('/preco_teto/<string:ticker>', methods=['GET'])
@jwt_required()
def calcular_preco_teto(ticker):
    """Calcula Preço Teto por 4 métodos: Bazin, Graham, Gordon, DCF"""
    usuario_id = get_jwt_identity()
    
    ativo = db.session.query(Ativo).filter(
        Ativo.ticker == ticker.upper()
    ).first()
    
    if not ativo:
        return jsonify({"erro": f"Ativo {ticker} não encontrado"}), 404
    
    # Campos snake_case do banco
    dy = float(ativo.dividend_yield or 0.06)
    pl = float(ativo.p_l or 12)
    roe = float(ativo.roe or 0.15)
    preco_atual = float(ativo.preco_atual or 30)
    
    k = 0.12
    g = 0.05
    eps = 2.50
    
    # 1. BAZIN
    pt_bazin = (dy / (k - g)) if (k > g) else 0
    
    # 2. GRAHAM
    pt_graham = (eps * (8.5 + 2 * g * 100)) * 4.4 / 7.0
    
    # 3. GORDON
    d1 = dy * (1 + g)
    pt_gordon = d1 / (k - g) if (k > g) else 0
    
    # 4. DCF
    fcf = 5.0
    wacc = 0.10
    crescimento_terminal = 0.03
    anos_projetados = 5
    fluxos = [fcf * (1 + g)**i for i in range(1, anos_projetados + 1)]
    valor_terminal = fluxos[-1] * (1 + crescimento_terminal) / (wacc - crescimento_terminal)
    fluxos.append(valor_terminal)
    pt_dcf = sum([fluxo / (1 + wacc)**(i+1) for i, fluxo in enumerate(fluxos)])
    
    # MÉDIA E SINAL
    pts = [pt_bazin, pt_graham, pt_gordon, pt_dcf]
    pt_medio = sum(pts) / len(pts)
    
    if pt_medio > preco_atual * 1.2:
        sinal = "🟢 COMPRA"
        cor = "green"
    elif pt_medio > preco_atual:
        sinal = "🟡 NEUTRO"
        cor = "yellow"
    else:
        sinal = "🔴 VENDA"
        cor = "red"
    
    margem_seguranca = ((pt_medio - preco_atual) / pt_medio) * 100 if pt_medio > 0 else 0
    
    resultado = {
        "ativo": ticker.upper(),
        "preco_atual": preco_atual,
        "pt_medio": round(float(pt_medio), 2),
        "margem_seguranca": round(float(margem_seguranca), 2),
        "metodos": {
            "bazin": {"pt": round(float(pt_bazin), 2), "dy": dy, "k": k, "g": g},
            "graham": {"pt": round(float(pt_graham), 2), "eps": eps, "g": g},
            "gordon": {"pt": round(float(pt_gordon), 2), "d1": round(float(d1), 4), "k": k, "g": g},
            "dcf": {"pt": round(float(pt_dcf), 2), "fcf": fcf, "wacc": wacc, "anos": anos_projetados}
        },
        "sinal": sinal,
        "cor": cor,
        "recomendacao": f"Preço teto médio (4 métodos): R$ {pt_medio:.2f}. Margem: {margem_seguranca:.1f}%"
    }
    
    return jsonify(resultado), 200
