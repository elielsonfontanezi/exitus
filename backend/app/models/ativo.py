# -*- coding: utf-8 -*-
"""Exitus - Model Ativo - Entidade para instrumentos financeiros"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Numeric, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import db

class TipoAtivo(enum.Enum):
    """Enum para tipos de ativo"""
    ACAO = "acao"
    FII = "fii"
    REIT = "reit"
    BOND = "bond"
    ETF = "etf"
    CRIPTO = "cripto"
    OUTRO = "outro"

class ClasseAtivo(enum.Enum):
    """Enum para classes de ativo"""
    RENDA_VARIAVEL = "renda_variavel"
    RENDA_FIXA = "renda_fixa"
    CRIPTO = "cripto"
    HIBRIDO = "hibrido"

class Ativo(db.Model):
    """Model para ativos financeiros"""
    __tablename__ = 'ativos'  # ⬅️ PLURAL
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    nome = Column(String(200), nullable=False, index=True)
    tipo = Column(Enum(TipoAtivo), nullable=False, index=True)
    classe = Column(Enum(ClasseAtivo), nullable=False, index=True)
    
    # Mercado
    mercado = Column(String(10), nullable=False, default='BR', index=True)
    moeda = Column(String(3), nullable=False, default='BRL', index=True)
    
    # Cotação
    preco_atual = Column(Numeric(18, 6), nullable=True)
    data_ultima_cotacao = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Indicadores
    dividend_yield = Column(Numeric(8, 4), nullable=True)
    p_l = Column(Numeric(10, 2), nullable=True)
    p_vp = Column(Numeric(10, 2), nullable=True)
    roe = Column(Numeric(8, 4), nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    deslistado = Column(Boolean, default=False, nullable=False, index=True)
    data_deslistagem = Column(Date, nullable=True)
    
    # Metadados
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Ativo {self.ticker} - {self.nome} ({self.mercado})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "ticker": self.ticker,
            "nome": self.nome,
            "tipo": self.tipo.value if self.tipo else None,
            "classe": self.classe.value if self.classe else None,
            "mercado": self.mercado,
            "moeda": self.moeda,
            "preco_atual": str(self.preco_atual) if self.preco_atual else None,
            "data_ultima_cotacao": self.data_ultima_cotacao.isoformat() if self.data_ultima_cotacao else None,
            "dividend_yield": str(self.dividend_yield) if self.dividend_yield else None,
            "p_l": str(self.p_l) if self.p_l else None,
            "p_vp": str(self.p_vp) if self.p_vp else None,
            "roe": str(self.roe) if self.roe else None,
            "ativo": self.ativo,
            "deslistado": self.deslistado,
            "data_deslistagem": self.data_deslistagem.isoformat() if self.data_deslistagem else None,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
