# -*- coding: utf-8 -*-
"""
Exitus - Model MovimentacaoCaixa
Entidade para movimentações de caixa em corretoras
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, DateTime, Enum, Numeric, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum


class TipoMovimentacao(enum.Enum):
    """Enum para tipos de movimentação"""
    DEPOSITO = "deposito"                    # Depósito na corretora
    SAQUE = "saque"                          # Saque da corretora
    TRANSFERENCIA_ENVIADA = "transf_env"    # Transferência para outra corretora
    TRANSFERENCIA_RECEBIDA = "transf_rec"   # Transferência de outra corretora
    CREDITO_PROVENTO = "credito_prov"       # Crédito de provento
    PAGAMENTO_TAXA = "pagto_taxa"           # Pagamento de taxa/custódia
    PAGAMENTO_IMPOSTO = "pagto_imposto"     # Pagamento de imposto
    AJUSTE = "ajuste"                        # Ajuste manual
    OUTRO = "outro"                          # Outros tipos


class MovimentacaoCaixa(db.Model):
    """
    Model para movimentações de caixa em corretoras
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário
        corretora_id (UUID): ID da corretora (origem)
        tipo_movimentacao (TipoMovimentacao): Tipo da movimentação
        valor (Decimal): Valor da movimentação
        moeda (str): Moeda (BRL, USD, EUR)
        data_movimentacao (date): Data da movimentação
        corretora_destino_id (UUID): ID da corretora destino (transferências)
        provento_id (UUID): ID do provento (se for crédito de provento)
        descricao (str): Descrição da movimentação
        comprovante (str): Referência ao comprovante
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário proprietário
        corretora: Corretora origem
        corretora_destino: Corretora destino (para transferências)
        provento: Provento relacionado (para créditos)
    """
    
    __tablename__ = 'movimentacao_caixa'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da movimentação"
    )
    
    # Foreign keys obrigatórias
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
        comment="ID da corretora (origem)"
    )
    
    # Foreign keys opcionais
    corretora_destino_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('corretora.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="ID da corretora destino (apenas para transferências)"
    )
    
    provento_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('provento.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="ID do provento (apenas para crédito de provento)"
    )
    
    # Dados da movimentação
    tipo_movimentacao = db.Column(
        Enum(TipoMovimentacao),
        nullable=False,
        index=True,
        comment="Tipo da movimentação"
    )
    
    valor = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Valor da movimentação"
    )
    
    moeda = db.Column(
        String(3),
        nullable=False,
        default='BRL',
        index=True,
        comment="Código ISO 4217 da moeda (BRL, USD, EUR)"
    )
    
    data_movimentacao = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data da movimentação"
    )
    
    # Metadados
    descricao = db.Column(
        Text,
        nullable=True,
        comment="Descrição da movimentação"
    )
    
    comprovante = db.Column(
        String(200),
        nullable=True,
        comment="Referência ao comprovante (número, hash, arquivo)"
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
    usuario = relationship('Usuario', backref='movimentacoes_caixa', lazy='joined')
    corretora = relationship(
        'Corretora',
        foreign_keys=[corretora_id],
        backref='movimentacoes_caixa',
        lazy='joined'
    )
    corretora_destino = relationship(
        'Corretora',
        foreign_keys=[corretora_destino_id],
        lazy='joined'
    )
    provento = relationship('Provento', lazy='joined')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "valor > 0",
            name="movimentacao_valor_positivo"
        ),
        db.CheckConstraint(
            "moeda ~* '^[A-Z]{3}$'",
            name="movimentacao_moeda_iso_format"
        ),
        db.CheckConstraint(
            """
            (tipo_movimentacao IN ('transferencia_enviada', 'transferencia_recebida') 
             AND corretora_destino_id IS NOT NULL)
            OR 
            (tipo_movimentacao NOT IN ('transferencia_enviada', 'transferencia_recebida'))
            """,
            name="movimentacao_transferencia_tem_destino"
        ),
        db.CheckConstraint(
            """
            (tipo_movimentacao = 'credito_provento' AND provento_id IS NOT NULL)
            OR 
            (tipo_movimentacao != 'credito_provento')
            """,
            name="movimentacao_credito_tem_provento"
        ),
        {'comment': 'Tabela de movimentações de caixa em corretoras'}
    )
    
    def is_entrada(self):
        """Verifica se é movimentação de entrada (aumenta saldo)"""
        return self.tipo_movimentacao in [
            TipoMovimentacao.DEPOSITO,
            TipoMovimentacao.TRANSFERENCIA_RECEBIDA,
            TipoMovimentacao.CREDITO_PROVENTO,
            TipoMovimentacao.AJUSTE  # Depende do contexto, mas incluímos aqui
        ]
    
    def is_saida(self):
        """Verifica se é movimentação de saída (diminui saldo)"""
        return self.tipo_movimentacao in [
            TipoMovimentacao.SAQUE,
            TipoMovimentacao.TRANSFERENCIA_ENVIADA,
            TipoMovimentacao.PAGAMENTO_TAXA,
            TipoMovimentacao.PAGAMENTO_IMPOSTO
        ]
    
    def is_transferencia(self):
        """Verifica se é transferência entre corretoras"""
        return self.tipo_movimentacao in [
            TipoMovimentacao.TRANSFERENCIA_ENVIADA,
            TipoMovimentacao.TRANSFERENCIA_RECEBIDA
        ]
    
    def is_credito_provento(self):
        """Verifica se é crédito de provento"""
        return self.tipo_movimentacao == TipoMovimentacao.CREDITO_PROVENTO
    
    def impacto_saldo(self):
        """
        Calcula o impacto no saldo da corretora
        
        Returns:
            Decimal: Valor positivo para entradas, negativo para saídas
        """
        if self.is_entrada():
            return self.valor
        elif self.is_saida():
            return -self.valor
        return 0
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da movimentação
        """
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'corretora_id': str(self.corretora_id),
            'corretora_destino_id': str(self.corretora_destino_id) if self.corretora_destino_id else None,
            'provento_id': str(self.provento_id) if self.provento_id else None,
            'tipo_movimentacao': self.tipo_movimentacao.value if self.tipo_movimentacao else None,
            'valor': float(self.valor) if self.valor else 0,
            'moeda': self.moeda,
            'impacto_saldo': float(self.impacto_saldo()),
            'data_movimentacao': self.data_movimentacao.isoformat() if self.data_movimentacao else None,
            'descricao': self.descricao,
            'comprovante': self.comprovante,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        tipo = self.tipo_movimentacao.value if self.tipo_movimentacao else "N/A"
        sinal = "+" if self.is_entrada() else "-"
        return f"<MovimentacaoCaixa {tipo.upper()} {sinal} {self.moeda} {self.valor}>"
