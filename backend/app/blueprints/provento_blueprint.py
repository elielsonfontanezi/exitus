# -*- coding: utf-8 -*-
"""
Exitus - Provento Blueprint - Endpoints CRUD
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models import TipoProvento, Provento  # ✅ ADICIONAR Provento
from sqlalchemy.orm import joinedload  # ✅ ADICIONAR joinedload
from app.services.provento_service import ProventoService
from app.schemas.provento_schema import (
    ProventoSchema, 
    ProventoCreateSchema, 
    ProventoUpdateSchema, 
    ProventoResponseSchema
)
from app.utils.responses import success_response, error_response, not_found


provento_bp = Blueprint('proventos', __name__, url_prefix='/api/proventos')


@provento_bp.route('/', methods=['GET'])
@jwt_required()
def listar_proventos():
    """Lista proventos com filtros"""
    usuario_id = get_jwt_identity()
    
    # Filtros
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo_id = request.args.get('ativo_id', type=str)
    tipo = request.args.get('tipo', type=str)
    ano = request.args.get('ano', type=int)
    
    # Montar dict de filtros
    filters = {}
    if ativo_id:
        filters['ativo_id'] = ativo_id
    if tipo:
        try:
            # Converte string para Enum Python
            tipo_enum = TipoProvento[tipo.upper()]
            filters['tipo_provento'] = tipo_enum
        except KeyError:
            return error_response(
                f"Tipo inválido: {tipo}. Use: {', '.join([t.name.lower() for t in TipoProvento])}",
                400
            )
    if ano:  # ✅ ADICIONAR
        filters['ano'] = ano
    
    pagination = ProventoService.get_all(
        usuario_id=usuario_id,
        page=page,
        per_page=per_page,
        filters=filters
    )
    
    return success_response(
        data={
            'proventos': ProventoResponseSchema(many=True).dump(pagination.items),
            'total': pagination.total,
            'pages': pagination.pages,
            'page': pagination.page
        },
        message=f"{pagination.total} proventos encontrados"
    )


# @provento_bp.route('/<uuid:id>', methods=['GET'])
# @jwt_required()
# def get_provento(id):
#     """Buscar provento por ID"""
#     provento = ProventoService.get_by_id(id)
    
#     if not provento:
#         return not_found("Provento não encontrado")
    
#     return success_response(
#         ProventoResponseSchema().dump(provento),
#         "Dados do provento"
#     )

@provento_bp.route("/<uuid:id>", methods=["GET"])
@jwt_required()
def get_provento(id):
    """Buscar provento por ID"""
    provento = Provento.query.options(
        joinedload(Provento.ativo)
    ).get(id)

    if not provento:
        return not_found("Provento não encontrado")

    return success_response(
        ProventoResponseSchema().dump(provento),
        "Dados do provento",
    )


@provento_bp.route('/', methods=['POST'])
@jwt_required()
def criar_provento():
    """Criar novo provento"""
    try:
        data = ProventoCreateSchema().load(request.json)
        provento = ProventoService.create(data)
        
        return success_response(
            ProventoResponseSchema().dump(provento),
            "Provento criado com sucesso",
            201
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Erro ao criar provento: {str(e)}", 500)


@provento_bp.route('/<uuid:id>', methods=['PUT'])
@jwt_required()
def atualizar_provento(id):
    """Atualizar provento"""
    try:
        data = ProventoUpdateSchema().load(request.json)
        provento = ProventoService.update(id, data)
        
        return success_response(
            ProventoResponseSchema().dump(provento),
            "Provento atualizado"
        )
    except ValidationError as e:
        return error_response(str(e), 400)
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error_response(f"Erro ao atualizar: {str(e)}", 500)


@provento_bp.route('/<uuid:id>', methods=['DELETE'])
@jwt_required()
def deletar_provento(id):
    """Deletar provento"""
    try:
        ProventoService.delete(id)
        return success_response(None, "Provento deletado com sucesso")
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error_response(f"Erro ao deletar: {str(e)}", 500)
