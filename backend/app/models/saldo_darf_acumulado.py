# -*- coding: utf-8 -*-
"""
Exitus - Model SaldoDarfAcumulado (EXITUS-DARF-ACUMULADO-001)
Armazena saldo de DARF acumulado por categoria e código de receita,
permitindo pagamento quando atingir o mínimo de R$10,00.
"""

from datetime import datetime
from decimal import Decimal
import uuid

from app.database import db


class SaldoDarfAcumulado(db.Model):
    """
    Saldo de DARF acumulado por categoria fiscal e código de receita.
    
    Conforme IN RFB 1.585/2015, DARF com valor inferior a R$10,00
    deve ser acumulado para pagamento em mês seguinte.
    
    Attributes:
        id (UUID): Primary key
        usuario_id (UUID): ID do usuário (FK)
        categoria (str): Categoria fiscal (swing_acoes, day_trade, fiis, exterior, rf)
        codigo_receita (str): Código DARF (6015, 0561, 9453)
        ano_mes (str): Mês de referência no formato YYYY-MM
        saldo (Decimal): Saldo acumulado no mês (>= 0)
        created_at (datetime): Data de criação
        updated_at (datetime): Data de atualização
    """

    __tablename__ = 'saldo_darf_acumulado'

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='ID único do registro'
    )

    usuario_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        comment='ID do usuário proprietário do saldo'
    )

    categoria = db.Column(
        db.String(20),
        nullable=False,
        comment='Categoria fiscal (swing_acoes, day_trade, fiis, exterior, rf)'
    )

    codigo_receita = db.Column(
        db.String(10),
        nullable=False,
        comment='Código de receita do DARF (6015, 0561, 9453)'
    )

    ano_mes = db.Column(
        db.String(7),
        nullable=False,
        comment='Mês de referência no formato YYYY-MM'
    )

    saldo = db.Column(
        db.Numeric(15, 2),
        nullable=False,
        default=Decimal('0'),
        comment='Saldo acumulado no mês (valores < R$10,00)'
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment='Data de criação do registro'
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment='Data da última atualização'
    )

    __table_args__ = (
        db.UniqueConstraint(
            'usuario_id', 'categoria', 'codigo_receita', 'ano_mes',
            name='unique_saldo_darf_usuario_categoria_codigo_mes'
        ),
        db.CheckConstraint(
            "categoria IN ('swing_acoes', 'day_trade', 'fiis', 'exterior', 'rf')",
            name='saldo_darf_categoria_valida'
        ),
        db.CheckConstraint(
            "codigo_receita IN ('6015', '0561', '9453')",
            name='saldo_darf_codigo_receita_valido'
        ),
        db.CheckConstraint(
            'saldo >= 0',
            name='saldo_darf_nao_negativo'
        ),
        {'comment': 'Saldo de DARF acumulado por categoria e código de receita (DARF-ACUMULADO-001)'}
    )

    def __repr__(self):
        return f'<SaldoDarfAcumulado {self.usuario_id} {self.categoria} {self.codigo_receita} {self.ano_mes}: R${self.saldo}>'

    def to_dict(self):
        """Serializa o objeto para dicionário."""
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'categoria': self.categoria,
            'codigo_receita': self.codigo_receita,
            'ano_mes': self.ano_mes,
            'saldo': float(self.saldo),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
