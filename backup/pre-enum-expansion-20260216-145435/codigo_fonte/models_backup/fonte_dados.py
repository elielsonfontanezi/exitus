# -*- coding: utf-8 -*-
"""
Exitus - Model FonteDados
Entidade para gerenciamento de fontes de dados externas (APIs)
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class TipoFonteDados(enum.Enum):
    """Enum para tipos de fonte de dados"""
    API = "api"              # API RESTful
    SCRAPER = "scraper"      # Web scraping
    MANUAL = "manual"        # Entrada manual
    ARQUIVO = "arquivo"      # Import de arquivo
    OUTRO = "outro"          # Outros tipos


class FonteDados(db.Model):
    """
    Model para fontes de dados externas
    
    Attributes:
        id (UUID): Identificador único
        nome (str): Nome da fonte
        tipo_fonte (TipoFonteDados): Tipo da fonte
        url_base (str): URL base da API/fonte
        requer_autenticacao (bool): Se requer chave API
        rate_limit (str): Limite de requisições
        ativa (bool): Se fonte está ativa
        prioridade (int): Ordem de prioridade (1 = maior)
        ultima_consulta (datetime): Timestamp da última consulta
        total_consultas (int): Total de consultas realizadas
        total_erros (int): Total de erros encontrados
        observacoes (str): Observações sobre a fonte
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    """
    
    __tablename__ = 'fonte_dados'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da fonte"
    )
    
    # Identificação
    nome = db.Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome da fonte de dados (ex: yfinance, Alpha Vantage)"
    )
    
    tipo_fonte = db.Column(
        Enum(TipoFonteDados),
        nullable=False,
        index=True,
        comment="Tipo da fonte de dados"
    )
    
    url_base = db.Column(
        String(500),
        nullable=True,
        comment="URL base da API ou site"
    )
    
    # Configurações
    requer_autenticacao = db.Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica se requer chave API ou autenticação"
    )
    
    rate_limit = db.Column(
        String(50),
        nullable=True,
        comment="Limite de requisições (ex: '5/minute', '500/day')"
    )
    
    ativa = db.Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica se fonte está ativa"
    )
    
    prioridade = db.Column(
        Integer,
        default=100,
        nullable=False,
        index=True,
        comment="Ordem de prioridade (1 = maior prioridade)"
    )
    
    # Estatísticas
    ultima_consulta = db.Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp da última consulta bem-sucedida"
    )
    
    total_consultas = db.Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total de consultas realizadas"
    )
    
    total_erros = db.Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total de erros encontrados"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações sobre a fonte de dados"
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
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "prioridade > 0",
            name="fonte_prioridade_positiva"
        ),
        db.CheckConstraint(
            "total_consultas >= 0",
            name="fonte_consultas_positivas"
        ),
        db.CheckConstraint(
            "total_erros >= 0",
            name="fonte_erros_positivos"
        ),
        db.CheckConstraint(
            "length(nome) >= 2",
            name="fonte_nome_min_length"
        ),
        {'comment': 'Tabela de fontes de dados externas (APIs, scrapers)'}
    )
    
    def is_active(self):
        """Verifica se fonte está ativa"""
        return self.ativa
    
    def is_api(self):
        """Verifica se é API"""
        return self.tipo_fonte == TipoFonteDados.API
    
    def registrar_consulta_sucesso(self):
        """Registra uma consulta bem-sucedida"""
        # Garantir valores não-None
        if self.total_consultas is None:
            self.total_consultas = 0
        if self.total_erros is None:
            self.total_erros = 0
        
        self.ultima_consulta = datetime.utcnow()
        self.total_consultas += 1

    def registrar_erro(self):
        """Registra um erro na consulta"""
        # Garantir valores não-None
        if self.total_consultas is None:
            self.total_consultas = 0
        if self.total_erros is None:
            self.total_erros = 0
        
        self.total_erros += 1
        self.total_consultas += 1

    def taxa_sucesso(self):
        """
        Calcula a taxa de sucesso das consultas
        
        Returns:
            float: Percentual de sucesso (0-100)
        """
        total = self.total_consultas if self.total_consultas else 0
        erros = self.total_erros if self.total_erros else 0
        
        if total > 0:
            sucessos = total - erros
            return (sucessos / total) * 100
        return 100.0  # Sem consultas = 100% por padrão

    def taxa_erro(self):
        """
        Calcula a taxa de erro das consultas
        
        Returns:
            float: Percentual de erro (0-100)
        """
        total = self.total_consultas if self.total_consultas else 0
        erros = self.total_erros if self.total_erros else 0
        
        if total > 0:
            return (erros / total) * 100
        return 0.0

    def health_status(self):
        """
        Determina o status de saúde da fonte
        
        Returns:
            str: 'healthy', 'degraded', 'down', 'unknown'
        """
        total = self.total_consultas if self.total_consultas else 0
        
        if total == 0:
            return 'unknown'
        
        taxa_sucesso = self.taxa_sucesso()
        
        if taxa_sucesso >= 95:
            return 'healthy'
        elif taxa_sucesso >= 80:
            return 'degraded'
        else:
            return 'down'

    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da fonte
        """
        return {
            'id': str(self.id),
            'nome': self.nome,
            'tipo_fonte': self.tipo_fonte.value if self.tipo_fonte else None,
            'url_base': self.url_base,
            'requer_autenticacao': self.requer_autenticacao,
            'rate_limit': self.rate_limit,
            'ativa': self.ativa,
            'prioridade': self.prioridade,
            'ultima_consulta': self.ultima_consulta.isoformat() if self.ultima_consulta else None,
            'total_consultas': self.total_consultas,
            'total_erros': self.total_erros,
            'taxa_sucesso': round(self.taxa_sucesso(), 2),
            'taxa_erro': round(self.taxa_erro(), 2),
            'health_status': self.health_status(),
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        status = "✓" if self.ativa else "✗"
        return f"<FonteDados {status} {self.nome} (prioridade {self.prioridade})>"
