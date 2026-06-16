# backend/app/blueprints/relatorios.py - VERSÃO FUNCIONAL COMPLETA
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auditoria_relatorio_service import AuditoriaRelatorioService
from app.models.auditoria_relatorio import AuditoriaRelatorio

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/api')

@relatorios_bp.route('/relatorios', methods=['GET'])
@jwt_required()
def list_relatorios():
    """Lista relatórios do usuário logado"""
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    relatorios = AuditoriaRelatorioService.list_by_usuario(usuario_id, page, per_page)
    return jsonify({'data': relatorios, 'total': len(relatorios)}), 200

@relatorios_bp.route('/relatorios', methods=['POST'])
@jwt_required()
def create_relatorio():
    """Cria novo relatório de auditoria"""
    data = request.get_json()
    usuario_id = get_jwt_identity()
    relatorio = AuditoriaRelatorioService.create(usuario_id, data)
    return jsonify({'data': relatorio}), 201
