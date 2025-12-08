# -*- coding: utf-8 -*-
"""
Exitus - ProjecaoRendaService
Service para projeções de renda passiva
"""
from decimal import Decimal
from typing import Dict, List
from sqlalchemy.orm import Session
from app.database import db
from app.models import Usuario, ProjecaoRenda

class ProjecaoRendaService:
    """Service para projeções de renda mensal/anual"""
    
    @staticmethod
    def calcular_projecao(
        usuario_id: str,
        portfolio_id: str = None,
        mes_ano: str = None  # '2025-12'
    ) -> ProjecaoRenda:
        """Calcula projeção de renda para mês/ano específico"""
        # Lógica de cálculo simplificada (implementar com dados reais)
        projecao = ProjecaoRenda(
            usuario_id=usuario_id,
            portfolio_id=portfolio_id,
            mes_ano=mes_ano or '2025-12',
            renda_dividendos_projetada=Decimal('1500.50'),
            renda_jcp_projetada=Decimal('850.25'),
            renda_rendimentos_projetada=Decimal('3200.00'),
            renda_total_mes=Decimal('5550.75'),
            renda_anual_projetada=Decimal('66609.00')
        )
        db.session.add(projecao)
        db.session.commit()
        return projecao
    
    @staticmethod
    def listar_projecoes(usuario_id: str) -> List[Dict]:
        """Lista projeções do usuário"""
        return (db.session.query(ProjecaoRenda)
               .filter_by(usuario_id=usuario_id)
               .order_by(ProjecaoRenda.mes_ano.desc())
               .all())
