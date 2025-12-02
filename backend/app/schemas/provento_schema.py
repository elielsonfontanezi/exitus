# -*- coding: utf-8 -*-
"""
Exitus - Provento Schemas - Validação Marshmallow
"""

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Provento
from decimal import Decimal


class ProventoCreateSchema(Schema):
    """Schema para criação de provento"""
    
    ativo_id = fields.UUID(required=True)
    tipo_provento = fields.Str(required=True)
    valor_por_acao = fields.Decimal(required=True, as_string=True)
    quantidade_ativos = fields.Decimal(required=True, as_string=True)
    valor_bruto = fields.Decimal(required=False, as_string=True)
    imposto_retido = fields.Decimal(required=False, as_string=True, load_default=0)
    valor_liquido = fields.Decimal(required=False, as_string=True)
    data_com = fields.Date(required=True)
    data_pagamento = fields.Date(required=True)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo_provento')
    def validate_tipo(self, value):
        """Valida tipo de provento"""
        valid_tipos = ['dividendo', 'jcp', 'rendimento', 'bonificacao', 'direito']
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('valor_por_acao')
    def validate_valor(self, value):
        """Valida valor positivo"""
        if Decimal(str(value)) <= 0:
            raise ValidationError("Valor por ação deve ser maior que zero")
    
    @validates('quantidade_ativos')
    def validate_quantidade(self, value):
        """Valida quantidade positiva"""
        if Decimal(str(value)) <= 0:
            raise ValidationError("Quantidade deve ser maior que zero")
    
    @validates_schema
    def validate_datas(self, data, **kwargs):
        """Valida datas"""
        if data.get('data_pagamento') and data.get('data_com'):
            if data['data_pagamento'] < data['data_com']:
                raise ValidationError({'data_pagamento': 'Data de pagamento deve ser >= data COM'})
        
        if data.get('valor_bruto') and data.get('imposto_retido'):
            if Decimal(str(data['imposto_retido'])) > Decimal(str(data['valor_bruto'])):
                raise ValidationError({'imposto_retido': 'Imposto não pode ser maior que valor bruto'})


class ProventoUpdateSchema(Schema):
    """Schema para atualização de provento"""
    
    tipo_provento = fields.Str(required=False)
    valor_por_acao = fields.Decimal(required=False, as_string=True)
    quantidade_ativos = fields.Decimal(required=False, as_string=True)
    valor_bruto = fields.Decimal(required=False, as_string=True)
    imposto_retido = fields.Decimal(required=False, as_string=True)
    valor_liquido = fields.Decimal(required=False, as_string=True)
    data_com = fields.Date(required=False)
    data_pagamento = fields.Date(required=False)
    observacoes = fields.Str(required=False, allow_none=True)


class ProventoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de provento"""
    
    class Meta:
        model = Provento
        load_instance = False
        include_fk = True
    
    tipo_provento = fields.Method("get_tipo_str")
    valor_por_acao = fields.Decimal(as_string=True)
    quantidade_ativos = fields.Decimal(as_string=True)
    valor_bruto = fields.Decimal(as_string=True)
    imposto_retido = fields.Decimal(as_string=True)
    valor_liquido = fields.Decimal(as_string=True)
    
    ativo = fields.Method("get_ativo_info")
    
    def get_tipo_str(self, obj):
        return obj.tipo_provento.value if obj.tipo_provento else None
    
    def get_ativo_info(self, obj):
        if obj.ativo:
            return {
                'id': str(obj.ativo.id),
                'ticker': obj.ativo.ticker,
                'nome': obj.ativo.nome,
                'tipo': obj.ativo.tipo.value
            }
        return None
