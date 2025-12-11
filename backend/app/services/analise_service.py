# -*- coding: utf-8 -*-
"""
Exitus - AnaliseService (M7.2)
Service para análises financeiras avançadas e cálculos quantitativos
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
from scipy.optimize import newton

from sqlalchemy import func, and_

from app.database import db
from app.models.posicao import Posicao
from app.models.transacao import Transacao
from app.models.provento import Provento
from app.models.ativo import Ativo


class AnaliseService:
    """Service para análises quantitativas e cálculos financeiros avançados."""

    @staticmethod
    def calcular_irr(fluxos_caixa: List[Tuple[date, Decimal]]) -> Optional[float]:
        """
        Calcula Taxa Interna de Retorno (IRR) usando método Newton-Raphson.
        
        Args:
            fluxos_caixa: Lista de tuplas (data, valor)
                - Valores negativos: investimentos (saídas)
                - Valores positivos: retornos (entradas)
                
        Returns:
            Taxa anual em percentual (ex: 12.5 para 12.5% ao ano)
            None se não convergir
            
        Example:
            >>> fluxos = [
            ...     (date(2024, 1, 1), Decimal('-10000')),  # Investimento inicial
            ...     (date(2024, 6, 1), Decimal('500')),      # Dividendo
            ...     (date(2024, 12, 31), Decimal('11000'))   # Venda + dividendos
            ... ]
            >>> irr = AnaliseService.calcular_irr(fluxos)
            >>> print(f"IRR: {irr:.2f}%")
        """
        if not fluxos_caixa or len(fluxos_caixa) < 2:
            return None
        
        # Ordenar por data
        fluxos_ordenados = sorted(fluxos_caixa, key=lambda x: x[0])
        
        # Data base (primeira transação)
        data_base = fluxos_ordenados[0][0]
        
        # Converter para arrays numpy
        valores = np.array([float(f[1]) for f in fluxos_ordenados], dtype=float)
        dias = np.array([(f[0] - data_base).days for f in fluxos_ordenados], dtype=float)
        
        # Função NPV (Net Present Value)
        def npv(taxa_diaria):
            return np.sum(valores / ((1 + taxa_diaria) ** dias))
        
        # Derivada do NPV
        def npv_derivada(taxa_diaria):
            return np.sum(-dias * valores / ((1 + taxa_diaria) ** (dias + 1)))
        
        try:
            # Chute inicial: 0.01% ao dia (equivalente a ~3.7% ao ano)
            taxa_diaria = newton(npv, x0=0.0001, fprime=npv_derivada, maxiter=100, tol=1e-6)
            
            # Converter taxa diária para anual
            taxa_anual = ((1 + taxa_diaria) ** 365 - 1) * 100
            
            return round(float(taxa_anual), 2)
        
        except (RuntimeError, ValueError):
            # Não convergiu
            return None

    @staticmethod
    def calcular_sharpe_ratio(
        retornos: List[float],
        taxa_livre_risco: float = 3.0
    ) -> Optional[float]:
        """
        Calcula Índice de Sharpe.
        
        Args:
            retornos: Lista de retornos percentuais diários/mensais
            taxa_livre_risco: Taxa livre de risco anual em % (default: 3% Selic)
            
        Returns:
            Índice de Sharpe (> 1.0 = boa, > 2.0 = excelente)
            None se dados insuficientes
            
        Formula:
            Sharpe = (Retorno Médio - Taxa Livre Risco) / Desvio Padrão
        """
        if not retornos or len(retornos) < 2:
            return None
        
        retornos_array = np.array(retornos, dtype=float)
        
        # Retorno médio
        retorno_medio = np.mean(retornos_array)
        
        # Desvio padrão
        desvio_padrao = np.std(retornos_array, ddof=1)
        
        if desvio_padrao == 0:
            return None
        
        # Ajustar taxa livre de risco para mesma periodicidade
        # Assumindo retornos diários: taxa_diaria = (1 + taxa_anual)^(1/365) - 1
        taxa_diaria = ((1 + taxa_livre_risco / 100) ** (1 / 365) - 1) * 100
        
        # Calcular Sharpe
        sharpe = (retorno_medio - taxa_diaria) / desvio_padrao
        
        return round(float(sharpe), 2)

    @staticmethod
    def calcular_sortino_ratio(
        retornos: List[float],
        target_return: float = 0.0
    ) -> Optional[float]:
        """
        Calcula Índice de Sortino (penaliza apenas desvio negativo).
        
        Args:
            retornos: Lista de retornos percentuais
            target_return: Retorno alvo em % (default: 0)
            
        Returns:
            Índice de Sortino
            None se dados insuficientes
            
        Formula:
            Sortino = (Retorno Médio - Target) / Downside Deviation
        """
        if not retornos or len(retornos) < 2:
            return None
        
        retornos_array = np.array(retornos, dtype=float)
        
        # Retorno médio
        retorno_medio = np.mean(retornos_array)
        
        # Calcular apenas desvios negativos (downside)
        retornos_negativos = retornos_array[retornos_array < target_return]
        
        if len(retornos_negativos) == 0:
            return None
        
        # Downside deviation
        downside_deviation = np.sqrt(np.mean((retornos_negativos - target_return) ** 2))
        
        if downside_deviation == 0:
            return None
        
        # Calcular Sortino
        sortino = (retorno_medio - target_return) / downside_deviation
        
        return round(float(sortino), 2)

    @staticmethod
    def calcular_max_drawdown(precos: List[Tuple[date, Decimal]]) -> Dict:
        """
        Calcula Maximum Drawdown (maior queda acumulada do pico).
        
        Args:
            precos: Lista de tuplas (data, preco)
            
        Returns:
            Dict com:
                - max_drawdown_percentual: % de queda máxima
                - data_pico: Data do pico
                - data_vale: Data do vale (ponto mais baixo)
                - valor_pico: Valor no pico
                - valor_vale: Valor no vale
            None se dados insuficientes
        """
        if not precos or len(precos) < 2:
            return None
        
        # Ordenar por data
        precos_ordenados = sorted(precos, key=lambda x: x[0])
        
        # Arrays
        datas = [p[0] for p in precos_ordenados]
        valores = np.array([float(p[1]) for p in precos_ordenados], dtype=float)
        
        # Calcular picos acumulados (running maximum)
        picos = np.maximum.accumulate(valores)
        
        # Calcular drawdowns
        drawdowns = (valores - picos) / picos * 100
        
        # Encontrar drawdown máximo
        idx_max_dd = np.argmin(drawdowns)
        max_drawdown = drawdowns[idx_max_dd]
        
        # Encontrar pico correspondente
        idx_pico = np.argmax(valores[:idx_max_dd + 1])
        
        return {
            'max_drawdown_percentual': round(float(max_drawdown), 2),
            'data_pico': datas[idx_pico].isoformat(),
            'data_vale': datas[idx_max_dd].isoformat(),
            'valor_pico': round(float(valores[idx_pico]), 2),
            'valor_vale': round(float(valores[idx_max_dd]), 2),
            'duracao_dias': (datas[idx_max_dd] - datas[idx_pico]).days
        }

    @staticmethod
    def calcular_volatilidade(
        retornos: List[float],
        anualizar: bool = True
    ) -> Optional[float]:
        """
        Calcula volatilidade (desvio padrão dos retornos).
        
        Args:
            retornos: Lista de retornos percentuais
            anualizar: Se True, retorna volatilidade anualizada
            
        Returns:
            Volatilidade em % ao ano (se anualizar=True)
            None se dados insuficientes
        """
        if not retornos or len(retornos) < 2:
            return None
        
        retornos_array = np.array(retornos, dtype=float)
        
        # Desvio padrão
        volatilidade = np.std(retornos_array, ddof=1)
        
        if anualizar:
            # Assumindo retornos diários: vol_anual = vol_diaria * sqrt(252)
            # 252 = dias úteis por ano
            volatilidade_anual = volatilidade * np.sqrt(252)
            return round(float(volatilidade_anual), 2)
        
        return round(float(volatilidade), 2)

    @staticmethod
    def analisar_performance_portfolio(
        usuario_id: UUID,
        portfolio_id: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Análise completa de performance do portfolio.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio (opcional)
            data_inicio: Data inicial (default: 1 ano atrás)
            data_fim: Data final (default: hoje)
            
        Returns:
            Dict com métricas completas de performance
        """
        # Datas padrão
        if data_fim is None:
            data_fim = date.today()
        
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=365)
        
        # Buscar transações do período
        query_txn = Transacao.query.filter(
            Transacao.usuario_id == usuario_id,
            Transacao.data_operacao >= data_inicio,
            Transacao.data_operacao <= data_fim
        )
        
        if portfolio_id:
            query_txn = query_txn.filter_by(portfolio_id=portfolio_id)
        
        transacoes = query_txn.order_by(Transacao.data_operacao).all()
        
        # Buscar proventos do período
        query_prov = Provento.query.filter(
            Provento.usuario_id == usuario_id,
            Provento.data_pagamento >= data_inicio,
            Provento.data_pagamento <= data_fim,
            Provento.status_pagamento == 'PAGO'
        )
        
        proventos = query_prov.all()
        
        # Montar fluxos de caixa para IRR
        fluxos_caixa = []
        
        # Transações
        for txn in transacoes:
            valor = txn.valor_total + txn.taxas
            if txn.tipo_operacao.value == 'COMPRA':
                valor = -valor  # Saída de caixa
            fluxos_caixa.append((txn.data_operacao, valor))
        
        # Proventos (entradas)
        for prov in proventos:
            fluxos_caixa.append((prov.data_pagamento, prov.valor_liquido))
        
        # Calcular IRR
        irr = AnaliseService.calcular_irr(fluxos_caixa) if fluxos_caixa else None
        
        # Buscar posições atuais
        query_pos = Posicao.query.filter(
            Posicao.usuario_id == usuario_id,
            Posicao.quantidade > 0
        )
        
        if portfolio_id:
            query_pos = query_pos.filter_by(portfolio_id=portfolio_id)
        
        posicoes = query_pos.all()
        
        # Calcular valor atual do portfolio
        valor_atual_total = sum(p.valor_atual or Decimal('0.00') for p in posicoes)
        custo_total = sum(p.custo_total for p in posicoes)
        
        # Adicionar posição atual ao fluxo de caixa (para IRR completo)
        if valor_atual_total > 0:
            fluxos_caixa.append((data_fim, valor_atual_total))
            irr = AnaliseService.calcular_irr(fluxos_caixa)
        
        # Calcular retornos diários simulados (baseado em transações)
        retornos_diarios = AnaliseService._calcular_retornos_diarios(transacoes, data_inicio, data_fim)
        
        # Calcular métricas
        sharpe = AnaliseService.calcular_sharpe_ratio(retornos_diarios) if retornos_diarios else None
        sortino = AnaliseService.calcular_sortino_ratio(retornos_diarios) if retornos_diarios else None
        volatilidade = AnaliseService.calcular_volatilidade(retornos_diarios) if retornos_diarios else None
        
        # Calcular drawdown
        precos_portfolio = AnaliseService._calcular_valor_portfolio_historico(
            posicoes, data_inicio, data_fim
        )
        max_dd = AnaliseService.calcular_max_drawdown(precos_portfolio) if precos_portfolio else None
        
        # Rentabilidade total
        rentabilidade_total = Decimal('0.00')
        if custo_total > 0:
            rentabilidade_total = ((valor_atual_total - custo_total) / custo_total) * 100
        
        return {
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'portfolio_id': str(portfolio_id) if portfolio_id else None,
            'metricas_financeiras': {
                'irr_percentual': irr,
                'sharpe_ratio': sharpe,
                'sortino_ratio': sortino,
                'volatilidade_anual': volatilidade,
                'max_drawdown': max_dd,
                'rentabilidade_total': float(rentabilidade_total)
            },
            'valores': {
                'custo_total': float(custo_total),
                'valor_atual': float(valor_atual_total),
                'lucro_nao_realizado': float(valor_atual_total - custo_total)
            },
            'atividade': {
                'num_transacoes': len(transacoes),
                'num_proventos': len(proventos),
                'num_posicoes_ativas': len(posicoes)
            }
        }

    @staticmethod
    def comparar_com_benchmark(
        usuario_id: UUID,
        portfolio_id: Optional[UUID],
        benchmark: str = 'IBOV',
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Compara performance do portfolio com benchmark.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio
            benchmark: Código do benchmark ('IBOV', 'SP500', etc)
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Dict com comparação de performance
            
        Note:
            Implementação simplificada - requer integração com API de benchmarks
        """
        # Análise do portfolio
        perf_portfolio = AnaliseService.analisar_performance_portfolio(
            usuario_id, portfolio_id, data_inicio, data_fim
        )
        
        # TODO: Integrar com API para dados de benchmark real
        # Por enquanto, retornar apenas dados do portfolio
        return {
            'portfolio': perf_portfolio,
            'benchmark': {
                'codigo': benchmark,
                'status': 'nao_implementado',
                'mensagem': 'Integração com API de benchmarks pendente (M8)'
            }
        }

    @staticmethod
    def calcular_correlacao_ativos(
        usuario_id: UUID,
        ativo1_id: UUID,
        ativo2_id: UUID,
        dias: int = 90
    ) -> Optional[float]:
        """
        Calcula correlação entre dois ativos.
        
        Args:
            usuario_id: ID do usuário
            ativo1_id: ID do primeiro ativo
            ativo2_id: ID do segundo ativo
            dias: Número de dias históricos a analisar
            
        Returns:
            Coeficiente de correlação (-1 a 1)
            None se dados insuficientes
            
        Note:
            Implementação simplificada - requer dados históricos de preços
        """
        # TODO: Implementar quando houver tabela de histórico de preços
        return None

    # ============ MÉTODOS PRIVADOS ============

    @staticmethod
    def _calcular_retornos_diarios(
        transacoes: List[Transacao],
        data_inicio: date,
        data_fim: date
    ) -> List[float]:
        """
        Calcula retornos diários simulados baseados em transações.
        
        Note:
            Implementação simplificada - ideal seria ter preços diários
        """
        if not transacoes:
            return []
        
        # Simular retornos baseados em variação de preços das transações
        retornos = []
        
        for i in range(1, len(transacoes)):
            txn_anterior = transacoes[i - 1]
            txn_atual = transacoes[i]
            
            # Calcular variação percentual de preço
            if txn_anterior.preco_unitario > 0:
                retorno = ((txn_atual.preco_unitario - txn_anterior.preco_unitario) / 
                          txn_anterior.preco_unitario * 100)
                retornos.append(float(retorno))
        
        return retornos

    @staticmethod
    def _calcular_valor_portfolio_historico(
        posicoes: List[Posicao],
        data_inicio: date,
        data_fim: date
    ) -> List[Tuple[date, Decimal]]:
        """
        Calcula valor histórico do portfolio.
        
        Note:
            Implementação simplificada - usa valores atuais das posições
        """
        # Retornar apenas valor inicial e final
        valor_total = sum(p.valor_atual or Decimal('0.00') for p in posicoes)
        
        return [
            (data_inicio, valor_total),
            (data_fim, valor_total)
        ]
