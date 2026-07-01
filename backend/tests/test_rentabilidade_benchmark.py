# -*- coding: utf-8 -*-
"""Testes NEW-16 — benchmark na resposta de rentabilidade."""


class TestRentabilidadeBenchmark:
    def test_resposta_contem_benchmark(self, auth_client):
        resp = auth_client.get(
            '/api/portfolios/rentabilidade?periodo=6m&benchmark=IBOV',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'benchmark' in data
        assert data['benchmark'].get('nome') == 'IBOV'
