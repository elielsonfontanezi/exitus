# -*- coding: utf-8 -*-
"""REL-FIX-001 — smoke dos params de período usados pelos relatórios FE."""
from datetime import date


class TestRelatoriosPeriodoParams:
    def test_transacoes_data_inicio_fim(self, auth_client):
        resp = auth_client.get(
            '/api/transacoes?data_inicio=2024-01-01&data_fim=2024-12-31&per_page=50',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'transacoes' in data
        assert isinstance(data['transacoes'], list)

    def test_ir_apuracao_mes_yyyy_mm(self, auth_client):
        mes = date.today().strftime('%Y-%m')
        resp = auth_client.get(
            f'/api/ir/apuracao?mes={mes}',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body is not None
