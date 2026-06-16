# -*- coding: utf-8 -*-
"""
Exitus - Model FeriadoMercado
Entidade para feriados e dias sem pregão
"""

from datetime import datetime, time
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Enum, Text, Date, Time
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class TipoFeriado(enum.Enum):
    """Enum para tipos de feriado"""
    NACIONAL = "nacional"            # Feriado nacional
    BOLSA = "bolsa"                  # Feriado específico da bolsa
    PONTE = "ponte"                  # Ponto facultativo
    FECHAMENTO_ANTECIPADO = "antecip"  # Fechamento antecipado
    MANUTENCAO = "manutencao"        # Manutenção de sistemas
    OUTRO = "outro"                  # Outros tipos


class FeriadoMercado(db.Model):
    """
    Model para feriados e dias sem pregão
    
    Attributes:
        id (UUID): Identificador único
        pais (str): País do feriado (código ISO)
        mercado (str): Mercado/bolsa específica
        data_feriado (date): Data do feriado
        tipo_feriado (TipoFeriado): Tipo do feriado
        nome (str): Nome do feriado
        horario_fechamento (time): Horário de fechamento antecipado
        recorrente (bool): Se é feriado anual fixo
        observacoes (str): Observações sobre o feriado
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    """
    
    __tablename__ = 'feriado_mercado'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do feriado"
    )
    
    # Localização
    pais = db.Column(
        String(2),
        nullable=False,
        index=True,
        comment="Código ISO do país (BR, US, etc.)"
    )
    
    mercado = db.Column(
        String(20),
        nullable=True,
        index=True,
        comment="Mercado/bolsa específica (B3, NYSE, NASDAQ, etc.) - NULL = todos"
    )
    
    # Dados do feriado
    data_feriado = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data do feriado"
    )
    
    tipo_feriado = db.Column(
        Enum(TipoFeriado),
        nullable=False,
        index=True,
        comment="Tipo do feriado"
    )
    
    nome = db.Column(
        String(200),
        nullable=False,
        comment="Nome do feriado"
    )
    
    horario_fechamento = db.Column(
        Time,
        nullable=True,
        comment="Horário de fechamento antecipado (se aplicável)"
    )
    
    recorrente = db.Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Indica se é feriado anual fixo (sempre no mesmo dia/mês)"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações sobre o feriado"
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
            "pais ~* '^[A-Z]{2}$'",
            name="feriado_pais_iso_format"
        ),
        db.CheckConstraint(
            "length(nome) >= 3",
            name="feriado_nome_min_length"
        ),
        db.UniqueConstraint(
            'pais', 'mercado', 'data_feriado',
            name='unique_feriado_pais_mercado_data'
        ),
        {'comment': 'Tabela de feriados e dias sem pregão nos mercados'}
    )
    
    def is_fechamento_total(self):
        """Verifica se é fechamento total (não há pregão)"""
        return self.tipo_feriado in [
            TipoFeriado.NACIONAL,
            TipoFeriado.BOLSA,
            TipoFeriado.PONTE
        ]
    
    def is_fechamento_antecipado(self):
        """Verifica se é fechamento antecipado"""
        return self.tipo_feriado == TipoFeriado.FECHAMENTO_ANTECIPADO
    
    def is_recorrente(self):
        """Verifica se é feriado recorrente (anual)"""
        return self.recorrente
    
    def dias_ate_feriado(self):
        """
        Calcula quantos dias faltam para o feriado
        
        Returns:
            int: Dias até feriado (negativo se já passou)
        """
        hoje = datetime.utcnow().date()
        delta = self.data_feriado - hoje
        return delta.days
    
    def is_hoje(self):
        """Verifica se o feriado é hoje"""
        return self.data_feriado == datetime.utcnow().date()
    
    def is_futuro(self):
        """Verifica se o feriado é no futuro"""
        return self.data_feriado > datetime.utcnow().date()
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados do feriado
        """
        return {
            'id': str(self.id),
            'pais': self.pais,
            'mercado': self.mercado,
            'data_feriado': self.data_feriado.isoformat() if self.data_feriado else None,
            'tipo_feriado': self.tipo_feriado.value if self.tipo_feriado else None,
            'nome': self.nome,
            'horario_fechamento': self.horario_fechamento.isoformat() if self.horario_fechamento else None,
            'recorrente': self.recorrente,
            'is_fechamento_total': self.is_fechamento_total(),
            'is_fechamento_antecipado': self.is_fechamento_antecipado(),
            'dias_ate_feriado': self.dias_ate_feriado(),
            'is_hoje': self.is_hoje(),
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<FeriadoMercado {self.pais} {self.data_feriado} - {self.nome}>"
