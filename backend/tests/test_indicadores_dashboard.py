# -*- coding: utf-8 -*-
"""Testes NEW-06 / FEAT-010 — indicadores macro do dashboard."""
from unittest.mock import patch

import pytest

from app.services.indicadores_service import IndicadoresService
from app.services.macro_fetch_service import clear_macro_cache


class TestIndicadoresDashboard:
    def setup_method(self):
        clear_macro_cache()

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
            assert dados['fontes']['cdi'] in (
                'parametros_macro', 'fallback', 'api_externa'
            )

    @patch('app.services.indicadores_service.fetch_macro_indicators')
    def test_service_prioriza_api_externa(self, mock_fetch, app):
        mock_fetch.return_value = {
            'cdi_anual': 14.75,
            'selic_anual': 14.25,
            'ipca_anual': 4.72,
            'ibovespa_anual': 23.0,
        }
        with app.app_context():
            dados = IndicadoresService.get_dashboard_indicadores()
            assert dados['cdi_anual'] == 14.75
            assert dados['ibovespa_anual'] == 23.0
            assert dados['fontes']['cdi'] == 'api_externa'
            assert dados['fontes']['ibovespa'] == 'api_externa'

    def test_endpoint_requer_auth(self, client):
        resp = client.get('/api/indicadores/dashboard')
        assert resp.status_code == 401
