# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.provento_service import ProventoService
from app.schemas.provento_schema import ProventoResponseSchema
import logging

logger = logging.getLogger(__name__)
provento_bp = Blueprint('provento', __name__, url_prefix='/api/proventos')
proventos_schema = ProventoResponseSchema(many=True)

@provento_bp.route('/', methods=['GET'], strict_slashes=False)
@provento_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_proventos():
    try:
        usuario_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        paginacao = ProventoService.get_all(usuario_id, page, per_page)
        return jsonify({
            'success': True,
            'data': {'proventos': proventos_schema.dump(paginacao.items), 'total': paginacao.total},
            'message': f"{paginacao.total} proventos encontrados"
        })
    except Exception as e:
        logger.error(f"Erro ao listar proventos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
