# -*- coding: utf-8 -*-
"""Exitus - Usuario Schemas - Validação Marshmallow"""

from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Usuario, UserRole
from app.database import db

class UsuarioCreateSchema(Schema):
    """Schema para criação de usuário"""
    username = fields.Str(required=True, validate=lambda x: 3 <= len(x) <= 50)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8, load_only=True)
    nome_completo = fields.Str(required=False, allow_none=True)
    role = fields.Str(required=False, default='user')
    
    @validates('username')
    def validate_username(self, value):
        """Valida se username já existe"""
        if Usuario.query.filter_by(username=value).first():
            raise ValidationError("Username já existe")
    
    @validates('email')
    def validate_email(self, value):
        """Valida se email já existe"""
        if Usuario.query.filter_by(email=value).first():
            raise ValidationError("Email já existe")
    
    @validates('role')
    def validate_role(self, value):
        """Valida se role é válida"""
        valid_roles = ['admin', 'user', 'readonly']
        if value.lower() not in valid_roles:
            raise ValidationError(f"Role inválida. Opções: {', '.join(valid_roles)}")

class UsuarioUpdateSchema(Schema):
    """Schema para atualização de usuário"""
    email = fields.Email(required=False)
    nome_completo = fields.Str(required=False, allow_none=True)
    ativo = fields.Bool(required=False)
    role = fields.Str(required=False)
    
    @validates('email')
    def validate_email_unique(self, value):
        """Valida se email já existe (exceto o próprio)"""
        # Validação adicional será feita no service
        pass
    
    @validates('role')
    def validate_role(self, value):
        """Valida se role é válida"""
        valid_roles = ['admin', 'user', 'readonly']
        if value.lower() not in valid_roles:
            raise ValidationError(f"Role inválida. Opções: {', '.join(valid_roles)}")

class ChangePasswordSchema(Schema):
    """Schema para troca de senha"""
    old_password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

class UsuarioResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de usuário (sem senha)"""
    class Meta:
        model = Usuario
        load_instance = False
        exclude = ('password_hash',)
    
    role = fields.Method("get_role_str")
    
    def get_role_str(self, obj):
        """Converte Enum para string"""
        return obj.role.value if obj.role else None
