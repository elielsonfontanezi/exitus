# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Service
Service layer para análises avançadas de portfólio
"""

from app.database import db
from app.models import Posicao, Transacao, Provento, MovimentacaoCaixa
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service para analytics de portfólio"""

    @staticmethod
    def get_dashboard(usuario_id):
        """
        Retorna dashboard completo do portfólio
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: Dados do dashboard
        """
        try:
            # Resumo de posições
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            total_investido = sum(p.custo_total for p in posicoes)
            total_atual = sum(p.valor_atual or Decimal('0') for p in posicoes)
            total_lucro_realizado = sum(p.lucro_prejuizo_realizado for p in posicoes)
            total_lucro_nao_realizado = sum(p.lucro_prejuizo_nao_realizado or Decimal('0') for p in posicoes)
            
            lucro_total = total_lucro_realizado + total_lucro_nao_realizado
            roi = (lucro_total / total_investido * 100) if total_investido > 0 else Decimal('0')
            
            # Proventos recebidos
            proventos_total = PortfolioService._calcular_proventos_total(usuario_id)
            
            # Distribuição por classe
            distribuicao = PortfolioService.get_distribuicao_classes(usuario_id)
            
            # Top 5 posições
            top_posicoes = sorted(posicoes, key=lambda p: p.valor_atual or Decimal('0'), reverse=True)[:5]
            
            return {
                'resumo_geral': {
                    'total_investido': float(total_investido),
                    'valor_atual': float(total_atual),
                    'lucro_realizado': float(total_lucro_realizado),
                    'lucro_nao_realizado': float(total_lucro_nao_realizado),
                    'lucro_total': float(lucro_total),
                    'roi_percentual': float(roi),
                    'quantidade_posicoes': len(posicoes)
                },
                'proventos': proventos_total,
                'distribuicao_classes': distribuicao,
                'top_posicoes': [
                    {
                        'ticker': p.ativo.ticker,
                        'nome': p.ativo.nome,
                        'quantidade': float(p.quantidade),
                        'valor_atual': float(p.valor_atual or 0),
                        'lucro_prejuizo': float((p.valor_atual or 0) - p.custo_total),
                        'percentual_carteira': float((p.valor_atual or 0) / total_atual * 100) if total_atual > 0 else 0
                    }
                    for p in top_posicoes
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard: {e}")
            raise


    @staticmethod
    def _calcular_proventos_total(usuario_id):
        """Calcula total de proventos recebidos"""
        from app.services.provento_service import ProventoService
        return ProventoService.calcular_total_recebido(usuario_id)


    @staticmethod
    def get_distribuicao_classes(usuario_id):
        """
        Retorna distribuição do portfólio por classe de ativo
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: Distribuição por classe
        """
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            total_carteira = sum(p.valor_atual or Decimal('0') for p in posicoes)
            
            distribuicao = {}
            
            for p in posicoes:
                classe = p.ativo.classe.value if p.ativo.classe else 'outros'
                valor = p.valor_atual or Decimal('0')
                
                if classe not in distribuicao:
                    distribuicao[classe] = {
                        'valor': Decimal('0'),
                        'quantidade_ativos': 0,
                        'lucro_prejuizo': Decimal('0')
                    }
                
                distribuicao[classe]['valor'] += valor
                distribuicao[classe]['quantidade_ativos'] += 1
                distribuicao[classe]['lucro_prejuizo'] += (valor - p.custo_total)
            
            # Calcular percentuais
            resultado = {}
            for classe, dados in distribuicao.items():
                percentual = (dados['valor'] / total_carteira * 100) if total_carteira > 0 else Decimal('0')
                
                resultado[classe] = {
                    'valor': float(dados['valor']),
                    'percentual': float(percentual),
                    'quantidade_ativos': dados['quantidade_ativos'],
                    'lucro_prejuizo': float(dados['lucro_prejuizo'])
                }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao calcular distribuição: {e}")
            raise


    @staticmethod
    def get_distribuicao_setores(usuario_id):
        """
        Retorna distribuição do portfólio por setor
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: Distribuição por setor
        """
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            total_carteira = sum(p.valor_atual or Decimal('0') for p in posicoes)
            
            distribuicao = {}
            
            for p in posicoes:
                setor = p.ativo.setor or 'Não classificado'
                valor = p.valor_atual or Decimal('0')
                
                if setor not in distribuicao:
                    distribuicao[setor] = {
                        'valor': Decimal('0'),
                        'quantidade_ativos': 0
                    }
                
                distribuicao[setor]['valor'] += valor
                distribuicao[setor]['quantidade_ativos'] += 1
            
            # Calcular percentuais e ordenar
            resultado = []
            for setor, dados in distribuicao.items():
                percentual = (dados['valor'] / total_carteira * 100) if total_carteira > 0 else Decimal('0')
                resultado.append({
                    'setor': setor,
                    'valor': float(dados['valor']),
                    'percentual': float(percentual),
                    'quantidade_ativos': dados['quantidade_ativos']
                })
            
            # Ordenar por valor (maior primeiro)
            resultado.sort(key=lambda x: x['valor'], reverse=True)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao calcular distribuição por setor: {e}")
            raise


    @staticmethod
    def get_evolucao_patrimonio(usuario_id, meses=12):
        """
        Retorna evolução do patrimônio ao longo do tempo
        
        Args:
            usuario_id (UUID): ID do usuário
            meses (int): Quantidade de meses para análise
        
        Returns:
            list: Evolução mensal
        """
        try:
            data_inicio = date.today() - timedelta(days=meses * 30)
            
            transacoes = Transacao.query.filter_by(usuario_id=usuario_id).filter(
                Transacao.data_transacao >= data_inicio
            ).order_by(Transacao.data_transacao.asc()).all()
            
            if not transacoes:
                return []
            
            # Agrupar por mês
            evolucao = {}
            patrimonio_acumulado = Decimal('0')
            
            for t in transacoes:
                mes_ano = t.data_transacao.strftime('%Y-%m')
                
                if mes_ano not in evolucao:
                    evolucao[mes_ano] = {
                        'data': mes_ano,
                        'aportes': Decimal('0'),
                        'resgates': Decimal('0'),
                        'patrimonio': Decimal('0')
                    }
                
                if t.tipo.value == 'compra':
                    evolucao[mes_ano]['aportes'] += t.valor_liquido
                    patrimonio_acumulado += t.valor_liquido
                elif t.tipo.value == 'venda':
                    evolucao[mes_ano]['resgates'] += t.valor_liquido
                    patrimonio_acumulado -= t.valor_liquido
                
                evolucao[mes_ano]['patrimonio'] = patrimonio_acumulado
            
            resultado = [
                {
                    'mes': dados['data'],
                    'aportes': float(dados['aportes']),
                    'resgates': float(dados['resgates']),
                    'patrimonio': float(dados['patrimonio'])
                }
                for dados in evolucao.values()
            ]
            
            return sorted(resultado, key=lambda x: x['mes'])
            
        except Exception as e:
            logger.error(f"Erro ao calcular evolução: {e}")
            raise


    @staticmethod
    def get_metricas_risco(usuario_id):
        """
        Calcula métricas de risco do portfólio
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            dict: Métricas de risco
        """
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            if not posicoes:
                return {}
            
            total_carteira = sum(p.valor_atual or Decimal('0') for p in posicoes)
            
            # Concentração (% do maior ativo)
            maior_posicao = max(posicoes, key=lambda p: p.valor_atual or Decimal('0'))
            concentracao = (maior_posicao.valor_atual or Decimal('0')) / total_carteira * 100 if total_carteira > 0 else Decimal('0')
            
            # Diversificação (quantidade de ativos)
            qtd_ativos = len(posicoes)
            
            # Índice Herfindahl-Hirschman (HHI) - mede concentração
            hhi = sum(
                ((p.valor_atual or Decimal('0')) / total_carteira * 100) ** 2
                for p in posicoes
            ) if total_carteira > 0 else Decimal('0')
            
            # Classificação de risco baseado em HHI
            if hhi < 1500:
                nivel_concentracao = 'Baixa'
            elif hhi < 2500:
                nivel_concentracao = 'Moderada'
            else:
                nivel_concentracao = 'Alta'
            
            return {
                'quantidade_ativos': qtd_ativos,
                'maior_posicao': {
                    'ticker': maior_posicao.ativo.ticker,
                    'percentual': float(concentracao)
                },
                'hhi': float(hhi),
                'nivel_concentracao': nivel_concentracao,
                'recomendacao': PortfolioService._gerar_recomendacao_risco(qtd_ativos, float(hhi))
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de risco: {e}")
            raise


    @staticmethod
    def _gerar_recomendacao_risco(qtd_ativos, hhi):
        """Gera recomendação baseada em métricas de risco"""
        recomendacoes = []
        
        if qtd_ativos < 5:
            recomendacoes.append("Considere diversificar mais seu portfólio (mínimo recomendado: 5-10 ativos)")
        
        if hhi > 2500:
            recomendacoes.append("Carteira muito concentrada. Considere reduzir exposição aos ativos principais")
        
        if not recomendacoes:
            recomendacoes.append("Portfólio com boa diversificação")
        
        return recomendacoes


    @staticmethod
    def get_performance_ativos(usuario_id):
        """
        Retorna performance individual de cada ativo
        
        Args:
            usuario_id (UUID): ID do usuário
        
        Returns:
            list: Performance dos ativos
        """
        try:
            posicoes = Posicao.query.filter_by(usuario_id=usuario_id).options(
                joinedload(Posicao.ativo)
            ).all()
            
            performance = []
            
            for p in posicoes:
                valor_atual = p.valor_atual or Decimal('0')
                lucro = valor_atual - p.custo_total
                roi = (lucro / p.custo_total * 100) if p.custo_total > 0 else Decimal('0')
                
                performance.append({
                    'ticker': p.ativo.ticker,
                    'nome': p.ativo.nome,
                    'quantidade': float(p.quantidade),
                    'preco_medio': float(p.preco_medio),
                    'preco_atual': float(p.ativo.preco_atual) if p.ativo.preco_atual else None,
                    'custo_total': float(p.custo_total),
                    'valor_atual': float(valor_atual),
                    'lucro_prejuizo': float(lucro),
                    'roi_percentual': float(roi),
                    'lucro_realizado': float(p.lucro_prejuizo_realizado)
                })
            
            # Ordenar por ROI (maior primeiro)
            performance.sort(key=lambda x: x['roi_percentual'], reverse=True)
            
            return performance
            
        except Exception as e:
            logger.error(f"Erro ao calcular performance: {e}")
            raise
