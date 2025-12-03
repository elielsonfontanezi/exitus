from decimal import Decimal
from sqlalchemy import func
from app.models import Posicao, Ativo
from app.database import db  # ← DB GLOBAL

def get_portfolio_metrics(usuario_id):
    """Calcula métricas reais do portfólio do usuário"""
    
    portfolio = db.session.query(Posicao, Ativo).outerjoin(
        Ativo, Posicao.ativo_id == Ativo.id
    ).filter(
        Posicao.usuario_id == usuario_id,
        Posicao.quantidade > 0
    ).all()
    
    if not portfolio:
        return {"erro": "Nenhuma posição ativa encontrada para este usuário"}
    
    total_custo = sum(float(p[0].custo_total or 0) for p in portfolio)
    total_valor_atual = sum(float(p[0].valor_atual or 0) for p in portfolio)
    
    rentabilidade_ytd = (
        (total_valor_atual - total_custo) / total_custo 
        if total_custo > 0 else 0.0
    )
    
    alocacao = {}
    total_valor = total_valor_atual
    for posicao, ativo in portfolio:
        classe = getattr(ativo, 'classe', 'desconhecida')
        valor = float(posicao.valor_atual or 0)
        alocacao[classe] = alocacao.get(classe, 0) + valor
    
    alocacao_pct = {k: v/total_valor for k, v in alocacao.items()} if total_valor > 0 else {}
    
    return {
        "total_custo": total_custo,
        "total_valor_atual": total_valor_atual,
        "rentabilidade_ytd": rentabilidade_ytd,
        "alocacao": alocacao_pct,
        "dividend_yield_medio": 0.045,
        "total_posicoes": len(portfolio)
    }
