# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.posicao_service import PosicaoService
from app.schemas.posicao_schema import PosicaoResponseSchema
import logging

logger = logging.getLogger(__name__)
# ADICIONADO strict_slashes=False para aceitar /api/posicoes e /api/posicoes/
posicao_bp = Blueprint('posicao', __name__, url_prefix='/api/posicoes')
posicoes_schema = PosicaoResponseSchema(many=True)

@posicao_bp.route('/', methods=['GET'], strict_slashes=False)
@posicao_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_posicoes():
    try:
        usuario_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        paginacao = PosicaoService.get_all(usuario_id, page, per_page)
        return jsonify({
            'success': True,
            'data': {'posicoes': posicoes_schema.dump(paginacao.items), 'total': paginacao.total},
            'message': f"{paginacao.total} posições encontradas"
        })
    except Exception as e:
        logger.error(f"Erro ao listar posições: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
