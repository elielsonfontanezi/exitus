# -*- coding: utf-8 -*-
"""
Testes para app.utils.ativo_classifier (BUG-020)

Cobertura:
- Inferência por padrão de ticker (puro, sem DB)
- Lookup do banco como prioridade
- Cache de classificações (seeds, manuais, API, heurística)
- API externa (metadata) com mock
- Avisos e níveis de confiança para casos ambíguos
- Fallback seguro para classificações de baixa confiança
"""
from unittest import mock

import pytest

from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.ativo_classificacao_cache import (
    AtivoClassificacaoCache,
    FonteClassificacao,
    NivelConfianca,
)
from app.models.usuario import Usuario
from app.database import db
from app.utils.ativo_classifier import (
    inferir_classificacao_ativo,
    classificar_ativo,
    salvar_classificacao_cache,
)


# ---------------------------------------------------------------------------
# Inferência pura (sem DB)
# ---------------------------------------------------------------------------

class TestInferirClassificacaoAtivo:
    def test_acao_b3_petr4(self):
        r = inferir_classificacao_ativo('PETR4')
        assert r['tipo'] == TipoAtivo.ACAO
        assert r['mercado'] == 'BR'
        assert r['moeda'] == 'BRL'
        assert r['fonte'] == FonteClassificacao.HEURISTICA
        assert r['confianca'] == NivelConfianca.ALTA
        assert r['aviso'] is None

    def test_acao_b3_vale3(self):
        r = inferir_classificacao_ativo('VALE3')
        assert r['tipo'] == TipoAtivo.ACAO
        assert r['mercado'] == 'BR'
        assert r['aviso'] is None

    def test_acao_pn_b_cple6(self):
        r = inferir_classificacao_ativo('CPLE6')
        assert r['tipo'] == TipoAtivo.ACAO
        assert r['mercado'] == 'BR'
        assert r['confianca'] == NivelConfianca.ALTA

    def test_fii_default_para_sufixo_11(self):
        """Tickers desconhecidos terminados em 11 viram FII + aviso."""
        r = inferir_classificacao_ativo('HGLG11')
        assert r['tipo'] == TipoAtivo.FII
        assert r['mercado'] == 'BR'
        assert r['moeda'] == 'BRL'
        assert r['confianca'] == NivelConfianca.MEDIA
        assert r['aviso'] is not None

    def test_etf_br_bova11_via_curadoria(self):
        """BOVA11 está na lista curada → ETF, sem aviso."""
        r = inferir_classificacao_ativo('BOVA11')
        assert r['tipo'] == TipoAtivo.ETF
        assert r['mercado'] == 'BR'
        assert r['moeda'] == 'BRL'
        assert r['confianca'] == NivelConfianca.ALTA
        assert r['aviso'] is None

    def test_etf_br_smal11_via_curadoria(self):
        r = inferir_classificacao_ativo('SMAL11')
        assert r['tipo'] == TipoAtivo.ETF
        assert r['mercado'] == 'BR'
        assert r['confianca'] == NivelConfianca.ALTA

    def test_unit_klbn11_via_curadoria(self):
        r = inferir_classificacao_ativo('KLBN11')
        assert r['tipo'] == TipoAtivo.UNIT
        assert r['mercado'] == 'BR'
        assert r['aviso'] is None
        assert r['confianca'] == NivelConfianca.ALTA

    def test_unit_taee11_via_curadoria(self):
        r = inferir_classificacao_ativo('TAEE11')
        assert r['tipo'] == TipoAtivo.UNIT
        assert r['mercado'] == 'BR'

    def test_bdr_aapl34(self):
        r = inferir_classificacao_ativo('AAPL34')
        assert r['tipo'] == TipoAtivo.STOCK_INTL
        assert r['mercado'] == 'INTL'
        assert r['moeda'] == 'BRL'
        assert r['confianca'] == NivelConfianca.ALTA
        assert r['aviso'] is None

    def test_bdr_msft34(self):
        r = inferir_classificacao_ativo('MSFT34')
        assert r['tipo'] == TipoAtivo.STOCK_INTL
        assert r['mercado'] == 'INTL'

    def test_bdr_tsla34(self):
        r = inferir_classificacao_ativo('TSLA34')
        assert r['tipo'] == TipoAtivo.STOCK_INTL

    def test_stock_us_aapl(self):
        """4 letras sem número → STOCK US + aviso (pode ser ETF/REIT)."""
        r = inferir_classificacao_ativo('AAPL')
        assert r['tipo'] == TipoAtivo.STOCK
        assert r['mercado'] == 'US'
        assert r['moeda'] == 'USD'
        assert r['confianca'] == NivelConfianca.BAIXA
        assert r['aviso'] is not None

    def test_stock_us_msft(self):
        r = inferir_classificacao_ativo('MSFT')
        assert r['tipo'] == TipoAtivo.STOCK
        assert r['mercado'] == 'US'

    def test_stock_us_3_letras(self):
        """ADRs com 3 letras (PBR) → STOCK US por heurística."""
        r = inferir_classificacao_ativo('PBR')
        assert r['tipo'] == TipoAtivo.STOCK
        assert r['mercado'] == 'US'
        assert r['confianca'] == NivelConfianca.BAIXA

    def test_normalizacao_lowercase(self):
        r = inferir_classificacao_ativo('petr4')
        assert r['tipo'] == TipoAtivo.ACAO

    def test_ticker_vazio(self):
        r = inferir_classificacao_ativo('')
        assert r['tipo'] == TipoAtivo.OUTRO
        assert r['confianca'] == NivelConfianca.BAIXA
        assert r['aviso'] is not None

    def test_ticker_none(self):
        r = inferir_classificacao_ativo(None)  # type: ignore
        assert r['tipo'] == TipoAtivo.OUTRO
        assert r['confianca'] == NivelConfianca.BAIXA

    def test_ticker_invalido_fallback(self):
        """Padrão não reconhecido → OUTRO + aviso."""
        r = inferir_classificacao_ativo('XYZ123ABC')
        assert r['tipo'] == TipoAtivo.OUTRO
        assert r['confianca'] == NivelConfianca.BAIXA
        assert r['aviso'] is not None


