"""M7.5 - Cotações Multi-Provider com Fallback Otimizado"""
import requests
import logging
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List
import pandas as pd
import yfinance as yf
from app.utils.circuit_breaker import get_circuit_breaker, with_retry


load_dotenv()
logger = logging.getLogger(__name__)

class CotacoesService:
    """Fallback cascata com 8 providers"""

    # Tokens do .env
    BRAPI_TOKEN = os.getenv('BRAPI_API_KEY', '')
    ALPHA_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    FINNHUB_KEY = os.getenv('FINNHUB_API_KEY', '')
    TWELVE_KEY = os.getenv('TWELVE_DATA_API_KEY', '')
    MARKETSTACK_KEY = os.getenv('MARKETSTACK_API_KEY', '')
    HGFINANCE_KEY = os.getenv('HGFINANCE_API_KEY', '')
    TIMEOUT = 5

    @staticmethod
    def _build_brapi_url(ticker):
        """Constrói URL brapi.dev com token"""
        base_url = f"https://brapi.dev/api/quote/{ticker}"
        if CotacoesService.BRAPI_TOKEN:
            return f"{base_url}?token={CotacoesService.BRAPI_TOKEN}"
        return base_url

    @staticmethod
    def obter_cotacao(ticker, mercado='BR'):
        """Fallback otimizado por mercado"""
        
        # ============================================
        # ATIVOS BRASIL (B3)
        # ============================================
        if mercado == 'BR':
            
            # 1️⃣ BRAPI.DEV (PRINCIPAL BR - mais rápido)
            _cb_brapi = get_circuit_breaker('brapi.dev', failure_threshold=3, recovery_timeout=60)
            if _cb_brapi.call_allowed():
                try:
                    logger.info(f"📡 [1/4 BR] brapi.dev para {ticker}")
                    url = CotacoesService._build_brapi_url(ticker)
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                    if resp.status_code == 200:
                        data = resp.json()['results'][0]
                        _cb_brapi.record_success()
                        logger.info(f"✅ brapi.dev OK: {ticker}")
                        return {
                            'ticker': ticker,
                            'preco_atual': float(data['regularMarketPrice']),
                            'variacao_percentual': float(data['regularMarketChangePercent']),
                            'volume': int(data['regularMarketVolume']),
                            'dy_12m': round(float(data.get('dividendYield', 0)) * 100, 2),
                            'pl': round(float(data.get('trailingPE', 0)), 2),
                            'provider': 'brapi.dev',
                            'success': True
                        }
                    else:
                        _cb_brapi.record_failure()
                except Exception as e:
                    _cb_brapi.record_failure()
                    logger.warning(f"⚠️ brapi.dev falhou: {e}")
            else:
                logger.info(f"⚡ [1/4 BR] brapi.dev OPEN — pulando para próximo provider")

            # 2️⃣ HG FINANCE (BR específico)
            if CotacoesService.HGFINANCE_KEY:
                _cb_hg = get_circuit_breaker('hgfinance', failure_threshold=3, recovery_timeout=60)
                if _cb_hg.call_allowed():
                    try:
                        logger.info(f"📡 [2/4 BR] hgfinance para {ticker}")
                        url = f"https://api.hgbrasil.com/finance/stock_price?key={CotacoesService.HGFINANCE_KEY}&symbol={ticker}"
                        resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                        
                        if resp.status_code == 200:
                            data = resp.json()['results'][ticker]
                            _cb_hg.record_success()
                            logger.info(f"✅ hgfinance OK: {ticker}")
                            return {
                                'ticker': ticker,
                                'preco_atual': float(data['price']),
                                'variacao_percentual': float(data['change_percent']),
                                'volume': 0,
                                'dy_12m': 0,
                                'pl': 0,
                                'provider': 'hgfinance',
                                'success': True
                            }
                        else:
                            _cb_hg.record_failure()
                    except Exception as e:
                        _cb_hg.record_failure()
                        logger.warning(f"⚠️ hgfinance falhou: {e}")
                else:
                    logger.info(f"⚡ [2/4 BR] hgfinance OPEN — pulando")

            # 3️⃣ YFINANCE (BR com .SA)
            _cb_yf_br = get_circuit_breaker('yfinance.BR', failure_threshold=3, recovery_timeout=120)
            if _cb_yf_br.call_allowed():
                try:
                    logger.info(f"📡 [3/4 BR] yfinance para {ticker}")
                    from requests.exceptions import Timeout
                    
                    stock = yf.Ticker(f'{ticker}.SA')
                    hist = stock.history(period='1d', timeout=CotacoesService.TIMEOUT)
                    
                    if not hist.empty:
                        _cb_yf_br.record_success()
                        logger.info(f"✅ yfinance OK: {ticker}")
                        return {
                            'ticker': ticker,
                            'preco_atual': float(hist['Close'].iloc[-1]),
                            'variacao_percentual': 0,
                            'volume': int(hist['Volume'].iloc[-1]),
                            'dy_12m': 0,
                            'pl': 0,
                            'provider': 'yfinance',
                            'success': True
                        }
                    else:
                        _cb_yf_br.record_failure()
                except Exception as e:
                    _cb_yf_br.record_failure()
                    logger.warning(f"⚠️ yfinance falhou: {e}")
            else:
                logger.info(f"⚡ [3/4 BR] yfinance.BR OPEN — pulando")

            # 4️⃣ TWELVE DATA (Global backup)
            if CotacoesService.TWELVE_KEY:
                _cb_twelve = get_circuit_breaker('twelvedata', failure_threshold=3, recovery_timeout=60)
                if _cb_twelve.call_allowed():
                    try:
                        logger.info(f"📡 [4/4 BR] twelvedata para {ticker}")
                        url = f"https://api.twelvedata.com/price?symbol={ticker}.SA&apikey={CotacoesService.TWELVE_KEY}"
                        resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            if 'price' in data:
                                _cb_twelve.record_success()
                                logger.info(f"✅ twelvedata OK: {ticker}")
                                return {
                                    'ticker': ticker,
                                    'preco_atual': float(data['price']),
                                    'variacao_percentual': 0,
                                    'volume': 0,
                                    'dy_12m': 0,
                                    'pl': 0,
                                    'provider': 'twelvedata',
                                    'success': True
                                }
                            else:
                                _cb_twelve.record_failure()
                        else:
                            _cb_twelve.record_failure()
                    except Exception as e:
                        _cb_twelve.record_failure()
                        logger.warning(f"⚠️ twelvedata falhou: {e}")
                else:
                    logger.info(f"⚡ [4/4 BR] twelvedata OPEN — pulando")

        # ============================================
        # ATIVOS US/GLOBAL
        # ============================================
        else:
            
            # 1️⃣ FINNHUB (PRINCIPAL US - 60 req/min)
            if CotacoesService.FINNHUB_KEY:
                _cb_finnhub = get_circuit_breaker('finnhub', failure_threshold=3, recovery_timeout=60)
                if _cb_finnhub.call_allowed():
                    try:
                        logger.info(f"📡 [1/4 US] finnhub para {ticker}")
                        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={CotacoesService.FINNHUB_KEY}"
                        resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get('c'):  # current price
                                _cb_finnhub.record_success()
                                logger.info(f"✅ finnhub OK: {ticker} = ${data['c']}")
                                return {
                                    'ticker': ticker,
                                    'preco_atual': float(data['c']),
                                    'variacao_percentual': float(data.get('dp', 0)),
                                    'volume': 0,
                                    'dy_12m': 0,
                                    'pl': 0,
                                    'provider': 'finnhub',
                                    'success': True
                                }
                            else:
                                _cb_finnhub.record_failure()
                        else:
                            _cb_finnhub.record_failure()
                    except Exception as e:
                        _cb_finnhub.record_failure()
                        logger.warning(f"⚠️ finnhub falhou: {e}")
                else:
                    logger.info(f"⚡ [1/4 US] finnhub OPEN — pulando")

            # 2️⃣ ALPHA VANTAGE (Confiável US)
            _cb_alpha = get_circuit_breaker('alphavantage', failure_threshold=3, recovery_timeout=60)
            if _cb_alpha.call_allowed():
                try:
                    logger.info(f"📡 [2/4 US] alphavantage para {ticker}")
                    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={CotacoesService.ALPHA_KEY}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                    if resp.status_code == 200:
                        data = resp.json().get('Global Quote', {})
                        if data and '05. price' in data:
                            _cb_alpha.record_success()
                            logger.info(f"✅ alphavantage OK: {ticker}")
                            return {
                                'ticker': ticker,
                                'preco_atual': float(data['05. price']),
                                'variacao_percentual': float(data.get('10. change percent', '0').replace('%', '')),
                                'volume': int(data.get('06. volume', 0)),
                                'dy_12m': 0,
                                'pl': 0,
                                'provider': 'alphavantage',
                                'success': True
                            }
                        else:
                            _cb_alpha.record_failure()
                    else:
                        _cb_alpha.record_failure()
                except Exception as e:
                    _cb_alpha.record_failure()
                    logger.warning(f"⚠️ alphavantage falhou: {e}")
            else:
                logger.info(f"⚡ [2/4 US] alphavantage OPEN — pulando")

            # 3️⃣ TWELVE DATA (Global)
            _cb_twelve_us = get_circuit_breaker('twelvedata', failure_threshold=3, recovery_timeout=60)
            if CotacoesService.TWELVE_KEY and _cb_twelve_us.call_allowed():
                try:
                    logger.info(f"📡 [3/4 US] twelvedata para {ticker}")
                    url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={CotacoesService.TWELVE_KEY}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'price' in data:
                            _cb_twelve_us.record_success()
                            logger.info(f"✅ twelvedata OK: {ticker}")
                            return {
                                'ticker': ticker,
                                'preco_atual': float(data['price']),
                                'variacao_percentual': 0,
                                'volume': 0,
                                'dy_12m': 0,
                                'pl': 0,
                                'provider': 'twelvedata',
                                'success': True
                            }
                        else:
                            _cb_twelve_us.record_failure()
                    else:
                        _cb_twelve_us.record_failure()
                except Exception as e:
                    _cb_twelve_us.record_failure()
                    logger.warning(f"⚠️ twelvedata falhou: {e}")
            elif CotacoesService.TWELVE_KEY:
                logger.info(f"⚡ [3/4 US] twelvedata OPEN — pulando")

            # 4️⃣ YFINANCE (Último recurso)
            _cb_yf_us = get_circuit_breaker('yfinance.US', failure_threshold=3, recovery_timeout=120)
            if _cb_yf_us.call_allowed():
                try:
                    logger.info(f"📡 [4/4 US] yfinance para {ticker}")
                    from requests.exceptions import Timeout
                    
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='1d', timeout=CotacoesService.TIMEOUT)
                    
                    if not hist.empty:
                        _cb_yf_us.record_success()
                        logger.info(f"✅ yfinance OK: {ticker}")
                        return {
                            'ticker': ticker,
                            'preco_atual': float(hist['Close'].iloc[-1]),
                            'variacao_percentual': 0,
                            'volume': int(hist['Volume'].iloc[-1]),
                            'dy_12m': 0,
                            'pl': 0,
                            'provider': 'yfinance',
                            'success': True
                        }
                    else:
                        _cb_yf_us.record_failure()
                except Exception as e:
                    _cb_yf_us.record_failure()
                    logger.warning(f"⚠️ yfinance falhou: {e}")
            else:
                logger.info(f"⚡ [4/4 US] yfinance.US OPEN — pulando")

        # ❌ TODAS FALHARAM
        logger.error(f"❌ Todos os providers falharam para {ticker} (alguns podem estar com circuito OPEN)")
        return {'success': False, 'error': 'Todas APIs indisponíveis', 'ticker': ticker}

    # @staticmethod
    # def buscar_historico(ticker: str, data_inicio: date, data_fim: date) -> List[dict]:
    @staticmethod
    def buscar_historico(ticker: str, data_inicio: date, data_fim: date, mercado: str = 'BR') -> List[dict]:        
        """Busca histórico com fallback multi-provider (EXITUS-CIRCUITBREAKER-001)."""

        logger.info(
            "Buscando histórico multi-provider: %s (%s a %s, mercado=%s)",
            ticker,
            data_inicio,
            data_fim,
            mercado
        )

        provedores = (
            CotacoesService._cadeia_historico_br
            if mercado == 'BR'
            else CotacoesService._cadeia_historico_us
        )

        for fetcher in provedores(ticker, data_inicio, data_fim):
            registros = fetcher()
            if registros:
                logger.info(
                    "✅ Histórico obtido via %s: %s registros",
                    fetcher.__name__,
                    len(registros)
                )
                return registros

        logger.error("❌ Nenhum provider retornou histórico para %s", ticker)
        return []

    # ------------------------------------------------------------------
    # Helpers de histórico
    # ------------------------------------------------------------------

    @staticmethod
    def _filtrar_intervalo(registros: List[dict], data_inicio: date, data_fim: date) -> List[dict]:
        return [r for r in registros if data_inicio <= r['data'] <= data_fim]

    @staticmethod
    def _cadeia_historico_br(ticker: str, data_inicio: date, data_fim: date):
        yield lambda: CotacoesService._historico_brapi(ticker, data_inicio, data_fim)
        yield lambda: CotacoesService._historico_twelvedata(f"{ticker}.SA", data_inicio, data_fim)
        yield lambda: CotacoesService._historico_alphavantage(f"{ticker}.SA", data_inicio, data_fim)
        yield lambda: CotacoesService._historico_yfinance(ticker, data_inicio, data_fim, sufixo_br=True)

    @staticmethod
    def _cadeia_historico_us(ticker: str, data_inicio: date, data_fim: date):
        yield lambda: CotacoesService._historico_alphavantage(ticker, data_inicio, data_fim)
        yield lambda: CotacoesService._historico_twelvedata(ticker, data_inicio, data_fim)
        yield lambda: CotacoesService._historico_finnhub(ticker, data_inicio, data_fim)
        yield lambda: CotacoesService._historico_yfinance(ticker, data_inicio, data_fim)

    @staticmethod
    def _historico_brapi(ticker: str, data_inicio: date, data_fim: date) -> List[dict]:
        cb = get_circuit_breaker('brapi.dev', failure_threshold=3, recovery_timeout=60)
        if not cb.call_allowed():
            logger.info("⚡ brapi.dev historico OPEN — pulando")
            return []

        try:
            interval = "?interval=1d&range=1y"
            url = f"https://brapi.dev/api/quote/{ticker}{interval}"
            if CotacoesService.BRAPI_TOKEN:
                url = f"{url}&token={CotacoesService.BRAPI_TOKEN}"

            resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            historico = data['results'][0].get('historicalDataPrice', [])

            registros = []
            for row in historico:
                data_row = datetime.fromtimestamp(row['date']).date()
                registros.append({
                    'data': data_row,
                    'abertura': Decimal(str(row.get('open'))) if row.get('open') is not None else None,
                    'fechamento': Decimal(str(row.get('close'))) if row.get('close') is not None else None,
                    'minimo': Decimal(str(row.get('low'))) if row.get('low') is not None else None,
                    'maximo': Decimal(str(row.get('high'))) if row.get('high') is not None else None,
                    'volume': row.get('volume')
                })

            cb.record_success()
            return CotacoesService._filtrar_intervalo(registros, data_inicio, data_fim)

        except Exception as e:
            cb.record_failure()
            logger.warning("⚠️ brapi.dev historico falhou: %s", e)
            return []

    @staticmethod
    def _historico_twelvedata(symbol: str, data_inicio: date, data_fim: date) -> List[dict]:
        if not CotacoesService.TWELVE_KEY:
            return []

        cb = get_circuit_breaker('twelvedata', failure_threshold=3, recovery_timeout=60)
        if not cb.call_allowed():
            logger.info("⚡ twelvedata historico OPEN — pulando")
            return []

        try:
            url = (
                "https://api.twelvedata.com/time_series"
                f"?symbol={symbol}&interval=1day&start_date={data_inicio}&end_date={data_fim}"
                f"&apikey={CotacoesService.TWELVE_KEY}"
            )
            resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()

            if 'values' not in payload:
                raise ValueError(payload.get('message', 'sem dados de histórico'))

            registros = []
            for row in payload['values']:
                data_row = datetime.strptime(row['datetime'], '%Y-%m-%d').date()
                registros.append({
                    'data': data_row,
                    'abertura': Decimal(row['open']),
                    'fechamento': Decimal(row['close']),
                    'minimo': Decimal(row['low']),
                    'maximo': Decimal(row['high']),
                    'volume': int(float(row.get('volume') or 0)) or None
                })

            cb.record_success()
            return CotacoesService._filtrar_intervalo(registros, data_inicio, data_fim)

        except Exception as e:
            cb.record_failure()
            logger.warning("⚠️ twelvedata historico falhou: %s", e)
            return []

    @staticmethod
    def _historico_alphavantage(symbol: str, data_inicio: date, data_fim: date) -> List[dict]:
        cb = get_circuit_breaker('alphavantage', failure_threshold=3, recovery_timeout=60)
        if not cb.call_allowed():
            logger.info("⚡ alphavantage historico OPEN — pulando")
            return []

        try:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={CotacoesService.ALPHA_KEY}"
            )
            resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            series = payload.get('Time Series (Daily)', {})

            if not series:
                raise ValueError(payload.get('Note') or 'limite atingido ou sem dados')

            registros = []
            for data_str, valores in series.items():
                data_row = datetime.strptime(data_str, '%Y-%m-%d').date()
                registros.append({
                    'data': data_row,
                    'abertura': Decimal(valores['1. open']),
                    'fechamento': Decimal(valores['4. close']),
                    'minimo': Decimal(valores['3. low']),
                    'maximo': Decimal(valores['2. high']),
                    'volume': int(valores['6. volume']) if valores.get('6. volume') else None
                })

            cb.record_success()
            return CotacoesService._filtrar_intervalo(registros, data_inicio, data_fim)

        except Exception as e:
            cb.record_failure()
            logger.warning("⚠️ alphavantage historico falhou: %s", e)
            return []

    @staticmethod
    def _historico_finnhub(ticker: str, data_inicio: date, data_fim: date) -> List[dict]:
        if not CotacoesService.FINNHUB_KEY:
            return []

        cb = get_circuit_breaker('finnhub', failure_threshold=3, recovery_timeout=60)
        if not cb.call_allowed():
            logger.info("⚡ finnhub historico OPEN — pulando")
            return []

        try:
            unix_from = int(datetime.combine(data_inicio, datetime.min.time()).timestamp())
            unix_to = int(datetime.combine(data_fim, datetime.max.time()).timestamp())
            url = (
                "https://finnhub.io/api/v1/stock/candle"
                f"?symbol={ticker}&resolution=D&from={unix_from}&to={unix_to}&token={CotacoesService.FINNHUB_KEY}"
            )
            resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()

            if payload.get('s') != 'ok':
                raise ValueError(payload.get('s'))

            registros = []
            for ts, o, h, l, c, v in zip(
                payload['t'], payload['o'], payload['h'], payload['l'], payload['c'], payload['v']
            ):
                data_row = datetime.fromtimestamp(ts).date()
                registros.append({
                    'data': data_row,
                    'abertura': Decimal(str(o)),
                    'fechamento': Decimal(str(c)),
                    'minimo': Decimal(str(l)),
                    'maximo': Decimal(str(h)),
                    'volume': int(v)
                })

            cb.record_success()
            return CotacoesService._filtrar_intervalo(registros, data_inicio, data_fim)

        except Exception as e:
            cb.record_failure()
            logger.warning("⚠️ finnhub historico falhou: %s", e)
            return []

    @staticmethod
    def _historico_yfinance(ticker: str, data_inicio: date, data_fim: date, sufixo_br: bool = False) -> List[dict]:
        cb = get_circuit_breaker(
            'yfinance.BR' if sufixo_br else 'yfinance.US',
            failure_threshold=3,
            recovery_timeout=120
        )
        if not cb.call_allowed():
            logger.info("⚡ yfinance historico OPEN — pulando")
            return []

        try:
            import yfinance as yf
            from datetime import timedelta

            yahoo_ticker = f"{ticker}.SA" if sufixo_br and '.' not in ticker and '^' not in ticker else ticker
            data_fim_ajustada = data_fim + timedelta(days=1)

            stock = yf.Ticker(yahoo_ticker)
            hist = stock.history(
                start=data_inicio.strftime('%Y-%m-%d'),
                end=data_fim_ajustada.strftime('%Y-%m-%d')
            )

            if hist.empty:
                raise ValueError('yfinance retornou dataframe vazio')

            registros = []
            for data_index, row in hist.iterrows():
                registros.append({
                    'data': data_index.date(),
                    'abertura': Decimal(str(row['Open'])) if not pd.isna(row['Open']) else None,
                    'fechamento': Decimal(str(row['Close'])),
                    'minimo': Decimal(str(row['Low'])) if not pd.isna(row['Low']) else None,
                    'maximo': Decimal(str(row['High'])) if not pd.isna(row['High']) else None,
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else None
                })

            cb.record_success()
            return registros

        except Exception as e:
            cb.record_failure()
            logger.warning("⚠️ yfinance historico falhou: %s", e)
            return []
