from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.portfolio_service import get_portfolio_metrics

calculosbp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculosbp.route('/portfolio', methods=['GET'])
@jwt_required()
def calcular_portfolio():
    """Endpoint principal - métricas reais do portfólio"""
    
    # CORREÇÃO: get_jwt_identity() retorna UUID direto
    usuario_id = get_jwt_identity()
    
    # Calcular métricas reais
    metrics = get_portfolio_metrics(usuario_id)
    
    if "erro" in metrics:
        return jsonify(metrics), 404

    # Estrutura completa com valores reais + métricas mock restantes
    resultado = {
        "rentabilidade": {
            "YTD": metrics["rentabilidade_ytd"],
            "1A": 0.12,  # Futuro: histórico real
            "3A": 0.36   # Futuro: histórico real
        },
        "volatilidade_anualizada": 0.14,  # Futuro
        "sharpe_ratio": 1.15,             # Futuro
        "drawdown_maximo": 0.10,          # Futuro
        "correlacao_ativos": {},          # Futuro
        "alocacao": metrics["alocacao"],
        "dividend_yield_medio": metrics["dividend_yield_medio"],
        "portfolio_info": {
            "total_custo": metrics["total_custo"],
            "total_valor_atual": metrics["total_valor_atual"],
            "total_posicoes": metrics["total_posicoes"]
        }
    }
    
    return jsonify(resultado), 200
