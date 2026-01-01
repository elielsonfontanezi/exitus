# backend/app/blueprints/portfolio/blueprint.py
# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Blueprint
Define as rotas da API para CRUD e Analytics de Portfolios.
"""
import logging
from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio_schema import (
    PortfolioCreateSchema,
    PortfolioUpdateSchema,
    PortfolioResponseSchema
)

logger = logging.getLogger(__name__)
portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolios')

# --- ROTAS CRUD ---

@portfolio_bp.route('/', methods=['GET'])
@jwt_required()
def list_portfolios():
    """Lista todos os portfolios do usuário logado."""
    usuario_id = UUID(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    try:
        pagination = PortfolioService.get_all_for_user(usuario_id, page, per_page)
        return jsonify({
            "portfolios": PortfolioResponseSchema(many=True).dump(pagination.items),
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        }), 200
    except Exception as e:
        logger.error(f"Erro ao listar portfolios: {e}")
        return jsonify({"error": "Erro interno ao processar a solicitação."}), 500

@portfolio_bp.route('/<uuid:portfolio_id>', methods=['GET'])
@jwt_required()
def get_portfolio(portfolio_id: UUID):
    """Busca um portfolio por ID."""
    usuario_id = UUID(get_jwt_identity())
    portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
    if not portfolio:
        return jsonify({"error": "Portfolio não encontrado."}), 404
    return jsonify(PortfolioResponseSchema().dump(portfolio)), 200

@portfolio_bp.route('/', methods=['POST'])
@jwt_required()
def create_portfolio():
    """Cria um novo portfolio."""
    usuario_id = UUID(get_jwt_identity())
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Requisição sem corpo JSON."}), 400

    try:
        data = PortfolioCreateSchema().load(json_data)
        novo_portfolio = PortfolioService.create(data, usuario_id)
        return jsonify(PortfolioResponseSchema().dump(novo_portfolio)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict
    except Exception as e:
        logger.error(f"Erro ao criar portfolio: {e}")
        return jsonify({"error": "Erro interno ao criar o portfolio."}), 500

@portfolio_bp.route('/<uuid:portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id: UUID):
    """Atualiza um portfolio existente."""
    usuario_id = UUID(get_jwt_identity())
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Requisição sem corpo JSON."}), 400

    try:
        data = PortfolioUpdateSchema().load(json_data)
        portfolio_atualizado = PortfolioService.update(portfolio_id, data, usuario_id)
        if not portfolio_atualizado:
            return jsonify({"error": "Portfolio não encontrado."}), 404
        return jsonify(PortfolioResponseSchema().dump(portfolio_atualizado)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict
    except Exception as e:
        logger.error(f"Erro ao atualizar portfolio {portfolio_id}: {e}")
        return jsonify({"error": "Erro interno ao atualizar o portfolio."}), 500

@portfolio_bp.route('/<uuid:portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id: UUID):
    """Desativa (soft delete) um portfolio."""
    usuario_id = UUID(get_jwt_identity())
    try:
        success = PortfolioService.delete(portfolio_id, usuario_id)
        if not success:
            return jsonify({"error": "Portfolio não encontrado ou já inativo."}), 404
        return '', 204 # No Content
    except Exception as e:
        logger.error(f"Erro ao deletar portfolio {portfolio_id}: {e}")
        return jsonify({"error": "Erro interno ao deletar o portfolio."}), 500


# --- ROTAS DE ANALYTICS (STUBS) ---
# Mantidas para compatibilidade com implementações futuras ou existentes.

@portfolio_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """(STUB) Retorna dashboard completo do portfólio."""
    usuario_id = UUID(get_jwt_identity())
    dados = PortfolioService.get_dashboard(usuario_id)
    return jsonify(dados), 200

@portfolio_bp.route('/alocacao', methods=['GET'])
@jwt_required()
def alocacao():
    """(STUB) Retorna alocação do portfólio por classe de ativo."""
    usuario_id = UUID(get_jwt_identity())
    dados = PortfolioService.get_alocacao(usuario_id)
    return jsonify(dados), 200
