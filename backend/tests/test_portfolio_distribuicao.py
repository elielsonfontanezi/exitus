# -*- coding: utf-8 -*-
"""Testes NEW-03 — distribuição por classe e segmento (tipo)."""
import uuid
from decimal import Decimal

import pytest

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.posicao import Posicao
from app.services.portfolio_service import PortfolioService


def _criar_usuario(assessora_id):
    from app.models.usuario import Usuario, UserRole
    suffix = str(uuid.uuid4())[:8]
    u = Usuario(
        username=f'ds{suffix}',
        email=f'ds{suffix}@test.exitus',
        role=UserRole.ADMIN,
        assessora_id=assessora_id,
    )
    u.set_password('senha123')
    _db.session.add(u)
    _db.session.commit()
    _db.session.refresh(u)
    return u


def _criar_ativo(ticker, tipo, classe, preco='100.00'):
    a = Ativo(
        ticker=ticker,
        nome=f'Ativo {ticker}',
        tipo=tipo,
        classe=classe,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal(preco),
    )
    _db.session.add(a)
    _db.session.commit()
    _db.session.refresh(a)
    return a


def _criar_posicao(usuario_id, ativo, corretora_id, assessora_id, qtd='10'):
    p = Posicao(
        usuario_id=usuario_id,
        ativo_id=ativo.id,
        corretora_id=corretora_id,
        assessora_id=assessora_id,
        quantidade=Decimal(qtd),
        preco_medio=Decimal('90.00'),
        custo_total=Decimal(qtd) * Decimal('90.00'),
    )
    _db.session.add(p)
    _db.session.commit()
    return p


class TestDistribuicaoService:
    def test_classes_agrupadas(self, app, assessora_seed, corretora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            a1 = _criar_ativo(f'AC{uuid.uuid4().int % 10000}', TipoAtivo.ACAO, ClasseAtivo.RENDA_VARIAVEL)
            a2 = _criar_ativo(f'FI{uuid.uuid4().int % 10000}', TipoAtivo.FII, ClasseAtivo.RENDA_VARIAVEL)
            a3 = _criar_ativo(f'CB{uuid.uuid4().int % 10000}', TipoAtivo.CDB, ClasseAtivo.RENDA_FIXA)
            _criar_posicao(u.id, a1, corretora_seed.id, assessora_seed.id, '10')
            _criar_posicao(u.id, a2, corretora_seed.id, assessora_seed.id, '5')
            _criar_posicao(u.id, a3, corretora_seed.id, assessora_seed.id, '20')

            result = PortfolioService.get_distribuicao_classes(u.id)
            assert result['patrimonio_total'] == pytest.approx(3500.0, abs=1.0)
            por_chave = {i['chave']: i for i in result['itens']}
            assert por_chave['renda_variavel']['valor'] == pytest.approx(1500.0, abs=1.0)
            assert por_chave['renda_fixa']['valor'] == pytest.approx(2000.0, abs=1.0)
            assert por_chave['renda_variavel']['percentual'] == pytest.approx(42.86, abs=0.1)
        finally:
            _db.session.rollback()
            Posicao.query.filter_by(usuario_id=u.id).delete()
            _db.session.commit()

    def test_setores_por_tipo(self, app, assessora_seed, corretora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            a1 = _criar_ativo(f'S1{uuid.uuid4().int % 10000}', TipoAtivo.ACAO, ClasseAtivo.RENDA_VARIAVEL)
            a2 = _criar_ativo(f'S2{uuid.uuid4().int % 10000}', TipoAtivo.FII, ClasseAtivo.RENDA_VARIAVEL)
            _criar_posicao(u.id, a1, corretora_seed.id, assessora_seed.id, '10')
            _criar_posicao(u.id, a2, corretora_seed.id, assessora_seed.id, '10')

            setores = PortfolioService.get_distribuicao_setores(u.id)
            por_seg = {s['segmento']: s for s in setores}
            assert 'acao' in por_seg
            assert 'fii' in por_seg
            assert por_seg['acao']['label'] == 'Ações'
            assert por_seg['fii']['label'] == 'FIIs'
            assert por_seg['acao']['classe'] == 'renda_variavel'
        finally:
            _db.session.rollback()
            Posicao.query.filter_by(usuario_id=u.id).delete()
            _db.session.commit()

    def test_vazio_retorna_listas_vazias(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        classes = PortfolioService.get_distribuicao_classes(u.id)
        setores = PortfolioService.get_distribuicao_setores(u.id)
        assert classes['itens'] == []
        assert classes['patrimonio_total'] == 0.0
        assert setores == []


class TestDistribuicaoEndpoints:
    def test_get_classes_sem_auth_401(self, client):
        assert client.get('/api/portfolios/distribuicao/classes').status_code == 401

    def test_get_setores_sem_auth_401(self, client):
        assert client.get('/api/portfolios/distribuicao/setores').status_code == 401

    def test_get_classes_autenticado(self, auth_client):
        rv = auth_client.get(
            '/api/portfolios/distribuicao/classes',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'itens' in data
        assert 'patrimonio_total' in data

    def test_get_setores_autenticado(self, auth_client):
        rv = auth_client.get(
            '/api/portfolios/distribuicao/setores',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'setores' in data
        assert isinstance(data['setores'], list)
