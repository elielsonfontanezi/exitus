"""M7.1 - Projeções Blueprint Completo"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.projecao_renda_service import ProjecaoRendaService

projecoes_bp = Blueprint('projecoes', __name__, url_prefix='/api/projecoes')

@projecoes_bp.route('', methods=['GET'])
@jwt_required()
def list_projecoes():
    """Lista projeções de renda"""
    usuario_id = get_jwt_identity()
    portfolio_id = request.args.get('portfolio_id')
    mes_ano = request.args.get('mes_ano')
    projecoes = ProjecaoRendaService.list_by_usuario(usuario_id, portfolio_id, mes_ano)
    return jsonify({'data': projecoes}), 200

@projecoes_bp.route('', methods=['POST'])
@jwt_required()
def create_projecao():
    """Gera projeção de renda"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    projecao = ProjecaoRendaService.create_or_update(usuario_id, data)
    return jsonify({'data': projecao, 'message': 'Projeção gerada'}), 201

@projecoes_bp.route('/<mes_ano>', methods=['GET'])
@jwt_required()
def get_projecao_mes(mes_ano):
    """Projeção por mês/ano"""
    usuario_id = get_jwt_identity()
    projecao = ProjecaoRendaService.get_by_mes_ano(usuario_id, mes_ano)
    return jsonify({'data': projecao}), 200
