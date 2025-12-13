# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

class EventoCorporativoResponseSchema(Schema):
    id = fields.Str()
    ativo_id = fields.Str()
    tipo_evento = fields.Str() 
    proporcao = fields.Str()
    data_com = fields.Date()
    # CORRIGIDO: data_aprovacao -> data_evento
    data_evento = fields.Date() 
    descricao = fields.Str()
