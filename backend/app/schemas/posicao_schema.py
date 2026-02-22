# -- coding: utf-8 --
# backend/app/schemas/posicao_schema.py
# Exitus - Posicao Schemas - Validacao Marshmallow
# Correcoes: GAP EXITUS-POS-001 — campos completos + nested ativo e corretora

from marshmallow import Schema, fields


class AtivoNestedSchema(Schema):
    """Nested schema para ativo dentro de posicao."""
    id = fields.Str()
    ticker = fields.Str()
    nome = fields.Str()
    tipo = fields.Str()
    classe = fields.Str()
    mercado = fields.Str()
    moeda = fields.Str()
    preco_atual = fields.Float(allow_none=True)
    dividend_yield = fields.Float(allow_none=True)
    pl = fields.Float(allow_none=True)
    pvp = fields.Float(allow_none=True)


class CorretoraNestedSchema(Schema):
    """Nested schema para corretora dentro de posicao."""
    id = fields.Str()
    nome = fields.Str()
    tipo = fields.Str()
    pais = fields.Str()
    moeda_padrao = fields.Str()


class PosicaoResponseSchema(Schema):
    """Schema completo de resposta de posicao.
    Correcoes aplicadas:
      - GAP EXITUS-POS-001: adicionados todos os campos do model Posicao
      - GAP EXITUS-POS-001: nested ativo e corretora incluidos
    """
    id = fields.Str()
    usuario_id = fields.Str()
    ativo_id = fields.Str()
    corretora_id = fields.Str()
    quantidade = fields.Float()
    preco_medio = fields.Float()
    custo_total = fields.Float()
    taxas_acumuladas = fields.Float()
    impostos_acumulados = fields.Float()
    valor_atual = fields.Float(allow_none=True)
    lucro_prejuizo_realizado = fields.Float()
    lucro_prejuizo_nao_realizado = fields.Float(allow_none=True)
    data_primeira_compra = fields.Date(allow_none=True)
    data_ultima_atualizacao = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
    # Nested objects
    ativo = fields.Nested(AtivoNestedSchema, allow_none=True)
    corretora = fields.Nested(CorretoraNestedSchema, allow_none=True)


class PosicaoResumoSchema(Schema):
    """Schema para resumo consolidado das posicoes do usuario."""
    quantidade_posicoes = fields.Int()
    total_investido = fields.Float()
    total_valor_atual = fields.Float()
    total_lucro_realizado = fields.Float()
    total_lucro_nao_realizado = fields.Float()
    lucro_total = fields.Float()
    roi_percentual = fields.Float()
