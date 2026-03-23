# -*- coding: utf-8 -*-
"""
Exitus - Carteira Blueprint
Rotas para dados consolidados da carteira (saldo, resumo, etc.)
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.carteira_service import CarteiraService
from app.utils.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

carteira_bp = Blueprint('carteira', __name__, url_prefix='/api/carteira')


@carteira_bp.route('/saldo-caixa', methods=['GET'])
@jwt_required()
def get_saldo_caixa():
    """
    Retorna saldo disponível em caixa do usuário.
    
    Query params:
        - moeda: BRL ou USD (default: BRL)
    
    Returns:
        {
            "saldo_brl": 12450.00,
            "saldo_usd": 2280.50,
            "moeda_exibicao": "BRL",
            "taxa_cambio": 5.46
        }
    """
    try:
        usuario_id = get_jwt_identity()
        moeda = request.args.get('moeda', 'BRL').upper()
        
        dados = CarteiraService.get_saldo_caixa(usuario_id, moeda)
        
        return success_response(
            data=dados,
            message="Saldo em caixa obtido com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter saldo em caixa: {e}")
        return error_response(str(e), 500)
