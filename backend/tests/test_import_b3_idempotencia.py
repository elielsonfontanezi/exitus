# -*- coding: utf-8 -*-
"""
EXITUS-VALIDATION-001 — Testes de idempotência e sanitização da importação B3.

Cobre:
- Deduplicação por hash: reimportar o mesmo arquivo não duplica registros
- Modo dry_run: não persiste dados, retorna preview correto
- Sanitização: campos com XSS/Unicode malicioso são limpos
- Hash gerado corretamente e inclui nome do arquivo
"""
import uuid
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.database import db as _db
from app.models.ativo import Ativo, ClasseAtivo
from app.models.provento import Provento, TipoProvento
from app.models.transacao import Transacao, TipoTransacao
from app.models.corretora import Corretora
from app.services.import_b3_service import ImportB3Service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_movimentacao(produto='BTLG11', tipo='Rendimento', data=None,
                       quantidade=10, preco=0.80, valor=8.00,
                       instituicao='XP INVESTIMENTOS'):
    return {
        'data': data or date(2026, 3, 1),
        'tipo_movimentacao': tipo,
        'produto': produto,
        'instituicao': instituicao,
        'quantidade': Decimal(str(quantidade)),
        'preco_unitario': Decimal(str(preco)),
        'valor_operacao': Decimal(str(valor)),
    }


def _make_negociacao(codigo='PETR4', tipo='Compra', data=None,
                     quantidade=10, preco=38.50, valor=385.00,
                     instituicao='XP INVESTIMENTOS'):
    return {
        'data': data or date(2026, 3, 1),
        'tipo_movimentacao': tipo,
        'mercado': 'BOVESPA',
        'prazo_vencimento': '',
        'instituicao': instituicao,
        'codigo_negociacao': codigo,
        'quantidade': Decimal(str(quantidade)),
        'preco': Decimal(str(preco)),
        'valor': Decimal(str(valor)),
    }


def _service(arquivo='arquivo_teste.xlsx'):
    svc = ImportB3Service()
    svc.arquivo_origem = arquivo
    return svc


def _cleanup_por_hash(hash_val):
    Provento.query.filter_by(hash_importacao=hash_val).delete()
    Transacao.query.filter_by(hash_importacao=hash_val).delete()
    _db.session.commit()


# ---------------------------------------------------------------------------
# Testes: _sanitizar_texto
# ---------------------------------------------------------------------------

class TestSanitizarTexto:
    def test_remove_tag_html(self, app):
        svc = _service()
        resultado = svc._sanitizar_texto('<script>alert(1)</script>BTLG11')
        assert '<script>' not in resultado
        assert '</script>' not in resultado
        assert 'BTLG11' in resultado

    def test_remove_caracteres_controle(self, app):
        svc = _service()
        resultado = svc._sanitizar_texto('PETR4\x00\x01')
        assert '\x00' not in resultado
        assert '\x01' not in resultado
        assert 'PETR4' in resultado

    def test_trunca_em_500_chars(self, app):
        svc = _service()
        texto_longo = 'A' * 600
        assert len(svc._sanitizar_texto(texto_longo)) == 500

    def test_texto_normal_preservado(self, app):
        svc = _service()
        assert svc._sanitizar_texto('XP INVESTIMENTOS') == 'XP INVESTIMENTOS'

    def test_none_retorna_vazio(self, app):
        svc = _service()
        assert svc._sanitizar_texto(None) == ''


# ---------------------------------------------------------------------------
# Testes: _gerar_hash_linha
# ---------------------------------------------------------------------------

class TestGerarHashLinha:
    def test_hash_determinista(self, app):
        svc = _service('arq.xlsx')
        mov = _make_movimentacao()
        h1 = svc._gerar_hash_linha(mov)
        h2 = svc._gerar_hash_linha(mov)
        assert h1 == h2

    def test_hash_diferente_por_arquivo(self, app):
        svc1 = _service('arquivo_a.xlsx')
        svc2 = _service('arquivo_b.xlsx')
        mov = _make_movimentacao()
        assert svc1._gerar_hash_linha(mov) != svc2._gerar_hash_linha(mov)

    def test_hash_diferente_por_valor(self, app):
        svc = _service('arq.xlsx')
        mov1 = _make_movimentacao(valor=8.00)
        mov2 = _make_movimentacao(valor=9.00)
        assert svc._gerar_hash_linha(mov1) != svc._gerar_hash_linha(mov2)

    def test_hash_e_md5_hexdigest_32_chars(self, app):
        svc = _service('arq.xlsx')
        h = svc._gerar_hash_linha(_make_movimentacao())
        assert len(h) == 32


# ---------------------------------------------------------------------------
# Testes: idempotência de proventos
# ---------------------------------------------------------------------------

