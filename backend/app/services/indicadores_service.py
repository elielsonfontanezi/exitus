# -*- coding: utf-8 -*-
"""Agregador de indicadores macro para o dashboard."""

import os
from datetime import datetime, timezone

from app.services.macro_fetch_service import fetch_macro_indicators
from app.services.parametros_macro_service import ParametrosMacroService


class IndicadoresService:
    """Indicadores de mercado para comparação no dashboard."""

    _DEFAULT_CDI = float(os.getenv('CDI_ANUAL', '14.75'))
    _DEFAULT_IBOV = float(os.getenv('IBOVESPA_ANUAL', '23.0'))
    _DEFAULT_IPCA = float(os.getenv('IPCA_ANUAL', '4.72'))
    _DEFAULT_SELIC = float(os.getenv('SELIC_ANUAL', '14.25'))

    @staticmethod
    def get_dashboard_indicadores():
        """
        Retorna CDI, Ibovespa, IPCA e SELIC para o painel de benchmark.

        Prioridade: API externa (BCB + brapi) → parametros_macro → env defaults.
        """
        api_data = fetch_macro_indicators()
        parametro = ParametrosMacroService.get_by_pais_mercado('BR', 'B3', ativo_only=True)
        params = ParametrosMacroService.get_parametros_dict('BR', 'B3')

        cdi_db = round(float(params['taxa_livre_risco']) * 100, 2)
        ipca_db = round(float(params['inflacao_anual']) * 100, 2)
        selic_db = round(float(params.get('ytm_rf', params['taxa_livre_risco'])) * 100, 2)

        def _valid_annual(val):
            if val is None:
                return None
            v = float(val)
            return v if 1.0 <= v <= 50.0 else None

        cdi = _valid_annual(api_data.get('cdi_anual')) if api_data else None
        ipca = _valid_annual(api_data.get('ipca_anual')) if api_data else None
        selic = _valid_annual(api_data.get('selic_anual')) if api_data else None
        ibov = api_data.get('ibovespa_anual') if api_data else None

        fonte_cdi = 'api_externa' if cdi is not None else 'parametros_macro'
        fonte_ibov = 'api_externa' if ibov is not None else 'env'
        fonte_ipca = 'api_externa' if ipca is not None else 'parametros_macro'
        fonte_selic = 'api_externa' if selic is not None else 'parametros_macro'

        if cdi is None:
            cdi = cdi_db if cdi_db > 0 else IndicadoresService._DEFAULT_CDI
            fonte_cdi = 'parametros_macro' if cdi_db > 0 else 'fallback'
        if ipca is None:
            ipca = ipca_db if ipca_db > 0 else IndicadoresService._DEFAULT_IPCA
            fonte_ipca = 'parametros_macro' if ipca_db > 0 else 'fallback'
        if selic is None:
            selic = selic_db if selic_db > 0 else IndicadoresService._DEFAULT_SELIC
            fonte_selic = 'parametros_macro' if selic_db > 0 else 'fallback'
        if ibov is None:
            ibov = IndicadoresService._DEFAULT_IBOV

        if parametro and parametro.updated_at:
            atualizado_em = parametro.updated_at.isoformat()
        else:
            atualizado_em = datetime.now(timezone.utc).isoformat()

        return {
            'cdi_anual': round(float(cdi), 2),
            'ibovespa_anual': round(float(ibov), 2),
            'ipca_anual': round(float(ipca), 2),
            'selic_anual': round(float(selic), 2),
            'fontes': {
                'cdi': fonte_cdi,
                'ibovespa': fonte_ibov,
                'ipca': fonte_ipca,
                'selic': fonte_selic,
            },
            'atualizado_em': atualizado_em,
        }
