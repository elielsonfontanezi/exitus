# -*- coding: utf-8 -*-
"""Testes CONCENTRACAO-001 — análise de concentração da carteira."""
import uuid
from decimal import Decimal

import pytest

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.posicao import Posicao
from app.services.concentracao_service import ConcentracaoService


def _criar_usuario(assessora_id):
    from app.models.usuario import Usuario, UserRole
    suffix = str(uuid.uuid4())[:8]
    u = Usuario(
        username=f'cc{suffix}',
        email=f'cc{suffix}@test.exitus',
        role=UserRole.ADMIN,
        assessora_id=assessora_id,
    )
    u.set_password('senha123')
    _db.session.add(u)
    _db.session.commit()
    _db.session.refresh(u)
    return u


def _criar_ativo(ticker, preco='100.00'):
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


class TestConcentracaoService:
    def test_vazio_retorna_zeros(self, app, assessora_seed):
        u = _criar_usuario(assessora_seed.id)
        result = ConcentracaoService.calcular_concentracao(u.id)
        assert result['patrimonio_total'] == 0.0
        assert result['qtd_posicoes'] == 0
        assert result['concentrado'] is False

    def test_top1_e_hhi(self, app, assessora_seed, corretora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            a1 = _criar_ativo(f'C1{uuid.uuid4().int % 10000}', '500.00')
            a2 = _criar_ativo(f'C2{uuid.uuid4().int % 10000}', '100.00')
            _criar_posicao(u.id, a1, corretora_seed.id, assessora_seed.id, '10')
            _criar_posicao(u.id, a2, corretora_seed.id, assessora_seed.id, '10')

            result = ConcentracaoService.calcular_concentracao(u.id)
            assert result['patrimonio_total'] == pytest.approx(6000.0, abs=1.0)
            assert result['top1_percentual'] == pytest.approx(83.33, abs=0.1)
            assert result['top1_ticker'] == a1.ticker
            assert result['concentrado'] is True
            assert any(a['tipo'] == 'top1' for a in result['alertas'])
        finally:
            Posicao.query.filter_by(usuario_id=u.id).delete()
            _db.session.commit()

    def test_carteira_balanceada_sem_alertas(self, app, assessora_seed, corretora_seed):
        u = _criar_usuario(assessora_seed.id)
        try:
            for i in range(10):
                a = _criar_ativo(f'CB{i}{uuid.uuid4().int % 1000}', '100.00')
                _criar_posicao(u.id, a, corretora_seed.id, assessora_seed.id, '10')

            result = ConcentracaoService.calcular_concentracao(u.id)
            assert result['top1_percentual'] == pytest.approx(10.0, abs=0.1)
            assert result['top5_percentual'] == pytest.approx(50.0, abs=0.1)
            assert result['concentrado'] is False
            assert result['alertas'] == []
        finally:
            Posicao.query.filter_by(usuario_id=u.id).delete()
            _db.session.commit()


class TestConcentracaoEndpoint:
    def test_sem_auth_401(self, client):
        assert client.get('/api/portfolios/concentracao').status_code == 401

    def test_autenticado_estrutura(self, auth_client):
        rv = auth_client.get(
            '/api/portfolios/concentracao',
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 200
        data = rv.get_json()['data']
        assert 'top1_percentual' in data
        assert 'hhi' in data
        assert 'alertas' in data
        assert 'ativos' in data
