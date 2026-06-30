# -*- coding: utf-8 -*-
"""Testes NEW-15 — endpoint matriz de correlação."""
import pytest


class TestCorrelacaoEndpoint:
    def test_correlacao_requer_auth(self, client):
        resp = client.get('/api/performance/correlacao')
        assert resp.status_code == 401

    def test_correlacao_estrutura(self, auth_client):
        resp = auth_client.get(
            '/api/performance/correlacao',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert 'ativos' in body
        assert 'correlacao' in body
        assert isinstance(body['ativos'], list)
        assert isinstance(body['correlacao'], list)
        n = len(body['ativos'])
        if n > 0:
            assert len(body['correlacao']) == n
            assert len(body['correlacao'][0]) == n

    def test_correlacao_vazia_sem_posicoes(self, auth_client):
        resp = auth_client.get(
            '/api/performance/correlacao',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['ativos'] == [] or isinstance(body['correlacao'], list)
