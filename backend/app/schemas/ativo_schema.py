# -*- coding: utf-8 -*-
"""Exitus - Ativo Schemas - Validação Marshmallow"""

from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Ativo, TipoAtivo, ClasseAtivo
from app.database import db
from decimal import Decimal

class AtivoCreateSchema(Schema):
    """Schema para criação de ativo"""
    ticker = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 20)
    nome = fields.Str(required=True, validate=lambda x: 2 <= len(x) <= 200)
    tipo = fields.Str(required=True)
    classe = fields.Str(required=True)
    mercado = fields.Str(required=True, validate=lambda x: len(x) <= 10)
    moeda = fields.Str(required=True, validate=lambda x: len(x) == 3)
    preco_atual = fields.Decimal(required=False, as_string=True, allow_none=True)
    dividend_yield = fields.Decimal(required=False, as_string=True, allow_none=True)
    pl = fields.Decimal(required=False, as_string=True, allow_none=True)
    pvp = fields.Decimal(required=False, as_string=True, allow_none=True)
    roe = fields.Decimal(required=False, as_string=True, allow_none=True)
    ativo = fields.Bool(required=False, default=True)
    deslistado = fields.Bool(required=False, default=False)
    
    @validates('tipo')
    def validate_tipo(self, value):
        """Valida se tipo é válido"""
        valid_tipos = ['acao', 'fii', 'reit', 'bond', 'etf', 'cripto', 'outro']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('classe')
    def validate_classe(self, value):
        """Valida se classe é válida"""
        valid_classes = ['renda_variavel', 'renda_fixa', 'cripto', 'hibrido']
        if value.lower() not in valid_classes:
            raise ValidationError(f"Classe inválida. Opções: {', '.join(valid_classes)}")
    
    @validates('moeda')
    def validate_moeda(self, value):
        """Valida código ISO da moeda (3 letras maiúsculas)"""
        if not value.isupper() or len(value) != 3:
            raise ValidationError("Moeda deve ser código ISO 4217 (ex: BRL, USD, EUR)")
    
    @validates('ticker')
    def validate_ticker_format(self, value):
        """Valida formato do ticker"""
        if not value.replace('.', '').replace('-', '').isalnum():
            raise ValidationError("Ticker deve conter apenas letras, números, pontos e hífens")

class AtivoUpdateSchema(Schema):
    """Schema para atualização de ativo"""
    nome = fields.Str(required=False, validate=lambda x: 2 <= len(x) <= 200)
    tipo = fields.Str(required=False)
    classe = fields.Str(required=False)
    mercado = fields.Str(required=False, validate=lambda x: len(x) <= 10)
    moeda = fields.Str(required=False, validate=lambda x: len(x) == 3)
    preco_atual = fields.Decimal(required=False, as_string=True, allow_none=True)
    dividend_yield = fields.Decimal(required=False, as_string=True, allow_none=True)
    pl = fields.Decimal(required=False, as_string=True, allow_none=True)
    pvp = fields.Decimal(required=False, as_string=True, allow_none=True)
    roe = fields.Decimal(required=False, as_string=True, allow_none=True)
    ativo = fields.Bool(required=False)
    deslistado = fields.Bool(required=False)
    data_deslistagem = fields.Date(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        valid_tipos = ['acao', 'fii', 'reit', 'bond', 'etf', 'cripto', 'outro']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('classe')
    def validate_classe(self, value):
        valid_classes = ['renda_variavel', 'renda_fixa', 'cripto', 'hibrido']
        if value.lower() not in valid_classes:
            raise ValidationError(f"Classe inválida. Opções: {', '.join(valid_classes)}")

class AtivoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de ativo"""
    class Meta:
        model = Ativo
        load_instance = False
    
    tipo = fields.Method("get_tipo_str")
    classe = fields.Method("get_classe_str")
    preco_atual = fields.Decimal(as_string=True)
    dividend_yield = fields.Decimal(as_string=True)
    pl = fields.Decimal(as_string=True)
    pvp = fields.Decimal(as_string=True)
    roe = fields.Decimal(as_string=True)
    
    def get_tipo_str(self, obj):
        """Converte Enum para string"""
        return obj.tipo.value if obj.tipo else None
    
    def get_classe_str(self, obj):
        """Converte Enum para string"""
        return obj.classe.value if obj.classe else None
