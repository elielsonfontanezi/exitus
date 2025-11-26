# -*- coding: utf-8 -*-
"""
Exitus - Model Posicao
Entidade para holdings/posições em carteira de ativos
"""

from datetime import datetime
from app.database import db
from sqlalchemy import String, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Posicao(db.Model):
    """
    Model para posições em carteira (holdings)
    
    Attributes:
        id (UUID): Identificador único
        usuario_id (UUID): ID do usuário proprietário
        corretora_id (UUID): ID da corretora onde está a posição
        ativo_id (UUID): ID do ativo
        quantidade (Decimal): Quantidade de ativos em posse
        preco_medio (Decimal): Preço médio de aquisição
        custo_total (Decimal): Custo total investido
        taxas_acumuladas (Decimal): Taxas de corretagem acumuladas
        impostos_acumulados (Decimal): Impostos pagos acumulados
        valor_atual (Decimal): Valor de mercado atual da posição
        lucro_prejuizo_realizado (Decimal): L/P realizado (vendas)
        lucro_prejuizo_nao_realizado (Decimal): L/P não realizado
        data_primeira_compra (date): Data da primeira aquisição
        data_ultima_atualizacao (datetime): Última atualização
        created_at (datetime): Data de criação
        updated_at (datetime): Data da última atualização
    
    Relationships:
        usuario: Usuário proprietário
        corretora: Corretora onde está a posição
        ativo: Ativo da posição
    """
    
    __tablename__ = 'posicao'
    
    # Chave primária
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da posição"
    )
    
    # Foreign keys
    usuario_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID do usuário proprietário"
    )
    
    corretora_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('corretora.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID da corretora onde está a posição"
    )
    
    ativo_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey('ativo.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="ID do ativo"
    )
    
    # Dados da posição
    quantidade = db.Column(
        Numeric(precision=18, scale=8),
        nullable=False,
        default=0,
        comment="Quantidade de ativos (suporta fracionários)"
    )
    
    preco_medio = db.Column(
        Numeric(precision=18, scale=6),
        nullable=False,
        default=0,
        comment="Preço médio de aquisição"
    )
    
    custo_total = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Custo total investido (quantidade * preço médio)"
    )
    
    taxas_acumuladas = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Taxas de corretagem e custódia acumuladas"
    )
    
    impostos_acumulados = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Impostos pagos acumulados (IR, IOF, etc.)"
    )
    
    # Valores calculados
    valor_atual = db.Column(
        Numeric(precision=18, scale=2),
        nullable=True,
        comment="Valor de mercado atual da posição"
    )
    
    lucro_prejuizo_realizado = db.Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        default=0,
        comment="Lucro/prejuízo realizado em vendas"
    )
    
    lucro_prejuizo_nao_realizado = db.Column(
        Numeric(precision=18, scale=2),
        nullable=True,
        comment="Lucro/prejuízo não realizado (marcação a mercado)"
    )
    
    # Datas
    data_primeira_compra = db.Column(
        Date,
        nullable=True,
        index=True,
        comment="Data da primeira aquisição deste ativo"
    )
    
    data_ultima_atualizacao = db.Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data da última atualização de valores"
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
    usuario = relationship('Usuario', backref='posicoes', lazy='joined')
    corretora = relationship('Corretora', backref='posicoes', lazy='joined')
    ativo = relationship('Ativo', backref='posicoes', lazy='joined')
    
    # Constraints de tabela
    __table_args__ = (
        db.CheckConstraint(
            "quantidade >= 0",
            name="posicao_quantidade_positiva"
        ),
        db.CheckConstraint(
            "preco_medio >= 0",
            name="posicao_preco_medio_positivo"
        ),
        db.CheckConstraint(
            "custo_total >= 0",
            name="posicao_custo_total_positivo"
        ),
        db.CheckConstraint(
            "taxas_acumuladas >= 0",
            name="posicao_taxas_positivas"
        ),
        db.CheckConstraint(
            "impostos_acumulados >= 0",
            name="posicao_impostos_positivos"
        ),
        db.UniqueConstraint(
            'usuario_id', 'corretora_id', 'ativo_id',
            name='unique_posicao_usuario_corretora_ativo'
        ),
        {'comment': 'Tabela de posições em carteira (holdings)'}
    )
    
    def calcular_valor_atual(self, preco_mercado):
        """
        Calcula o valor atual da posição baseado no preço de mercado
        
        Args:
            preco_mercado (Decimal): Preço atual do ativo no mercado
        
        Returns:
            Decimal: Valor atual da posição
        """
        self.valor_atual = self.quantidade * preco_mercado
        self.data_ultima_atualizacao = datetime.utcnow()
        return self.valor_atual
    
    def calcular_lucro_prejuizo_nao_realizado(self):
        """
        Calcula o lucro/prejuízo não realizado (marcação a mercado)
        
        Returns:
            Decimal: L/P não realizado
        """
        if self.valor_atual is not None:
            self.lucro_prejuizo_nao_realizado = self.valor_atual - self.custo_total
        return self.lucro_prejuizo_nao_realizado
    
    def adicionar_compra(self, quantidade, preco_unitario, taxas=0, impostos=0):
        """
        Adiciona uma compra à posição (recalcula preço médio)
        
        Args:
            quantidade (Decimal): Quantidade comprada
            preco_unitario (Decimal): Preço unitário da compra
            taxas (Decimal): Taxas da operação
            impostos (Decimal): Impostos da operação
        """
        # Garantir valores não-None (defaults do SQLAlchemy só aplicam ao persistir)
        if self.quantidade is None:
            self.quantidade = 0
        if self.preco_medio is None:
            self.preco_medio = 0
        if self.custo_total is None:
            self.custo_total = 0
        if self.taxas_acumuladas is None:
            self.taxas_acumuladas = 0
        if self.impostos_acumulados is None:
            self.impostos_acumulados = 0
        if self.lucro_prejuizo_realizado is None:
            self.lucro_prejuizo_realizado = 0
        
        custo_compra = quantidade * preco_unitario
        
        # Recalcular preço médio ponderado
        novo_custo_total = self.custo_total + custo_compra
        nova_quantidade = self.quantidade + quantidade
        
        if nova_quantidade > 0:
            self.preco_medio = novo_custo_total / nova_quantidade
        
        self.quantidade = nova_quantidade
        self.custo_total = novo_custo_total
        self.taxas_acumuladas += taxas
        self.impostos_acumulados += impostos
        
        # Definir data primeira compra se for a primeira
        if self.data_primeira_compra is None:
            self.data_primeira_compra = datetime.utcnow().date()

    
    def adicionar_venda(self, quantidade, preco_unitario, taxas=0, impostos=0):
        """
        Adiciona uma venda à posição
        
        Args:
            quantidade (Decimal): Quantidade vendida
            preco_unitario (Decimal): Preço unitário da venda
            taxas (Decimal): Taxas da operação
            impostos (Decimal): Impostos da operação
        
        Raises:
            ValueError: Se quantidade vendida for maior que quantidade em posse
        """
        # Garantir valores não-None
        if self.quantidade is None:
            self.quantidade = 0
        if self.preco_medio is None:
            self.preco_medio = 0
        if self.custo_total is None:
            self.custo_total = 0
        if self.taxas_acumuladas is None:
            self.taxas_acumuladas = 0
        if self.impostos_acumulados is None:
            self.impostos_acumulados = 0
        if self.lucro_prejuizo_realizado is None:
            self.lucro_prejuizo_realizado = 0
        
        if quantidade > self.quantidade:
            raise ValueError(
                f"Quantidade vendida ({quantidade}) maior que quantidade em posse ({self.quantidade})"
            )
        
        # Calcular lucro/prejuízo realizado
        receita_venda = quantidade * preco_unitario
        custo_proporcional = quantidade * self.preco_medio
        lp_realizado = receita_venda - custo_proporcional - taxas - impostos
        
        self.lucro_prejuizo_realizado += lp_realizado
        self.quantidade -= quantidade
        self.custo_total -= custo_proporcional
        self.taxas_acumuladas += taxas
        self.impostos_acumulados += impostos
        
        # Se zerou a posição, resetar preço médio
        if self.quantidade == 0:
            self.preco_medio = 0
            self.custo_total = 0

    
    def percentual_lucro_prejuizo(self):
        """
        Calcula o percentual de lucro/prejuízo não realizado
        
        Returns:
            Decimal: Percentual de L/P (ex: 15.5 = 15.5%)
        """
        if self.custo_total > 0 and self.lucro_prejuizo_nao_realizado is not None:
            return (self.lucro_prejuizo_nao_realizado / self.custo_total) * 100
        return 0
    
    def to_dict(self):
        """
        Converte objeto para dicionário (para serialização JSON)
        
        Returns:
            dict: Dicionário com dados da posição
        """
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'corretora_id': str(self.corretora_id),
            'ativo_id': str(self.ativo_id),
            'quantidade': float(self.quantidade) if self.quantidade else 0,
            'preco_medio': float(self.preco_medio) if self.preco_medio else 0,
            'custo_total': float(self.custo_total) if self.custo_total else 0,
            'taxas_acumuladas': float(self.taxas_acumuladas) if self.taxas_acumuladas else 0,
            'impostos_acumulados': float(self.impostos_acumulados) if self.impostos_acumulados else 0,
            'valor_atual': float(self.valor_atual) if self.valor_atual else None,
            'lucro_prejuizo_realizado': float(self.lucro_prejuizo_realizado) if self.lucro_prejuizo_realizado else 0,
            'lucro_prejuizo_nao_realizado': float(self.lucro_prejuizo_nao_realizado) if self.lucro_prejuizo_nao_realizado else None,
            'percentual_lp': float(self.percentual_lucro_prejuizo()),
            'data_primeira_compra': self.data_primeira_compra.isoformat() if self.data_primeira_compra else None,
            'data_ultima_atualizacao': self.data_ultima_atualizacao.isoformat() if self.data_ultima_atualizacao else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """Representação string do objeto"""
        return f"<Posicao {self.quantidade}x {self.ativo.ticker if self.ativo else 'N/A'}>"
