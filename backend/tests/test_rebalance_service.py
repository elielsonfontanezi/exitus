# -*- coding: utf-8 -*-
"""
Testes unitários e de integração — RebalanceService (REBALANCE-001)

Cenários:
- Metas: obter (defaults), salvar (upsert), validação soma > 100%, classe inválida
- Desvio: cálculo com posições mock, valor_ajuste correto, precisa_rebalancear
- Sugestão: ações comprar/vender, carteira_balanceada quando dentro da tolerância
- Multi-tenant: usuário A não vê metas de B
- Endpoints GET/PUT /meta-alocacao e GET /rebalanceamento/sugestao
"""
import uuid
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.database import db as _db
from app.models.meta_alocacao import MetaAlocacao
from app.services.rebalance_service import RebalanceService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _criar_usuario(assessora_id):
    from app.models.usuario import Usuario, UserRole
    suffix = str(uuid.uuid4())[:8]
    u = Usuario(
        username=f'rb{suffix}',
        email=f'rb{suffix}@test.exitus',
        role=UserRole.ADMIN,
        assessora_id=assessora_id,
    )
    u.set_password('senha123')
    _db.session.add(u)
    _db.session.commit()
    _db.session.refresh(u)
    return u


def _limpar_metas(usuario_id):
    MetaAlocacao.query.filter_by(usuario_id=usuario_id).delete()
    _db.session.commit()


# ---------------------------------------------------------------------------
# Metas — obter e salvar
# ---------------------------------------------------------------------------

class TestObterMetas:
    def test_defaults_sem_metas(self, app, assessora_seed):
        """Sem metas registradas deve retornar as 3 classes com target=0."""
        u = _criar_usuario(assessora_seed.id)
        try:
            metas = RebalanceService.obter_metas(u.id)
            assert len(metas) == 3
            classes = {m['classe'] for m in metas}
            assert classes == {'renda_variavel', 'renda_fixa', 'cripto'}
            for m in metas:
                assert m['percentual_target'] == 0.0
        finally:
            _limpar_metas(u.id)

    def test_retorna_metas_salvas(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 60.0},
                {'classe': 'renda_fixa', 'percentual_target': 30.0},
            ])
            metas = RebalanceService.obter_metas(u.id)
            por_classe = {m['classe']: m for m in metas}
            assert por_classe['renda_variavel']['percentual_target'] == 60.0
            assert por_classe['renda_fixa']['percentual_target'] == 30.0
            assert por_classe['cripto']['percentual_target'] == 0.0
        finally:
            _limpar_metas(u.id)


class TestSalvarMetas:
    def test_upsert_atualiza_existente(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 60.0},
            ])
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 55.0},
            ])
            metas = RebalanceService.obter_metas(u.id)
            por_classe = {m['classe']: m for m in metas}
            assert por_classe['renda_variavel']['percentual_target'] == 55.0
            # Não deve haver duplicatas
            count = MetaAlocacao.query.filter_by(
                usuario_id=u.id, classe='renda_variavel'
            ).count()
            assert count == 1
        finally:
            _limpar_metas(u.id)

    def test_soma_acima_100_levanta_erro(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            with pytest.raises(ValueError, match="100%"):
                RebalanceService.salvar_metas(u.id, [
                    {'classe': 'renda_variavel', 'percentual_target': 70.0},
                    {'classe': 'renda_fixa', 'percentual_target': 40.0},
                ])
        finally:
            _limpar_metas(u.id)

    def test_classe_invalida_levanta_erro(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            with pytest.raises(ValueError, match="Classe inválida"):
                RebalanceService.salvar_metas(u.id, [
                    {'classe': 'imoveis', 'percentual_target': 30.0},
                ])
        finally:
            _limpar_metas(u.id)

    def test_tolerancia_customizada(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 60.0, 'tolerancia_pct': 5.0},
            ])
            metas = RebalanceService.obter_metas(u.id)
            por_classe = {m['classe']: m for m in metas}
            assert por_classe['renda_variavel']['tolerancia_pct'] == 5.0
        finally:
            _limpar_metas(u.id)


# ---------------------------------------------------------------------------
# Desvio
# ---------------------------------------------------------------------------

_ALOCACAO_MOCK = {
    'renda_variavel': {'valor': 75000.0, 'percentual': 75.0},
    'renda_fixa':     {'valor': 20000.0, 'percentual': 20.0},
    'cripto':         {'valor': 5000.0,  'percentual': 5.0},
}

