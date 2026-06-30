import numpy as np
import logging
from app.models.ativo import Ativo
from app.models.historico_preco import HistoricoPreco
from app.services.valuation_service import calcular_valor_justo

logger = logging.getLogger(__name__)

def float_safe(value):
    """Converte Decimal/float/None para float seguro"""
    if value is None:
        return 0.0
    return float(value)

def calcular_margem_seguranca(ticker_or_ativo):
    """
    Calcula margem de segurança via valuation_service (BUG-VAL-005).

    Usa valor_justo calculado (Bazin/Graham/Gordon/DCF/Cap Rate + IQR + ponderação)
    como preço de referência — NÃO usa ativo.preco_teto (campo estático do usuário).

    Aceita ticker (str) ou objeto Ativo.
    Retorna (margem_percentual, valor_justo).
    """
    if isinstance(ticker_or_ativo, str):
        ativo = Ativo.query.filter_by(ticker=ticker_or_ativo.upper()).first()
        if not ativo:
            raise ValueError("Ativo não encontrado.")
    else:
        ativo = ticker_or_ativo

    vj = calcular_valor_justo(ativo)
    valor_justo = vj['valor_justo']
    preco_atual = vj['preco_atual']

    if valor_justo <= 0:
        raise ValueError("Valor justo inválido — verifique os dados do ativo.")

    margem = (valor_justo - preco_atual) / valor_justo * 100
    return margem, valor_justo

def calcular_buy_score(ticker_or_ativo):
    """Calcula buy score. Aceita ticker (str) ou objeto Ativo.
    
    Returns:
        dict: {
            'score': int (0-100),
            'components': {
                'margem': {'value': float, 'points': int, 'max': 30},
                'zscore': {'value': float, 'points': int, 'max': 25},
                'dy': {'value': float, 'points': int, 'max': 20},
                'beta': {'value': float, 'points': int, 'max': 25}
            }
        }
    """
    if isinstance(ticker_or_ativo, str):
        ativo = Ativo.query.filter_by(ticker=ticker_or_ativo.upper()).first()
        if not ativo:
            raise ValueError("Ativo não encontrado.")
    else:
        ativo = ticker_or_ativo
    
    try:
        margem, _ = calcular_margem_seguranca(ativo)
        zscore = calcular_zscore(ativo)
    except:
        margem, zscore = 0, 0
    
    dy = float_safe(ativo.dividend_yield) if ativo.dividend_yield else 4.0
    beta = float_safe(ativo.beta) if ativo.beta else 1.0
    
    # Buy Score 0-100 otimizado
    margem_pts = np.clip(margem * 3, 0, 30)
    z_pts = 25 if zscore < -1 else 15 if zscore < 0 else 5
    dy_pts = np.clip(dy * 5, 0, 20)
    beta_pts = np.clip(max(0, 25 - (beta - 1) * 12.5), 0, 25)
    
    score = margem_pts + z_pts + dy_pts + beta_pts
    
    return {
        'score': round(min(score, 100)),
        'components': {
            'margem': {'value': round(margem, 2), 'points': round(margem_pts), 'max': 30},
            'zscore': {'value': round(zscore, 2), 'points': z_pts, 'max': 25},
            'dy': {'value': round(dy, 2), 'points': round(dy_pts), 'max': 20},
            'beta': {'value': round(beta, 2), 'points': round(beta_pts), 'max': 25}
        }
    }


def calcular_zscore(ticker_or_ativo, dias: int = 252) -> float:
    """
    Calcula Z-Score baseado em histórico real de preços.
    
    Args:
        ticker_or_ativo: Código do ativo (str) ou objeto Ativo
        dias: Janela de dias úteis (padrão: 252 = 1 ano)
        
    Returns:
        Z-Score (-3 a +3 tipicamente)
        
    Raises:
        ValueError: Se ativo não encontrado ou histórico insuficiente
    """
    import numpy as np
    from app.services.historico_service import HistoricoService
    
    # Buscar ativo
    if isinstance(ticker_or_ativo, str):
        ativo = Ativo.query.filter_by(ticker=ticker_or_ativo.upper()).first()
        if not ativo:
            raise ValueError(f"Ativo {ticker_or_ativo} não encontrado")
    else:
        ativo = ticker_or_ativo
    
    preco_atual = float(ativo.preco_atual)
    
    # ✅ NOVO: Buscar histórico real (lazy loading)
    # Se já tem histórico suficiente (≥30 dias), usar existente
    # Se insuficiente, tentar buscar da API
    historico_existente = HistoricoPreco.query\
        .filter_by(ativoid=ativo.id)\
        .order_by(HistoricoPreco.data.desc())\
        .limit(dias)\
        .all()
    
    if len(historico_existente) >= 30:
        historico = historico_existente
    else:
        historico = HistoricoService.obter_ou_criar_historico(str(ativo.id), dias=dias)
    
    if len(historico) < 30:
        raise ValueError(f"Histórico insuficiente: {len(historico)} dias (mínimo 30)")
    
    # Extrair preços de fechamento
    precos = np.array([float(h.preco_fechamento) for h in historico])
    
    media = np.mean(precos)
    std = np.std(precos)
    
    if std == 0:
        logger.warning(f"{ticker}: Desvio padrão zero (preço constante)")
        return 0.0
    
    z = (preco_atual - media) / std
    return round(float(z), 2)


def obter_watchlist_top():
    ativos = Ativo.query.all()
    resultado = []
    for ativo in ativos:
        try:
            score_result = calcular_buy_score(ativo.ticker)
            score = score_result['score'] if isinstance(score_result, dict) else score_result
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
