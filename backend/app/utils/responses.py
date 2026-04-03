# -*- coding: utf-8 -*-
"""Exitus - Utility Responses - Respostas padronizadas"""

from flask import jsonify

def success(data=None, message="Sucesso", status=200):
    """Resposta de sucesso padronizada."""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status

def error(message="Erro interno do servidor", status=500):
    """Resposta de erro genérico."""
    return jsonify({
        "success": False,
        "message": message
    }), status

def unauthorized(message="Não autorizado"):
    """Resposta 401."""
    return jsonify({
        "success": False,
        "message": message
    }), 401

def forbidden(message="Acesso negado"):
    """Resposta 403."""
    return jsonify({
        "success": False,
        "message": message
    }), 403

def not_found(message="Recurso não encontrado"):
    """Resposta 404."""
    return jsonify({
        "success": False,
        "message": message
    }), 404

def paginated_response(items, total, page, per_page, message="Sucesso"):
    """Resposta paginada padronizada."""
    return jsonify({
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
        }
    }), 200

# ============================================
# ALIASES para retrocompatibilidade
# ============================================
success_response = success
error_response = error
unauthorized_response = unauthorized
forbidden_response = forbidden
not_found_response = not_found
