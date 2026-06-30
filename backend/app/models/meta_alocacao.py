# -*- coding: utf-8 -*-
"""
Exitus - Model MetaAlocacao — REBALANCE-001

Persiste a meta percentual por classe de ativo (renda_variavel / renda_fixa / cripto)
definida pelo usuário. Usada por rebalance_service para calcular desvios e sugestões.

Campo percentual_target: 0–100 (% do patrimônio total)
Campo tolerancia_pct: desvio aceitável em pp antes de sinalizar (default 2%)
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import db


CLASSES_VALIDAS = ('renda_variavel', 'renda_fixa', 'cripto')


class MetaAlocacao(db.Model):
    __tablename__ = 'meta_alocacao'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment='Identificador único')
    usuario_id = Column(UUID(as_uuid=True),
                        ForeignKey('usuario.id', ondelete='CASCADE'),
                        nullable=False, index=True,
                        comment='Usuário proprietário')
    assessora_id = Column(UUID(as_uuid=True),
                          ForeignKey('assessora.id', ondelete='CASCADE'),
                          nullable=True, index=True,
                          comment='Assessora (multi-tenancy)')
    classe = Column(String(30), nullable=False,
                    comment='renda_variavel | renda_fixa | cripto')
    percentual_target = Column(Numeric(5, 2), nullable=False,
                               comment='% alvo desta classe (0–100)')
    tolerancia_pct = Column(Numeric(4, 2), nullable=False, default=2.00,
                            comment='Tolerância em pp (default 2%)')
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship('Usuario', backref='metas_alocacao')
    assessora = relationship('Assessora', backref='metas_alocacao')

    __table_args__ = (
        UniqueConstraint('usuario_id', 'classe', name='uq_meta_alocacao_usuario_classe'),
        CheckConstraint('percentual_target >= 0 AND percentual_target <= 100',
                        name='chk_meta_alocacao_percentual_valido'),
        CheckConstraint('tolerancia_pct >= 0 AND tolerancia_pct <= 50',
                        name='chk_meta_alocacao_tolerancia_valida'),
        CheckConstraint("classe IN ('renda_variavel', 'renda_fixa', 'cripto')",
                        name='chk_meta_alocacao_classe_valida'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'classe': self.classe,
            'percentual_target': float(self.percentual_target),
            'tolerancia_pct': float(self.tolerancia_pct),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
