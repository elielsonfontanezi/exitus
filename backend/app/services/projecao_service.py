# -*- coding: utf-8 -*-
"""
Exitus - ProjecaoService (M7.2)
Service para projeções de renda passiva
"""

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID
import calendar

from sqlalchemy import func, and_, extract

from app.database import db
from app.models.projecao_renda import ProjecaoRenda
from app.models.posicao import Posicao
from app.models.provento import Provento
from app.models.ativo import Ativo


class ProjecaoService:
    """Service para projeções de renda passiva."""

    @staticmethod
    def listar_projecoes(
        usuario_id: UUID,
        portfolio_id: Optional[UUID] = None,
        meses: int = 12
    ) -> List[Dict]:
        """
        Lista projeções de renda do usuário.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: Filtrar por portfolio específico (opcional)
            meses: Número de meses a retornar (default: 12)
            
        Returns:
            Lista de projeções ordenadas por mês/ano
        """
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        
        # Buscar projeções dos últimos N meses
        data_limite = datetime.utcnow() - relativedelta(months=meses)
        
        projecoes = query.order_by(ProjecaoRenda.mes_ano.desc()).limit(meses).all()
        
        return [p.to_dict() for p in projecoes]

    @staticmethod
    def obter_projecao(usuario_id: UUID, projecao_id: UUID) -> Dict:
        """
        Obtém projeção específica por ID.
        
        Args:
            usuario_id: ID do usuário
            projecao_id: ID da projeção
            
        Returns:
            Dict com dados da projeção
            
        Raises:
            ValueError: Se projeção não encontrada
        """
        projecao = ProjecaoRenda.query.filter_by(
            id=projecao_id,
            usuario_id=usuario_id
        ).first()
        
        if not projecao:
            raise ValueError("Projeção não encontrada")
        
        return projecao.to_dict()

    @staticmethod
    def calcular_projecao_renda(
        usuario_id: UUID,
        portfolio_id: Optional[UUID] = None,
        meses_projecao: int = 12,
        taxa_crescimento_anual: Optional[Decimal] = None
    ) -> Dict:
        """
        Calcula projeção de renda passiva para os próximos N meses.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio (None = todos)
            meses_projecao: Número de meses a projetar (default: 12)
            taxa_crescimento_anual: Taxa de crescimento esperada em % (opcional)
            
        Returns:
            Dict com projeções calculadas
        """
        # Taxa de crescimento padrão: 5% ao ano
        if taxa_crescimento_anual is None:
            taxa_crescimento_anual = Decimal('5.0')
        
        # Taxa mensal
        taxa_mensal = (taxa_crescimento_anual / 100) / 12
        
        # Buscar posições ativas
        query_posicoes = Posicao.query.filter_by(usuario_id=usuario_id)\
            .filter(Posicao.quantidade > 0)\
            .join(Ativo)
        
        if portfolio_id:
            query_posicoes = query_posicoes.filter_by(portfolio_id=portfolio_id)
        
        posicoes = query_posicoes.all()
        
        if not posicoes:
            return {
                'status': 'sem_posicoes',
                'mensagem': 'Nenhuma posição ativa encontrada',
                'projecoes': []
            }
        
        # Calcular média mensal de proventos dos últimos 12 meses
        historico_proventos = ProjecaoService._obter_historico_proventos(
            usuario_id, portfolio_id, meses=12
        )
        
        # Gerar projeções mensais
        projecoes = []
        data_base = datetime.utcnow().date()
        
        for mes_offset in range(1, meses_projecao + 1):
            data_projecao = data_base + relativedelta(months=mes_offset)
            mes_ano = data_projecao.strftime('%Y-%m')
            
            # Calcular renda projetada com crescimento
            fator_crescimento = (1 + taxa_mensal) ** mes_offset
            
            renda_dividendos = historico_proventos['dividendos_medio_mensal'] * fator_crescimento
            renda_jcp = historico_proventos['jcp_medio_mensal'] * fator_crescimento
            renda_rendimentos = historico_proventos['rendimentos_medio_mensal'] * fator_crescimento
            
            renda_total = renda_dividendos + renda_jcp + renda_rendimentos
            
            projecoes.append({
                'mes_ano': mes_ano,
                'renda_dividendos_projetada': float(renda_dividendos),
                'renda_jcp_projetada': float(renda_jcp),
                'renda_rendimentos_projetada': float(renda_rendimentos),
                'renda_total_mes': float(renda_total),
                'ativos_contribuindo': len(posicoes)
            })
        
        # Calcular renda anual projetada
        renda_anual = sum(p['renda_total_mes'] for p in projecoes)
        
        return {
            'status': 'success',
            'usuario_id': str(usuario_id),
            'portfolio_id': str(portfolio_id) if portfolio_id else None,
            'taxa_crescimento_anual': float(taxa_crescimento_anual),
            'meses_projecao': meses_projecao,
            'renda_anual_projetada': renda_anual,
            'historico_base': {
                'dividendos_medio_mensal': float(historico_proventos['dividendos_medio_mensal']),
                'jcp_medio_mensal': float(historico_proventos['jcp_medio_mensal']),
                'rendimentos_medio_mensal': float(historico_proventos['rendimentos_medio_mensal'])
            },
            'projecoes': projecoes
        }

    @staticmethod
    def recalcular_projecoes(
        usuario_id: UUID,
        portfolio_id: Optional[UUID] = None
    ) -> Dict:
        """
        Recalcula e persiste projeções no banco.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio (opcional)
            
        Returns:
            Dict com resultado da operação
        """
        # Calcular novas projeções
        resultado = ProjecaoService.calcular_projecao_renda(
            usuario_id=usuario_id,
            portfolio_id=portfolio_id,
            meses_projecao=12
        )
        
        if resultado['status'] != 'success':
            return resultado
        
        # Deletar projeções antigas deste portfolio
        query_delete = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query_delete = query_delete.filter_by(portfolio_id=portfolio_id)
        
        query_delete.delete()
        
        # Persistir novas projeções
        projecoes_criadas = []
        for proj_data in resultado['projecoes']:
            projecao = ProjecaoRenda(
                usuario_id=usuario_id,
                portfolio_id=portfolio_id,
                mes_ano=proj_data['mes_ano'],
                renda_dividendos_projetada=Decimal(str(proj_data['renda_dividendos_projetada'])),
                renda_jcp_projetada=Decimal(str(proj_data['renda_jcp_projetada'])),
                renda_rendimentos_projetada=Decimal(str(proj_data['renda_rendimentos_projetada'])),
                renda_total_mes=Decimal(str(proj_data['renda_total_mes'])),
                renda_anual_projetada=Decimal(str(resultado['renda_anual_projetada'])),
                ativos_contribuindo=proj_data['ativos_contribuindo']
            )
            db.session.add(projecao)
            projecoes_criadas.append(projecao)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'mensagem': f'{len(projecoes_criadas)} projeções criadas/atualizadas',
            'renda_anual_projetada': resultado['renda_anual_projetada'],
            'projecoes': [p.to_dict() for p in projecoes_criadas]
        }

    @staticmethod
    def gerar_cenarios(
        usuario_id: UUID,
        portfolio_id: Optional[UUID] = None
    ) -> Dict:
        """
        Gera cenários de projeção (conservador, moderado, otimista).
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio (opcional)
            
        Returns:
            Dict com 3 cenários de projeção
        """
        cenarios = {
            'conservador': ProjecaoService.calcular_projecao_renda(
                usuario_id, portfolio_id, meses_projecao=12, taxa_crescimento_anual=Decimal('2.0')
            ),
            'moderado': ProjecaoService.calcular_projecao_renda(
                usuario_id, portfolio_id, meses_projecao=12, taxa_crescimento_anual=Decimal('5.0')
            ),
            'otimista': ProjecaoService.calcular_projecao_renda(
                usuario_id, portfolio_id, meses_projecao=12, taxa_crescimento_anual=Decimal('8.0')
            )
        }
        
        return {
            'status': 'success',
            'usuario_id': str(usuario_id),
            'portfolio_id': str(portfolio_id) if portfolio_id else None,
            'cenarios': cenarios
        }

    @staticmethod
    def obter_projecao_por_mes(
        usuario_id: UUID,
        mes_ano: str,
        portfolio_id: Optional[UUID] = None
    ) -> Dict:
        """
        Obtém projeção de um mês específico.
        
        Args:
            usuario_id: ID do usuário
            mes_ano: Mês/ano no formato 'YYYY-MM'
            portfolio_id: ID do portfolio (opcional)
            
        Returns:
            Dict com projeção do mês
            
        Raises:
            ValueError: Se projeção não encontrada
        """
        query = ProjecaoRenda.query.filter_by(
            usuario_id=usuario_id,
            mes_ano=mes_ano
        )
        
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        
        projecao = query.first()
        
        if not projecao:
            raise ValueError(f"Projeção para {mes_ano} não encontrada")
        
        return projecao.to_dict()

    # ============ MÉTODOS PRIVADOS ============

    @staticmethod
    def _obter_historico_proventos(
        usuario_id: UUID,
        portfolio_id: Optional[UUID],
        meses: int = 12
    ) -> Dict:
        """
        Calcula média mensal de proventos dos últimos N meses.
        
        Args:
            usuario_id: ID do usuário
            portfolio_id: ID do portfolio (opcional)
            meses: Número de meses a analisar
            
        Returns:
            Dict com médias por tipo de provento
        """
        data_limite = datetime.utcnow() - relativedelta(months=meses)
        
        # Query base de proventos pagos
        query = Provento.query.filter(
            Provento.usuario_id == usuario_id,
            Provento.data_pagamento >= data_limite.date(),
            Provento.status_pagamento == 'PAGO'
        )
        
        if portfolio_id:
            # Filtrar por ativos do portfolio
            query = query.join(Ativo).join(Posicao).filter(
                Posicao.portfolio_id == portfolio_id
            )
        
        proventos = query.all()
        
        # Agrupar por tipo
        total_dividendos = Decimal('0.00')
        total_jcp = Decimal('0.00')
        total_rendimentos = Decimal('0.00')
        
        for prov in proventos:
            tipo = prov.tipo_provento.value if hasattr(prov.tipo_provento, 'value') else prov.tipo_provento
            
            if tipo == 'DIVIDENDO':
                total_dividendos += prov.valor_liquido
            elif tipo == 'JCP':
                total_jcp += prov.valor_liquido
            elif tipo == 'RENDIMENTO':
                total_rendimentos += prov.valor_liquido
        
        # Calcular médias mensais
        divisor = Decimal(str(meses)) if meses > 0 else Decimal('1')
        
        return {
            'dividendos_medio_mensal': total_dividendos / divisor,
            'jcp_medio_mensal': total_jcp / divisor,
            'rendimentos_medio_mensal': total_rendimentos / divisor,
            'total_proventos_periodo': len(proventos),
            'meses_analisados': meses
        }
