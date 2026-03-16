# -- coding: utf-8 --
# Exitus - Modelo Transacao - Módulo 2 Fase 2.2.4
# v0.7.13 — GAP-001: @property custo_total (soma dinâmica dos 5 sub-campos)

import enum
from datetime import datetime
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import db


class TipoTransacao(enum.Enum):
    COMPRA       = 'compra'
    VENDA        = 'venda'
    DIVIDENDO    = 'dividendo'
    JCP          = 'jcp'
    ALUGUEL      = 'aluguel'
    BONIFICACAO  = 'bonificacao'
    SPLIT        = 'split'
    GRUPAMENTO   = 'grupamento'
    SUBSCRICAO   = 'subscricao'
    AMORTIZACAO  = 'amortizacao'


class Transacao(db.Model):
    """
    Modelo de Transação. Representa operações financeiras do usuário:
    - Compra/venda de ativos
    - Recebimento de dividendos/JCP
    - Eventos corporativos (bonificação, desdobramento, grupamento)
    """
    __tablename__ = 'transacao'

    # --- Identificação ---
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id  = Column(UUID(as_uuid=True), ForeignKey('usuario.id'), nullable=False)
    tipo        = Column(
        Enum(TipoTransacao, name='tipotransacao', create_type=False,
             values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # --- Relacionamentos ---
    ativo_id    = Column(UUID(as_uuid=True), ForeignKey('ativo.id'), nullable=False)
    corretora_id = Column(UUID(as_uuid=True), ForeignKey('corretora.id'), nullable=False)
    assessora_id = Column(UUID(as_uuid=True), ForeignKey('assessora.id', ondelete='CASCADE'), nullable=True, index=True)

    # --- Dados da transação ---
    data_transacao  = Column(DateTime(timezone=True), nullable=False)
    quantidade      = Column(Numeric(18, 8), nullable=False)
    preco_unitario  = Column(Numeric(18, 6), nullable=False)
    valor_total     = Column(Numeric(18, 2), nullable=False)  # quantidade × preco_unitario

    # --- Custos operacionais ---
    taxa_corretagem = Column(Numeric(18, 2), nullable=False, default=0)
    taxa_liquidacao = Column(Numeric(18, 2), nullable=False, default=0)
    emolumentos     = Column(Numeric(18, 2), nullable=False, default=0)
    imposto         = Column(Numeric(18, 2), nullable=False, default=0)
    outros_custos   = Column(Numeric(18, 2), nullable=False, default=0)

    # --- Totalizadores ---
    custos_totais   = Column(Numeric(18, 2), nullable=False, default=0)
    valor_liquido   = Column(Numeric(18, 2), nullable=False)  # valor_total ± custos

    # --- Metadados ---
    observacoes      = Column(Text, nullable=True)
    hash_importacao  = Column(sa.String(64), nullable=True, index=True,
                              comment="Hash MD5 da linha original do arquivo B3 para deduplicação")
    arquivo_origem   = Column(sa.String(255), nullable=True,
                              comment="Nome do arquivo B3 de origem da importação")
    created_at  = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at  = Column(DateTime(timezone=True), nullable=False,
                         default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- ORM relationships ---
    assessora = relationship('Assessora', back_populates='transacoes')
    usuario  = relationship('Usuario', backref='transacoes', lazy=True)
    ativo    = relationship('Ativo', backref='transacoes',
                            primaryjoin='Transacao.ativo_id == Ativo.id', lazy=True)
    corretora = relationship('Corretora', backref='transacoes', lazy=True)

    # -----------------------------------------------------------------------
    # GAP-001 — @property custo_total
    # Calcula dinamicamente a soma dos 5 sub-campos de custo operacional.
    # NÃO depende da coluna física custos_totais (que pode ficar dessincronizada).
    # Retorna float para facilitar serialização Marshmallow via fields.Method.
    # -----------------------------------------------------------------------
    @property
    def custo_total(self) -> float:
        """Soma dinâmica dos custos operacionais da transação."""
        taxa_c = self.taxa_corretagem or Decimal('0')
        taxa_l = self.taxa_liquidacao or Decimal('0')
        emol   = self.emolumentos    or Decimal('0')
        imp    = self.imposto        or Decimal('0')
        outros = self.outros_custos  or Decimal('0')
        return float(taxa_c + taxa_l + emol + imp + outros)

    def __repr__(self):
        return (f'<Transacao {self.tipo.value} '
                f'{self.quantidade} '
                f'{self.ativo.ticker if self.ativo else "?"} '
                f'{self.data_transacao.date()}>')

    def to_dict(self):
        """Serializa transação para dict."""
        return {
            'id':               str(self.id),
            'usuario_id':       str(self.usuario_id),
            'tipo':             self.tipo.value,
            'ativo_id':         str(self.ativo_id),
            'corretora_id':     str(self.corretora_id),
            'data_transacao':   self.data_transacao.isoformat(),
            'quantidade':       str(self.quantidade),
            'preco_unitario':   str(self.preco_unitario),
            'valor_total':      str(self.valor_total),
            'taxa_corretagem':  str(self.taxa_corretagem),
            'taxa_liquidacao':  str(self.taxa_liquidacao),
            'emolumentos':      str(self.emolumentos),
            'imposto':          str(self.imposto),
            'outros_custos':    str(self.outros_custos),
            'custos_totais':    str(self.custos_totais),
            'custo_total':      self.custo_total,   # GAP-001: campo calculado
            'valor_liquido':    str(self.valor_liquido),
            'observacoes':      self.observacoes,
            'created_at':       self.created_at.isoformat(),
            'updated_at':       self.updated_at.isoformat(),
        }
