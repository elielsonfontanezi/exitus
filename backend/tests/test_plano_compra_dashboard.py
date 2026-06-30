# -*- coding: utf-8 -*-
"""Testes NEW-13 — dashboard de planos de compra."""
import uuid
from decimal import Decimal
from uuid import UUID

import jwt
import pytest

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from datetime import datetime, timedelta

from app.models.plano_compra import PlanoCompra, StatusPlanoCompra


def _criar_ativo():
    suffix = str(uuid.uuid4().int)[:8]
    ticker = f'PD{suffix}'
    a = Ativo(
        ticker=ticker,
        nome=f'Ativo {ticker}',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('38.50'),
    )
    _db.session.add(a)
    _db.session.commit()
    _db.session.refresh(a)
    return a


def _user_from_client(auth_client):
    token = auth_client._auth_headers['Authorization'].split()[1]
    payload = jwt.decode(token, options={'verify_signature': False})
    return UUID(payload['sub']), payload.get('assessora_id')


class TestPlanoCompraDashboard:
    def test_dashboard_vazio(self, auth_client):
        resp = auth_client.get('/api/plano-compra/dashboard', headers=auth_client._auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['resumo']['total_planos'] == 0
        assert data['resumo']['planos_ativos'] == 0
        assert data['resumo']['progresso_medio'] == 0.0
        assert data['proximos_aportes'] == []
        assert data['planos'] == []

    def test_dashboard_com_planos(self, auth_client, app):
        ativo = _criar_ativo()
        plano = None
        try:
            user_id, assessora_id = _user_from_client(auth_client)
            plano = PlanoCompra(
                usuario_id=user_id,
                assessora_id=UUID(assessora_id) if assessora_id else None,
                ativo_id=ativo.id,
                nome='Plano Dashboard',
                quantidade_alvo=100,
                quantidade_acumulada=25,
                valor_aporte_mensal=500,
                data_inicio=datetime.utcnow(),
                proximo_aporte=datetime.utcnow() + timedelta(days=7),
                status=StatusPlanoCompra.ATIVO,
            )
            _db.session.add(plano)
            _db.session.commit()
            _db.session.refresh(plano)

            resp = auth_client.get('/api/plano-compra/dashboard', headers=auth_client._auth_headers)
            assert resp.status_code == 200
            body = resp.get_json()['data']
            resumo = body['resumo']
            assert resumo['total_planos'] == 1
            assert resumo['planos_ativos'] == 1
            assert resumo['total_aporte_mensal'] == pytest.approx(500.0)
            assert resumo['total_investido'] == pytest.approx(25 * 38.50, abs=0.01)
            assert resumo['progresso_medio'] == pytest.approx(25.0)
            assert resumo['desvio_meta_percentual'] == pytest.approx(75.0)
            assert len(body['proximos_aportes']) == 1
            assert body['proximos_aportes'][0]['ativo_ticker'] == ativo.ticker
            assert len(body['planos']) == 1
        finally:
            if plano:
                PlanoCompra.query.filter_by(id=plano.id).delete()
            _db.session.delete(ativo)
            _db.session.commit()
