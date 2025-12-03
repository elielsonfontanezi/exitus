# -*- coding: utf-8 -*-
"""
Exitus - EventoCorporativo Schemas - Validação Marshmallow
"""

from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import EventoCorporativo
from decimal import Decimal


class EventoCorporativoCreateSchema(Schema):
    """Schema para criação de evento corporativo"""
    
    ativo_id = fields.UUID(required=True)
    tipo_evento = fields.Str(required=True)
    descricao = fields.Str(required=True)
    data_anuncio = fields.Date(required=True)
    data_com = fields.Date(required=False, allow_none=True)
    data_aprovacao = fields.Date(required=False, allow_none=True)
    data_execucao = fields.Date(required=False, allow_none=True)
    proporcao = fields.Str(required=False, allow_none=True)
    preco_subscricao = fields.Decimal(required=False, allow_none=True, as_string=True)
    observacoes = fields.Str(required=False, allow_none=True)
    url_informacao = fields.Str(required=False, allow_none=True)
    
    @validates('tipo_evento')
    def validate_tipo(self, value):
        """Valida tipo de evento"""
        valid_tipos = [
            'desdobramento', 'grupamento', 'bonificacao', 'subscricao',
            'incorporacao', 'cisao', 'fusao', 'mudanca_ticker', 'oferta_publica'
        ]
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('proporcao')
    def validate_proporcao(self, value):
        """Valida formato da proporção (ex: '2:1', '1:10')"""
        if value:
            if ':' not in value:
                raise ValidationError("Proporção deve estar no formato 'X:Y' (ex: '2:1', '1:10')")
            
            try:
                partes = value.split(':')
                if len(partes) != 2:
                    raise ValidationError("Proporção inválida")
                
                numerador = float(partes[0])
                denominador = float(partes[1])
                
                if numerador <= 0 or denominador <= 0:
                    raise ValidationError("Valores da proporção devem ser positivos")
            except (ValueError, IndexError):
                raise ValidationError("Formato de proporção inválido")
    
    @validates('preco_subscricao')
    def validate_preco(self, value):
        """Valida preço de subscrição"""
        if value is not None and Decimal(str(value)) <= 0:
            raise ValidationError("Preço de subscrição deve ser maior que zero")
    
    @validates_schema
    def validate_datas(self, data, **kwargs):
        """Valida ordem das datas"""
        data_anuncio = data.get('data_anuncio')
        data_com = data.get('data_com')
        data_aprovacao = data.get('data_aprovacao')
        data_execucao = data.get('data_execucao')
        
        if data_com and data_anuncio:
            if data_com < data_anuncio:
                raise ValidationError({'data_com': 'Data COM deve ser >= data de anúncio'})
        
        if data_execucao and data_anuncio:
            if data_execucao < data_anuncio:
                raise ValidationError({'data_execucao': 'Data de execução deve ser >= data de anúncio'})
        
        # Subscrição requer preço
        if data.get('tipo_evento', '').lower() == 'subscricao':
            if not data.get('preco_subscricao'):
                raise ValidationError({'preco_subscricao': 'Subscrição requer preço de subscrição'})


class EventoCorporativoUpdateSchema(Schema):
    """Schema para atualização de evento corporativo"""
    
    tipo_evento = fields.Str(required=False)
    descricao = fields.Str(required=False)
    data_anuncio = fields.Date(required=False)
    data_com = fields.Date(required=False, allow_none=True)
    data_aprovacao = fields.Date(required=False, allow_none=True)
    data_execucao = fields.Date(required=False, allow_none=True)
    proporcao = fields.Str(required=False, allow_none=True)
    preco_subscricao = fields.Decimal(required=False, allow_none=True, as_string=True)
    observacoes = fields.Str(required=False, allow_none=True)
    url_informacao = fields.Str(required=False, allow_none=True)


class EventoCorporativoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de evento corporativo"""
    
    class Meta:
        model = EventoCorporativo
        load_instance = False
        include_fk = True
    
    tipo_evento = fields.Method("get_tipo_str")
    preco_subscricao = fields.Decimal(as_string=True)
    
    ativo = fields.Method("get_ativo_info")
    
    def get_tipo_str(self, obj):
        return obj.tipo_evento.value if obj.tipo_evento else None
    
    def get_ativo_info(self, obj):
        if obj.ativo:
            return {
                'id': str(obj.ativo.id),
                'ticker': obj.ativo.ticker,
                'nome': obj.ativo.nome,
                'tipo': obj.ativo.tipo.value
            }
        return None
