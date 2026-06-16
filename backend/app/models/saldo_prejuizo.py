# -*- coding: utf-8 -*-
"""
Exitus - Model SaldoPrejuizo (EXITUS-IR-003)
Armazena saldo de prejuízo acumulado por categoria fiscal, permitindo
compensação entre meses conforme IN RFB 1.585/2015.

Categorias: swing_acoes, day_trade, fiis, exterior
Regra: prejuízo de um mês pode ser compensado contra lucros futuros
da MESMA categoria (swing × swing, day-trade × day-trade, etc.)
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, DateTime, Numeric, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class SaldoPrejuizo(db.Model):
    """
    Saldo de prejuízo acumulado por categoria fiscal e mês.

    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário
        categoria (str): Categoria fiscal (swing_acoes, day_trade, fiis, exterior)
        ano_mes (str): Mês de referência no formato 'YYYY-MM'
        saldo (Decimal): Saldo de prejuízo acumulado (positivo = prejuízo a compensar)
        created_at (datetime): Data de criação
        updated_at (datetime): Data de atualização
    """

    __tablename__ = 'saldo_prejuizo'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único"
    )

    usuario_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID do usuário"
    )
    
    assessora_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('assessora.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="ID da assessora (multi-tenancy)"
    )

    categoria = db.Column(
        String(20),
        nullable=False,
        comment="Categoria fiscal: swing_acoes, day_trade, fiis, exterior"
    )

    ano_mes = db.Column(
        String(7),
        nullable=False,
        comment="Mês de referência (YYYY-MM)"
    )

    saldo = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Saldo de prejuízo acumulado (positivo = prejuízo a compensar)"
    )

    created_at = db.Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relacionamentos
    assessora = relationship('Assessora', back_populates='saldos_prejuizo')
    usuario = relationship('Usuario', backref='saldos_prejuizo', lazy='joined')

    __table_args__ = (
        UniqueConstraint(
            'usuario_id', 'categoria', 'ano_mes',
            name='unique_saldo_prejuizo_usuario_categoria_mes'
        ),
        CheckConstraint(
            "categoria IN ('swing_acoes', 'day_trade', 'fiis', 'exterior')",
            name='saldo_prejuizo_categoria_valida'
        ),
        CheckConstraint(
            "saldo >= 0",
            name='saldo_prejuizo_nao_negativo'
        ),
        {'comment': 'Saldo de prejuízo acumulado por categoria fiscal (IR-003)'}
    )

    def __repr__(self):
        return f'<SaldoPrejuizo {self.usuario_id} {self.categoria} {self.ano_mes}: R${self.saldo}>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'categoria': self.categoria,
            'ano_mes': self.ano_mes,
            'saldo': float(self.saldo),
        }
