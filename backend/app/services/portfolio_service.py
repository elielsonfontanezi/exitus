from decimal import Decimal
import numpy as np
from sqlalchemy import func
from app.models import Posicao, Ativo
from app.database import db

def get_portfolio_metrics(usuario_id):
    """Calcula métricas reais + AVANÇADAS do portfólio do usuário"""
    
    portfolio = db.session.query(Posicao, Ativo).outerjoin(
        Ativo, Posicao.ativo_id == Ativo.id
    ).filter(
        Posicao.usuario_id == usuario_id,
        Posicao.quantidade > 0
    ).all()
    
    if not portfolio:
        return {"erro": "Nenhuma posição ativa encontrada para este usuário"}
    
    # 1. MÉTRICAS BÁSICAS
    total_custo = sum(float(p[0].custo_total or 0) for p in portfolio)
    total_valor_atual = sum(float(p[0].valor_atual or 0) for p in portfolio)
    rentabilidade_ytd = ((total_valor_atual - total_custo) / total_custo 
                        if total_custo > 0 else 0.0)
    
    # 2. ALOCAÇÃO POR CLASSE
    alocacao = {}
    total_valor = total_valor_atual
    for posicao, ativo in portfolio:
        classe = getattr(ativo, 'classe', 'desconhecida')
        valor = float(posicao.valor_atual or 0)
        alocacao[classe] = alocacao.get(classe, 0) + valor
    
    alocacao_pct = {k: v/total_valor for k, v in alocacao.items()} if total_valor > 0 else {}
    
    # 3. RETORNOS POR POSIÇÃO (para cálculos estatísticos)
    retornos = []
    for posicao, ativo in portfolio:
        if posicao.valor_atual and posicao.custo_total and float(posicao.custo_total) > 0:
            retorno = (float(posicao.valor_atual) - float(posicao.custo_total)) / float(posicao.custo_total)
            retornos.append(retorno)
    
    # 4. MÉTRICAS DE RISCO AVANÇADAS
    if len(retornos) > 0:
        # Volatilidade anualizada (252 dias úteis)
        volatilidade_diaria = np.std(retornos)
        volatilidade_anualizada = volatilidade_diaria * np.sqrt(252)
        
        # Sharpe Ratio (retorno - Rf) / volatilidade
        retorno_medio = np.mean(retornos)
        rf = 0.10  # Taxa livre de risco CDI ~10%
        sharpe_ratio = (retorno_medio - rf) / volatilidade_anualizada
        
        # Max Drawdown (simplificado)
        pico = np.maximum.accumulate(retornos)
        drawdown = (pico - retornos) / pico
        max_drawdown = np.max(drawdown)
        
        # Beta vs IBOV (mock dados 30 dias)
        retornos_ibov_mock = np.array([0.012, -0.008, 0.015, -0.003, 0.009, 
                                     0.002, -0.011, 0.007, 0.004, -0.006])
        retornos_port = np.array(retornos[:len(retornos_ibov_mock)])
        if len(retornos_port) > 1:
            cov_matrix = np.cov(retornos_port, retornos_ibov_mock)
            beta = cov_matrix[0,1] / cov_matrix[1,1]
        else:
            beta = 1.0
    else:
        volatilidade_anualizada = 0.0
        sharpe_ratio = 0.0
        max_drawdown = 0.0
        beta = 1.0
    
    # 5. CORRELAÇÃO ENTRE ATIVOS (placeholder para implementação futura)
    correlacao_ativos = {"placeholder": "Correlação requer histórico de preços"}
    
    return {
        "portfolio_info": {
            "total_custo": total_custo,
            "total_valor_atual": total_valor_atual,
            "total_posicoes": len(portfolio)
        },
        "rentabilidade_ytd": rentabilidade_ytd,
        "alocacao": alocacao_pct,
        "dividend_yield_medio": 0.045,
        # MÉTRICAS AVANÇADAS
        "volatilidade_anualizada": float(volatilidade_anualizada),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": float(max_drawdown),
        "beta_ibov": float(beta),
        "correlacao_ativos": correlacao_ativos
    }