# ---------------------------------------------------------------------------
# Classificação com lookup no banco
# ---------------------------------------------------------------------------

class TestClassificarAtivoComBanco:
    def test_lookup_no_banco_tem_prioridade(self, app):
        """Se ativo já existe no banco, copia classificação dele."""
        with app.app_context():
            ativo = Ativo(
                ticker='TESTBOVA11',
                nome='Teste',
                tipo=TipoAtivo.ETF,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                ativo=True,
            )
            db.session.add(ativo)
            db.session.commit()

            try:
                r = classificar_ativo('TESTBOVA11')
                assert r['tipo'] == TipoAtivo.ETF
                assert r['mercado'] == 'BR'
                assert r['fonte'] == FonteClassificacao.MANUAL
                assert r['confianca'] == NivelConfianca.ALTA
                assert r['aviso'] is None
            finally:
                db.session.delete(ativo)
                db.session.commit()

    def test_sem_lookup_cai_em_inferencia(self, app):
        """Ticker novo → segue inferência pura."""
        with app.app_context():
            r = classificar_ativo('WXYZ4')
            assert r['tipo'] == TipoAtivo.ACAO
            assert r['mercado'] == 'BR'
            assert r['confianca'] == NivelConfianca.ALTA


# ---------------------------------------------------------------------------
# Cache de classificações (seeds / manuais)
# ---------------------------------------------------------------------------

