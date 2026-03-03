# -*- coding: utf-8 -*-
"""
Exitus - Regras Fiscais Blueprint
CRUD completo usando banco de dados (EXITUS-CRUD-001)
Substituiu mock data estático por RegraFiscalService.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services.regra_fiscal_service import RegraFiscalService
from app.utils.exceptions import ExitusError
from app.schemas.regra_fiscal_schema import (
    RegraFiscalResponseSchema,
    RegraFiscalCreateSchema,
    RegraFiscalUpdateSchema,
)
from app.utils.decorators import admin_required
import logging

logger = logging.getLogger(__name__)
regrasbp = Blueprint('regras_fiscais', __name__, url_prefix='/api/regras-fiscais')

regras_schema = RegraFiscalResponseSchema(many=True)
regra_schema = RegraFiscalResponseSchema()
create_schema = RegraFiscalCreateSchema()
update_schema = RegraFiscalUpdateSchema()


@regrasbp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_regras():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        pais = request.args.get('pais', type=str)
        tipo_ativo = request.args.get('tipo_ativo', type=str)
        ativa = request.args.get('ativa', type=lambda x: x.lower() == 'true')

        paginacao = RegraFiscalService.get_all(page, per_page, pais, tipo_ativo, ativa)

        return jsonify({
            'success': True,
            'data': {
                'regras': regras_schema.dump(paginacao.items),
                'total': paginacao.total,
                'pages': paginacao.pages,
                'page': paginacao.page,
            },
            'message': f"{paginacao.total} regras fiscais encontradas"
        })
    except Exception as e:
        logger.error(f"Erro ao listar regras fiscais: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@regrasbp.route('/<uuid:regra_id>', methods=['GET'])
@jwt_required()
def buscar_regra(regra_id):
    try:
        regra = RegraFiscalService.get_by_id(regra_id)
        if not regra:
            return jsonify({'success': False, 'error': 'Regra fiscal não encontrada'}), 404
        return jsonify({
            'success': True,
            'data': regra_schema.dump(regra),
            'message': 'Dados da regra fiscal'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar regra fiscal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@regrasbp.route('/', methods=['POST'], strict_slashes=False)
@admin_required
def criar_regra():
    try:
        data = create_schema.load(request.get_json())
        regra = RegraFiscalService.create(data)
        return jsonify({
            'success': True,
            'data': regra_schema.dump(regra),
            'message': 'Regra fiscal criada com sucesso'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao criar regra fiscal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@regrasbp.route('/<uuid:regra_id>', methods=['PUT'])
@admin_required
def atualizar_regra(regra_id):
    try:
        data = update_schema.load(request.get_json())
        regra = RegraFiscalService.update(regra_id, data)
        return jsonify({
            'success': True,
            'data': regra_schema.dump(regra),
            'message': 'Regra fiscal atualizada'
        })
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao atualizar regra fiscal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@regrasbp.route('/<uuid:regra_id>', methods=['DELETE'])
@admin_required
def deletar_regra(regra_id):
    try:
        RegraFiscalService.delete(regra_id)
        return jsonify({'success': True, 'message': 'Regra fiscal deletada com sucesso'})
    except ExitusError as e:
        return jsonify({'success': False, 'error': str(e)}), e.http_status
    except Exception as e:
        logger.error(f"Erro ao deletar regra fiscal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
