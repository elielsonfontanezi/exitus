# -*- coding: utf-8 -*-
"""
EXITUS-TESTS-001 — conftest.py
Fixtures globais para testes pytest do Sistema Exitus.

Estratégia:
- PostgreSQL real (exitusdb_test) — paridade total com produção
- UUID, Enum, Numeric, timezone funcionam nativamente
- Schema pré-existente (pg_dump do exitusdb de produção)
- app fixture escopo session mantém app_context() ativo durante toda a suite
- Fixtures de function NÃO abrem novos app_context() — reutilizam o de sessão
- Isolamento via DELETE explícito no teardown de cada fixture
"""
import uuid as uuid_lib
import pytest
from decimal import Decimal
from app import create_app
from app.database import db as _db


# ---------------------------------------------------------------------------
# app — escopo de sessão: cria app e mantém contexto ativo para toda a suite
# ---------------------------------------------------------------------------
@pytest.fixture(scope='session')
def app():
    """Flask app apontando para exitusdb_test com contexto ativo na sessão."""
    application = create_app(testing=True)
    ctx = application.app_context()
    ctx.push()
    yield application
    _db.session.remove()
    ctx.pop()


# ---------------------------------------------------------------------------
# client — cliente HTTP sem autenticação
# ---------------------------------------------------------------------------
@pytest.fixture(scope='function')
def client(app):
    """Cliente HTTP para testes sem autenticação."""
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# auth_client — cliente HTTP autenticado com JWT de admin
# ---------------------------------------------------------------------------
@pytest.fixture(scope='function')
def auth_client(app):
    """
    Cliente HTTP com JWT de admin válido.
    Cria usuário com nome único por teste e faz DELETE no teardown.
    """
    from app.models.usuario import Usuario, UserRole

    suffix = str(uuid_lib.uuid4())[:8]
    username = f'ta{suffix}'

    u = Usuario(username=username, email=f'{username}@test.exitus', role=UserRole.ADMIN)
    u.set_password('senha_teste_123')
    _db.session.add(u)
    _db.session.commit()

    with app.test_client() as c:
        response = c.post('/api/auth/login', json={
            'username': username,
            'password': 'senha_teste_123',
        })
        assert response.status_code == 200, (
            f"Falha no login do fixture auth_client: {response.get_json()}"
        )
        token = response.get_json()['data']['access_token']
        c._auth_headers = {'Authorization': f'Bearer {token}'}
        yield c

    Usuario.query.filter_by(username=username).delete()
    _db.session.commit()


# ---------------------------------------------------------------------------
# Fixtures de entidades pré-criadas
# ---------------------------------------------------------------------------
@pytest.fixture(scope='function')
def usuario_seed(app):
    """Usuário admin com nome único. DELETE no teardown."""
    from app.models.usuario import Usuario, UserRole

    suffix = str(uuid_lib.uuid4())[:8]
    username = f'us{suffix}'
    u = Usuario(username=username, email=f'{username}@test.exitus', role=UserRole.ADMIN)
    u.set_password('senha_teste_123')
    _db.session.add(u)
    _db.session.commit()
    _db.session.refresh(u)

    yield u

    Usuario.query.filter_by(username=username).delete()
    _db.session.commit()


@pytest.fixture(scope='function')
def ativo_seed(app):
    """Ativo de teste com ticker único. DELETE no teardown."""
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo

    suffix = str(uuid_lib.uuid4().int)[:6]
    ticker = f'PT{suffix}'
    a = Ativo(
        ticker=ticker, nome=f'Ativo Seed {ticker}',
        tipo=TipoAtivo.ACAO, classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR', moeda='BRL',
        preco_atual=Decimal('38.50'),
        dividend_yield=Decimal('12.5'),
        p_l=Decimal('4.2'),
        p_vp=Decimal('1.1'),
    )
    _db.session.add(a)
    _db.session.commit()
    _db.session.refresh(a)

    yield a

    Ativo.query.filter_by(ticker=ticker).delete()
    _db.session.commit()


@pytest.fixture(scope='function')
def corretora_seed(app, usuario_seed):
    """Corretora vinculada ao usuario_seed. DELETE no teardown."""
    from app.models.corretora import Corretora, TipoCorretora

    suffix = str(uuid_lib.uuid4())[:8]
    nome = f'Corretora Teste {suffix}'
    c = Corretora(
        nome=nome,
        cnpj=f'00.000.000/000{suffix[:1]}-00',
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=usuario_seed.id,
    )
    _db.session.add(c)
    _db.session.commit()
    _db.session.refresh(c)

    yield c

    Corretora.query.filter_by(nome=nome).delete()
    _db.session.commit()
