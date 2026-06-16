# -*- coding: utf-8 -*-
"""
EXITUS-ANOMALY-001 — Testes de integração para detecção de preços anômalos.

Cobre:
  - GET /api/cotacoes/anomalias (401, 400 params inválidos, 200 sem anomalias)
  - AnomalyService.detectar_anomalias — anomalia detectada, anomalia suprimida por evento
  - AnomalyService.verificar_ativo — detecção inline ao salvar cotação
"""
import uuid
import pytest
from decimal import Decimal
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Helpers de fixture
# ---------------------------------------------------------------------------

def _criar_ativo_teste(db, suffix=None):
    from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
    suffix = suffix or str(uuid.uuid4())[:8]
    a = Ativo(
        ticker=f'AX{suffix}',
        nome=f'Ativo Anomaly {suffix}',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('50.00'),
    )
    db.session.add(a)
    db.session.flush()
    return a


def _criar_historico(db, ativo_id, data: date, fechamento: float):
    from app.models.historico_preco import HistoricoPreco
    h = HistoricoPreco(
        ativoid=ativo_id,
        data=data,
        preco_fechamento=Decimal(str(fechamento)),
    )
    db.session.add(h)
    db.session.flush()
    return h


def _criar_evento_corporativo(db, ativo_id, data_evento: date):
    from app.models.evento_corporativo import EventoCorporativo, TipoEventoCorporativo
    e = EventoCorporativo(
        ativo_id=ativo_id,
        tipo_evento=TipoEventoCorporativo.SPLIT,
        data_evento=data_evento,
        proporcao='2:1',
        descricao='Split 2:1 teste',
    )
    db.session.add(e)
    db.session.flush()
    return e


# ---------------------------------------------------------------------------
# Testes do endpoint HTTP
# ---------------------------------------------------------------------------

