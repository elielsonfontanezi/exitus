from flask import Blueprint, jsonify, request
from app.services.buy_signals_service import (
    calcular_margem_seguranca,
    calcular_buy_score,
    calcular_zscore,
    obter_watchlist_top
)

buy_signals_bp = Blueprint('buy_signals_bp', __name__)

@buy_signals_bp.route('/margem-seguranca/<string:ticker>', methods=['GET'])
def margem_seguranca(ticker):
    from app.models.ativo import Ativo
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        return jsonify({"success": False, "error": f"Ativo {ticker} não encontrado"}), 404
    try:
        margem, preco_teto = calcular_margem_seguranca(ticker)
        sinal = "🟢 COMPRA" if margem > 5 else "🟡 NEUTRO" if margem > 0 else "🔴 VENDA"
        return jsonify({"success": True, "data": {"ticker": ticker, "margem_seguranca": margem, "sinal": sinal}, "message": f"Margem de segurança: {margem:.2f}% vs Teto R${preco_teto:.2f}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@buy_signals_bp.route('/buy-score/<string:ticker>', methods=['GET'])
def buy_score(ticker):
    from app.models.ativo import Ativo
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        return jsonify({"success": False, "error": f"Ativo {ticker} não encontrado"}), 404
    try:
        score = calcular_buy_score(ticker)
        return jsonify({"success": True, "data": {"ticker": ticker, "buy_score": score}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@buy_signals_bp.route('/zscore/<string:ticker>', methods=['GET'])
def zscore(ticker):
    from app.models.ativo import Ativo
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        return jsonify({"success": False, "error": f"Ativo {ticker} não encontrado"}), 404
    try:
        z = calcular_zscore(ticker)
        return jsonify({"success": True, "data": {"ticker": ticker, "z_score": z}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@buy_signals_bp.route('/watchlist-top', methods=['GET'])
def watchlist_top():
    try:
        top10 = obter_watchlist_top()
        return jsonify({"success": True, "data": top10})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
