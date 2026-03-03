# -*- coding: utf-8 -*-
"""
EXITUS-TESTS-001 — Testes unitários de business_rules.py

Cobre as 5 regras de negócio implementadas em EXITUS-BUSINESS-001:
1. validar_horario_mercado
2. validar_feriado (mockado)
3. validar_saldo_venda (mockado)
4. calcular_taxas_b3
5. detectar_day_trade (mockado)
"""
import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from app.utils.business_rules import (
    validar_horario_mercado,
    calcular_taxas_b3,
    TAXAS_B3,
    HORARIOS_MERCADO,
)


# ===========================================================================
# 1. validar_horario_mercado
# ===========================================================================
class TestValidarHorarioMercado:

    def test_dentro_pregao_b3(self):
        dt = datetime(2026, 3, 3, 12, 0)
        assert validar_horario_mercado(dt, 'B3') is None

    def test_antes_abertura_b3(self):
        dt = datetime(2026, 3, 3, 9, 59)
        result = validar_horario_mercado(dt, 'B3')
        assert result is not None
        assert 'B3' in result
        assert '10:00' in result

    def test_apos_fechamento_b3(self):
        dt = datetime(2026, 3, 3, 17, 1)
        result = validar_horario_mercado(dt, 'B3')
        assert result is not None
        assert '17:00' in result

    def test_exatamente_abertura_b3(self):
        dt = datetime(2026, 3, 3, 10, 0)
        assert validar_horario_mercado(dt, 'B3') is None

    def test_exatamente_fechamento_b3(self):
        dt = datetime(2026, 3, 3, 17, 0)
        assert validar_horario_mercado(dt, 'B3') is None

    def test_dentro_pregao_nyse(self):
        dt = datetime(2026, 3, 3, 14, 0)
        assert validar_horario_mercado(dt, 'NYSE') is None

    def test_antes_abertura_nyse(self):
        dt = datetime(2026, 3, 3, 9, 0)
        result = validar_horario_mercado(dt, 'NYSE')
        assert result is not None
        assert '09:30' in result

    def test_dentro_pregao_nasdaq(self):
        dt = datetime(2026, 3, 3, 11, 0)
        assert validar_horario_mercado(dt, 'NASDAQ') is None

    def test_mercado_desconhecido_retorna_none(self):
        dt = datetime(2026, 3, 3, 8, 0)
        assert validar_horario_mercado(dt, 'BOLSA_XPTO') is None

    def test_data_nao_datetime_retorna_none(self):
        assert validar_horario_mercado('2026-03-03', 'B3') is None

    def test_none_retorna_none(self):
        assert validar_horario_mercado(None, 'B3') is None

    def test_mercado_case_insensitive(self):
        dt = datetime(2026, 3, 3, 8, 0)
        result_upper = validar_horario_mercado(dt, 'B3')
        result_lower = validar_horario_mercado(dt, 'b3')
        assert result_upper is not None
        assert result_lower is not None
        assert '10:00' in result_upper
        assert '10:00' in result_lower


# ===========================================================================
# 2. calcular_taxas_b3 (sem DB — pure math)
# ===========================================================================
class TestCalcularTaxasB3:

    def test_calculo_basico(self):
        resultado = calcular_taxas_b3(Decimal('1000.00'))
        assert 'emolumentos' in resultado
        assert 'taxa_liquidacao' in resultado

    def test_valores_corretos_1000(self):
        resultado = calcular_taxas_b3(Decimal('1000.00'))
        esperado_emol = round(Decimal('1000.00') * TAXAS_B3['emolumentos'], 2)
        esperado_liq = round(Decimal('1000.00') * TAXAS_B3['taxa_liquidacao'], 2)
        assert resultado['emolumentos'] == esperado_emol
        assert resultado['taxa_liquidacao'] == esperado_liq

    def test_valores_corretos_10000(self):
        resultado = calcular_taxas_b3(Decimal('10000.00'))
        assert resultado['emolumentos'] == Decimal('0.33')
        assert resultado['taxa_liquidacao'] == Decimal('2.75')

    def test_valor_zero(self):
        resultado = calcular_taxas_b3(Decimal('0'))
        assert resultado['emolumentos'] == Decimal('0.00')
        assert resultado['taxa_liquidacao'] == Decimal('0.00')

    def test_aceita_float(self):
        resultado = calcular_taxas_b3(1000.0)
        assert resultado['emolumentos'] > Decimal('0')

    def test_aceita_int(self):
        resultado = calcular_taxas_b3(1000)
        assert resultado['emolumentos'] > Decimal('0')

    def test_retorno_e_decimal(self):
        resultado = calcular_taxas_b3(Decimal('1000.00'))
        assert isinstance(resultado['emolumentos'], Decimal)
        assert isinstance(resultado['taxa_liquidacao'], Decimal)

    def test_proporcionalidade(self):
        r10k = calcular_taxas_b3(Decimal('10000.00'))
        r20k = calcular_taxas_b3(Decimal('20000.00'))
        assert r20k['emolumentos'] == r10k['emolumentos'] * 2
        assert r20k['taxa_liquidacao'] == r10k['taxa_liquidacao'] * 2


