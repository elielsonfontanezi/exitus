# -*- coding: utf-8 -*-
"""
Exitus - Assessora Blueprint
Endpoints para gestão de assessoras (admin only)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError as MarshmallowValidationError

from app.services.assessora_service import AssessoraService
from app.schemas.assessora_schema import (
    AssessoraSchema,
    AssessoraCreateSchema,
    AssessoraUpdateSchema,
    AssessoraStatsSchema
)
from app.utils.responses import success, error, paginated_response
from app.utils.exceptions import NotFoundError, ValidationError


assessora_bp = Blueprint('assessora', __name__, url_prefix='/api/assessoras')


def require_admin():
    """Decorator helper para verificar se usuário é admin"""
    jwt_data = get_jwt()
    role = jwt_data.get('role', 'user')
    
    if role != 'admin':
        return error('Acesso negado. Apenas administradores.', 403)
    
    return None


@assessora_bp.route('', methods=['GET'])
@jwt_required()
def list_assessoras():
    """
    Lista todas as assessoras (admin only)
    
    Query params:
        - page: Página (default: 1)
        - per_page: Registros por página (default: 20)
        - ativo: Filtrar por status (true/false/null)
    
    Returns:
        200: Lista paginada de assessoras
        403: Acesso negado (não admin)
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtro de status
    ativo = request.args.get('ativo', type=str)
    ativo_filter = None
    if ativo == 'true':
        ativo_filter = True
    elif ativo == 'false':
        ativo_filter = False
    
    # Buscar assessoras
    pagination = AssessoraService.get_all(
        page=page,
        per_page=per_page,
        ativo=ativo_filter
    )
    
    # Serializar
    schema = AssessoraSchema(many=True)
    assessoras_data = schema.dump(pagination.items)
    
    return paginated_response(
        items=assessoras_data,
        total=pagination.total,
        page=pagination.page,
        per_page=pagination.per_page,
        message='Assessoras listadas com sucesso'
    )


@assessora_bp.route('/<uuid:assessora_id>', methods=['GET'])
@jwt_required()
def get_assessora(assessora_id):
    """
    Busca assessora por ID (admin only)
    
    Args:
        assessora_id: UUID da assessora
    
    Returns:
        200: Dados da assessora
        403: Acesso negado
        404: Assessora não encontrada
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        assessora = AssessoraService.get_by_id(assessora_id)
        schema = AssessoraSchema()
        
        return success(
            data=schema.dump(assessora),
            message='Assessora encontrada'
        )
    
    except NotFoundError as e:
        return error(str(e), 404)


@assessora_bp.route('', methods=['POST'])
@jwt_required()
def create_assessora():
    """
    Cria nova assessora (admin only)
    
    Body:
        - nome: Nome da assessora (required)
        - razao_social: Razão social (required)
        - cnpj: CNPJ (required, unique)
        - email: Email (required, unique)
        - telefone, site, endereco, etc (optional)
    
    Returns:
        201: Assessora criada
        400: Dados inválidos
        403: Acesso negado
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        # Validar dados
        schema = AssessoraCreateSchema()
        data = schema.load(request.json)
        
        # Criar assessora
        assessora = AssessoraService.create(data)
        
        # Serializar resposta
        response_schema = AssessoraSchema()
        
        return success(
            data=response_schema.dump(assessora),
            message='Assessora criada com sucesso',
            status=201
        )
    
    except MarshmallowValidationError as e:
        return error(f'Dados inválidos: {e.messages}', 400)
    
    except ValidationError as e:
        return error(str(e), 400)


@assessora_bp.route('/<uuid:assessora_id>', methods=['PUT'])
@jwt_required()
def update_assessora(assessora_id):
    """
    Atualiza assessora existente (admin only)
    
    Args:
        assessora_id: UUID da assessora
    
    Body:
        Campos a atualizar (todos opcionais)
    
    Returns:
        200: Assessora atualizada
        400: Dados inválidos
        403: Acesso negado
        404: Assessora não encontrada
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        # Validar dados
        schema = AssessoraUpdateSchema()
        data = schema.load(request.json)
        
        # Atualizar assessora
        assessora = AssessoraService.update(assessora_id, data)
        
        # Serializar resposta
        response_schema = AssessoraSchema()
        
        return success(
            data=response_schema.dump(assessora),
            message='Assessora atualizada com sucesso'
        )
    
    except MarshmallowValidationError as e:
        return error(f'Dados inválidos: {e.messages}', 400)
    
    except ValidationError as e:
        return error(str(e), 400)
    
    except NotFoundError as e:
        return error(str(e), 404)


@assessora_bp.route('/<uuid:assessora_id>', methods=['DELETE'])
@jwt_required()
def delete_assessora(assessora_id):
    """
    Deleta assessora (soft delete por padrão, admin only)
    
    Args:
        assessora_id: UUID da assessora
    
    Query params:
        - hard: Se true, deleta fisicamente (default: false)
    
    Returns:
        200: Assessora deletada
        400: Erro ao deletar
        403: Acesso negado
        404: Assessora não encontrada
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        
        AssessoraService.delete(assessora_id, hard_delete=hard_delete)
        
        delete_type = 'fisicamente' if hard_delete else '(desativada)'
        
        return success(
            message=f'Assessora deletada {delete_type} com sucesso'
        )
    
    except ValidationError as e:
        return error(str(e), 400)
    
    except NotFoundError as e:
        return error(str(e), 404)


@assessora_bp.route('/<uuid:assessora_id>/stats', methods=['GET'])
@jwt_required()
def get_assessora_stats(assessora_id):
    """
    Retorna métricas da assessora (admin only)
    
    Args:
        assessora_id: UUID da assessora
    
    Returns:
        200: Métricas da assessora
        403: Acesso negado
        404: Assessora não encontrada
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        stats = AssessoraService.get_stats(assessora_id)
        
        # Serializar
        schema = AssessoraStatsSchema()
        
        return success(
            data=schema.dump(stats),
            message='Métricas obtidas com sucesso'
        )
    
    except NotFoundError as e:
        return error(str(e), 404)


@assessora_bp.route('/<uuid:assessora_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_assessora_ativo(assessora_id):
    """
    Ativa/desativa assessora (admin only)
    
    Args:
        assessora_id: UUID da assessora
    
    Returns:
        200: Status atualizado
        403: Acesso negado
        404: Assessora não encontrada
    """
    # Verificar permissão admin
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        assessora = AssessoraService.toggle_ativo(assessora_id)
        
        schema = AssessoraSchema()
        
        status_text = 'ativada' if assessora.ativo else 'desativada'
        
        return success(
            data=schema.dump(assessora),
            message=f'Assessora {status_text} com sucesso'
        )
    
    except NotFoundError as e:
        return error(str(e), 404)
