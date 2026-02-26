# -- coding: utf-8 --
# Exitus - Transacao Schemas - Validação Marshmallow
# v0.7.13 — GAP-001: custo_total via fields.Method em Response e List schemas

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Transacao, TipoTransacao
from datetime import datetime
from decimal import Decimal


class TransacaoCreateSchema(Schema):
    """Schema para criação de transação."""
    tipo           = fields.Str(required=True)
    ativo_id       = fields.UUID(required=True)
    corretora_id   = fields.UUID(required=True)
    data_transacao = fields.DateTime(required=True)
    quantidade     = fields.Decimal(required=True,  as_string=True)
    preco_unitario = fields.Decimal(required=True,  as_string=True)
    taxa_corretagem = fields.Decimal(required=False, as_string=True, load_default=0)
    taxa_liquidacao = fields.Decimal(required=False, as_string=True, load_default=0)
    emolumentos    = fields.Decimal(required=False,  as_string=True, load_default=0)
    imposto        = fields.Decimal(required=False,  as_string=True, load_default=0)
    outros_custos  = fields.Decimal(required=False,  as_string=True, load_default=0)
    observacoes    = fields.Str(required=False, allow_none=True)

    @validates('tipo')
    def validate_tipo(self, value):
        valid_tipos = [
            'compra', 'venda', 'dividendo', 'jcp', 'aluguel',
            'bonificacao', 'split', 'grupamento', 'subscricao', 'amortizacao',
        ]
        if value.lower() not in valid_tipos:
            raise ValidationError(
                f'Tipo inválido: {value}. Opções: {", ".join(valid_tipos)}'
            )

    @validates('quantidade')
    def validate_quantidade(self, value):
        if Decimal(str(value)) <= 0:
            raise ValidationError('Quantidade deve ser maior que zero')

    @validates('preco_unitario')
    def validate_preco(self, value):
        if Decimal(str(value)) < 0:
            raise ValidationError('Preço unitário não pode ser negativo')

    @validates_schema
    def validate_compra_venda(self, data, **kwargs):
        # Fix batch TRX-001, TRX-005
        tipo  = data.get('tipo', '').lower()
        preco = Decimal(str(data.get('preco_unitario', 0)))
        if tipo in ('compra', 'venda') and preco <= 0:
            raise ValidationError(
                {'preco_unitario': 'Compra/venda deve ter preço unitário maior que zero'}
            )


class TransacaoUpdateSchema(Schema):
    """Schema para atualização de transação — todos os campos opcionais."""
    data_transacao  = fields.DateTime(required=False)
    quantidade      = fields.Decimal(required=False, as_string=True)
    preco_unitario  = fields.Decimal(required=False, as_string=True)
    taxa_corretagem = fields.Decimal(required=False, as_string=True)
    taxa_liquidacao = fields.Decimal(required=False, as_string=True)
    emolumentos     = fields.Decimal(required=False, as_string=True)
    imposto         = fields.Decimal(required=False, as_string=True)
    outros_custos   = fields.Decimal(required=False, as_string=True)
    observacoes     = fields.Str(required=False, allow_none=True)

    @validates('quantidade')
    def validate_quantidade(self, value):
        if Decimal(str(value)) <= 0:
            raise ValidationError('Quantidade deve ser maior que zero')

    @validates('preco_unitario')
    def validate_preco(self, value):
        if Decimal(str(value)) < 0:
            raise ValidationError('Preço unitário não pode ser negativo')


class TransacaoListSchema(Schema):
    """Schema resumido para listagem de transações (GET /)."""
    # Fix batch TRX-001, TRX-005, TRX-006
    id             = fields.UUID(dump_only=True)
    tipo           = fields.Method('get_tipo_str')
    ativo_id       = fields.UUID()
    corretora_id   = fields.UUID()
    data_transacao = fields.DateTime()
    quantidade     = fields.Decimal(as_string=True)
    preco_unitario = fields.Decimal(as_string=True)
    valor_total    = fields.Decimal(as_string=True)       # TRX-005
    custos_totais  = fields.Decimal(as_string=True)       # TRX-001
    # GAP-001: custo_total calculado dinamicamente
    custo_total    = fields.Method('get_custo_total')
    valor_liquido  = fields.Decimal(as_string=True)
    ativo          = fields.Method('get_ativo_info')      # TRX-005
    created_at     = fields.DateTime(dump_only=True)

    def get_tipo_str(self, obj):
        return obj.tipo.value if obj.tipo else None

    def get_ativo_info(self, obj):
        if obj.ativo:
            return {
                'id':      str(obj.ativo.id),
                'ticker':  obj.ativo.ticker,
                'nome':    obj.ativo.nome,
                'tipo':    obj.ativo.tipo.value,
                'mercado': obj.ativo.mercado,
            }
        return None

    def get_custo_total(self, obj):
        """GAP-001 — lê @property do model (soma dinâmica dos 5 sub-campos)."""
        return obj.custo_total  # já é float graças ao @property


class TransacaoResponseSchema(SQLAlchemyAutoSchema):
    """Schema completo de resposta — inclui todos os campos e nested objects."""
    class Meta:
        model        = Transacao
        load_instance = False
        include_fk   = True

    # Campos numéricos explícitos — garante as_string=True e evita null
    # Fix batch TRX-001, TRX-005
    tipo           = fields.Method('get_tipo_str')
    quantidade     = fields.Decimal(as_string=True)
    preco_unitario = fields.Decimal(as_string=True)
    valor_total    = fields.Decimal(as_string=True)       # TRX-005
    taxa_corretagem = fields.Decimal(as_string=True)
    taxa_liquidacao = fields.Decimal(as_string=True)
    emolumentos    = fields.Decimal(as_string=True)
    imposto        = fields.Decimal(as_string=True)
    outros_custos  = fields.Decimal(as_string=True)
    custos_totais  = fields.Decimal(as_string=True)       # TRX-001
    # GAP-001: custo_total calculado dinamicamente via @property
    custo_total    = fields.Method('get_custo_total')
    valor_liquido  = fields.Decimal(as_string=True)
    data_transacao = fields.DateTime(dump_only=True)      # TRX-005

    # Nested objects — TRX-005
    ativo          = fields.Method('get_ativo_info')
    corretora      = fields.Method('get_corretora_info')

    def get_tipo_str(self, obj):
        return obj.tipo.value if obj.tipo else None

    def get_ativo_info(self, obj):
        """Retorna info básica do ativo — funciona mesmo com lazy load."""
        if obj.ativo:
            return {
                'id':      str(obj.ativo.id),
                'ticker':  obj.ativo.ticker,
                'nome':    obj.ativo.nome,
                'tipo':    obj.ativo.tipo.value,
                'mercado': obj.ativo.mercado,
            }
        return None

    def get_corretora_info(self, obj):
        if obj.corretora:
            return {
                'id':   str(obj.corretora.id),
                'nome': obj.corretora.nome,
                'tipo': obj.corretora.tipo.value,
            }
        return None

    def get_custo_total(self, obj):
        """GAP-001 — lê @property do model (soma dinâmica dos 5 sub-campos)."""
        return obj.custo_total  # já é float graças ao @property
