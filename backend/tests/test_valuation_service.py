# -*- coding: utf-8 -*-
"""
Testes unitários para valuation_service.py — BUG-VAL-005

Cobertura:
- remover_outliers_iqr: IQR com 4 valores, edge-cases (≤2, tudo igual, nenhum removido)
- classificar_perfil_valuation: fii, growth, bancos, value, dividendos, padrao
- calcular_valor_justo: ações (ITUB4-like), FII só cap_rate, FII com FFO+AFFO, fallback
- Garantias retrocompatíveis: pt_medio == valor_justo; campos faixa_min/faixa_max presentes
- preco_teto_usuario NÃO entra no cálculo
"""
import pytest
from decimal import Decimal
from unittest.mock import patch

from app.services.valuation_service import (
    remover_outliers_iqr,
    classificar_perfil_valuation,
    calcular_valor_justo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class AtivoFake:
    """Objeto simples para simular um Ativo do banco sem dependência de DB."""
    def __init__(self, **kwargs):
        defaults = {
            'ticker': 'TEST3',
            'tipo': _TipoFake('acao'),
            'mercado': 'BR',
            'moeda': 'BRL',
            'preco_atual': Decimal('42.24'),
            'dividend_yield': Decimal('0.065'),
            'eps': Decimal('4.17'),
            'fcf': Decimal('5.50'),
            'p_l': Decimal('10.0'),
            'p_vp': None,
            'ffo_por_cota': None,
            'affo_por_cota': None,
            'preco_teto_usuario': Decimal('38.00'),  # campo estático do usuário — NÃO deve influenciar
        }
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


class _TipoFake:
    """Simula TipoAtivo Enum."""
    def __init__(self, value):
        self.value = value

    def lower(self):
        return self.value.lower()


# Parâmetros macro padrão BR (fallback hardcoded)
_PARAMS_BR = {
    'taxa_livre_risco': 0.105,
    'crescimento_medio': 0.05,
    'custo_capital': 0.12,
    'cap_rate_fii': 0.08,
    'inflacao_anual': 0.045,
    'ytm_rf': 0.105,
}


# ---------------------------------------------------------------------------
# remover_outliers_iqr
# ---------------------------------------------------------------------------

class TestRemoverOutliersIqr:
    def test_remove_outlier_alto(self):
        """Graham R$1938 deve ser removido quando os outros são ~R$46-58."""
        valores = {'bazin': 46.0, 'gordon': 48.0, 'graham': 1938.0, 'dcf': 58.0}
        resultado = remover_outliers_iqr(valores)
        assert 'graham' not in resultado
        assert 'bazin' in resultado and 'gordon' in resultado and 'dcf' in resultado

    def test_nao_remove_valores_coesos(self):
        """Valores próximos não devem ser removidos."""
        valores = {'bazin': 44.0, 'gordon': 46.0, 'graham': 48.0, 'dcf': 50.0}
        resultado = remover_outliers_iqr(valores)
        assert resultado == valores

    def test_dois_valores_sem_iqr(self):
        """Com ≤2 valores, retorna tudo sem aplicar IQR."""
        valores = {'cap_rate': 140.0, 'ffo_cap_rate': 120.0}
        resultado = remover_outliers_iqr(valores)
        assert resultado == valores

    def test_um_valor_sem_iqr(self):
        valores = {'cap_rate': 140.0}
        resultado = remover_outliers_iqr(valores)
        assert resultado == valores

    def test_nunca_retorna_vazio(self):
        """Mesmo com IQR=0 (todos iguais), não retorna dict vazio."""
        valores = {'a': 10.0, 'b': 10.0, 'c': 10.0}
        resultado = remover_outliers_iqr(valores)
        assert len(resultado) > 0

    def test_remove_outlier_baixo(self):
        """Outlier baixo (ex: Graham sem EPS → pt=0 filtrado antes) não deve passar."""
        valores = {'bazin': 46.0, 'gordon': 48.0, 'dcf': 52.0, 'graham': 5.0}
        resultado = remover_outliers_iqr(valores)
        assert 'graham' not in resultado


# ---------------------------------------------------------------------------
# classificar_perfil_valuation
# ---------------------------------------------------------------------------

class TestClassificarPerfil:
    def test_fii(self):
        ativo = AtivoFake(tipo=_TipoFake('fii'), ticker='HGLG11')
        assert classificar_perfil_valuation(ativo) == 'fii'

    def test_reit(self):
        ativo = AtivoFake(tipo=_TipoFake('reit'), ticker='O', mercado='US')
        assert classificar_perfil_valuation(ativo) == 'fii'

    def test_stock_us_growth(self):
        ativo = AtivoFake(tipo=_TipoFake('stock'), mercado='US', ticker='AAPL')
        assert classificar_perfil_valuation(ativo) == 'growth'

    def test_banco_br(self):
        ativo = AtivoFake(tipo=_TipoFake('acao'), ticker='ITUB4', mercado='BR')
        assert classificar_perfil_valuation(ativo) == 'bancos'

    def test_banco_br_bbdc(self):
        ativo = AtivoFake(tipo=_TipoFake('acao'), ticker='BBDC4', mercado='BR')
        assert classificar_perfil_valuation(ativo) == 'bancos'

    def test_value_pl_baixo(self):
        ativo = AtivoFake(tipo=_TipoFake('acao'), ticker='VALE3', p_l=Decimal('6.5'))
        assert classificar_perfil_valuation(ativo) == 'value'

    def test_dividendos_default(self):
        ativo = AtivoFake(tipo=_TipoFake('acao'), ticker='PETR4', p_l=Decimal('12.0'))
        assert classificar_perfil_valuation(ativo) == 'dividendos'

    def test_padrao_tipo_desconhecido(self):
        ativo = AtivoFake(tipo=_TipoFake('cripto'), ticker='BTC')
        assert classificar_perfil_valuation(ativo) == 'padrao'

    def test_unit_como_acao(self):
        ativo = AtivoFake(tipo=_TipoFake('unit'), ticker='KLBN11', mercado='BR')
        # Unit não é banco nem low P/L → dividendos
        assert classificar_perfil_valuation(ativo) in ('dividendos', 'value')


# ---------------------------------------------------------------------------
# calcular_valor_justo — Ações
# ---------------------------------------------------------------------------

class TestCalcularValorJustoAcoes:

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_itub4_like_retorno_estrutura(self, mock_params):
        """ITUB4-like: estrutura completa de retorno."""
        ativo = AtivoFake(
            ticker='ITUB4',
            tipo=_TipoFake('acao'),
            preco_atual=Decimal('42.24'),
            dividend_yield=Decimal('0.065'),
            eps=Decimal('4.17'),
            fcf=Decimal('5.50'),
            p_l=Decimal('10.5'),
        )
        result = calcular_valor_justo(ativo)

        # Retrocompatibilidade: pt_medio == valor_justo
        assert result['pt_medio'] == result['valor_justo']

        # Campos obrigatórios
        for campo in ('valor_justo', 'pt_medio', 'faixa_min', 'faixa_max',
                      'margem_seguranca', 'sinal', 'perfil', 'metodos',
                      'metodos_agregados', 'outliers_removidos', 'parametros_regiao'):
            assert campo in result, f"Campo ausente: {campo}"

        # Faixa coerente
        assert result['faixa_min'] <= result['valor_justo'] <= result['faixa_max']

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_itub4_like_valor_razoavel(self, mock_params):
        """
        ITUB4 após BUG-VAL-001: Bazin~46, Graham~32, Gordon~48, DCF~58.
        IQR não deve remover nenhum (coesos).
        valor_justo esperado: ~46-47 (não R$499 da média antiga).
        """
        ativo = AtivoFake(
            ticker='ITUB4',
            tipo=_TipoFake('acao'),
            preco_atual=Decimal('42.24'),
            dividend_yield=Decimal('0.065'),
            eps=Decimal('4.17'),
            fcf=Decimal('5.50'),
            p_l=Decimal('10.5'),
        )
        result = calcular_valor_justo(ativo)
        vj = result['valor_justo']

        # Valor justo deve ser realista (não inflado por média simples com EPS errado)
        assert 30 <= vj <= 100, f"valor_justo={vj} fora do intervalo esperado [30, 100]"
        # Perfil: p_l=10.5 → dividendos (não bancos pois ITUB4[:4]='ITUB' → bancos)
        assert result['perfil'] == 'bancos'

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_outlier_graham_alto_removido(self, mock_params):
        """
        Com EPS muito alto, Graham gera outlier que deve ser removido pelo IQR.
        """
        ativo = AtivoFake(
            ticker='TEST3',
            tipo=_TipoFake('acao'),
            preco_atual=Decimal('42.00'),
            dividend_yield=Decimal('0.065'),
            eps=Decimal('50.00'),   # EPS irreal → Graham ~4500
            fcf=Decimal('5.50'),
            p_l=Decimal('10.5'),
        )
        result = calcular_valor_justo(ativo)
        assert 'graham' in result['outliers_removidos'], (
            f"Graham deveria ser outlier, outliers_removidos={result['outliers_removidos']}"
        )
        # valor_justo não pode ser inflado pelo outlier
        assert result['valor_justo'] < 500

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_preco_teto_usuario_nao_influencia(self, mock_params):
        """
        preco_teto_usuario (campo estático do usuário) NÃO deve alterar valor_justo.
        Dois ativos idênticos com preco_teto_usuario diferentes → mesmo valor_justo.
        """
        base = dict(
            ticker='TEST3', tipo=_TipoFake('acao'),
            preco_atual=Decimal('42.24'), dividend_yield=Decimal('0.065'),
            eps=Decimal('4.17'), fcf=Decimal('5.50'), p_l=Decimal('10.5'),
        )
        a1 = AtivoFake(**base, preco_teto_usuario=Decimal('38.00'))
        a2 = AtivoFake(**base, preco_teto_usuario=Decimal('200.00'))
        r1 = calcular_valor_justo(a1)
        r2 = calcular_valor_justo(a2)
        assert r1['valor_justo'] == r2['valor_justo']

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_metodo_agregacao_informado(self, mock_params):
        ativo = AtivoFake()
        result = calcular_valor_justo(ativo)
        assert result['metodo_agregacao'] == 'mediana_ponderada'


# ---------------------------------------------------------------------------
# calcular_valor_justo — FIIs
# ---------------------------------------------------------------------------

class TestCalcularValorJustoFii:

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_fii_apenas_cap_rate(self, mock_params):
        """
        FII sem ffo/affo: apenas cap_rate.
        HGLG11-like: preco=152.30, dy=8.2%, cap=8% → pt=(0.082×152.30)/0.08=156.11
        """
        ativo = AtivoFake(
            ticker='HGLG11',
            tipo=_TipoFake('fii'),
            preco_atual=Decimal('152.30'),
            dividend_yield=Decimal('0.082'),
            ffo_por_cota=None,
            affo_por_cota=None,
        )
        result = calcular_valor_justo(ativo)
        assert result['perfil'] == 'fii'
        assert 'cap_rate' in result['metodos']
        assert 'ffo_cap_rate' not in result['metodos']
        assert 'affo_cap_rate' not in result['metodos']
        # pt = (0.082 × 152.30) / 0.08 ≈ 156.11
        assert abs(result['valor_justo'] - 156.11) < 1.0
        assert result['pt_medio'] == result['valor_justo']

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_fii_com_ffo(self, mock_params):
        """
        FII com ffo_por_cota: dois métodos (cap_rate + ffo_cap_rate).
        ffo=12.00, cap=8% → pt_ffo=150.00
        """
        ativo = AtivoFake(
            ticker='HGLG11',
            tipo=_TipoFake('fii'),
            preco_atual=Decimal('152.30'),
            dividend_yield=Decimal('0.082'),
            ffo_por_cota=Decimal('12.00'),
            affo_por_cota=None,
        )
        result = calcular_valor_justo(ativo)
        assert 'cap_rate' in result['metodos']
        assert 'ffo_cap_rate' in result['metodos']
        assert abs(result['metodos']['ffo_cap_rate']['pt'] - 150.00) < 0.05

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_fii_com_ffo_e_affo(self, mock_params):
        """
        FII com todos os três métodos.
        affo=11.00, cap=8% → pt_affo=137.50
        """
        ativo = AtivoFake(
            ticker='HGLG11',
            tipo=_TipoFake('fii'),
            preco_atual=Decimal('152.30'),
            dividend_yield=Decimal('0.082'),
            ffo_por_cota=Decimal('12.00'),
            affo_por_cota=Decimal('11.00'),
        )
        result = calcular_valor_justo(ativo)
        assert 'affo_cap_rate' in result['metodos']
        assert abs(result['metodos']['affo_cap_rate']['pt'] - 137.50) < 0.05
        # 3 métodos → IQR pulado (≤2 testa, mas 3 valores próximos não remove nada)
        assert len(result['metodos']) == 3

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_fii_pesos_normalizados_sem_ffo(self, mock_params):
        """Sem ffo/affo, cap_rate recebe peso 1.0 (100%)."""
        ativo = AtivoFake(
            ticker='HGLG11', tipo=_TipoFake('fii'),
            preco_atual=Decimal('152.30'), dividend_yield=Decimal('0.082'),
            ffo_por_cota=None, affo_por_cota=None,
        )
        result = calcular_valor_justo(ativo)
        if result['metodos_agregados']:
            peso_cap = result['metodos_agregados'].get('cap_rate', {}).get('peso', 0)
            assert abs(peso_cap - 1.0) < 0.001

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_fii_faixa_min_max(self, mock_params):
        """Faixa min/max coerente com os métodos calculados."""
        ativo = AtivoFake(
            ticker='HGLG11', tipo=_TipoFake('fii'),
            preco_atual=Decimal('152.30'), dividend_yield=Decimal('0.082'),
            ffo_por_cota=Decimal('12.00'), affo_por_cota=Decimal('11.00'),
        )
        result = calcular_valor_justo(ativo)
        assert result['faixa_min'] <= result['valor_justo'] <= result['faixa_max']
        assert result['faixa_min'] > 0


# ---------------------------------------------------------------------------
# calcular_valor_justo — Fallback
# ---------------------------------------------------------------------------

class TestCalcularValorJustoFallback:

    @patch('app.services.valuation_service.get_parametros_macro', return_value=_PARAMS_BR)
    def test_tipo_desconhecido_fallback(self, mock_params):
        """Tipo desconhecido usa fallback +10% do preço atual."""
        ativo = AtivoFake(
            tipo=_TipoFake('cripto'),
            preco_atual=Decimal('100.00'),
        )
        result = calcular_valor_justo(ativo)
        assert result['valor_justo'] == 110.0
        assert result['perfil'] == 'padrao'
