# -*- coding: utf-8 -*-
"""
Exitus - RelatorioService (M7.2)
Service para geração e gestão de relatórios consolidados
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID
import uuid

from sqlalchemy import func, and_, or_, extract
from sqlalchemy.orm import joinedload

from app.database import db
from app.models.auditoria_relatorio import AuditoriaRelatorio
from app.models.posicao import Posicao
from app.models.transacao import Transacao
from app.models.provento import Provento
from app.models.ativo import Ativo
from app.models.corretora import Corretora


class RelatorioService:
    """Service para operações de relatórios e análises."""

    @staticmethod
    def listar_relatorios(usuario_id: UUID, page: int = 1, per_page: int = 10) -> Dict:
        """
        Lista relatórios paginados por usuário.
        
        Args:
            usuario_id: ID do usuário
            page: Número da página
            per_page: Itens por página
            
        Returns:
            Dict com relatórios paginados
        """
        query = AuditoriaRelatorio.query.filter_by(usuario_id=usuario_id)\
            .order_by(AuditoriaRelatorio.timestamp_criacao.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'relatorios': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }

    @staticmethod
    def obter_relatorio(usuario_id: UUID, relatorio_id: UUID) -> Dict:
        """
        Obtém relatório específico por ID.
        
        Args:
            usuario_id: ID do usuário proprietário
            relatorio_id: ID do relatório
            
        Returns:
            Dict com dados do relatório
            
        Raises:
            ValueError: Se relatório não encontrado
        """
        relatorio = AuditoriaRelatorio.query.filter_by(
            id=relatorio_id,
            usuario_id=usuario_id
        ).first()
        
        if not relatorio:
            raise ValueError("Relatório não encontrado")
        
        return relatorio.to_dict()

    @staticmethod
    def gerar_relatorio_portfolio(
        usuario_id: UUID,
        filtros: Optional[Dict] = None
    ) -> Dict:
        """
        Gera relatório consolidado de portfolio.
        
        Args:
            usuario_id: ID do usuário
            filtros: Dict com filtros opcionais:
                - pais: str (ex: 'BR', 'US')
                - mercado: str (ex: 'B3', 'NYSE')
                - setor: str
                - classe: str (ex: 'RENDA_VARIAVEL')
                - data_inicio: date
                - data_fim: date
                
        Returns:
            Dict com relatório completo
        """
        filtros = filtros or {}
        
        # Query base de posições
        query = Posicao.query.filter_by(usuario_id=usuario_id)\
            .join(Ativo)\
            .join(Corretora)\
            .options(
                joinedload(Posicao.ativo),
                joinedload(Posicao.corretora)
            )
        
        # Aplicar filtros dimensionais
        if filtros.get('pais'):
            query = query.filter(Corretora.pais == filtros['pais'].upper())
        
        if filtros.get('mercado'):
            query = query.filter(Ativo.mercado == filtros['mercado'].upper())
        
        if filtros.get('classe'):
            query = query.filter(Ativo.classe == filtros['classe'].upper())
        
        # Apenas posições ativas (quantidade > 0)
        query = query.filter(Posicao.quantidade > 0)
        
        posicoes = query.all()
        
        # Calcular métricas consolidadas
        metricas = RelatorioService._calcular_metricas_portfolio(posicoes)
        
        # Montar estrutura do relatório
        relatorio_data = {
            'tipo': 'PORTFOLIO',
            'data_geracao': datetime.utcnow().isoformat(),
            'filtros_aplicados': filtros,
            'metricas': metricas,
            'posicoes': [RelatorioService._posicao_to_dict(p) for p in posicoes],
            'total_posicoes': len(posicoes)
        }
        
        # Persistir auditoria
        auditoria = RelatorioService._persistir_auditoria(
            usuario_id=usuario_id,
            tipo_relatorio='PORTFOLIO',
            filtros=filtros,
            resultado=relatorio_data
        )
        
        relatorio_data['relatorio_id'] = str(auditoria.id)
        
        return relatorio_data

    @staticmethod
    def gerar_relatorio_performance(
        usuario_id: UUID,
        data_inicio: date,
        data_fim: date,
        filtros: Optional[Dict] = None
    ) -> Dict:
        """
        Gera relatório de performance do portfolio no período.
        
        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do período
            data_fim: Data final do período
            filtros: Filtros adicionais
            
        Returns:
            Dict com relatório de performance
        """
        filtros = filtros or {}
        
        # Buscar transações do período
        query_transacoes = Transacao.query.filter(
            Transacao.usuario_id == usuario_id,
            Transacao.data_operacao >= data_inicio,
            Transacao.data_operacao <= data_fim
        ).join(Ativo)
        
        if filtros.get('pais'):
            query_transacoes = query_transacoes.join(Corretora).filter(
                Corretora.pais == filtros['pais'].upper()
            )
        
        transacoes = query_transacoes.all()
        
        # Buscar proventos do período
        query_proventos = Provento.query.filter(
            Provento.usuario_id == usuario_id,
            Provento.data_pagamento >= data_inicio,
            Provento.data_pagamento <= data_fim,
            Provento.status_pagamento == 'PAGO'
        ).join(Ativo)
        
        proventos = query_proventos.all()
        
        # Calcular métricas de performance
        performance = RelatorioService._calcular_performance_periodo(
            transacoes, proventos, data_inicio, data_fim
        )
        
        relatorio_data = {
            'tipo': 'PERFORMANCE',
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'data_geracao': datetime.utcnow().isoformat(),
            'filtros_aplicados': filtros,
            'performance': performance,
            'transacoes_periodo': len(transacoes),
            'proventos_recebidos': len(proventos)
        }
        
        # Persistir auditoria
        auditoria = RelatorioService._persistir_auditoria(
            usuario_id=usuario_id,
            tipo_relatorio='PERFORMANCE',
            filtros={**filtros, 'data_inicio': data_inicio.isoformat(), 'data_fim': data_fim.isoformat()},
            resultado=relatorio_data,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        relatorio_data['relatorio_id'] = str(auditoria.id)
        
        return relatorio_data

    @staticmethod
    def deletar_relatorio(usuario_id: UUID, relatorio_id: UUID) -> bool:
        """
        Deleta relatório (apenas auditoria, não dados originais).
        
        Args:
            usuario_id: ID do usuário proprietário
            relatorio_id: ID do relatório
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            ValueError: Se relatório não encontrado
        """
        relatorio = AuditoriaRelatorio.query.filter_by(
            id=relatorio_id,
            usuario_id=usuario_id
        ).first()
        
        if not relatorio:
            raise ValueError("Relatório não encontrado")
        
        db.session.delete(relatorio)
        db.session.commit()
        
        return True

    @staticmethod
    def marcar_download(usuario_id: UUID, relatorio_id: UUID) -> Dict:
        """
        Marca relatório como baixado pela primeira vez.
        
        Args:
            usuario_id: ID do usuário
            relatorio_id: ID do relatório
            
        Returns:
            Dict com relatório atualizado
        """
        relatorio = AuditoriaRelatorio.query.filter_by(
            id=relatorio_id,
            usuario_id=usuario_id
        ).first()
        
        if not relatorio:
            raise ValueError("Relatório não encontrado")
        
        if not relatorio.foi_baixado():
            relatorio.marcar_download()
            db.session.commit()
        
        return relatorio.to_dict()

    # ============ MÉTODOS PRIVADOS DE CÁLCULO ============

    @staticmethod
    def _calcular_metricas_portfolio(posicoes: List[Posicao]) -> Dict:
        """Calcula métricas consolidadas do portfolio."""
        total_custo = Decimal('0.00')
        total_valor_atual = Decimal('0.00')
        total_lucro_nao_realizado = Decimal('0.00')
        total_taxas = Decimal('0.00')
        total_impostos = Decimal('0.00')
        
        alocacao_por_classe = {}
        alocacao_por_mercado = {}
        alocacao_por_moeda = {}
        
        for pos in posicoes:
            # Totais
            total_custo += pos.custo_total
            total_valor_atual += pos.valor_atual or Decimal('0.00')
            total_lucro_nao_realizado += pos.lucro_prejuizo_nao_realizado or Decimal('0.00')
            total_taxas += pos.taxas_acumuladas
            total_impostos += pos.impostos_acumulados
            
            # Alocações
            classe = pos.ativo.classe.value if pos.ativo.classe else 'INDEFINIDO'
            mercado = pos.ativo.mercado
            moeda = pos.ativo.moeda
            
            alocacao_por_classe[classe] = alocacao_por_classe.get(classe, Decimal('0.00')) + (pos.valor_atual or Decimal('0.00'))
            alocacao_por_mercado[mercado] = alocacao_por_mercado.get(mercado, Decimal('0.00')) + (pos.valor_atual or Decimal('0.00'))
            alocacao_por_moeda[moeda] = alocacao_por_moeda.get(moeda, Decimal('0.00')) + (pos.valor_atual or Decimal('0.00'))
        
        # Calcular percentuais de alocação
        if total_valor_atual > 0:
            alocacao_por_classe = {k: float((v / total_valor_atual) * 100) for k, v in alocacao_por_classe.items()}
            alocacao_por_mercado = {k: float((v / total_valor_atual) * 100) for k, v in alocacao_por_mercado.items()}
            alocacao_por_moeda = {k: float((v / total_valor_atual) * 100) for k, v in alocacao_por_moeda.items()}
        
        # Rentabilidade total
        rentabilidade_percentual = Decimal('0.00')
        if total_custo > 0:
            rentabilidade_percentual = ((total_valor_atual - total_custo) / total_custo) * 100
        
        return {
            'total_custo': float(total_custo),
            'total_valor_atual': float(total_valor_atual),
            'total_lucro_nao_realizado': float(total_lucro_nao_realizado),
            'rentabilidade_percentual': float(rentabilidade_percentual),
            'total_taxas': float(total_taxas),
            'total_impostos': float(total_impostos),
            'alocacao_por_classe': alocacao_por_classe,
            'alocacao_por_mercado': alocacao_por_mercado,
            'alocacao_por_moeda': alocacao_por_moeda
        }

    @staticmethod
    def _calcular_performance_periodo(
        transacoes: List[Transacao],
        proventos: List[Provento],
        data_inicio: date,
        data_fim: date
    ) -> Dict:
        """Calcula métricas de performance do período."""
        # Totais de transações
        total_compras = Decimal('0.00')
        total_vendas = Decimal('0.00')
        total_taxas_periodo = Decimal('0.00')
        
        for txn in transacoes:
            if txn.tipo_operacao.value == 'COMPRA':
                total_compras += txn.valor_total
            else:  # VENDA
                total_vendas += txn.valor_total
            total_taxas_periodo += txn.taxas
        
        # Totais de proventos
        total_proventos = sum(p.valor_liquido for p in proventos)
        
        # Rentabilidade bruta do período (vendas + proventos - compras)
        fluxo_liquido = total_vendas + total_proventos - total_compras
        
        return {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'total_compras': float(total_compras),
            'total_vendas': float(total_vendas),
            'total_proventos': float(total_proventos),
            'total_taxas': float(total_taxas_periodo),
            'fluxo_liquido': float(fluxo_liquido),
            'num_transacoes': len(transacoes),
            'num_proventos': len(proventos)
        }

    @staticmethod
    def _posicao_to_dict(posicao: Posicao) -> Dict:
        """Converte posição para dict simplificado."""
        return {
            'ativo_ticker': posicao.ativo.ticker,
            'ativo_nome': posicao.ativo.nome,
            'quantidade': float(posicao.quantidade),
            'preco_medio': float(posicao.preco_medio),
            'custo_total': float(posicao.custo_total),
            'valor_atual': float(posicao.valor_atual) if posicao.valor_atual else None,
            'lucro_nao_realizado': float(posicao.lucro_prejuizo_nao_realizado) if posicao.lucro_prejuizo_nao_realizado else None,
            'corretora': posicao.corretora.nome
        }

    @staticmethod
    def _persistir_auditoria(
        usuario_id: UUID,
        tipo_relatorio: str,
        filtros: Dict,
        resultado: Dict,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> AuditoriaRelatorio:
        """Persiste auditoria do relatório gerado."""
        auditoria = AuditoriaRelatorio(
            usuario_id=usuario_id,
            tipo_relatorio=tipo_relatorio,
            data_inicio=data_inicio,
            data_fim=data_fim,
            filtros=filtros,
            resultado_json=resultado,
            formato_export='VISUALIZACAO',
            chave_api_auditoria=str(uuid.uuid4())
        )
        
        db.session.add(auditoria)
        db.session.commit()
        db.session.refresh(auditoria)
        
        return auditoria
