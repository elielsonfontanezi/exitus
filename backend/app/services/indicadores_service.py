# -*- coding: utf-8 -*-
"""Agregador de indicadores macro para o dashboard."""

import os
from datetime import datetime, timezone

from app.services.parametros_macro_service import ParametrosMacroService


class IndicadoresService:
    """Indicadores de mercado para comparação no dashboard."""

    _DEFAULT_CDI = float(os.getenv('CDI_ANUAL', '11.75'))
    _DEFAULT_IBOV = float(os.getenv('IBOVESPA_ANUAL', '8.32'))

    @staticmethod
    def get_dashboard_indicadores():
        """
        Retorna CDI, Ibovespa, IPCA e SELIC para o painel de benchmark.

        CDI/IPCA/SELIC vêm de parametros_macro (BR/B3).
        Ibovespa usa env var até haver fonte dedicada no banco.
        """
        parametro = ParametrosMacroService.get_by_pais_mercado('BR', 'B3', ativo_only=True)
        params = ParametrosMacroService.get_parametros_dict('BR', 'B3')

        cdi = round(float(params['taxa_livre_risco']) * 100, 2)
        ipca = round(float(params['inflacao_anual']) * 100, 2)
        selic = round(float(params.get('ytm_rf', params['taxa_livre_risco'])) * 100, 2)

        ibov = IndicadoresService._DEFAULT_IBOV
        fonte_ibov = 'env'

        if parametro and parametro.updated_at:
            atualizado_em = parametro.updated_at.isoformat()
            fonte_cdi = 'parametros_macro'
        else:
            atualizado_em = datetime.now(timezone.utc).isoformat()
            fonte_cdi = 'fallback'
            if cdi <= 0:
                cdi = IndicadoresService._DEFAULT_CDI

        return {
            'cdi_anual': cdi,
            'ibovespa_anual': ibov,
            'ipca_anual': ipca,
            'selic_anual': selic,
            'fontes': {
                'cdi': fonte_cdi,
                'ibovespa': fonte_ibov,
                'ipca': fonte_cdi,
                'selic': fonte_cdi,
            },
            'atualizado_em': atualizado_em,
        }
