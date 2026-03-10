# -*- coding: utf-8 -*-
"""
Exitus - CalendarioDividendoService
Serviço para gerenciar calendário de dividendos futuros
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
import calendar

from app.database import db
from app.models.calendario_dividendo import CalendarioDividendo
from app.models.ativo import Ativo
from app.models.provento import Provento, TipoProvento
from app.models.posicao import Posicao


class CalendarioDividendoService:
    """Serviço para gerenciamento de calendário de dividendos"""
    
    @staticmethod
    def gerar_calendario(usuario_id: str, meses_futuros: int = 12) -> List[CalendarioDividendo]:
        """
        Gera calendário de dividendos para os próximos N meses
        
        Args:
            usuario_id: ID do usuário
            meses_futuros: Quantidade de meses futuros a considerar
            
        Returns:
            Lista de CalendarioDividendo gerados
        """
        # Obter posições atuais do usuário
        posicoes = Posicao.query.filter(
            Posicao.usuario_id == usuario_id,
            Posicao.quantidade > 0
        ).all()
        
        calendario = []
        
        for posicao in posicoes:
            # Gerar calendário para este ativo
            calendario_ativo = CalendarioDividendoService._gerar_calendario_ativo(
                posicao.ativo, posicao.quantidade, usuario_id, meses_futuros
            )
            calendario.extend(calendario_ativo)
        
        # Ordenar por data
        calendario.sort(key=lambda x: x.data_esperada)
        
        return calendario
    
    @staticmethod
    def _gerar_calendario_ativo(ativo: Ativo, quantidade: int, usuario_id: str, 
                              meses_futuros: int) -> List[CalendarioDividendo]:
        """
        Gera calendário de dividendos para um ativo específico
        
        Args:
            ativo: Ativo para gerar calendário
            quantidade: Quantidade de ativos
            usuario_id: ID do usuário
            meses_futuros: Meses futuros a considerar
            
        Returns:
            Lista de CalendarioDividendo para o ativo
        """
        calendario = []
        
        # Obter histórico de proventos para determinar padrão
        proventos_historicos = Provento.query.filter_by(
            ativo_id=ativo.id,
            tipo_provento=TipoProvento.DIVIDENDO
        ).order_by(Provento.data_pagamento.desc()).limit(12).all()
        
        if not proventos_historicos:
            # Sem histórico, não gerar calendário
            return calendario
        
        # Analisar padrão de pagamento
        meses_pagamento = CalendarioDividendoService._analisar_padrao_pagamento(
            proventos_historicos
        )
        
        # Gerar proventos futuros baseados no padrão
        data_base = date.today()
        
        for i in range(meses_futuros):
            data_provento = CalendarioDividendoService._proxima_data_pagamento(
                data_base, i, meses_pagamento
            )
            
            if data_provento:
                # Calcular valor estimado
                valor_estimado = CalendarioDividendoService._calcular_valor_estimado(
                    ativo, quantidade, proventos_historicos
                )
                
                # Criar calendário
                calendario_item = CalendarioDividendo(
                    ativo_id=ativo.id,
                    usuario_id=usuario_id,
                    data_esperada=data_provento,
                    tipo_provento='dividendo',
                    valor_estimado=valor_estimado,
                    quantidade=quantidade,
                    status='previsto'
                )
                
                calendario.append(calendario_item)
        
        return calendario
    
    @staticmethod
    def _analisar_padrao_pagamento(proventos: List[Provento]) -> List[int]:
        """
        Analisa histórico para determinar meses de pagamento
        
        Args:
            proventos: Lista de proventos históricos
            
        Returns:
            Lista de meses (1-12) em que o ativo paga dividendos
        """
        meses_pagamento = set()
        
        for provento in proventos:
            if provento.data_pagamento:
                meses_pagamento.add(provento.data_pagamento.month)
        
        return sorted(list(meses_pagamento))
    
    @staticmethod
    def _proxima_data_pagamento(data_base: date, meses_a_frente: int, 
                              meses_pagamento: List[int]) -> Optional[date]:
        """
        Calcula próxima data de pagamento baseada no padrão
        
        Args:
            data_base: Data base para cálculo
            meses_a_frente: Quantos meses à frente
            meses_pagamento: Meses em que ocorre pagamento
            
        Returns:
            Próxima data de pagamento ou None
        """
        if not meses_pagamento:
            return None
        
        # Calcular mês alvo
        mes_alvo = ((data_base.month - 1 + meses_a_frente) % 12) + 1
        ano_alvo = data_base.year + ((data_base.month - 1 + meses_a_frente) // 12)
        
        # Verificar se o ativo paga neste mês
        if mes_alvo in meses_pagamento:
            # Útil dia útil do mês
            ultimo_dia = calendar.monthrange(ano_alvo, mes_alvo)[1]
            data_pagamento = date(ano_alvo, mes_alvo, min(ultimo_dia, 15))
            
            # Ajustar para dia útil (não final de semana)
            while data_pagamento.weekday() >= 5:  # Sábado=5, Domingo=6
                data_pagamento -= timedelta(days=1)
            
            return data_pagamento
        
        return None
    
    @staticmethod
    def _calcular_valor_estimado(ativo: Ativo, quantidade: int, 
                               proventos_historicos: List[Provento]) -> Optional[Decimal]:
        """
        Calcula valor estimado do próximo dividendo
        
        Args:
            ativo: Ativo para cálculo
            quantidade: Quantidade de ativos
            proventos_historicos: Histórico de proventos
            
        Returns:
            Valor estimado ou None
        """
        if not proventos_historicos:
            return None
        
        # Média dos últimos 3 proventos
        ultimos_proventos = proventos_historicos[:3]
        
        if not ultimos_proventos:
            return None
        
        total_valor_por_acao = sum(
            float(p.valor_por_acao or 0) for p in ultimos_proventos 
            if p.valor_por_acao
        )
        
        if total_valor_por_acao == 0:
            return None
        
        media_valor_por_acao = total_valor_por_acao / len(ultimos_proventos)
        
        # Aplicar yield estimado do ativo se disponível
        yield_estimado = float(ativo.dividend_yield or 0)
        
        if yield_estimado > 0:
            # Usar yield como referência
            preco_atual = float(ativo.preco_atual or 0)
            if preco_atual > 0:
                valor_por_yield = (preco_atual * yield_estimado / 100) / 4  # Trimestral
                media_valor_por_acao = max(media_valor_por_acao, valor_por_yield)
        
        return Decimal(str(media_valor_por_acao * quantidade))
    
    @staticmethod
    def criar_calendario(calendario_data: Dict[str, Any]) -> CalendarioDividendo:
        """
        Cria um novo item no calendário
        
        Args:
            calendario_data: Dados do calendário
            
        Returns:
            CalendarioDividendo criado
        """
        calendario = CalendarioDividendo(**calendario_data)
        
        db.session.add(calendario)
        db.session.commit()
        
        return calendario
    
    @staticmethod
    def listar_calendario(usuario_id: str, data_inicio: Optional[date] = None,
                         data_fim: Optional[date] = None, 
                         ativo_id: Optional[str] = None) -> List[CalendarioDividendo]:
        """
        Lista calendário de dividendos com filtros
        
        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial (opcional)
            data_fim: Data final (opcional)
            ativo_id: ID do ativo (opcional)
            
        Returns:
            Lista de CalendarioDividendo
        """
        query = CalendarioDividendo.query.filter_by(usuario_id=usuario_id)
        
        if data_inicio:
            query = query.filter(CalendarioDividendo.data_esperada >= data_inicio)
        
        if data_fim:
            query = query.filter(CalendarioDividendo.data_esperada <= data_fim)
        
        if ativo_id:
            query = query.filter(CalendarioDividendo.ativo_id == ativo_id)
        
        return query.order_by(CalendarioDividendo.data_esperada.asc()).all()
    
    @staticmethod
    def atualizar_calendario(calendario_id: str, dados: Dict[str, Any]) -> Optional[CalendarioDividendo]:
        """
        Atualiza um item do calendário
        
        Args:
            calendario_id: ID do calendário
            dados: Dados para atualizar
            
        Returns:
            CalendarioDividendo atualizado ou None
        """
        calendario = CalendarioDividendo.query.get(calendario_id)
        
        if not calendario:
            return None
        
        # Atualizar campos permitidos
        campos_permitidos = [
            'data_esperada', 'tipo_provento', 'yield_estimado', 
            'valor_estimado', 'quantidade', 'status', 'observacoes',
            'data_pagamento', 'valor_real'
        ]
        
        for campo, valor in dados.items():
            if campo in campos_permitidos and hasattr(calendario, campo):
                setattr(calendario, campo, valor)
        
        calendario.updated_at = datetime.utcnow()
        db.session.commit()
        
        return calendario
    
    @staticmethod
    def excluir_calendario(calendario_id: str) -> bool:
        """
        Exclui um item do calendário
        
        Args:
            calendario_id: ID do calendário
            
        Returns:
            True se excluído, False se não encontrado
        """
        calendario = CalendarioDividendo.query.get(calendario_id)
        
        if not calendario:
            return False
        
        db.session.delete(calendario)
        db.session.commit()
        
        return True
    
    @staticmethod
    def confirmar_pagamento(calendario_id: str, data_pagamento: date, 
                          valor_real: Decimal) -> Optional[CalendarioDividendo]:
        """
        Confirma pagamento de dividendo
        
        Args:
            calendario_id: ID do calendário
            data_pagamento: Data real do pagamento
            valor_real: Valor real pago
            
        Returns:
            CalendarioDividendo atualizado ou None
        """
        calendario = CalendarioDividendo.query.get(calendario_id)
        
        if not calendario:
            return None
        
        calendario.confirmar_pagamento(data_pagamento, valor_real)
        db.session.commit()
        
        return calendario
