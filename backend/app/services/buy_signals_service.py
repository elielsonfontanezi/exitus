import numpy as np
from app.models.ativo import Ativo

def float_safe(value):
    """Converte Decimal/float/None para float seguro"""
    if value is None:
        return 0.0
    return float(value)

def calcular_margem_seguranca(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    if not ativo:
        raise ValueError("Ativo não encontrado.")
    
    preco_atual = float_safe(ativo.preco_atual)
    preco_teto = float_safe(ativo.preco_teto)
    
    if preco_teto == 0:
        raise ValueError("Preço teto inválido.")
    
    margem = (preco_teto - preco_atual) / preco_teto * 100
    return margem, preco_teto

def calcular_buy_score(ticker):
    try:
        margem, _ = calcular_margem_seguranca(ticker)
        zscore = calcular_zscore(ticker)
    except:
        margem, zscore = 0, 0
    
    dy = float_safe(Ativo.query.filter_by(ticker=ticker).first().dividend_yield) if Ativo.query.filter_by(ticker=ticker).first() else 4.0
    beta = float_safe(Ativo.query.filter_by(ticker=ticker).first().beta) if Ativo.query.filter_by(ticker=ticker).first() else 1.0
    
    # Buy Score 0-100 otimizado
    margem_pts = np.clip(margem * 3, 0, 30)
    z_pts = 25 if zscore < -1 else 15 if zscore < 0 else 5
    dy_pts = np.clip(dy * 5, 0, 20)
    beta_pts = np.clip(max(0, 25 - (beta - 1) * 12.5), 0, 25)
    
    score = margem_pts + z_pts + dy_pts + beta_pts
    return round(min(score, 100))

def calcular_zscore(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    if not ativo:
        raise ValueError("Ativo não encontrado.")
    
    preco_atual = float_safe(ativo.preco_atual)
    
    # Histórico realista PETR4 (baseado nos dados atuais)
    historico_simulado = np.array([
        42.0, 41.5, 40.8, 39.2, 38.6, 37.9, 38.1, 39.8, 
        41.2, 40.5, 39.0, 38.6
    ], dtype=float)
    
    media = np.mean(historico_simulado)
    std = np.std(historico_simulado)
    if std == 0:
        return 0.0
    z = (preco_atual - media) / std
    return round(float(z), 2)

def obter_watchlist_top():
    ativos = Ativo.query.all()
    resultado = []
    for ativo in ativos:
        try:
            score = calcular_buy_score(ativo.ticker)
            resultado.append({
                "ticker": ativo.ticker,
                "buy_score": score,
                "preco_atual": float_safe(ativo.preco_atual),
                "preco_teto": float_safe(ativo.preco_teto)
            })
        except:
            continue
    resultado.sort(key=lambda x: x["buy_score"], reverse=True)
    return resultado[:10]
