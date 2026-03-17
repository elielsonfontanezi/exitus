# -*- coding: utf-8 -*-
"""M7.1 - ProjecaoRenda Service — GAP EXITUS-SERVICE-REVIEW-001"""
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc

from app.database import db
from app.models.posicao import Posicao
from app.models.projecao_renda import ProjecaoRenda
from app.models.provento import Provento, TipoProvento

logger = logging.getLogger(__name__)


class ProjecaoRendaService:

    @staticmethod
    def list_by_usuario(usuario_id, portfolio_id=None, mes_ano=None):
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        if mes_ano:
            query = query.filter_by(mes_ano=mes_ano)
        return [p.to_dict() for p in query.order_by(desc(ProjecaoRenda.created_at)).all()]

    @staticmethod
    def get_by_mes_ano(usuario_id, mes_ano):
        projecao = ProjecaoRenda.query.filter_by(
            usuario_id=usuario_id, mes_ano=mes_ano
        ).first()
        return projecao.to_dict() if projecao else {}

    @staticmethod
    def calcular_projecao(usuario_id: UUID,
                          meses: int = 12,
                          portfolio_id: Optional[UUID] = None) -> List[Dict]:
        """
        Calcula projeção de renda passiva mensal para os próximos `meses` meses.

        Método:
        - Busca posições do usuário
        - Para cada ativo com dividend_yield: projeta renda mensal = qtd × preco_atual × DY / 12
        - Classifica por tipo de provento predominante via histórico de Provento

        Returns:
            Lista de dicts por mês, com renda_dividendos, renda_jcp, renda_rendimentos, renda_total.
        """
        query = Posicao.query.filter_by(usuario_id=usuario_id)
        posicoes = query.all()

        if not posicoes:
            return []

        # Calcular renda mensal por tipo de provento para cada ativo
        renda_dividendos_mes = Decimal('0')
        renda_jcp_mes = Decimal('0')
        renda_rendimentos_mes = Decimal('0')

        for pos in posicoes:
            ativo = pos.ativo
            if not ativo or not ativo.dividend_yield:
                continue

            preco = Decimal(str(ativo.preco_atual or pos.preco_medio or 0))
            qtd = Decimal(str(pos.quantidade or 0))
            dy_anual = Decimal(str(ativo.dividend_yield))

            renda_anual_ativo = qtd * preco * dy_anual
            renda_mensal_ativo = renda_anual_ativo / Decimal('12')

            # Determinar tipo predominante via histórico de proventos
            tipo_predominante = ProjecaoRendaService._tipo_provento_predominante(ativo.id)

            if tipo_predominante == TipoProvento.JCP:
                renda_jcp_mes += renda_mensal_ativo
            elif tipo_predominante in (TipoProvento.RENDIMENTO, TipoProvento.CUPOM):
                renda_rendimentos_mes += renda_mensal_ativo
            else:
                renda_dividendos_mes += renda_mensal_ativo

        renda_total_mes = renda_dividendos_mes + renda_jcp_mes + renda_rendimentos_mes

        # Gerar projeção para cada mês futuro
        hoje = date.today()
        resultado = []
        for i in range(meses):
            mes = hoje.month + i
            ano = hoje.year + (mes - 1) // 12
            mes = ((mes - 1) % 12) + 1
            mes_ano_str = f"{ano:04d}-{mes:02d}"

            resultado.append({
                'mes_ano': mes_ano_str,
                'renda_dividendos_projetada': round(float(renda_dividendos_mes), 2),
                'renda_jcp_projetada': round(float(renda_jcp_mes), 2),
                'renda_rendimentos_projetada': round(float(renda_rendimentos_mes), 2),
                'renda_total_mes': round(float(renda_total_mes), 2),
                'renda_anual_projetada': round(float(renda_total_mes * 12), 2),
            })

        return resultado

    @staticmethod
    def _tipo_provento_predominante(ativo_id: UUID) -> TipoProvento:
        """Retorna o tipo de provento mais comum para o ativo nos últimos 12 meses."""
        from sqlalchemy import func
        resultado = (
            db.session.query(
                Provento.tipo_provento,
                func.count(Provento.id).label('total')
            )
            .filter(Provento.ativo_id == ativo_id)
            .group_by(Provento.tipo_provento)
            .order_by(func.count(Provento.id).desc())
            .first()
        )
        if resultado:
            return resultado.tipo_provento
        return TipoProvento.DIVIDENDO

    @staticmethod
    def create_or_update(usuario_id, data):
        """Persiste ou atualiza projeção calculada."""
        mes_ano = data.get('mes_ano')
        portfolio_id = data.get('portfolio_id')

        existing = ProjecaoRenda.query.filter_by(
            usuario_id=usuario_id,
            mes_ano=mes_ano,
            portfolio_id=portfolio_id,
        ).first()

        if existing:
            for campo in ('renda_dividendos_projetada', 'renda_jcp_projetada',
                          'renda_rendimentos_projetada', 'renda_total_mes',
                          'renda_anual_projetada'):
                if campo in data:
                    setattr(existing, campo, data[campo])
            db.session.commit()
            db.session.refresh(existing)
            return existing.to_dict()

        projecao = ProjecaoRenda(usuario_id=usuario_id, **data)
        db.session.add(projecao)
        db.session.commit()
        db.session.refresh(projecao)
        return projecao.to_dict()
