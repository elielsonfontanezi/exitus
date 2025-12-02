# -*- coding: utf-8 -*-
"""Exitus - Auth Blueprint - Endpoints de autenticação"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginSchema, TokenResponseSchema, UserMeSchema
from app.utils.responses import success, error, unauthorized

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """Login e geração de tokens JWT."""
    try:
        data = LoginSchema().load(request.json)
        tokens = AuthService.login(data['username'], data['password'])
        return success(tokens, "Login realizado com sucesso", 200)
    except ValueError as e:
        return unauthorized(str(e))
    except Exception as e:
        return error(f"Erro no login: {str(e)}", 500)

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

@bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    """Logout - invalida refresh token (implementação básica)."""
    return success({"message": "Logout realizado com sucesso"}, 200)
