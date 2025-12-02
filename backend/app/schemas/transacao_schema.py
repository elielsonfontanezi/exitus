# -*- coding: utf-8 -*-
"""Exitus - Transacao Schemas - Validação Marshmallow"""

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Transacao, TipoTransacao
from datetime import datetime
from decimal import Decimal

class TransacaoCreateSchema(Schema):
    """Schema para criação de transação"""
    tipo = fields.Str(required=True)
    ativo_id = fields.UUID(required=True)
    corretora_id = fields.UUID(required=True)
    data_transacao = fields.DateTime(required=True)
    quantidade = fields.Decimal(required=True, as_string=True)
    preco_unitario = fields.Decimal(required=True, as_string=True)
    taxa_corretagem = fields.Decimal(required=False, as_string=True, load_default="0")
    taxa_liquidacao = fields.Decimal(required=False, as_string=True, load_default="0")
    emolumentos = fields.Decimal(required=False, as_string=True, load_default="0")
    imposto = fields.Decimal(required=False, as_string=True, load_default="0")
    outros_custos = fields.Decimal(required=False, as_string=True, load_default="0")
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        """Valida se tipo é válido"""
        valid_tipos = ['compra', 'venda', 'dividendo', 'jcp', 'bonificacao', 'desdobramento', 'grupamento']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('quantidade')
    def validate_quantidade(self, value):
        """Valida quantidade positiva"""
        if Decimal(str(value)) <= 0:
            raise ValidationError("Quantidade deve ser maior que zero")
    
    @validates('preco_unitario')
    def validate_preco(self, value):
        """Valida preço não negativo"""
        if Decimal(str(value)) < 0:
            raise ValidationError("Preço unitário não pode ser negativo")
    
    @validates_schema
    def validate_compra_venda(self, data, **kwargs):
        """Validações específicas por tipo"""
        tipo = data.get('tipo', '').lower()
        preco = Decimal(str(data.get('preco_unitario', 0)))
        
        # Compra/venda devem ter preço > 0
        if tipo in ['compra', 'venda'] and preco == 0:
            raise ValidationError(
                {"preco_unitario": "Compra/venda deve ter preço unitário maior que zero"}
            )

class TransacaoUpdateSchema(Schema):
    """Schema para atualização de transação"""
    data_transacao = fields.DateTime(required=False)
    quantidade = fields.Decimal(required=False, as_string=True)
    preco_unitario = fields.Decimal(required=False, as_string=True)
    taxa_corretagem = fields.Decimal(required=False, as_string=True)
    taxa_liquidacao = fields.Decimal(required=False, as_string=True)
    emolumentos = fields.Decimal(required=False, as_string=True)
    imposto = fields.Decimal(required=False, as_string=True)
    outros_custos = fields.Decimal(required=False, as_string=True)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('quantidade')
    def validate_quantidade(self, value):
        if Decimal(str(value)) <= 0:
            raise ValidationError("Quantidade deve ser maior que zero")
    
    @validates('preco_unitario')
    def validate_preco(self, value):
        if Decimal(str(value)) < 0:
            raise ValidationError("Preço unitário não pode ser negativo")

class TransacaoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de transação"""
    class Meta:
        model = Transacao
        load_instance = False
        include_fk = True
    
    tipo = fields.Method("get_tipo_str")
    quantidade = fields.Decimal(as_string=True)
    preco_unitario = fields.Decimal(as_string=True)
    valor_total = fields.Decimal(as_string=True)
    taxa_corretagem = fields.Decimal(as_string=True)
    taxa_liquidacao = fields.Decimal(as_string=True)
    emolumentos = fields.Decimal(as_string=True)
    imposto = fields.Decimal(as_string=True)
    outros_custos = fields.Decimal(as_string=True)
    custos_totais = fields.Decimal(as_string=True)
    valor_liquido = fields.Decimal(as_string=True)
    
    # Campos relacionados (nested)
    ativo = fields.Method("get_ativo_info")
    corretora = fields.Method("get_corretora_info")
    
    def get_tipo_str(self, obj):
        """Converte Enum para string"""
        return obj.tipo.value if obj.tipo else None
    
    def get_ativo_info(self, obj):
        """Retorna info básica do ativo"""
        if obj.ativo:
            return {
                "id": str(obj.ativo.id),
                "ticker": obj.ativo.ticker,
                "nome": obj.ativo.nome,
                "tipo": obj.ativo.tipo.value,
                "mercado": obj.ativo.mercado
            }
        return None
    
    def get_corretora_info(self, obj):
        """Retorna info básica da corretora"""
        if obj.corretora:
            return {
                "id": str(obj.corretora.id),
                "nome": obj.corretora.nome,
                "tipo": obj.corretora.tipo.value
            }
        return None
