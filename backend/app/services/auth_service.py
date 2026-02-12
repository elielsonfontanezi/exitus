# -*- coding: utf-8 -*-
"""Exitus - Auth Service - Lógica de autenticação JWT"""

from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.database import db
from app.models import Usuario

class AuthService:
    @staticmethod
    def login(username, password):
        """
        Autentica usuário e retorna tokens.
        
        Returns:
            dict: {
                'access_token': str,
                'refresh_token': str,
                'token_type': 'Bearer',
                'expires_in': 3600
            }
        
        Raises:
            ValueError: Se credenciais inválidas ou usuário inativo
        """
        user = Usuario.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Credenciais inválidas")
        
        if not user.ativo:
            raise ValueError("Credenciais inválidas")  # Mensagem genérica por segurança
        
        # Gerar tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role.value}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
            # 'user' será adicionado na route (GAP-002)
        }

