# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate, post_dump


class RegraFiscalResponseSchema(Schema):
    id = fields.Str()
    pais = fields.Str()
    tipo_ativo = fields.Str(allow_none=True)
    tipo_operacao = fields.Str(allow_none=True)
    aliquota_ir = fields.Float()
    valor_isencao = fields.Float(allow_none=True)
    incide_sobre = fields.Str()
    descricao = fields.Str()
    vigencia_inicio = fields.Date()
    vigencia_fim = fields.Date(allow_none=True)
    ativa = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @post_dump
    def extract_enum_value(self, data, **kwargs):
        if data.get('incide_sobre') and '.' in str(data['incide_sobre']):
            data['incide_sobre'] = str(data['incide_sobre']).split('.')[-1].lower()
        return data


class RegraFiscalCreateSchema(Schema):
    pais = fields.Str(required=True, validate=validate.Length(equal=2))
    aliquota_ir = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    incide_sobre = fields.Str(required=True, validate=validate.OneOf([
        'lucro', 'receita', 'provento', 'operacao'
    ]))
    descricao = fields.Str(required=True, validate=validate.Length(min=3))
    vigencia_inicio = fields.Date(required=True)
    tipo_ativo = fields.Str(load_default=None)
    tipo_operacao = fields.Str(load_default=None)
    valor_isencao = fields.Float(load_default=None)
    vigencia_fim = fields.Date(load_default=None)
    ativa = fields.Bool(load_default=True)


class RegraFiscalUpdateSchema(Schema):
    pais = fields.Str(validate=validate.Length(equal=2))
    aliquota_ir = fields.Float(validate=validate.Range(min=0, max=100))
    incide_sobre = fields.Str(validate=validate.OneOf([
        'lucro', 'receita', 'provento', 'operacao'
    ]))
    descricao = fields.Str(validate=validate.Length(min=3))
    vigencia_inicio = fields.Date()
    tipo_ativo = fields.Str(allow_none=True)
    tipo_operacao = fields.Str(allow_none=True)
    valor_isencao = fields.Float(allow_none=True)
    vigencia_fim = fields.Date(allow_none=True)
    ativa = fields.Bool()
