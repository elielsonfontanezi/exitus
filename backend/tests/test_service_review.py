# -*- coding: utf-8 -*-
"""
Testes — EXITUS-SERVICE-REVIEW-001
Cobre: AnaliseService, ProjecaoRendaService, RelatorioPerformanceService, AuditoriaRelatorioService
"""

import uuid
import math
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.corretora import Corretora, TipoCorretora
from app.models.historico_preco import HistoricoPreco
from app.models.posicao import Posicao
from app.models.provento import Provento, TipoProvento
from app.models.usuario import Usuario, UserRole
from app.services.analise_service import AnaliseService
from app.services.auditoria_relatorio_service import AuditoriaRelatorioService
from app.services.projecao_renda_service import ProjecaoRendaService
from app.services.relatorio_performance_service import RelatorioPerformanceService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid():
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Fixture base
# ---------------------------------------------------------------------------

@pytest.fixture
def setup_sr(app):
    """Cria usuário, corretora, ativo, posição e histórico de preços."""
    suffix = _uid()

    u = Usuario(username=f'sr_{suffix}', email=f'sr_{suffix}@test.exitus', role=UserRole.ADMIN)
    u.set_password('teste123')
    _db.session.add(u)
    _db.session.flush()

    c = Corretora(nome=f'Cor SR {suffix}', tipo=TipoCorretora.CORRETORA, pais='BR', usuario_id=u.id)
    _db.session.add(c)
    _db.session.flush()

    a = Ativo(
        ticker=f'SR{suffix[:4]}',
        nome=f'Ativo SR {suffix}',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='B3', moeda='BRL',
        preco_atual=Decimal('50.00'),
        dividend_yield=Decimal('0.08'),
    )
    _db.session.add(a)
    _db.session.flush()

    pos = Posicao(
        usuario_id=u.id, corretora_id=c.id, ativo_id=a.id,
        quantidade=Decimal('100'), preco_medio=Decimal('40.00'),
        custo_total=Decimal('4000.00'),
        data_primeira_compra=date.today() - timedelta(days=365),
    )
    _db.session.add(pos)
    _db.session.flush()

    # Histórico de preços — 10 pontos
    hoje = date.today()
    for i in range(10):
        d = hoje - timedelta(days=10 - i)
        preco = Decimal(str(40 + i * 1.1))
        h = HistoricoPreco(
            ativoid=a.id, data=d,
            preco_fechamento=preco, preco_abertura=preco,
            preco_minimo=preco - Decimal('0.5'), preco_maximo=preco + Decimal('0.5'),
        )
        _db.session.add(h)

    _db.session.commit()

    yield {'usuario': u, 'corretora': c, 'ativo': a, 'posicao': pos}

    try:
        HistoricoPreco.query.filter_by(ativoid=a.id).delete()
        Provento.query.filter_by(ativo_id=a.id).delete()
        Posicao.query.filter_by(usuario_id=u.id).delete()
        Ativo.query.filter_by(id=a.id).delete()
        Corretora.query.filter_by(id=c.id).delete()
        Usuario.query.filter_by(id=u.id).delete()
        _db.session.commit()
    except Exception:
        _db.session.rollback()


# ---------------------------------------------------------------------------
# AnaliseService
# ---------------------------------------------------------------------------

