# -*- coding: utf-8 -*-
"""
Exitus - Assessora Schema
Validação e serialização de dados de assessoras
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class AssessoraSchema(Schema):
    """Schema para validação de assessoras"""
    
    id = fields.UUID(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    razao_social = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    cnpj = fields.Str(required=True, validate=validate.Length(min=14, max=18))
    email = fields.Email(required=True)
    telefone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    site = fields.Str(allow_none=True, validate=validate.Length(max=200))
    endereco = fields.Str(allow_none=True, validate=validate.Length(max=200))
    cidade = fields.Str(allow_none=True, validate=validate.Length(max=100))
    estado = fields.Str(allow_none=True, validate=validate.Length(min=2, max=2))
    cep = fields.Str(allow_none=True, validate=validate.Length(min=8, max=9))
    numero_cvm = fields.Str(allow_none=True, validate=validate.Length(max=50))
    anbima = fields.Bool(missing=False)
    ativo = fields.Bool(missing=True)
    data_cadastro = fields.DateTime(dump_only=True)
    logo_url = fields.Str(allow_none=True, validate=validate.Length(max=500))
    cor_primaria = fields.Str(missing='#3B82F6', validate=validate.Length(max=7))
    cor_secundaria = fields.Str(missing='#1E40AF', validate=validate.Length(max=7))
    max_usuarios = fields.Int(allow_none=True, validate=validate.Range(min=1))
    max_portfolios = fields.Int(allow_none=True, validate=validate.Range(min=1))
    plano = fields.Str(
        missing='basico',
        validate=validate.OneOf(['basico', 'profissional', 'enterprise'])
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Campos calculados (dump_only)
    total_usuarios = fields.Int(dump_only=True)
    total_portfolios = fields.Int(dump_only=True)
    pode_adicionar_usuario = fields.Bool(dump_only=True)
    pode_adicionar_portfolio = fields.Bool(dump_only=True)
    
    @validates('cnpj')
    def validate_cnpj(self, value):
        """Valida formato básico do CNPJ"""
        # Remove caracteres não numéricos
        cnpj_numeros = ''.join(filter(str.isdigit, value))
        
        if len(cnpj_numeros) != 14:
            raise ValidationError('CNPJ deve ter 14 dígitos')
        
        return value
    
    @validates('cor_primaria')
    def validate_cor_primaria(self, value):
        """Valida formato de cor hexadecimal"""
        if not value.startswith('#') or len(value) != 7:
            raise ValidationError('Cor deve estar no formato #RRGGBB')
        
        return value
    
    @validates('cor_secundaria')
    def validate_cor_secundaria(self, value):
        """Valida formato de cor hexadecimal"""
        if not value.startswith('#') or len(value) != 7:
            raise ValidationError('Cor deve estar no formato #RRGGBB')
        
        return value


class AssessoraCreateSchema(AssessoraSchema):
    """Schema para criação de assessora (campos obrigatórios)"""
    
    class Meta:
        exclude = ['id', 'created_at', 'updated_at', 'data_cadastro',
                   'total_usuarios', 'total_portfolios', 
                   'pode_adicionar_usuario', 'pode_adicionar_portfolio']


class AssessoraUpdateSchema(Schema):
    """Schema para atualização de assessora (todos campos opcionais)"""
    
    nome = fields.Str(validate=validate.Length(min=3, max=200))
    razao_social = fields.Str(validate=validate.Length(min=3, max=200))
    cnpj = fields.Str(validate=validate.Length(min=14, max=18))
    email = fields.Email()
    telefone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    site = fields.Str(allow_none=True, validate=validate.Length(max=200))
    endereco = fields.Str(allow_none=True, validate=validate.Length(max=200))
    cidade = fields.Str(allow_none=True, validate=validate.Length(max=100))
    estado = fields.Str(allow_none=True, validate=validate.Length(min=2, max=2))
    cep = fields.Str(allow_none=True, validate=validate.Length(min=8, max=9))
    numero_cvm = fields.Str(allow_none=True, validate=validate.Length(max=50))
    anbima = fields.Bool()
    ativo = fields.Bool()
    logo_url = fields.Str(allow_none=True, validate=validate.Length(max=500))
    cor_primaria = fields.Str(validate=validate.Length(max=7))
    cor_secundaria = fields.Str(validate=validate.Length(max=7))
    max_usuarios = fields.Int(allow_none=True, validate=validate.Range(min=1))
    max_portfolios = fields.Int(allow_none=True, validate=validate.Range(min=1))
    plano = fields.Str(validate=validate.OneOf(['basico', 'profissional', 'enterprise']))


class AssessoraStatsSchema(Schema):
    """Schema para estatísticas da assessora"""
    
    assessora_id = fields.UUID(required=True)
    nome = fields.Str(required=True)
    ativo = fields.Bool(required=True)
    plano = fields.Str(required=True)
    total_usuarios = fields.Int(required=True)
    usuarios_ativos = fields.Int(required=True)
    total_portfolios = fields.Int(required=True)
    portfolios_ativos = fields.Int(required=True)
    total_transacoes = fields.Int(required=True)
    volume_total = fields.Float(required=True)
    max_usuarios = fields.Int(allow_none=True)
    max_portfolios = fields.Int(allow_none=True)
    pode_adicionar_usuario = fields.Bool(required=True)
    pode_adicionar_portfolio = fields.Bool(required=True)
