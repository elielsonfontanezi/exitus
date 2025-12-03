"""Exitus - Blueprint Proventos - Módulo 3"""

from flask import Blueprint, jsonify

bp = Blueprint('proventos', __name__, url_prefix='/api/proventos')

@bp.route('', methods=['GET'])
def list_proventos():
    """Lista todos os proventos do usuário"""
    return jsonify({
        "success": True,
        "message": "Lista de proventos",
        "data": {
            "proventos": [],
            "total": 0
        }
    }), 200