class TestAnaliseService:

    def test_analisar_sem_posicoes_retorna_zero(self, app):
        resultado = AnaliseService.analisar_performance_portfolio(uuid.uuid4())
        assert resultado['total_posicoes'] == 0
        assert resultado['patrimonio_total'] == 0.0

    def test_analisar_com_posicao_retorna_patrimonio(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = AnaliseService.analisar_performance_portfolio(u.id)
        assert resultado['total_posicoes'] == 1
        assert resultado['patrimonio_total'] > 0

    def test_analisar_alocacao_soma_100(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = AnaliseService.analisar_performance_portfolio(u.id)
        total_pct = sum(resultado['alocacao_atual'].values())
        assert abs(total_pct - 100.0) < 0.01

    def test_comparar_benchmark_retorna_estrutura(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = AnaliseService.comparar_com_benchmark(u.id, 'CDI', '6m')
        assert 'benchmark' in resultado
        assert resultado['benchmark'] == 'CDI'
        assert 'portfolio_retorno' in resultado
        assert 'alpha' in resultado

    def test_correlacao_sem_historico_suficiente_retorna_vazio(self, app):
        resultado = AnaliseService.calcular_correlacao_ativos(uuid.uuid4())
        assert resultado['ativos'] == []
        assert resultado['correlacao'] == []

    def test_correlacao_helper_pearson(self, app):
        """Correlação perfeita positiva deve ser 1.0"""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        r = AnaliseService._correlacao(x, x)
        assert r is not None
        assert abs(r - 1.0) < 1e-6

    def test_correlacao_helper_negativa(self, app):
        """Correlação perfeita negativa deve ser -1.0"""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 4.0, 3.0, 2.0, 1.0]
        r = AnaliseService._correlacao(x, y)
        assert r is not None
        assert abs(r + 1.0) < 1e-6

    def test_correlacao_helper_constante_retorna_none(self, app):
        """Série constante (desvio = 0) retorna None"""
        x = [1.0, 1.0, 1.0]
        y = [2.0, 3.0, 4.0]
        r = AnaliseService._correlacao(x, y)
        assert r is None


# ---------------------------------------------------------------------------
# ProjecaoRendaService
# ---------------------------------------------------------------------------

class TestProjecaoRendaService:

    def test_projecao_sem_posicoes_retorna_lista_vazia(self, app):
        resultado = ProjecaoRendaService.calcular_projecao(uuid.uuid4(), meses=3)
        assert resultado == []

    def test_projecao_retorna_quantidade_meses(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = ProjecaoRendaService.calcular_projecao(u.id, meses=6)
        assert len(resultado) == 6

    def test_projecao_meses_corretos(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = ProjecaoRendaService.calcular_projecao(u.id, meses=3)
        hoje = date.today()
        # Primeiro mês deve ser o mês atual ou o próximo
        primeiro = resultado[0]['mes_ano']
        assert len(primeiro) == 7  # formato YYYY-MM
        assert primeiro[:4].isdigit()

    def test_projecao_renda_positiva_com_dy(self, app, setup_sr):
        """Ativo com DY=8% e 100 cotas a R$50 → renda = 100*50*0.08/12 = R$33.33/mês"""
        u = setup_sr['usuario']
        resultado = ProjecaoRendaService.calcular_projecao(u.id, meses=1)
        assert len(resultado) == 1
        assert resultado[0]['renda_total_mes'] > 0
        esperado = 100 * 50.0 * 0.08 / 12
        assert abs(resultado[0]['renda_total_mes'] - round(esperado, 2)) < 0.5

    def test_tipo_provento_predominante_default_dividendo(self, app, setup_sr):
        a = setup_sr['ativo']
        tipo = ProjecaoRendaService._tipo_provento_predominante(a.id)
        assert tipo == TipoProvento.DIVIDENDO


# ---------------------------------------------------------------------------
# RelatorioPerformanceService — helpers
# ---------------------------------------------------------------------------

class TestRelatorioPerformanceService:

    def test_volatilidade_serie_constante_zero(self, app):
        retornos = [0.0, 0.0, 0.0, 0.0, 0.0]
        vol = RelatorioPerformanceService._volatilidade_anualizada(retornos)
        assert vol == 0.0

    def test_volatilidade_serie_variavel(self, app):
        retornos = [0.01, -0.02, 0.015, -0.005, 0.008]
        vol = RelatorioPerformanceService._volatilidade_anualizada(retornos)
        assert vol is not None and vol > 0

    def test_max_drawdown_sem_queda(self, app):
        """Série crescente → drawdown = 0"""
        valores = [100.0, 110.0, 120.0, 130.0]
        dd = RelatorioPerformanceService._max_drawdown(valores)
        assert dd == 0.0

    def test_max_drawdown_com_queda(self, app):
        """Pico 100, vale 60 → drawdown = 40%"""
        valores = [80.0, 100.0, 60.0, 70.0]
        dd = RelatorioPerformanceService._max_drawdown(valores)
        assert dd is not None
        assert abs(dd - 0.40) < 0.001

    def test_max_drawdown_lista_unica(self, app):
        assert RelatorioPerformanceService._max_drawdown([100.0]) is None

    def test_calcular_sem_posicoes_retorna_nulos(self, app):
        di = date.today() - timedelta(days=30)
        df = date.today()
        resultado = RelatorioPerformanceService.calcular(uuid.uuid4(), di, df)
        assert resultado['indice_sharpe'] is None
        assert resultado['max_drawdown_percentual'] is None

    def test_calcular_com_historico_retorna_metricas(self, app, setup_sr):
        u = setup_sr['usuario']
        di = date.today() - timedelta(days=12)
        df = date.today()
        resultado = RelatorioPerformanceService.calcular(u.id, di, df)
        # Com 10 pontos de histórico, deve calcular algo
        assert 'retorno_bruto_percentual' in resultado
        assert 'indice_sharpe' in resultado

    def test_resultado_vazio_estrutura(self, app):
        di = date(2025, 1, 1)
        df = date(2025, 12, 31)
        r = RelatorioPerformanceService._resultado_vazio(di, df)
        assert r['periodo_inicio'] == '2025-01-01'
        assert r['periodo_fim'] == '2025-12-31'
        assert r['total_pontos_serie'] == 0


# ---------------------------------------------------------------------------
# AuditoriaRelatorioService — fix bug current_app.db
# ---------------------------------------------------------------------------

class TestAuditoriaRelatorioService:

    def test_create_nao_usa_current_app_db(self, app, setup_sr):
        """Verifica que o bug current_app.db foi corrigido — create() não levanta AttributeError"""
        u = setup_sr['usuario']
        from datetime import date

        try:
            resultado = AuditoriaRelatorioService.create(
                u.id,
                {
                    'tipo_relatorio': 'performance',
                    'data_inicio': date(2025, 1, 1),
                    'data_fim': date(2025, 12, 31),
                }
            )
            assert resultado is not None
        except AttributeError as e:
            pytest.fail(f"Bug current_app.db ainda presente: {e}")

    def test_list_by_usuario_retorna_lista(self, app, setup_sr):
        u = setup_sr['usuario']
        resultado = AuditoriaRelatorioService.list_by_usuario(u.id)
        assert isinstance(resultado, list)
