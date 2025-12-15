# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Blueprint
Rotas para analytics de portfólio
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.portfolio_service import PortfolioService
from app.utils.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


@portfolio_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Retorna dashboard completo do portfólio"""
    try:
        usuario_id = get_jwt_identity()
        dados = PortfolioService.get_dashboard(usuario_id)
        
        return success_response(
            data=dados,
            message="Dashboard gerado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/alocacao', methods=['GET'])
@jwt_required()
def alocacao():
    """Retorna alocação do portfólio por classe de ativo"""
    try:
        usuario_id = get_jwt_identity()
        alocacao_data = PortfolioService.get_alocacao(usuario_id)

        return success_response(
            data=alocacao_data,
            message="Alocação por classe calculada"
        )

    except Exception as e:
        logger.error(f"Erro ao calcular alocação: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/distribuicao/classes', methods=['GET'])
@jwt_required()
def distribuicao_classes():
    """Retorna distribuição por classe de ativo"""
    try:
        usuario_id = get_jwt_identity()
        distribuicao = PortfolioService.get_distribuicao_classes(usuario_id)
        
        return success_response(
            data=distribuicao,
            message="Distribuição por classes calculada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular distribuição: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/distribuicao/setores', methods=['GET'])
@jwt_required()
def distribuicao_setores():
    """Retorna distribuição por setor"""
    try:
        usuario_id = get_jwt_identity()
        distribuicao = PortfolioService.get_distribuicao_setores(usuario_id)
        
        return success_response(
            data={'setores': distribuicao},
            message="Distribuição por setores calculada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular distribuição: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/evolucao', methods=['GET'])
@jwt_required()
def evolucao_patrimonio():
    """Retorna evolução do patrimônio ao longo do tempo"""
    try:
        usuario_id = get_jwt_identity()
        meses = request.args.get('meses', 12, type=int)
        
        if meses < 1 or meses > 60:
            return error_response("Meses deve estar entre 1 e 60", 400)
        
        evolucao = PortfolioService.get_evolucao_patrimonio(usuario_id, meses)
        
        return success_response(
            data={'evolucao': evolucao},
            message=f"Evolução de {meses} meses calculada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular evolução: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/metricas-risco', methods=['GET'])
@jwt_required()
def metricas_risco():
    """Retorna métricas de risco do portfólio"""
    try:
        usuario_id = get_jwt_identity()
        metricas = PortfolioService.get_metricas_risco(usuario_id)
        
        return success_response(
            data=metricas,
            message="Métricas de risco calculadas"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {e}")
        return error_response(str(e), 500)


@portfolio_bp.route('/performance', methods=['GET'])
@jwt_required()
def performance_ativos():
    """Retorna performance individual de cada ativo"""
    try:
        usuario_id = get_jwt_identity()
        performance = PortfolioService.get_performance_ativos(usuario_id)
        
        return success_response(
            data={'ativos': performance, 'total': len(performance)},
            message="Performance calculada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular performance: {e}")
        return error_response(str(e), 500)
