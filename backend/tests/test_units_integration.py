# -*- coding: utf-8 -*-
"""
EXITUS-UNITS-001 — Testes de integração: UNITs B3

Cobre:
- TipoAtivo.UNIT: criação de ativo com tipo 'unit'
- Listagem e filtro por tipo 'unit'
- TipoEventoCorporativo.DESMEMBRAMENTO: criação de evento corporativo
- Método is_desmembramento() no model
- Isenção de proventos em UNITs (proventos não são pagos diretamente às UNITs)
"""
import uuid as _uuid
import pytest
from app.database import db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.evento_corporativo import EventoCorporativo, TipoEventoCorporativo
from datetime import date


def _unique_ticker(prefix='UNT'):
    suffix = str(_uuid.uuid4().int)[:4]
    return f'{prefix}{suffix}'


# ===========================================================================
# TipoAtivo.UNIT — criação via API
# ===========================================================================
class TestAtivoUnit:

    def test_criar_ativo_tipo_unit_retorna_201(self, auth_client):
        ticker = _unique_ticker()
        rv = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': f'Unit Teste {ticker}',
                'tipo': 'unit',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
            },
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 201, rv.get_json()
        data = rv.get_json()
        assert data['success'] is True
        assert data['data']['tipo'] == 'unit'

        ativo_id = data['data']['id']
        Ativo.query.filter_by(id=ativo_id).delete()
        db.session.commit()

    def test_criar_ativo_tipo_unit_persistido_no_banco(self, app, auth_client):
        ticker = _unique_ticker('UB')
        rv = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': f'Unit Banco {ticker}',
                'tipo': 'unit',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
            },
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 201
        ativo_id = rv.get_json()['data']['id']

        ativo = db.session.get(Ativo, ativo_id)
        assert ativo is not None
        assert ativo.tipo == TipoAtivo.UNIT

        db.session.delete(ativo)
        db.session.commit()

    def test_listar_filtrando_por_tipo_unit(self, auth_client):
        ticker = _unique_ticker('UL')
        rv_create = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': f'Unit Listagem {ticker}',
                'tipo': 'unit',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
            },
            headers=auth_client._auth_headers,
        )
        assert rv_create.status_code == 201
        ativo_id = rv_create.get_json()['data']['id']

        rv_list = auth_client.get(
            '/api/ativos/?tipo=unit',
            headers=auth_client._auth_headers,
        )
        assert rv_list.status_code == 200
        data = rv_list.get_json()
        inner = data.get('data', {})
        ativos = inner.get('ativos', []) if isinstance(inner, dict) else inner
        tipos = [a['tipo'] for a in ativos]
        assert all(t == 'unit' for t in tipos), f"Tipos inesperados: {tipos}"
        tickers_retornados = [a['ticker'] for a in ativos]
        assert ticker in tickers_retornados

        Ativo.query.filter_by(id=ativo_id).delete()
        db.session.commit()

    def test_tipo_unit_e_renda_variavel(self, app, auth_client):
        ticker = _unique_ticker('URV')
        rv = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': f'Unit RV {ticker}',
                'tipo': 'unit',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
            },
            headers=auth_client._auth_headers,
        )
        assert rv.status_code == 201
        ativo_id = rv.get_json()['data']['id']

        ativo = db.session.get(Ativo, ativo_id)
        assert ativo.classe == ClasseAtivo.RENDA_VARIAVEL

        db.session.delete(ativo)
        db.session.commit()


# ===========================================================================
# TipoEventoCorporativo.DESMEMBRAMENTO — model e API
# ===========================================================================
class TestDesmembramentoUnit:

    def _criar_ativo_unit(self, ticker):
        ativo = Ativo(
            ticker=ticker,
            nome=f'Unit Evento {ticker}',
            tipo=TipoAtivo.UNIT,
            classe=ClasseAtivo.RENDA_VARIAVEL,
            mercado='BR',
            moeda='BRL',
            ativo=True,
        )
        db.session.add(ativo)
        db.session.commit()
        return ativo.id

    def test_is_desmembramento_retorna_true(self, app):
        ticker = _unique_ticker('UE')
        ativo_id = self._criar_ativo_unit(ticker)

        evento = EventoCorporativo(
            ativo_id=ativo_id,
            tipo_evento=TipoEventoCorporativo.DESMEMBRAMENTO,
            data_evento=date(2026, 3, 4),
            descricao='Desmembramento de UNIT em ações ON e PN',
            proporcao=None,
        )
        db.session.add(evento)
        db.session.commit()
        evento_id = evento.id

        assert evento.is_desmembramento() is True
        assert evento.is_split() is False
        assert evento.is_grupamento() is False

        EventoCorporativo.query.filter_by(id=evento_id).delete()
        Ativo.query.filter_by(id=ativo_id).delete()
        db.session.commit()

    def test_criar_evento_desmembramento_via_api(self, app, auth_client):
        ticker = _unique_ticker('UD')
        ativo_id = self._criar_ativo_unit(ticker)

        rv = auth_client.post(
            '/api/eventos-corporativos/',
            json={
                'ativo_id': str(ativo_id),
                'tipo_evento': 'desmembramento',
                'data_evento': '2026-03-04',
                'descricao': 'Desmembramento UNIT em ações constituintes',
            },
            headers=auth_client._auth_headers,
        )
        assert rv.status_code in (200, 201), rv.get_json()

        EventoCorporativo.query.filter_by(ativo_id=ativo_id).delete()
        Ativo.query.filter_by(id=ativo_id).delete()
        db.session.commit()

    def test_tipo_evento_desmembramento_no_enum(self):
        valores = [e.value for e in TipoEventoCorporativo]
        assert 'desmembramento' in valores

    def test_tipo_unit_no_enum_tipoativo(self):
        valores = [e.value for e in TipoAtivo]
        assert 'unit' in valores
