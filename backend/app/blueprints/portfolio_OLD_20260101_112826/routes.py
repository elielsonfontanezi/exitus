from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from uuid import UUID

from . import bp
from app.services.portfolio_service import PortfolioService
# Assumindo que o schema já existe conforme sua confirmação
from app.schemas.portfolio_schema import (
    PortfolioCreateSchema, 
    PortfolioUpdateSchema, 
    PortfolioResponseSchema
)

# --- ROTAS CRUD ---

@bp.route('', methods=['GET'])
@jwt_required()
def list_portfolios():
    usuario_id = UUID(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    
    pagination = PortfolioService.get_all_for_user(usuario_id, page=page)
    
    return jsonify({
        "data": PortfolioResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page
    }), 200

@bp.route('/<uuid:portfolio_id>', methods=['GET'])
@jwt_required()
def get_portfolio(portfolio_id):
    usuario_id = UUID(get_jwt_identity())
    portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
    if not portfolio:
        return jsonify({"message": "Portfolio não encontrado"}), 404
    return jsonify({"data": PortfolioResponseSchema().dump(portfolio)}), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_portfolio():
    usuario_id = UUID(get_jwt_identity())
    json_data = request.get_json()
    
    try:
        data = PortfolioCreateSchema().load(json_data)
        novo = PortfolioService.create(data, usuario_id)
        return jsonify({
            "message": "Portfolio criado com sucesso",
            "data": PortfolioResponseSchema().dump(novo)
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/<uuid:portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id):
    usuario_id = UUID(get_jwt_identity())
    json_data = request.get_json()
    
    try:
        data = PortfolioUpdateSchema().load(json_data)
        updated = PortfolioService.update(portfolio_id, data, usuario_id)
        if not updated:
            return jsonify({"message": "Portfolio não encontrado"}), 404
        return jsonify({
            "message": "Portfolio atualizado",
            "data": PortfolioResponseSchema().dump(updated)
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

@bp.route('/<uuid:portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id):
    usuario_id = UUID(get_jwt_identity())
    if PortfolioService.delete(portfolio_id, usuario_id):
        return jsonify({"message": "Portfolio removido"}), 200
    return jsonify({"message": "Portfolio não encontrado"}), 404

# --- ROTAS ANALYTICS (M7) ---

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    usuario_id = UUID(get_jwt_identity())
    data = PortfolioService.get_dashboard(usuario_id)
    return jsonify({"data": data}), 200
