# -*- coding: utf-8 -*-
"""
Exitus - Model CalendarioDividendo
Calendário de proventos futuros esperados para planejamento
"""

from datetime import datetime, date
from app.database import db
from sqlalchemy import Column, String, Text, Date, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class CalendarioDividendo(db.Model):
    """
    Model para calendário de proventos futuros.
    
    Permite planejar fluxo de caixa futuro com base em histórico
    e yield esperado dos ativos do usuário.
    
    Attributes:
        id (UUID): Identificador único
        ativo_id (UUID): ID do ativo
        usuario_id (UUID): ID do usuário proprietário
        data_esperada (Date): Data prevista do provento
        tipo_provento (TipoProvento): Tipo do provento
        yield_estimado (Decimal): Yield percentual estimado
        valor_estimado (Decimal): Valor em R$ estimado
        quantidade (Integer): Quantidade de ativos
        status (StatusCalendario): Status do calendário
        observacoes (Text): Observações adicionais
        data_pagamento (Date): Data real do pagamento (quando confirmado)
        valor_real (Decimal): Valor real pago (quando confirmado)
        created_at (datetime): Data de criação
        updated_at (datetime): Data de atualização
    """
    
    __tablename__ = 'calendario_dividendo'
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    ativo_id = Column(UUID(as_uuid=True), ForeignKey('ativo.id'), nullable=False)
    assessora_id = Column(UUID(as_uuid=True), ForeignKey('assessora.id', ondelete='CASCADE'), nullable=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False)
    
    # Dados do Calendário
    data_esperada = Column(Date, nullable=False, comment='Data prevista do provento')
    tipo_provento = Column(String(20), nullable=False, default='dividendo', comment='Tipo do provento')
    
    # Estimativas
    yield_estimado = Column(db.Numeric(8, 4), nullable=True, comment='Yield percentual estimado')
    valor_estimado = Column(db.Numeric(18, 2), nullable=True, comment='Valor em R$ estimado')
    quantidade = Column(db.Integer, nullable=False, default=0, comment='Quantidade de ativos')
    
    # Status e Controle
    status = Column(String(20), nullable=False, default='previsto', comment='Status do calendário')
    observacoes = Column(db.Text, nullable=True, comment='Observações adicionais')
    
    # Dados Reais (quando confirmado/pago)
    data_pagamento = Column(Date, nullable=True, comment='Data real do pagamento')
    valor_real = Column(db.Numeric(18, 2), nullable=True, comment='Valor real pago')
    
    # Timestamps
    created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                        onupdate=datetime.utcnow)
    
    # Relationships
    ativo = relationship("Ativo", backref="calendario_dividendos")
    usuario = relationship("Usuario", backref="calendario_dividendos")
    
    # Indexes
    __table_args__ = (
        Index('idx_calendario_usuario_data', 'usuario_id', 'data_esperada'),
        Index('idx_calendario_ativo_data', 'ativo_id', 'data_esperada'),
        Index('idx_calendario_status', 'status'),
        Index('idx_calendario_usuario_ativo', 'usuario_id', 'ativo_id'),
    )
    
    def __repr__(self):
        return f"<CalendarioDividendo {self.ativo.ticker if self.ativo else 'N/A'} - {self.data_esperada}>"
    
    def to_dict(self):
        """Converte para dicionário serializável"""
        return {
            'id': str(self.id),
            'ativo_id': str(self.ativo_id),
            'usuario_id': str(self.usuario_id),
            'data_esperada': self.data_esperada.isoformat() if self.data_esperada else None,
            'tipo_provento': self.tipo_provento,
            'yield_estimado': float(self.yield_estimado) if self.yield_estimado else None,
            'valor_estimado': float(self.valor_estimado) if self.valor_estimado else None,
            'quantidade': self.quantidade,
            'status': self.status,
            'observacoes': self.observacoes,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'valor_real': float(self.valor_real) if self.valor_real else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ativo': self.ativo.to_dict() if self.ativo else None
        }
    
    @property
    def ticker(self):
        """Alias para ticker do ativo"""
        return self.ativo.ticker if self.ativo else None
    
    @property
    def nome_ativo(self):
        """Alias para nome do ativo"""
        return self.ativo.nome if self.ativo else None
    
    def atualizar_status(self, novo_status=None):
        """Atualiza status e timestamp"""
        if novo_status:
            self.status = novo_status
        self.updated_at = datetime.utcnow()
    
    def confirmar_pagamento(self, data_pagamento=None, valor_real=None):
        """Confirma o pagamento do dividendo"""
        self.status = 'pago'
        if data_pagamento:
            self.data_pagamento = data_pagamento
        if valor_real:
            self.valor_real = valor_real
        self.updated_at = datetime.utcnow()
