"""Exitus - Blueprint Posicoes - Módulo 3"""

from flask import Blueprint, jsonify

bp = Blueprint('posicoes', __name__, url_prefix='/api/posicoes')

@bp.route('', methods=['GET'])
def list_posicoes():
    """Lista todas as posições do usuário"""
    return jsonify({
        "success": True,
        "message": "Lista de posições",
        "data": {
            "posicoes": [],
            "total": 0
        }
    }), 200
