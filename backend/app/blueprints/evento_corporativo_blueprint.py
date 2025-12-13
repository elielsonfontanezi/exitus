# -*- coding: utf-8 -*-
"""
Exitus - Evento Corporativo Blueprint M3.3
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.evento_corporativo_service import EventoCorporativoService
from app.schemas.evento_corporativo_schema import EventoCorporativoResponseSchema
import logging

logger = logging.getLogger(__name__)
evento_bp = Blueprint('eventos_corporativos', __name__, url_prefix='/api/eventos-corporativos')
eventos_schema = EventoCorporativoResponseSchema(many=True)

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
                'total': paginacao.total
            },
            'message': f"{paginacao.total} eventos encontrados"
        })
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
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
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao aplicar evento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
