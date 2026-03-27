# -*- coding: utf-8 -*-
"""
Exitus - CalendarioDividendo Schema
Schemas para validação de dados do calendário de dividendos
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date, datetime
from decimal import Decimal


class CalendarioDividendoCreateSchema(Schema):
    """Schema para criação de CalendarioDividendo"""
    
    ativo_id = fields.UUID(required=True, description="ID do ativo")
    usuario_id = fields.UUID(required=True, description="ID do usuário")
    data_esperada = fields.Date(required=True, description="Data esperada do provento")
    tipo_provento = fields.String(
        required=True,
        validate=validate.OneOf(['dividendo', 'jcp', 'rendimento', 'cupom', 'bonificacao', 'direito_sub', 'outro']),
        description="Tipo do provento"
    )
    yield_estimado = fields.Decimal(
        places=4,
        allow_none=True,
        validate=validate.Range(min=0, max=100),
        description="Yield percentual estimado"
    )
    valor_estimado = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0),
        description="Valor estimado em R$"
    )
    quantidade = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        description="Quantidade de ativos"
    )
    status = fields.String(
        required=False,
        validate=validate.OneOf(['previsto', 'confirmado', 'atrasado', 'pago']),
        missing='previsto',
        description="Status do calendário"
    )
    observacoes = fields.String(
        allow_none=True,
        validate=validate.Length(max=1000),
        description="Observações adicionais"
    )
    
    @validates('data_esperada')
    def validate_data_esperada(self, value):
        """Valida se data esperada é futura"""
        if value < date.today():
            raise ValidationError("Data esperada deve ser futura")


class CalendarioDividendoUpdateSchema(Schema):
    """Schema para atualização de CalendarioDividendo"""
    
    data_esperada = fields.Date(
        allow_none=True,
        description="Data esperada do provento"
    )
    tipo_provento = fields.String(
        allow_none=True,
        validate=validate.OneOf(['dividendo', 'jcp', 'rendimento', 'cupom', 'bonificacao', 'direito_sub', 'outro']),
        description="Tipo do provento"
    )
    yield_estimado = fields.Decimal(
        places=4,
        allow_none=True,
        validate=validate.Range(min=0, max=100),
        description="Yield percentual estimado"
    )
    valor_estimado = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0),
        description="Valor estimado em R$"
    )
    quantidade = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=0),
        description="Quantidade de ativos"
    )
    status = fields.String(
        allow_none=True,
        validate=validate.OneOf(['previsto', 'confirmado', 'atrasado', 'pago']),
        description="Status do calendário"
    )
    observacoes = fields.String(
        allow_none=True,
        validate=validate.Length(max=1000),
        description="Observações adicionais"
    )
    data_pagamento = fields.Date(
        allow_none=True,
        description="Data real do pagamento"
    )
    valor_real = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0),
        description="Valor real pago em R$"
    )
    
    @validates('data_esperada')
    def validate_data_esperada(self, value):
        """Valida se data esperada é futura (se informada)"""
        if value and value < date.today():
            raise ValidationError("Data esperada deve ser futura")
    
    @validates('data_pagamento')
    def validate_data_pagamento(self, value):
        """Valida se data pagamento não é futura (se informada)"""
        if value and value > date.today():
            raise ValidationError("Data de pagamento não pode ser futura")


class CalendarioDividendoResponseSchema(Schema):
    """Schema para resposta de CalendarioDividendo"""
    
    id = fields.UUID(description="ID do calendário")
    ativo_id = fields.UUID(description="ID do ativo")
    usuario_id = fields.UUID(description="ID do usuário")
    data_esperada = fields.Date(description="Data esperada do provento")
    tipo_provento = fields.String(description="Tipo do provento")
    yield_estimado = fields.Decimal(
        places=4,
        allow_none=True,
        description="Yield percentual estimado"
    )
    valor_estimado = fields.Decimal(
        places=2,
        allow_none=True,
        description="Valor estimado em R$"
    )
    quantidade = fields.Integer(description="Quantidade de ativos")
    status = fields.String(description="Status do calendário")
    observacoes = fields.String(
        allow_none=True,
        description="Observações adicionais"
    )
    data_pagamento = fields.Date(
        allow_none=True,
        description="Data real do pagamento"
    )
    valor_real = fields.Decimal(
        places=2,
        allow_none=True,
        description="Valor real pago em R$"
    )
    created_at = fields.DateTime(description="Data de criação")
    updated_at = fields.DateTime(description="Data de atualização")
    
    # Relacionamentos
    ativo = fields.Method(
        "get_ativo",
        allow_none=True,
        description="Dados do ativo"
    )

    def get_ativo(self, obj):
        if not getattr(obj, "ativo", None):
            return None
        return {
            "id": str(obj.ativo.id),
            "ticker": obj.ativo.ticker,
            "nome": obj.ativo.nome,
        }


class CalendarioDividendoConfirmarPagamentoSchema(Schema):
    """Schema para confirmação de pagamento"""
    
    data_pagamento = fields.Date(
        required=True,
        description="Data real do pagamento"
    )
    valor_real = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0),
        description="Valor real pago em R$"
    )
    
    @validates('data_pagamento')
    def validate_data_pagamento(self, value):
        """Valida se data pagamento não é futura"""
        if value > date.today():
            raise ValidationError("Data de pagamento não pode ser futura")


class CalendarioDividendoGerarSchema(Schema):
    """Schema para geração de calendário"""
    
    usuario_id = fields.UUID(required=True, description="ID do usuário")
    meses_futuros = fields.Integer(
        required=False,
        missing=12,
        validate=validate.Range(min=1, max=24),
        description="Quantidade de meses futuros"
    )
    ativo_id = fields.UUID(
        allow_none=True,
        description="ID do ativo específico (opcional)"
    )
