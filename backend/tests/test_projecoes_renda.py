# -*- coding: utf-8 -*-
"""Testes NEW-17 — projeções de renda passiva."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.database import db as _db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.projecao_renda import ProjecaoRenda
from app.models.provento import Provento, TipoProvento
from app.services.projecao_service import ProjecaoService


class TestProjecoesRenda:
    def test_cenarios_estrutura(self, auth_client):
        resp = auth_client.get(
            '/api/projecoes/cenarios',
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert 'conservador' in body
        assert 'moderado' in body
        assert 'otimista' in body
        assert 'renda_mensal' in body['moderado']
        assert 'media_mensal_historica' in body

    def test_cenarios_sem_proventos_retorna_zero(self, app, usuario_seed):
        with app.app_context():
            dados = ProjecaoService.gerar_cenarios(usuario_seed.id)
            assert dados['moderado']['renda_mensal'] >= 0
            assert dados['conservador']['renda_mensal'] <= dados['otimista']['renda_mensal']

    def test_recalcular_persiste_12_meses(self, auth_client, app):
        me_resp = auth_client.get('/api/auth/me', headers=auth_client._auth_headers)
        usuario_id = me_resp.get_json()['data']['id']
        try:
            resp = auth_client.post(
                '/api/projecoes/recalcular',
                headers=auth_client._auth_headers,
                json={},
            )
            assert resp.status_code == 200
            body = resp.get_json()
            assert body.get('recalculadas') == 12
            assert body.get('status') == 'ok'

            list_resp = auth_client.get(
                '/api/projecoes/renda',
                headers=auth_client._auth_headers,
            )
            assert list_resp.status_code == 200
            proj = list_resp.get_json().get('projecoes', [])
            assert len(proj) >= 1
        finally:
            with app.app_context():
                ProjecaoRenda.query.filter_by(usuario_id=usuario_id).delete()
                _db.session.commit()

    def test_cenarios_com_proventos(self, app, usuario_seed, corretora_seed):
        ativo = None
        prov = None
        pos = None
        try:
            n = uuid4().int % 1000
            ativo = Ativo(
                ticker=f'PRJ{n}',
                nome=f'Proj {n}',
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
            )
            _db.session.add(ativo)
            _db.session.flush()

            from app.models.posicao import Posicao
            pos = Posicao(
                usuario_id=usuario_seed.id,
                ativo_id=ativo.id,
                corretora_id=corretora_seed.id,
                quantidade=Decimal('100'),
                preco_medio=Decimal('10'),
                custo_total=Decimal('1000'),
            )
            _db.session.add(pos)

            prov = Provento(
                ativo_id=ativo.id,
                tipo_provento=TipoProvento.DIVIDENDO,
                valor_por_acao=Decimal('0.50'),
                quantidade_ativos=Decimal('100'),
                valor_bruto=Decimal('50'),
                imposto_retido=Decimal('0'),
                valor_liquido=Decimal('50'),
                data_com=date.today(),
                data_pagamento=date.today(),
            )
            _db.session.add(prov)
            _db.session.commit()

            dados = ProjecaoService.gerar_cenarios(usuario_seed.id)
            assert dados['media_mensal_historica'] >= 0
            assert dados['moderado']['renda_anual'] == round(
                dados['moderado']['renda_mensal'] * 12, 2
            )
        finally:
            if prov:
                _db.session.delete(prov)
            if pos:
                _db.session.delete(pos)
            if ativo:
                _db.session.delete(ativo)
            _db.session.commit()
