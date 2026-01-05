# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Blueprint
Rotas para analytics de portfólio
"""

import logging
from uuid import UUID
from marshmallow import ValidationError
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.portfolio_service import PortfolioService
from app.utils.responses import success_response, error_response
# Schema imports (verificar se existem, caso contrário criar os schemas)
from app.schemas.portfolio_schema import PortfolioCreateSchema, PortfolioUpdateSchema, PortfolioResponseSchema

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolios')


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

# Adicionar ao final do arquivo, antes do último comentário

@portfolio_bp.route('/alocacao', methods=['GET'])
@jwt_required()
def get_alocacao():
    """Retorna alocação do portfólio por classe de ativo."""
    from uuid import UUID
    from flask import jsonify
    from flask_jwt_extended import get_jwt_identity
    import logging
    
    logger = logging.getLogger(__name__)
    usuario_id = UUID(get_jwt_identity())
    
    try:
        alocacao_data = PortfolioService.get_alocacao(usuario_id)
        return jsonify(alocacao_data), 200
    except Exception as e:
        logger.error(f"Erro ao calcular alocação: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CRUD COMPLETO - ROTAS FALTANTES
# ============================================================================

# --- 1. GET /api/portfolios - LISTAR PORTFOLIOS ---
# ADICIONAR no portfolio_service.py (após get_all_for_user)

@portfolio_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_portfolios():
    """
    Lista portfolios do usuário com paginação.
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # CORREÇÃO: Usar get_all_for_user (nome correto do método no service)
        pagination = PortfolioService.get_all(usuario_id, page, per_page)
        
        return success_response(  # CORREÇÃO: snake_case
            data={
                'portfolios': [
                    {
                        'id': str(p.id),
                        'nome': p.nome,
                        'descricao': p.descricao,
                        'objetivo': p.objetivo,
                        'ativo': p.ativo,
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None
                    } for p in pagination.items
                ],
                'total': pagination.total,
                'pages': pagination.pages,
                'page': pagination.page
            },
            message=f"{pagination.total} portfolios encontrados"
        )
    except Exception as e:
        logger.error(f"Erro ao listar portfolios: {e}")
        return error_response(str(e), 500)  # CORREÇÃO: snake_case


# --- 2. GET /api/portfolios/<id> - BUSCAR PORTFOLIO POR ID ---
@portfolio_bp.route('/<uuid:portfolio_id>', methods=['GET'])
@jwt_required()
def get_portfolio_by_id(portfolio_id):
    """
    Busca portfolio por ID.
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        
        portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
        
        if not portfolio:
            return error_response("Portfolio não encontrado", 404)  # CORREÇÃO
        
        return success_response(  # CORREÇÃO
            data={
                'id': str(portfolio.id),
                'nome': portfolio.nome,
                'descricao': portfolio.descricao,
                'objetivo': portfolio.objetivo,
                'ativo': portfolio.ativo,
                'usuario_id': str(portfolio.usuario_id),
                'created_at': portfolio.created_at.isoformat() if hasattr(portfolio, 'created_at') else None,
                'updated_at': portfolio.updated_at.isoformat() if hasattr(portfolio, 'updated_at') else None
            },
            message="Portfolio encontrado"
        )
    except ValueError as e:
        return error_response(str(e), 404)  # CORREÇÃO
    except Exception as e:
        logger.error(f"Erro ao buscar portfolio: {e}")
        return error_response(str(e), 500)  # CORREÇÃO


# --- 3. POST /api/portfolios - CRIAR PORTFOLIO ---
@portfolio_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_portfolio():
    """
    Cria novo portfolio.
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        data = request.get_json()
        
        # Validações básicas
        if not data.get('nome'):
            return error_response("Nome do portfolio é obrigatório", 400)  # CORREÇÃO
        
        # CORREÇÃO: Inverter ordem dos parâmetros (service espera data primeiro)
        novo_portfolio = PortfolioService.create(data, usuario_id)
        
        return success_response(  # CORREÇÃO
            data={
                'id': str(novo_portfolio.id),
                'nome': novo_portfolio.nome,
                'descricao': novo_portfolio.descricao,
                'objetivo': novo_portfolio.objetivo,
                'ativo': novo_portfolio.ativo,
                'usuario_id': str(novo_portfolio.usuario_id),
                'created_at': novo_portfolio.created_at.isoformat() if hasattr(novo_portfolio, 'created_at') else None
            },
            message="Portfolio criado com sucesso",
            #statuscode=201
        )
    except ValueError as e:
        return error_response(str(e), 400)  # CORREÇÃO
    except Exception as e:
        logger.error(f"Erro ao criar portfolio: {e}")
        return error_response(f"Erro ao criar portfolio: {str(e)}", 500)  # CORREÇÃO


# --- 4. PUT /api/portfolios/<id> - ATUALIZAR PORTFOLIO ---
@portfolio_bp.route('/<uuid:portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id):
    """
    Atualiza portfolio existente.
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        data = request.get_json()
        
        # CORREÇÃO: Inverter ordem dos parâmetros (service espera portfolio_id, data, usuario_id)
        portfolio_atualizado = PortfolioService.update(portfolio_id, data, usuario_id)
        
        if not portfolio_atualizado:  # ADICIONAR: Verificar se retornou None
            return error_response("Portfolio não encontrado", 404)
        
        return success_response(  # CORREÇÃO
            data={
                'id': str(portfolio_atualizado.id),
                'nome': portfolio_atualizado.nome,
                'descricao': portfolio_atualizado.descricao,
                'objetivo': portfolio_atualizado.objetivo,
                'ativo': portfolio_atualizado.ativo,
                'updated_at': portfolio_atualizado.updated_at.isoformat() if hasattr(portfolio_atualizado, 'updated_at') else None
            },
            message="Portfolio atualizado com sucesso"
        )
    except ValueError as e:
        return error_response(str(e), 404)  # CORREÇÃO
    except Exception as e:
        logger.error(f"Erro ao atualizar portfolio: {e}")
        return error_response(str(e), 500)  # CORREÇÃO


# --- 5. DELETE /api/portfolios/<id> - DELETAR (SOFT DELETE) PORTFOLIO ---
@portfolio_bp.route('/<uuid:portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id):
    """
    Deleta portfolio (soft delete - marca como inativo).
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        
        # Soft delete via service
        sucesso = PortfolioService.delete(portfolio_id, usuario_id)
        
        if not sucesso:  # ADICIONAR: Verificar se retornou False
            return error_response("Portfolio não encontrado", 404)
        
        return success_response(  # CORREÇÃO
            message="Portfolio deletado com sucesso (soft delete)"
        )
    except ValueError as e:
        return error_response(str(e), 404)  # CORREÇÃO
    except Exception as e:
        logger.error(f"Erro ao deletar portfolio: {e}")
        return error_response(str(e), 500)  # CORREÇÃO
