# -*- coding: utf-8 -*-
"""
Exitus — Hierarquia de exceções tipadas para mapeamento semântico HTTP.

Uso nos services:
    from app.utils.exceptions import NotFoundError, ConflictError
    raise NotFoundError("Ativo não encontrado")

O handler genérico em app/__init__.py converte automaticamente para a
resposta HTTP correta, sem necessidade de tratamento em cada blueprint.
"""


class ExitusError(Exception):
    """Exceção base do sistema Exitus."""
    http_status: int = 500


class NotFoundError(ExitusError):
    """Recurso não encontrado — HTTP 404."""
    http_status = 404


class ConflictError(ExitusError):
    """Conflito de unicidade ou integridade referencial — HTTP 409."""
    http_status = 409


class ForbiddenError(ExitusError):
    """Acesso negado — HTTP 403."""
    http_status = 403


class BusinessRuleError(ExitusError):
    """Violação de regra de negócio — HTTP 422."""
    http_status = 422


class ValidationError(ExitusError):
    """Erro de validação de dados — HTTP 400."""
    http_status = 400
