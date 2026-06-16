# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate, post_dump


class FeriadoMercadoResponseSchema(Schema):
    id = fields.Str()
    pais = fields.Str()
    mercado = fields.Str(allow_none=True)
    data_feriado = fields.Date()
    tipo_feriado = fields.Str()
    nome = fields.Str()
    horario_fechamento = fields.Time(allow_none=True)
    recorrente = fields.Bool()
    observacoes = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @post_dump
    def extract_enum_value(self, data, **kwargs):
        if data.get('tipo_feriado') and '.' in str(data['tipo_feriado']):
            data['tipo_feriado'] = str(data['tipo_feriado']).split('.')[-1].lower()
        return data


class FeriadoMercadoCreateSchema(Schema):
    pais = fields.Str(required=True, validate=validate.Length(equal=2))
    data_feriado = fields.Date(required=True)
    tipo_feriado = fields.Str(required=True, validate=validate.OneOf([
        'nacional', 'bolsa', 'ponte', 'antecip', 'manutencao', 'outro'
    ]))
    nome = fields.Str(required=True, validate=validate.Length(min=3))
    mercado = fields.Str(load_default=None)
    horario_fechamento = fields.Time(load_default=None)
    recorrente = fields.Bool(load_default=False)
    observacoes = fields.Str(load_default=None)


class FeriadoMercadoUpdateSchema(Schema):
    pais = fields.Str(validate=validate.Length(equal=2))
    data_feriado = fields.Date()
    tipo_feriado = fields.Str(validate=validate.OneOf([
        'nacional', 'bolsa', 'ponte', 'antecip', 'manutencao', 'outro'
    ]))
    nome = fields.Str(validate=validate.Length(min=3))
    mercado = fields.Str(allow_none=True)
    horario_fechamento = fields.Time(allow_none=True)
    recorrente = fields.Bool()
    observacoes = fields.Str(allow_none=True)
