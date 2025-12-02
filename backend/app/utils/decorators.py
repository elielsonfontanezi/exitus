# -*- coding: utf-8 -*-
"""Exitus - Decorators - Controle de autorização por roles"""

from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Usuario
from app.utils.responses import forbidden, unauthorized

def admin_required(f):
    """Decorator: apenas usuários ADMIN."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        user = Usuario.query.get(identity)
        # ✅ CORREÇÃO: comparação case-insensitive
        if not user or user.role.value.upper() != 'ADMIN':
            return forbidden("Acesso restrito a administradores")
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator: usuários com roles específicas.
    
    Uso: @role_required('ADMIN', 'USER')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            identity = get_jwt_identity()
            user = Usuario.query.get(identity)
            # ✅ CORREÇÃO: comparação case-insensitive
            user_role = user.role.value.upper() if user else None
            roles_upper = [r.upper() for r in roles]
            
            if not user or user_role not in roles_upper:
                return forbidden(f"Acesso restrito às roles: {', '.join(roles)}")
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def owner_or_admin_required(resource_model):
    """Decorator: proprietário do recurso OU ADMIN.
    
    Uso: @owner_or_admin_required(Usuario)
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(resource_id, *args, **kwargs):
            identity = get_jwt_identity()
            current_user = Usuario.query.get(identity)
            
            if not current_user:
                return unauthorized("Usuário não encontrado")
            
            # ✅ CORREÇÃO: comparação case-insensitive
            if current_user.role.value.upper() == 'ADMIN':
                g.current_user = current_user
                return f(resource_id, *args, **kwargs)
            
            # Verificar se é o dono do recurso
            resource = resource_model.query.filter_by(usuario_id=identity).first()
            if not resource:
                return forbidden("Acesso negado ao recurso")
            
            g.current_user = current_user
            g.resource_owner = True
            return f(resource_id, *args, **kwargs)
        return decorated_function
    return decorator
