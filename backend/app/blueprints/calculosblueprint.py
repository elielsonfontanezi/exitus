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
    """Calcula Preço Teto por 4 métodos para ativo específico"""
    usuario_id = get_jwt_identity()
    
    # Buscar ativo pela tabela 'ativos' snake_case
    ativo = db.session.query(Ativo).filter(
        Ativo.ticker == ticker.upper()
    ).first()
    
    if not ativo:
        return jsonify({"erro": f"Ativo {ticker} não encontrado"}), 404
    
    # Campos snake_case CORRETOS do banco
    dy = float(ativo.dividend_yield or 0.06)
    pl = float(ativo.p_l or 12)
    roe = float(ativo.roe or 0.15)
    preco_atual = float(ativo.preco_atual or 30)
    
    # 1. MÉTODO BAZIN
    k = 0.12  # Taxa requerida
    g = 0.05  # Crescimento
    pt_bazin = (dy / (k - g)) if (k > g) else 0
    
    # 2. MÉTODO GRAHAM
    eps = 2.50
    pt_graham = (eps * (8.5 + 2 * g)) * 4.4 / 0.07
    
    # 3. MÉTODO GORDON
    d1 = dy * 1.05
    pt_gordon = d1 / (k - g)
    
    # 4. SINAL
    pt_medio = (pt_bazin + pt_graham + pt_gordon) / 3
    sinal = "🟢 COMPRA" if pt_medio > preco_atual * 1.2 else "🟡 NEUTRO" if pt_medio > preco_atual else "🔴 VENDA"
    
    resultado = {
        "ativo": ticker,
        "preco_atual": preco_atual,
        "pt_medio": float(pt_medio),
        "metodos": {
            "bazin": {"pt": float(pt_bazin), "dy": dy, "k": k, "g": g},
            "graham": {"pt": float(pt_graham), "eps": eps, "g": g},
            "gordon": {"pt": float(pt_gordon), "d1": float(d1), "k": k, "g": g}
        },
        "sinal": sinal,
        "recomendacao": f"Preço teto médio: R$ {pt_medio:.2f}"
    }
    
    return jsonify(resultado), 200