class TestClassificacaoCache:
    def test_classificacao_cache_seed_tem_prioridade_sobre_heuristica(self, app):
        """Cache seed curado deve sobrepor inferência pura."""
        with app.app_context():
            cache = AtivoClassificacaoCache(
                ticker='NEWETF11',
                tipo=TipoAtivo.ETF,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                fonte=FonteClassificacao.SEED,
                confianca=NivelConfianca.ALTA,
            )
            db.session.add(cache)
            db.session.commit()

            try:
                r = classificar_ativo('NEWETF11')
                assert r['tipo'] == TipoAtivo.ETF
                assert r['fonte'] == FonteClassificacao.SEED
                assert r['confianca'] == NivelConfianca.ALTA
                assert r['aviso'] is None
            finally:
                db.session.delete(cache)
                db.session.commit()

    def test_classificacao_cache_manual_tem_prioridade(self, app):
        """Correção manual do usuário sobrepõe heurística e seed."""
        with app.app_context():
            usuario = Usuario(
                username='classifier_test_user',
                email='classifier_test@example.com',
                password_hash='fakehash',
            )
            db.session.add(usuario)
            db.session.commit()

            cache = AtivoClassificacaoCache(
                ticker='WEIRD11',
                tipo=TipoAtivo.UNIT,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                fonte=FonteClassificacao.MANUAL,
                confianca=NivelConfianca.ALTA,
                usuario_id=usuario.id,
                observacoes='Correção manual do usuário',
            )
            db.session.add(cache)
            db.session.commit()

            try:
                r = classificar_ativo('WEIRD11', usuario_id=usuario.id)
                assert r['tipo'] == TipoAtivo.UNIT
                assert r['fonte'] == FonteClassificacao.MANUAL
                assert r['confianca'] == NivelConfianca.ALTA
                assert r['aviso'] is None
            finally:
                db.session.delete(cache)
                db.session.delete(usuario)
                db.session.commit()

    def test_salvar_classificacao_cache_atualiza_existente(self, app):
        with app.app_context():
            cache = salvar_classificacao_cache(
                ticker='CACHEABLE4',
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                fonte=FonteClassificacao.SEED,
                confianca=NivelConfianca.ALTA,
            )
            assert cache.tipo == TipoAtivo.ACAO

            cache2 = salvar_classificacao_cache(
                ticker='CACHEABLE4',
                tipo=TipoAtivo.ETF,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                fonte=FonteClassificacao.MANUAL,
                confianca=NivelConfianca.ALTA,
            )
            assert cache2.id == cache.id
            assert cache2.tipo == TipoAtivo.ETF
            assert cache2.fonte == FonteClassificacao.MANUAL

            db.session.delete(cache2)
            db.session.commit()


# ---------------------------------------------------------------------------
# API externa (mock)
# ---------------------------------------------------------------------------

class TestClassificacaoApiExterna:
    def test_api_externa_classifica_etf(self, app):
        with app.app_context():
            fake_info = {'type': 'ETF'}
            fake_ticker = mock.MagicMock()
            fake_ticker.info = fake_info

            with mock.patch('yfinance.Ticker', return_value=fake_ticker):
                r = classificar_ativo('WEIRD11', usar_api_externa=True)
                assert r['tipo'] == TipoAtivo.ETF
                assert r['fonte'] == FonteClassificacao.API
                assert r['confianca'] == NivelConfianca.MEDIA
                assert r['aviso'] is not None

    def test_api_externa_classifica_reit(self, app):
        with app.app_context():
            fake_ticker = mock.MagicMock()
            fake_ticker.info = {'type': 'REIT'}

            with mock.patch('yfinance.Ticker', return_value=fake_ticker):
                r = classificar_ativo('O', usar_api_externa=True)
                assert r['tipo'] == TipoAtivo.REIT
                assert r['fonte'] == FonteClassificacao.API

    def test_api_externa_falha_cai_em_heuristica(self, app):
        with app.app_context():
            with mock.patch('yfinance.Ticker', side_effect=Exception('offline')):
                r = classificar_ativo('PETR4', usar_api_externa=True)
                assert r['tipo'] == TipoAtivo.ACAO
                assert r['fonte'] == FonteClassificacao.HEURISTICA
                assert r['confianca'] == NivelConfianca.ALTA


# ---------------------------------------------------------------------------
# Fallback e confiança
# ---------------------------------------------------------------------------

class TestClassificacaoFallback:
    def test_fallback_outro_para_confianca_baixa(self, app):
        with app.app_context():
            r = classificar_ativo('XYZ123ABC', usar_api_externa=False)
            assert r['tipo'] == TipoAtivo.OUTRO
            assert r['confianca'] == NivelConfianca.BAIXA
            assert 'revise manualmente' in r['aviso'].lower()

    def test_us_stock_tem_confianca_baixa(self, app):
        with app.app_context():
            r = classificar_ativo('VTI', usar_api_externa=False)
            assert r['tipo'] == TipoAtivo.STOCK
            assert r['confianca'] == NivelConfianca.BAIXA
            assert r['aviso'] is not None
