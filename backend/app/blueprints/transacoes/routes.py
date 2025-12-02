# -*- coding: utf-8 -*-
"""Exitus - Transacoes Blueprint - Endpoints CRUD"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from app.services.transacao_service import TransacaoService
from app.schemas.transacao_schema import TransacaoCreateSchema, TransacaoUpdateSchema, TransacaoResponseSchema
from app.utils.responses import success, error, not_found
from uuid import UUID

bp = Blueprint('transacoes', __name__, url_prefix='/api/transacoes')

@bp.route('', methods=['GET'])
@jwt_required()
def list_transacoes():
    """Lista transações do usuário com filtros"""
    usuario_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tipo = request.args.get('tipo', type=str)
    ativo_id = request.args.get('ativo_id', type=str)
    corretora_id = request.args.get('corretora_id', type=str)
    data_inicio = request.args.get('data_inicio', type=str)
    data_fim = request.args.get('data_fim', type=str)
    
    # Converter datas
    try:
        data_inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
        data_fim = datetime.fromisoformat(data_fim) if data_fim else None
    except ValueError:
        return error("Formato de data inválido. Use ISO 8601 (YYYY-MM-DD)", 400)
    
    pagination = TransacaoService.get_all(
        usuario_id, page, per_page, tipo, ativo_id, corretora_id, data_inicio, data_fim
    )
    
    return success({
        "transacoes": TransacaoResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page
    }, "Lista de transações")

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_transacao(id):
    """Buscar transação por ID"""
    usuario_id = get_jwt_identity()
    
    transacao = TransacaoService.get_by_id(id, usuario_id)
    if not transacao:
        return not_found("Transação não encontrada")
    
    return success(TransacaoResponseSchema().dump(transacao), "Dados da transação")

@bp.route('', methods=['POST'])
@jwt_required()
def create_transacao():
    """Criar nova transação"""
    usuario_id = get_jwt_identity()
    
    try:
        data = TransacaoCreateSchema().load(request.json)
        transacao = TransacaoService.create(usuario_id, data)
        return success(
            TransacaoResponseSchema().dump(transacao),
            "Transação criada com sucesso",
            201
        )
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao criar transação: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['PUT'])
@jwt_required()
def update_transacao(id):
    """Atualizar transação"""
    usuario_id = get_jwt_identity()
    
    try:
        data = TransacaoUpdateSchema().load(request.json)
        transacao = TransacaoService.update(id, usuario_id, data)
        return success(TransacaoResponseSchema().dump(transacao), "Transação atualizada")
    except ValidationError as e:
        return error(str(e), 400)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao atualizar: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_transacao(id):
    """Deletar transação"""
    usuario_id = get_jwt_identity()
    
    try:
        TransacaoService.delete(id, usuario_id)
        return success(None, "Transação deletada com sucesso")
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error(f"Erro ao deletar: {str(e)}", 500)

@bp.route('/resumo/<uuid:ativo_id>', methods=['GET'])
@jwt_required()
def get_resumo_ativo(ativo_id):
    """Retorna resumo de transações de um ativo"""
    usuario_id = get_jwt_identity()
    
    resumo = TransacaoService.get_resumo_por_ativo(usuario_id, ativo_id)
    return success(resumo, "Resumo do ativo")
