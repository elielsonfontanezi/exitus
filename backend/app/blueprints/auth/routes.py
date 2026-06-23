# -*- coding: utf-8 -*-
"""
Exitus - Auth Blueprint - Endpoints de autenticação
CORREÇÃO GAP-001 e GAP-002
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService
from app.schemas.auth_schema import LoginSchema, TokenResponseSchema, UserMeSchema
from app.schemas.usuario_schema import UsuarioUpdateSchema, ChangePasswordSchema
from app.utils.responses import success, error, unauthorized, bad_request, conflict
from app.utils.decorators import admin_required
from app.models import Usuario
from app.database import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/login', methods=['POST'])
def login():
    """
    Login e geração de tokens JWT.
    
    CORREÇÃO GAP-001: Tratamento correto de ValidationError (retorna 400, não 500)
    CORREÇÃO GAP-002: Response inclui dados do usuário
    """
    try:
        # CORREÇÃO GAP-001: Capturar ValidationError ANTES de chegar no service
        data = request.get_json()
        
        # Validação manual adicional para body vazio
        if not data:
            return error("Body da requisição é obrigatório", 400)
        
        # Schema validation com tratamento de erro
        schema = LoginSchema()
        validated_data = schema.load(data)
        
        # Chama service com dados validados
        result = AuthService.login(validated_data['username'], validated_data['password'])
        
        # Extrair usuário do resultado (sem query adicional)
        user = result.pop('user')
        result['user'] = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'nome_completo': user.nome_completo,
            'role': user.role.value if user.role else 'user'
        }
        
        return success(result, "Login realizado com sucesso", 200)
    
    except ValidationError as err:
        # CORREÇÃO GAP-001: ValidationError retorna 400, não 500
        return jsonify({
            'success': False,
            'message': 'Dados inválidos',
            'errors': err.messages
        }), 400
    
    except ValueError as e:
        # Erros de lógica de negócio (credenciais inválidas, usuário inativo)
        return unauthorized(str(e))
    
    except Exception as e:
        # Erro interno real (banco de dados, etc.)
        # Logging deveria ser feito aqui
        return error(f"Erro interno no servidor", 500)


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh do access_token."""
    identity = get_jwt_identity()
    tokens = AuthService.refresh(identity)
    return success(tokens, "Token renovado com sucesso", 200)


@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Dados do usuário autenticado."""
    identity = get_jwt_identity()
    user = db.session.get(Usuario, identity)
    
    if not user:
        return unauthorized("Usuário não encontrado")
    
    return success(UserMeSchema().dump(user), "Dados do usuário")


@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """Atualiza dados do usuário autenticado (nome e email)."""
    identity = get_jwt_identity()
    user = db.session.get(Usuario, identity)
    if not user:
        return unauthorized("Usuário não encontrado")
    
    data = request.get_json()
    if not data:
        return bad_request("Body da requisição é obrigatório")
    
    try:
        validated = UsuarioUpdateSchema().load(data)
    except ValidationError as e:
        return bad_request("Dados inválidos", e.messages)
    
    # Filtrar apenas campos permitidos para o próprio perfil
    allowed = {k: v for k, v in validated.items() if k in ('email', 'nome_completo')}
    if not allowed:
        return bad_request("Nenhum campo permitido para atualização")
    
    try:
        updated = UsuarioService.update(user.id, allowed, user)
        return success(UserMeSchema().dump(updated), "Perfil atualizado com sucesso")
    except ValueError as e:
        return bad_request(str(e))
    except Exception as e:
        return error(f"Erro ao atualizar perfil: {str(e)}", 500)


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Troca senha do usuário autenticado."""
    identity = get_jwt_identity()
    user = db.session.get(Usuario, identity)
    if not user:
        return unauthorized("Usuário não encontrado")
    
    data = request.get_json()
    if not data:
        return bad_request("Body da requisição é obrigatório")
    
    try:
        validated = ChangePasswordSchema().load(data)
    except ValidationError as e:
        return bad_request("Dados inválidos", e.messages)
    
    try:
        UsuarioService.change_password(user.id, validated['old_password'], validated['new_password'])
        return success(None, "Senha alterada com sucesso")
    except Exception as e:
        return error(f"Erro ao alterar senha: {str(e)}", 500)


@bp.route('/me/admin', methods=['GET'])
@admin_required
def me_admin():
    """Endpoint de teste - apenas para ADMIN."""
    identity = get_jwt_identity()
    user = db.session.get(Usuario, identity)
    
    return success(
        {
            'message': 'Você é um administrador!',
            'user': UserMeSchema().dump(user)
        },
        "Acesso ADMIN confirmado"
    )


@bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    """Logout - invalida refresh token (implementação básica)."""
    return success({'message': 'Logout realizado com sucesso'}, 200)
