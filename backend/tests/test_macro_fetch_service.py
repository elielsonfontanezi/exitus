# -*- coding: utf-8 -*-
"""Testes do macro_fetch_service (mocks — sem chamada real)."""
from unittest.mock import patch

from app.services.macro_fetch_service import clear_macro_cache, fetch_macro_indicators


class TestMacroFetchService:
    def setup_method(self):
        clear_macro_cache()

    @patch('app.services.macro_fetch_service._fetch_ibovespa_12m')
    @patch('app.services.macro_fetch_service._fetch_bcb_series')
    def test_fetch_macro_indicators_agrega_bcb_e_brapi(self, mock_bcb, mock_ibov):
        mock_bcb.side_effect = lambda sid: {
            432: 14.25,
            4391: 14.75,
            13522: 4.72,
        }.get(sid)
        mock_ibov.return_value = 23.0

        result = fetch_macro_indicators()
        assert result is not None
        assert result['selic_anual'] == 14.25
        assert result['cdi_anual'] == 14.75
        assert result['ipca_anual'] == 4.72
        assert result['ibovespa_anual'] == 23.0

    @patch('app.services.macro_fetch_service._fetch_ibovespa_12m', return_value=None)
    @patch('app.services.macro_fetch_service._fetch_bcb_series', return_value=None)
    def test_fetch_macro_indicators_retorna_none_sem_dados(self, _bcb, _ibov):
        assert fetch_macro_indicators() is None
