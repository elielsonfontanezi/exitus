# -*- coding: utf-8 -*-
"""
Exitus - Movimentacao Caixa Blueprint M3.2
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.movimentacao_caixa_service import MovimentacaoCaixaService
from app.schemas.movimentacao_caixa_schema import MovimentacaoCaixaResponseSchema, MovimentacaoCaixaCreateSchema
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)
movimentacao_bp = Blueprint('movimentacao', __name__, url_prefix='/api/movimentacoes')
movimentacao_schema = MovimentacaoCaixaResponseSchema()
movimentacoes_schema = MovimentacaoCaixaResponseSchema(many=True)
create_schema = MovimentacaoCaixaCreateSchema()

@movimentacao_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_movimentacoes():
    try:
        usuario_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Filtros
        corretora_id = request.args.get('corretora_id')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        paginacao = MovimentacaoCaixaService.get_all(
            usuario_id, page, per_page, corretora_id, data_inicio, data_fim
        )
        
        return jsonify({
            'success': True,
            'data': {
                'movimentacoes': movimentacoes_schema.dump(paginacao.items),
                'total': paginacao.total
            },
            'message': f"{paginacao.total} movimentações encontradas"
        })
    except Exception as e:
        logger.error(f"Erro ao listar movimentações: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@movimentacao_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def criar_movimentacao():
    try:
        usuario_id = get_jwt_identity()
        dados = create_schema.load(request.get_json())
        
        nova_movimentacao = MovimentacaoCaixaService.create(usuario_id, dados)
        
        return jsonify({
            'success': True,
            'data': movimentacao_schema.dump(nova_movimentacao),
            'message': "Movimentação registrada com sucesso"
        }), 201
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao criar movimentação: {e}")
        return jsonify({'success': False, 'error': "Erro interno ao processar movimentação"}), 500

@movimentacao_bp.route('/saldo/<uuid:corretora_id>', methods=['GET'])
@jwt_required()
def obter_saldo(corretora_id):
    try:
        usuario_id = get_jwt_identity()
        saldo = MovimentacaoCaixaService.get_saldo(usuario_id, str(corretora_id))
        return jsonify({
            'success': True,
            'data': {'saldo': saldo, 'corretora_id': corretora_id},
            'message': "Saldo calculado com sucesso"
        })
    except Exception as e:
        logger.error(f"Erro ao calcular saldo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
