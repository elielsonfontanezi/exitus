# -*- coding: utf-8 -*-
"""
Exitus - Assessora Model
Model para assessoras de investimento (multi-tenancy)
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import db


class Assessora(db.Model):
    """
    Model para Assessoras de Investimento
    Implementa multi-tenancy: cada assessora tem seus próprios usuários, portfolios, etc.
    """
    
    __tablename__ = "assessora"
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    nome = Column(String(200), nullable=False, unique=True)
    razao_social = Column(String(200), nullable=True)
    cnpj = Column(String(18), nullable=True, unique=True)
    
    # Contato
    email = Column(String(120), nullable=False, unique=True)
    telefone = Column(String(20), nullable=True)
    site = Column(String(200), nullable=True)
    
    # Endereço
    endereco = Column(Text, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(9), nullable=True)
    
    # Certificações e Regulamentação
    numero_cvm = Column(String(50), nullable=True)  # Número de registro na CVM
    anbima = Column(Boolean, default=False)  # Certificação ANBIMA
    
    # Controle
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Configurações
    logo_url = Column(String(500), nullable=True)
    cor_primaria = Column(String(7), nullable=True, default="#3B82F6")  # Hex color
    cor_secundaria = Column(String(7), nullable=True, default="#1E40AF")
    
    # Limites e Planos
    max_usuarios = Column(db.Integer, nullable=True)  # Limite de usuários (null = ilimitado)
    max_portfolios = Column(db.Integer, nullable=True)  # Limite de portfolios
    plano = Column(String(50), nullable=False, default="basico")  # basico, profissional, enterprise
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos (lazy para evitar N+1)
    usuarios = relationship("Usuario", back_populates="assessora", lazy="dynamic", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="assessora", lazy="dynamic", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="assessora", lazy="dynamic")
    posicoes = relationship("Posicao", back_populates="assessora", lazy="dynamic")
    planos_compra = relationship("PlanoCompra", back_populates="assessora", lazy="dynamic")
    planos_venda = relationship("PlanoVenda", back_populates="assessora", lazy="dynamic")
    movimentacoes_caixa = relationship("MovimentacaoCaixa", back_populates="assessora", lazy="dynamic")
    proventos = relationship("Provento", back_populates="assessora", lazy="dynamic")
    saldos_prejuizo = relationship("SaldoPrejuizo", back_populates="assessora", lazy="dynamic")
    saldos_darf_acumulados = relationship("SaldoDarfAcumulado", back_populates="assessora", lazy="dynamic")
    historicos_precos = relationship("HistoricoPreco", back_populates="assessora", lazy="dynamic")
    eventos_corporativos = relationship("EventoCorporativo", back_populates="assessora", lazy="dynamic")
    configuracoes_alertas = relationship("ConfiguracaoAlerta", back_populates="assessora", lazy="dynamic")
    auditorias_relatorios = relationship("AuditoriaRelatorio", back_populates="assessora", lazy="dynamic")
    logs_auditoria = relationship("LogAuditoria", back_populates="assessora", lazy="dynamic")
    
    def __repr__(self):
        return f"<Assessora {self.nome}>"
    
    def to_dict(self):
        """Serializa para dicionário"""
        return {
            "id": str(self.id),
            "nome": self.nome,
            "razao_social": self.razao_social,
            "cnpj": self.cnpj,
            "email": self.email,
            "telefone": self.telefone,
            "site": self.site,
            "numero_cvm": self.numero_cvm,
            "anbima": self.anbima,
            "ativo": self.ativo,
            "plano": self.plano,
            "logo_url": self.logo_url,
            "cor_primaria": self.cor_primaria,
            "cor_secundaria": self.cor_secundaria,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def total_usuarios(self):
        """Total de usuários ativos"""
        return self.usuarios.filter_by(ativo=True).count()
    
    @property
    def total_portfolios(self):
        """Total de portfolios"""
        return self.portfolios.count()
    
    @property
    def pode_adicionar_usuario(self):
        """Verifica se pode adicionar mais usuários"""
        if self.max_usuarios is None:
            return True
        return self.total_usuarios < self.max_usuarios
    
    @property
    def pode_adicionar_portfolio(self):
        """Verifica se pode adicionar mais portfolios"""
        if self.max_portfolios is None:
            return True
        return self.total_portfolios < self.max_portfolios
