"""M7.4 - Schemas Marshmallow para Alertas"""
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load

# CREATE Schema
class AlertaCreateSchema(Schema):
    nome = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=100),
        error_messages={'required': 'Nome é obrigatório'}
    )
    tipo_alerta = fields.Str(
        required=True,
        validate=validate.OneOf([
            'ALTA_PRECO', 'QUEDA_PRECO', 'DIVIDENDO_PREVISTO',
            'META_RENTABILIDADE', 'VOLATILIDADE_ALTA', 'DESVIO_ALOCACAO'
        ])
    )
    ticker = fields.Str(
        allow_none=True,
        validate=validate.Length(max=20)
    )
    condicao_operador = fields.Str(
        required=True,
        validate=validate.OneOf(['>', '<', '>=', '<=', '==', 'ENTRE'])
    )
    condicao_valor = fields.Float(required=True, validate=validate.Range(min=0))
    condicao_valor2 = fields.Float(allow_none=True, validate=validate.Range(min=0))
    frequencia_notificacao = fields.Str(
        required=True,
        validate=validate.OneOf(['IMEDIATA', 'DIARIA', 'SEMANAL', 'MENSAL'])
    )
    canais_entrega = fields.List(
        fields.Str(validate=validate.OneOf(['WEBAPP', 'EMAIL', 'SMS'])),
        required=True,
        validate=validate.Length(min=1)
    )
    ativo = fields.Bool(missing=True)

    @validates('canais_entrega')
    def valida_canais(self, value):
        if not value or len(value) == 0:
            raise ValidationError('Ao menos 1 canal de entrega é obrigatório')

# UPDATE Schema
class AlertaUpdateSchema(Schema):
    nome = fields.Str(validate=validate.Length(min=5, max=100))
    tipo_alerta = fields.Str(
        validate=validate.OneOf([
            'ALTA_PRECO', 'QUEDA_PRECO', 'DIVIDENDO_PREVISTO',
            'META_RENTABILIDADE', 'VOLATILIDADE_ALTA', 'DESVIO_ALOCACAO'
        ])
    )
    ticker = fields.Str(validate=validate.Length(max=20), allow_none=True)
    condicao_operador = fields.Str(validate=validate.OneOf(['>', '<', '>=', '<=', '==', 'ENTRE']))
    condicao_valor = fields.Float(validate=validate.Range(min=0))
    condicao_valor2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    frequencia_notificacao = fields.Str(
        validate=validate.OneOf(['IMEDIATA', 'DIARIA', 'SEMANAL', 'MENSAL'])
    )
    canais_entrega = fields.List(
        fields.Str(validate=validate.OneOf(['WEBAPP', 'EMAIL', 'SMS'])),
        validate=validate.Length(min=1)
    )
    ativo = fields.Bool()

# RESPONSE Schema
class AlertaResponseSchema(Schema):
    id = fields.Str()
    usuario_id = fields.Str()
    nome = fields.Str()
    tipo_alerta = fields.Str()
    ticker = fields.Str(allow_none=True)
    condicao_operador = fields.Str()
    condicao_valor = fields.Float()
    condicao_valor2 = fields.Float(allow_none=True)
    ativo = fields.Bool()
    frequencia_notificacao = fields.Str()
    canais_entrega = fields.List(fields.Str())
    total_acionamentos = fields.Int()
    timestamp_ultimo_acionamento = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

# LIST Schema (Paginated)
class AlertaListSchema(Schema):
    alertas = fields.List(fields.Nested(AlertaResponseSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    total_pages = fields.Int()
