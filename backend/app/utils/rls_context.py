# -*- coding: utf-8 -*-
"""
Exitus - RLS Context Manager
Helper para gerenciar contexto de Row-Level Security (RLS) no PostgreSQL

Este módulo fornece funções e decorators para setar o contexto de assessora_id
na sessão PostgreSQL, permitindo que as políticas RLS filtrem automaticamente
os dados no nível do banco de dados.
"""

from functools import wraps
from flask import g
from flask_jwt_extended import get_jwt
from sqlalchemy import text
from app.database import db
from app.utils.tenant import get_current_assessora_id


def set_rls_context(assessora_id: str = None):
    """
    Seta o contexto RLS na sessão PostgreSQL atual.
    
    Args:
        assessora_id: UUID da assessora (string). Se None, tenta obter do JWT.
    
    Example:
        set_rls_context('23c54cb4-cb0a-438f-b985-def21d70904e')
    """
    if assessora_id is None:
        assessora_id = get_current_assessora_id()
    
    if assessora_id:
        # Setar variável de sessão PostgreSQL usando SET LOCAL
        # SET LOCAL garante que a configuração dure até o fim da transação
        db.session.execute(
            text("SET LOCAL app.current_assessora_id = :assessora_id"),
            {'assessora_id': str(assessora_id)}
        )
        # Armazenar no contexto Flask para referência
        g.rls_assessora_id = str(assessora_id)


def clear_rls_context():
    """
    Limpa o contexto RLS da sessão PostgreSQL atual.
    
    Example:
        clear_rls_context()
    """
    db.session.execute(text("SELECT set_config('app.current_assessora_id', NULL, false)"))
    if hasattr(g, 'rls_assessora_id'):
        delattr(g, 'rls_assessora_id')


def get_rls_context() -> str:
    """
    Obtém o assessora_id atual do contexto RLS.
    
    Returns:
        str: UUID da assessora atual ou None
    
    Example:
        current_assessora = get_rls_context()
    """
    if hasattr(g, 'rls_assessora_id'):
        return g.rls_assessora_id
    return None


def with_rls_context(func):
    """
    Decorator que automaticamente seta o contexto RLS antes de executar a função.
    
    O assessora_id é extraído do JWT da requisição atual.
    
    Example:
        @app.route('/api/portfolios')
        @jwt_required()
        @with_rls_context
        def get_portfolios():
            # RLS já está ativo aqui
            return PortfolioService.get_all(current_user_id)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Setar contexto RLS antes da função
        set_rls_context()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Limpar contexto após a função (opcional, mas boa prática)
            # Comentado para manter contexto durante toda a request
            # clear_rls_context()
            pass
    return wrapper


class RLSContext:
    """
    Context manager para uso em blocos with.
    
    Example:
        with RLSContext('23c54cb4-cb0a-438f-b985-def21d70904e'):
            # Queries aqui terão RLS ativo
            portfolios = Portfolio.query.all()
    """
    
    def __init__(self, assessora_id: str = None):
        """
        Args:
            assessora_id: UUID da assessora. Se None, usa JWT atual.
        """
        self.assessora_id = assessora_id
        self.previous_context = None
    
    def __enter__(self):
        """Seta o contexto RLS ao entrar no bloco with"""
        self.previous_context = get_rls_context()
        set_rls_context(self.assessora_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restaura o contexto anterior ao sair do bloco with"""
        if self.previous_context:
            set_rls_context(self.previous_context)
        else:
            clear_rls_context()
        return False


def init_rls_for_request():
    """
    Inicializa RLS para a requisição atual.
    
    Deve ser chamado em um before_request handler do Flask.
    
    Example:
        @app.before_request
        def setup_rls():
            init_rls_for_request()
    """
    try:
        # Tentar obter assessora_id do JWT
        jwt_data = get_jwt()
        if jwt_data and 'assessora_id' in jwt_data:
            set_rls_context(jwt_data['assessora_id'])
    except Exception:
        # Se não houver JWT ou erro, não setar contexto
        # (útil para endpoints públicos)
        pass
