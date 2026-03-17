# backend/app/schemas/ativo_schema.py
"""
Exitus - Ativo Schemas - Validação Marshmallow (COBERTURA GLOBAL)
"""
from marshmallow import Schema, fields, validates, ValidationError
#from marshmallowsqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Ativo, TipoAtivo, ClasseAtivo
from decimal import Decimal


class AtivoCreateSchema(Schema):
    """Schema para criação de ativo - Cobertura Global"""
    ticker = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 20)
    nome = fields.Str(required=True, validate=lambda x: 2 <= len(x) <= 200)
    tipo = fields.Str(required=True)
    classe = fields.Str(required=True)
    mercado = fields.Str(required=True, validate=lambda x: len(x) <= 10)
    bolsa_origem = fields.Str(required=False, allow_none=True, validate=lambda x: len(x) <= 20)
    moeda = fields.Str(required=True, validate=lambda x: len(x) == 3)
    
    # Indicadores (opcionais)
    preco_atual = fields.Decimal(required=False, as_string=True, allow_none=True)
    dividend_yield = fields.Decimal(required=False, as_string=True, allow_none=True)
    p_l = fields.Decimal(required=False, as_string=True, allow_none=True)
    p_vp = fields.Decimal(required=False, as_string=True, allow_none=True)
    roe = fields.Decimal(required=False, as_string=True, allow_none=True)
    beta = fields.Decimal(required=False, as_string=True, allow_none=True)
    preco_teto = fields.Decimal(required=False, as_string=True, allow_none=True)
    cap_rate = fields.Decimal(required=False, as_string=True, allow_none=True)
    
    # Status
    ativo = fields.Bool(required=False, default=True)
    deslistado = fields.Bool(required=False, default=False)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        """Valida se tipo é válido"""
        valid_tipos = [t.value for t in TipoAtivo]
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('classe')
    def validate_classe(self, value):
        """Valida se classe é válida"""
        valid_classes = [c.value for c in ClasseAtivo]
        if value.lower() not in valid_classes:
            raise ValidationError(f"Classe inválida. Opções: {', '.join(valid_classes)}")
    
    @validates('mercado')
    def validate_mercado(self, value):
        """Valida se mercado é válido"""
        valid_mercados = ['BR', 'US', 'EU', 'ASIA', 'GLOBAL']
        if value.upper() not in valid_mercados:
            raise ValidationError(f"Mercado inválido. Opções: {', '.join(valid_mercados)}")
    
    @validates('moeda')
    def validate_moeda(self, value):
        """Valida código ISO da moeda (3 letras maiúsculas)"""
        if not value.isupper() or len(value) != 3:
            raise ValidationError("Moeda deve ser código ISO 4217 (ex: BRL, USD, EUR)")
    
    @validates('ticker')
    def validate_ticker_format(self, value):
        """Valida formato do ticker"""
        if not value.replace('.', '').replace('-', '').isalnum():
            raise ValidationError("Ticker deve conter apenas letras, números, pontos e hífens")


class AtivoUpdateSchema(Schema):
    """Schema para atualização de ativo"""
    nome = fields.Str(required=False, validate=lambda x: 2 <= len(x) <= 200)
    tipo = fields.Str(required=False)
    classe = fields.Str(required=False)
    mercado = fields.Str(required=False, validate=lambda x: len(x) <= 10)
    bolsa_origem = fields.Str(required=False, allow_none=True)
    moeda = fields.Str(required=False, validate=lambda x: len(x) == 3)
    
    preco_atual = fields.Decimal(required=False, as_string=True, allow_none=True)
    dividend_yield = fields.Decimal(required=False, as_string=True, allow_none=True)
    p_l = fields.Decimal(required=False, as_string=True, allow_none=True)
    p_vp = fields.Decimal(required=False, as_string=True, allow_none=True)
    roe = fields.Decimal(required=False, as_string=True, allow_none=True)
    beta = fields.Decimal(required=False, as_string=True, allow_none=True)
    preco_teto = fields.Decimal(required=False, as_string=True, allow_none=True)
    cap_rate = fields.Decimal(required=False, as_string=True, allow_none=True)
    
    ativo = fields.Bool(required=False)
    deslistado = fields.Bool(required=False)
    data_deslistagem = fields.Date(required=False, allow_none=True)
    observacoes = fields.Str(required=False, allow_none=True)
    
    @validates('tipo')
    def validate_tipo(self, value):
        valid_tipos = [t.value for t in TipoAtivo]
        if value.lower() not in valid_tipos:
            raise ValidationError(f"Tipo inválido. Opções: {', '.join(valid_tipos)}")
    
    @validates('classe')
    def validate_classe(self, value):
        valid_classes = [c.value for t in ClasseAtivo]
        if value.lower() not in valid_classes:
            raise ValidationError(f"Classe inválida. Opções: {', '.join(valid_classes)}")
    
    @validates('mercado')
    def validate_mercado(self, value):
        valid_mercados = ['BR', 'US', 'EU', 'ASIA', 'GLOBAL']
        if value.upper() not in valid_mercados:
            raise ValidationError(f"Mercado inválido. Opções: {', '.join(valid_mercados)}")


class AtivoResponseSchema(SQLAlchemyAutoSchema):
    """Schema para resposta de ativo"""
    class Meta:
        model = Ativo
        load_instance = False
    
    tipo = fields.Method("get_tipo_str")
    classe = fields.Method("get_classe_str")
    preco_atual = fields.Decimal(as_string=True)
    dividend_yield = fields.Decimal(as_string=True)
    p_l = fields.Decimal(as_string=True)
    p_vp = fields.Decimal(as_string=True)
    roe = fields.Decimal(as_string=True)
    beta = fields.Decimal(as_string=True)
    preco_teto = fields.Decimal(as_string=True)
    cap_rate = fields.Decimal(as_string=True)
    
    def get_tipo_str(self, obj):
        """Converte Enum para string"""
        return obj.tipo.value if obj.tipo else None
    
    def get_classe_str(self, obj):
        """Converte Enum para string"""
        return obj.classe.value if obj.classe else None
