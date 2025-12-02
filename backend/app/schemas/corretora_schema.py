# -*- coding: utf-8 -*-
"""Exitus - Corretora Schemas - Validação Marshmallow"""

from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Corretora, TipoCorretora
from app.database import db

class CorretoraCreateSchema(Schema):
    """Schema para criação de corretora"""
    nome = fields.Str(required=True, validate=lambda x: 2 <= len(x) <= 100)
    tipo = fields.Str(required=True)
    pais = fields.Str(required=True, validate=lambda x: len(x) == 2)
    moeda_padrao = fields.Str(required=True, validate=lambda x: len(x) == 3)
    saldo_atual = fields.Decimal(required=False, as_string=True, default="0.00")
    ativa = fields.Bool(required=False, default=True)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        """Valida se tipo é válido"""
        valid_tipos = ['corretora', 'exchange']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('pais')
    def validate_pais(self, value):
        """Valida código ISO do país (2 letras maiúsculas)"""
        if not value.isupper() or len(value) != 2:
            raise ValidationError("País deve ser código ISO 3166-1 alpha-2 (ex: BR, US)")
    
    @validates('moeda_padrao')
    def validate_moeda(self, value):
        """Valida código ISO da moeda (3 letras maiúsculas)"""
        if not value.isupper() or len(value) != 3:
            raise ValidationError("Moeda deve ser código ISO 4217 (ex: BRL, USD, EUR)")

class CorretoraUpdateSchema(Schema):
    """Schema para atualização de corretora"""
    nome = fields.Str(required=False, validate=lambda x: 2 <= len(x) <= 100)
    tipo = fields.Str(required=False)
    pais = fields.Str(required=False, validate=lambda x: len(x) == 2)
    moeda_padrao = fields.Str(required=False, validate=lambda x: len(x) == 3)
    saldo_atual = fields.Decimal(required=False, as_string=True)
    ativa = fields.Bool(required=False)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        valid_tipos = ['corretora', 'exchange']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('pais')
    def validate_pais(self, value):
        if not value.isupper() or len(value) != 2:
            raise ValidationError("País deve ser código ISO 3166-1 alpha-2 (ex: BR, US)")
    
    @validates('moeda_padrao')
    def validate_moeda(self, value):
        if not value.isupper() or len(value) != 3:
            raise ValidationError("Moeda deve ser código ISO 4217 (ex: BRL, USD, EUR)")

class CorretoraResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de corretora"""
    class Meta:
        model = Corretora
        load_instance = False
        include_fk = True
    
    tipo = fields.Method("get_tipo_str")
    saldo_atual = fields.Decimal(as_string=True)
    
    def get_tipo_str(self, obj):
        """Converte Enum para string"""
        return obj.tipo.value if obj.tipo else None
