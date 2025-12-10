"""M7.1 - Relatórios Blueprint Completo"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auditoria_relatorio_service import AuditoriaRelatorioService
from app.models.auditoria_relatorio import AuditoriaRelatorio

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

@relatorios_bp.route('', methods=['GET'])
@jwt_required()
def list_relatorios():
    """Lista relatórios do usuário (paginado)"""
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        relatorios = AuditoriaRelatorioService.list_by_usuario(usuario_id, page, per_page)
        return jsonify({'data': relatorios, 'page': page, 'per_page': per_page}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('', methods=['POST'])
@jwt_required()
def create_relatorio():
    """Cria auditoria de relatório"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    relatorio = AuditoriaRelatorioService.create(usuario_id, data)
    return jsonify({'data': relatorio, 'message': 'Relatório criado'}), 201
