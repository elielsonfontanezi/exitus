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
        """
        Busca histórico de preços de um ticker entre duas datas.
        
        Args:
            ticker: Símbolo do ativo (ex: 'PETR4')
            data_inicio: Data inicial do histórico
            data_fim: Data final do histórico
            
        Returns:
            Lista de dicts com formato:
            [
                {
                    'data': date(2026, 1, 6),
                    'abertura': Decimal('31.50'),
                    'fechamento': Decimal('31.26'),
                    'minimo': Decimal('31.10'),
                    'maximo': Decimal('31.80'),
                    'volume': 125000000
                },
                ...
            ]
        """
        try:
            logger.info(f"Buscando histórico: {ticker} ({data_inicio} a {data_fim})")
            
            import yfinance as yf
            from datetime import timedelta
            
            # yfinance usa ticker com sufixo para Brasil
            #yahoo_ticker = f"{ticker}.SA" if ticker and not any(x in ticker for x in ['.SA', '^']) else ticker
            yahoo_ticker = ticker
            if mercado == 'BR' and '.' not in ticker and '^' not in ticker:
                yahoo_ticker = f"{ticker}.SA"
                        
            # Adicionar 1 dia à data_fim porque yfinance é exclusive no end
            data_fim_ajustada = data_fim + timedelta(days=1)
            
            stock = yf.Ticker(yahoo_ticker)
            hist = stock.history(
                start=data_inicio.strftime('%Y-%m-%d'),
                end=data_fim_ajustada.strftime('%Y-%m-%d')
            )
            
            if hist.empty:
                logger.warning(f"yfinance não retornou dados para {ticker}")
                return []
            
            # Converter DataFrame para lista de dicts
            resultado = []
            for data_index, row in hist.iterrows():
                resultado.append({
                    'data': data_index.date(),
                    'abertura': Decimal(str(row['Open'])) if not pd.isna(row['Open']) else None,
                    'fechamento': Decimal(str(row['Close'])),
                    'minimo': Decimal(str(row['Low'])) if not pd.isna(row['Low']) else None,
                    'maximo': Decimal(str(row['High'])) if not pd.isna(row['High']) else None,
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else None
                })
            
            logger.info(f"✅ {len(resultado)} registros obtidos para {ticker}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico de {ticker}: {str(e)}", exc_info=True)
            return []
