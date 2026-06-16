# -- coding: utf-8 --
# backend/app/schemas/posicao_schema.py
# Exitus - Posicao Schemas - Validacao Marshmallow
# v0.7.10 — GAP EXITUS-POS-001: campos completos + nested ativo e corretora
# v0.7.11 — GAP EXITUS-POS-008: enum serialization corrigida em AtivoNestedSchema

from marshmallow import Schema, fields


class AtivoNestedSchema(Schema):
    """Nested schema para ativo dentro de posicao.

    GAP EXITUS-POS-008: tipo e classe usam fields.Method() para serializar
    apenas o .value do Enum (ex.: "fii", "renda_variavel") em vez da
    representacao Python (ex.: "TipoAtivo.FII", "ClasseAtivo.RENDA_VARIAVEL").
    Padrao identico ao AtivoResponseSchema.
    """
    id = fields.Str()
    ticker = fields.Str()
    nome = fields.Str()
    tipo = fields.Method("get_tipo_str")
    classe = fields.Method("get_classe_str")
    mercado = fields.Str()
    moeda = fields.Str()
    preco_atual = fields.Float(allow_none=True)
    dividend_yield = fields.Float(allow_none=True)
    pl = fields.Float(allow_none=True)
    pvp = fields.Float(allow_none=True)

    def get_tipo_str(self, obj):
        """Serializa TipoAtivo para string lowercase (ex.: 'fii', 'acao')."""
        if obj.tipo is None:
            return None
        return obj.tipo.value if hasattr(obj.tipo, 'value') else str(obj.tipo)

    def get_classe_str(self, obj):
        """Serializa ClasseAtivo para string lowercase (ex.: 'renda_variavel')."""
        if obj.classe is None:
            return None
        return obj.classe.value if hasattr(obj.classe, 'value') else str(obj.classe)


class CorretoraNestedSchema(Schema):
    """Nested schema para corretora dentro de posicao."""
    id = fields.Str()
    nome = fields.Str()
    tipo = fields.Method("get_tipo_str")
    pais = fields.Str()
    moeda_padrao = fields.Str()

    def get_tipo_str(self, obj):
        """Serializa TipoCorretora para string lowercase (ex.: 'corretora')."""
        if obj.tipo is None:
            return None
        return obj.tipo.value if hasattr(obj.tipo, 'value') else str(obj.tipo)


class PosicaoResponseSchema(Schema):
    """Schema completo de resposta de posicao.

    Historico de correcoes:
      v0.7.10 — GAP EXITUS-POS-001: todos os campos do model + nested ativo/corretora
      v0.7.11 — GAP EXITUS-POS-008: enum serialization em nested corrigida
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
