# -*- coding: utf-8 -*-
"""
Exitus - Model Portfolio
Sistema de agrupamento de posições em portfolios
"""
from datetime import datetime
from app.database import db
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Portfolio(db.Model):
    """
    Model para portfolios (agrupamento de posições).

    Permite ao usuário organizar seus investimentos em múltiplos portfolios
    (ex: "Longo Prazo", "Trade", "Dividendos", "Internacional").

    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário proprietário
        nome (str): Nome do portfolio (ex: "Portfolio Principal")
        descricao (str): Descrição detalhada (opcional)
        objetivo (str): Objetivo do portfolio (ex: "Renda Passiva", "Crescimento")
        ativo (bool): Se o portfolio está ativo
        valor_inicial (Decimal): Valor inicial investido (opcional)
        percentual_alocacao_target (Decimal): % de alocação desejada (opcional)
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização

    Relationships:
        usuario: Usuário proprietário
        posicoes: Lista de posições vinculadas
        alertas: Lista de alertas vinculados
    """
    __tablename__ = 'portfolio'

    # ========================================
    # CHAVE PRIMÁRIA
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Identificador único do portfolio'
    )

    # ========================================
    # FOREIGN KEYS
    # ========================================
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='ID do usuário proprietário'
    )

    # ========================================
    # DADOS DO PORTFOLIO
    # ========================================
    nome = Column(
        String(100),
        nullable=False,
        comment='Nome do portfolio (ex: Portfolio Principal, Trade, Longo Prazo)'
    )

    descricao = Column(
        Text,
        nullable=True,
        comment='Descrição detalhada do portfolio e sua estratégia'
    )

    objetivo = Column(
        String(50),
        nullable=True,
        comment='Objetivo do portfolio (Renda Passiva, Crescimento, Proteção, etc.)'
    )

    ativo = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment='Indica se o portfolio está ativo'
    )

    # ========================================
    # DADOS FINANCEIROS (OPCIONAIS)
    # ========================================
    valor_inicial = Column(
        Numeric(18, 2),
        nullable=True,
        comment='Valor inicial investido no portfolio (R$)'
    )

    percentual_alocacao_target = Column(
        Numeric(5, 2),
        nullable=True,
        comment='Percentual de alocação desejada do patrimônio total (0-100)'
    )

    # ========================================
    # TIMESTAMPS
    # ========================================
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment='Data de criação do registro'
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment='Data da última atualização'
    )

    # ========================================
    # RELACIONAMENTOS
    # ========================================
    usuario = relationship('Usuario', back_populates='portfolios', lazy='joined')
    # posicoes = relationship('Posicao', back_populates='portfolio', lazy='dynamic')  # Descomentar quando Posicao tiver portfolio_id
    alertas = relationship('ConfiguracaoAlerta', back_populates='portfolio', lazy='dynamic')

    # ========================================
    # CONSTRAINTS DE TABELA
    # ========================================
    __table_args__ = (
        db.CheckConstraint('LENGTH(nome) >= 3', name='portfolio_nome_min_length'),
        db.CheckConstraint('valor_inicial IS NULL OR valor_inicial >= 0', name='portfolio_valor_inicial_positivo'),
        db.CheckConstraint('percentual_alocacao_target IS NULL OR (percentual_alocacao_target >= 0 AND percentual_alocacao_target <= 100)', name='portfolio_percentual_valido'),
        {'comment': 'Tabela de portfolios (agrupamento de posições)'}
    )

    # ========================================
    # MÉTODOS
    # ========================================
    def to_dict(self):
        """Converte objeto para dicionário para serialização JSON."""
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'nome': self.nome,
            'descricao': self.descricao,
            'objetivo': self.objetivo,
            'ativo': self.ativo,
            'valor_inicial': float(self.valor_inicial) if self.valor_inicial else None,
            'percentual_alocacao_target': float(self.percentual_alocacao_target) if self.percentual_alocacao_target else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        """Representação string do objeto."""
        status = "ATIVO" if self.ativo else "INATIVO"
        return f"<Portfolio '{self.nome}' ({status})>"
