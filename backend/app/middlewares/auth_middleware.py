# -*- coding: utf-8 -*-
"""Exitus - Auth Middlewares - Middlewares JWT avançados"""

from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.database import db
from app.models import Usuario
from app.utils.responses import unauthorized, forbidden

def require_jwt():
    """Middleware: requer JWT válido em todas as rotas protegidas."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                g.jwt_identity = identity
                return f(*args, **kwargs)
            except Exception:
                return unauthorized("Token JWT inválido ou expirado"), 401
        return decorated_function
    return decorator

def rate_limit_by_user(max_requests=100):
    """Middleware: rate limiting por usuário (implementação básica)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identity = get_jwt_identity()
            # Implementação simples - pode usar Redis em produção
            request_count = getattr(g, 'request_count', 0)
            g.request_count = request_count + 1
            
            if g.request_count > max_requests:
                return forbidden("Limite de requisições excedido"), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
