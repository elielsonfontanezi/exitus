# -*- coding: utf-8 -*-
"""
M7.3 - Projeções Blueprint (4 endpoints)
- GET    /api/projecoes/renda
- GET    /api/projecoes/renda/<portfolio_id>  
- POST   /api/projecoes/recalcular
- GET    /api/projecoes/cenarios
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID, uuid4

from app.services.projecao_service import ProjecaoService

projecoes_bp = Blueprint("projecoes", __name__, url_prefix="/api/projecoes")


@projecoes_bp.route("/renda", methods=["GET"])
@jwt_required()
def listar_projecoes():
    """Lista projeções de renda (12 meses)."""
    usuario_id = get_jwt_identity()
    portfolio_id = request.args.get("portfolio_id")
    
    try:
        dados = ProjecaoService.listar_projecoes(
            usuario_id=UUID(usuario_id),
            portfolio_id=UUID(portfolio_id) if portfolio_id else None
        )
        return jsonify({"projecoes": dados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projecoes_bp.route("/renda/<string:portfolio_id>", methods=["GET"])
@jwt_required()
def projecoes_portfolio(portfolio_id):
    """Projeções específicas de um portfolio."""
    usuario_id = get_jwt_identity()
    
    try:
        dados = ProjecaoService.listar_projecoes(
            usuario_id=UUID(usuario_id),
            portfolio_id=UUID(portfolio_id)
        )
        return jsonify({"projecoes": dados}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projecoes_bp.route("/recalcular", methods=["POST"])
@jwt_required()
def recalcular_projecoes():
    """Recalcula e persiste projeções no banco."""
    usuario_id = get_jwt_identity()
    payload = request.get_json() or {}
    portfolio_id = payload.get("portfolio_id")
    
    try:
        resultado = ProjecaoService.recalcular_projecoes(
            usuario_id=UUID(usuario_id),
            portfolio_id=UUID(portfolio_id) if portfolio_id else None
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@projecoes_bp.route("/cenarios", methods=["GET"])
@jwt_required()
def cenarios_projecao():
    """Gera 3 cenários: conservador/moderado/otimista."""
    usuario_id = get_jwt_identity()
    portfolio_id = request.args.get("portfolio_id")
    
    try:
        dados = ProjecaoService.gerar_cenarios(
            usuario_id=UUID(usuario_id),
            portfolio_id=UUID(portfolio_id) if portfolio_id else None
        )
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
