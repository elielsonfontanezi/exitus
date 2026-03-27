"""Exitus - Blueprint Eventos - Módulo 3"""

from flask import Blueprint, jsonify

bp = Blueprint('eventos', __name__, url_prefix='/api/eventos')

@bp.route('', methods=['GET'])
def list_eventos():
    """Lista todos os eventos corporativos"""
    return jsonify({
        "success": True,
        "message": "Lista de eventos corporativos",
        "data": {
            "eventos": [],
            "total": 0
        }
    }), 200
