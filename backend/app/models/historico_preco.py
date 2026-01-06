"""
Model HistoricoPreco - Histórico diário de preços dos ativos
Criado em: 2026-01-06
Issue: #1 - Gap P0 da Revisão M1-4
"""

from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index
import uuid
from datetime import datetime


class HistoricoPreco(db.Model):
    """
    Armazena histórico diário de preços dos ativos.
    
    Utilizado para cálculos de:
    - Z-Score (desvio do preço histórico)
    - Volatilidade (desvio padrão dos retornos)
    - Sharpe Ratio (retorno ajustado ao risco)
    - Beta (correlação com índice de mercado)
    """
    
    __tablename__ = 'historico_preco'
    
    # Colunas
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativoid = db.Column(UUID(as_uuid=True), db.ForeignKey('ativo.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    preco_abertura = db.Column(db.Numeric(18, 6), nullable=True)
    preco_fechamento = db.Column(db.Numeric(18, 6), nullable=False)
    preco_minimo = db.Column(db.Numeric(18, 6), nullable=True)
    preco_maximo = db.Column(db.Numeric(18, 6), nullable=True)
    volume = db.Column(db.BigInteger, nullable=True)
    createdat = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updatedat = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)
    
    # Relacionamento com Ativo
    ativo = db.relationship('Ativo', backref=db.backref('historico_precos', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('ativoid', 'data', name='uq_historico_ativo_data'),
        db.CheckConstraint('preco_fechamento > 0', name='ck_historico_fechamento_positivo'),
        db.CheckConstraint(
            'preco_minimo IS NULL OR preco_maximo IS NULL OR preco_minimo <= preco_maximo',
            name='ck_historico_minmax'
        ),
        Index('ix_historico_ativoid_data', 'ativoid', 'data'),
    )
    
    def __repr__(self):
        return f'<HistoricoPreco {self.ativo.ticker if self.ativo else "?"} {self.data} R${self.preco_fechamento}>'
    
    def to_dict(self):
        """Serializa para JSON."""
        return {
            'id': str(self.id),
            'ativoid': str(self.ativoid),
            'ticker': self.ativo.ticker if self.ativo else None,
            'data': self.data.isoformat() if self.data else None,
            'preco_abertura': float(self.preco_abertura) if self.preco_abertura else None,
            'preco_fechamento': float(self.preco_fechamento),
            'preco_minimo': float(self.preco_minimo) if self.preco_minimo else None,
            'preco_maximo': float(self.preco_maximo) if self.preco_maximo else None,
            'volume': self.volume,
            'createdat': self.createdat.isoformat() if self.createdat else None,
            'updatedat': self.updatedat.isoformat() if self.updatedat else None
        }
