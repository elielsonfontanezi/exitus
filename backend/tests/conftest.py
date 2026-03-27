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
def auth_client(app, assessora_seed):
    """
    Cliente HTTP com JWT de admin válido.
    Cria usuário com nome único por teste e faz DELETE no teardown.
    """
    from app.models.usuario import Usuario, UserRole

    suffix = str(uuid_lib.uuid4())[:8]
    username = f'ta{suffix}'

    u = Usuario(
        username=username,
        email=f'{username}@test.exitus',
        role=UserRole.ADMIN,
        assessora_id=assessora_seed.id
    )
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
def assessora_seed(app):
    """Assessora padrão para testes. DELETE no teardown."""
    from app.models.assessora import Assessora

    suffix = str(uuid_lib.uuid4())[:8]
    a = Assessora(
        nome=f'Assessora Teste {suffix}',
        razao_social=f'Assessora Teste LTDA {suffix}',
        cnpj=f'{uuid_lib.uuid4().int % 100000000000000:014d}',
        email=f'assessora{suffix}@test.exitus',
        ativo=True
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


@pytest.fixture(scope='function')
def usuario_seed(app, assessora_seed):
    """Usuário admin com nome único. DELETE no teardown."""
    from app.models.usuario import Usuario, UserRole

    suffix = str(uuid_lib.uuid4())[:8]
    username = f'us{suffix}'
    u = Usuario(
        username=username,
        email=f'{username}@test.exitus',
        role=UserRole.ADMIN,
        assessora_id=assessora_seed.id
    )
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
        from app.models.assessora import Assessora
        
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
        
        # 6. Deletar usuarios (dependem de assessora)
        Usuario.query.delete(synchronize_session=False)
        
        # 7. Deletar assessoras (base)
        Assessora.query.delete(synchronize_session=False)
        
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


# ---------------------------------------------------------------------------
# load_scenario — carrega cenário específico de teste
# ---------------------------------------------------------------------------
@pytest.fixture(scope='function')
def load_scenario(app, request):
    """
    Carrega um cenário específico de teste do diretório scenarios.
    
    Uso:
    @pytest.mark.parametrize("scenario", ["test_e2e", "test_ir", "test_stress"])
    def test_meu_cenario(app, load_scenario, scenario):
        # Cenário já está carregado no banco
        pass
    """
    scenario_name = request.param
    
    # Caminho do cenário (suporta execução via container ou direto)
    from pathlib import Path
    container_scenarios = Path('/app/seed_data/scenarios')
    local_scenarios = Path('./scripts/seed_data/scenarios')
    scenarios_dir = container_scenarios if container_scenarios.exists() else local_scenarios
    
    scenario_file = scenarios_dir / f'{scenario_name}.json'
    
    if not scenario_file.exists():
        pytest.fail(f"Cenário não encontrado: {scenario_file}")
    
    # Carregar e parsear JSON
    import json
    with open(scenario_file, 'r', encoding='utf-8') as f:
        scenario_data = json.load(f)
    
    # Popular banco com dados do cenário
    with app.app_context():
        from app.models.assessora import Assessora
        from app.models.usuario import Usuario, UserRole
        from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
        from app.models.corretora import Corretora, TipoCorretora
        from app.models.transacao import Transacao, TipoTransacao
        from app.models.provento import Provento, TipoProvento
        from app.models.movimentacao_caixa import MovimentacaoCaixa, TipoMovimentacao
        from datetime import datetime
        from decimal import Decimal
        
        # Mapeamento de usuários para assessoras
        assessora_map = {}
        usuario_map = {}
        ativo_map = {}
        corretora_map = {}
        
        try:
            # 1. Criar assessoras
            for assessora_data in scenario_data.get('assessoras', []):
                assessora = Assessora(
                    nome=assessora_data['nome'],
                    razao_social=assessora_data['razao_social'],
                    cnpj=assessora_data['cnpj'],
                    email=assessora_data.get('email'),
                    telefone=assessora_data.get('telefone'),
                    ativo=assessora_data.get('ativo', True)
                )
                _db.session.add(assessora)
                _db.session.flush()
                assessora_map[assessora.nome] = assessora
            
            # 2. Criar usuários
            for usuario_data in scenario_data.get('usuarios', []):
                # Encontrar assessora (primeira disponível se não especificada)
                assessora_id = None
                if assessora_map:
                    assessora_id = list(assessora_map.values())[0].id
                
                usuario = Usuario(
                    username=usuario_data['username'],
                    email=usuario_data['email'],
                    role=UserRole[usuario_data['role']],
                    nome_completo=usuario_data.get('nome_completo'),
                    assessora_id=assessora_id,
                    ativo=usuario_data.get('ativo', True)
                )
                usuario.set_password(usuario_data['password'])
                _db.session.add(usuario)
                _db.session.flush()
                usuario_map[usuario.username] = usuario
            
            # 3. Criar ativos
            for ativo_data in scenario_data.get('ativos', []):
                ativo = Ativo(
                    ticker=ativo_data['ticker'],
                    nome=ativo_data['nome'],
                    tipo=TipoAtivo[ativo_data['tipo']],
                    classe=ClasseAtivo[ativo_data['classe']],
                    mercado=ativo_data['mercado'],
                    moeda=ativo_data['moeda'],
                    pais=ativo_data['pais'],
                    preco_atual=Decimal(str(ativo_data.get('preco_atual', 0))),
                    preco_teto=Decimal(str(ativo_data.get('preco_teto', 0))),
                    dividend_yield=Decimal(str(ativo_data.get('dividend_yield', 0))),
                    p_l=Decimal(str(ativo_data.get('p_l', 0))),
                    p_vp=Decimal(str(ativo_data.get('p_vp', 0))),
                    taxa=Decimal(str(ativo_data.get('taxa', 0))) if ativo_data.get('taxa') else None,
                    vencimento=datetime.fromisoformat(ativo_data['vencimento']).date() if ativo_data.get('vencimento') else None,
                    observacoes=ativo_data.get('observacoes'),
                    ativo=ativo_data.get('ativo', True)
                )
                _db.session.add(ativo)
                _db.session.flush()
                ativo_map[ativo.ticker] = ativo
            
            # 4. Criar corretoras
            for corretora_data in scenario_data.get('corretoras', []):
                # Vincular a primeiro usuário se não especificado
                usuario_id = None
                if usuario_map:
                    usuario_id = list(usuario_map.values())[0].id
                
                corretora = Corretora(
                    nome=corretora_data['nome'],
                    cnpj=corretora_data['cnpj'],
                    tipo=TipoCorretora[corretora_data['tipo']],
                    pais=corretora_data['pais'],
                    usuario_id=usuario_id,
                    ativa=corretora_data.get('ativa', True)
                )
                _db.session.add(corretora)
                _db.session.flush()
                corretora_map[corretora.nome] = corretora
            
            # 5. Criar transações
            for transacao_data in scenario_data.get('transacoes', []):
                usuario = usuario_map.get(transacao_data['usuario'])
                ativo = ativo_map.get(transacao_data['ativo'])
                corretora = corretora_map.get(transacao_data['corretora'])
                
                if not all([usuario, ativo, corretora]):
                    pytest.fail(f"Dados incompletos para transação: {transacao_data}")
                
                quantidade = Decimal(str(transacao_data['quantidade']))
                preco_unitario = Decimal(str(transacao_data['preco_unitario']))
                valor_total = quantidade * preco_unitario
                custos = Decimal(str(transacao_data.get('custos_totais', 0)))
                
                tipo = TipoTransacao[transacao_data['tipo']]
                if tipo == TipoTransacao.COMPRA:
                    valor_liquido = valor_total + custos
                else:
                    valor_liquido = valor_total - custos
                
                transacao = Transacao(
                    usuario_id=usuario.id,
                    ativo_id=ativo.id,
                    corretora_id=corretora.id,
                    tipo=tipo,
                    data_transacao=datetime.fromisoformat(transacao_data['data_transacao']).date(),
                    quantidade=quantidade,
                    preco_unitario=preco_unitario,
                    valor_total=valor_total,
                    taxa_corretagem=Decimal(str(transacao_data.get('taxa_corretagem', 0))),
                    taxa_liquidacao=Decimal('0'),
                    emolumentos=Decimal('0'),
                    imposto=Decimal('0'),
                    outros_custos=Decimal('0'),
                    custos_totais=custos,
                    valor_liquido=valor_liquido
                )
                _db.session.add(transacao)
            
            # 6. Criar proventos
            for provento_data in scenario_data.get('proventos', []):
                ativo = ativo_map.get(provento_data['ativo'])
                if not ativo:
                    pytest.fail(f"Ativo não encontrado para provento: {provento_data['ativo']}")
                
                provento = Provento(
                    ativo_id=ativo.id,
                    tipo_provento=TipoProvento[provento_data['tipo_provento']],
                    data_com=datetime.fromisoformat(provento_data['data_com']).date(),
                    data_pagamento=datetime.fromisoformat(provento_data['data_pagamento']).date(),
                    valor_unitario=Decimal(str(provento_data['valor_unitario'])),
                    observacoes=provento_data.get('observacoes')
                )
                _db.session.add(provento)
            
            # 7. Criar movimentações de caixa
            for mov_data in scenario_data.get('movimentacoes_caixa', []):
                usuario = usuario_map.get(mov_data['usuario'])
                corretora = corretora_map.get(mov_data['corretora'])
                
                if not all([usuario, corretora]):
                    pytest.fail(f"Dados incompletos para movimentação: {mov_data}")
                
                movimentacao = MovimentacaoCaixa(
                    usuario_id=usuario.id,
                    corretora_id=corretora.id,
                    tipo=TipoMovimentacao[mov_data['tipo']],
                    data_movimentacao=datetime.fromisoformat(mov_data['data_movimentacao']).date(),
                    valor=Decimal(str(mov_data['valor'])),
                    observacoes=mov_data.get('observacoes')
                )
                _db.session.add(movimentacao)
            
            _db.session.commit()
            print(f"✅ Cenário '{scenario_name}' carregado com sucesso")
            
        except Exception as e:
            _db.session.rollback()
            pytest.fail(f"Erro ao carregar cenário '{scenario_name}': {e}")
    
    yield
    
    # Limpeza será feita pelo cleanup_test_data automático
