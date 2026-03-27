# -*- coding: utf-8 -*-
"""
Testes — EXITUS-COVERAGE-001
Cobertura de import_b3_service.py: parsers, validações e edge cases.
"""

import io
import os
import tempfile
import uuid
import pytest
from datetime import date, datetime
from decimal import Decimal

import pandas as pd

from app.services.import_b3_service import ImportB3Service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _service(arquivo='test_parsers.xlsx'):
    svc = ImportB3Service()
    svc.arquivo_origem = arquivo
    return svc


def _tmp_csv(conteudo: str, suffix='.csv') -> str:
    """Cria arquivo temporário CSV com o conteúdo dado."""
    f = tempfile.NamedTemporaryFile(
        mode='w', suffix=suffix, delete=False, encoding='utf-8'
    )
    f.write(conteudo)
    f.close()
    return f.name


def _tmp_excel(df: pd.DataFrame) -> str:
    """Cria arquivo temporário Excel com o DataFrame dado."""
    f = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    f.close()
    df.to_excel(f.name, index=False)
    return f.name


# ---------------------------------------------------------------------------
# Testes: _parse_data
# ---------------------------------------------------------------------------

class TestParseData:
    def test_formato_brasileiro_completo(self, app):
        svc = _service()
        resultado = svc._parse_data('15/03/2025')
        assert resultado == date(2025, 3, 15)

    def test_formato_brasileiro_curto(self, app):
        svc = _service()
        resultado = svc._parse_data('15/03/25')
        assert resultado == date(2025, 3, 15)

    def test_formato_iso(self, app):
        svc = _service()
        resultado = svc._parse_data('2025-03-15')
        assert resultado == date(2025, 3, 15)

    def test_string_vazia_retorna_none(self, app):
        svc = _service()
        assert svc._parse_data('') is None

    def test_none_retorna_none(self, app):
        svc = _service()
        assert svc._parse_data(None) is None

    def test_formato_invalido_retorna_none(self, app):
        svc = _service()
        assert svc._parse_data('data_invalida') is None

    def test_formato_invalido_parcial_retorna_none(self, app):
        svc = _service()
        assert svc._parse_data('32/13/2025') is None

    def test_com_espacos_extras(self, app):
        svc = _service()
        resultado = svc._parse_data('  15/03/2025  ')
        assert resultado == date(2025, 3, 15)


# ---------------------------------------------------------------------------
# Testes: _parse_quantidade
# ---------------------------------------------------------------------------

class TestParseQuantidade:
    def test_inteiro(self, app):
        svc = _service()
        assert svc._parse_quantidade(100) == Decimal('100')

    def test_float(self, app):
        svc = _service()
        assert svc._parse_quantidade(100.0) == Decimal('100')

    def test_string_numerica(self, app):
        svc = _service()
        assert svc._parse_quantidade('100') == Decimal('100')

    def test_string_com_separador(self, app):
        svc = _service()
        assert svc._parse_quantidade('1.000') == Decimal('1000')

    def test_traco_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_quantidade('-') == Decimal('0')

    def test_none_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_quantidade(None) == Decimal('0')

    def test_vazio_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_quantidade('') == Decimal('0')

    def test_nan_retorna_zero(self, app):
        import math
        svc = _service()
        assert svc._parse_quantidade(float('nan')) == Decimal('0')


# ---------------------------------------------------------------------------
# Testes: _parse_monetario
# ---------------------------------------------------------------------------

class TestParseMonetario:
    def test_float(self, app):
        svc = _service()
        assert svc._parse_monetario(12.50) == Decimal('12.5')

    def test_inteiro(self, app):
        svc = _service()
        assert svc._parse_monetario(100) == Decimal('100')

    def test_string_formato_brasileiro(self, app):
        svc = _service()
        assert svc._parse_monetario('1.234,56') == Decimal('1234.56')

    def test_string_com_rs(self, app):
        svc = _service()
        assert svc._parse_monetario('R$ 1.234,56') == Decimal('1234.56')

    def test_string_formato_americano(self, app):
        svc = _service()
        assert svc._parse_monetario('1234.56') == Decimal('1234.56')

    def test_traco_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_monetario('-') == Decimal('0')

    def test_none_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_monetario(None) == Decimal('0')

    def test_vazio_retorna_zero(self, app):
        svc = _service()
        assert svc._parse_monetario('') == Decimal('0')

    def test_nan_retorna_zero(self, app):
        import math
        svc = _service()
        assert svc._parse_monetario(float('nan')) == Decimal('0')

    def test_valor_zero(self, app):
        svc = _service()
        assert svc._parse_monetario(0) == Decimal('0')


