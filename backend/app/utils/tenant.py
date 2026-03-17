# -*- coding: utf-8 -*-
"""
Exitus - Tenant Utilities
Helpers para multi-tenancy com assessoras
"""

from flask import g
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps


def get_current_assessora_id():
    """
    Retorna assessora_id do JWT atual
    
    Returns:
        str: UUID da assessora atual ou None
    """
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        return claims.get('assessora_id')
    except:
        return None


def require_assessora(f):
    """
    Decorator para garantir que assessora_id existe no JWT
    
    Usage:
        @require_assessora
        def minha_funcao():
            assessora_id = get_current_assessora_id()
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        assessora_id = get_current_assessora_id()
        if not assessora_id:
            return {'error': 'Assessora não identificada no token'}, 403
        g.assessora_id = assessora_id
        return f(*args, **kwargs)
    return decorated_function


def require_same_assessora(model_assessora_id):
    """
    Valida que o registro pertence à mesma assessora do usuário
    
    Args:
        model_assessora_id: UUID da assessora do registro
        
    Raises:
        PermissionError: Se assessoras não coincidem
    """
    current_assessora_id = get_current_assessora_id()
    
    if not current_assessora_id:
        return  # Sem assessora no token, permite acesso
    
    if model_assessora_id and str(model_assessora_id) != str(current_assessora_id):
        raise PermissionError("Acesso negado: registro pertence a outra assessora")


def filter_by_assessora(query, model_class):
    """
    Adiciona filtro de assessora_id à query se houver assessora no token
    
    Args:
        query: SQLAlchemy query object
        model_class: Classe do model (ex: Usuario, Portfolio)
        
    Returns:
        Query filtrada por assessora_id
        
    Usage:
        query = Usuario.query
        query = filter_by_assessora(query, Usuario)
        usuarios = query.all()
    """
    assessora_id = get_current_assessora_id()
    
    if assessora_id and hasattr(model_class, 'assessora_id'):
        query = query.filter_by(assessora_id=assessora_id)
    
    return query
