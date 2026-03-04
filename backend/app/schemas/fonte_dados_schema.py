# -*- coding: utf-8 -*-
"""
Exitus - Schema para FonteDados
Marshmallow schemas para validação e serialização
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.fonte_dados import FonteDados, TipoFonteDados


class FonteDadosResponseSchema(Schema):
    """Schema para resposta de FonteDados"""
    id = fields.UUID(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    tipo_fonte = fields.Str(required=True, validate=validate.OneOf([e.value for e in TipoFonteDados]))
    url_base = fields.Str(allow_none=True, validate=validate.URL())
    requer_autenticacao = fields.Boolean(required=True)
    rate_limit = fields.Str(allow_none=True)
    ativa = fields.Boolean(required=True)
    prioridade = fields.Integer(required=True, validate=validate.Range(min=1))
    ultima_consulta = fields.DateTime(allow_none=True)
    total_consultas = fields.Integer(required=True, validate=validate.Range(min=0))
    total_erros = fields.Integer(required=True, validate=validate.Range(min=0))
    taxa_sucesso = fields.Decimal(dump_only=True, places=2)
    taxa_erro = fields.Decimal(dump_only=True, places=2)
    health_status = fields.Str(dump_only=True)
    observacoes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class FonteDadosCreateSchema(Schema):
    """Schema para criação de FonteDados"""
    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    tipo_fonte = fields.Str(required=True, validate=validate.OneOf([e.value for e in TipoFonteDados]))
    url_base = fields.Str(allow_none=True, validate=validate.URL())
    requer_autenticacao = fields.Boolean(missing=False)
    rate_limit = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d+/(minute|hour|day|month)$'))
    ativa = fields.Boolean(missing=True)
    prioridade = fields.Integer(missing=100, validate=validate.Range(min=1))
    observacoes = fields.Str(allow_none=True)


class FonteDadosUpdateSchema(Schema):
    """Schema para atualização de FonteDados"""
    nome = fields.Str(validate=validate.Length(min=2, max=100))
    tipo_fonte = fields.Str(validate=validate.OneOf([e.value for e in TipoFonteDados]))
    url_base = fields.Str(allow_none=True, validate=validate.URL())
    requer_autenticacao = fields.Boolean()
    rate_limit = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d+/(minute|hour|day|month)$'))
    ativa = fields.Boolean()
    prioridade = fields.Integer(validate=validate.Range(min=1))
    observacoes = fields.Str(allow_none=True)


class FonteDadosListSchema(Schema):
    """Schema para listagem de FonteDados (com estatísticas incluídas)"""
    id = fields.UUID(dump_only=True)
    nome = fields.Str(dump_only=True)
    tipo_fonte = fields.Str(dump_only=True)
    url_base = fields.Str(allow_none=True, dump_only=True)
    ativa = fields.Boolean(dump_only=True)
    prioridade = fields.Integer(dump_only=True)
    ultima_consulta = fields.DateTime(allow_none=True, dump_only=True)
    total_consultas = fields.Integer(dump_only=True)
    total_erros = fields.Integer(dump_only=True)
    taxa_sucesso = fields.Decimal(dump_only=True, places=2)
    taxa_erro = fields.Decimal(dump_only=True, places=2)
    health_status = fields.Str(dump_only=True)