# ---------------------------------------------------------------------------
# Testes: _extrair_ticker
# ---------------------------------------------------------------------------

class TestExtrairTicker:
    def test_fii_com_descricao(self, app):
        svc = _service()
        assert svc._extrair_ticker('BTLG11 - BTG PACTUAL LOGISTICA') == 'BTLG11'

    def test_acao_simples(self, app):
        svc = _service()
        assert svc._extrair_ticker('PETR4') == 'PETR4'

    def test_fii_simples(self, app):
        svc = _service()
        assert svc._extrair_ticker('XPML11') == 'XPML11'

    def test_com_hifen(self, app):
        svc = _service()
        resultado = svc._extrair_ticker('KNRI11-FII')
        assert resultado == 'KNRI11'

    def test_minusculo_e_convertido(self, app):
        svc = _service()
        assert svc._extrair_ticker('petr4') == 'PETR4'

    def test_vazio_retorna_vazio(self, app):
        svc = _service()
        assert svc._extrair_ticker('') == ''

    def test_none_retorna_vazio(self, app):
        svc = _service()
        assert svc._extrair_ticker(None) == ''

    def test_ticker_com_tres_digitos(self, app):
        svc = _service()
        assert svc._extrair_ticker('VALE3 - VALE ON') == 'VALE3'

    def test_bdr_ticker(self, app):
        """BDRs têm 5 letras + 1 dígito: AAPL34"""
        svc = _service()
        assert svc._extrair_ticker('AAPL34 - APPLE BDR') == 'AAPL34'


# ---------------------------------------------------------------------------
# Testes: _obter_ou_criar_ativo (tipo FII vs ACAO)
# ---------------------------------------------------------------------------

class TestObterOuCriarAtivo:
    def test_ticker_fii_11_detectado(self, app):
        from app.models.ativo import TipoAtivo
        svc = _service()
        svc.usuario_id = None
        resultado = {'ativos_criados': 0}
        ativo = svc._obter_ou_criar_ativo('BTLG11', resultado)
        assert ativo.tipo == TipoAtivo.FII

    def test_ticker_acao_detectado(self, app):
        from app.models.ativo import TipoAtivo
        svc = _service()
        resultado = {'ativos_criados': 0}
        ativo = svc._obter_ou_criar_ativo('PETR4', resultado)
        assert ativo.tipo == TipoAtivo.ACAO

    def test_ativo_existente_nao_duplica(self, app):
        svc = _service()
        resultado = {'ativos_criados': 0}
        # Primeira chamada — cria ou encontra
        ativo1 = svc._obter_ou_criar_ativo('VALE3', resultado)
        # Segunda chamada — deve retornar o mesmo
        resultado2 = {'ativos_criados': 0}
        ativo2 = svc._obter_ou_criar_ativo('VALE3', resultado2)
        assert ativo1.id == ativo2.id
        assert resultado2['ativos_criados'] == 0


# ---------------------------------------------------------------------------
# Testes: _gerar_hash_linha
# ---------------------------------------------------------------------------

class TestGerarHashLinha:
    def test_hash_deterministico(self, app):
        svc = _service('arquivo.xlsx')
        row = {
            'data': date(2025, 1, 1),
            'tipo_movimentacao': 'Dividendo',
            'produto': 'PETR4',
            'instituicao': 'XP',
            'quantidade': 100,
            'preco_unitario': Decimal('2.00'),
            'valor_operacao': Decimal('200.00'),
        }
        h1 = svc._gerar_hash_linha(row)
        h2 = svc._gerar_hash_linha(row)
        assert h1 == h2

    def test_hash_muda_com_arquivo(self, app):
        row = {
            'data': date(2025, 1, 1),
            'tipo_movimentacao': 'Dividendo',
            'produto': 'PETR4',
            'instituicao': 'XP',
            'quantidade': 100,
            'preco_unitario': Decimal('2.00'),
            'valor_operacao': Decimal('200.00'),
        }
        svc1 = _service('arquivo_a.xlsx')
        svc2 = _service('arquivo_b.xlsx')
        assert svc1._gerar_hash_linha(row) != svc2._gerar_hash_linha(row)

    def test_hash_muda_com_conteudo(self, app):
        svc = _service('arquivo.xlsx')
        row1 = {'data': date(2025, 1, 1), 'tipo_movimentacao': 'Dividendo',
                'produto': 'PETR4', 'instituicao': 'XP',
                'quantidade': 100, 'preco_unitario': Decimal('2.00'),
                'valor_operacao': Decimal('200.00')}
        row2 = {**row1, 'valor_operacao': Decimal('300.00')}
        assert svc._gerar_hash_linha(row1) != svc._gerar_hash_linha(row2)

    def test_hash_32_chars(self, app):
        svc = _service()
        row = {'data': date(2025, 1, 1), 'tipo_movimentacao': 'Dividendo',
               'produto': 'PETR4', 'instituicao': 'XP',
               'quantidade': 100, 'preco_unitario': Decimal('2.00'),
               'valor_operacao': Decimal('200.00')}
        h = svc._gerar_hash_linha(row)
        assert len(h) == 32


