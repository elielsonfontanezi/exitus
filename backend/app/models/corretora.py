# -*- coding: utf-8 -*-
"""Exitus - Model Corretora"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import db

class TipoCorretora(enum.Enum):
    """Enum para tipos de corretora"""
    CORRETORA = "corretora"
    EXCHANGE = "exchange"

class Corretora(db.Model):
    """Model para corretoras/exchanges"""
    __tablename__ = 'corretora'  # ⬅️ PLURAL
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Dados
    nome = Column(String(100), nullable=False, index=True)
    tipo = Column(Enum(TipoCorretora), default=TipoCorretora.CORRETORA, nullable=False, index=True)
    pais = Column(String(2), nullable=False, default='BR', index=True)
    moeda_padrao = Column(String(3), nullable=False, default='BRL', index=True)
    saldo_atual = Column(Numeric(18, 2), default=0.00, nullable=False)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False, index=True)
    observacoes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    usuario = relationship("Usuario", backref="corretoras", primaryjoin="Corretora.usuario_id == Usuario.id", lazy=True)
    
    def __repr__(self):
        return f"<Corretora {self.nome} ({self.pais})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "nome": self.nome,
            "tipo": self.tipo.value if self.tipo else None,
            "pais": self.pais,
            "moeda_padrao": self.moeda_padrao,
            "saldo_atual": str(self.saldo_atual),
            "ativa": self.ativa,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
