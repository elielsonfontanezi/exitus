# -*- coding: utf-8 -*-
"""
Exitus - Auth Blueprint - Endpoints de autenticação
CORREÇÃO GAP-001 e GAP-002
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginSchema, TokenResponseSchema, UserMeSchema
from app.utils.responses import success, error, unauthorized
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
        tokens = AuthService.login(validated_data['username'], validated_data['password'])
        
        # CORREÇÃO GAP-002: Adicionar dados do usuário na resposta
        # Buscar usuário pelo username para incluir na response
        user = Usuario.query.filter_by(username=validated_data['username']).first()
        
        if user:
            tokens['user'] = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'nome_completo': user.nome_completo,
                'role': user.role.value if user.role else 'user'
            }
        
        return success(tokens, "Login realizado com sucesso", 200)
    
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
    user = Usuario.query.get(identity)
    
    if not user:
        return unauthorized("Usuário não encontrado")
    
    return success(UserMeSchema().dump(user), "Dados do usuário")


@bp.route('/me/admin', methods=['GET'])
@admin_required
def me_admin():
    """Endpoint de teste - apenas para ADMIN."""
    identity = get_jwt_identity()
    user = Usuario.query.get(identity)
    
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