class TestAnomaliaEndpoint:
    """GET /api/cotacoes/anomalias"""

    def test_401_sem_token(self, client):
        rv = client.get('/api/cotacoes/anomalias')
        assert rv.status_code == 401

    def test_400_limiar_invalido(self, auth_client):
        rv = auth_client.get('/api/cotacoes/anomalias?limiar=abc',
                              headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_400_data_ref_invalida(self, auth_client):
        rv = auth_client.get('/api/cotacoes/anomalias?data_ref=nao-e-data',
                              headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_200_sem_anomalias(self, auth_client):
        """Sem historico_preco suficiente: lista vazia, estrutura correta."""
        rv = auth_client.get('/api/cotacoes/anomalias?data_ref=2000-01-01',
                              headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True
        assert 'anomalias' in data['data']
        assert 'total' in data['data']
        assert 'limiar_pct' in data['data']
        assert 'data_ref' in data['data']
        assert data['data']['total'] == 0

    def test_200_limiar_customizado(self, auth_client):
        """Endpoint aceita limiar customizado e devolve limiar_pct correto."""
        rv = auth_client.get('/api/cotacoes/anomalias?limiar=15&data_ref=2000-01-01',
                              headers=auth_client._auth_headers)
        assert rv.status_code == 200
        assert rv.get_json()['data']['limiar_pct'] == 15.0


# ---------------------------------------------------------------------------
# Testes do AnomalyService
# ---------------------------------------------------------------------------

class TestAnomalyServiceDetectar:
    """AnomalyService.detectar_anomalias — lógica de detecção."""

    def test_sem_historico_nao_detecta(self, app):
        """Ativo sem historico_preco: nenhuma anomalia."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            db.session.commit()
            ativo_id = ativo.id

        try:
            from app.services.anomaly_service import AnomalyService
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date.today(),
            )
            assert anomalias == []
        finally:
            from app.models.ativo import Ativo
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_variacao_abaixo_limiar_nao_detecta(self, app):
        """Variação de 10% com limiar 20%: não é anomalia."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 6, 1)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 110.0)  # +10%
            db.session.commit()
            ativo_id, h1_id, h2_id = ativo.id, h1.id, h2.id

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 6, 1),
            )
            assert anomalias == []
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_variacao_acima_limiar_detecta_anomalia(self, app):
        """Variação de 30% sem evento corporativo: anomalia detectada."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 6, 1)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 130.0)  # +30%
            db.session.commit()
            ativo_id, h1_id, h2_id = ativo.id, h1.id, h2.id
            ticker = ativo.ticker

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 6, 1),
            )
            assert len(anomalias) == 1
            a = anomalias[0]
            assert a['ticker'] == ticker
            assert a['variacao_pct'] == pytest.approx(30.0, abs=0.01)
            assert a['direcao'] == 'alta'
            assert a['preco_atual'] == pytest.approx(130.0)
            assert a['preco_anterior'] == pytest.approx(100.0)
            assert a['tem_evento_corporativo'] is False
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_queda_acima_limiar_detectada(self, app):
        """Queda de 25% sem evento: direcao='queda'."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 7, 1)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 75.0)  # -25%
            db.session.commit()
            ativo_id, h1_id, h2_id = ativo.id, h1.id, h2.id

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 7, 1),
            )
            assert len(anomalias) == 1
            assert anomalias[0]['direcao'] == 'queda'
            assert anomalias[0]['variacao_pct'] == pytest.approx(25.0, abs=0.01)
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_evento_corporativo_suprime_anomalia(self, app):
        """Variação de 50% com split na janela: não deve ser anomalia."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 8, 1)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 50.0)   # -50% (split 2:1)
            ev = _criar_evento_corporativo(db, ativo.id, hoje)
            db.session.commit()
            ativo_id, h1_id, h2_id, ev_id = ativo.id, h1.id, h2.id, ev.id

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 8, 1),
            )
            assert anomalias == []
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            from app.models.evento_corporativo import EventoCorporativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            EventoCorporativo.query.filter_by(id=ev_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_evento_na_janela_suprime(self, app):
        """Evento a 3 dias da anomalia (dentro da janela de 5d) suprime."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 9, 10)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 140.0)   # +40%
            ev = _criar_evento_corporativo(db, ativo.id, hoje - timedelta(days=3))
            db.session.commit()
            ativo_id, h1_id, h2_id, ev_id = ativo.id, h1.id, h2.id, ev.id

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 9, 10),
            )
            assert anomalias == []
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            from app.models.evento_corporativo import EventoCorporativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            EventoCorporativo.query.filter_by(id=ev_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_evento_fora_da_janela_nao_suprime(self, app):
        """Evento a 10 dias (fora da janela de 5d): anomalia deve ser detectada."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            hoje = date(2025, 10, 20)
            ontem = hoje - timedelta(days=1)
            h1 = _criar_historico(db, ativo.id, ontem, 100.0)
            h2 = _criar_historico(db, ativo.id, hoje, 135.0)   # +35%
            ev = _criar_evento_corporativo(db, ativo.id, hoje - timedelta(days=10))
            db.session.commit()
            ativo_id, h1_id, h2_id, ev_id = ativo.id, h1.id, h2.id, ev.id

        try:
            anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                ativo_id=ativo_id,
                data_ref=date(2025, 10, 20),
            )
            assert len(anomalias) == 1
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            from app.models.evento_corporativo import EventoCorporativo
            HistoricoPreco.query.filter_by(id=h1_id).delete()
            HistoricoPreco.query.filter_by(id=h2_id).delete()
            EventoCorporativo.query.filter_by(id=ev_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_resultado_ordenado_por_variacao_desc(self, app):
        """Com dois ativos anômalos, o de maior variação vem primeiro."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            a1 = _criar_ativo_teste(db, suffix='A1')
            a2 = _criar_ativo_teste(db, suffix='A2')
            hoje = date(2025, 11, 1)
            ontem = hoje - timedelta(days=1)
            h1a = _criar_historico(db, a1.id, ontem, 100.0)
            h1b = _criar_historico(db, a1.id, hoje, 125.0)  # +25%
            h2a = _criar_historico(db, a2.id, ontem, 100.0)
            h2b = _criar_historico(db, a2.id, hoje, 160.0)  # +60%
            db.session.commit()
            ids = [a1.id, a2.id, h1a.id, h1b.id, h2a.id, h2b.id]

        try:
            # Consultar apenas esses dois ativos via detectar_anomalias sem filtro de ativo_id
            # mas usando data_ref pontual
            all_anomalias = AnomalyService.detectar_anomalias(
                limiar=Decimal('0.20'),
                data_ref=date(2025, 11, 1),
            )
            tickers_nossos = {a1.ticker, a2.ticker}
            anomalias = [x for x in all_anomalias if x['ticker'] in tickers_nossos]
            assert len(anomalias) == 2
            assert anomalias[0]['variacao_pct'] >= anomalias[1]['variacao_pct']
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            for hid in ids[2:]:
                HistoricoPreco.query.filter_by(id=hid).delete()
            for aid in ids[:2]:
                Ativo.query.filter_by(id=aid).delete()
            db.session.commit()


class TestAnomalyServiceVerificarAtivo:
    """AnomalyService.verificar_ativo — detecção inline."""

    def test_sem_historico_retorna_none(self, app):
        """Sem registros anteriores: verificar_ativo retorna None."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            db.session.commit()
            ativo_id = ativo.id

        try:
            result = AnomalyService.verificar_ativo(
                ativo_id=ativo_id,
                preco_novo=Decimal('130.00'),
                data_novo=date(2025, 6, 1),
            )
            assert result is None
        finally:
            from app.models.ativo import Ativo
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_variacao_normal_retorna_none(self, app):
        """Variação de 5%: verificar_ativo retorna None."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            ontem = date(2025, 6, 1)
            h = _criar_historico(db, ativo.id, ontem, 100.0)
            db.session.commit()
            ativo_id, h_id = ativo.id, h.id

        try:
            result = AnomalyService.verificar_ativo(
                ativo_id=ativo_id,
                preco_novo=Decimal('105.00'),
                data_novo=date(2025, 6, 2),
            )
            assert result is None
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            HistoricoPreco.query.filter_by(id=h_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_variacao_anomala_retorna_dict(self, app):
        """Variação de 40% sem evento: verificar_ativo retorna dict de anomalia."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            ontem = date(2025, 6, 1)
            h = _criar_historico(db, ativo.id, ontem, 100.0)
            db.session.commit()
            ativo_id, h_id = ativo.id, h.id

        try:
            result = AnomalyService.verificar_ativo(
                ativo_id=ativo_id,
                preco_novo=Decimal('140.00'),
                data_novo=date(2025, 6, 2),
            )
            assert result is not None
            assert result['variacao_pct'] == pytest.approx(40.0, abs=0.01)
            assert result['direcao'] == 'alta'
            assert result['tem_evento_corporativo'] is False
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            HistoricoPreco.query.filter_by(id=h_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()

    def test_evento_corporativo_suprime_inline(self, app):
        """Variação de 50% com split: verificar_ativo retorna None."""
        from app.database import db
        from app.services.anomaly_service import AnomalyService

        with app.app_context():
            ativo = _criar_ativo_teste(db)
            ontem = date(2025, 8, 1)
            hoje = date(2025, 8, 2)
            h = _criar_historico(db, ativo.id, ontem, 100.0)
            ev = _criar_evento_corporativo(db, ativo.id, hoje)
            db.session.commit()
            ativo_id, h_id, ev_id = ativo.id, h.id, ev.id

        try:
            result = AnomalyService.verificar_ativo(
                ativo_id=ativo_id,
                preco_novo=Decimal('50.00'),
                data_novo=hoje,
            )
            assert result is None
        finally:
            from app.models.historico_preco import HistoricoPreco
            from app.models.ativo import Ativo
            from app.models.evento_corporativo import EventoCorporativo
            HistoricoPreco.query.filter_by(id=h_id).delete()
            EventoCorporativo.query.filter_by(id=ev_id).delete()
            Ativo.query.filter_by(id=ativo_id).delete()
            db.session.commit()
