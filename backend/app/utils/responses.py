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
