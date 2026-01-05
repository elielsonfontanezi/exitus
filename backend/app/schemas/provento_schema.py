# -*- coding: utf-8 -*-
"""
Exitus - Provento Schema - Serialização Marshmallow
"""

from marshmallow import Schema, fields, post_dump, post_load, validates, ValidationError
from app.models.provento import TipoProvento

class ProventoSchema(Schema):
    """Schema para serialização de Proventos"""
    
    # Identificadores
    id = fields.UUID(dump_only=True)
    ativo_id = fields.UUID(required=True)
    
    # Tipo (ENUM - serializado customizado)
    tipo_provento = fields.Method("get_tipo_provento", deserialize="load_tipo_provento")
    
    # Valores monetários
    valor_por_acao = fields.Decimal(as_string=True, required=True)
    quantidade_ativos = fields.Decimal(as_string=True, required=True)
    valor_bruto = fields.Decimal(as_string=True, required=True)
    imposto_retido = fields.Decimal(as_string=True, default="0.00")
    valor_liquido = fields.Decimal(as_string=True, required=True)
    
    # Datas
    data_com = fields.Date(required=True)
    data_pagamento = fields.Date(required=True)
    
    # Observações
    observacoes = fields.String(allow_none=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # ✅ ADICIONAR: Campos nested do ativo
    ativo = fields.Method('get_ativo_info')
    
    def get_tipo_provento(self, obj):
        """
        Serializa enum TipoProvento corretamente.
        
        Garante que retorna apenas o valor (ex: "dividendo")
        e não "TipoProvento.DIVIDENDO"
        """
        if hasattr(obj.tipo_provento, 'value'):
            return obj.tipo_provento.value
        
        # Fallback: remove prefixo "TipoProvento." se existir
        tipo_str = str(obj.tipo_provento)
        if tipo_str.startswith('TipoProvento.'):
            tipo_str = tipo_str.replace('TipoProvento.', '').lower()
        
        return tipo_str
    
    def load_tipo_provento(self, value):
        """
        Deserializa tipo_provento de string para Enum.
        
        Args:
            value (str): Valor em lowercase (ex: "dividendo", "jcp")
        
        Returns:
            TipoProvento: Enum correspondente
        
        Raises:
            ValidationError: Se tipo inválido
        """
        try:
            # Converte "dividendo" -> TipoProvento.DIVIDENDO
            return TipoProvento[value.upper()]
        except (KeyError, AttributeError):
            raise ValidationError(
                f"Tipo de provento inválido: {value}. "
                f"Valores aceitos: {', '.join([t.value for t in TipoProvento])}"
            )


class ProventoCreateSchema(Schema):
    """Schema para criação de Provento"""
    ativo_id = fields.UUID(required=True)
    tipo_provento = fields.String(required=True)
    valor_por_acao = fields.Decimal(required=True)
    quantidade_ativos = fields.Decimal(required=True)
    valor_bruto = fields.Decimal(required=True)
    imposto_retido = fields.Decimal(missing="0.00")
    valor_liquido = fields.Decimal(required=True)
    data_com = fields.Date(required=True)
    data_pagamento = fields.Date(required=True)
    observacoes = fields.String(allow_none=True)
    
    @validates('tipo_provento')
    def validate_tipo_provento(self, value):
        """Valida e converte tipo_provento para UPPERCASE"""
        valid_tipos = ['dividendo', 'rendimento', 'jcp', 'bonificacao']
        
        if value.lower() not in valid_tipos:
            raise ValidationError(
                f"Tipo inválido: {value}. Use: {', '.join(valid_tipos)}"
            )
        
        # ✅ CONVERTER PARA UPPERCASE (PostgreSQL enum)
        return value.upper()

class ProventoUpdateSchema(Schema):
    """Schema para atualização de Provento (todos campos opcionais)"""
    
    tipo_provento = fields.String()
    valor_por_acao = fields.Decimal()
    quantidade_ativos = fields.Decimal()
    valor_bruto = fields.Decimal()
    imposto_retido = fields.Decimal()
    valor_liquido = fields.Decimal()
    data_com = fields.Date()
    data_pagamento = fields.Date()
    observacoes = fields.String(allow_none=True)


class ProventoResponseSchema(Schema):
    """
    Schema para resposta de API (inclui campos calculados).
    
    Herda de ProventoSchema e adiciona campos extras.
    """
    
    # Campos base do ProventoSchema
    id = fields.UUID(dump_only=True)
    ativo_id = fields.UUID()
    tipo_provento = fields.Method("get_tipo_provento")
    valor_por_acao = fields.Decimal(as_string=True)
    quantidade_ativos = fields.Decimal(as_string=True)
    valor_bruto = fields.Decimal(as_string=True)
    imposto_retido = fields.Decimal(as_string=True)
    valor_liquido = fields.Decimal(as_string=True)
    data_com = fields.Date()
    data_pagamento = fields.Date()
    observacoes = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Campos calculados/extras
    percentual_imposto = fields.Method("get_percentual_imposto")
    dias_ate_pagamento = fields.Method("get_dias_ate_pagamento")
    
    def get_tipo_provento(self, obj):
        """Serializa enum corretamente"""
        if hasattr(obj.tipo_provento, 'value'):
            return obj.tipo_provento.value
        return str(obj.tipo_provento).replace('TipoProvento.', '').lower()
    
    def get_percentual_imposto(self, obj):
        """Calcula percentual de imposto retido"""
        if hasattr(obj, 'percentual_imposto') and callable(obj.percentual_imposto):
            return float(obj.percentual_imposto())
        return 0.0
    
    def get_dias_ate_pagamento(self, obj):
        """Calcula dias até pagamento"""
        if hasattr(obj, 'dias_ate_pagamento') and callable(obj.dias_ate_pagamento):
            return obj.dias_ate_pagamento()
        return None
