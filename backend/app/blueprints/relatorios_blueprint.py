# -*- coding: utf-8 -*-
"""
Exitus M7 - Relatórios Blueprint
24 endpoints REST para relatórios e alertas
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auditoria_relatorio_service import AuditoriaRelatorioService
from app.services.configuracao_alerta_service import ConfiguracaoAlertaService
from app.services.projecao_renda_service import ProjecaoRendaService
from app.services.relatorio_performance_service import RelatorioPerformanceService

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')

@relatorios_bp.route('/auditoria', methods=['GET'])
@jwt_required()
def listar_auditoria():
    """Lista histórico de relatórios do usuário"""
    usuario_id = get_jwt_identity()
    relatorios = AuditoriaRelatorioService.listar_por_usuario(usuario_id)
    return jsonify({'relatorios': [r.to_dict() for r in relatorios]})

@relatorios_bp.route('/projecoes', methods=['GET'])
@jwt_required()
def listar_projecoes():
    """Lista projeções de renda"""
    usuario_id = get_jwt_identity()
    projecoes = ProjecaoRendaService.listar_projecoes(usuario_id)
    return jsonify({'projecoes': [p.to_dict() for p in projecoes]})

@relatorios_bp.route('/performance', methods=['POST'])
@jwt_required()
def calcular_performance():
    """Calcula performance do período"""
    usuario_id = get_jwt_identity()
    data = request.json
    relatorio = RelatorioPerformanceService.calcular_performance(
        usuario_id, data['periodo_inicio'], data['periodo_fim']
    )
    return jsonify(relatorio.to_dict()), 201
