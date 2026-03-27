from app.database import db
from sqlalchemy import Column, String, Numeric, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class ParametrosMacro(db.Model):
    __tablename__ = 'parametros_macro'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pais = Column(String(2), nullable=False, index=True)  # BR, US, EU, JP
    mercado = Column(String(10), nullable=False, index=True)  # B3, NYSE, etc
    taxa_livre_risco = Column(Numeric(8,6), nullable=False)  # CDI, T-Bill
    crescimento_medio = Column(Numeric(8,6), nullable=False)  # g esperado
    custo_capital = Column(Numeric(8,6), nullable=False)  # WACC médio
    inflacao_anual = Column(Numeric(8,6), nullable=False)
    cap_rate_fii = Column(Numeric(8,6))  # Para FIIs/REITs
    ytm_rf = Column(Numeric(8,6))  # Yield Renda Fixa
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('ix_parametros_macro_pais_mercado', 'pais', 'mercado', unique=True),
    )
    
    def __repr__(self):
        return f'<ParametrosMacro(pais="{self.pais}", mercado="{self.mercado}")>'
