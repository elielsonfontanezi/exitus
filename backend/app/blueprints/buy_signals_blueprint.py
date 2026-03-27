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

@buy_signals_bp.route('/analisar/<string:ticker>', methods=['GET'])
def analisar_ativo(ticker):
    """
    Análise completa de um ativo para Buy Signals.
    Retorna: buy_score, margem, z_score, métricas fundamentalistas, sinal de compra.
    """
    from app.models.ativo import Ativo
    
    ticker = ticker.upper()
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    
    if not ativo:
        return jsonify({
            "success": False, 
            "error": f"Ativo {ticker} não encontrado"
        }), 404
    
    try:
        buy_score = calcular_buy_score(ticker)
        margem, preco_teto = calcular_margem_seguranca(ticker)
        
        try:
            z_score = calcular_zscore(ticker)
        except:
            z_score = 0.0
        
        sinal = "COMPRAR" if buy_score >= 80 else "AGUARDAR" if buy_score >= 60 else "VENDER"
        
        resultado = {
            "ticker": ticker,
            "nome": ativo.nome or ticker,
            "mercado": ativo.mercado or "BR",
            "buyscore": buy_score,
            "margem": round(margem, 2),
            "z_score": z_score,
            "sinal": sinal,
            "preco_atual": float(ativo.preco_atual) if ativo.preco_atual else 0.0,
            "preco_teto": float(preco_teto),
            "dy": float(ativo.dividend_yield) if ativo.dividend_yield else 0.0,
            "pl": float(ativo.p_l) if ativo.p_l else 0.0,
            "pvp": float(ativo.p_vp) if ativo.p_vp else 0.0,
            "roe": float(ativo.roe) if ativo.roe else 0.0,
            "tipo": ativo.tipo.value if ativo.tipo else "ACAO"
        }
        
        return jsonify({"success": True, "data": resultado}), 200
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"Erro ao analisar ativo: {str(e)}"
        }), 400
