# -*- coding: utf-8 -*-
"""Schemas Marshmallow para MetaAlocacao — REBALANCE-001"""
from marshmallow import Schema, fields, validates, validates_schema, ValidationError

CLASSES_VALIDAS = ('renda_variavel', 'renda_fixa', 'cripto')


class MetaAlocacaoItemSchema(Schema):
    """Schema para um item de meta (uma classe)."""
    classe = fields.Str(required=True)
    percentual_target = fields.Float(required=True)
    tolerancia_pct = fields.Float(load_default=2.0)

    @validates('classe')
    def validate_classe(self, value):
        if value not in CLASSES_VALIDAS:
            raise ValidationError(f"classe deve ser uma de: {CLASSES_VALIDAS}")

    @validates('percentual_target')
    def validate_percentual(self, value):
        if not (0 <= value <= 100):
            raise ValidationError("percentual_target deve estar entre 0 e 100")

    @validates('tolerancia_pct')
    def validate_tolerancia(self, value):
        if not (0 <= value <= 50):
            raise ValidationError("tolerancia_pct deve estar entre 0 e 50")


class MetaAlocacaoBulkSchema(Schema):
    """Schema para salvar múltiplas metas de uma vez."""
    metas = fields.List(fields.Nested(MetaAlocacaoItemSchema), required=True)

    @validates_schema
    def validate_soma(self, data, **kwargs):
        metas = data.get('metas', [])
        soma = sum(m.get('percentual_target', 0) for m in metas)
        if soma > 100:
            raise ValidationError(
                f"Soma dos percentuais ({soma:.1f}%) não pode exceder 100%"
            )
