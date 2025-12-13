from marshmallow import Schema, fields

class ProventoResponseSchema(Schema):
    id = fields.Str()
    # Tratamento para Enum: converte para string automaticamente se for simples, 
    # se falhar, o marshmallow tenta str() no objeto.
    tipo_provento = fields.Str() 
    valor_por_acao = fields.Float()
    valor_bruto = fields.Float()
    valor_liquido = fields.Float()
    data_com = fields.Date()
    data_pagamento = fields.Date()
    ativo_id = fields.Str()
