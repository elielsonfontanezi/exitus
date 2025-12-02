# -*- coding: utf-8 -*-
"""Exitus - Usuarios Blueprint - Endpoints CRUD"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.usuario_service import UsuarioService
from app.schemas.usuario_schema import (
    UsuarioCreateSchema, UsuarioUpdateSchema, 
    ChangePasswordSchema, UsuarioResponseSchema
)
from app.utils.responses import success, error, not_found, forbidden
from app.utils.decorators import admin_required
from app.models import Usuario

bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

@bp.route('', methods=['GET'])
@admin_required
def list_usuarios():
    """Lista usuários (admin only) com paginação e filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=lambda x: x.lower() == 'true')
    role = request.args.get('role', type=str)
    search = request.args.get('search', type=str)
    
    pagination = UsuarioService.get_all(page, per_page, ativo, role, search)
    
    return success({
        "usuarios": UsuarioResponseSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page
    }, "Lista de usuários")

@bp.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    """Ver detalhes de usuário (próprio ou admin)"""
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)
    usuario = UsuarioService.get_by_id(id)
    
    if not usuario:
        return not_found("Usuário não encontrado")
    
    # Verifica permissão: próprio usuário ou admin
    if str(usuario.id) != current_user_id and current_user.role.value.upper() != 'ADMIN':
        return forbidden("Acesso negado")
    
    return success(UsuarioResponseSchema().dump(usuario), "Dados do usuário")

@bp.route('', methods=['POST'])
def create_usuario():
    """Criar usuário (registro público)"""
    try:
        data = UsuarioCreateSchema().load(request.json)
        usuario = UsuarioService.create(data)
        return success(
            UsuarioResponseSchema().dump(usuario), 
            "Usuário criado com sucesso", 
            201
        )
    except ValidationError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao criar usuário: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    """Atualizar usuário (próprio ou admin)"""
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)
    
    # Verifica permissão
    if str(id) != current_user_id and current_user.role.value.upper() != 'ADMIN':
        return forbidden("Acesso negado")
    
    try:
        data = UsuarioUpdateSchema().load(request.json)
        usuario = UsuarioService.update(id, data, current_user)
        return success(UsuarioResponseSchema().dump(usuario), "Usuário atualizado")
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao atualizar: {str(e)}", 500)

@bp.route('/<uuid:id>', methods=['DELETE'])
@admin_required
def delete_usuario(id):
    """Deletar usuário (admin only)"""
    try:
        UsuarioService.delete(id)
        return success(None, "Usuário deletado com sucesso")
    except ValueError as e:
        return not_found(str(e))
    except Exception as e:
        return error(f"Erro ao deletar: {str(e)}", 500)

@bp.route('/<uuid:id>/password', methods=['PATCH'])
@jwt_required()
def change_password(id):
    """Trocar senha (próprio usuário)"""
    current_user_id = get_jwt_identity()
    
    # Apenas o próprio usuário pode trocar sua senha
    if str(id) != current_user_id:
        return forbidden("Você só pode trocar sua própria senha")
    
    try:
        data = ChangePasswordSchema().load(request.json)
        UsuarioService.change_password(id, data['old_password'], data['new_password'])
        return success(None, "Senha alterada com sucesso")
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Erro ao trocar senha: {str(e)}", 500)
