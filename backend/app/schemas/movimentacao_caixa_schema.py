# -*- coding: utf-8 -*-
"""
Exitus - MovimentacaoCaixa Schemas - Validação Marshmallow
"""

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import MovimentacaoCaixa
from decimal import Decimal


class MovimentacaoCaixaCreateSchema(Schema):
    """Schema para criação de movimentação"""
    
    corretora_id = fields.UUID(required=True)
    corretora_destino_id = fields.UUID(required=False, allow_none=True)
    provento_id = fields.UUID(required=False, allow_none=True)
    tipo_movimentacao = fields.Str(required=True)
    valor = fields.Decimal(required=True, as_string=True)
    moeda = fields.Str(required=True)
    data_movimentacao = fields.Date(required=True)
    descricao = fields.Str(required=False, allow_none=True)
    comprovante = fields.Str(required=False, allow_none=True)
    
    @validates('tipo_movimentacao')
    def validate_tipo(self, value):
        """Valida tipo de movimentação"""
        valid_tipos = [
            'deposito', 'saque', 'transferencia_enviada', 
            'transferencia_recebida', 'credito_provento', 
            'pagamento_taxa', 'pagamento_imposto', 'ajuste', 'outro'
        ]
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('valor')
    def validate_valor(self, value):
        """Valida valor positivo"""
        if Decimal(str(value)) <= 0:
            raise ValidationError("Valor deve ser maior que zero")
    
    @validates('moeda')
    def validate_moeda(self, value):
        """Valida código ISO da moeda"""
        if not value.isupper() or len(value) != 3:
            raise ValidationError("Moeda deve ser código ISO 4217 (ex: BRL, USD, EUR)")
    
    @validates_schema
    def validate_transferencia(self, data, **kwargs):
        """Valida transferências"""
        tipo = data.get('tipo_movimentacao', '').lower()
        
        if tipo in ['transferencia_enviada', 'transferencia_recebida']:
            if not data.get('corretora_destino_id'):
                raise ValidationError({'corretora_destino_id': 'Transferência requer corretora de destino'})
        
        if tipo == 'credito_provento':
            if not data.get('provento_id'):
                raise ValidationError({'provento_id': 'Crédito de provento requer provento_id'})


class MovimentacaoCaixaUpdateSchema(Schema):
    """Schema para atualização de movimentação"""
    
    tipo_movimentacao = fields.Str(required=False)
    valor = fields.Decimal(required=False, as_string=True)
    moeda = fields.Str(required=False)
    data_movimentacao = fields.Date(required=False)
    descricao = fields.Str(required=False, allow_none=True)
    comprovante = fields.Str(required=False, allow_none=True)


class MovimentacaoCaixaResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de movimentação"""
    
    class Meta:
        model = MovimentacaoCaixa
        load_instance = False
        include_fk = True
    
    tipo_movimentacao = fields.Method("get_tipo_str")
    valor = fields.Decimal(as_string=True)
    
    corretora = fields.Method("get_corretora_info")
    corretora_destino = fields.Method("get_corretora_destino_info")
    provento = fields.Method("get_provento_info")
    
    def get_tipo_str(self, obj):
        return obj.tipo_movimentacao.value if obj.tipo_movimentacao else None
    
    def get_corretora_info(self, obj):
        if obj.corretora:
            return {
                'id': str(obj.corretora.id),
                'nome': obj.corretora.nome,
                'tipo': obj.corretora.tipo.value
            }
        return None
    
    def get_corretora_destino_info(self, obj):
        if obj.corretora_destino:
            return {
                'id': str(obj.corretora_destino.id),
                'nome': obj.corretora_destino.nome
            }
        return None
    
    def get_provento_info(self, obj):
        if obj.provento:
            return {
                'id': str(obj.provento.id),
                'tipo': obj.provento.tipo_provento.value,
                'valor': float(obj.provento.valor_liquido)
            }
        return None
