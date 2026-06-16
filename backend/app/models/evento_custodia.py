from datetime import datetime
from enum import Enum

from app.database import db
import uuid


class TipoEventoCustodia(Enum):
    """Tipos de eventos de custódia"""
    LIQUIDACAO_D2 = "LIQUIDACAO_D2"  # Liquidação D+2 de operações
    TRANSFERENCIA_ENTRADA = "TRANSFERENCIA_ENTRADA"  # Entrada por transferência
    TRANSFERENCIA_SAIDA = "TRANSFERENCIA_SAIDA"  # Saída por transferência
    AJUSTE_POSICAO = "AJUSTE_POSICAO"  # Ajuste de posição
    DESDOBRAMENTO = "DESDOBRAMENTO"  # Split de ações
    AGRUPAMENTO = "AGRUPAMENTO"  # Inplit de ações
    AMORTIZACAO = "AMORTIZACAO"  # Amortização de capital
    OUTRO = "OUTRO"  # Outros eventos


class EventoCustodia(db.Model):
    """Modelo para eventos de custódia da B3"""
    
    __tablename__ = 'evento_custodia'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('usuario.id'), nullable=False)
    ativo_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('ativo.id'), nullable=False)
    corretora_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('corretora.id'), nullable=False)
    
    # Dados do evento
    tipo_evento = db.Column(db.Enum(TipoEventoCustodia, values_callable=lambda x: [e.value for e in x]), nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    quantidade = db.Column(db.Numeric(18, 8), nullable=False)
    valor_operacao = db.Column(db.Numeric(18, 2), nullable=False)
    
    # Metadados
    observacoes = db.Column(db.Text)
    fonte = db.Column(db.String(50), default='B3_IMPORT')
    dados_origem = db.Column(db.JSON)  # Dados originais do arquivo B3
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='eventos_custodia')
    ativo = db.relationship('Ativo', backref='eventos_custodia')
    corretora = db.relationship('Corretora', backref='eventos_custodia')
    
    def __repr__(self):
        return f'<EventoCustodia {self.tipo_evento.value} - {self.ativo.ticker} - {self.data_evento}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'ativo_id': str(self.ativo_id),
            'corretora_id': str(self.corretora_id),
            'tipo_evento': self.tipo_evento.value,
            'data_evento': self.data_evento.isoformat(),
            'quantidade': float(self.quantidade),
            'valor_operacao': float(self.valor_operacao),
            'observacoes': self.observacoes,
            'fonte': self.fonte,
            'dados_origem': self.dados_origem,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @property
    def preco_unitario(self):
        """Calcula preço unitário"""
        if self.quantidade and self.quantidade != 0:
            return self.valor_operacao / self.quantidade
        return 0
