# -*- coding: utf-8 -*-
"""
Exitus - Model Transacao
Entidade para registro de operações de compra e venda de ativos
"""

from datetime import datetime, timedelta
from app.database import db
from sqlalchemy import String, DateTime, Enum, Numeric, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum


class TipoOperacao(enum.Enum):
    """Enum para tipos de operação"""
    COMPRA = "compra"
    VENDA = "venda"


class Transacao(db.Model):
    """
    Model para transações de compra e venda de ativos
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário
        corretora_id (UUID): ID da corretora
        ativo_id (UUID): ID do ativo
        tipo_operacao (TipoOperacao): COMPRA ou VENDA
        quantidade (Decimal): Quantidade transacionada
        preco_unitario (Decimal): Preço por unidade
        valor_total (Decimal): Valor total da operação
        taxas (Decimal): Taxas de corretagem e custódia
        impostos (Decimal): IR e outros impostos
        data_operacao (date): Data da operação
        data_liquidacao (date): Data de liquidação
        observacoes (str): Observações sobre a transação
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário que realizou a operação
        corretora: Corretora onde foi realizada
        ativo: Ativo transacionado
    """
    
    __tablename__ = 'transacao'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da transação"
    )
    
    # Foreign keys
    usuario_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID do usuário"
    )
    
    corretora_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('corretora.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID da corretora"
    )
    
    ativo_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('ativo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="ID do ativo transacionado"
    )
    
    # Dados da transação
    tipo_operacao = db.Column(
        Enum(TipoOperacao),
        nullable=False,
        index=True,
        comment="Tipo de operação: COMPRA ou VENDA"
    )
    
    quantidade = db.Column(
        Numeric(precision=18, scale=8),
        nullable=False,
        comment="Quantidade transacionada (suporta fracionários)"
    )
    
    preco_unitario = db.Column(
        Numeric(precision=18, scale=6),
        nullable=False,
        comment="Preço por unidade"
    )
    
    valor_total = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Valor total da operação (quantidade * preço)"
    )
    
    taxas = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Taxas de corretagem, custódia, emolumentos"
    )
    
    impostos = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="IR retido na fonte, IOF, etc."
    )
    
    # Datas
    data_operacao = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data da operação"
    )
    
    data_liquidacao = db.Column(
        Date,
        nullable=True,
        index=True,
        comment="Data de liquidação (D+2, D+3, etc.)"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações sobre a transação"
    )
    
    # Timestamps
    created_at = db.Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Data de criação do registro"
    )
    
    updated_at = db.Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Data da última atualização"
    )
    
    # Relacionamentos
    usuario = relationship('Usuario', backref='transacoes', lazy='joined')
    corretora = relationship('Corretora', backref='transacoes', lazy='joined')
    ativo = relationship('Ativo', backref='transacoes', lazy='joined')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "quantidade > 0",
            name="transacao_quantidade_positiva"
        ),
        db.CheckConstraint(
            "preco_unitario > 0",
            name="transacao_preco_positivo"
        ),
        db.CheckConstraint(
            "valor_total > 0",
            name="transacao_valor_total_positivo"
        ),
        db.CheckConstraint(
            "taxas >= 0",
            name="transacao_taxas_positivas"
        ),
        db.CheckConstraint(
            "impostos >= 0",
            name="transacao_impostos_positivos"
        ),
        db.CheckConstraint(
            "data_liquidacao IS NULL OR data_liquidacao >= data_operacao",
            name="transacao_data_liquidacao_valida"
        ),
        {'comment': 'Tabela de transações de compra e venda de ativos'}
    )
    
    def __init__(self, **kwargs):
        """
        Inicializa transação com cálculos automáticos
        """
        super(Transacao, self).__init__(**kwargs)
        
        # Calcular valor total se não fornecido
        if self.valor_total is None and self.quantidade and self.preco_unitario:
            self.valor_total = self.quantidade * self.preco_unitario
        
        # Calcular data de liquidação se não fornecida (D+2 para ações BR)
        if self.data_liquidacao is None and self.data_operacao:
            self.data_liquidacao = self.data_operacao + timedelta(days=2)
    
    def is_compra(self):
        """Verifica se é uma operação de compra"""
        return self.tipo_operacao == TipoOperacao.COMPRA
    
    def is_venda(self):
        """Verifica se é uma operação de venda"""
        return self.tipo_operacao == TipoOperacao.VENDA
    
    def custo_total(self):
        """
        Calcula o custo total da operação (valor + taxas + impostos)
        
        Returns:
            Decimal: Custo total
        """
        taxas = self.taxas if self.taxas else 0
        impostos = self.impostos if self.impostos else 0
        return self.valor_total + taxas + impostos
    
    def receita_liquida(self):
        """
        Calcula a receita líquida em caso de venda (valor - taxas - impostos)
        
        Returns:
            Decimal: Receita líquida (None se não for venda)
        """
        if not self.is_venda():
            return None
        
        taxas = self.taxas if self.taxas else 0
        impostos = self.impostos if self.impostos else 0
        return self.valor_total - taxas - impostos
    
    def percentual_custos(self):
        """
        Calcula o percentual de custos (taxas + impostos) sobre o valor
        
        Returns:
            Decimal: Percentual de custos (ex: 1.5 = 1.5%)
        """
        if self.valor_total > 0:
            taxas = self.taxas if self.taxas else 0
            impostos = self.impostos if self.impostos else 0
            total_custos = taxas + impostos
            return (total_custos / self.valor_total) * 100
        return 0
    
    def dias_ate_liquidacao(self):
        """
        Calcula quantos dias faltam para liquidação
        
        Returns:
            int: Dias até liquidação (negativo se já liquidada)
        """
        if self.data_liquidacao:
            hoje = datetime.utcnow().date()
            delta = self.data_liquidacao - hoje
            return delta.days
        return None
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da transação
        """
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'corretora_id': str(self.corretora_id),
            'ativo_id': str(self.ativo_id),
            'tipo_operacao': self.tipo_operacao.value if self.tipo_operacao else None,
            'quantidade': float(self.quantidade) if self.quantidade else 0,
            'preco_unitario': float(self.preco_unitario) if self.preco_unitario else 0,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'taxas': float(self.taxas) if self.taxas else 0,
            'impostos': float(self.impostos) if self.impostos else 0,
            'custo_total': float(self.custo_total()),
            'receita_liquida': float(self.receita_liquida()) if self.receita_liquida() else None,
            'percentual_custos': float(self.percentual_custos()),
            'data_operacao': self.data_operacao.isoformat() if self.data_operacao else None,
            'data_liquidacao': self.data_liquidacao.isoformat() if self.data_liquidacao else None,
            'dias_ate_liquidacao': self.dias_ate_liquidacao(),
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        tipo = "COMPRA" if self.is_compra() else "VENDA"
        ticker = self.ativo.ticker if self.ativo else "N/A"
        return f"<Transacao {tipo} {self.quantidade}x {ticker} @ {self.preco_unitario}>"
