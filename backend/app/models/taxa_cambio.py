# -*- coding: utf-8 -*-
"""Exitus - Model TaxaCambio - Histórico de cotações de moeda"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import db


# Pares de moeda suportados e suas taxas de fallback (relação com BRL)
TAXAS_FALLBACK = {
    'BRL/USD': Decimal('0.18'),
    'BRL/EUR': Decimal('0.17'),
    'BRL/GBP': Decimal('0.14'),
    'BRL/BTC': Decimal('0.000003'),
    'USD/BRL': Decimal('5.60'),
    'EUR/BRL': Decimal('6.00'),
    'GBP/BRL': Decimal('7.10'),
}

MOEDAS_SUPORTADAS = {'BRL', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD'}


class TaxaCambio(db.Model):
    """Histórico de taxas de câmbio entre pares de moedas"""
    __tablename__ = 'taxa_cambio'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    par_moeda = Column(String(7), nullable=False, index=True,
                       comment='Par no formato BASE/COTACAO (ex: BRL/USD)')
    moeda_base = Column(String(3), nullable=False,
                        comment='Moeda base (ex: BRL)')
    moeda_cotacao = Column(String(3), nullable=False,
                           comment='Moeda de cotação (ex: USD)')
    taxa = Column(Numeric(precision=18, scale=8), nullable=False,
                  comment='1 moeda_base = taxa moeda_cotacao')
    data_referencia = Column(Date(), nullable=False, index=True)
    fonte = Column(String(50), nullable=False, default='manual')
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('par_moeda', 'data_referencia', name='uq_taxa_cambio_par_data'),
        Index('ix_taxa_cambio_par_data', 'par_moeda', 'data_referencia'),
    )

    @classmethod
    def get_taxa_atual(cls, par_moeda: str) -> 'TaxaCambio | None':
        """Retorna a cotação mais recente para o par informado"""
        return (
            cls.query
            .filter_by(par_moeda=par_moeda.upper())
            .order_by(cls.data_referencia.desc())
            .first()
        )

    @classmethod
    def get_taxa_na_data(cls, par_moeda: str, data: date) -> 'TaxaCambio | None':
        """Retorna a cotação mais próxima anterior ou igual à data informada"""
        return (
            cls.query
            .filter(
                cls.par_moeda == par_moeda.upper(),
                cls.data_referencia <= data
            )
            .order_by(cls.data_referencia.desc())
            .first()
        )

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'par_moeda': self.par_moeda,
            'moeda_base': self.moeda_base,
            'moeda_cotacao': self.moeda_cotacao,
            'taxa': float(self.taxa),
            'data_referencia': self.data_referencia.isoformat() if self.data_referencia else None,
            'fonte': self.fonte,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<TaxaCambio {self.par_moeda} {self.data_referencia} = {self.taxa}>'
