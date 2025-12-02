# -*- coding: utf-8 -*-
"""Exitus - Corretoras Blueprint - Endpoints CRUD"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.corretora_service import CorretoraService
from app.schemas.corretora_schema import (
    CorretoraCreateSchema, CorretoraUpdateSchema, CorretoraResponseSchema
)
from app.utils.responses import success, error, not_found, forbidden

bp = Blueprint('corretoras', __name__, url_prefix='/api/corretoras')

@bp.route('', methods=['GET'])
@jwt_required()
def list_corretoras():
    """Lista corretoras do usuário autenticado"""
    usuario_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativa = request.args.get('ativa', type=lambda x: x.lower() == 'true')
    tipo = request.args.get('tipo', type=str)
    pais = request.args.get('pais', type=str)
    search = request.args.get('search', type=str)
    
    pagination = CorretoraService.get_all(usuario_id, page, per_page, ativa, tipo, pais, search)
    
    return success({
        "corretoras": CorretoraResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page
    }, "Lista de corretoras")

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_corretora(id):
    """Buscar corretora por ID"""
    usuario_id = get_jwt_identity()
    corretora = CorretoraService.get_by_id(id, usuario_id)
    
    if not corretora:
        return not_found("Corretora não encontrada")
    
    return success(CorretoraResponseSchema().dump(corretora), "Dados da corretora")

@bp.route('', methods=['POST'])
@jwt_required()
def create_corretora():
    """Criar nova corretora"""
    usuario_id = get_jwt_identity()
    
    try:
        data = CorretoraCreateSchema().load(request.json)
        corretora = CorretoraService.create(data, usuario_id)
        return success(
            CorretoraResponseSchema().dump(corretora),
            "Corretora criada com sucesso",
            201
        )
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao criar corretora: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['PUT'])
@jwt_required()
def update_corretora(id):
    """Atualizar corretora"""
    usuario_id = get_jwt_identity()
    
    try:
        data = CorretoraUpdateSchema().load(request.json)
        corretora = CorretoraService.update(id, data, usuario_id)
        return success(CorretoraResponseSchema().dump(corretora), "Corretora atualizada")
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao atualizar: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_corretora(id):
    """Deletar corretora"""
    usuario_id = get_jwt_identity()
    
    try:
        CorretoraService.delete(id, usuario_id)
        return success(None, "Corretora deletada com sucesso")
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error(f"Erro ao deletar: {str(e)}", 500)

@bp.route('/saldo-total', methods=['GET'])
@jwt_required()
def saldo_total():
    """Saldo total do usuário em determinada moeda"""
    usuario_id = get_jwt_identity()
    moeda = request.args.get('moeda', 'BRL', type=str)
    
    total = CorretoraService.get_saldo_total(usuario_id, moeda)
    
    return success({
        "moeda": moeda.upper(),
        "saldo_total": str(total)
    }, "Saldo total calculado")
