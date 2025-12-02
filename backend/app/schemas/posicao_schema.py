# -*- coding: utf-8 -*-
"""
Exitus - Posicao Schemas - Validação Marshmallow
"""

from marshmallow import Schema, fields, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Posicao


class PosicaoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de posição"""
    
    class Meta:
        model = Posicao
        load_instance = False
        include_fk = True
    
    # Campos calculados como string para JSON
    quantidade = fields.Decimal(as_string=True)
    preco_medio = fields.Decimal(as_string=True)
    custo_total = fields.Decimal(as_string=True)
    taxas_acumuladas = fields.Decimal(as_string=True)
    impostos_acumulados = fields.Decimal(as_string=True)
    valor_atual = fields.Decimal(as_string=True)
    lucro_prejuizo_realizado = fields.Decimal(as_string=True)
    lucro_prejuizo_nao_realizado = fields.Decimal(as_string=True)
    
    # Nested fields
    ativo = fields.Method("get_ativo_info")
    corretora = fields.Method("get_corretora_info")
    
    def get_ativo_info(self, obj):
        """Retorna info básica do ativo"""
        if obj.ativo:
            return {
                'id': str(obj.ativo.id),
                'ticker': obj.ativo.ticker,
                'nome': obj.ativo.nome,
                'tipo': obj.ativo.tipo.value,
                'classe': obj.ativo.classe.value,
                'mercado': obj.ativo.mercado,
                'preco_atual': float(obj.ativo.preco_atual) if obj.ativo.preco_atual else None
            }
        return None
    
    def get_corretora_info(self, obj):
        """Retorna info básica da corretora"""
        if obj.corretora:
            return {
                'id': str(obj.corretora.id),
                'nome': obj.corretora.nome,
                'tipo': obj.corretora.tipo.value
            }
        return None


class PosicaoResumoSchema(Schema):
    """Schema para resumo consolidado de posições"""
    
    quantidade_posicoes = fields.Int()
    total_investido = fields.Float()
    total_valor_atual = fields.Float()
    total_lucro_realizado = fields.Float()
    total_lucro_nao_realizado = fields.Float()
    lucro_total = fields.Float()
    roi_percentual = fields.Float()


class PosicaoConsolidadaSchema(Schema):
    """Schema para posição consolidada por ativo"""
    
    ativo = fields.Dict()
    quantidade_total = fields.Float()
    preco_medio = fields.Float()
    custo_total = fields.Float()
    valor_atual = fields.Float()
    lucro_prejuizo = fields.Float()
    corretoras = fields.List(fields.Dict())
