# -*- coding: utf-8 -*-
"""Exitus - Ativos Blueprint - Endpoints CRUD"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.ativo_service import AtivoService
from app.schemas.ativo_schema import (
    AtivoCreateSchema, AtivoUpdateSchema, AtivoResponseSchema
)
from app.utils.responses import success, error, not_found, forbidden
from app.utils.decorators import admin_required

bp = Blueprint('ativos', __name__, url_prefix='/api/ativos')

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_ativos():
    """Lista ativos com filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=lambda x: x.lower() == 'true')
    tipo = request.args.get('tipo', type=str)
    classe = request.args.get('classe', type=str)
    mercado = request.args.get('mercado', type=str)
    deslistado = request.args.get('deslistado', type=lambda x: x.lower() == 'true')
    search = request.args.get('search', type=str)
    
    pagination = AtivoService.get_all(page, per_page, ativo, tipo, classe, mercado, deslistado, search)
    
    return success({
        "ativos": AtivoResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page
    }, "Lista de ativos")

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_ativo(id):
    """Buscar ativo por ID"""
    ativo = AtivoService.get_by_id(id)
    
    if not ativo:
        return not_found("Ativo não encontrado")
    
    return success(AtivoResponseSchema().dump(ativo), "Dados do ativo")

@bp.route('/ticker/<string:ticker>', methods=['GET'])
@jwt_required()
def get_by_ticker(ticker):
    """Buscar ativo por ticker e mercado"""
    mercado = request.args.get('mercado', 'BR', type=str)
    ativo = AtivoService.get_by_ticker(ticker, mercado)
    
    if not ativo:
        return not_found(f"Ativo {ticker} não encontrado no mercado {mercado}")
    
    return success(AtivoResponseSchema().dump(ativo), "Dados do ativo")

@bp.route('/', methods=['POST'], strict_slashes=False)
@admin_required
def create_ativo():
    """Criar novo ativo (admin only)"""
    try:
        data = AtivoCreateSchema().load(request.json)
        ativo = AtivoService.create(data)
        return success(
            AtivoResponseSchema().dump(ativo),
            "Ativo criado com sucesso",
            201
        )
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao criar ativo: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['PUT'])
@admin_required
def update_ativo(id):
    """Atualizar ativo (admin only)"""
    try:
        data = AtivoUpdateSchema().load(request.json)
        ativo = AtivoService.update(id, data)
        return success(AtivoResponseSchema().dump(ativo), "Ativo atualizado")
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao atualizar: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['DELETE'])
@admin_required
def delete_ativo(id):
    """Deletar ativo (admin only)"""
    try:
        AtivoService.delete(id)
        return success(None, "Ativo deletado com sucesso")
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error(f"Erro ao deletar: {str(e)}", 500)

@bp.route('/mercado/<string:mercado>', methods=['GET'])
@jwt_required()
def list_by_mercado(mercado):
    """Listar ativos de um mercado específico"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    pagination = AtivoService.get_by_mercado(mercado, page, per_page)
    
    return success({
        "mercado": mercado.upper(),
        "ativos": AtivoResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page
    }, f"Ativos do mercado {mercado.upper()}")
