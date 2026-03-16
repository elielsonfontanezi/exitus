"""
Model: PlanoCompra
Representa um plano de compra programada de ativos
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import db
import enum


class StatusPlanoCompra(enum.Enum):
    """Status possíveis de um plano de compra"""
    ATIVO = "ativo"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class PlanoCompra(db.Model):
    """
    Model para planos de compra programada de ativos.
    Permite ao usuário definir metas de aquisição com aportes mensais.
    """
    __tablename__ = 'plano_compra'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False, index=True)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey('ativo.id', ondelete='CASCADE'), nullable=False, index=True)
    assessora_id = Column(UUID(as_uuid=True), ForeignKey('assessora.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Dados do plano
    nome = Column(String(200), nullable=False)
    descricao = Column(String(500), nullable=True)
    quantidade_alvo = Column(Numeric(15, 4), nullable=False)
    quantidade_acumulada = Column(Numeric(15, 4), nullable=False, default=0)
    valor_aporte_mensal = Column(Numeric(15, 2), nullable=False)
    
    # Datas
    data_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_fim_prevista = Column(DateTime, nullable=True)
    data_conclusao = Column(DateTime, nullable=True)
    
    # Status e controle
    status = Column(SQLEnum(StatusPlanoCompra), nullable=False, default=StatusPlanoCompra.ATIVO, index=True)
    proximo_aporte = Column(DateTime, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    assessora = relationship('Assessora', back_populates='planos_compra')
    usuario = relationship('Usuario', back_populates='planos_compra')
    ativo = relationship('Ativo', backref='planos_compra')

    def __repr__(self):
        return f'<PlanoCompra {self.nome} - {self.ativo.ticker if self.ativo else "N/A"}>'

    def to_dict(self):
        """Serializa o plano de compra para dict"""
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'ativo_id': str(self.ativo_id),
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade_alvo': float(self.quantidade_alvo),
            'quantidade_acumulada': float(self.quantidade_acumulada),
            'valor_aporte_mensal': float(self.valor_aporte_mensal),
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim_prevista': self.data_fim_prevista.isoformat() if self.data_fim_prevista else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'status': self.status.value,
            'proximo_aporte': self.proximo_aporte.isoformat() if self.proximo_aporte else None,
            'progresso_percentual': self.calcular_progresso(),
            'ativo': {
                'id': str(self.ativo.id),
                'ticker': self.ativo.ticker,
                'nome': self.ativo.nome,
                'tipo': self.ativo.tipo.value,
                'mercado': self.ativo.mercado,
                'preco_atual': float(self.ativo.preco_atual) if self.ativo.preco_atual else None
            } if self.ativo else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def calcular_progresso(self):
        """Calcula o progresso percentual do plano"""
        if self.quantidade_alvo and self.quantidade_alvo > 0:
            return round((float(self.quantidade_acumulada) / float(self.quantidade_alvo)) * 100, 2)
        return 0.0

    def esta_concluido(self):
        """Verifica se o plano atingiu a meta"""
        return self.quantidade_acumulada >= self.quantidade_alvo

    def pode_receber_aporte(self):
        """Verifica se o plano pode receber um novo aporte"""
        return self.status == StatusPlanoCompra.ATIVO and not self.esta_concluido()