# ===========================================================================
# 3. validar_feriado (com mock de FeriadoMercado.query)
# ===========================================================================
class TestValidarFeriado:

    def test_sem_feriado_retorna_none(self):
        feriado_mock = MagicMock()
        feriado_mock.query.filter_by.return_value.filter.return_value.first.return_value = None
        feriado_mock.query.filter_by.return_value.first.return_value = None

        with patch('app.utils.business_rules.FeriadoMercado', feriado_mock):
            from app.utils import business_rules
            result = business_rules.validar_feriado(date(2026, 3, 3), 'B3')
        assert result is None

    def test_com_feriado_retorna_warning(self):
        item = MagicMock()
        item.nome = 'Carnaval'
        item.tipo_feriado.value = 'NACIONAL'

        feriado_mock = MagicMock()
        feriado_mock.query.filter_by.return_value.filter.return_value.first.return_value = item
        feriado_mock.query.filter_by.return_value.first.return_value = item

        with patch('app.utils.business_rules.FeriadoMercado', feriado_mock):
            from app.utils import business_rules
            result = business_rules.validar_feriado(date(2026, 3, 3), 'B3')
        assert result is not None
        assert 'Carnaval' in result

    def test_aceita_datetime(self):
        feriado_mock = MagicMock()
        feriado_mock.query.filter_by.return_value.filter.return_value.first.return_value = None
        feriado_mock.query.filter_by.return_value.first.return_value = None

        with patch('app.utils.business_rules.FeriadoMercado', feriado_mock):
            from app.utils import business_rules
            result = business_rules.validar_feriado(datetime(2026, 3, 3, 10, 0), 'B3')
        assert result is None


# ===========================================================================
# 4. validar_saldo_venda (com mock de Posicao.query)
# ===========================================================================
class TestValidarSaldoVenda:

    def _posicao_mock(self, quantidade):
        m = MagicMock()
        m.quantidade = quantidade
        return m

    def _make_posicao_cls(self, posicoes):
        cls = MagicMock()
        cls.query.filter_by.return_value.filter_by.return_value.all.return_value = posicoes
        cls.query.filter_by.return_value.all.return_value = posicoes
        return cls

    def test_sem_posicao_levanta_erro(self):
        posicao_cls = self._make_posicao_cls([])
        with patch('app.utils.business_rules.Posicao', posicao_cls):
            from app.utils import business_rules
            with pytest.raises(ValueError, match='não há posição'):
                business_rules.validar_saldo_venda('uid', 'aid', Decimal('10'))

    def test_saldo_insuficiente_levanta_erro(self):
        posicao_cls = self._make_posicao_cls([self._posicao_mock(Decimal('5'))])
        with patch('app.utils.business_rules.Posicao', posicao_cls):
            from app.utils import business_rules
            with pytest.raises(ValueError, match='Saldo insuficiente'):
                business_rules.validar_saldo_venda('uid', 'aid', Decimal('10'))

    def test_saldo_suficiente_retorna_none(self):
        posicao_cls = self._make_posicao_cls([self._posicao_mock(Decimal('20'))])
        with patch('app.utils.business_rules.Posicao', posicao_cls):
            from app.utils import business_rules
            result = business_rules.validar_saldo_venda('uid', 'aid', Decimal('10'))
        assert result is None

    def test_saldo_exato_retorna_none(self):
        posicao_cls = self._make_posicao_cls([self._posicao_mock(Decimal('10'))])
        with patch('app.utils.business_rules.Posicao', posicao_cls):
            from app.utils import business_rules
            result = business_rules.validar_saldo_venda('uid', 'aid', Decimal('10'))
        assert result is None

    def test_soma_multiplas_posicoes(self):
        posicoes = [self._posicao_mock(Decimal('5')), self._posicao_mock(Decimal('7'))]
        posicao_cls = self._make_posicao_cls(posicoes)
        with patch('app.utils.business_rules.Posicao', posicao_cls):
            from app.utils import business_rules
            result = business_rules.validar_saldo_venda('uid', 'aid', Decimal('10'))
        assert result is None


