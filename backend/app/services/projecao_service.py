# -*- coding: utf-8 -*-
"""Exitus - ProjecaoService (M7.2) — NEW-17 enriquecido."""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta

from app.database import db
from app.models.projecao_renda import ProjecaoRenda
from app.services.provento_service import ProventoService


class ProjecaoService:
    @staticmethod
    def _media_mensal_proventos(usuario_id: UUID) -> float:
        """Média mensal de proventos líquidos nos últimos 12 meses."""
        hoje = date.today()
        inicio = hoje - relativedelta(months=12)
        proventos = ProventoService.get_recebidos_usuario(
            usuario_id, data_inicio=inicio, data_fim=hoje
        )
        if not proventos:
            return 0.0

        totais_por_mes: Dict[str, float] = {}
        for p in proventos:
            dp = p.get('data_pagamento', '')[:7]
            if not dp:
                continue
            totais_por_mes[dp] = totais_por_mes.get(dp, 0.0) + float(
                p.get('valor_liquido_recebido', 0)
            )

        if not totais_por_mes:
            total = sum(float(p.get('valor_liquido_recebido', 0)) for p in proventos)
            return round(total / 12.0, 2)

        media = sum(totais_por_mes.values()) / max(len(totais_por_mes), 1)
        return round(media, 2)

    @staticmethod
    def _cenario_dict(renda_mensal: float, fator: float) -> Dict:
        mensal = round(renda_mensal * fator, 2)
        return {
            'renda_mensal': mensal,
            'renda_anual': round(mensal * 12, 2),
        }

    @staticmethod
    def listar_projecoes(usuario_id: UUID, portfolio_id: UUID = None) -> List[Dict]:
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        return [p.to_dict() for p in query.order_by(ProjecaoRenda.mes_ano.asc()).all()]

    @staticmethod
    def recalcular_projecoes(usuario_id: UUID, portfolio_id: UUID = None) -> Dict:
        """Persiste 12 meses futuros com base na média mensal de proventos."""
        media = ProjecaoService._media_mensal_proventos(usuario_id)
        hoje = date.today()
        recalculadas = 0

        for i in range(1, 13):
            ref = hoje + relativedelta(months=i)
            mes_ano = ref.strftime('%Y-%m')
            renda = Decimal(str(round(media, 2)))

            filtros = {'usuario_id': usuario_id, 'mes_ano': mes_ano}
            if portfolio_id:
                filtros['portfolio_id'] = portfolio_id
            else:
                filtros['portfolio_id'] = None

            existente = ProjecaoRenda.query.filter_by(**filtros).first()
            if existente:
                existente.renda_dividendos_projetada = renda
                existente.renda_total_mes = renda
                existente.renda_anual_projetada = renda * 12
                existente.updated_at = datetime.utcnow()
            else:
                registro = ProjecaoRenda(
                    usuario_id=usuario_id,
                    portfolio_id=portfolio_id,
                    mes_ano=mes_ano,
                    renda_dividendos_projetada=renda,
                    renda_jcp_projetada=Decimal('0'),
                    renda_rendimentos_projetada=Decimal('0'),
                    renda_total_mes=renda,
                    renda_anual_projetada=renda * 12,
                )
                db.session.add(registro)
            recalculadas += 1

        db.session.commit()
        return {
            'status': 'ok',
            'recalculadas': recalculadas,
            'portfolio_id': str(portfolio_id) if portfolio_id else None,
            'periodo': '12 meses futuros',
            'media_mensal_base': media,
        }

    @staticmethod
    def gerar_cenarios(usuario_id: UUID, portfolio_id: UUID = None) -> Dict:
        media = ProjecaoService._media_mensal_proventos(usuario_id)
        return {
            'media_mensal_historica': media,
            'portfolio_id': str(portfolio_id) if portfolio_id else None,
            'conservador': ProjecaoService._cenario_dict(media, 0.8),
            'moderado': ProjecaoService._cenario_dict(media, 1.0),
            'otimista': ProjecaoService._cenario_dict(media, 1.2),
        }
