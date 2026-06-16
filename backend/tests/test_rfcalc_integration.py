# -*- coding: utf-8 -*-
"""
Exitus - Testes de Integração - RFCALC-001
Testes para Duration, YTM, FFO, AFFO e endpoints /calculos/rf e /calculos/fii
"""

import pytest
import json
from datetime import date, timedelta
from app.services.rfcalc_service import RFCalcService


class TestDuration:
    """Testes unitários para Duration de Macaulay e Modificada"""

    def test_duration_macaulay_titulo_par(self):
        """
        Título negociando no par: Duration próxima ao vencimento
        CDB: VN=1000, cupom=10%, 3 períodos, YTM=10%
        """
        fluxos = [100.0, 100.0, 1100.0]
        preco = 1000.0
        taxa = 0.10

        dur = RFCalcService.duration_macaulay(preco, fluxos, taxa)

        # Duration esperada ~2.7355 para título com cupom=10%, 3 anos
        assert 2.5 < dur < 3.0

    def test_duration_macaulay_zero_cupom(self):
        """Título zero-cupom de 1 período: Duration = 1.0 exato"""
        # Único fluxo no vencimento (1 período): Duration = 1
        fluxos = [1100.0]         # principal + juros ao final
        preco = 1000.0            # PV exato com taxa 10%: 1100/1.10 = 1000
        dur = RFCalcService.duration_macaulay(preco, fluxos, 0.10)
        assert abs(dur - 1.0) < 0.0001

    def test_duration_modificada_menor_que_macaulay(self):
        """Duration Modificada deve ser menor que Macaulay"""
        fluxos = [100.0, 100.0, 1100.0]
        preco = 1000.0
        ytm = 0.10

        dur_mac = RFCalcService.duration_macaulay(preco, fluxos, ytm)
        dur_mod = RFCalcService.duration_modificada(dur_mac, ytm)

        assert dur_mod < dur_mac
        assert abs(dur_mod - dur_mac / (1 + ytm)) < 0.0001

    def test_duration_preco_invalido(self):
        """Deve lançar exceção para preço zero ou negativo"""
        fluxos = [100.0, 1100.0]
        with pytest.raises(ValueError):
            RFCalcService.duration_macaulay(0, fluxos, 0.10)

        with pytest.raises(ValueError):
            RFCalcService.duration_macaulay(-100, fluxos, 0.10)


class TestYTM:
    """Testes unitários para Yield to Maturity"""

    def test_ytm_titulo_no_par(self):
        """Título no par: YTM deve ser igual ao cupom"""
        # CDB: VN=1000, cupom=10%, 3 anos, preço=1000
        fluxos = [100.0, 100.0, 1100.0]
        preco = 1000.0

        ytm = RFCalcService.calcular_ytm(preco, fluxos)

        assert abs(ytm - 0.10) < 0.0001

    def test_ytm_titulo_abaixo_par(self):
        """Título com desconto: YTM > cupom"""
        # Mesmo título mas preço = 950 (desconto)
        fluxos = [100.0, 100.0, 1100.0]
        preco = 950.0

        ytm = RFCalcService.calcular_ytm(preco, fluxos)

        assert ytm > 0.10  # YTM deve ser maior que cupom quando há desconto

    def test_ytm_titulo_acima_par(self):
        """Título com prêmio: YTM < cupom"""
        fluxos = [100.0, 100.0, 1100.0]
        preco = 1050.0

        ytm = RFCalcService.calcular_ytm(preco, fluxos)

        assert ytm < 0.10  # YTM deve ser menor que cupom quando há prêmio

    def test_ytm_preco_invalido(self):
        """Deve lançar exceção para preço zero"""
        with pytest.raises(ValueError):
            RFCalcService.calcular_ytm(0, [100.0, 1100.0])

    def test_ytm_fluxos_vazios(self):
        """Deve lançar exceção para lista de fluxos vazia"""
        with pytest.raises(ValueError):
            RFCalcService.calcular_ytm(1000.0, [])


class TestFluxosCupom:
    """Testes para geração de fluxos de cupom"""

    def test_fluxos_cupom_ultimo_inclui_principal(self):
        """Último fluxo deve incluir devolução do principal"""
        fluxos = RFCalcService.calcular_fluxos_cupom(
            valor_nominal=1000.0,
            taxa_cupom=0.10,
            frequencia_anual=1,
            periodos=3
        )
        assert len(fluxos) == 3
        assert fluxos[0] == 100.0
        assert fluxos[1] == 100.0
        assert fluxos[2] == 1100.0  # cupom + principal

    def test_fluxos_cupom_semestral(self):
        """Cupom semestral: taxa dividida por 2"""
        fluxos = RFCalcService.calcular_fluxos_cupom(
            valor_nominal=1000.0,
            taxa_cupom=0.10,
            frequencia_anual=2,
            periodos=4  # 2 anos semestrais = 4 períodos
        )
        assert len(fluxos) == 4
        assert fluxos[0] == 50.0   # 10%/2 * 1000
        assert fluxos[-1] == 1050.0


