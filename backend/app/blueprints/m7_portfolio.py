from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.relatorio_service import RelatorioService
from uuid import UUID

bp_m7 = Blueprint('m7_portfolio', __name__, url_prefix='/api/m7')

@bp_m7.route('/portfolio', methods=['GET'])
@jwt_required()
def portfolio():
    # FIX: get_jwt_identity() já retorna string UUID diretamente
    usuario_id = UUID(get_jwt_identity())
    return jsonify(RelatorioService.portfolio_simple(usuario_id))
