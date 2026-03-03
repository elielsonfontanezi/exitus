# -*- coding: utf-8 -*-
"""
Exitus - Feriados Blueprint
CRUD completo usando banco de dados (EXITUS-CRUD-001)
Substituiu mock data estático por FeriadoMercadoService.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services.feriado_mercado_service import FeriadoMercadoService
from app.schemas.feriado_mercado_schema import (
    FeriadoMercadoResponseSchema,
    FeriadoMercadoCreateSchema,
    FeriadoMercadoUpdateSchema,
)
from app.utils.decorators import admin_required
import logging

logger = logging.getLogger(__name__)
feriadosbp = Blueprint('feriados', __name__, url_prefix='/api/feriados')

feriados_schema = FeriadoMercadoResponseSchema(many=True)
feriado_schema = FeriadoMercadoResponseSchema()
create_schema = FeriadoMercadoCreateSchema()
update_schema = FeriadoMercadoUpdateSchema()


@feriadosbp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_feriados():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        pais = request.args.get('pais', type=str)
        mercado = request.args.get('mercado', type=str)
        ano = request.args.get('ano', type=int)

        paginacao = FeriadoMercadoService.get_all(page, per_page, pais, mercado, ano)

        return jsonify({
            'success': True,
            'data': {
                'feriados': feriados_schema.dump(paginacao.items),
                'total': paginacao.total,
                'pages': paginacao.pages,
                'page': paginacao.page,
            },
            'message': f"{paginacao.total} feriados encontrados"
        })
    except Exception as e:
        logger.error(f"Erro ao listar feriados: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@feriadosbp.route('/<uuid:feriado_id>', methods=['GET'])
@jwt_required()
def buscar_feriado(feriado_id):
    try:
        feriado = FeriadoMercadoService.get_by_id(feriado_id)
        if not feriado:
            return jsonify({'success': False, 'error': 'Feriado não encontrado'}), 404
        return jsonify({
            'success': True,
            'data': feriado_schema.dump(feriado),
            'message': 'Dados do feriado'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar feriado: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@feriadosbp.route('/', methods=['POST'], strict_slashes=False)
@admin_required
def criar_feriado():
    try:
        data = create_schema.load(request.get_json())
        feriado = FeriadoMercadoService.create(data)
        return jsonify({
            'success': True,
            'data': feriado_schema.dump(feriado),
            'message': 'Feriado criado com sucesso'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Erro ao criar feriado: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@feriadosbp.route('/<uuid:feriado_id>', methods=['PUT'])
@admin_required
def atualizar_feriado(feriado_id):
    try:
        data = update_schema.load(request.get_json())
        feriado = FeriadoMercadoService.update(feriado_id, data)
        return jsonify({
            'success': True,
            'data': feriado_schema.dump(feriado),
            'message': 'Feriado atualizado'
        })
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Erro ao atualizar feriado: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@feriadosbp.route('/<uuid:feriado_id>', methods=['DELETE'])
@admin_required
def deletar_feriado(feriado_id):
    try:
        FeriadoMercadoService.delete(feriado_id)
        return jsonify({'success': True, 'message': 'Feriado deletado com sucesso'})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Erro ao deletar feriado: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

