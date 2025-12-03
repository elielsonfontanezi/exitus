# -*- coding: utf-8 -*-
"""
Exitus - EventoCorporativo Blueprint
Rotas para gerenciamento de eventos corporativos
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.evento_corporativo_service import EventoCorporativoService
from app.schemas.evento_corporativo_schema import (
    EventoCorporativoCreateSchema,
    EventoCorporativoUpdateSchema,
    EventoCorporativoResponseSchema
)
from app.utils.responses import success_response, error_response
from app.decorators import admin_required
from marshmallow import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

evento_corporativo_bp = Blueprint('evento_corporativo', __name__, url_prefix='/api/eventos-corporativos')

# Schemas
evento_create_schema = EventoCorporativoCreateSchema()
evento_update_schema = EventoCorporativoUpdateSchema()
evento_schema = EventoCorporativoResponseSchema()
eventos_schema = EventoCorporativoResponseSchema(many=True)


@evento_corporativo_bp.route('', methods=['GET'])
@jwt_required()
def listar_eventos():
    """Lista eventos corporativos com filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        filters = {}
        if request.args.get('ativo_id'):
            filters['ativo_id'] = request.args.get('ativo_id')
        if request.args.get('tipo_evento'):
            filters['tipo_evento'] = request.args.get('tipo_evento')
        if request.args.get('data_anuncio_inicio'):
            filters['data_anuncio_inicio'] = datetime.strptime(
                request.args.get('data_anuncio_inicio'), '%Y-%m-%d'
            ).date()
        if request.args.get('data_anuncio_fim'):
            filters['data_anuncio_fim'] = datetime.strptime(
                request.args.get('data_anuncio_fim'), '%Y-%m-%d'
            ).date()
        
        paginacao = EventoCorporativoService.get_all(page, per_page, filters)
        
        return success_response(
            data={
                'eventos': eventos_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} eventos encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/<uuid:evento_id>', methods=['GET'])
@jwt_required()
def buscar_evento(evento_id):
    """Busca evento por ID"""
    try:
        evento = EventoCorporativoService.get_by_id(evento_id)
        
        if not evento:
            return error_response("Evento não encontrado", 404)
        
        return success_response(
            data=evento_schema.dump(evento),
            message="Evento encontrado"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar evento: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('', methods=['POST'])
@admin_required()
def criar_evento():
    """Cria novo evento corporativo (ADMIN)"""
    try:
        data = evento_create_schema.load(request.get_json())
        evento = EventoCorporativoService.create(data)
        
        return success_response(
            data=evento_schema.dump(evento),
            message="Evento criado com sucesso",
            status_code=201
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao criar evento: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/<uuid:evento_id>', methods=['PUT'])
@admin_required()
def atualizar_evento(evento_id):
    """Atualiza evento corporativo (ADMIN)"""
    try:
        data = evento_update_schema.load(request.get_json())
        evento = EventoCorporativoService.update(evento_id, data)
        
        return success_response(
            data=evento_schema.dump(evento),
            message="Evento atualizado com sucesso"
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao atualizar evento: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/<uuid:evento_id>', methods=['DELETE'])
@admin_required()
def deletar_evento(evento_id):
    """Deleta evento corporativo (ADMIN)"""
    try:
        EventoCorporativoService.delete(evento_id)
        return success_response(message="Evento deletado com sucesso")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao deletar evento: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/ativo/<uuid:ativo_id>', methods=['GET'])
@jwt_required()
def eventos_por_ativo(ativo_id):
    """Lista eventos de um ativo"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        paginacao = EventoCorporativoService.get_por_ativo(ativo_id, page, per_page)
        
        return success_response(
            data={
                'eventos': eventos_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} eventos encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar eventos por ativo: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/meus-eventos', methods=['GET'])
@jwt_required()
def meus_eventos():
    """Lista eventos que afetam as posições do usuário"""
    try:
        usuario_id = get_jwt_identity()
        
        data_inicio = None
        data_fim = None
        
        if request.args.get('data_inicio'):
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d').date()
        if request.args.get('data_fim'):
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d').date()
        
        eventos = EventoCorporativoService.get_eventos_usuario(usuario_id, data_inicio, data_fim)
        
        return success_response(
            data={'eventos': eventos, 'total': len(eventos)},
            message=f"{len(eventos)} eventos encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar eventos do usuário: {e}")
        return error_response(str(e), 500)


@evento_corporativo_bp.route('/<uuid:evento_id>/aplicar-split', methods=['POST'])
@jwt_required()
def aplicar_split(evento_id):
    """Aplica desdobramento/grupamento nas posições do usuário"""
    try:
        usuario_id = get_jwt_identity()
        resultado = EventoCorporativoService.aplicar_evento_split(evento_id, usuario_id)
        
        return success_response(
            data=resultado,
            message=f"Evento aplicado a {resultado['posicoes_afetadas']} posições"
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao aplicar evento: {e}")
        return error_response(str(e), 500)
