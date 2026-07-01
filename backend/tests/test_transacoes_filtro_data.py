# -*- coding: utf-8 -*-
"""Testes FIX-HIST-001 — filtro de data em transações."""
from datetime import datetime, timezone

from app.services.transacao_service import TransacaoService


class TestTransacoesFiltroData:
    def test_filtro_data_inclui_ultimo_dia(self, app, usuario_seed, ativo_seed, corretora_seed):
        """Transação no fim do dia deve aparecer quando data_fim é a mesma data (YYYY-MM-DD)."""
        with app.app_context():
            data_ref = datetime(2024, 6, 15, 18, 30, tzinfo=timezone.utc)
            TransacaoService.create(usuario_seed.id, {
                'tipo': 'compra',
                'ativo_id': ativo_seed.id,
                'corretora_id': corretora_seed.id,
                'data_transacao': data_ref.isoformat(),
                'quantidade': 10,
                'preco_unitario': 30.0,
                'taxa_corretagem': 0,
                'imposto': 0,
                'outros_custos': 0,
            })

            pagination = TransacaoService.get_all(
                usuario_seed.id,
                page=1,
                per_page=50,
                data_inicio=datetime(2024, 6, 15),
                data_fim=datetime(2024, 6, 15),
            )
            datas = [
                t.data_transacao.date().isoformat()
                for t in pagination.items
            ]
            assert '2024-06-15' in datas

    def test_list_com_filtro_data_endpoint(self, auth_client):
        resp = auth_client.get(
            '/api/transacoes?data_inicio=2024-01-01&data_fim=2024-12-31&per_page=50',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        data = body.get('data', body)
        assert 'transacoes' in data
        assert isinstance(data['transacoes'], list)
