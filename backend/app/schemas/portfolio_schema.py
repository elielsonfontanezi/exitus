# backend/app/schemas/portfolio_schema.py
# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Schemas
Schemas Marshmallow para validação e serialização de dados de Portfolio.
"""
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Portfolio

class PortfolioCreateSchema(Schema):
    """Schema para criação de um novo portfolio."""
    nome = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100),
        error_messages={"required": "O nome do portfolio é obrigatório."}
    )
    descricao = fields.Str(
        required=False,
        validate=validate.Length(max=500)
    )
    objetivo = fields.Str(
        required=False,
        validate=validate.Length(max=100)
    )

class PortfolioUpdateSchema(Schema):
    """Schema para atualização de um portfolio. Todos os campos são opcionais."""
    nome = fields.Str(
        required=False,
        validate=validate.Length(min=3, max=100)
    )
    descricao = fields.Str(
        required=False,
        validate=validate.Length(max=500)
    )
    objetivo = fields.Str(
        required=False,
        validate=validate.Length(max=100)
    )

class PortfolioResponseSchema(SQLAlchemyAutoSchema):
    """Schema para serializar a resposta de um portfolio."""
    class Meta:
        model = Portfolio
        load_instance = False
        exclude = ("usuario",) # Exclui o objeto de relacionamento para evitar loops

    id = fields.UUID()
    usuario_id = fields.UUID()
    created_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
    updated_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')
