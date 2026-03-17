# -*- coding: utf-8 -*-
"""Exitus - Auth Service - Lógica de autenticação JWT"""

from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from app.database import db
from app.models import Usuario
from app.services.auditoria_service import AuditoriaService

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
            # Auditoria de falha de login
            if user:
                AuditoriaService.registrar_login(
                    usuario_id=user.id,
                    sucesso=False,
                    mensagem="Senha incorreta"
                )
            raise ValueError("Credenciais inválidas")
        
        if not user.ativo:
            # Auditoria de falha de login (usuário inativo)
            AuditoriaService.registrar_login(
                usuario_id=user.id,
                sucesso=False,
                mensagem="Usuário inativo"
            )
            raise ValueError("Credenciais inválidas")  # Mensagem genérica por segurança
        
        # Gerar tokens com assessora_id
        additional_claims = {'role': user.role.value}
        if user.assessora_id:
            additional_claims['assessora_id'] = str(user.assessora_id)
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Auditoria de login bem-sucedido
        AuditoriaService.registrar_login(
            usuario_id=user.id,
            sucesso=True
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': user
        }

