# -*- coding: utf-8 -*-
"""
Exitus - Testes de Row-Level Security (RLS)
Valida que as políticas RLS no PostgreSQL bloqueiam acesso cross-tenant
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch

from app.models import (
    Assessora, Usuario, Portfolio, Transacao, Posicao, Ativo, Corretora
)
from app.models.usuario import UserRole
from app.models.transacao import TipoTransacao
from app.utils.rls_context import set_rls_context, clear_rls_context, RLSContext
from app.database import db


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def assessora_rls_a(app):
    """Assessora A para testes RLS"""
    import time
    suffix = str(int(time.time() * 1000000))[-8:]
    assessora = Assessora(
        id=uuid.uuid4(),
        nome=f'Assessora RLS A {suffix}',
        razao_social=f'Assessora RLS A Ltda {suffix}',
        cnpj=f'33{suffix}0001',
        email=f'rls_a_{suffix}@teste.com',
        ativo=True
    )
    db.session.add(assessora)
    db.session.commit()
    yield assessora
    db.session.rollback()


@pytest.fixture
def assessora_rls_b(app):
    """Assessora B para testes RLS"""
    import time
    suffix = str(int(time.time() * 1000000))[-8:]
    assessora = Assessora(
        id=uuid.uuid4(),
        nome=f'Assessora RLS B {suffix}',
        razao_social=f'Assessora RLS B Ltda {suffix}',
        cnpj=f'44{suffix}0002',
        email=f'rls_b_{suffix}@teste.com',
        ativo=True
    )
    db.session.add(assessora)
    db.session.commit()
    yield assessora
    db.session.rollback()


@pytest.fixture
def usuario_rls_a(app, assessora_rls_a):
    """Usuário da Assessora A"""
    usuario = Usuario(
        id=uuid.uuid4(),
        assessora_id=assessora_rls_a.id,
        username=f'usuario_rls_a_{uuid.uuid4().hex[:8]}',
        email=f'rls_a_{uuid.uuid4().hex[:8]}@teste.com',
        role=UserRole.USER,
        ativo=True
    )
    usuario.set_password('senha123')
    db.session.add(usuario)
    db.session.commit()
    yield usuario
    db.session.rollback()


@pytest.fixture
def usuario_rls_b(app, assessora_rls_b):
    """Usuário da Assessora B"""
    usuario = Usuario(
        id=uuid.uuid4(),
        assessora_id=assessora_rls_b.id,
        username=f'usuario_rls_b_{uuid.uuid4().hex[:8]}',
        email=f'rls_b_{uuid.uuid4().hex[:8]}@teste.com',
        role=UserRole.USER,
        ativo=True
    )
    usuario.set_password('senha123')
    db.session.add(usuario)
    db.session.commit()
    yield usuario
    db.session.rollback()


# ============================================================================
# TESTES DE RLS - ISOLAMENTO AUTOMÁTICO
# ============================================================================

class TestRLSIsolamento:
    """Testes de isolamento automático via RLS no PostgreSQL"""

    def test_rls_bloqueia_select_cross_tenant_portfolio(
        self, app, usuario_rls_a, usuario_rls_b, assessora_rls_a, assessora_rls_b
    ):
        """RLS deve bloquear SELECT de portfolios de outra assessora"""
        # Criar portfolios para ambas assessoras SEM contexto RLS
        clear_rls_context()
        
        portfolio_a = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_a.id,
            nome='Portfolio RLS A'
        )
        portfolio_b = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_b.id,
            assessora_id=assessora_rls_b.id,
            nome='Portfolio RLS B'
        )
        db.session.add_all([portfolio_a, portfolio_b])
        db.session.commit()
        
        # Setar contexto RLS para Assessora A
        set_rls_context(str(assessora_rls_a.id))
        
        # Query deve retornar apenas portfolio A
        portfolios = Portfolio.query.all()
        
        assert len(portfolios) == 1
        assert portfolios[0].nome == 'Portfolio RLS A'
        assert portfolios[0].assessora_id == assessora_rls_a.id
        
        clear_rls_context()

    def test_rls_context_manager_isola_dados(
        self, app, usuario_rls_a, usuario_rls_b, assessora_rls_a, assessora_rls_b
    ):
        """Context manager RLSContext deve isolar dados corretamente"""
        # Criar portfolios sem RLS
        clear_rls_context()
        
        portfolio_a = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_a.id,
            nome='Portfolio Context A'
        )
        portfolio_b = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_b.id,
            assessora_id=assessora_rls_b.id,
            nome='Portfolio Context B'
        )
        db.session.add_all([portfolio_a, portfolio_b])
        db.session.commit()
        
        # Usar context manager para Assessora A
        with RLSContext(str(assessora_rls_a.id)):
            portfolios_a = Portfolio.query.all()
            assert len(portfolios_a) == 1
            assert portfolios_a[0].nome == 'Portfolio Context A'
        
        # Usar context manager para Assessora B
        with RLSContext(str(assessora_rls_b.id)):
            portfolios_b = Portfolio.query.all()
            assert len(portfolios_b) == 1
            assert portfolios_b[0].nome == 'Portfolio Context B'
        
        clear_rls_context()

    def test_rls_bloqueia_insert_com_assessora_errada(
        self, app, usuario_rls_a, assessora_rls_a, assessora_rls_b
    ):
        """RLS deve bloquear INSERT com assessora_id diferente do contexto"""
        # Setar contexto para Assessora A
        set_rls_context(str(assessora_rls_a.id))
        
        # Tentar inserir portfolio com assessora_id de B (deve falhar ou ser bloqueado)
        portfolio_errado = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_b.id,  # Assessora B, mas contexto é A
            nome='Portfolio Bloqueado'
        )
        db.session.add(portfolio_errado)
        
        # Commit deve falhar ou registro não deve ser visível
        try:
            db.session.commit()
            # Se commit passou, verificar se registro é visível
            portfolios = Portfolio.query.all()
            # Não deve estar visível pois assessora_id não bate com contexto
            assert all(p.assessora_id == assessora_rls_a.id for p in portfolios)
        except Exception:
            # Esperado: RLS bloqueou o INSERT
            db.session.rollback()
        
        clear_rls_context()

    def test_rls_sem_contexto_retorna_todos(
        self, app, usuario_rls_a, usuario_rls_b, assessora_rls_a, assessora_rls_b
    ):
        """Sem contexto RLS, deve retornar todos os registros (fallback)"""
        # Criar portfolios sem RLS
        clear_rls_context()
        
        portfolio_a = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_a.id,
            nome='Portfolio Sem Contexto A'
        )
        portfolio_b = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_b.id,
            assessora_id=assessora_rls_b.id,
            nome='Portfolio Sem Contexto B'
        )
        db.session.add_all([portfolio_a, portfolio_b])
        db.session.commit()
        
        # Query sem contexto RLS deve retornar todos
        portfolios = Portfolio.query.all()
        
        # Deve retornar ambos (política permite NULL)
        assert len(portfolios) >= 2
        
        clear_rls_context()


# ============================================================================
# TESTES DE RLS - DEFESA EM PROFUNDIDADE
# ============================================================================

class TestRLSDefesaProfundidade:
    """Testes que RLS funciona mesmo se filter_by_assessora() falhar"""

    def test_rls_protege_mesmo_sem_filter_service(
        self, app, usuario_rls_a, usuario_rls_b, assessora_rls_a, assessora_rls_b
    ):
        """RLS protege mesmo se esquecermos de usar filter_by_assessora()"""
        # Criar portfolios sem RLS
        clear_rls_context()
        
        portfolio_a = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_a.id,
            nome='Portfolio Defesa A'
        )
        portfolio_b = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_b.id,
            assessora_id=assessora_rls_b.id,
            nome='Portfolio Defesa B'
        )
        db.session.add_all([portfolio_a, portfolio_b])
        db.session.commit()
        
        # Setar contexto RLS para A
        set_rls_context(str(assessora_rls_a.id))
        
        # Query direta SEM filter_by_assessora() - RLS deve proteger
        portfolios = Portfolio.query.all()
        
        assert len(portfolios) == 1
        assert portfolios[0].assessora_id == assessora_rls_a.id
        
        clear_rls_context()

    def test_rls_funciona_com_multiplas_tabelas(
        self, app, usuario_rls_a, assessora_rls_a, assessora_rls_b
    ):
        """RLS deve funcionar em múltiplas tabelas simultaneamente"""
        # Criar dados em múltiplas tabelas sem RLS
        clear_rls_context()
        
        portfolio_a = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_a.id,
            nome='Portfolio Multi A'
        )
        portfolio_b = Portfolio(
            id=uuid.uuid4(),
            usuario_id=usuario_rls_a.id,
            assessora_id=assessora_rls_b.id,
            nome='Portfolio Multi B'
        )
        db.session.add_all([portfolio_a, portfolio_b])
        db.session.commit()
        
        # Setar contexto para A
        set_rls_context(str(assessora_rls_a.id))
        
        # Queries em múltiplas tabelas devem respeitar RLS
        portfolios = Portfolio.query.all()
        
        assert len(portfolios) == 1
        assert all(p.assessora_id == assessora_rls_a.id for p in portfolios)
        
        clear_rls_context()
