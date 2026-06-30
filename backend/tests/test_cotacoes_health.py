# -*- coding: utf-8 -*-
"""Testes NEW-04 — saúde das cotações."""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.services.cotacoes_service import CotacoesService


def _criar_ativo(ticker, preco='10.00', data_cotacao=None):
    a = Ativo(
        ticker=ticker,
        nome=f'Ativo {ticker}',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal(preco) if preco else None,
        data_ultima_cotacao=data_cotacao,
    )
    _db.session.add(a)
    _db.session.commit()
    _db.session.refresh(a)
    return a


class TestCotacoesHealth:
    def test_health_endpoint(self, client):
        resp = client.get('/api/cotacoes/health')
        assert resp.status_code == 200
        body = resp.get_json()
        assert 'status' in body
        assert 'resumo' in body
        assert 'desatualizados' in body
        assert 'sem_cotacao' in body
        assert 'total_ativos' in body['resumo']

    def test_saude_classifica_ativos(self, app):
        n = uuid.uuid4().int % 10
        t_ok = f'OKZZ{n}'
        t_old = f'OLZZ{n}'
        t_none = f'NCZZ{n}'
        ativos = []
        try:
            now = datetime.now()
            ativos.append(_criar_ativo(t_ok, '50.00', now - timedelta(minutes=5)))
            ativos.append(_criar_ativo(t_old, '30.00', now - timedelta(hours=2)))
            ativos.append(_criar_ativo(t_none, None, None))

            saude = CotacoesService.get_saude_cotacoes(ttl_minutes=15)
            tickers_old = [a['ticker'] for a in saude['desatualizados']]
            tickers_none = [a['ticker'] for a in saude['sem_cotacao']]
            assert t_old in tickers_old
            assert t_none in tickers_none
            assert t_ok not in tickers_old
            assert t_ok not in tickers_none
            assert saude['resumo']['desatualizados'] >= 1
            assert saude['resumo']['sem_cotacao'] >= 1
        finally:
            for a in ativos:
                _db.session.delete(a)
            _db.session.commit()

    def test_anomalias_endpoint_auth(self, auth_client):
        resp = auth_client.get('/api/cotacoes/anomalias?data_ref=2000-01-01', headers=auth_client._auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'anomalias' in data['data']
