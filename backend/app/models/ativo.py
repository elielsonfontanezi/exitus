# backend/app/models/ativo.py
"""
Exitus - Model Ativo - Entidade para instrumentos financeiros (COBERTURA GLOBAL)
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Numeric, Text, Date, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import db


class TipoAtivo(enum.Enum):
    """Enum para tipos de ativo - 14 tipos (Multi-Mercado)"""
    # Mercado BR
    ACAO = "acao"                    # Ações Brasil (B3)
    FII = "fii"                      # Fundos Imobiliários BR
    CDB = "cdb"                      # Certificado de Depósito Bancário BR
    LCI_LCA = "lci_lca"             # Letra de Crédito Imobiliário/Agrícola BR
    TESOURO_DIRETO = "tesouro_direto"  # Tesouro Direto BR
    DEBENTURE = "debenture"          # Debêntures BR
    
    # Mercado US
    STOCK = "stock"                  # Ações US (NYSE, NASDAQ)
    REIT = "reit"                    # Real Estate Investment Trust US
    BOND = "bond"                    # Bonds US (corporativo, governamental)
    ETF = "etf"                      # Exchange Traded Funds US
    
    # Mercado INTL (EU/ASIA)
    STOCK_INTL = "stock_intl"       # Ações Internacionais (EU, ASIA)
    ETF_INTL = "etf_intl"           # ETFs Internacionais
    
    # Mercado BR — especial
    UNIT = "unit"                    # Certificados de depósito (UNITs B3 — ex: TAEE11, KLBN11)

    # Outros
    CRIPTO = "cripto"                # Criptomoedas
    OUTRO = "outro"                  # Outros ativos

class ClasseAtivo(enum.Enum):
    """Classes de ativos para alocação de portfólio"""
    RENDA_VARIAVEL = "renda_variavel"
    RENDA_FIXA = "renda_fixa"
    CRIPTO = "cripto"
    COMMODITY = "commodity"
    HIBRIDO = "hibrido"


class Mercado(enum.Enum):
    """Regiões/mercados principais (para filtros e agregações)"""
    BR = "BR"        # Brasil (B3)
    US = "US"        # Estados Unidos
    EU = "EU"        # Europa
    ASIA = "ASIA"    # Ásia
    GLOBAL = "GLOBAL"  # Ativos globais (ETFs internacionais, criptomoedas)


# Mapeamento de bolsas específicas → região (para seeds e conversões)
BOLSA_TO_MERCADO = {
    # Estados Unidos
    'NYSE': 'US',
    'NASDAQ': 'US',
    'AMEX': 'US',
    'OTC': 'US',
    
    # Europa
    'EURONEXT': 'EU',
    'LSE': 'EU',        # London Stock Exchange
    'XETRA': 'EU',      # Deutsche Börse
    'BME': 'EU',        # Bolsa de Madrid
    'BORSA': 'EU',      # Borsa Italiana
    
    # Ásia
    'TSE': 'ASIA',      # Tokyo Stock Exchange
    'HKEX': 'ASIA',     # Hong Kong
    'SSE': 'ASIA',      # Shanghai
    'SZSE': 'ASIA',     # Shenzhen
    'KRX': 'ASIA',      # Korea Exchange
    
    # Brasil
    'B3': 'BR',
    'BOVESPA': 'BR',    # Legacy
    
    # Global
    'CRIPTO': 'GLOBAL',
    'CRYPTO': 'GLOBAL',
}


# Mapeamento inverso: região → sufixo para APIs (yfinance)
MERCADO_TO_SUFFIX = {
    'BR': '.SA',    # Brasil requer .SA
    'US': '',       # EUA sem sufixo
    'EU': '',       # Europa sem sufixo (depende da bolsa)
    'ASIA': '',     # Ásia sem sufixo (depende da bolsa)
    'GLOBAL': '',   # Global sem sufixo
}


class Ativo(db.Model):
    """Model para ativos financeiros - Cobertura Global"""
    __tablename__ = 'ativo'
    
    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    
    # Classificação
    tipo = Column(Enum(TipoAtivo, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    classe = Column(Enum(ClasseAtivo, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    mercado = Column(String(10), nullable=False, index=True)  # BR, US, EU, ASIA, GLOBAL
    moeda = Column(String(3), nullable=False)
    
    # Indicadores Fundamentalistas
    preco_atual = Column(Numeric(15, 2), nullable=True)
    dividend_yield = Column(Numeric(5, 4), nullable=True)
    p_l = Column(Numeric(10, 2), nullable=True)
    p_vp = Column(Numeric(10, 2), nullable=True)
    roe = Column(Numeric(5, 4), nullable=True)
    beta = Column(Numeric(5, 2), nullable=True)
    
    # Indicadores para Valuation
    preco_teto = Column(Numeric(15, 2), nullable=True)
    cap_rate = Column(Numeric(8, 4), nullable=True)  # Para FIIs/REITs

    # Campos de Renda Fixa (RFCALC-001)
    taxa_cupom = Column(Numeric(8, 6), nullable=True)      # Taxa de cupom anual (ex: 0.1050 = 10,50%)
    valor_nominal = Column(Numeric(15, 2), nullable=True)  # Valor nominal/face do título
    data_vencimento = Column(Date, nullable=True)          # Vencimento do título RF

    # Campos de FII/REIT (RFCALC-001)
    ffo_por_cota = Column(Numeric(10, 4), nullable=True)   # Funds From Operations por cota
    affo_por_cota = Column(Numeric(10, 4), nullable=True)  # Adjusted FFO por cota
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False, index=True)
    deslistado = Column(Boolean, default=False, nullable=False, index=True)
    data_deslistagem = Column(Date, nullable=True)
    data_ultima_cotacao = Column(DateTime, nullable=True, index=True)
    
    # Metadata
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraint de unicidade: ticker deve ser único por mercado
    __table_args__ = (
        db.UniqueConstraint('ticker', 'mercado', name='uq_ativo_ticker_mercado'),
        db.Index('ix_ativo_data_vencimento', 'data_vencimento'),
    )
    
    def __repr__(self):
        return f"<Ativo {self.ticker} ({self.mercado})>"
    
    def to_dict(self):
        """Serializa ativo para JSON"""
        return {
            'id': str(self.id),
            'ticker': self.ticker,
            'nome': self.nome,
            'tipo': self.tipo.value if self.tipo else None,
            'classe': self.classe.value if self.classe else None,
            'mercado': self.mercado,
            'moeda': self.moeda,
            'preco_atual': float(self.preco_atual) if self.preco_atual else None,
            'dividend_yield': float(self.dividend_yield) if self.dividend_yield else None,
            'p_l': float(self.p_l) if self.p_l else None,
            'p_vp': float(self.p_vp) if self.p_vp else None,
            'roe': float(self.roe) if self.roe else None,
            'beta': float(self.beta) if self.beta else None,
            'preco_teto': float(self.preco_teto) if self.preco_teto else None,
            'cap_rate': float(self.cap_rate) if self.cap_rate else None,
            'taxa_cupom': float(self.taxa_cupom) if self.taxa_cupom else None,
            'valor_nominal': float(self.valor_nominal) if self.valor_nominal else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'ffo_por_cota': float(self.ffo_por_cota) if self.ffo_por_cota else None,
            'affo_por_cota': float(self.affo_por_cota) if self.affo_por_cota else None,
            'ativo': self.ativo,
            'deslistado': self.deslistado,
            'data_deslistagem': self.data_deslistagem.isoformat() if self.data_deslistagem else None,
            'data_ultima_cotacao': self.data_ultima_cotacao.isoformat() if self.data_ultima_cotacao else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def get_ticker_api(self):
        """Retorna ticker formatado para APIs externas (yfinance)"""
        suffix = MERCADO_TO_SUFFIX.get(self.mercado, '')
        return f"{self.ticker}{suffix}"
