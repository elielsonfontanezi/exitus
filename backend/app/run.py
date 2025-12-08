
# M7.5 COTAÇÕES LIVE - ROTAS PERMANENTES
from flask import request, jsonify
from flask_jwt_extended import jwt_required
import yfinance as yf
from app.database import db
from app.models import Ativo
import os

@app.route('/api/cotacoes/<ticker>', methods=['GET'])
@jwt_required()
def api_cotacoes(ticker):
    try:
        ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
        if not ativo:
            return jsonify({'error': f'Ativo {ticker} não encontrado'}), 404
        
        yahoo_ticker = f'{ticker}.SA' if ativo.mercado == 'BR' else ticker
        stock = yf.Ticker(yahoo_ticker)
        info = stock.info
        
        cotacao = {
            'ticker': ticker,
            'preco_atual': float(info.get('currentPrice') or info.get('regularMarketPrice') or 0),
            'variacao_percentual': float(info.get('regularMarketChangePercent', 0)),
            'volume': int(info.get('volume', 0)),
            'dy_12m': round(float(info.get('dividendYield', 0)) * 100, 2),
            'pl': round(float(info.get('forwardPE', 0)), 2)
        }
        
        # CORRIGIR nomes colunas banco
        ativo.preco_atual = cotacao['preco_atual']
        ativo.dividend_yield = cotacao['dy_12m']
        ativo.p_l = cotacao['pl']
        db.session.commit()
        
        return jsonify(cotacao)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cotacoes')
@jwt_required()
def dashboard_cotacoes():
    return '''
<!DOCTYPE html>
<html>
<head><title>Exitus - Cotações Live</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gradient-to-br from-gray-900 to-black text-white p-8 min-h-screen">
<h1 class="text-5xl font-bold mb-12 text-center text-yellow-400">📈 Cotações Live</h1>
<div id="cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto"></div>
<script>
["PETR4","VALE3","AAPL","BTC-USD"].forEach(async ticker=>{
  try{
    const resp=await fetch(`/api/cotacoes/\${ticker}`,{headers:{"Authorization":"Bearer ''' + request.headers.get('Authorization') + '''"}});
    const data=await resp.json();
    const color=data.preco_atual>0?'bg-green-900 border-green-500':'bg-red-900 border-red-500';
    document.getElementById('cards').innerHTML+=`
      <div class="\${color} border-4 rounded-2xl p-8 shadow-2xl hover:scale-105">
        <h2 class="text-2xl font-bold">\${data.ticker}</h2>
        <div class="text-4xl font-black">\${data.preco_atual?.toLocaleString()}</div>
        <div class="\${data.variacao_percentual>0?'text-green-400':'text-red-400'}">\${data.variacao_percentual>0?'📈':'📉'} \${data.variacao_percentual.toFixed(2)}%</div>
      </div>`;
  }catch(e){console.log(e);}
});
</script>
</body>
</html>
    '''
