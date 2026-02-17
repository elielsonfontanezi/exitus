"""M7.1 - ProjecaoRenda Model Completo"""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import db

class ProjecaoRenda(db.Model):
    """Projeções de renda passiva mensal por portfolio"""
    __tablename__ = 'projecoes_renda'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False, index=True)
    portfolio_id = Column(UUID(as_uuid=True), nullable=True)
    mes_ano = Column(String(7), nullable=False, index=True)  # '2025-12'
    
    # Projeções por tipo (R$)
    renda_dividendos_projetada = Column(Numeric(18, 2), default=0.00, nullable=False)
    renda_jcp_projetada = Column(Numeric(18, 2), default=0.00, nullable=False)
    renda_rendimentos_projetada = Column(Numeric(18, 2), default=0.00, nullable=False)
    renda_total_mes = Column(Numeric(18, 2), default=0.00, nullable=False)
    renda_anual_projetada = Column(Numeric(18, 2), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, 
                       onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'portfolio_id', 'mes_ano', 
                           name='projecoes_renda_usuario_id_portfolio_id_mes_ano_key'),
    )
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'portfolio_id': str(self.portfolio_id) if self.portfolio_id else None,
            'mes_ano': self.mes_ano,
            'renda_dividendos_projetada': float(self.renda_dividendos_projetada),
            'renda_jcp_projetada': float(self.renda_jcp_projetada),
            'renda_rendimentos_projetada': float(self.renda_rendimentos_projetada),
            'renda_total_mes': float(self.renda_total_mes),
            'renda_anual_projetada': float(self.renda_anual_projetada) if self.renda_anual_projetada else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
