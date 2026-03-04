# -*- coding: utf-8 -*-
"""
Exitus - Schema para ParametrosMacro
Marshmallow schemas para validação e serialização
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.parametros_macro import ParametrosMacro


class ParametrosMacroResponseSchema(Schema):
    """Schema para resposta de ParametrosMacro"""
    id = fields.UUID(dump_only=True)
    pais = fields.Str(required=True, validate=validate.Length(min=2, max=2))
    mercado = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    taxa_livre_risco = fields.Decimal(required=True, places=6)
    crescimento_medio = fields.Decimal(required=True, places=6)
    custo_capital = fields.Decimal(required=True, places=6)
    inflacao_anual = fields.Decimal(required=True, places=6)
    cap_rate_fii = fields.Decimal(allow_none=True, places=6)
    ytm_rf = fields.Decimal(allow_none=True, places=6)
    ativo = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ParametrosMacroCreateSchema(Schema):
    """Schema para criação de ParametrosMacro"""
    pais = fields.Str(required=True, validate=validate.Length(min=2, max=2))
    mercado = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    taxa_livre_risco = fields.Decimal(required=True, places=6, validate=validate.Range(min=0, max=1))
    crescimento_medio = fields.Decimal(required=True, places=6, validate=validate.Range(min=-0.5, max=0.5))
    custo_capital = fields.Decimal(required=True, places=6, validate=validate.Range(min=0, max=1))
    inflacao_anual = fields.Decimal(required=True, places=6, validate=validate.Range(min=-0.5, max=1))
    cap_rate_fii = fields.Decimal(allow_none=True, places=6, validate=validate.Range(min=0, max=1))
    ytm_rf = fields.Decimal(allow_none=True, places=6, validate=validate.Range(min=0, max=1))
    ativo = fields.Boolean(missing=True)
    
    @validates('pais')
    def validate_pais(self, value):
        """Valida código do país (ex: BR, US, EU, JP)"""
        paises_validos = ['BR', 'US', 'EU', 'JP', 'CN', 'GB', 'CA', 'AU']
        if value.upper() not in paises_validos:
            raise ValidationError(f'País deve ser um dos seguintes: {", ".join(paises_validos)}')
    
    @validates('mercado')
    def validate_mercado(self, value):
        """Valida nome do mercado (ex: B3, NYSE, Euronext)"""
        mercados_validos = ['B3', 'NYSE', 'NASDAQ', 'Euronext', 'Tokyo', 'Shanghai', 'LSE', 'TSX']
        if value not in mercados_validos:
            raise ValidationError(f'Mercado deve ser um dos seguintes: {", ".join(mercados_validos)}')


class ParametrosMacroUpdateSchema(Schema):
    """Schema para atualização de ParametrosMacro"""
    taxa_livre_risco = fields.Decimal(places=6, validate=validate.Range(min=0, max=1))
    crescimento_medio = fields.Decimal(places=6, validate=validate.Range(min=-0.5, max=0.5))
    custo_capital = fields.Decimal(places=6, validate=validate.Range(min=0, max=1))
    inflacao_anual = fields.Decimal(places=6, validate=validate.Range(min=-0.5, max=1))
    cap_rate_fii = fields.Decimal(allow_none=True, places=6, validate=validate.Range(min=0, max=1))
    ytm_rf = fields.Decimal(allow_none=True, places=6, validate=validate.Range(min=0, max=1))
    ativo = fields.Boolean()
