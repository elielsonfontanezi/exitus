from marshmallow import Schema, fields

class PosicaoResponseSchema(Schema):
    id = fields.Str()
    quantidade = fields.Float()
    preco_medio = fields.Float()
    custototal = fields.Float()
    ativo_id = fields.Str()
    corretora_id = fields.Str()

class PosicaoResumoSchema(Schema):
    quantidade_posicoes = fields.Int()
    total_investido = fields.Float()
    total_valor_atual = fields.Float()
    lucro_total = fields.Float()