# ===========================================================================
# 5. detectar_day_trade (com mock de Transacao.query)
# ===========================================================================
class TestDetectarDayTrade:

    def _transacao_cls(self, first_result):
        cls = MagicMock()
        cls.query.filter.return_value.first.return_value = first_result
        cls.tipo = 'compra'
        return cls

    def test_sem_operacao_oposta_retorna_false(self):
        t_cls = self._transacao_cls(None)
        with patch('app.utils.business_rules.Transacao', t_cls):
            from app.utils import business_rules
            result = business_rules.detectar_day_trade('uid', 'aid', datetime(2026, 3, 3, 10, 0), 'compra')
        assert result is False

    def test_com_operacao_oposta_retorna_true(self):
        t_cls = self._transacao_cls(MagicMock())
        with patch('app.utils.business_rules.Transacao', t_cls):
            from app.utils import business_rules
            result = business_rules.detectar_day_trade('uid', 'aid', datetime(2026, 3, 3, 10, 0), 'compra')
        assert result is True

    def test_tipo_nao_compra_venda_retorna_false(self):
        from app.utils.business_rules import detectar_day_trade
        result = detectar_day_trade('uid', 'aid', datetime(2026, 3, 3, 10, 0), 'dividendo')
        assert result is False

    def test_aceita_date_sem_hora(self):
        t_cls = self._transacao_cls(None)
        with patch('app.utils.business_rules.Transacao', t_cls):
            from app.utils import business_rules
            result = business_rules.detectar_day_trade('uid', 'aid', date(2026, 3, 3), 'venda')
        assert result is False


# ===========================================================================
# 6. validar_transacao — orquestradora (mocks completos)
# ===========================================================================
class TestValidarTransacao:

    @patch('app.utils.business_rules.detectar_day_trade', return_value=False)
    @patch('app.utils.business_rules.validar_feriado', return_value=None)
    @patch('app.utils.business_rules.validar_horario_mercado', return_value=None)
    def test_compra_sem_issues_retorna_estrutura(self, mock_hora, mock_feriado, mock_dt):
        from app.utils.business_rules import validar_transacao
        data = {
            'tipo': 'compra',
            'data_transacao': datetime(2026, 3, 3, 12, 0),
            'ativo_id': 'aid',
            'quantidade': Decimal('10'),
            'preco_unitario': Decimal('38.50'),
        }
        result = validar_transacao('uid', data, 'B3')
        assert 'warnings' in result
        assert 'is_day_trade' in result
        assert 'taxas_calculadas' in result
        assert result['warnings'] == []
        assert result['is_day_trade'] is False
        assert result['taxas_calculadas'] is not None

    @patch('app.utils.business_rules.detectar_day_trade', return_value=True)
    @patch('app.utils.business_rules.validar_feriado', return_value=None)
    @patch('app.utils.business_rules.validar_horario_mercado', return_value=None)
    def test_day_trade_detectado_adiciona_warning(self, mock_hora, mock_feriado, mock_dt):
        from app.utils.business_rules import validar_transacao
        data = {
            'tipo': 'compra',
            'data_transacao': datetime(2026, 3, 3, 12, 0),
            'ativo_id': 'aid',
            'quantidade': Decimal('10'),
            'preco_unitario': Decimal('38.50'),
        }
        result = validar_transacao('uid', data, 'B3')
        assert result['is_day_trade'] is True
        assert any('Day-trade' in w for w in result['warnings'])

    @patch('app.utils.business_rules.detectar_day_trade', return_value=False)
    @patch('app.utils.business_rules.validar_feriado', return_value=None)
    @patch('app.utils.business_rules.validar_horario_mercado', return_value='Fora do pregão')
    def test_warning_horario_incluido(self, mock_hora, mock_feriado, mock_dt):
        from app.utils.business_rules import validar_transacao
        data = {
            'tipo': 'compra',
            'data_transacao': datetime(2026, 3, 3, 8, 0),
            'ativo_id': 'aid',
            'quantidade': Decimal('10'),
            'preco_unitario': Decimal('38.50'),
        }
        result = validar_transacao('uid', data, 'B3')
        assert 'Fora do pregão' in result['warnings']

    @patch('app.utils.business_rules.validar_saldo_venda', side_effect=ValueError('Saldo insuficiente'))
    @patch('app.utils.business_rules.validar_feriado', return_value=None)
    @patch('app.utils.business_rules.validar_horario_mercado', return_value=None)
    def test_venda_sem_saldo_levanta_erro(self, mock_hora, mock_feriado, mock_saldo):
        from app.utils.business_rules import validar_transacao
        data = {
            'tipo': 'venda',
            'data_transacao': datetime(2026, 3, 3, 12, 0),
            'ativo_id': 'aid',
            'quantidade': Decimal('100'),
            'preco_unitario': Decimal('38.50'),
        }
        with pytest.raises(ValueError, match='Saldo insuficiente'):
            validar_transacao('uid', data, 'B3')

    @patch('app.utils.business_rules.detectar_day_trade', return_value=False)
    @patch('app.utils.business_rules.validar_feriado', return_value=None)
    @patch('app.utils.business_rules.validar_horario_mercado', return_value=None)
    def test_tipo_nao_compra_venda_sem_taxas(self, mock_hora, mock_feriado, mock_dt):
        from app.utils.business_rules import validar_transacao
        data = {
            'tipo': 'dividendo',
            'data_transacao': datetime(2026, 3, 3, 12, 0),
        }
        result = validar_transacao('uid', data, 'B3')
        assert result['taxas_calculadas'] is None
        assert result['is_day_trade'] is False
