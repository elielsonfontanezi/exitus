# -*- coding: utf-8 -*-
"""
M7.3 - Performance/Analise Blueprint (4 endpoints)
- GET /api/performance/performance
- GET /api/performance/benchmark  
- GET /api/performance/correlacao
- GET /api/performance/desvio-alocacao
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from datetime import date

from app.services.analise_service import AnaliseService
from app.services.relatorio_service import RelatorioService

performance_bp = Blueprint("performance", __name__, url_prefix="/api/performance")


@performance_bp.route("/performance", methods=["GET"])
@jwt_required()
def performance_portfolio():
    """Métricas avançadas: Sharpe, Sortino, IRR, Drawdown."""
    usuario_id = get_jwt_identity()
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")
    
    try:
        data_inicio = date.fromisoformat(data_inicio) if data_inicio else None
        data_fim = date.fromisoformat(data_fim) if data_fim else None
        
        resultado = RelatorioService.gerar_relatorio_performance(
            usuario_id=UUID(usuario_id),
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros={}
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/benchmark", methods=["GET"])
@jwt_required()
def comparar_benchmark():
    """Compara portfolio vs IBOV/SP500."""
    usuario_id = get_jwt_identity()
    benchmark = request.args.get("benchmark", "IBOV")
    
    try:
        resultado = AnaliseService.comparar_com_benchmark(
            usuario_id=UUID(usuario_id),
            benchmark=benchmark
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/correlacao", methods=["GET"])
@jwt_required()
def correlacao_ativos():
    """Matriz de correlação entre ativos do portfolio."""
    usuario_id = get_jwt_identity()
    
    try:
        resultado = AnaliseService.calcular_correlacao_ativos(usuario_id=UUID(usuario_id))
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@performance_bp.route("/desvio-alocacao", methods=["GET"])
@jwt_required()
def desvio_alocacao():
    """Desvios de alocação vs target."""
    usuario_id = get_jwt_identity()
    portfolio_id = request.args.get("portfolio_id")
    
    try:
        resultado = AnaliseService.analisar_performance_portfolio(
            usuario_id=UUID(usuario_id),
            portfolio_id=UUID(portfolio_id) if portfolio_id else None
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
