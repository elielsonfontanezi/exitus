# -*- coding: utf-8 -*-
"""Exitus - Modelo Transacao - Módulo 2 Fase 2.2.4"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import db

class TipoTransacao(enum.Enum):
    """Enum para tipos de transação"""
    COMPRA = "compra"
    VENDA = "venda"
    DIVIDENDO = "dividendo"
    JCP = "jcp"
    BONIFICACAO = "bonificacao"
    DESDOBRAMENTO = "desdobramento"
    GRUPAMENTO = "grupamento"

class Transacao(db.Model):
    """
    Modelo de Transação.
    
    Representa operações financeiras do usuário:
    - Compra/venda de ativos
    - Recebimento de dividendos/JCP
    - Eventos corporativos (bonificação, desdobramento, grupamento)
    """
    __tablename__ = 'transacoes'
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    
    # Relacionamentos
    ativo_id = Column(UUID(as_uuid=True), ForeignKey('ativos.id'), nullable=False)
    corretora_id = Column(UUID(as_uuid=True), ForeignKey('corretoras.id'), nullable=False)
    
    # Dados da transação
    data_transacao = Column(DateTime(timezone=True), nullable=False)
    quantidade = Column(Numeric(18, 8), nullable=False)
    preco_unitario = Column(Numeric(18, 6), nullable=False)
    valor_total = Column(Numeric(18, 2), nullable=False)  # quantidade * preco_unitario
    
    # Custos operacionais
    taxa_corretagem = Column(Numeric(18, 2), nullable=False, default=0)
    taxa_liquidacao = Column(Numeric(18, 2), nullable=False, default=0)
    emolumentos = Column(Numeric(18, 2), nullable=False, default=0)
    imposto = Column(Numeric(18, 2), nullable=False, default=0)
    outros_custos = Column(Numeric(18, 2), nullable=False, default=0)
    
    # Totalizadores
    custos_totais = Column(Numeric(18, 2), nullable=False, default=0)
    valor_liquido = Column(Numeric(18, 2), nullable=False)  # valor_total +/- custos
    
    # Metadados
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (lazy loading)
    usuario = relationship("Usuario", backref="transacoes", lazy=True)
    ativo = relationship("Ativo", backref="transacoes", lazy=True)
    corretora = relationship("Corretora", backref="transacoes", lazy=True)
    
    def __repr__(self):
        return f"<Transacao {self.tipo.value} {self.quantidade} {self.ativo.ticker if self.ativo else '?'} @ {self.data_transacao.date()}>"
    
    def to_dict(self):
        """Serializa transação para dict"""
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "tipo": self.tipo.value,
            "ativo_id": str(self.ativo_id),
            "corretora_id": str(self.corretora_id),
            "data_transacao": self.data_transacao.isoformat(),
            "quantidade": str(self.quantidade),
            "preco_unitario": str(self.preco_unitario),
            "valor_total": str(self.valor_total),
            "taxa_corretagem": str(self.taxa_corretagem),
            "taxa_liquidacao": str(self.taxa_liquidacao),
            "emolumentos": str(self.emolumentos),
            "imposto": str(self.imposto),
            "outros_custos": str(self.outros_custos),
            "custos_totais": str(self.custos_totais),
            "valor_liquido": str(self.valor_liquido),
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
