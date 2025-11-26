# -*- coding: utf-8 -*-
"""
Exitus - Model Ativo
Entidade para instrumentos financeiros (ações, FIIs, REITs, bonds, criptomoedas)
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Enum, Numeric, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class TipoAtivo(enum.Enum):
    """Enum para tipos de ativo"""
    ACAO = "acao"              # Ação
    FII = "fii"                # Fundo Imobiliário
    REIT = "reit"              # Real Estate Investment Trust
    BOND = "bond"              # Título de renda fixa
    ETF = "etf"                # Exchange Traded Fund
    CRIPTO = "cripto"          # Criptomoeda
    OUTRO = "outro"            # Outros tipos


class ClasseAtivo(enum.Enum):
    """Enum para classes de ativo"""
    RENDA_VARIAVEL = "renda_variavel"
    RENDA_FIXA = "renda_fixa"
    CRIPTO = "cripto"
    HIBRIDO = "hibrido"


class Ativo(db.Model):
    """
    Model para ativos financeiros (ações, FIIs, REITs, bonds, criptomoedas)
    
    Attributes:
        id (UUID): Identificador único
        ticker (str): Código/símbolo do ativo (ex: PETR4, AAPL)
        nome (str): Nome completo do ativo
        tipo (TipoAtivo): Tipo do ativo
        classe (ClasseAtivo): Classe do ativo
        mercado (str): Mercado/país (BR, US, EUR)
        moeda (str): Moeda de negociação (BRL, USD, EUR)
        preco_atual (Decimal): Preço/cotação atual
        data_ultima_cotacao (datetime): Data da última cotação
        dividend_yield (Decimal): Dividend Yield (%)
        p_l (Decimal): Índice Preço/Lucro
        p_vp (Decimal): Índice Preço/Valor Patrimonial
        roe (Decimal): Return on Equity (%)
        ativo (bool): Indica se ativo está ativo para negociação
        deslistado (bool): Indica se foi deslistado da bolsa
        data_deslistagem (date): Data de deslistagem (se aplicável)
        observacoes (str): Observações gerais
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    
    Relationships:
        posicoes: Posições deste ativo nos portfolios
        transacoes: Transações realizadas com este ativo
        proventos: Proventos distribuídos por este ativo
        eventos_corporativos: Eventos corporativos deste ativo
    """
    
    __tablename__ = 'ativo'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do ativo"
    )
    
    # Identificação do ativo
    ticker = db.Column(
        String(20),
        nullable=False,
        index=True,
        comment="Código/símbolo do ativo (ex: PETR4, AAPL, BTC)"
    )
    
    nome = db.Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nome completo do ativo"
    )
    
    tipo = db.Column(
        Enum(TipoAtivo),
        nullable=False,
        index=True,
        comment="Tipo do ativo (ação, FII, REIT, bond, cripto)"
    )
    
    classe = db.Column(
        Enum(ClasseAtivo),
        nullable=False,
        index=True,
        comment="Classe do ativo (renda variável, fixa, cripto)"
    )
    
    # Mercado e moeda
    mercado = db.Column(
        String(10),
        nullable=False,
        default='BR',
        index=True,
        comment="Mercado/país de negociação (BR, US, EUR)"
    )
    
    moeda = db.Column(
        String(3),
        nullable=False,
        default='BRL',
        index=True,
        comment="Moeda de negociação (BRL, USD, EUR)"
    )
    
    # Cotação
    preco_atual = db.Column(
        Numeric(precision=18, scale=6),
        nullable=True,
        comment="Preço/cotação atual do ativo"
    )
    
    data_ultima_cotacao = db.Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data e hora da última cotação"
    )
    
    # Indicadores financeiros
    dividend_yield = db.Column(
        Numeric(precision=8, scale=4),
        nullable=True,
        comment="Dividend Yield em % (ex: 6.5000 = 6.5%)"
    )
    
    p_l = db.Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        comment="Índice Preço/Lucro"
    )
    
    p_vp = db.Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        comment="Índice Preço/Valor Patrimonial"
    )
    
    roe = db.Column(
        Numeric(precision=8, scale=4),
        nullable=True,
        comment="Return on Equity em %"
    )
    
    # Status
    ativo = db.Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica se ativo está disponível para negociação"
    )
    
    deslistado = db.Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Indica se ativo foi deslistado da bolsa"
    )
    
    data_deslistagem = db.Column(
        Date,
        nullable=True,
        comment="Data de deslistagem (se aplicável)"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações e notas sobre o ativo"
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
    
    # Relacionamentos futuros (descomentar quando criar os models)
    # posicoes = relationship('Posicao', back_populates='ativo', lazy='dynamic')
    # transacoes = relationship('Transacao', back_populates='ativo', lazy='dynamic')
    # proventos = relationship('Provento', back_populates='ativo', lazy='dynamic')
    # eventos_corporativos = relationship('EventoCorporativo', back_populates='ativo', lazy='dynamic')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "preco_atual IS NULL OR preco_atual >= 0",
            name="ativo_preco_positivo"
        ),
        db.CheckConstraint(
            "length(ticker) >= 1",
            name="ativo_ticker_min_length"
        ),
        db.CheckConstraint(
            "length(nome) >= 2",
            name="ativo_nome_min_length"
        ),
        db.UniqueConstraint(
            'ticker', 'mercado',
            name='unique_ativo_ticker_mercado'
        ),
        {'comment': 'Tabela de ativos financeiros (ações, FIIs, REITs, bonds, criptomoedas)'}
    )
    
    def is_active(self):
        """Verifica se ativo está ativo"""
        return self.ativo and not self.deslistado
    
    def is_renda_fixa(self):
        """Verifica se é ativo de renda fixa"""
        return self.classe == ClasseAtivo.RENDA_FIXA
    
    def is_renda_variavel(self):
        """Verifica se é ativo de renda variável"""
        return self.classe == ClasseAtivo.RENDA_VARIAVEL
    
    def is_cripto(self):
        """Verifica se é criptomoeda"""
        return self.tipo == TipoAtivo.CRIPTO or self.classe == ClasseAtivo.CRIPTO
    
    def atualizar_cotacao(self, preco, data_cotacao=None):
        """
        Atualiza a cotação do ativo
        
        Args:
            preco (Decimal): Novo preço
            data_cotacao (datetime): Data da cotação (default: agora)
        
        Raises:
            ValueError: Se preço for negativo
        """
        if preco < 0:
            raise ValueError(f"Preço não pode ser negativo: {preco}")
        
        self.preco_atual = preco
        self.data_ultima_cotacao = data_cotacao or datetime.utcnow()
    
    def atualizar_indicadores(self, dy=None, pl=None, pvp=None, roe_value=None):
        """
        Atualiza indicadores financeiros do ativo
        
        Args:
            dy (Decimal): Dividend Yield
            pl (Decimal): Índice P/L
            pvp (Decimal): Índice P/VP
            roe_value (Decimal): ROE
        """
        if dy is not None:
            self.dividend_yield = dy
        if pl is not None:
            self.p_l = pl
        if pvp is not None:
            self.p_vp = pvp
        if roe_value is not None:
            self.roe = roe_value
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados do ativo
        """
        return {
            'id': str(self.id),
            'ticker': self.ticker,
            'nome': self.nome,
            'tipo': self.tipo.value if self.tipo else None,
            'classe': self.classe.value if self.classe else None,
            'mercado': self.mercado,
            'moeda': self.moeda,
            'preco_atual': float(self.preco_atual) if self.preco_atual else None,
            'data_ultima_cotacao': self.data_ultima_cotacao.isoformat() if self.data_ultima_cotacao else None,
            'dividend_yield': float(self.dividend_yield) if self.dividend_yield else None,
            'p_l': float(self.p_l) if self.p_l else None,
            'p_vp': float(self.p_vp) if self.p_vp else None,
            'roe': float(self.roe) if self.roe else None,
            'ativo': self.ativo,
            'deslistado': self.deslistado,
            'data_deslistagem': self.data_deslistagem.isoformat() if self.data_deslistagem else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<Ativo {self.ticker} - {self.nome} ({self.mercado})>"
