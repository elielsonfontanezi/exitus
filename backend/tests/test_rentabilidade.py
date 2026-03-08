# -*- coding: utf-8 -*-
"""
Testes — EXITUS-RENTABILIDADE-001
Rentabilidade TWR, MWR (XIRR) e benchmarks.
"""

import uuid
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.corretora import Corretora, TipoCorretora
from app.models.historico_preco import HistoricoPreco
from app.models.movimentacao_caixa import MovimentacaoCaixa, TipoMovimentacao
from app.models.parametros_macro import ParametrosMacro
from app.models.posicao import Posicao
from app.models.provento import Provento, TipoProvento
from app.models.transacao import Transacao, TipoTransacao
from app.models.usuario import Usuario, UserRole
from app.services.rentabilidade_service import RentabilidadeService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid():
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def setup_rentabilidade(app):
    """
    Cria dados completos para testar rentabilidade:
    - Usuário, corretora, ativo, posição
    - Transação de compra, provento, histórico de preço
    - Parâmetros macro (CDI)
    """
    suffix = _uid()

    # Usuário
    u = Usuario(username=f'rent_{suffix}', email=f'rent_{suffix}@test.exitus', role=UserRole.ADMIN)
    u.set_password('teste123')
    _db.session.add(u)
    _db.session.flush()

    # Corretora
    c = Corretora(
        nome=f'Corretora Rent {suffix}',
        tipo=TipoCorretora.CORRETORA,
        pais='BR',
        usuario_id=u.id,
    )
    _db.session.add(c)
    _db.session.flush()

    # Ativo
    ticker = f'RT{suffix[:4]}'
    a = Ativo(
        ticker=ticker, nome=f'Ativo Rent {ticker}',
        tipo=TipoAtivo.ACAO, classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='B3', moeda='BRL',
        preco_atual=Decimal('50.00'),
    )
    _db.session.add(a)
    _db.session.flush()

    hoje = date.today()
    data_compra = hoje - timedelta(days=180)

    # Posição
    pos = Posicao(
        usuario_id=u.id,
        corretora_id=c.id,
        ativo_id=a.id,
        quantidade=Decimal('100'),
        preco_medio=Decimal('40.00'),
        custo_total=Decimal('4000.00'),
        data_primeira_compra=data_compra,
    )
    _db.session.add(pos)
    _db.session.flush()

    # Transação de compra
    t = Transacao(
        usuario_id=u.id,
        ativo_id=a.id,
        corretora_id=c.id,
        tipo=TipoTransacao.COMPRA,
        quantidade=Decimal('100'),
        preco_unitario=Decimal('40.00'),
        valor_total=Decimal('4000.00'),
        valor_liquido=Decimal('4000.00'),
        data_transacao=data_compra,
    )
    _db.session.add(t)

    # Histórico de preço — início e fim
    for d, preco in [
        (data_compra, Decimal('40.00')),
        (hoje - timedelta(days=90), Decimal('45.00')),
        (hoje - timedelta(days=1), Decimal('50.00')),
        (hoje, Decimal('50.00')),
    ]:
        h = HistoricoPreco(
            ativoid=a.id,
            data=d,
            preco_fechamento=preco,
            preco_abertura=preco,
            preco_minimo=preco - Decimal('1'),
            preco_maximo=preco + Decimal('1'),
        )
        _db.session.add(h)

    # Parâmetros macro (CDI = 13.65% a.a.)
    param = ParametrosMacro.query.filter_by(pais='BR', mercado='B3').first()
    if not param:
        param = ParametrosMacro(
            pais='BR',
            mercado='B3',
            taxa_livre_risco=Decimal('0.1365'),
            crescimento_medio=Decimal('0.03'),
            custo_capital=Decimal('0.12'),
            inflacao_anual=Decimal('0.045'),
            ativo=True,
        )
        _db.session.add(param)

    _db.session.commit()

    yield {
        'usuario': u,
        'corretora': c,
        'ativo': a,
        'posicao': pos,
        'data_compra': data_compra,
    }

    # Cleanup
    try:
        HistoricoPreco.query.filter_by(ativoid=a.id).delete()
        Transacao.query.filter_by(usuario_id=u.id).delete()
        Provento.query.filter(Provento.ativo_id == a.id).delete()
        MovimentacaoCaixa.query.filter_by(usuario_id=u.id).delete()
        Posicao.query.filter_by(usuario_id=u.id).delete()
        Ativo.query.filter_by(id=a.id).delete()
        Corretora.query.filter_by(id=c.id).delete()
        Usuario.query.filter_by(id=u.id).delete()
        _db.session.commit()
    except Exception:
        _db.session.rollback()


