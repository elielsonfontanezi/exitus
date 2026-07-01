# -*- coding: utf-8 -*-
"""Testes NEW-19 — CRUD portfolios."""
from uuid import uuid4


class TestPortfoliosCrudEndpoint:
    def test_list_portfolios_requer_auth(self, client):
        resp = client.get('/api/portfolios')
        assert resp.status_code == 401

    def test_list_portfolios_estrutura(self, auth_client):
        resp = auth_client.get(
            '/api/portfolios',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'portfolios' in data
        assert isinstance(data['portfolios'], list)

    def test_create_portfolio(self, auth_client):
        nome = f'PF{uuid4().hex[:6]}'
        resp = auth_client.post(
            '/api/portfolios',
            headers=auth_client._auth_headers,
            json={
                'nome': nome,
                'objetivo': 'Teste',
                'descricao': 'Portfolio de teste',
            },
        )
        assert resp.status_code in (200, 201)
        body = resp.get_json()
        data = body.get('data', body)
        assert data.get('nome') == nome
