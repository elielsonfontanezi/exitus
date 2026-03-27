# -*- coding: utf-8 -*-
"""
Exitus - Model EventoCorporativo
Entidade para eventos corporativos que afetam ativos
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, DateTime, Enum, Boolean, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum


class TipoEventoCorporativo(enum.Enum):
    """Enum para tipos de evento corporativo"""
    SPLIT = "split"                          # Desdobramento (ex: 1 ação vira 2)
    GRUPAMENTO = "grupamento"                # Grupamento/Inplit (ex: 10 ações viram 1)
    BONIFICACAO = "bonificacao"              # Bonificação em ações
    DIREITO_SUBSCRICAO = "direito_sub"       # Direito de subscrição
    FUSAO = "fusao"                          # Fusão com outra empresa
    CISAO = "cisao"                          # Cisão (spin-off)
    INCORPORACAO = "incorporacao"            # Incorporação por outra empresa
    MUDANCA_TICKER = "mudanca_ticker"        # Mudança de código
    DESLISTAGEM = "deslistagem"              # Deslistagem da bolsa
    RELISTING = "relisting"                  # Relistagem
    CANCELAMENTO = "cancelamento"            # Cancelamento de ações
    OUTRO = "outro"                          # Outros eventos


class EventoCorporativo(db.Model):
    """
    Model para eventos corporativos que afetam ativos
    
    Attributes:
        id (UUID): Identificador único
        ativo_id (UUID): ID do ativo afetado
        tipo_evento (TipoEventoCorporativo): Tipo do evento
        data_evento (date): Data do evento
        data_com (date): Data COM (último dia para ter direito)
        proporcao (str): Proporção do evento (ex: "2:1", "1:10")
        ativo_novo_id (UUID): ID do novo ativo (fusões, mudanças)
        descricao (str): Descrição detalhada do evento
        impacto_posicoes (bool): Indica se posições já foram ajustadas
        observacoes (str): Observações adicionais
        created_at (datetime): Data de criação do registro
        updated_at (datetime): Data da última atualização
    
    Relationships:
        ativo: Ativo original afetado
        ativo_novo: Novo ativo (para fusões, mudanças de ticker)
    """
    
    __tablename__ = 'evento_corporativo'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do evento"
    )
    
    # Foreign keys
    ativo_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('ativo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="ID do ativo afetado pelo evento"
    )
    
    ativo_novo_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('ativo.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="ID do novo ativo (fusões, mudanças de ticker)"
    )
    
    # Dados do evento
    tipo_evento = db.Column(
        Enum(TipoEventoCorporativo),
        nullable=False,
        index=True,
        comment="Tipo do evento corporativo"
    )
    
    data_evento = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data do evento"
    )
    
    data_com = db.Column(
        Date,
        nullable=True,
        index=True,
        comment="Data COM (último dia para ter direito ao evento)"
    )
    
    proporcao = db.Column(
        String(20),
        nullable=True,
        comment="Proporção do evento (ex: '2:1', '1:10', '1:1.5')"
    )
    
    descricao = db.Column(
        Text,
        nullable=False,
        comment="Descrição detalhada do evento"
    )
    
    # Controle de processamento
    impacto_posicoes = db.Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Indica se as posições já foram ajustadas"
    )
    
    # Metadados
    observacoes = db.Column(
        Text,
        nullable=True,
        comment="Observações adicionais sobre o evento"
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
    ativo = relationship(
        'Ativo',
        foreign_keys=[ativo_id],
        backref='eventos_corporativos',
        lazy='joined'
    )
    ativo_novo = relationship(
        'Ativo',
        foreign_keys=[ativo_novo_id],
        lazy='joined'
    )
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "data_com IS NULL OR data_com <= data_evento",
            name="evento_data_com_valida"
        ),
        db.CheckConstraint(
            """
            (tipo_evento IN ('split', 'grupamento', 'bonificacao') AND proporcao IS NOT NULL)
            OR 
            (tipo_evento NOT IN ('split', 'grupamento', 'bonificacao'))
            """,
            name="evento_proporcao_obrigatoria"
        ),
        {'comment': 'Tabela de eventos corporativos que afetam ativos'}
    )
    
    def is_split(self):
        """Verifica se é split (desdobramento)"""
        return self.tipo_evento == TipoEventoCorporativo.SPLIT
    
    def is_grupamento(self):
        """Verifica se é grupamento (inplit)"""
        return self.tipo_evento == TipoEventoCorporativo.GRUPAMENTO
    
    def is_bonificacao(self):
        """Verifica se é bonificação"""
        return self.tipo_evento == TipoEventoCorporativo.BONIFICACAO
    
    def is_mudanca_ticker(self):
        """Verifica se é mudança de ticker"""
        return self.tipo_evento == TipoEventoCorporativo.MUDANCA_TICKER
    
    def parse_proporcao(self):
        """
        Faz parse da proporção do evento
        
        Returns:
            tuple: (numerador, denominador) ou None se inválido
            
        Examples:
            "2:1" -> (2.0, 1.0) # Split 2 para 1
            "1:10" -> (1.0, 10.0) # Grupamento 1 para 10
            "1:1.5" -> (1.0, 1.5) # Bonificação 50%
        """
        if not self.proporcao:
            return None
        
        try:
            parts = self.proporcao.split(':')
            if len(parts) == 2:
                return (float(parts[0]), float(parts[1]))
        except (ValueError, IndexError):
            pass
        
        return None
    
    def calcular_fator_ajuste(self):
        """
        Calcula o fator de ajuste para quantidade de ativos
        
        Returns:
            float: Fator multiplicador (ex: 2.0 para split 2:1, 0.1 para grupamento 1:10)
        """
        proporcao = self.parse_proporcao()
        if not proporcao:
            return 1.0
        
        numerador, denominador = proporcao
        
        if self.is_split() or self.is_bonificacao():
            # Split 2:1 ou Bonificação 1:1.5 -> multiplica quantidade
            return numerador / denominador
        elif self.is_grupamento():
            # Grupamento 1:10 -> divide quantidade (inverte proporção)
            return numerador / denominador
        
        return 1.0
    
    def calcular_fator_ajuste_preco(self):
        """
        Calcula o fator de ajuste para preço médio
        (inverso do ajuste de quantidade)
        
        Returns:
            float: Fator divisor para preço
        """
        fator_quantidade = self.calcular_fator_ajuste()
        if fator_quantidade > 0:
            return 1.0 / fator_quantidade
        return 1.0
    
    def marcar_como_processado(self):
        """Marca o evento como processado (posições ajustadas)"""
        self.impacto_posicoes = True
    
    def dias_ate_evento(self):
        """
        Calcula quantos dias faltam para o evento
        
        Returns:
            int: Dias até evento (negativo se já ocorreu)
        """
        hoje = datetime.utcnow().date()
        delta = self.data_evento - hoje
        return delta.days
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados do evento
        """
        return {
            'id': str(self.id),
            'ativo_id': str(self.ativo_id),
            'ativo_novo_id': str(self.ativo_novo_id) if self.ativo_novo_id else None,
            'tipo_evento': self.tipo_evento.value if self.tipo_evento else None,
            'data_evento': self.data_evento.isoformat() if self.data_evento else None,
            'data_com': self.data_com.isoformat() if self.data_com else None,
            'proporcao': self.proporcao,
            'fator_ajuste_quantidade': self.calcular_fator_ajuste(),
            'fator_ajuste_preco': self.calcular_fator_ajuste_preco(),
            'descricao': self.descricao,
            'impacto_posicoes': self.impacto_posicoes,
            'dias_ate_evento': self.dias_ate_evento(),
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        ticker = self.ativo.ticker if self.ativo else "N/A"
        tipo = self.tipo_evento.value if self.tipo_evento else "N/A"
        return f"<EventoCorporativo {tipo.upper()} {ticker} {self.proporcao or ''}>"
