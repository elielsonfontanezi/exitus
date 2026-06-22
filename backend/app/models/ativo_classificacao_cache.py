# -*- coding: utf-8 -*-
"""
Exitus - Model AtivoClassificacaoCache (BUG-020)

Cache de classificações de ativos para o classificador multi-camadas.
Armazena classificações curadas, manuais e obtidas via API externa,
com nível de confiança e origem (fonte) para rastreabilidade.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint
import uuid

from app.database import db
from app.models.ativo import TipoAtivo, ClasseAtivo


class FonteClassificacao(enum.Enum):
    """Origem da classificação armazenada."""
    SEED = "seed"
    MANUAL = "manual"
    API = "api"
    HEURISTICA = "heuristica"


class NivelConfianca(enum.Enum):
    """Nível de confiança da classificação."""
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class AtivoClassificacaoCache(db.Model):
    """Cache de classificações de ativos (seeds, manuais, API, heurística)."""
    __tablename__ = 'ativo_classificacao_cache'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)

    tipo = Column(
        Enum(TipoAtivo, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    classe = Column(
        Enum(ClasseAtivo, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    mercado = Column(String(10), nullable=False)
    moeda = Column(String(3), nullable=False)

    fonte = Column(
        Enum(FonteClassificacao, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    confianca = Column(
        Enum(NivelConfianca, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    usuario_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    observacoes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            'ticker', 'usuario_id',
            name='uq_ativo_classificacao_cache_ticker_usuario',
            deferrable=False,
        ),
        Index(
            'ix_ativo_classificacao_cache_ticker_fonte',
            'ticker', 'fonte',
        ),
    )

    def __repr__(self):
        return f"<AtivoClassificacaoCache {self.ticker} ({self.fonte.value})>"
