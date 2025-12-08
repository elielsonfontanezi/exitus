# -*- coding: utf-8 -*-
"""
Exitus - Model RelatorioPerformance
Relatórios de performance de portfolio
"""

from datetime import datetime
from app.database import db
from sqlalchemy import Column, DateTime, Numeric, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid


class RelatorioPerformance(db.Model):
    """
    Model para relatórios de performance de portfolio
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário proprietário
        portfolio_id (UUID): ID do portfolio (opcional)
        periodo_inicio (date): Data início do período
        periodo_fim (date): Data fim do período
        retorno_bruto_percentual (Decimal): Retorno bruto %
        retorno_liquido_percentual (Decimal): Retorno líquido %
        volatilidade_percentual (Decimal): Volatilidade %
        indice_sharpe (Decimal): Índice de Sharpe
        indice_sortino (Decimal): Índice de Sortino
        max_drawdown_percentual (Decimal): Max Drawdown %
        taxa_interna_retorno_irr (Decimal): IRR anual %
        beta_mercado (Decimal): Beta vs mercado
        alfa_de_jensen (Decimal): Alfa de Jensen
        valor_patrimonial_inicio (Decimal): Patrimônio início
        valor_patrimonial_fim (Decimal): Patrimônio fim
        alocacao_por_classe (JSON): Breakdown por classe de ativo
        alocacao_por_setor (JSON): Breakdown por setor
        alocacao_por_pais (JSON): Breakdown por país
        rentabilidade_por_ativo (JSON): Rentabilidade de cada ativo
        timestamp_calculo (datetime): Quando foi calculado
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário proprietário
        portfolio: Portfolio relacionado (opcional)
    """
    
    __tablename__ = "relatorios_performance"
    
    # Chave primária
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do relatório"
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
    periodo_inicio = Column(
        Date,
        nullable=False,
        index=True,
        comment="Data início do período analisado"
    )
    
    periodo_fim = Column(
        Date,
        nullable=False,
        index=True,
        comment="Data fim do período analisado"
    )
    
    # Métricas de retorno
    retorno_bruto_percentual = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Retorno bruto em % (sem descontar custos)"
    )
    
    retorno_liquido_percentual = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Retorno líquido em % (após custos e impostos)"
    )
    
    # Métricas de risco
    volatilidade_percentual = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Volatilidade anualizada em %"
    )
    
    indice_sharpe = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Índice de Sharpe (risk-adjusted return)"
    )
    
    indice_sortino = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Índice de Sortino (downside risk)"
    )
    
    max_drawdown_percentual = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Máximo drawdown em % (maior queda do pico)"
    )
    
    # Métricas avançadas
    taxa_interna_retorno_irr = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Taxa Interna de Retorno (IRR) anual em %"
    )
    
    beta_mercado = Column(
        Numeric(8, 4),
        nullable=True,
        comment="Beta em relação ao mercado (sensibilidade)"
    )
    
    alfa_de_jensen = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Alfa de Jensen (retorno excedente vs esperado)"
    )
    
    # Valores patrimoniais
    valor_patrimonial_inicio = Column(
        Numeric(18, 2),
        nullable=True,
        comment="Valor patrimonial no início do período"
    )
    
    valor_patrimonial_fim = Column(
        Numeric(18, 2),
        nullable=True,
        comment="Valor patrimonial no fim do período"
    )
    
    # Breakdown de alocação
    alocacao_por_classe = Column(
        JSON,
        nullable=True,
        comment="Distribuição por classe de ativo (JSON)"
    )
    
    alocacao_por_setor = Column(
        JSON,
        nullable=True,
        comment="Distribuição por setor (JSON)"
    )
    
    alocacao_por_pais = Column(
        JSON,
        nullable=True,
        comment="Distribuição por país (JSON)"
    )
    
    rentabilidade_por_ativo = Column(
        JSON,
        nullable=True,
        comment="Rentabilidade de cada ativo (JSON)"
    )
    
    # Auditoria
    timestamp_calculo = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Timestamp do cálculo do relatório"
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
    usuario = relationship("Usuario", backref="relatorios_performance", lazy="joined")
    # portfolio = relationship("Portfolio", backref="relatorios_performance", lazy="joined")  # Descomentar quando Portfolio existir
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "periodo_inicio <= periodo_fim",
            name="performance_periodo_valido"
        ),
        db.CheckConstraint(
            "valor_patrimonial_inicio IS NULL OR valor_patrimonial_inicio >= 0",
            name="performance_patrimonio_inicio_positivo"
        ),
        db.CheckConstraint(
            "valor_patrimonial_fim IS NULL OR valor_patrimonial_fim >= 0",
            name="performance_patrimonio_fim_positivo"
        ),
        {"comment": "Tabela de relatórios de performance"}
    )
    
    def calcular_variacao_patrimonial(self):
        """Calcula variação patrimonial absoluta"""
        if self.valor_patrimonial_inicio and self.valor_patrimonial_fim:
            return self.valor_patrimonial_fim - self.valor_patrimonial_inicio
        return None
    
    def calcular_variacao_percentual(self):
        """Calcula variação patrimonial percentual"""
        if self.valor_patrimonial_inicio and self.valor_patrimonial_fim and self.valor_patrimonial_inicio > 0:
            return ((self.valor_patrimonial_fim - self.valor_patrimonial_inicio) / self.valor_patrimonial_inicio) * 100
        return None
    
    def classificacao_sharpe(self):
        """Classifica o índice de Sharpe"""
        if self.indice_sharpe is None:
            return "N/A"
        
        sharpe = float(self.indice_sharpe)
        if sharpe < 0:
            return "Ruim"
        elif sharpe < 1:
            return "Regular"
        elif sharpe < 2:
            return "Bom"
        elif sharpe < 3:
            return "Muito Bom"
        else:
            return "Excelente"
    
    def to_dict(self):
        """Converte objeto para dicionário para serialização JSON"""
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "portfolio_id": str(self.portfolio_id) if self.portfolio_id else None,
            "periodo_inicio": self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            "periodo_fim": self.periodo_fim.isoformat() if self.periodo_fim else None,
            "retorno_bruto_percentual": float(self.retorno_bruto_percentual) if self.retorno_bruto_percentual else None,
            "retorno_liquido_percentual": float(self.retorno_liquido_percentual) if self.retorno_liquido_percentual else None,
            "volatilidade_percentual": float(self.volatilidade_percentual) if self.volatilidade_percentual else None,
            "indice_sharpe": float(self.indice_sharpe) if self.indice_sharpe else None,
            "classificacao_sharpe": self.classificacao_sharpe(),
            "indice_sortino": float(self.indice_sortino) if self.indice_sortino else None,
            "max_drawdown_percentual": float(self.max_drawdown_percentual) if self.max_drawdown_percentual else None,
            "taxa_interna_retorno_irr": float(self.taxa_interna_retorno_irr) if self.taxa_interna_retorno_irr else None,
            "beta_mercado": float(self.beta_mercado) if self.beta_mercado else None,
            "alfa_de_jensen": float(self.alfa_de_jensen) if self.alfa_de_jensen else None,
            "valor_patrimonial_inicio": float(self.valor_patrimonial_inicio) if self.valor_patrimonial_inicio else None,
            "valor_patrimonial_fim": float(self.valor_patrimonial_fim) if self.valor_patrimonial_fim else None,
            "variacao_patrimonial_absoluta": float(self.calcular_variacao_patrimonial()) if self.calcular_variacao_patrimonial() else None,
            "variacao_patrimonial_percentual": float(self.calcular_variacao_percentual()) if self.calcular_variacao_percentual() else None,
            "alocacao_por_classe": self.alocacao_por_classe,
            "alocacao_por_setor": self.alocacao_por_setor,
            "alocacao_por_pais": self.alocacao_por_pais,
            "rentabilidade_por_ativo": self.rentabilidade_por_ativo,
            "timestamp_calculo": self.timestamp_calculo.isoformat() if self.timestamp_calculo else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        periodo = f"{self.periodo_inicio} a {self.periodo_fim}" if self.periodo_inicio and self.periodo_fim else "N/A"
        return f"<RelatorioPerformance {periodo}>"
