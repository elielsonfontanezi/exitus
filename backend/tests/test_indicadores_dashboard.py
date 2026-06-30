# -*- coding: utf-8 -*-
"""Testes NEW-06 / FEAT-010 — indicadores macro do dashboard."""
import pytest

from app.services.indicadores_service import IndicadoresService


class TestIndicadoresDashboard:
    def test_endpoint_dashboard(self, auth_client):
        resp = auth_client.get(
            '/api/indicadores/dashboard',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        data = body['data']
        assert 'cdi_anual' in data
        assert 'ibovespa_anual' in data
        assert 'ipca_anual' in data
        assert 'selic_anual' in data
        assert 'fontes' in data
        assert data['cdi_anual'] > 0
        assert data['ibovespa_anual'] > 0

    def test_service_retorna_estrutura(self, app):
        with app.app_context():
            dados = IndicadoresService.get_dashboard_indicadores()
            assert isinstance(dados['cdi_anual'], float)
            assert isinstance(dados['ipca_anual'], float)
            assert dados['fontes']['cdi'] in ('parametros_macro', 'fallback')

    def test_endpoint_requer_auth(self, client):
        resp = client.get('/api/indicadores/dashboard')
        assert resp.status_code == 401
