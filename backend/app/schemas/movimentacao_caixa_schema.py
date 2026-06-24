# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate

class _EnumValueField(fields.Str):
    """Campo que serializa enum Python extraindo .value"""
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if hasattr(value, 'value'):
            return value.value
        return str(value)

class MovimentacaoCaixaCreateSchema(Schema):
    corretora_id = fields.Str(required=True)
    tipo_movimentacao = fields.Str(
        required=True,
        validate=validate.OneOf([
            'aporte', 'resgate', 'transferencia_enviada', 'transferencia_recebida',
            'credito_provento', 'taxa_custodia', 'taxa_corretagem', 'imposto',
            'ajuste', 'outro'
        ])
    )
    valor = fields.Float(required=True)
    data_movimentacao = fields.Date(required=True)
    descricao = fields.Str(load_default="")
    provento_id = fields.Str(load_default=None)

class MovimentacaoCaixaResponseSchema(Schema):
    id = fields.Str()
    corretora_id = fields.Str()
    tipo_movimentacao = _EnumValueField()
    valor = fields.Float()
    data_movimentacao = fields.Date()
    descricao = fields.Str()
    provento_id = fields.Str()
