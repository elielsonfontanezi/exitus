# -*- coding: utf-8 -*-
"""
Portfolio Service - Análise Consolidada de Portfolio
"""
from decimal import Decimal
import numpy as np
from sqlalchemy import func
from app.models import Posicao, Ativo, MovimentacaoCaixa
from app.database import db


class PortfolioService:
    """Service para cálculos e análises de portfolio consolidado"""
    
    @staticmethod
    def get_dashboard(usuario_id):
        """
        Dashboard completo do portfolio - conforme API Reference
        
        Returns:
            dict: {
                patrimonio_ativos, custo_aquisicao, saldo_caixa,
                patrimonio_total, lucro_bruto, rentabilidade_perc
            }
        """
        # Buscar posições ativas
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).filter(
            Posicao.quantidade > 0
        ).all()
        
        # Calcular métricas de ativos
        patrimonio_ativos = sum(float(p.valor_atual or 0) for p in posicoes)
        custo_aquisicao = sum(float(p.custo_total or 0) for p in posicoes)
        
        # Calcular saldo em caixa (somar todos os DEPOSITOs - SAQUEs)
        saldo_caixa = db.session.query(
            func.coalesce(func.sum(MovimentacaoCaixa.valor), 0)
        ).filter(
            MovimentacaoCaixa.usuario_id == usuario_id
        ).scalar() or 0.0
        
        saldo_caixa = float(saldo_caixa)
        
        # Calcular métricas consolidadas
        patrimonio_total = patrimonio_ativos + saldo_caixa
        lucro_bruto = patrimonio_ativos - custo_aquisicao
        rentabilidade_perc = (
            (lucro_bruto / custo_aquisicao * 100) if custo_aquisicao > 0 else 0.0
        )
        
        return {
            'patrimonio_ativos': round(patrimonio_ativos, 2),
            'custo_aquisicao': round(custo_aquisicao, 2),
            'saldo_caixa': round(saldo_caixa, 2),
            'patrimonio_total': round(patrimonio_total, 2),
            'lucro_bruto': round(lucro_bruto, 2),
            'rentabilidade_perc': round(rentabilidade_perc, 2)
        }
    
    @staticmethod
    def get_alocacao(usuario_id):
        """
        Distribuição do portfolio por classe de ativo
        
        Returns:
            dict: { classe: { valor, percentual }, ... }
        """
        posicoes = db.session.query(Posicao, Ativo).join(
            Ativo, Posicao.ativo_id == Ativo.id
        ).filter(
            Posicao.usuario_id == usuario_id,
            Posicao.quantidade > 0
        ).all()
        
        if not posicoes:
            return {}
        
        # Agrupar por classe
        alocacao = {}
        total_valor = 0.0
        
        for posicao, ativo in posicoes:
            # ✅ CONVERSÃO CRÍTICA: Enum -> String
            classe_raw = getattr(ativo, 'classe', None)
            
            if classe_raw is None:
                classe = 'DESCONHECIDA'
            elif hasattr(classe_raw, 'value'):
                # É um Enum, extrair o valor
                classe = str(classe_raw.value)
            else:
                # Já é string
                classe = str(classe_raw)
            
            valor_posicao = float(posicao.valor_atual or 0)
            total_valor += valor_posicao
            
            if classe not in alocacao:
                alocacao[classe] = {'valor': 0.0, 'percentual': 0.0}
            
            alocacao[classe]['valor'] += valor_posicao
        
        # Calcular percentuais
        if total_valor > 0:
            for classe in alocacao:
                alocacao[classe]['percentual'] = round(
                    (alocacao[classe]['valor'] / total_valor) * 100, 2
                )
                alocacao[classe]['valor'] = round(alocacao[classe]['valor'], 2)
        
        return alocacao
    
    @staticmethod
    def get_portfolio_metrics(usuario_id):
        """
        Métricas avançadas do portfolio (para calculosblueprint)
        
        Returns:
            dict: Estrutura COMPLETA esperada pelo calculosblueprint
        """
        dashboard = PortfolioService.get_dashboard(usuario_id)
        alocacao = PortfolioService.get_alocacao(usuario_id)
        
        # Contar ativos
        num_ativos = Posicao.query.filter_by(usuario_id=usuario_id).filter(
            Posicao.quantidade > 0
        ).count()
        
        # Calcular dividend yield médio (simplificado)
        posicoes_com_ativo = db.session.query(Posicao, Ativo).join(
            Ativo, Posicao.ativo_id == Ativo.id
        ).filter(
            Posicao.usuario_id == usuario_id,
            Posicao.quantidade > 0
        ).all()
        
        dividend_yields = [
            float(ativo.dividend_yield or 0) 
            for _, ativo in posicoes_com_ativo 
            if ativo.dividend_yield
        ]
        dividend_yield_medio = (
            sum(dividend_yields) / len(dividend_yields) 
            if dividend_yields else 0.0
        )
        
        # Retornar estrutura COMPLETA esperada pelo calculosblueprint
        return {
            'portfolio_info': {
                'patrimonio_total': dashboard['patrimonio_total'],
                'custo_total': dashboard['custo_aquisicao'],
                'num_ativos': num_ativos,
                'saldo_caixa': dashboard['saldo_caixa']
            },
            'rentabilidade_ytd': dashboard['rentabilidade_perc'] / 100,
            'alocacao': alocacao,  # Campo esperado: 'alocacao' não 'alocacao_por_classe'
            'dividend_yield_medio': round(dividend_yield_medio, 2),
            'volatilidade_anualizada': 0.0,  # TODO: calcular com histórico
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'beta_ibov': 0.0,  # TODO: calcular correlação com IBOV
            'correlacao_ativos': {}  # TODO: matriz de correlação
        }

    @staticmethod
    def get_distribuicao_classes(usuario_id):
        """
        Wrapper para get_alocacao (mantém compatibilidade com blueprint)
        
        Returns:
            dict: { total, classes: {...} }
        """
        alocacao = PortfolioService.get_alocacao(usuario_id)
        dashboard = PortfolioService.get_dashboard(usuario_id)
        
        return {
            'total': dashboard['patrimonio_total'],
            'classes': alocacao
        }
    
    @staticmethod
    def get_distribuicao_setores(usuario_id):
        """
        Distribuição por setor (simplificado - retorna vazio por enquanto)
        
        Returns:
            dict: Distribuição por setor
        """
        # TODO: Implementar quando houver campo 'setor' em Ativo
        return {}
    
    @staticmethod
    def get_evolucao_patrimonio(usuario_id, meses=12):
        """
        Evolução do patrimônio (simplificado - retorna snapshot atual)
        
        Returns:
            list: Histórico de patrimônio
        """
        # TODO: Implementar com histórico real de transações
        dashboard = PortfolioService.get_dashboard(usuario_id)
        return [{
            'mes': '2025-12',
            'patrimonio': dashboard['patrimonio_total']
        }]
    
    @staticmethod
    def get_metricas_risco(usuario_id):
        """
        Métricas de risco do portfolio
        
        Returns:
            dict: Métricas de risco
        """
        return {
            'volatilidade': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'var_95': 0.0  # Value at Risk 95%
        }
    
    @staticmethod
    def get_performance_ativos(usuario_id):
        """
        Performance individual de cada ativo
        
        Returns:
            list: Lista de ativos com performance
        """
        posicoes = db.session.query(Posicao, Ativo).join(
            Ativo, Posicao.ativo_id == Ativo.id
        ).filter(
            Posicao.usuario_id == usuario_id,
            Posicao.quantidade > 0
        ).all()
        
        performance = []
        for posicao, ativo in posicoes:
            ticker = getattr(ativo, 'ticker', 'N/A')
            custo = float(posicao.custo_total or 0)
            valor_atual = float(posicao.valor_atual or 0)
            lucro = valor_atual - custo
            rentabilidade = (lucro / custo * 100) if custo > 0 else 0.0
            
            performance.append({
                'ticker': ticker,
                'quantidade': float(posicao.quantidade),
                'custo_total': round(custo, 2),
                'valor_atual': round(valor_atual, 2),
                'lucro': round(lucro, 2),
                'rentabilidade_perc': round(rentabilidade, 2)
            })
        
        return performance

# ============================================
# FUNÇÕES STANDALONE para retrocompatibilidade
# ============================================

def get_portfolio_metrics(usuario_id):
    """Wrapper para retrocompatibilidade"""
    return PortfolioService.get_portfolio_metrics(usuario_id)


def get_dashboard(usuario_id):
    """Wrapper para get_dashboard"""
    return PortfolioService.get_dashboard(usuario_id)


def get_alocacao(usuario_id):
    """Wrapper para get_alocacao"""
    return PortfolioService.get_alocacao(usuario_id)
