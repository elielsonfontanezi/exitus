# -*- coding: utf-8 -*-
"""Exitus - db_utils.py - Helpers SQLAlchemy (EXITUS-SQLALCHEMY-001)

Funções utilitárias para uso seguro e consistente do SQLAlchemy.
Centraliza padrões para evitar erros recorrentes:
  - validate_enum()       → evita AttributeError em enums
  - safe_commit()         → evita PendingRollbackError
  - validate_positive()   → evita CheckViolation em constraints
  - safe_add_commit()     → padrão completo de insert seguro

Uso:
    from app.utils.db_utils import safe_commit, validate_enum, validate_positive
"""

import logging
from app.database import db

logger = logging.getLogger(__name__)


def validate_enum(enum_class, value, default=None):
    """Valida e converte string para enum, retornando default se inválido.

    Evita AttributeError ao acessar enum inexistente.

    Args:
        enum_class: Classe do enum (ex: TipoAtivo, ClasseAtivo)
        value:      Valor a converter (string ou o próprio enum)
        default:    Valor padrão se inválido (None lança ValueError)

    Returns:
        Membro do enum correspondente.

    Raises:
        ValueError: Se value inválido e default=None.

    Exemplo:
        tipo = validate_enum(TipoAtivo, 'acao', default=TipoAtivo.OUTRO)
    """
    if isinstance(value, enum_class):
        return value
    try:
        return enum_class(value)
    except (ValueError, KeyError):
        try:
            return enum_class[value.upper()] if isinstance(value, str) else enum_class[value]
        except (KeyError, AttributeError):
            if default is not None:
                logger.warning(f"Enum {enum_class.__name__}: valor '{value}' inválido, usando default '{default}'")
                return default
            raise ValueError(f"Valor '{value}' inválido para {enum_class.__name__}. "
                             f"Válidos: {[e.value for e in enum_class]}")


def safe_commit(session=None):
    """Commit seguro com rollback automático em caso de erro.

    Evita PendingRollbackError ao garantir rollback antes de re-raise.

    Args:
        session: Sessão SQLAlchemy (usa db.session se None)

    Raises:
        Exception: Re-lança a exceção original após rollback.

    Exemplo:
        db.session.add(objeto)
        safe_commit()
    """
    s = session or db.session
    try:
        s.commit()
    except Exception as e:
        s.rollback()
        logger.error(f"safe_commit: rollback executado — {type(e).__name__}: {e}")
        raise


def validate_positive(value, field_name, allow_zero=False):
    """Valida que valor numérico é positivo (ou >= 0 se allow_zero=True).

    Evita CheckViolation em constraints de quantidade/valor positivo.

    Args:
        value:      Valor numérico a validar.
        field_name: Nome do campo (para mensagem de erro).
        allow_zero: Se True, aceita zero (default False).

    Raises:
        ValueError: Se valor violar a constraint.

    Exemplo:
        validate_positive(quantidade, 'quantidade')
        validate_positive(preco, 'preco', allow_zero=False)
    """
    if value is None:
        raise ValueError(f"Campo '{field_name}' não pode ser None")
    threshold = 0 if allow_zero else 0
    if allow_zero and value < 0:
        raise ValueError(f"Campo '{field_name}' deve ser >= 0, recebido: {value}")
    if not allow_zero and value <= 0:
        raise ValueError(f"Campo '{field_name}' deve ser > 0, recebido: {value}")


def safe_add_commit(obj, session=None):
    """Adiciona objeto à sessão e faz commit seguro.

    Padrão completo de insert: add + commit + refresh.

    Args:
        obj:     Instância do model SQLAlchemy a persistir.
        session: Sessão SQLAlchemy (usa db.session se None).

    Returns:
        O mesmo objeto, com ID e timestamps preenchidos.

    Raises:
        Exception: Re-lança após rollback em caso de erro.

    Exemplo:
        usuario = Usuario(username='admin', ...)
        usuario = safe_add_commit(usuario)
        print(usuario.id)  # UUID gerado
    """
    s = session or db.session
    try:
        s.add(obj)
        s.commit()
        s.refresh(obj)
        return obj
    except Exception as e:
        s.rollback()
        logger.error(f"safe_add_commit: rollback — {type(e).__name__}: {e}")
        raise


def safe_delete_commit(obj, session=None):
    """Remove objeto da sessão e faz commit seguro.

    Args:
        obj:     Instância do model SQLAlchemy a remover.
        session: Sessão SQLAlchemy (usa db.session se None).

    Raises:
        Exception: Re-lança após rollback em caso de erro.
    """
    s = session or db.session
    try:
        s.delete(obj)
        s.commit()
    except Exception as e:
        s.rollback()
        logger.error(f"safe_delete_commit: rollback — {type(e).__name__}: {e}")
        raise


def flush_or_rollback(session=None):
    """Flush seguro com rollback automático.

    Útil para obter IDs gerados (UUID/serial) antes do commit final,
    mantendo tudo dentro da mesma transação.

    Args:
        session: Sessão SQLAlchemy (usa db.session se None).

    Raises:
        Exception: Re-lança após rollback em caso de erro.

    Exemplo:
        db.session.add(portfolio)
        flush_or_rollback()
        print(portfolio.id)  # UUID disponível antes do commit final
        db.session.add(posicao)  # usa portfolio.id como FK
        safe_commit()
    """
    s = session or db.session
    try:
        s.flush()
    except Exception as e:
        s.rollback()
        logger.error(f"flush_or_rollback: rollback — {type(e).__name__}: {e}")
        raise
