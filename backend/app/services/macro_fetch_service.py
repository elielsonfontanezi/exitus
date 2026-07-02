# -*- coding: utf-8 -*-
"""Fetch de indicadores macro (BCB SGS + brapi) com cache em memória."""

import logging
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

_CACHE: Dict[str, Any] = {}
_CACHE_TTL_SECONDS = 3600

_BCB_BASE = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs'
_BCB_SERIES = {
    'selic': 432,
    'cdi': 4389,
    'ipca': 13522,
}

_MIN_ANNUAL_RATE = 1.0
_MAX_ANNUAL_RATE = 50.0


def _cache_get(key: str) -> Optional[Dict[str, float]]:
    entry = _CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry['ts'] > _CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return entry['data']


def _cache_set(key: str, data: Dict[str, float]) -> None:
    _CACHE[key] = {'ts': time.time(), 'data': data}


def _is_plausible_annual_rate(value: Optional[float]) -> bool:
    """Rejeita taxas diárias (~0,05) exibidas como anuais."""
    if value is None:
        return False
    return _MIN_ANNUAL_RATE <= float(value) <= _MAX_ANNUAL_RATE


def _fetch_bcb_series(serie_id: int, timeout: int = 8) -> Optional[float]:
    url = f'{_BCB_BASE}.{serie_id}/dados/ultimos/1?formato=json'
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            return None
        return float(str(rows[0]['valor']).replace(',', '.'))
    except Exception as exc:
        logger.warning('BCB série %s falhou: %s', serie_id, exc)
        return None


def _fetch_ibovespa_12m(timeout: int = 10) -> Optional[float]:
    token = os.getenv('BRAPI_TOKEN', os.getenv('BRAPI_API_KEY', ''))
    params = {'range': '1y', 'interval': '1d'}
    if token:
        params['token'] = token
    url = f"https://brapi.dev/api/quote/%5EBVSP?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        results = payload.get('results') or []
        if not results:
            return None
        history = results[0].get('historicalDataPrice') or []
        if len(history) < 2:
            change = results[0].get('regularMarketChangePercent')
            if change is not None:
                return round(float(change), 2)
            return None
        first_close = float(history[0]['close'])
        last_close = float(history[-1]['close'])
        if first_close <= 0:
            return None
        return round(((last_close - first_close) / first_close) * 100, 2)
    except Exception as exc:
        logger.warning('brapi Ibovespa falhou: %s', exc)
        return None


def fetch_macro_indicators() -> Optional[Dict[str, float]]:
    """
    Busca CDI, SELIC, IPCA (12m) e Ibovespa (12m) em APIs externas.
    Retorna None se nenhum indicador foi obtido.
    """
    cached = _cache_get('macro_dashboard')
    if cached:
        return cached

    selic_raw = _fetch_bcb_series(_BCB_SERIES['selic'])
    cdi_raw = _fetch_bcb_series(_BCB_SERIES['cdi'])
    ipca_raw = _fetch_bcb_series(_BCB_SERIES['ipca'])
    ibov = _fetch_ibovespa_12m()

    selic = selic_raw if _is_plausible_annual_rate(selic_raw) else None
    cdi = cdi_raw if _is_plausible_annual_rate(cdi_raw) else None
    ipca = ipca_raw if _is_plausible_annual_rate(ipca_raw) else None

    partial = {
        k: v for k, v in {
            'selic_anual': selic,
            'cdi_anual': cdi,
            'ipca_anual': ipca,
            'ibovespa_anual': ibov,
        }.items() if v is not None
    }
    if not partial:
        return None

    _cache_set('macro_dashboard', partial)
    return partial


def clear_macro_cache() -> None:
    """Limpa cache (útil em testes)."""
    _CACHE.clear()