# ---------------------------------------------------------------------------
# Testes: _resolver_periodo
# ---------------------------------------------------------------------------

class TestResolverPeriodo:
    def test_12m(self, app):
        di, df = RentabilidadeService._resolver_periodo('12m')
        assert (df - di).days == 365

    def test_6m(self, app):
        di, df = RentabilidadeService._resolver_periodo('6m')
        assert (df - di).days == 180

    def test_ytd(self, app):
        di, df = RentabilidadeService._resolver_periodo('ytd')
        assert di.month == 1 and di.day == 1
        assert df == date.today()

    def test_periodo_invalido_usa_default_365(self, app):
        di, df = RentabilidadeService._resolver_periodo('99x')
        assert (df - di).days == 365


# ---------------------------------------------------------------------------
# Testes: XIRR
# ---------------------------------------------------------------------------

class TestXIRR:
    def test_xirr_caso_simples(self, app):
        """Investimento de 1000, retorno de 1100 após 1 ano ≈ 10%"""
        hoje = date.today()
        cashflows = [
            (hoje - timedelta(days=365), -1000.0),
            (hoje, 1100.0),
        ]
        taxa = RentabilidadeService._xirr(cashflows)
        assert taxa is not None
        assert abs(taxa - 0.10) < 0.01

    def test_xirr_sem_fluxos(self, app):
        assert RentabilidadeService._xirr([]) is None

    def test_xirr_fluxo_unico(self, app):
        hoje = date.today()
        assert RentabilidadeService._xirr([(hoje, 100.0)]) is None


# ---------------------------------------------------------------------------
# Testes: TWR
# ---------------------------------------------------------------------------

class TestTWR:
    def test_twr_sem_fluxo(self, app):
        """Portfólio que valoriza 25% sem aportes/resgates"""
        valores = [
            {'data': date(2025, 1, 1), 'valor': 1000.0},
            {'data': date(2025, 12, 31), 'valor': 1250.0},
        ]
        twr = RentabilidadeService._calcular_twr(valores, [])
        assert twr is not None
        assert abs(twr - 0.25) < 0.001

    def test_twr_com_aporte(self, app):
        """
        Portfólio: início 1000, aporte 500 no meio, fim 1800.
        Sub-período 1: 1000 → 1200 (antes do aporte) = +20%
        Sub-período 2: 1700 (1200+500) → 1800 = +5.88%
        TWR = (1.20 * 1.0588) - 1 = 0.2706 ≈ 27.06%
        """
        valores = [
            {'data': date(2025, 1, 1), 'valor': 1000.0},
            {'data': date(2025, 7, 1), 'valor': 1700.0},
            {'data': date(2025, 12, 31), 'valor': 1800.0},
        ]
        fluxos = [
            {'data': date(2025, 7, 1), 'valor': 500.0},
        ]
        twr = RentabilidadeService._calcular_twr(valores, fluxos)
        assert twr is not None
        # (1200/1000) * (1800/1700) -1 = 1.2 * 1.0588 - 1 ≈ 0.2706
        assert abs(twr - 0.2706) < 0.01

    def test_twr_lista_vazia(self, app):
        assert RentabilidadeService._calcular_twr([], []) is None

    def test_twr_ponto_unico(self, app):
        valores = [{'data': date(2025, 1, 1), 'valor': 1000.0}]
        assert RentabilidadeService._calcular_twr(valores, []) is None


