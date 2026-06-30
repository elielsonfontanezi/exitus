# -*- coding: utf-8 -*-
"""Blueprint de indicadores macro para o dashboard."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.services.indicadores_service import IndicadoresService

indicadores_bp = Blueprint('indicadores', __name__, url_prefix='/api/indicadores')


@indicadores_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_indicadores_dashboard():
    """Indicadores CDI, Ibovespa, IPCA e SELIC para o painel de benchmark."""
    try:
        dados = IndicadoresService.get_dashboard_indicadores()
        return jsonify({'success': True, 'data': dados}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
