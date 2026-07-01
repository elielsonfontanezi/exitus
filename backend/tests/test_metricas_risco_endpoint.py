# -*- coding: utf-8 -*-
"""Testes NEW-02 — métricas de risco endpoint."""


class TestMetricasRiscoEndpoint:
    def test_metricas_risco_requer_auth(self, client):
        resp = client.get('/api/portfolios/metricas-risco')
        assert resp.status_code == 401

    def test_metricas_risco_estrutura(self, auth_client):
        resp = auth_client.get(
            '/api/portfolios/metricas-risco',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'sharpe_ratio' in data
        assert 'max_drawdown' in data