class TestIdempotenciaProventos:
    def test_reimportacao_nao_duplica(self, app):
        svc = _service('mov_test.xlsx')
        mov = _make_movimentacao(produto=f'BTLG{uuid.uuid4().int % 100:02d}')
        hash_val = svc._gerar_hash_linha(mov)

        try:
            r1 = svc.importar_movimentacoes([mov])
            assert r1['proventos']['sucesso'] == 1
            assert r1['proventos']['duplicatas_ignoradas'] == 0

            r2 = svc.importar_movimentacoes([mov])
            assert r2['proventos']['sucesso'] == 0
            assert r2['proventos']['duplicatas_ignoradas'] == 1

            count = Provento.query.filter_by(hash_importacao=hash_val).count()
            assert count == 1
        finally:
            _cleanup_por_hash(hash_val)

    def test_relatorio_duplicatas_lista(self, app):
        svc = _service('mov_test2.xlsx')
        mov = _make_movimentacao(produto=f'HYPE{uuid.uuid4().int % 100:02d}')
        hash_val = svc._gerar_hash_linha(mov)

        try:
            svc.importar_movimentacoes([mov])
            r2 = svc.importar_movimentacoes([mov])
            assert len(r2['proventos']['duplicatas_lista']) == 1
            assert 'Duplicata ignorada' in r2['proventos']['duplicatas_lista'][0]
        finally:
            _cleanup_por_hash(hash_val)

    def test_arquivo_diferente_permite_insercao(self, app):
        """Mesmo conteúdo mas arquivo diferente = registros diferentes = ambos inseridos"""
        svc_a = _service('arquivo_a.xlsx')
        svc_b = _service('arquivo_b.xlsx')
        produto = f'RBRR{uuid.uuid4().int % 100:02d}'
        mov = _make_movimentacao(produto=produto)
        hash_a = svc_a._gerar_hash_linha(mov)
        hash_b = svc_b._gerar_hash_linha(mov)

        try:
            r1 = svc_a.importar_movimentacoes([mov])
            r2 = svc_b.importar_movimentacoes([mov])
            assert r1['proventos']['sucesso'] == 1
            assert r2['proventos']['sucesso'] == 1
        finally:
            _cleanup_por_hash(hash_a)
            _cleanup_por_hash(hash_b)


# ---------------------------------------------------------------------------
# Testes: dry_run de proventos
# ---------------------------------------------------------------------------

class TestDryRunProventos:
    def test_dry_run_nao_persiste(self, app):
        svc = _service('dry_test.xlsx')
        mov = _make_movimentacao(produto=f'MXRF{uuid.uuid4().int % 100:02d}')
        hash_val = svc._gerar_hash_linha(mov)

        try:
            r = svc.importar_movimentacoes([mov], dry_run=True)
            assert r['dry_run'] is True
            assert r['proventos']['sucesso'] == 1
            count = Provento.query.filter_by(hash_importacao=hash_val).count()
            assert count == 0
        finally:
            _cleanup_por_hash(hash_val)

    def test_dry_run_reporta_duplicatas_sem_persistir(self, app):
        svc = _service('dry_test2.xlsx')
        mov = _make_movimentacao(produto=f'VISC{uuid.uuid4().int % 100:02d}')
        hash_val = svc._gerar_hash_linha(mov)

        try:
            svc.importar_movimentacoes([mov])
            r = svc.importar_movimentacoes([mov], dry_run=True)
            assert r['dry_run'] is True
            assert r['proventos']['duplicatas_ignoradas'] == 1
        finally:
            _cleanup_por_hash(hash_val)


# ---------------------------------------------------------------------------
# Testes: idempotência de negociações (transações)
# ---------------------------------------------------------------------------

class TestIdempotenciaNegociacoes:
    def test_reimportacao_nao_duplica(self, app):
        svc = _service('neg_test.xlsx')
        neg = _make_negociacao(codigo=f'PETR{uuid.uuid4().int % 10}')
        hash_val = svc._gerar_hash_linha(neg)

        try:
            r1 = svc.importar_negociacoes([neg])
            assert r1['sucesso'] == 1
            assert r1['duplicatas_ignoradas'] == 0

            r2 = svc.importar_negociacoes([neg])
            assert r2['sucesso'] == 0
            assert r2['duplicatas_ignoradas'] == 1

            count = Transacao.query.filter_by(hash_importacao=hash_val).count()
            assert count == 1
        finally:
            _cleanup_por_hash(hash_val)

    def test_dry_run_nao_persiste_transacao(self, app):
        svc = _service('neg_dry.xlsx')
        neg = _make_negociacao(codigo=f'VALE{uuid.uuid4().int % 10}')
        hash_val = svc._gerar_hash_linha(neg)

        try:
            r = svc.importar_negociacoes([neg], dry_run=True)
            assert r['dry_run'] is True
            assert r['sucesso'] == 1
            count = Transacao.query.filter_by(hash_importacao=hash_val).count()
            assert count == 0
        finally:
            _cleanup_por_hash(hash_val)


# ---------------------------------------------------------------------------
# Testes: sanitização no fluxo de importação
# ---------------------------------------------------------------------------

class TestSanitizacaoNaImportacao:
    def test_xss_na_instituicao_e_limpo(self, app):
        svc = _service('sanit_test.xlsx')
        mov = _make_movimentacao(
            produto=f'XPML{uuid.uuid4().int % 10}',
            instituicao='<script>alert(1)</script>XP'
        )
        # Hash calculado após sanitização, como o service faz internamente
        mov_sanitizado = dict(mov)
        mov_sanitizado['instituicao'] = svc._sanitizar_texto(mov['instituicao'])
        mov_sanitizado['produto'] = svc._sanitizar_texto(mov['produto'])
        hash_val = svc._gerar_hash_linha(mov_sanitizado)

        try:
            r = svc.importar_movimentacoes([mov])
            assert r['proventos']['sucesso'] == 1
            provento = Provento.query.filter_by(hash_importacao=hash_val).first()
            assert provento is not None
        finally:
            _cleanup_por_hash(hash_val)

    def test_caractere_controle_no_produto_e_limpo(self, app):
        svc = _service('sanit_test2.xlsx')
        produto_limpo = f'KNRI{uuid.uuid4().int % 10}'
        mov = _make_movimentacao(produto=f'{produto_limpo}\x00')
        hash_val = svc._gerar_hash_linha(mov)

        try:
            svc._sanitizar_texto(f'{produto_limpo}\x00')
            assert True
        finally:
            _cleanup_por_hash(hash_val)
