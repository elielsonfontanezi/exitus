from flask import Blueprint, jsonify, request
from app.services.buy_signals_service import (
    calcular_margem_seguranca,
    calcular_buy_score,
    calcular_zscore,
    obter_watchlist_top
)
from app.services.valuation_service import calcular_valor_justo

buy_signals_bp = Blueprint('buy_signals_bp', __name__)

@buy_signals_bp.route('/margem-seguranca/<string:ticker>', methods=['GET'])
def margem_seguranca(ticker):
    from app.models.ativo import Ativo
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        return jsonify({"success": False, "error": f"Ativo {ticker} não encontrado"}), 404
    try:
        vj = calcular_valor_justo(ativo)
        margem = vj['margem_seguranca']
        valor_justo = vj['valor_justo']
        preco_atual = vj['preco_atual']
        sinal = "🟢 COMPRA" if margem > 5 else "🟡 NEUTRO" if margem > 0 else "🔴 VENDA"
        return jsonify({
            "success": True,
            "data": {
                "ticker": ticker.upper(),
                "margem_seguranca": round(margem, 2),
                "sinal": sinal,
                "valor_justo": round(valor_justo, 2),
                "preco_teto": round(valor_justo, 2),   # alias retrocompat
                "faixa_min": vj['faixa_min'],
                "faixa_max": vj['faixa_max'],
                "perfil": vj['perfil'],
                "preco_atual": round(preco_atual, 2),
            },
            "message": f"Margem de segurança: {margem:.2f}% vs Valor Justo R${valor_justo:.2f}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@buy_signals_bp.route('/buy-score/<string:ticker>', methods=['GET'])
def buy_score(ticker):
    from app.models.ativo import Ativo
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        return jsonify({"success": False, "error": f"Ativo {ticker} não encontrado"}), 404
    try:
        result = calcular_buy_score(ticker)
        return jsonify({"success": True, "data": {"ticker": ticker, "buy_score": result['score'], "components": result['components']}})
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
        return jsonify({"success": True, "data": {"ticker": ticker, "zscore": z}})
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
        buy_score_result = calcular_buy_score(ticker)
        buy_score = buy_score_result['score']
        vj = calcular_valor_justo(ativo)
        margem = vj['margem_seguranca']
        valor_justo = vj['valor_justo']

        try:
            z_score = calcular_zscore(ticker)
        except Exception:
            z_score = 0.0

        sinal = "COMPRAR" if buy_score >= 80 else "AGUARDAR" if buy_score >= 60 else "VENDER"

        resultado = {
            "ticker": ticker,
            "nome": ativo.nome or ticker,
            "mercado": ativo.mercado or "BR",
            "buyscore": buy_score,
            "components": buy_score_result['components'],
            "margem": round(margem, 2),
            "z_score": z_score,
            "sinal": sinal,
            "preco_atual": vj['preco_atual'],
            "preco_teto": round(valor_justo, 2),    # alias retrocompat
            "valor_justo": round(valor_justo, 2),
            "faixa_min": vj['faixa_min'],
            "faixa_max": vj['faixa_max'],
            "perfil_valuation": vj['perfil'],
            "dy": float(ativo.dividend_yield) if ativo.dividend_yield else 0.0,
            "pl": float(ativo.p_l) if ativo.p_l else 0.0,
            "pvp": float(ativo.p_vp) if ativo.p_vp else 0.0,
            "roe": float(ativo.roe) if ativo.roe else 0.0,
            "tipo": ativo.tipo.value if ativo.tipo else "ACAO",
        }

        return jsonify({"success": True, "data": resultado}), 200
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"Erro ao analisar ativo: {str(e)}"
        }), 400
