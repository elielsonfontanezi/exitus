# -- coding: utf-8 --
# Exitus - Transações Blueprint - Endpoints CRUD
# v0.7.13 — GAP-002: ownership antes do schema no PUT
#           GAP-003: rota /resumo-ativo/<ativo_id>
#           Fix: not_found (com underscore) consistente com responses.py
# Fix batch TRX-002, TRX-003, TRX-004, TRX-006, TRX-007

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime

from app.services.transacao_service import TransacaoService
from app.schemas.transacao_schema import (
    TransacaoCreateSchema,
    TransacaoUpdateSchema,
    TransacaoResponseSchema,
    TransacaoListSchema,
)
from app.utils.responses import success, error, not_found, forbidden
from app.utils.exceptions import ExitusError

bp = Blueprint('transacoes', __name__, url_prefix='/api/transacoes')


# -----------------------------------------------------------------------
# GET /api/transacoes
# -----------------------------------------------------------------------
@bp.route('', methods=['GET'])
@jwt_required()
def list_transacoes():
    """Lista transações do usuário com filtros e paginação."""
    usuario_id   = get_jwt_identity()
    page         = request.args.get('page',        1,    type=int)
    per_page     = request.args.get('per_page',    20,   type=int)
    tipo         = request.args.get('tipo',              type=str)
    ativo_id     = request.args.get('ativo_id',          type=str)
    corretora_id = request.args.get('corretora_id',      type=str)
    data_inicio  = request.args.get('data_inicio',       type=str)
    data_fim     = request.args.get('data_fim',          type=str)

    try:
        data_inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
        data_fim    = datetime.fromisoformat(data_fim)    if data_fim    else None
    except ValueError:
        return error('Formato de data inválido. Use ISO 8601: YYYY-MM-DD', 400)

    pagination = TransacaoService.get_all(
        usuario_id, page, per_page,
        tipo, ativo_id, corretora_id,
        data_inicio, data_fim,
    )

    return jsonify({
        'success': True,
        'message': f'{pagination.total} transações encontradas',
        'data': {
            'transacoes': TransacaoListSchema(many=True).dump(pagination.items),
            'total':      pagination.total,
            'pages':      pagination.pages,
            'page':       pagination.page,
            'per_page':   pagination.per_page,
        },
    }), 200


# -----------------------------------------------------------------------
# GET /api/transacoes/<id>
# -----------------------------------------------------------------------
@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_transacao(id):
    """Buscar transação por ID."""
    usuario_id = get_jwt_identity()
    try:
        transacao = TransacaoService.get_by_id(id, usuario_id)
        return success(TransacaoResponseSchema().dump(transacao), 'Dados da transação')
    except PermissionError as e:
        return forbidden(str(e))     # 403
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao buscar transação: {str(e)}', 500)


# -----------------------------------------------------------------------
# POST /api/transacoes
# -----------------------------------------------------------------------
@bp.route('', methods=['POST'])
@jwt_required()
def create_transacao():
    """Criar nova transação (EXITUS-BUSINESS-001: regras de negócio)."""
    usuario_id = get_jwt_identity()
    try:
        data      = TransacaoCreateSchema().load(request.json)
        resultado = TransacaoService.create(usuario_id, data)
        response_data = TransacaoResponseSchema().dump(resultado['transacao'])
        response_data['warnings'] = resultado.get('warnings', [])
        response_data['is_day_trade'] = resultado.get('is_day_trade', False)
        return success(
            response_data,
            'Transação criada com sucesso',
            201,
        )
    except ValidationError as e:
        return error(str(e), 400)
    except PermissionError as e:
        return forbidden(str(e))
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao criar transação: {str(e)}', 500)


# -----------------------------------------------------------------------
# PUT /api/transacoes/<id>
# GAP-002: ownership check ANTES do schema.load()
# -----------------------------------------------------------------------
@bp.route('/<uuid:id>', methods=['PUT'])
@jwt_required()
def update_transacao(id):
    """Atualizar transação."""
    usuario_id = get_jwt_identity()
    try:
        # GAP-002 — verificar ownership PRIMEIRO, antes de qualquer validação
        # de schema. Garante que 403 precede 400 quando o recurso pertence a
        # outro usuário.
        TransacaoService.check_ownership(id, usuario_id)

        data      = TransacaoUpdateSchema().load(request.json)
        transacao = TransacaoService.update(id, usuario_id, data)
        return success(TransacaoResponseSchema().dump(transacao), 'Transação atualizada')
    except PermissionError as e:
        return forbidden(str(e))     # 403 — TRX-002
    except ValidationError as e:
        return error(str(e), 400)
    except PermissionError as e:
        return forbidden(str(e))
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao atualizar transação: {str(e)}', 500)


# -----------------------------------------------------------------------
# DELETE /api/transacoes/<id>
# -----------------------------------------------------------------------
@bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def delete_transacao(id):
    """Deletar transação."""
    usuario_id = get_jwt_identity()
    try:
        TransacaoService.delete(id, usuario_id)
        return success(None, 'Transação deletada com sucesso')
    except PermissionError as e:
        return forbidden(str(e))
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao deletar transação: {str(e)}', 500)


# -----------------------------------------------------------------------
# GET /api/transacoes/resumo-ativo/<ativo_id>
# GAP-003: rota com nome explícito /resumo-ativo/ (era /resumo/)
# -----------------------------------------------------------------------
@bp.route('/resumo-ativo/<uuid:ativo_id>', methods=['GET'])
@jwt_required()
def get_resumo_ativo(ativo_id):
    """Retorna resumo de transações de um ativo específico do usuário."""
    usuario_id = get_jwt_identity()
    try:
        resumo = TransacaoService.get_resumo_por_ativo(usuario_id, ativo_id)
        return success(resumo, 'Resumo do ativo')
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao buscar resumo: {str(e)}', 500)
