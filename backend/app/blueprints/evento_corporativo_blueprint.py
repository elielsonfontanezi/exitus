# -*- coding: utf-8 -*-
"""
Exitus - Evento Corporativo Blueprint M3.3
CRUD completo + POST aplicar (EXITUS-CRUD-001)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.evento_corporativo_service import EventoCorporativoService
from app.schemas.evento_corporativo_schema import (
    EventoCorporativoResponseSchema,
    EventoCorporativoCreateSchema,
    EventoCorporativoUpdateSchema,
)
from app.utils.decorators import admin_required
from app.utils.exceptions import ExitusError
import logging

logger = logging.getLogger(__name__)
evento_bp = Blueprint('eventos_corporativos', __name__, url_prefix='/api/eventos-corporativos')

eventos_schema = EventoCorporativoResponseSchema(many=True)
evento_schema = EventoCorporativoResponseSchema()
create_schema = EventoCorporativoCreateSchema()
update_schema = EventoCorporativoUpdateSchema()


@evento_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_eventos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        ativo_id = request.args.get('ativo_id')
        
        paginacao = EventoCorporativoService.get_all(page, per_page, ativo_id)
        
        return jsonify({
            'success': True,
            'data': {
                'eventos': eventos_schema.dump(paginacao.items),
                'total': paginacao.total,
                'pages': paginacao.pages,
                'page': paginacao.page,
            },
            'message': f"{paginacao.total} eventos encontrados"
        })
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@evento_bp.route('/<uuid:evento_id>', methods=['GET'])
@jwt_required()
def get_evento(evento_id):
    try:
        evento = EventoCorporativoService.get_by_id(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento não encontrado'}), 404
        return jsonify({
            'success': True,
            'data': evento_schema.dump(evento),
            'message': 'Dados do evento'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@evento_bp.route('/', methods=['POST'], strict_slashes=False)
@admin_required
def criar_evento():
    try:
        data = create_schema.load(request.get_json())
        evento = EventoCorporativoService.create(data)
        return jsonify({
            'success': True,
            'data': evento_schema.dump(evento),
            'message': 'Evento corporativo criado com sucesso'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao criar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@evento_bp.route('/<uuid:evento_id>', methods=['PUT'])
@admin_required
def atualizar_evento(evento_id):
    try:
        data = update_schema.load(request.get_json())
        evento = EventoCorporativoService.update(evento_id, data)
        return jsonify({
            'success': True,
            'data': evento_schema.dump(evento),
            'message': 'Evento corporativo atualizado'
        })
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao atualizar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@evento_bp.route('/<uuid:evento_id>', methods=['DELETE'])
@admin_required
def deletar_evento(evento_id):
    try:
        EventoCorporativoService.delete(evento_id)
        return jsonify({'success': True, 'message': 'Evento corporativo deletado com sucesso'})
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao deletar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@evento_bp.route('/<uuid:evento_id>/aplicar', methods=['POST'])
@jwt_required()
def aplicar_evento(evento_id):
    try:
        usuario_id = get_jwt_identity()
        resultado = EventoCorporativoService.aplicar_evento(str(evento_id), usuario_id)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'message': "Evento processado"
        })
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao aplicar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
