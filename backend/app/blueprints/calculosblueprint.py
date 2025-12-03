from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Ativo
from app.services.portfolio_service import get_portfolio_metrics

calculosbp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculosbp.route('/portfolio', methods=['GET'])
@jwt_required()
def calcular_portfolio():
    """Endpoint principal - métricas reais + AVANÇADAS do portfólio"""
    usuario_id = get_jwt_identity()
    metrics = get_portfolio_metrics(usuario_id)
    
    if "erro" in metrics:
        return jsonify(metrics), 404
    
    # Estrutura completa com métricas avançadas
    resultado = {
        "portfolio_info": metrics["portfolio_info"],
        "rentabilidade": {
            "YTD": metrics["rentabilidade_ytd"],
            "1A": 0.12,  # Futuro: histórico real
            "3A": 0.36   # Futuro: histórico real
        },
        "alocacao": metrics["alocacao"],
        "dividend_yield_medio": metrics["dividend_yield_medio"],
        # MÉTRICAS DE RISCO AVANÇADAS
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
    """Calcula Preço Teto por 4 métodos: Bazin, Graham, Gordon, DCF"""
    usuario_id = get_jwt_identity()
    
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
    
    # Parâmetros de cálculo
    k = 0.12  # Taxa requerida
    g = 0.05  # Crescimento
    eps = 2.50  # EPS (futuro: real)
    
    # 1. MÉTODO BAZIN
    pt_bazin = (dy / (k - g)) if (k > g) else 0
    
    # 2. MÉTODO GRAHAM
    pt_graham = (eps * (8.5 + 2 * g * 100)) * 4.4 / 7.0
    
    # 3. MÉTODO GORDON
    d1 = dy * (1 + g)
    pt_gordon = d1 / (k - g) if (k > g) else 0
    
    # 4. MÉTODO DCF SIMPLIFICADO
    fcf = 5.0  # Free Cash Flow
    wacc = 0.10  # Custo médio de capital
    crescimento_terminal = 0.03
    anos_projetados = 5
    
    fluxos = [fcf * (1 + g)**i for i in range(1, anos_projetados + 1)]
    valor_terminal = fluxos[-1] * (1 + crescimento_terminal) / (wacc - crescimento_terminal)
    fluxos.append(valor_terminal)
    pt_dcf = sum([fluxo / (1 + wacc)**(i+1) for i, fluxo in enumerate(fluxos)])
    
    # PREÇO TETO MÉDIO (4 métodos)
    pts = [pt_bazin, pt_graham, pt_gordon, pt_dcf]
    pt_medio = sum(pts) / len(pts)
    
    # SINAL COM MARGEM DE SEGURANÇA
    margem_seguranca = ((pt_medio - preco_atual) / pt_medio) * 100 if pt_medio > 0 else 0
    
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
        "preco_atual": round(preco_atual, 2),
        "pt_medio": round(pt_medio, 2),
        "margem_seguranca": round(margem_seguranca, 1),
        "metodos": {
            "bazin": {
                "pt": round(pt_bazin, 2),
                "dy": dy,
                "k": k,
                "g": g,
                "descricao": "Dividend Yield Discounted"
            },
            "graham": {
                "pt": round(pt_graham, 2),
                "eps": eps,
                "g": g,
                "descricao": "Valor Intrínseco Graham"
            },
            "gordon": {
                "pt": round(pt_gordon, 2),
                "d1": round(d1, 4),
                "k": k,
                "g": g,
                "descricao": "Dividend Growth Model"
            },
            "dcf": {
                "pt": round(pt_dcf, 2),
                "fcf": fcf,
                "wacc": wacc,
                "anos": anos_projetados,
                "descricao": "Discounted Cash Flow"
            }
        },
        "sinal": sinal,
        "cor": cor,
        "recomendacao": f"Preço teto médio (4 métodos): R$ {pt_medio:.2f} | Margem: {margem_seguranca:.1f}%"
    }
    
    return jsonify(resultado), 200
