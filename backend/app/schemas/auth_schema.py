# -*- coding: utf-8 -*-
"""
Exitus - Auth Schemas - Validação Marshmallow
CORREÇÃO GAP-001: Melhorar mensagens de erro de validação
"""
from marshmallow import Schema, fields, validates, ValidationError, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Usuario


class LoginSchema(Schema):
    """
    Schema para validação de login.
    
    CORREÇÃO GAP-001:
    - Validação mais clara com mensagens customizadas
    - Pre-load hook para validar campos vazios antes do schema
    """
    username = fields.Str(
        required=True,
        validate=lambda x: len(x) >= 3,
        error_messages={
            'required': 'Username é obrigatório',
            'null': 'Username não pode ser nulo',
            'invalid': 'Username inválido'
        }
    )
    password = fields.Str(
        required=True,
        validate=lambda x: len(x) >= 6,
        error_messages={
            'required': 'Password é obrigatório',
            'null': 'Password não pode ser nulo',
            'invalid': 'Password inválido'
        }
    )

    @pre_load
    def strip_whitespace(self, data, **kwargs):
        """
        Remove espaços em branco e valida campos vazios ANTES do schema.
        Previne ValidationError não tratado que causa 500.
        """
        if not isinstance(data, dict):
            raise ValidationError("Body da requisição deve ser um objeto JSON")
        
        # Valida se campos existem e não são vazios
        username = data.get('username', '').strip() if data.get('username') else ''
        password = data.get('password', '').strip() if data.get('password') else ''
        
        if not username or not password:
            errors = {}
            if not username:
                errors['username'] = ['Username é obrigatório e não pode estar vazio']
            if not password:
                errors['password'] = ['Password é obrigatório e não pode estar vazio']
            raise ValidationError(errors)
        
        return {'username': username, 'password': password}

    @validates('username')
    def validate_username(self, value):
        """Valida comprimento mínimo do username."""
        if len(value) < 3:
            raise ValidationError('Username deve ter pelo menos 3 caracteres')


class TokenResponseSchema(Schema):
    """
    Schema para resposta de tokens.
    
    CORREÇÃO GAP-002: Adicionar campo 'user' na resposta
    """
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
    token_type = fields.Str(dump_only=True)
    expires_in = fields.Int(dump_only=True)
    user = fields.Dict(dump_only=True)  # <-- NOVO: GAP-002


class UserMeSchema(SQLAlchemyAutoSchema):
    """Schema para dados do usuário logado (sem senha)."""
    class Meta:
        model = Usuario
        load_instance = False
        exclude = ('password_hash', 'role')
    
    role = fields.Method('get_role_str')
    
    def get_role_str(self, obj):
        """Converte Enum para string."""
        return obj.role.value if obj.role else None
