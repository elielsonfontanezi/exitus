"""M7.1 - Performance Blueprint Completo"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.relatorio_performance_service import RelatorioPerformanceService

performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')

@performance_bp.route('', methods=['GET'])
@jwt_required()
def list_performance():
    """Lista relatórios de performance"""
    usuario_id = get_jwt_identity()
    portfolio_id = request.args.get('portfolio_id')
    periodo = request.args.get('periodo', '12m')
    relatorios = RelatorioPerformanceService.list_by_usuario(usuario_id, portfolio_id, periodo)
    return jsonify({'data': relatorios}), 200

@performance_bp.route('', methods=['POST'])
@jwt_required()
def generate_performance():
    """Gera relatório de performance"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    relatorio = RelatorioPerformanceService.generate(usuario_id, data)
    return jsonify({'data': relatorio, 'message': 'Relatório gerado'}), 201

@performance_bp.route('/<uuid:relatorio_id>', methods=['GET'])
@jwt_required()
def get_performance(relatorio_id):
    """Detalhes relatório performance"""
    usuario_id = get_jwt_identity()
    relatorio = RelatorioPerformanceService.get_by_id(usuario_id, relatorio_id)
    return jsonify({'data': relatorio}), 200
