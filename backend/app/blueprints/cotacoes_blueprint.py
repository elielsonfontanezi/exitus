"""M7.5 - Cotacoes Live Blueprint"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import yfinance as yf
from app.database import db
from app.models import Ativo

cotacoes_bp = Blueprint('cotacoes', __name__, url_prefix='/api/cotacoes')

@cotacoes_bp.route('/<ticker>', methods=['GET'])
@jwt_required()
def obter_cotacao(ticker):
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
        
        # Atualizar banco CORRETAMENTE
        ativo.preco_atual = cotacao['preco_atual']
        ativo.dividend_yield = cotacao['dy_12m']
        ativo.p_l = cotacao['pl']
        db.session.commit()
        
        return jsonify(cotacao)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cotacoes_bp.route('/batch', methods=['GET'])
@jwt_required()
def cotacoes_batch():
    tickers = request.args.get('symbols', 'PETR4,VALE3,AAPL,BTC-USD').split(',')
    resultados = {}
    for ticker in tickers:
        try:
            ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
            if ativo:
                resultados[ticker] = obter_cotacao(ticker)[0].get_json()
        except:
            resultados[ticker] = {'error': 'Erro ao obter cotação'}
    return jsonify(resultados)
