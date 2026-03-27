# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate, post_dump


class EventoCorporativoResponseSchema(Schema):
    id = fields.Str()
    ativo_id = fields.Str()
    ativo_novo_id = fields.Str(allow_none=True)
    tipo_evento = fields.Str()
    proporcao = fields.Str(allow_none=True)
    data_com = fields.Date(allow_none=True)
    data_evento = fields.Date()
    descricao = fields.Str()
    impacto_posicoes = fields.Bool()
    observacoes = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @post_dump
    def extract_enum_value(self, data, **kwargs):
        if data.get('tipo_evento') and '.' in str(data['tipo_evento']):
            data['tipo_evento'] = str(data['tipo_evento']).split('.')[-1].lower()
        return data


class EventoCorporativoCreateSchema(Schema):
    ativo_id = fields.Str(required=True)
    tipo_evento = fields.Str(required=True, validate=validate.OneOf([
        'split', 'grupamento', 'bonificacao', 'direito_sub',
        'fusao', 'cisao', 'incorporacao', 'mudanca_ticker',
        'deslistagem', 'relisting', 'cancelamento', 'desmembramento', 'outro'
    ]))
    data_evento = fields.Date(required=True)
    descricao = fields.Str(required=True, validate=validate.Length(min=3))
    data_com = fields.Date(load_default=None)
    proporcao = fields.Str(load_default=None)
    ativo_novo_id = fields.Str(load_default=None)
    observacoes = fields.Str(load_default=None)


class EventoCorporativoUpdateSchema(Schema):
    tipo_evento = fields.Str(validate=validate.OneOf([
        'split', 'grupamento', 'bonificacao', 'direito_sub',
        'fusao', 'cisao', 'incorporacao', 'mudanca_ticker',
        'deslistagem', 'relisting', 'cancelamento', 'desmembramento', 'outro'
    ]))
    data_evento = fields.Date()
    descricao = fields.Str(validate=validate.Length(min=3))
    data_com = fields.Date(allow_none=True)
    proporcao = fields.Str(allow_none=True)
    ativo_novo_id = fields.Str(allow_none=True)
    observacoes = fields.Str(allow_none=True)
