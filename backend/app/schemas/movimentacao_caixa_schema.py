# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate

class MovimentacaoCaixaCreateSchema(Schema):
    corretora_id = fields.Str(required=True)
    tipo_movimentacao = fields.Str(required=True) # Aceita string livre por enquanto
    valor = fields.Float(required=True)
    data_movimentacao = fields.Date(required=True)
    descricao = fields.Str(load_default="")
    provento_id = fields.Str(load_default=None)

class MovimentacaoCaixaResponseSchema(Schema):
    id = fields.Str()
    corretora_id = fields.Str()
    tipo_movimentacao = fields.Str()
    valor = fields.Float()
    data_movimentacao = fields.Date()
    descricao = fields.Str()
    provento_id = fields.Str()
