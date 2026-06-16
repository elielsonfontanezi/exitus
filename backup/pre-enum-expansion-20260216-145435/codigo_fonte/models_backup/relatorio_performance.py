"""M7.1 - RelatorioPerformance Model SIMPLIFICADO (colunas DB reais)"""
from datetime import datetime, date
from sqlalchemy import Column, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import db

class RelatorioPerformance(db.Model):
    __tablename__ = 'relatorios_performance'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False, index=True)
    portfolio_id = Column(UUID(as_uuid=True), nullable=True)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    retorno_bruto_percentual = Column(Numeric(10, 4), nullable=True)
    retorno_liquido_percentual = Column(Numeric(10, 4), nullable=True)
    indice_sharpe = Column(Numeric(8, 4), nullable=True)
    max_drawdown_percentual = Column(Numeric(8, 4), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'portfolio_id': str(self.portfolio_id) if self.portfolio_id else None,
            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fim': self.periodo_fim.isoformat() if self.periodo_fim else None,
            'retorno_bruto_percentual': float(self.retorno_bruto_percentual) if self.retorno_bruto_percentual else None,
            'retorno_liquido_percentual': float(self.retorno_liquido_percentual) if self.retorno_liquido_percentual else None,
            'indice_sharpe': float(self.indice_sharpe) if self.indice_sharpe else None,
            'max_drawdown_percentual': float(self.max_drawdown_percentual) if self.max_drawdown_percentual else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
