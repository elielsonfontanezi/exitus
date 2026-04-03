# -*- coding: utf-8 -*-
"""
Exitus - Plano de Venda Model
Plano disciplinado para realização de lucros
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Text, Numeric, DateTime, Date, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import db
# from app.models.base_model import BaseModel


class StatusPlanoVenda(PyEnum):
    """Status do plano de venda"""
    ATIVO = "ativo"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class TipoGatilho(PyEnum):
    """Tipo de gatilho para venda"""
    PRECO_ALVO = "preco_alvo"
    PERCENTUAL_LUCRO = "percentual_lucro"
    PARCELAS_SEMANAIS = "parcelas_semanais"
    PARCELAS_MENSAIS = "parcelas_mensais"
    DATA_LIMITE = "data_limite"
    GATILHO_MISTO = "gatilho_misto"


class PlanoVenda(db.Model):
    """Modelo para planos de venda programada"""
    
    __tablename__ = "plano_venda"
    
    # Dados básicos
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Relacionamentos
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativo.id"), nullable=False)
    assessora_id = Column(UUID(as_uuid=True), ForeignKey("assessora.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Configurações da venda
    quantidade_total = Column(Numeric(18, 8), nullable=False)  # Quantidade total para vender
    quantidade_vendida = Column(Numeric(18, 8), nullable=False, default=0)  # Já vendido
    preco_minimo = Column(Numeric(18, 6), nullable=True)  # Preço mínimo de venda
    preco_alvo = Column(Numeric(18, 6), nullable=True)  # Preço alvo
    
    # Gatilhos de venda
    tipo_gatilho = Column(Enum(TipoGatilho, values_callable=lambda x: [e.value for e in x]), nullable=False)
    gatilho_valor = Column(Numeric(18, 6), nullable=True)  # Valor do gatilho (preço ou %)
    data_limite = Column(Date, nullable=True)  # Para gatilho por data
    
    # Parcelamento (se aplicável)
    parcelas_total = Column(Integer, nullable=True)  # Número de parcelas
    parcelas_executadas = Column(Integer, nullable=False, default=0)
    valor_parcela_fixo = Column(Numeric(18, 2), nullable=True)  # Valor fixo por parcela
    
    # Controle
    status = Column(Enum(StatusPlanoVenda, values_callable=lambda x: [e.value for e in x]), nullable=False, default=StatusPlanoVenda.ATIVO)
    data_inicio = Column(Date, nullable=True)
    data_conclusao = Column(Date, nullable=True)
    
    # Campos de controle
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    assessora = relationship("Assessora", back_populates="planos_venda")
    usuario = relationship("Usuario", back_populates="planos_venda")
    ativo = relationship("Ativo")
    
    def __repr__(self):
        return f"<PlanoVenda {self.nome} - {self.ativo.ticker if self.ativo else 'N/A'}>"
    
    @property
    def quantidade_restante(self) -> Decimal:
        """Quantidade restante para vender"""
        return max(Decimal('0'), self.quantidade_total - self.quantidade_vendida)
    
    @property
    def progresso_percentual(self) -> float:
        """Progresso do plano em percentual"""
        if self.quantidade_total == 0:
            return 0.0
        return float((self.quantidade_vendida / self.quantidade_total) * 100)
    
    @property
    def parcelas_restantes(self) -> Optional[int]:
        """Parcelas restantes (se aplicável)"""
        if self.parcelas_total is None:
            return None
        return max(0, self.parcelas_total - self.parcelas_executadas)
    
    def esta_ativo(self) -> bool:
        """Verifica se plano está ativo"""
        return self.status == StatusPlanoVenda.ATIVO
    
    def esta_concluido(self) -> bool:
        """Verifica se plano está concluído"""
        return self.status == StatusPlanoVenda.CONCLUIDO or self.quantidade_restante <= 0
    
    def pode_executar_venda(self) -> bool:
        """Verifica se pode executar venda"""
        if not self.esta_ativo():
            return False
        if self.quantidade_restante <= 0:
            return False
        if self.data_limite and date.today() > self.data_limite:
            return False
        return True
    
    def deve_disparar_por_preco(self, preco_atual: Decimal) -> bool:
        """Verifica se deve disparar venda por preço"""
        if self.tipo_gatilho != TipoGatilho.PRECO_ALVO:
            return False
        
        if self.preco_alvo and preco_atual >= self.preco_alvo:
            return True
        
        return False
    
    def deve_disparar_por_percentual(self, preco_atual: Decimal, preco_medio: Decimal) -> bool:
        """Verifica se deve disparar venda por percentual de lucro"""
        if self.tipo_gatilho != TipoGatilho.PERCENTUAL_LUCRO:
            return False
        
        if not self.gatilho_valor or preco_medio <= 0:
            return False
        
        lucro_percentual = ((preco_atual - preco_medio) / preco_medio) * 100
        return lucro_percentual >= float(self.gatilho_valor)
    
    def deve_disparar_por_data(self) -> bool:
        """Verifica se deve disparar venda por data"""
        if self.tipo_gatilho != TipoGatilho.DATA_LIMITE:
            return False
        
        return self.data_limite and date.today() >= self.data_limite
    
    def calcular_quantidade_parcela(self) -> Optional[Decimal]:
        """Calcula quantidade da próxima parcela"""
        if self.tipo_gatilho not in [TipoGatilho.PARCELAS_SEMANAIS, TipoGatilho.PARCELAS_MENSAIS]:
            return None
        
        if self.parcelas_restantes is None or self.parcelas_restantes <= 0:
            return None
        
        return self.quantidade_restante / Decimal(self.parcelas_restantes)
    
    def registrar_venda(self, quantidade: Decimal, preco: Decimal) -> bool:
        """Registra uma venda executada"""
        if quantidade <= 0 or quantidade > self.quantidade_restante:
            return False
        
        if self.preco_minimo and preco < self.preco_minimo:
            return False
        
        self.quantidade_vendida += quantidade
        self.parcelas_executadas += 1
        self.updated_at = datetime.utcnow()
        
        # Verifica se concluiu
        if self.quantidade_restante <= 0:
            self.status = StatusPlanoVenda.CONCLUIDO
            self.data_conclusao = date.today()
        
        return True
    
    def pausar(self):
        """Pausa o plano"""
        if self.status == StatusPlanoVenda.ATIVO:
            self.status = StatusPlanoVenda.PAUSADO
            self.updated_at = datetime.utcnow()
    
    def reativar(self):
        """Reativa o plano"""
        if self.status == StatusPlanoVenda.PAUSADO:
            self.status = StatusPlanoVenda.ATIVO
            self.updated_at = datetime.utcnow()
    
    def cancelar(self):
        """Cancela o plano"""
        self.status = StatusPlanoVenda.CANCELADO
        self.updated_at = datetime.utcnow()


# Adicionar relacionamento ao Usuario (se ainda não existir)
# Isso deve ser importado no models/usuario.py
# from app.models.plano_venda import PlanoVenda
# planos_venda = relationship("PlanoVenda", back_populates="usuario", cascade="all, delete-orphan")
