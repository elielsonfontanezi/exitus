# -*- coding: utf-8 -*-
"""Testes de integração — EXITUS-MULTIMOEDA-001 — CambioService e endpoints"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock


# ─── Testes unitários do CambioService ────────────────────────────────────────

class TestCambioServiceIdentidade:
    def test_mesma_moeda_retorna_taxa_1(self):
        from app.services.cambio_service import CambioService
        resultado = CambioService.get_taxa('BRL', 'BRL')
        assert resultado['taxa'] == 1.0
        assert resultado['fonte'] == 'identidade'

    def test_usd_para_usd_retorna_1(self):
        from app.services.cambio_service import CambioService
        resultado = CambioService.get_taxa('USD', 'USD')
        assert resultado['taxa'] == 1.0

    # app_context necessário para acesso ao banco
    def test_brl_usd_usa_fallback_com_banco_vazio(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            resultado = CambioService.get_taxa('BRL', 'USD')
            assert resultado['taxa'] == float(TAXAS_FALLBACK['BRL/USD'])


class TestCambioServiceFallback:
    def test_brl_usd_fallback(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            resultado = CambioService.get_taxa('BRL', 'USD')
            assert resultado['taxa'] is not None
            assert resultado['taxa'] == float(TAXAS_FALLBACK.get('BRL/USD', 0))

    def test_usd_brl_fallback(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            resultado = CambioService.get_taxa('USD', 'BRL')
            assert resultado['taxa'] is not None
            assert resultado['taxa'] == float(TAXAS_FALLBACK.get('USD/BRL', 0))

    def test_brl_eur_fallback(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            resultado = CambioService.get_taxa('BRL', 'EUR')
            assert resultado['taxa'] == float(TAXAS_FALLBACK.get('BRL/EUR', 0))

    def test_par_inexistente_retorna_erro(self, app):
        from app.services.cambio_service import CambioService
        with app.app_context():
            resultado = CambioService.get_taxa('BRL', 'XYZ')
            assert resultado.get('erro') is not None
            assert resultado['taxa'] is None


class TestCambioServiceConverter:
    """
    Testes que só usam fallback hardcoded — sem app_context necessário.
    A lógica de fallback é chamada via mock do _taxa_do_banco retornando None.
    """

    def test_converter_brl_para_usd(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            valor = Decimal('100.00')
            resultado = CambioService.converter(valor, 'BRL', 'USD')
            taxa = float(TAXAS_FALLBACK['BRL/USD'])
            esperado = round(100 * taxa, 2)
            assert resultado['valor_convertido'] == pytest.approx(esperado, abs=0.01)
            assert resultado['moeda_origem'] == 'BRL'
            assert resultado['moeda_destino'] == 'USD'

    def test_converter_usd_para_brl(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            valor = Decimal('10.00')
            resultado = CambioService.converter(valor, 'USD', 'BRL')
            taxa = float(TAXAS_FALLBACK['USD/BRL'])
            esperado = round(10 * taxa, 2)
            assert resultado['valor_convertido'] == pytest.approx(esperado, abs=0.01)

    def test_converter_mesma_moeda(self):
        from app.services.cambio_service import CambioService
        resultado = CambioService.converter(Decimal('500.00'), 'BRL', 'BRL')
        assert resultado['valor_convertido'] == 500.0

    def test_converter_par_inexistente_retorna_erro(self, app):
        from app.services.cambio_service import CambioService
        with app.app_context():
            resultado = CambioService.converter(Decimal('100'), 'BRL', 'XYZ')
            assert resultado.get('erro') is not None
            assert resultado['valor_convertido'] is None

    def test_converter_para_brl_atalho(self, app):
        from app.services.cambio_service import CambioService, TAXAS_FALLBACK
        with app.app_context():
            resultado = CambioService.converter_para_brl(Decimal('1.00'), 'USD')
            taxa = float(TAXAS_FALLBACK['USD/BRL'])
            assert float(resultado) == pytest.approx(taxa, abs=0.01)

    def test_converter_para_brl_ja_e_brl(self):
        from app.services.cambio_service import CambioService
        resultado = CambioService.converter_para_brl(Decimal('100.00'), 'BRL')
        assert resultado == Decimal('100.00')


class TestCambioServicePar:
    def test_par_formatado_corretamente(self):
        from app.services.cambio_service import CambioService
        par = CambioService._construir_par('brl', 'usd')
        assert par == 'BRL/USD'

    def test_par_inverso(self):
        from app.services.cambio_service import CambioService
        par = CambioService._construir_par('USD', 'BRL')
        assert par == 'USD/BRL'


# ─── Testes dos endpoints (integração com banco) ──────────────────────────────

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        from app.database import db
        from app.models.usuario import Usuario, UserRole
        from flask_jwt_extended import create_access_token
        usuario = Usuario(
            username='test_cambio',
            email='test_cambio@exitus.com',
            nome_completo='Teste Cambio',
            role=UserRole.ADMIN,
        )
        usuario.set_password('senha123')
        db.session.add(usuario)
        db.session.commit()
        token = create_access_token(identity=str(usuario.id))
        yield {'Authorization': f'Bearer {token}'}
        db.session.delete(usuario)
        db.session.commit()


@pytest.fixture
def taxa_no_banco(app):
    with app.app_context():
        from app.database import db
        from app.models.taxa_cambio import TaxaCambio
        registro = TaxaCambio(
            par_moeda='BRL/USD',
            moeda_base='BRL',
            moeda_cotacao='USD',
            taxa=Decimal('0.17800000'),
            data_referencia=date.today(),
            fonte='teste',
        )
        db.session.add(registro)
        db.session.commit()
        yield registro
        db.session.delete(registro)
        db.session.commit()


class TestEndpointGetTaxa:
    def test_taxa_brl_usd_fallback(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/BRL-USD', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['taxa'] is not None
        assert data['data']['par_moeda'] == 'BRL/USD'

    def test_taxa_identidade(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/BRL-BRL', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['taxa'] == 1.0

    def test_taxa_par_invalido(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/INVALIDO', headers=auth_headers)
        assert resp.status_code == 400

    def test_taxa_sem_token(self, client):
        resp = client.get('/api/cambio/taxa/BRL-USD')
        assert resp.status_code == 401

    def test_taxa_par_inexistente(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/BRL-XYZ', headers=auth_headers)
        assert resp.status_code == 404


class TestEndpointConverter:
    def test_converter_brl_para_usd(self, client, auth_headers):
        resp = client.post('/api/cambio/converter',
                           json={'valor': 100, 'moeda_origem': 'BRL', 'moeda_destino': 'USD'},
                           headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['valor_convertido'] is not None
        assert data['data']['valor_convertido'] > 0

    def test_converter_campos_faltando(self, client, auth_headers):
        resp = client.post('/api/cambio/converter',
                           json={'valor': 100},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_converter_valor_negativo(self, client, auth_headers):
        resp = client.post('/api/cambio/converter',
                           json={'valor': -50, 'moeda_origem': 'BRL', 'moeda_destino': 'USD'},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_converter_moeda_invalida(self, client, auth_headers):
        resp = client.post('/api/cambio/converter',
                           json={'valor': 100, 'moeda_origem': 'BRLX', 'moeda_destino': 'USD'},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_converter_sem_token(self, client):
        resp = client.post('/api/cambio/converter',
                           json={'valor': 100, 'moeda_origem': 'BRL', 'moeda_destino': 'USD'})
        assert resp.status_code == 401


class TestEndpointListarPares:
    def test_listar_pares_retorna_200(self, client, auth_headers):
        resp = client.get('/api/cambio/pares', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['total'] > 0

    def test_pares_incluem_fallbacks(self, client, auth_headers):
        resp = client.get('/api/cambio/pares', headers=auth_headers)
        pares = [p['par_moeda'] for p in resp.get_json()['data']]
        assert 'BRL/USD' in pares
        assert 'USD/BRL' in pares


class TestEndpointRegistrarTaxa:
    def test_registrar_taxa_manual(self, client, auth_headers):
        resp = client.post('/api/cambio/taxa',
                           json={
                               'par_moeda': 'BRL/USD',
                               'taxa': 0.179,
                               'data_referencia': '2026-01-01',
                               'fonte': 'teste',
                           },
                           headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['taxa'] == pytest.approx(0.179, abs=0.0001)

    def test_registrar_taxa_campos_faltando(self, client, auth_headers):
        resp = client.post('/api/cambio/taxa',
                           json={'par_moeda': 'BRL/USD'},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_registrar_taxa_negativa(self, client, auth_headers):
        resp = client.post('/api/cambio/taxa',
                           json={'par_moeda': 'BRL/USD', 'taxa': -1, 'data_referencia': '2026-01-01'},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_registrar_taxa_par_invalido(self, client, auth_headers):
        resp = client.post('/api/cambio/taxa',
                           json={'par_moeda': 'INVALIDO', 'taxa': 0.18, 'data_referencia': '2026-01-01'},
                           headers=auth_headers)
        assert resp.status_code == 400


class TestEndpointHistorico:
    def test_historico_retorna_200(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/BRL-USD/historico', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'data' in data

    def test_historico_par_invalido(self, client, auth_headers):
        resp = client.get('/api/cambio/taxa/INVALIDO/historico', headers=auth_headers)
        assert resp.status_code == 400
