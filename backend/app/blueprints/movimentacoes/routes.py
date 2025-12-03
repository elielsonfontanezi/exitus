"""Exitus - Blueprint Movimentacoes - Módulo 3"""

from flask import Blueprint, jsonify

bp = Blueprint('movimentacoes', __name__, url_prefix='/api/movimentacoes')

@bp.route('', methods=['GET'])
def list_movimentacoes():
    """Lista todas as movimentações de caixa"""
    return jsonify({
        "success": True,
        "message": "Lista de movimentações",
        "data": {
            "movimentacoes": [],
            "total": 0
        }
    }), 200
