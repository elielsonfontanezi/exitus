# -*- coding: utf-8 -*-
"""
Exitus - Model RegraFiscal
Entidade para regras tributárias por país e tipo de ativo
"""

from datetime import datetime, date
from app.database import db
from sqlalchemy import String, Boolean, DateTime, Enum, Numeric, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class IncidenciaImposto(enum.Enum):
    """Enum para tipo de incidência do imposto"""
    LUCRO = "lucro"              # Incide sobre lucro/ganho de capital
    RECEITA = "receita"          # Incide sobre receita bruta
    PROVENTO = "provento"        # Incide sobre proventos recebidos
    OPERACAO = "operacao"        # Incide sobre cada operação


class RegraFiscal(db.Model):
    """
    Model para regras tributárias
    
    Attributes:
        id (UUID): Identificador único
        pais (str): País da regra (código ISO)
        tipo_ativo (str): Tipo de ativo (ACAO, FII, REIT, etc.)
        tipo_operacao (str): Tipo de operação (COMPRA, VENDA, DAY_TRADE)
        aliquota_ir (Decimal): Alíquota de IR em %
        valor_isencao (Decimal): Valor de isenção mensal
        incide_sobre (IncidenciaImposto): Sobre o que incide o imposto
        descricao (str): Descrição da regra
        vigencia_inicio (date): Data de início da vigência
        vigencia_fim (date): Data de fim da vigência
        ativa (bool): Indica se regra está ativa
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    """
    
    __tablename__ = 'regra_fiscal'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da regra"
    )
    
    # Identificação da regra
    pais = db.Column(
        String(2),
        nullable=False,
        index=True,
        comment="Código ISO do país (BR, US, etc.)"
    )
    
    tipo_ativo = db.Column(
        String(20),
        nullable=True,
        index=True,
        comment="Tipo de ativo (ACAO, FII, REIT, BOND, etc.) - NULL = todos"
    )
    
    tipo_operacao = db.Column(
        String(20),
        nullable=True,
        index=True,
        comment="Tipo de operação (COMPRA, VENDA, DAY_TRADE, SWING_TRADE) - NULL = todas"
    )
    
    # Valores fiscais
    aliquota_ir = db.Column(
        Numeric(precision=6, scale=4),
        nullable=False,
        comment="Alíquota de IR em % (ex: 15.0000 = 15%)"
    )
    
    valor_isencao = db.Column(
        Numeric(precision=18, scale=2),
        nullable=True,
        comment="Valor de isenção mensal (ex: R$ 20.000,00 no Brasil)"
    )
    
    incide_sobre = db.Column(
        Enum(IncidenciaImposto),
        nullable=False,
        index=True,
        comment="Sobre o que incide o imposto"
    )
    
    # Descrição
    descricao = db.Column(
        Text,
        nullable=False,
        comment="Descrição detalhada da regra fiscal"
    )
    
    # Vigência
    vigencia_inicio = db.Column(
        Date,
        nullable=False,
        index=True,
        comment="Data de início da vigência da regra"
    )
    
    vigencia_fim = db.Column(
        Date,
        nullable=True,
        index=True,
        comment="Data de fim da vigência (NULL = vigente indefinidamente)"
    )
    
    # Status
    ativa = db.Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Indica se regra está ativa"
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
            "aliquota_ir >= 0 AND aliquota_ir <= 100",
            name="regra_aliquota_valida"
        ),
        db.CheckConstraint(
            "valor_isencao IS NULL OR valor_isencao >= 0",
            name="regra_isencao_positiva"
        ),
        db.CheckConstraint(
            "pais ~* '^[A-Z]{2}$'",
            name="regra_pais_iso_format"
        ),
        db.CheckConstraint(
            "vigencia_fim IS NULL OR vigencia_fim >= vigencia_inicio",
            name="regra_vigencia_valida"
        ),
        {'comment': 'Tabela de regras tributárias por país e tipo de ativo'}
    )
    
    def is_active(self):
        """Verifica se regra está ativa"""
        return self.ativa
    
    def is_vigente(self, data_referencia=None):
        """
        Verifica se regra está vigente em uma data
        
        Args:
            data_referencia (date): Data de referência (default: hoje)
            
        Returns:
            bool: True se vigente
        """
        if not self.ativa:
            return False
        
        if data_referencia is None:
            data_referencia = datetime.utcnow().date()
        
        # Verifica início
        if data_referencia < self.vigencia_inicio:
            return False
        
        # Verifica fim (se definido)
        if self.vigencia_fim and data_referencia > self.vigencia_fim:
            return False
        
        return True
    
    def tem_isencao(self):
        """Verifica se regra possui valor de isenção"""
        return self.valor_isencao is not None and self.valor_isencao > 0
    
    def calcular_imposto(self, base_calculo):
        """
        Calcula o imposto devido sobre uma base de cálculo
        
        Args:
            base_calculo (Decimal): Valor base para cálculo
            
        Returns:
            Decimal: Valor do imposto devido
        """
        # Se tem isenção e base está abaixo, não há imposto
        if self.tem_isencao() and base_calculo <= self.valor_isencao:
            return 0
        
        # Calcula imposto sobre o valor (ou valor acima da isenção)
        valor_tributavel = base_calculo
        if self.tem_isencao():
            valor_tributavel = base_calculo - self.valor_isencao
        
        imposto = valor_tributavel * (self.aliquota_ir / 100)
        return max(imposto, 0)  # Nunca retornar negativo
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da regra
        """
        return {
            'id': str(self.id),
            'pais': self.pais,
            'tipo_ativo': self.tipo_ativo,
            'tipo_operacao': self.tipo_operacao,
            'aliquota_ir': float(self.aliquota_ir) if self.aliquota_ir else 0,
            'valor_isencao': float(self.valor_isencao) if self.valor_isencao else None,
            'incide_sobre': self.incide_sobre.value if self.incide_sobre else None,
            'descricao': self.descricao,
            'vigencia_inicio': self.vigencia_inicio.isoformat() if self.vigencia_inicio else None,
            'vigencia_fim': self.vigencia_fim.isoformat() if self.vigencia_fim else None,
            'ativa': self.ativa,
            'vigente': self.is_vigente(),
            'tem_isencao': self.tem_isencao(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<RegraFiscal {self.pais} {self.tipo_ativo or 'ALL'} IR={self.aliquota_ir}%>"
