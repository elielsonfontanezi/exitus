"""M7.1 - Alertas Blueprint Completo"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.configuracao_alerta_service import ConfiguracaoAlertaService

alertas_bp = Blueprint('alertas', __name__, url_prefix='/api/alertas')

@alertas_bp.route('', methods=['GET'])
@jwt_required()
def list_alertas():
    """Lista alertas do usuário"""
    usuario_id = get_jwt_identity()
    ativo_id = request.args.get('ativo_id')
    alertas = ConfiguracaoAlertaService.list_by_usuario(usuario_id, ativo_id)
    return jsonify({'data': alertas}), 200

@alertas_bp.route('', methods=['POST'])
@jwt_required()
def create_alerta():
    """Cria novo alerta"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    alerta = ConfiguracaoAlertaService.create(usuario_id, data)
    return jsonify({'data': alerta, 'message': 'Alerta criado'}), 201

@alertas_bp.route('/<uuid:alerta_id>', methods=['PUT'])
@jwt_required()
def update_alerta(alerta_id):
    """Atualiza alerta"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    alerta = ConfiguracaoAlertaService.update(usuario_id, alerta_id, data)
    return jsonify({'data': alerta}), 200

@alertas_bp.route('/<uuid:alerta_id>', methods=['DELETE'])
@jwt_required()
def delete_alerta(alerta_id):
    """Remove alerta"""
    usuario_id = get_jwt_identity()
    ConfiguracaoAlertaService.delete(usuario_id, alerta_id)
    return jsonify({'message': 'Alerta removido'}), 200
