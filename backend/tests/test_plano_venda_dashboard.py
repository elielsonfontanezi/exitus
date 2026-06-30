# -*- coding: utf-8 -*-
"""Testes NEW-14 — dashboard e gatilhos de planos de venda."""
import uuid
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

import jwt
import pytest

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.plano_venda import PlanoVenda, StatusPlanoVenda, TipoGatilho


def _criar_ativo(preco='50.00'):
    suffix = str(uuid.uuid4().int)[:8]
    ticker = f'PV{suffix}'
    a = Ativo(
        ticker=ticker,
        nome=f'Ativo {ticker}',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal(preco),
    )
    _db.session.add(a)
    _db.session.commit()
    _db.session.refresh(a)
    return a


def _user_from_client(auth_client):
    token = auth_client._auth_headers['Authorization'].split()[1]
    payload = jwt.decode(token, options={'verify_signature': False})
    return UUID(payload['sub']), payload.get('assessora_id')


def _criar_plano_venda(user_id, assessora_id, ativo, preco_alvo='40.00', qtd_total='100', qtd_vendida='30'):
    plano = PlanoVenda(
        usuario_id=user_id,
        assessora_id=UUID(assessora_id) if assessora_id else None,
        ativo_id=ativo.id,
        nome='Plano Venda Teste',
        quantidade_total=Decimal(qtd_total),
        quantidade_vendida=Decimal(qtd_vendida),
        preco_alvo=Decimal(preco_alvo),
        tipo_gatilho=TipoGatilho.PRECO_ALVO,
        status=StatusPlanoVenda.ATIVO,
        data_inicio=date.today(),
    )
    _db.session.add(plano)
    _db.session.commit()
    _db.session.refresh(plano)
    return plano


class TestPlanoVendaDashboard:
    def test_dashboard_vazio(self, auth_client):
        resp = auth_client.get('/api/plano-venda/dashboard', headers=auth_client._auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert data['resumo']['total_planos'] == 0
        assert data['resumo']['planos_ativos'] == 0
        assert data['proximos_gatilhos'] == []

    def test_dashboard_com_planos(self, auth_client):
        ativo = _criar_ativo()
        plano = None
        try:
            user_id, assessora_id = _user_from_client(auth_client)
            plano = _criar_plano_venda(user_id, assessora_id, ativo)

            resp = auth_client.get('/api/plano-venda/dashboard', headers=auth_client._auth_headers)
            assert resp.status_code == 200
            resumo = resp.get_json()['data']['resumo']
            assert resumo['total_planos'] == 1
            assert resumo['planos_ativos'] == 1
            assert resumo['quantidade_total_vender'] == pytest.approx(100.0)
            assert resumo['quantidade_total_vendida'] == pytest.approx(30.0)
            assert resumo['progresso_geral'] == pytest.approx(30.0)
        finally:
            if plano:
                PlanoVenda.query.filter_by(id=plano.id).delete()
            _db.session.delete(ativo)
            _db.session.commit()

    def test_verificar_gatilhos_preco_alvo(self, auth_client):
        ativo = _criar_ativo(preco='50.00')
        plano = None
        try:
            user_id, assessora_id = _user_from_client(auth_client)
            plano = _criar_plano_venda(user_id, assessora_id, ativo, preco_alvo='40.00')

            resp = auth_client.get('/api/plano-venda/verificar-gatilhos', headers=auth_client._auth_headers)
            assert resp.status_code == 200
            body = resp.get_json()['data']
            assert body['total'] >= 1
            disparo = next(d for d in body['disparos'] if d['plano_id'] == str(plano.id))
            assert disparo['ativo_ticker'] == ativo.ticker
            assert disparo['tipo_gatilho'] == 'preco_alvo'
            assert 'Preço alvo atingido' in disparo['motivo']
        finally:
            if plano:
                PlanoVenda.query.filter_by(id=plano.id).delete()
            _db.session.delete(ativo)
            _db.session.commit()

    def test_estatisticas(self, auth_client):
        ativo = _criar_ativo()
        plano = None
        try:
            user_id, assessora_id = _user_from_client(auth_client)
            plano = _criar_plano_venda(user_id, assessora_id, ativo)

            resp = auth_client.get('/api/plano-venda/estatisticas', headers=auth_client._auth_headers)
            assert resp.status_code == 200
            stats = resp.get_json()['data']
            assert stats['total_planos'] == 1
            assert stats['por_gatilho'].get('preco_alvo') == 1
            assert stats['volume_total'] == pytest.approx(100.0)
        finally:
            if plano:
                PlanoVenda.query.filter_by(id=plano.id).delete()
            _db.session.delete(ativo)
            _db.session.commit()

    def test_proximos_gatilhos_data_limite(self, auth_client):
        ativo = _criar_ativo()
        plano = None
        try:
            user_id, assessora_id = _user_from_client(auth_client)
            plano = PlanoVenda(
                usuario_id=user_id,
                assessora_id=UUID(assessora_id) if assessora_id else None,
                ativo_id=ativo.id,
                nome='Plano Data Limite',
                quantidade_total=Decimal('50'),
                quantidade_vendida=Decimal('0'),
                tipo_gatilho=TipoGatilho.DATA_LIMITE,
                data_limite=date.today() + timedelta(days=10),
                status=StatusPlanoVenda.ATIVO,
                data_inicio=date.today(),
            )
            _db.session.add(plano)
            _db.session.commit()

            resp = auth_client.get('/api/plano-venda/dashboard', headers=auth_client._auth_headers)
            proximos = resp.get_json()['data']['proximos_gatilhos']
            assert len(proximos) >= 1
            assert proximos[0]['plano_nome'] == 'Plano Data Limite'
            assert proximos[0]['dias_restantes'] == 10
        finally:
            if plano:
                PlanoVenda.query.filter_by(id=plano.id).delete()
            _db.session.delete(ativo)
            _db.session.commit()