class TestRFCompleto:
    """Testes para cálculo completo RF"""

    def test_rf_completo_titulo_par(self):
        """Título no par: YTM = cupom, duration consistente"""
        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=1000.0,
            valor_nominal=1000.0,
            taxa_cupom=0.10,
            data_vencimento=date.today() + timedelta(days=3 * 365),
            frequencia_anual=1
        )

        assert abs(resultado['ytm_anual'] - 0.10) < 0.001
        assert resultado['percentual_par'] == 100.0
        assert not resultado['negociando_acima_par']
        assert resultado['premio_desconto'] == 0.0

    def test_rf_completo_titulo_desconto(self):
        """Título com desconto: YTM > cupom, percentual_par < 100"""
        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=950.0,
            valor_nominal=1000.0,
            taxa_cupom=0.10,
            data_vencimento=date.today() + timedelta(days=3 * 365),
        )

        assert resultado['ytm_anual'] > 0.10
        assert resultado['percentual_par'] < 100.0
        assert resultado['premio_desconto'] == -50.0
        assert not resultado['negociando_acima_par']

    def test_rf_completo_titulo_premio(self):
        """Título com prêmio: YTM < cupom, negociando_acima_par=True"""
        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=1050.0,
            valor_nominal=1000.0,
            taxa_cupom=0.10,
            data_vencimento=date.today() + timedelta(days=3 * 365),
        )

        assert resultado['ytm_anual'] < 0.10
        assert resultado['percentual_par'] > 100.0
        assert resultado['negociando_acima_par']

    def test_rf_campos_presentes(self):
        """Verifica que todos os campos esperados estão presentes no resultado"""
        resultado = RFCalcService.calcular_rf_completo(
            preco_mercado=1000.0,
            valor_nominal=1000.0,
            taxa_cupom=0.105,
            data_vencimento=date.today() + timedelta(days=365 * 5),
        )

        campos_esperados = [
            'ytm_anual', 'ytm_anual_pct', 'duration_macaulay_anos',
            'duration_modificada_anos', 'periodos_restantes', 'frequencia_anual',
            'taxa_cupom_anual', 'taxa_cupom_anual_pct', 'cupom_por_periodo',
            'valor_nominal', 'preco_mercado', 'premio_desconto',
            'percentual_par', 'negociando_acima_par'
        ]
        for campo in campos_esperados:
            assert campo in resultado, f'Campo ausente: {campo}'


class TestFIICompleto:
    """Testes para cálculo completo FII/REIT"""

    def test_fii_p_ffo_basico(self):
        """P/FFO = preco / ffo"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=100.0,
            ffo_por_cota=10.0
        )
        assert resultado['p_ffo'] == 10.0

    def test_fii_ffo_yield(self):
        """FFO Yield = ffo / preco * 100"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=100.0,
            ffo_por_cota=8.5
        )
        assert resultado['ffo_yield_pct'] == 8.5

    def test_fii_com_affo(self):
        """Testa cálculo com AFFO"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=100.0,
            ffo_por_cota=10.0,
            affo_por_cota=8.0
        )
        assert 'p_affo' in resultado
        assert resultado['p_affo'] == 12.5
        assert resultado['affo_yield_pct'] == 8.0

    def test_fii_analise_barato(self):
        """P/FFO < 10 deve gerar sinal de potencialmente barato"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=80.0,
            ffo_por_cota=10.0  # P/FFO = 8x
        )
        analise = resultado['analise']
        assert any('abaixo de 10x' in s for s in analise)

    def test_fii_analise_pvp_desconto(self):
        """P/VP < 0.9 deve indicar desconto ao patrimônio"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=80.0,
            ffo_por_cota=10.0,
            p_vp=0.85
        )
        analise = resultado['analise']
        assert any('desconto ao patrimônio' in s for s in analise)

    def test_fii_campos_presentes(self):
        """Verifica campos obrigatórios na resposta"""
        resultado = RFCalcService.calcular_fii_completo(
            preco_atual=100.0,
            ffo_por_cota=10.0
        )
        for campo in ['preco_atual', 'ffo_por_cota', 'p_ffo', 'ffo_yield_pct', 'analise']:
            assert campo in resultado


class TestCalcularPeriodos:
    """Testes para cálculo de períodos"""

    def test_periodos_anuais_3_anos(self):
        """3 anos = 3 períodos anuais"""
        hoje = date.today()
        vencimento = date(hoje.year + 3, hoje.month, hoje.day)
        periodos = RFCalcService.calcular_periodos(hoje, vencimento, frequencia_anual=1)
        assert periodos == 3

    def test_periodos_semestrais_2_anos(self):
        """2 anos semestral = ~4 períodos"""
        hoje = date.today()
        vencimento = date(hoje.year + 2, hoje.month, hoje.day)
        periodos = RFCalcService.calcular_periodos(hoje, vencimento, frequencia_anual=2)
        assert 3 <= periodos <= 5  # tolerância de conversão

    def test_periodos_minimo_um(self):
        """Vencimento no passado deve retornar 1"""
        periodos = RFCalcService.calcular_periodos(
            date.today(), date.today() - timedelta(days=30)
        )
        assert periodos == 1
