# -*- coding: utf-8 -*-
"""
Exitus - Provento Blueprint
Rotas para gerenciamento de proventos
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.provento_service import ProventoService
from app.schemas.provento_schema import (
    ProventoCreateSchema, 
    ProventoUpdateSchema,
    ProventoResponseSchema
)
from app.utils.responses import success_response, error_response
from app.decorators import admin_required
from marshmallow import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

provento_bp = Blueprint('provento', __name__, url_prefix='/api/proventos')

# Schemas
provento_create_schema = ProventoCreateSchema()
provento_update_schema = ProventoUpdateSchema()
provento_schema = ProventoResponseSchema()
proventos_schema = ProventoResponseSchema(many=True)


@provento_bp.route('', methods=['GET'])
@jwt_required()
def listar_proventos():
    """Lista proventos com filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        filters = {}
        if request.args.get('ativo_id'):
            filters['ativo_id'] = request.args.get('ativo_id')
        if request.args.get('tipo_provento'):
            filters['tipo_provento'] = request.args.get('tipo_provento')
        if request.args.get('data_com_inicio'):
            filters['data_com_inicio'] = datetime.strptime(request.args.get('data_com_inicio'), '%Y-%m-%d').date()
        if request.args.get('data_com_fim'):
            filters['data_com_fim'] = datetime.strptime(request.args.get('data_com_fim'), '%Y-%m-%d').date()
        
        paginacao = ProventoService.get_all(page, per_page, filters)
        
        return success_response(
            data={
                'proventos': proventos_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} proventos encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar proventos: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/<uuid:provento_id>', methods=['GET'])
@jwt_required()
def buscar_provento(provento_id):
    """Busca provento por ID"""
    try:
        provento = ProventoService.get_by_id(provento_id)
        
        if not provento:
            return error_response("Provento não encontrado", 404)
        
        return success_response(
            data=provento_schema.dump(provento),
            message="Provento encontrado"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar provento: {e}")
        return error_response(str(e), 500)


@provento_bp.route('', methods=['POST'])
@admin_required()
def criar_provento():
    """Cria novo provento (ADMIN)"""
    try:
        data = provento_create_schema.load(request.get_json())
        provento = ProventoService.create(data)
        
        return success_response(
            data=provento_schema.dump(provento),
            message="Provento criado com sucesso",
            status_code=201
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao criar provento: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/<uuid:provento_id>', methods=['PUT'])
@admin_required()
def atualizar_provento(provento_id):
    """Atualiza provento (ADMIN)"""
    try:
        data = provento_update_schema.load(request.get_json())
        provento = ProventoService.update(provento_id, data)
        
        return success_response(
            data=provento_schema.dump(provento),
            message="Provento atualizado com sucesso"
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao atualizar provento: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/<uuid:provento_id>', methods=['DELETE'])
@admin_required()
def deletar_provento(provento_id):
    """Deleta provento (ADMIN)"""
    try:
        ProventoService.delete(provento_id)
        return success_response(message="Provento deletado com sucesso")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao deletar provento: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/ativo/<uuid:ativo_id>', methods=['GET'])
@jwt_required()
def proventos_por_ativo(ativo_id):
    """Lista proventos de um ativo"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        paginacao = ProventoService.get_por_ativo(ativo_id, page, per_page)
        
        return success_response(
            data={
                'proventos': proventos_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} proventos encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar proventos por ativo: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/recebidos', methods=['GET'])
@jwt_required()
def proventos_recebidos():
    """Lista proventos recebidos pelo usuário"""
    try:
        usuario_id = get_jwt_identity()
        
        data_inicio = None
        data_fim = None
        
        if request.args.get('data_inicio'):
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d').date()
        if request.args.get('data_fim'):
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d').date()
        
        proventos = ProventoService.get_recebidos_usuario(usuario_id, data_inicio, data_fim)
        
        return success_response(
            data={'proventos': proventos, 'total': len(proventos)},
            message=f"{len(proventos)} proventos recebidos"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar proventos recebidos: {e}")
        return error_response(str(e), 500)


@provento_bp.route('/total-recebido', methods=['GET'])
@jwt_required()
def total_proventos_recebidos():
    """Calcula total de proventos recebidos"""
    try:
        usuario_id = get_jwt_identity()
        ativo_id = request.args.get('ativo_id')
        
        total = ProventoService.calcular_total_recebido(usuario_id, ativo_id)
        
        return success_response(
            data=total,
            message="Total de proventos calculado"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular total de proventos: {e}")
        return error_response(str(e), 500)