# ---------------------------------------------------------------------------
# Testes: parse_movimentacoes (CSV)
# ---------------------------------------------------------------------------

class TestParseMovimentacoesCSV:
    def test_parse_csv_valido(self, app):
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            "15/03/2025,Dividendo,PETR4 - PETROBRAS,XP INVESTIMENTOS,100,2.00,200.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 1
            assert resultado[0]['tipo_movimentacao'] == 'Dividendo'
            assert resultado[0]['produto'] == 'PETR4 - PETROBRAS'
        finally:
            os.unlink(caminho)

    def test_parse_csv_linha_sem_data_ignorada(self, app):
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            ",Dividendo,PETR4,XP,100,2.00,200.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)

    def test_parse_csv_valor_zero_ignorado(self, app):
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            "15/03/2025,Dividendo,PETR4,XP,0,0.00,0.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)

    def test_parse_csv_tipo_custodia_ignorado(self, app):
        """'Transferência - Liquidação' é filtrado pelo parse_movimentacoes."""
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            "15/03/2025,Transferência - Liquidação,PETR4,XP,100,2.00,200.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)

    def test_parse_csv_tipo_cessao_ignorado(self, app):
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            "15/03/2025,Cessão de Direitos - Solicitada,PETR4,XP,100,2.00,200.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)

    def test_parse_csv_multiplas_linhas(self, app):
        csv = (
            "Data,Movimentação,Produto,Instituição,Quantidade,Preço unitário,Valor da Operação\n"
            "15/03/2025,Dividendo,PETR4,XP,100,2.00,200.00\n"
            "16/03/2025,Rendimento,XPML11,XP,50,0.80,40.00\n"
            "17/03/2025,Juros Sobre Capital Próprio,ITUB4,BTG,200,1.50,300.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_movimentacoes(caminho)
            assert len(resultado) == 3
        finally:
            os.unlink(caminho)


# ---------------------------------------------------------------------------
# Testes: parse_negociacoes (CSV)
# ---------------------------------------------------------------------------

class TestParseNegociacoesCSV:
    def test_parse_csv_negociacao_compra(self, app):
        csv = (
            "Data do Negócio,Tipo de Movimentação,Mercado,Prazo/Vencimento,Instituição,"
            "Código de Negociação,Quantidade,Preço,Valor\n"
            "15/03/2025,Compra,Mercado a Vista,,XP,PETR4,100,38.50,3850.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_negociacoes(caminho)
            assert len(resultado) == 1
            assert resultado[0]['tipo_movimentacao'] == 'Compra'
            assert resultado[0]['codigo_negociacao'] == 'PETR4'
            assert resultado[0]['quantidade'] == Decimal('100')
        finally:
            os.unlink(caminho)

    def test_parse_csv_negociacao_venda(self, app):
        csv = (
            "Data do Negócio,Tipo de Movimentação,Mercado,Prazo/Vencimento,Instituição,"
            "Código de Negociação,Quantidade,Preço,Valor\n"
            "15/03/2025,Venda,Mercado a Vista,,XP,VALE3,50,85.00,4250.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_negociacoes(caminho)
            assert len(resultado) == 1
            assert resultado[0]['tipo_movimentacao'] == 'Venda'
        finally:
            os.unlink(caminho)

    def test_parse_csv_sem_data_retorna_vazio(self, app):
        """Linha com data inválida deve ser ignorada."""
        csv = (
            "Data do Negócio,Tipo de Movimentação,Mercado,Prazo/Vencimento,Instituição,"
            "Código de Negociação,Quantidade,Preço,Valor\n"
            "DATA_ERRADA,Compra,Mercado a Vista,,XP,PETR4,100,38.50,3850.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_negociacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)

    def test_parse_csv_sem_data_ignorado(self, app):
        csv = (
            "Data do Negócio,Tipo de Movimentação,Mercado,Prazo/Vencimento,Instituição,"
            "Código de Negociação,Quantidade,Preço,Valor\n"
            ",Compra,Mercado a Vista,,XP,PETR4,100,38.50,3850.00\n"
        )
        caminho = _tmp_csv(csv)
        try:
            svc = _service(caminho)
            resultado = svc.parse_negociacoes(caminho)
            assert len(resultado) == 0
        finally:
            os.unlink(caminho)


# ---------------------------------------------------------------------------
# Testes: importar_negociacoes — tipo não mapeado
# ---------------------------------------------------------------------------

class TestImportarNegociacoesTipos:
    def test_tipo_nao_mapeado_gera_erro(self, app):
        svc = _service()
        neg = [{
            'data': date(2025, 3, 15),
            'tipo_movimentacao': 'TipoInexistente',
            'codigo_negociacao': 'PETR4',
            'instituicao': 'XP',
            'quantidade': Decimal('100'),
            'preco': Decimal('38.50'),
            'valor': Decimal('3850.00'),
            'mercado': 'Vista',
            'prazo_vencimento': '',
        }]
        resultado = svc.importar_negociacoes(neg, dry_run=True)
        assert resultado['erros'] == 1
        assert any('não mapeado' in e for e in resultado['erros_lista'])

    def test_tipo_compra_mapeado_corretamente(self, app):
        from app.models.transacao import TipoTransacao
        svc = _service()
        tipo = svc.mapeamento_tipos_transacao.get('Compra')
        assert tipo == TipoTransacao.COMPRA

    def test_tipo_venda_mapeado_corretamente(self, app):
        from app.models.transacao import TipoTransacao
        svc = _service()
        tipo = svc.mapeamento_tipos_transacao.get('Venda')
        assert tipo == TipoTransacao.VENDA


# ---------------------------------------------------------------------------
# Testes: importar_movimentacoes — tipo não mapeado
# ---------------------------------------------------------------------------

class TestImportarMovimentacoesTipos:
    def test_tipo_nao_mapeado_gera_erro(self, app):
        svc = _service()
        mov = [{
            'data': date(2025, 3, 15),
            'tipo_movimentacao': 'TipoDesconhecido',
            'produto': 'PETR4',
            'instituicao': 'XP',
            'quantidade': Decimal('100'),
            'preco_unitario': Decimal('2.00'),
            'valor_operacao': Decimal('200.00'),
        }]
        resultado = svc.importar_movimentacoes(mov, dry_run=True)
        assert resultado['proventos']['erros'] == 1

    def test_todos_tipos_provento_mapeados(self, app):
        """Verifica que todos os tipos do mapeamento são TipoProvento válidos."""
        from app.models.provento import TipoProvento
        svc = _service()
        for nome, tipo in svc.mapeamento_tipos_provento.items():
            assert isinstance(tipo, TipoProvento), f"Tipo inválido para: {nome}"

    def test_dry_run_movimentacoes_nao_persiste(self, app):
        """dry_run=True não deve persistir nenhum provento."""
        from app.models.provento import Provento
        svc = _service('dry_run_mov_test.xlsx')
        sufixo = str(uuid.uuid4())[:8]
        mov = [{
            'data': date(2025, 3, 15),
            'tipo_movimentacao': 'Dividendo',
            'produto': f'PETR{sufixo[:1]}',
            'instituicao': 'XP',
            'quantidade': Decimal('100'),
            'preco_unitario': Decimal('2.00'),
            'valor_operacao': Decimal('200.00'),
        }]
        count_antes = Provento.query.count()
        svc.importar_movimentacoes(mov, dry_run=True)
        count_depois = Provento.query.count()
        assert count_antes == count_depois

    def test_dry_run_negociacoes_nao_persiste(self, app):
        """dry_run=True não deve persistir nenhuma transação."""
        from app.models.transacao import Transacao
        svc = _service('dry_run_neg_test.xlsx')
        neg = [{
            'data': date(2025, 3, 15),
            'tipo_movimentacao': 'Compra',
            'codigo_negociacao': 'VALE3',
            'instituicao': 'BTG',
            'quantidade': Decimal('50'),
            'preco': Decimal('85.00'),
            'valor': Decimal('4250.00'),
            'mercado': 'Vista',
            'prazo_vencimento': '',
        }]
        count_antes = Transacao.query.count()
        svc.importar_negociacoes(neg, dry_run=True)
        count_depois = Transacao.query.count()
        assert count_antes == count_depois
