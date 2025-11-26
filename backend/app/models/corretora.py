# -*- coding: utf-8 -*-
"""
Exitus - Model Corretora
Entidade para gestão de contas de investimento (corretoras e exchanges)
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Enum, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum


class TipoCorretora(enum.Enum):
    """Enum para tipos de corretora"""
    CORRETORA = "corretora"  # Corretora tradicional
    EXCHANGE = "exchange"     # Exchange de criptomoedas


class Corretora(db.Model):
    """
    Model para corretoras/exchanges de investimento
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário proprietário
        nome (str): Nome da corretora
        tipo (TipoCorretora): Tipo (corretora ou exchange)
        pais (str): Código ISO do país (BR, US, etc.)
        moeda_padrao (str): Moeda padrão (BRL, USD, EUR)
        saldo_atual (Decimal): Saldo disponível em caixa
        ativa (bool): Indica se conta está ativa
        observacoes (str): Observações do usuário
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário proprietário da conta
        posicoes: Posições de ativos nesta corretora
        transacoes: Transações realizadas nesta corretora
        movimentacoes_caixa: Movimentações de caixa desta corretora
    """
    
    __tablename__ = 'corretora'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da corretora"
    )
    
    # Foreign key para Usuario
    usuario_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID do usuário proprietário"
    )
    
    # Dados da corretora
    nome = db.Column(
        String(100),
        nullable=False,
        index=True,
        comment="Nome da corretora/exchange (ex: XP, Clear, Binance)"
    )
    
    tipo = db.Column(
        Enum(TipoCorretora),
        default=TipoCorretora.CORRETORA,
        nullable=False,
        index=True,
        comment="Tipo: corretora tradicional ou exchange cripto"
    )
    
    pais = db.Column(
        String(2),
        nullable=False,
        default='BR',
        index=True,
        comment="Código ISO 3166-1 alpha-2 do país (BR, US, etc.)"
    )
    
    moeda_padrao = db.Column(
        String(3),
        nullable=False,
        default='BRL',
        index=True,
        comment="Código ISO 4217 da moeda (BRL, USD, EUR)"
    )
    
    saldo_atual = db.Column(
        Numeric(precision=18, scale=2),
        default=0.00,
        nullable=False,
        comment="Saldo disponível em caixa (na moeda padrão)"
    )
    
    # Status e metadados
    ativa = db.Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica se conta está ativa"
    )
    
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações e notas do usuário sobre a conta"
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
    usuario = relationship(
        'Usuario',
        backref='corretoras',
        lazy='joined'
    )
    
    # Relacionamentos futuros (descomentar quando criar os models)
    # posicoes = relationship('Posicao', back_populates='corretora', lazy='dynamic')
    # transacoes = relationship('Transacao', back_populates='corretora', lazy='dynamic')
    # movimentacoes_caixa = relationship('MovimentacaoCaixa', back_populates='corretora', lazy='dynamic')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "saldo_atual >= 0",
            name="corretora_saldo_positivo"
        ),
        db.CheckConstraint(
            "length(nome) >= 2",
            name="corretora_nome_min_length"
        ),
        db.CheckConstraint(
            "pais ~* '^[A-Z]{2}$'",
            name="corretora_pais_iso_format"
        ),
        db.CheckConstraint(
            "moeda_padrao ~* '^[A-Z]{3}$'",
            name="corretora_moeda_iso_format"
        ),
        db.UniqueConstraint(
            'usuario_id', 'nome', 'pais',
            name='unique_corretora_usuario_nome_pais'
        ),
        {'comment': 'Tabela de corretoras e contas de investimento'}
    )
    
    def is_active(self):
        """Verifica se corretora está ativa"""
        return self.ativa
    
    def is_exchange(self):
        """Verifica se é exchange de criptomoedas"""
        return self.tipo == TipoCorretora.EXCHANGE
    
    def atualizar_saldo(self, valor, operacao='credito'):
        """
        Atualiza o saldo da corretora
        
        Args:
            valor (Decimal): Valor a ser creditado/debitado
            operacao (str): 'credito' ou 'debito'
        
        Raises:
            ValueError: Se saldo ficar negativo ou operação inválida
        """
        if operacao == 'credito':
            self.saldo_atual += valor
        elif operacao == 'debito':
            if self.saldo_atual < valor:
                raise ValueError(f"Saldo insuficiente. Disponível: {self.saldo_atual}, Solicitado: {valor}")
            self.saldo_atual -= valor
        else:
            raise ValueError(f"Operação inválida: {operacao}. Use 'credito' ou 'debito'")
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da corretora
        """
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'nome': self.nome,
            'tipo': self.tipo.value if self.tipo else TipoCorretora.CORRETORA.value,
            'pais': self.pais,
            'moeda_padrao': self.moeda_padrao,
            'saldo_atual': float(self.saldo_atual) if self.saldo_atual else 0.0,
            'ativa': self.ativa,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<Corretora {self.nome} ({self.pais}/{self.moeda_padrao})>"