class TestCalcularDesvio:
    def test_desvio_correto(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 60.0},
                {'classe': 'renda_fixa',     'percentual_target': 30.0},
                {'classe': 'cripto',         'percentual_target': 10.0},
            ])
            with patch(
                'app.services.portfolio_service.PortfolioService.get_alocacao',
                return_value=_ALOCACAO_MOCK
            ), patch(
                'app.services.rebalance_service.Posicao.query'
            ) as mock_q:
                mock_q.filter_by.return_value.count.return_value = 5
                resultado = RebalanceService.calcular_desvio(u.id)

            por_classe = {c['classe']: c for c in resultado['classes']}

            # renda_variavel: 75% atual vs 60% target → +15pp sobrealoc
            rv = por_classe['renda_variavel']
            assert rv['desvio_pct'] == pytest.approx(15.0, abs=0.1)
            assert rv['precisa_rebalancear'] is True
            assert rv['valor_ajuste'] < 0  # deve vender

            # renda_fixa: 20% vs 30% → -10pp subaloc
            rf = por_classe['renda_fixa']
            assert rf['desvio_pct'] == pytest.approx(-10.0, abs=0.1)
            assert rf['precisa_rebalancear'] is True
            assert rf['valor_ajuste'] > 0  # deve comprar

            # cripto: 5% vs 10% → -5pp — dentro da tolerância default (2%)? NÃO (5 > 2)
            cr = por_classe['cripto']
            assert cr['precisa_rebalancear'] is True
        finally:
            _limpar_metas(u.id)

    def test_dentro_tolerancia_nao_precisa(self, app, assessora_seed):
        """Desvio de 1pp com tolerância de 2pp → não precisa rebalancear."""
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 74.0, 'tolerancia_pct': 2.0},
            ])
            alocacao_proxima = {
                'renda_variavel': {'valor': 75000.0, 'percentual': 75.0},
                'renda_fixa':     {'valor': 20000.0, 'percentual': 20.0},
                'cripto':         {'valor': 5000.0,  'percentual': 5.0},
            }
            with patch(
                'app.services.portfolio_service.PortfolioService.get_alocacao',
                return_value=alocacao_proxima
            ), patch(
                'app.services.rebalance_service.Posicao.query'
            ) as mock_posicao:
                mock_posicao.filter_by.return_value.count.return_value = 3
                resultado = RebalanceService.calcular_desvio(u.id)

            por_classe = {c['classe']: c for c in resultado['classes']}
            # desvio = 75 - 74 = 1pp < tolerância 2pp
            assert por_classe['renda_variavel']['precisa_rebalancear'] is False
        finally:
            _limpar_metas(u.id)

    def test_patrimonio_total_somado(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            with patch(
                'app.services.portfolio_service.PortfolioService.get_alocacao',
                return_value=_ALOCACAO_MOCK
            ), patch(
                'app.services.rebalance_service.Posicao.query'
            ) as mock_posicao:
                mock_posicao.filter_by.return_value.count.return_value = 5
                resultado = RebalanceService.calcular_desvio(u.id)
            assert resultado['patrimonio_total'] == pytest.approx(100000.0, abs=1.0)
        finally:
            _limpar_metas(u.id)


# ---------------------------------------------------------------------------
# Sugestões
# ---------------------------------------------------------------------------

class TestSugerirRebalanceamento:
    def test_acoes_geradas(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 60.0},
                {'classe': 'renda_fixa',     'percentual_target': 30.0},
                {'classe': 'cripto',         'percentual_target': 10.0},
            ])
            with patch(
                'app.services.portfolio_service.PortfolioService.get_alocacao',
                return_value=_ALOCACAO_MOCK
            ), patch(
                'app.services.rebalance_service.Posicao.query'
            ) as mock_posicao:
                mock_posicao.filter_by.return_value.count.return_value = 5
                sugestao = RebalanceService.sugerir_rebalanceamento(u.id)

            assert sugestao['carteira_balanceada'] is False
            acoes = {a['classe']: a for a in sugestao['acoes']}
            assert acoes['renda_variavel']['direcao'] == 'vender'
            assert acoes['renda_fixa']['direcao'] == 'comprar'
            assert acoes['renda_variavel']['valor_brl'] == pytest.approx(15000.0, abs=1.0)
        finally:
            _limpar_metas(u.id)

    def test_carteira_balanceada(self, app, assessora_seed):
        """Se nenhuma classe estiver fora da tolerância, carteira_balanceada=True."""
        u = _criar_usuario(assessora_seed.id)
        try:
            # metas = 0% → nenhuma fora da tolerância (desvio = atual, mas tolerância default 2%
            # e sem metas, desvio = atual - 0 = grande → vai marcar como fora)
            # Para teste de balanceada: criar metas exatas com tolerância alta
            RebalanceService.salvar_metas(u.id, [
                {'classe': 'renda_variavel', 'percentual_target': 75.0, 'tolerancia_pct': 5.0},
                {'classe': 'renda_fixa',     'percentual_target': 20.0, 'tolerancia_pct': 5.0},
                {'classe': 'cripto',         'percentual_target': 5.0,  'tolerancia_pct': 5.0},
            ])
            with patch(
                'app.services.portfolio_service.PortfolioService.get_alocacao',
                return_value=_ALOCACAO_MOCK
            ), patch(
                'app.services.rebalance_service.Posicao.query'
            ) as mock_posicao:
                mock_posicao.filter_by.return_value.count.return_value = 5
                sugestao = RebalanceService.sugerir_rebalanceamento(u.id)

            assert sugestao['carteira_balanceada'] is True
            assert sugestao['total_acoes'] == 0
        finally:
            _limpar_metas(u.id)


