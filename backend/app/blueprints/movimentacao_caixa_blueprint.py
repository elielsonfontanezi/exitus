# -*- coding: utf-8 -*-
"""
Exitus - MovimentacaoCaixa Blueprint
Rotas para gerenciamento de movimentações de caixa
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.movimentacao_caixa_service import MovimentacaoCaixaService
from app.schemas.movimentacao_caixa_schema import (
    MovimentacaoCaixaCreateSchema,
    MovimentacaoCaixaUpdateSchema,
    MovimentacaoCaixaResponseSchema
)
from app.utils.responses import success_response, error_response
from marshmallow import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

movimentacao_caixa_bp = Blueprint('movimentacao_caixa', __name__, url_prefix='/api/movimentacoes-caixa')

# Schemas
movimentacao_create_schema = MovimentacaoCaixaCreateSchema()
movimentacao_update_schema = MovimentacaoCaixaUpdateSchema()
movimentacao_schema = MovimentacaoCaixaResponseSchema()
movimentacoes_schema = MovimentacaoCaixaResponseSchema(many=True)


@movimentacao_caixa_bp.route('', methods=['GET'])
@jwt_required()
def listar_movimentacoes():
    """Lista movimentações de caixa do usuário"""
    try:
        usuario_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        filters = {}
        if request.args.get('corretora_id'):
            filters['corretora_id'] = request.args.get('corretora_id')
        if request.args.get('tipo_movimentacao'):
            filters['tipo_movimentacao'] = request.args.get('tipo_movimentacao')
        if request.args.get('data_inicio'):
            filters['data_inicio'] = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d').date()
        if request.args.get('data_fim'):
            filters['data_fim'] = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d').date()
        if request.args.get('moeda'):
            filters['moeda'] = request.args.get('moeda')
        
        paginacao = MovimentacaoCaixaService.get_all(usuario_id, page, per_page, filters)
        
        return success_response(
            data={
                'movimentacoes': movimentacoes_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} movimentações encontradas"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar movimentações: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('/<uuid:movimentacao_id>', methods=['GET'])
@jwt_required()
def buscar_movimentacao(movimentacao_id):
    """Busca movimentação por ID"""
    try:
        usuario_id = get_jwt_identity()
        movimentacao = MovimentacaoCaixaService.get_by_id(movimentacao_id, usuario_id)
        
        if not movimentacao:
            return error_response("Movimentação não encontrada", 404)
        
        return success_response(
            data=movimentacao_schema.dump(movimentacao),
            message="Movimentação encontrada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar movimentação: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('', methods=['POST'])
@jwt_required()
def criar_movimentacao():
    """Cria nova movimentação de caixa"""
    try:
        usuario_id = get_jwt_identity()
        data = movimentacao_create_schema.load(request.get_json())
        
        movimentacao = MovimentacaoCaixaService.create(usuario_id, data)
        
        return success_response(
            data=movimentacao_schema.dump(movimentacao),
            message="Movimentação criada com sucesso",
            status_code=201
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao criar movimentação: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('/<uuid:movimentacao_id>', methods=['PUT'])
@jwt_required()
def atualizar_movimentacao(movimentacao_id):
    """Atualiza movimentação de caixa"""
    try:
        usuario_id = get_jwt_identity()
        data = movimentacao_update_schema.load(request.get_json())
        
        movimentacao = MovimentacaoCaixaService.update(movimentacao_id, usuario_id, data)
        
        return success_response(
            data=movimentacao_schema.dump(movimentacao),
            message="Movimentação atualizada com sucesso"
        )
        
    except ValidationError as e:
        return error_response(e.messages, 400)
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao atualizar movimentação: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('/<uuid:movimentacao_id>', methods=['DELETE'])
@jwt_required()
def deletar_movimentacao(movimentacao_id):
    """Deleta movimentação de caixa"""
    try:
        usuario_id = get_jwt_identity()
        MovimentacaoCaixaService.delete(movimentacao_id, usuario_id)
        
        return success_response(message="Movimentação deletada com sucesso")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Erro ao deletar movimentação: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('/saldo/<uuid:corretora_id>', methods=['GET'])
@jwt_required()
def saldo_corretora(corretora_id):
    """Retorna saldo consolidado de uma corretora"""
    try:
        usuario_id = get_jwt_identity()
        saldos = MovimentacaoCaixaService.get_saldo_corretora(usuario_id, corretora_id)
        
        return success_response(
            data={'saldos': saldos},
            message="Saldo calculado"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular saldo: {e}")
        return error_response(str(e), 500)


@movimentacao_caixa_bp.route('/extrato', methods=['GET'])
@jwt_required()
def extrato():
    """Gera extrato de movimentações"""
    try:
        usuario_id = get_jwt_identity()
        
        corretora_id = request.args.get('corretora_id')
        data_inicio = None
        data_fim = None
        
        if request.args.get('data_inicio'):
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d').date()
        if request.args.get('data_fim'):
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d').date()
        
        extrato = MovimentacaoCaixaService.get_extrato(usuario_id, corretora_id, data_inicio, data_fim)
        
        return success_response(
            data={'extrato': extrato, 'total': len(extrato)},
            message="Extrato gerado"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar extrato: {e}")
        return error_response(str(e), 500)
