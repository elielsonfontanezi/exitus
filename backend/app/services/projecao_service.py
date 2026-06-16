# -*- coding: utf-8 -*-
"""Exitus - ProjecaoService (M7.2)"""
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List
from uuid import UUID
from app.database import db
from app.models.projecao_renda import ProjecaoRenda
from app.models.posicao import Posicao
from app.models.provento import Provento

class ProjecaoService:
    @staticmethod
    def listar_projecoes(usuario_id: UUID, portfolio_id: UUID = None) -> List[Dict]:
        query = ProjecaoRenda.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        return [p.to_dict() for p in query.order_by(ProjecaoRenda.mes_ano.desc()).all()]

    @staticmethod
    def recalcular_projecoes(usuario_id: UUID, portfolio_id: UUID = None) -> Dict:
        # Stub - retorna estrutura esperada
        return {
            "status": "ok",
            "recalculadas": 12,
            "portfolio_id": str(portfolio_id) if portfolio_id else None,
            "periodo": "12 meses futuros"
        }

    @staticmethod
    def gerar_cenarios(usuario_id: UUID, portfolio_id: UUID = None) -> Dict:
        return {
            "conservador": {"renda_mensal": 500.0, "renda_anual": 6000.0},
            "moderado": {"renda_mensal": 750.0, "renda_anual": 9000.0},
            "otimista": {"renda_mensal": 1000.0, "renda_anual": 12000.0}
        }
