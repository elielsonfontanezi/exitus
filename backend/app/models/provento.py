# -*- coding: utf-8 -*-
"""
Exitus - Model Provento
Entidade para registro de proventos (dividendos, JCP, rendimentos)
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, DateTime, Enum, Numeric, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum


class TipoProvento(enum.Enum):
    """Enum para tipos de provento"""
    DIVIDENDO = "dividendo"              # Dividendo ordinário
    JCP = "jcp"                          # Juros sobre Capital Próprio
    RENDIMENTO = "rendimento"            # Rendimento de FII
    CUPOM = "cupom"                      # Cupom de título de renda fixa
    BONIFICACAO = "bonificacao"          # Bonificação em dinheiro
    DIREITO_SUBSCRICAO = "direito_sub"   # Direito de subscrição vendido
    OUTRO = "outro"                      # Outros tipos


class Provento(db.Model):
    """
    Model para proventos recebidos de ativos
    
    Attributes:
        id (UUID): Identificador único
        ativo_id (UUID): ID do ativo que pagou o provento
        tipo_provento (TipoProvento): Tipo do provento
        valor_por_acao (Decimal): Valor unitário por ativo
        data_com (date): Data COM (último dia para ter direito)
        data_pagamento (date): Data efetiva do pagamento
        quantidade_ativos (Decimal): Quantidade de ativos que geraram provento
        valor_bruto (Decimal): Valor bruto recebido
        imposto_retido (Decimal): IR retido na fonte
        valor_liquido (Decimal): Valor líquido creditado
        observacoes (str): Observações sobre o provento
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        ativo: Ativo que pagou o provento
    """
    
    __tablename__ = 'provento'
        # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do provento"
    )
    
    # Foreign key
    ativo_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('ativo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="ID do ativo que pagou o provento"
    )
    
    # Tipo de provento
    tipo_provento = db.Column(
        Enum(TipoProvento),
        nullable=False,
        index=True,
        comment="Tipo do provento (dividendo, JCP, rendimento, etc.)"
    )
    
    # Valores
    valor_por_acao = db.Column(
        Numeric(precision=18, scale=6),
        nullable=False,
        comment="Valor unitário por ativo"
    )
    
    quantidade_ativos = db.Column(
        Numeric(precision=18, scale=8),
        nullable=False,
        comment="Quantidade de ativos que geraram o provento"
    )
    
    valor_bruto = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Valor bruto recebido"
    )
    
    imposto_retido = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="IR retido na fonte"
    )
    
    valor_liquido = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Valor líquido creditado"
    )
    
    # Datas
    data_com = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data COM (último dia para ter direito ao provento)"
    )
    
    data_pagamento = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data efetiva do pagamento"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações sobre o provento"
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
    ativo = relationship('Ativo', backref='proventos', lazy='joined')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "valor_por_acao > 0",
            name="provento_valor_por_acao_positivo"
        ),
        db.CheckConstraint(
            "quantidade_ativos > 0",
            name="provento_quantidade_positiva"
        ),
        db.CheckConstraint(
            "valor_bruto > 0",
            name="provento_valor_bruto_positivo"
        ),
        db.CheckConstraint(
            "imposto_retido >= 0",
            name="provento_imposto_positivo"
        ),
        db.CheckConstraint(
            "valor_liquido > 0",
            name="provento_valor_liquido_positivo"
        ),
        db.CheckConstraint(
            "valor_liquido <= valor_bruto",
            name="provento_liquido_menor_bruto"
        ),
        db.CheckConstraint(
            "data_pagamento >= data_com",
            name="provento_data_pagamento_valida"
        ),
        {'comment': 'Tabela de proventos recebidos (dividendos, JCP, rendimentos)'}
    )
    
    def __init__(self, **kwargs):
        """
        Inicializa provento com cálculos automáticos
        """
        super(Provento, self).__init__(**kwargs)
        
        # Calcular valor bruto se não fornecido
        if self.valor_bruto is None and self.valor_por_acao and self.quantidade_ativos:
            self.valor_bruto = self.valor_por_acao * self.quantidade_ativos
        
        # Calcular valor líquido se não fornecido
        if self.valor_liquido is None and self.valor_bruto is not None:
            imposto = self.imposto_retido if self.imposto_retido else 0
            self.valor_liquido = self.valor_bruto - imposto
    
    def is_dividendo(self):
        """Verifica se é dividendo"""
        return self.tipo_provento == TipoProvento.DIVIDENDO
    
    def is_jcp(self):
        """Verifica se é JCP"""
        return self.tipo_provento == TipoProvento.JCP
    
    def is_rendimento_fii(self):
        """Verifica se é rendimento de FII"""
        return self.tipo_provento == TipoProvento.RENDIMENTO
    
    def percentual_imposto(self):
        """
        Calcula o percentual de imposto retido
        
        Returns:
            Decimal: Percentual de imposto (ex: 15.0 = 15%)
        """
        if self.valor_bruto and self.valor_bruto > 0:
            imposto = self.imposto_retido if self.imposto_retido else 0
            return (imposto / self.valor_bruto) * 100
        return 0
    
    def dividend_yield_efetivo(self, preco_ativo):
        """
        Calcula o dividend yield efetivo baseado no preço do ativo
        
        Args:
            preco_ativo (Decimal): Preço atual do ativo
            
        Returns:
            Decimal: DY efetivo em % (ex: 6.5 = 6.5%)
        """
        if preco_ativo and preco_ativo > 0:
            return (self.valor_por_acao / preco_ativo) * 100
        return 0
    
    def dias_ate_pagamento(self):
        """
        Calcula quantos dias faltam para o pagamento
        
        Returns:
            int: Dias até pagamento (negativo se já pago)
        """
        hoje = datetime.utcnow().date()
        delta = self.data_pagamento - hoje
        return delta.days
    
    def to_dict(self):
        """Converte objeto para dicionário para serialização JSON"""
        
        # ✅ CORREÇÃO: Serializar enum corretamente
        tipo_str = self.tipo_provento.value if isinstance(self.tipo_provento, TipoProvento) else str(self.tipo_provento)
        
        # Remove prefixo "TipoProvento." se existir
        if tipo_str.startswith('TipoProvento.'):
            tipo_str = tipo_str.replace('TipoProvento.', '').lower()
        
        return {
            'id': str(self.id),
            'ativo_id': str(self.ativo_id),
            'tipo_provento': tipo_str,  # ✅ CORRIGIDO
            'valor_por_acao': float(self.valor_por_acao) if self.valor_por_acao else 0,
            'quantidade_ativos': float(self.quantidade_ativos) if self.quantidade_ativos else 0,
            'valor_bruto': float(self.valor_bruto) if self.valor_bruto else 0,
            'imposto_retido': float(self.imposto_retido) if self.imposto_retido else 0,
            'valor_liquido': float(self.valor_liquido) if self.valor_liquido else 0,
            'data_com': self.data_com.isoformat() if self.data_com else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        ticker = self.ativo.ticker if self.ativo else "N/A"
        tipo = self.tipo_provento.value if self.tipo_provento else "N/A"
        return f"<Provento {tipo.upper()} {ticker} R$ {self.valor_por_acao}/ação>"
