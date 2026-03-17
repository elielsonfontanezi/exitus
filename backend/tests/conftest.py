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
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise

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

    _db.session.rollback()
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
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(u)

    yield u

    # Limpeza feita por cleanup_test_data - não deletar aqui para evitar FK violation


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
        preco_teto=Decimal('50.00'),
        dividend_yield=Decimal('12.5'),
        p_l=Decimal('4.2'),
        p_vp=Decimal('1.1'),
    )
    _db.session.add(a)
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(a)

    yield a

    # Limpeza feita por cleanup_test_data - não deletar aqui para evitar FK violation


@pytest.fixture(scope='function', autouse=True)
def cleanup_test_data(app):
    """
    Limpa dados de teste após cada teste para evitar violações de FK.
    
    Este fixture roda ANTES do teardown dos outros fixtures (usuario_seed, ativo_seed, etc.)
    e deleta todas as transações, posições e movimentações criadas durante o teste.
    Isso garante que os fixtures possam deletar suas entidades sem violação de FK.
    """
    yield
    
    from app.models.transacao import Transacao
    from app.models.posicao import Posicao
    from app.models.movimentacao_caixa import MovimentacaoCaixa
    
    # Rollback para limpar transação pendente
    _db.session.rollback()
    
    # Deletar TODOS os dados criados durante o teste
    # Usar synchronize_session=False para forçar delete direto no banco
    # Ordem é crítica: dependências primeiro, depois entidades base
    try:
        from app.models.ativo import Ativo
        from app.models.corretora import Corretora
        from app.models.usuario import Usuario
        
        # 1. Deletar posições (dependem de ativo + corretora + usuario)
        Posicao.query.delete(synchronize_session=False)
        
        # 2. Deletar transações (dependem de ativo + corretora + usuario)
        Transacao.query.delete(synchronize_session=False)
        
        # 3. Deletar movimentações (dependem de corretora + usuario)
        MovimentacaoCaixa.query.delete(synchronize_session=False)
        
        # 4. Deletar corretoras (dependem de usuario)
        Corretora.query.delete(synchronize_session=False)
        
        # 5. Deletar ativos (independentes)
        Ativo.query.delete(synchronize_session=False)
        
        # 6. Deletar usuarios (base)
        Usuario.query.delete(synchronize_session=False)
        
        _db.session.commit()
    except Exception as e:
        _db.session.rollback()
        # Não propagar erro


@pytest.fixture(scope='function')
def corretora_seed(app, usuario_seed):
    """Corretora vinculada ao usuario_seed. DELETE no teardown."""
    from app.models.corretora import Corretora, TipoCorretora

    suffix = str(uuid_lib.uuid4())[:8]
    nome = f'Corretora Teste {suffix}'
    c = Corretora(
        nome=nome,
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=usuario_seed.id,
    )
    _db.session.add(c)
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(c)

    yield c

    # Limpeza feita por cleanup_test_data - não deletar aqui para evitar FK violation


@pytest.fixture(scope='function')
def transacao_seed(app, usuario_seed, ativo_seed, corretora_seed):
    """Transação vinculada aos seeds. Limpeza feita por cleanup_test_data."""
    from app.models.transacao import Transacao, TipoTransacao
    from datetime import datetime
    
    t = Transacao(
        usuario_id=usuario_seed.id,
        ativo_id=ativo_seed.id,
        corretora_id=corretora_seed.id,
        tipo=TipoTransacao.COMPRA,
        data_transacao=datetime(2024, 1, 15),
        quantidade=100,
        preco_unitario=25.50,
        valor_total=2550.00,
        taxa_corretagem=10.00,
        custos_totais=10.00,
        valor_liquido=2560.00
    )
    _db.session.add(t)
    try:
        _db.session.commit()
    except Exception:
        _db.session.rollback()
        raise
    _db.session.refresh(t)
    
    yield t
    
    # Não faz DELETE - cleanup_test_data já limpa todas as transações
