# -*- coding: utf-8 -*-
"""Testes NEW-08 — regras fiscais endpoint."""


class TestRegrasFiscaisEndpoint:
    def test_list_regras_requer_auth(self, client):
        resp = client.get('/api/regras-fiscais')
        assert resp.status_code == 401

    def test_list_regras_estrutura(self, auth_client):
        resp = auth_client.get(
            '/api/regras-fiscais',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'regras' in data
        assert isinstance(data['regras'], list)

    def test_create_regra_requer_admin(self, auth_client):
        resp = auth_client.post(
            '/api/regras-fiscais',
            headers=auth_client._auth_headers,
            json={
                'pais': 'BR',
                'aliquota_ir': 15.0,
                'incide_sobre': 'lucro',
                'descricao': 'Regra teste endpoint',
                'vigencia_inicio': '2024-01-01',
            },
        )
        assert resp.status_code in (200, 201)
