# -*- coding: utf-8 -*-
"""
Exitus - Model ProjecaoRenda
Projeções de renda passiva futura
"""

from datetime import datetime
from app.database import db
from sqlalchemy import Column, DateTime, Numeric, Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid


class ProjecaoRenda(db.Model):
    """
    Model para projeções de renda passiva mensal
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário proprietário
        portfolio_id (UUID): ID do portfolio (opcional)
        mes_ano (str): Mês/ano da projeção (formato: YYYY-MM)
        renda_dividendos_projetada (Decimal): Renda de dividendos
        renda_jcp_projetada (Decimal): Renda de JCP
        renda_rendimento_projetada (Decimal): Renda de rendimentos (FIIs, etc)
        renda_total_mes (Decimal): Soma das rendas do mês
        renda_anual_projetada (Decimal): Projeção anual
        crescimento_percentual_mes (Decimal): % crescimento vs mês anterior
        crescimento_percentual_ano (Decimal): % crescimento vs ano anterior
        ativos_contribuindo (int): Quantidade de ativos pagando
        timestamp_calculo (datetime): Quando foi calculado
        metadados (JSON): Detalhes por ativo
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário proprietário
        portfolio: Portfolio relacionado (opcional)
    """
    
    __tablename__ = "projecoes_renda"
    
    # Chave primária
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da projeção"
    )
    
    # Foreign keys
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID do usuário proprietário"
    )
    
    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey('portfolio.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="ID do portfolio (opcional, null = todos portfolios)"
    )
    
    # Período
    mes_ano = Column(
        String(7),  # formato YYYY-MM
        nullable=False,
        index=True,
        comment="Mês/ano da projeção (ex: 2025-12)"
    )
    
    # Projeções por tipo
    renda_dividendos_projetada = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Renda projetada de dividendos"
    )
    
    renda_jcp_projetada = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Renda projetada de JCP"
    )
    
    renda_rendimento_projetada = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Renda projetada de rendimentos (FIIs, REITs, etc)"
    )
    
    renda_total_mes = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
        comment="Soma total de renda do mês"
    )
    
    renda_anual_projetada = Column(
        Numeric(18, 2),
        nullable=True,
        comment="Projeção de renda anual (12 meses)"
    )
    
    # Crescimento
    crescimento_percentual_mes = Column(
        Numeric(8, 4),
        nullable=True,
        comment="% crescimento em relação ao mês anterior"
    )
    
    crescimento_percentual_ano = Column(
        Numeric(8, 4),
        nullable=True,
        comment="% crescimento em relação ao ano anterior"
    )
    
    # Estatísticas
    ativos_contribuindo = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Quantidade de ativos contribuindo com renda"
    )
    
    # Auditoria
    timestamp_calculo = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Timestamp do cálculo da projeção"
    )
    
    metadados = Column(
        JSON,
        nullable=True,
        comment="Detalhes por ativo (JSON com breakdown)"
    )
    
    # Timestamps padrão
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Data de criação do registro"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Data da última atualização"
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", backref="projecoes_renda", lazy="joined")
    # portfolio = relationship("Portfolio", backref="projecoes_renda", lazy="joined")  # Descomentar quando Portfolio existir
    
    # Constraints de tabela
    __table_args__ = (
        db.UniqueConstraint(
            'usuario_id', 'portfolio_id', 'mes_ano',
            name='unique_projecao_usuario_portfolio_mes'
        ),
        db.CheckConstraint(
            "renda_dividendos_projetada >= 0",
            name="projecao_dividendos_positivo"
        ),
        db.CheckConstraint(
            "renda_jcp_projetada >= 0",
            name="projecao_jcp_positivo"
        ),
        db.CheckConstraint(
            "renda_rendimento_projetada >= 0",
            name="projecao_rendimento_positivo"
        ),
        db.CheckConstraint(
            "renda_total_mes >= 0",
            name="projecao_total_positivo"
        ),
        db.CheckConstraint(
            "ativos_contribuindo >= 0",
            name="projecao_ativos_positivo"
        ),
        db.CheckConstraint(
            "mes_ano ~ '^[0-9]{4}-[0-9]{2}$'",
            name="projecao_mesano_formato"
        ),
        {"comment": "Tabela de projeções de renda passiva mensal"}
    )
    
    def calcular_total(self):
        """Recalcula o total de renda do mês"""
        self.renda_total_mes = (
            (self.renda_dividendos_projetada or 0) +
            (self.renda_jcp_projetada or 0) +
            (self.renda_rendimento_projetada or 0)
        )
        return self.renda_total_mes
    
    def calcular_crescimento_mes(self, renda_mes_anterior):
        """
        Calcula crescimento percentual em relação ao mês anterior
        
        Args:
            renda_mes_anterior (Decimal): Renda do mês anterior
        """
        if renda_mes_anterior and renda_mes_anterior > 0:
            self.crescimento_percentual_mes = (
                ((self.renda_total_mes - renda_mes_anterior) / renda_mes_anterior) * 100
            )
        else:
            self.crescimento_percentual_mes = 0
    
    def calcular_crescimento_ano(self, renda_ano_anterior):
        """
        Calcula crescimento percentual em relação ao mesmo mês do ano anterior
        
        Args:
            renda_ano_anterior (Decimal): Renda do mesmo mês do ano anterior
        """
        if renda_ano_anterior and renda_ano_anterior > 0:
            self.crescimento_percentual_ano = (
                ((self.renda_total_mes - renda_ano_anterior) / renda_ano_anterior) * 100
            )
        else:
            self.crescimento_percentual_ano = 0
    
    def to_dict(self):
        """Converte objeto para dicionário para serialização JSON"""
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "portfolio_id": str(self.portfolio_id) if self.portfolio_id else None,
            "mes_ano": self.mes_ano,
            "renda_dividendos_projetada": float(self.renda_dividendos_projetada) if self.renda_dividendos_projetada else 0,
            "renda_jcp_projetada": float(self.renda_jcp_projetada) if self.renda_jcp_projetada else 0,
            "renda_rendimento_projetada": float(self.renda_rendimento_projetada) if self.renda_rendimento_projetada else 0,
            "renda_total_mes": float(self.renda_total_mes) if self.renda_total_mes else 0,
            "renda_anual_projetada": float(self.renda_anual_projetada) if self.renda_anual_projetada else None,
            "crescimento_percentual_mes": float(self.crescimento_percentual_mes) if self.crescimento_percentual_mes else None,
            "crescimento_percentual_ano": float(self.crescimento_percentual_ano) if self.crescimento_percentual_ano else None,
            "ativos_contribuindo": self.ativos_contribuindo,
            "timestamp_calculo": self.timestamp_calculo.isoformat() if self.timestamp_calculo else None,
            "metadados": self.metadados,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<ProjecaoRenda {self.mes_ano} - R$ {self.renda_total_mes}>"
