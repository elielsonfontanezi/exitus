import uuid
from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import db


class HistoricoPatrimonio(db.Model):
    __tablename__ = 'historico_patrimonio'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    data = Column(Date, nullable=False, comment='Último dia do mês do snapshot')
    patrimonio_total = Column(Numeric(15, 2), nullable=False, comment='Patrimônio total (posições + caixa)')
    patrimonio_renda_variavel = Column(Numeric(15, 2), default=0, comment='Valor em renda variável')
    patrimonio_renda_fixa = Column(Numeric(15, 2), default=0, comment='Valor em renda fixa')
    saldo_caixa = Column(Numeric(15, 2), default=0, comment='Saldo disponível em caixa')
    observacoes = Column(Text, comment='Observações sobre o período')
    
    usuario = relationship('Usuario', back_populates='historico_patrimonio')
    
    __table_args__ = (
        UniqueConstraint('usuario_id', 'data', name='uq_historico_patrimonio_usuario_data'),
        Index('idx_historico_patrimonio_usuario_data', 'usuario_id', 'data'),
        Index('idx_historico_patrimonio_data', 'data'),
    )
    
    def __repr__(self):
        return f'<HistoricoPatrimonio {self.data} - R$ {self.patrimonio_total}>'