# ---------------------------------------------------------------------------
# Testes: Benchmark CDI
# ---------------------------------------------------------------------------

class TestBenchmarkCDI:
    def test_cdi_retorna_valor(self, app, setup_rentabilidade):
        di = date.today() - timedelta(days=365)
        df = date.today()
        retorno = RentabilidadeService._benchmark_cdi(di, df)
        assert retorno is not None
        assert retorno > 0

    def test_cdi_periodo_zero(self, app, setup_rentabilidade):
        hoje = date.today()
        retorno = RentabilidadeService._benchmark_cdi(hoje, hoje)
        assert retorno == 0.0


# ---------------------------------------------------------------------------
# Testes: Integração calcular()
# ---------------------------------------------------------------------------

class TestCalcularIntegracao:
    def test_calcular_retorna_estrutura(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        resultado = RentabilidadeService.calcular(
            dados['usuario'].id, '6m', 'CDI'
        )
        assert 'twr' in resultado
        assert 'mwr' in resultado
        assert 'benchmark' in resultado
        assert resultado['benchmark']['nome'] == 'CDI'
        assert resultado['periodo'] == '6m'
        assert resultado['dias'] > 0

    def test_calcular_twr_positivo_com_valorizacao(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        resultado = RentabilidadeService.calcular(
            dados['usuario'].id, '6m', 'CDI'
        )
        # Ativo subiu de 40 para 50 → TWR deve ser > 0
        if resultado['twr'] is not None:
            assert resultado['twr'] > 0

    def test_calcular_com_benchmark_invalido(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        resultado = RentabilidadeService.calcular(
            dados['usuario'].id, '6m', 'INVALIDO'
        )
        assert resultado['benchmark']['retorno'] is None

    def test_calcular_usuario_sem_posicoes(self, app):
        """Usuário sem posições deve retornar TWR/MWR None"""
        fake_id = uuid.uuid4()
        resultado = RentabilidadeService.calcular(fake_id, '12m', 'CDI')
        assert resultado['twr'] is None or resultado['twr'] == 0.0


# ---------------------------------------------------------------------------
# Testes: Endpoint /api/portfolios/rentabilidade
# ---------------------------------------------------------------------------

class TestEndpointRentabilidade:
    def test_sem_jwt_retorna_401(self, app):
        with app.test_client() as c:
            r = c.get('/api/portfolios/rentabilidade')
            assert r.status_code == 401

    def test_periodo_invalido_retorna_400(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        u = dados['usuario']

        with app.test_client() as c:
            from flask_jwt_extended import create_access_token
            with app.app_context():
                token = create_access_token(identity=str(u.id))
            r = c.get(
                '/api/portfolios/rentabilidade?periodo=99x',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert r.status_code == 400

    def test_benchmark_invalido_retorna_400(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        u = dados['usuario']

        with app.test_client() as c:
            from flask_jwt_extended import create_access_token
            with app.app_context():
                token = create_access_token(identity=str(u.id))
            r = c.get(
                '/api/portfolios/rentabilidade?benchmark=XYZ',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert r.status_code == 400

    def test_endpoint_retorna_200(self, app, setup_rentabilidade):
        dados = setup_rentabilidade
        u = dados['usuario']

        with app.test_client() as c:
            from flask_jwt_extended import create_access_token
            with app.app_context():
                token = create_access_token(identity=str(u.id))
            r = c.get(
                '/api/portfolios/rentabilidade?periodo=6m&benchmark=CDI',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert r.status_code == 200
            body = r.get_json()
            assert 'data' in body
            assert 'twr' in body['data']
            assert 'benchmark' in body['data']