# ---------------------------------------------------------------------------
# Multi-tenant
# ---------------------------------------------------------------------------

class TestMultiTenant:
    def test_usuario_a_nao_ve_metas_de_b(self, app, assessora_seed):
        u_a = _criar_usuario(assessora_seed.id)
        u_b = _criar_usuario(assessora_seed.id)
        try:
            RebalanceService.salvar_metas(u_a.id, [
                {'classe': 'renda_variavel', 'percentual_target': 80.0},
            ])
            metas_b = RebalanceService.obter_metas(u_b.id)
            por_classe = {m['classe']: m for m in metas_b}
            assert por_classe['renda_variavel']['percentual_target'] == 0.0
        finally:
            _limpar_metas(u_a.id)
            _limpar_metas(u_b.id)


# ---------------------------------------------------------------------------
# Endpoints HTTP
# ---------------------------------------------------------------------------

class TestEndpointsMeta:
    def test_get_meta_sem_auth_401(self, client):
        rv = client.get('/api/portfolios/meta-alocacao')
        assert rv.status_code == 401

    def test_put_meta_sem_auth_401(self, client):
        rv = client.put('/api/portfolios/meta-alocacao', json={'metas': []})
        assert rv.status_code == 401

    def test_get_sugestao_sem_auth_401(self, client):
        rv = client.get('/api/portfolios/rebalanceamento/sugestao')
        assert rv.status_code == 401

    def test_get_meta_retorna_tres_classes(self, auth_client, usuario_seed):
        rv = auth_client.get('/api/portfolios/meta-alocacao',
                             headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()
        assert 'data' in data
        metas = data['data']['metas']
        assert len(metas) == 3

    def test_put_meta_valida(self, auth_client, usuario_seed):
        payload = {
            'metas': [
                {'classe': 'renda_variavel', 'percentual_target': 60.0},
                {'classe': 'renda_fixa',     'percentual_target': 30.0},
                {'classe': 'cripto',         'percentual_target': 10.0},
            ]
        }
        rv = auth_client.put('/api/portfolios/meta-alocacao',
                             json=payload, headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['success'] is True

    def test_put_meta_soma_invalida_400(self, auth_client, usuario_seed):
        payload = {
            'metas': [
                {'classe': 'renda_variavel', 'percentual_target': 70.0},
                {'classe': 'renda_fixa',     'percentual_target': 50.0},
            ]
        }
        rv = auth_client.put('/api/portfolios/meta-alocacao',
                             json=payload, headers=auth_client._auth_headers)
        assert rv.status_code == 400

    def test_get_sugestao_retorna_estrutura(self, auth_client, usuario_seed):
        rv = auth_client.get('/api/portfolios/rebalanceamento/sugestao',
                             headers=auth_client._auth_headers)
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'acoes' in data
        assert 'carteira_balanceada' in data
        assert 'patrimonio_total' in data
