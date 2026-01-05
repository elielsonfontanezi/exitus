import yfinance as yf
from app.database import db
from app.models import Ativo, FonteDados

class CotacaoService:
    @staticmethod
    def obter_cotacao(ticker):
        try:
            ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
            if not ativo:
                return {'error': 'Ativo não encontrado'}
            
            # yfinance adapta ticker (PETR4 → PETR4.SA)
            yahoo_ticker = f'{ticker}.SA' if ativo.mercado == 'BR' else ticker
            stock = yf.Ticker(yahoo_ticker)
            info = stock.info
            
            cotacao = {
                'ticker': ticker,
                'preco_atual': float(info.get('currentPrice', 0)),
                'preco_anterior': float(info.get('previousClose', 0)),
                'variacao_percentual': float(info.get('regularMarketChangePercent', 0)),
                'volume': int(info.get('volume', 0)),
                'dy_12m': float(info.get('dividendYield', 0)) * 100 if info.get('dividendYield') else 0,
                'pl': float(info.get('forwardPE', 0)) if info.get('forwardPE') else 0
            }
            
            # Atualizar Ativo no banco
            ativo.precoatual = cotacao['preco_atual']
            ativo.dividendyield = cotacao['dy_12m']
            ativo.pl = cotacao['pl']
            db.session.commit()
            
            return cotacao
        except Exception as e:
            return {'error': str(e)}
