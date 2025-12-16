"""M7.5 - Cotações Multi-Provider com Fallback Otimizado"""
import requests
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

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
            try:
                logger.info(f"📡 [1/4 BR] brapi.dev para {ticker}")
                url = CotacoesService._build_brapi_url(ticker)
                resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                if resp.status_code == 200:
                    data = resp.json()['results'][0]
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
            except Exception as e:
                logger.warning(f"⚠️ brapi.dev falhou: {e}")

            # 2️⃣ HG FINANCE (BR específico)
            if CotacoesService.HGFINANCE_KEY:
                try:
                    logger.info(f"📡 [2/4 BR] hgfinance para {ticker}")
                    url = f"https://api.hgbrasil.com/finance/stock_price?key={CotacoesService.HGFINANCE_KEY}&symbol={ticker}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                    
                    if resp.status_code == 200:
                        data = resp.json()['results'][ticker]
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
                except Exception as e:
                    logger.warning(f"⚠️ hgfinance falhou: {e}")

            # 3️⃣ YFINANCE (BR com .SA)
            try:
                logger.info(f"📡 [3/4 BR] yfinance para {ticker}")
                import yfinance as yf
                from requests.exceptions import Timeout
                
                stock = yf.Ticker(f'{ticker}.SA')
                hist = stock.history(period='1d', timeout=CotacoesService.TIMEOUT)
                
                if not hist.empty:
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
            except Timeout:
                logger.warning(f"⚠️ yfinance timeout 5s")
            except Exception as e:
                logger.warning(f"⚠️ yfinance falhou: {e}")

            # 4️⃣ TWELVE DATA (Global backup)
            if CotacoesService.TWELVE_KEY:
                try:
                    logger.info(f"📡 [4/4 BR] twelvedata para {ticker}")
                    url = f"https://api.twelvedata.com/price?symbol={ticker}.SA&apikey={CotacoesService.TWELVE_KEY}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'price' in data:
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
                except Exception as e:
                    logger.warning(f"⚠️ twelvedata falhou: {e}")

        # ============================================
        # ATIVOS US/GLOBAL
        # ============================================
        else:
            
            # 1️⃣ FINNHUB (PRINCIPAL US - 60 req/min)
            if CotacoesService.FINNHUB_KEY:
                try:
                    logger.info(f"📡 [1/4 US] finnhub para {ticker}")
                    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={CotacoesService.FINNHUB_KEY}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get('c'):  # current price
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
                except Exception as e:
                    logger.warning(f"⚠️ finnhub falhou: {e}")

            # 2️⃣ ALPHA VANTAGE (Confiável US)
            try:
                logger.info(f"📡 [2/4 US] alphavantage para {ticker}")
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={CotacoesService.ALPHA_KEY}"
                resp = requests.get(url, timeout=CotacoesService.TIMEOUT)

                if resp.status_code == 200:
                    data = resp.json().get('Global Quote', {})
                    if data and '05. price' in data:
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
            except Exception as e:
                logger.warning(f"⚠️ alphavantage falhou: {e}")

            # 3️⃣ TWELVE DATA (Global)
            if CotacoesService.TWELVE_KEY:
                try:
                    logger.info(f"📡 [3/4 US] twelvedata para {ticker}")
                    url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={CotacoesService.TWELVE_KEY}"
                    resp = requests.get(url, timeout=CotacoesService.TIMEOUT)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if 'price' in data:
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
                except Exception as e:
                    logger.warning(f"⚠️ twelvedata falhou: {e}")

            # 4️⃣ YFINANCE (Último recurso)
            try:
                logger.info(f"📡 [4/4 US] yfinance para {ticker}")
                import yfinance as yf
                from requests.exceptions import Timeout
                
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1d', timeout=CotacoesService.TIMEOUT)
                
                if not hist.empty:
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
            except Timeout:
                logger.warning(f"⚠️ yfinance timeout 5s")
            except Exception as e:
                logger.warning(f"⚠️ yfinance falhou: {e}")

        # ❌ TODAS FALHARAM
        logger.error(f"❌ Todos os 4 providers falharam para {ticker}")
        return {'success': False, 'error': 'Todas APIs indisponíveis', 'ticker': ticker}
