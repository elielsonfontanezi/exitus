# -*- coding: utf-8 -*-
"""
Exitus - Posicao Blueprint
Rotas para gerenciamento de posições
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.posicao_service import PosicaoService
from app.schemas.posicao_schema import (
    PosicaoResponseSchema, 
    PosicaoResumoSchema,
    PosicaoConsolidadaSchema
)
from app.utils.responses import success_response, error_response
from app.decorators import admin_required
import logging

logger = logging.getLogger(__name__)

posicao_bp = Blueprint('posicao', __name__, url_prefix='/api/posicoes')

# Schemas
posicao_schema = PosicaoResponseSchema()
posicoes_schema = PosicaoResponseSchema(many=True)
resumo_schema = PosicaoResumoSchema()
consolidada_schema = PosicaoConsolidadaSchema()


@posicao_bp.route('', methods=['GET'])
@jwt_required()
def listar_posicoes():
    """
    Lista posições do usuário com filtros e paginação
    
    Query Params:
        - page (int): Página atual (default: 1)
        - per_page (int): Registros por página (default: 50, max: 100)
        - ativo_id (UUID): Filtrar por ativo
        - corretora_id (UUID): Filtrar por corretora
        - ticker (str): Buscar por ticker
        - lucro_positivo (bool): Filtrar por lucro > 0
        - quantidade_min (float): Quantidade mínima
    """
    try:
        usuario_id = get_jwt_identity()
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Filtros
        filters = {}
        if request.args.get('ativo_id'):
            filters['ativo_id'] = request.args.get('ativo_id')
        if request.args.get('corretora_id'):
            filters['corretora_id'] = request.args.get('corretora_id')
        if request.args.get('ticker'):
            filters['ticker'] = request.args.get('ticker')
        if request.args.get('lucro_positivo') is not None:
            filters['lucro_positivo'] = request.args.get('lucro_positivo', type=bool)
        if request.args.get('quantidade_min'):
            filters['quantidade_min'] = request.args.get('quantidade_min', type=float)
        
        # Buscar posições
        paginacao = PosicaoService.get_all(usuario_id, page, per_page, filters)
        
        return success_response(
            data={
                'posicoes': posicoes_schema.dump(paginacao.items),
                'total': paginacao.total,
                'page': paginacao.page,
                'per_page': paginacao.per_page,
                'pages': paginacao.pages
            },
            message=f"{paginacao.total} posições encontradas"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar posições: {e}")
        return error_response(str(e), 500)


@posicao_bp.route('/<uuid:posicao_id>', methods=['GET'])
@jwt_required()
def buscar_posicao(posicao_id):
    """Busca posição por ID"""
    try:
        usuario_id = get_jwt_identity()
        posicao = PosicaoService.get_by_id(posicao_id, usuario_id)
        
        if not posicao:
            return error_response("Posição não encontrada", 404)
        
        return success_response(
            data=posicao_schema.dump(posicao),
            message="Posição encontrada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar posição: {e}")
        return error_response(str(e), 500)


@posicao_bp.route('/calcular', methods=['POST'])
@jwt_required()
def calcular_posicoes():
    """
    Recalcula todas as posições do usuário a partir das transações
    """
    try:
        usuario_id = get_jwt_identity()
        resultado = PosicaoService.calcular_posicoes(usuario_id)
        
        return success_response(
            data=resultado,
            message="Posições recalculadas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao calcular posições: {e}")
        return error_response(str(e), 500)


@posicao_bp.route('/resumo', methods=['GET'])
@jwt_required()
def resumo_posicoes():
    """Retorna resumo consolidado das posições"""
    try:
        usuario_id = get_jwt_identity()
        resumo = PosicaoService.get_resumo(usuario_id)
        
        return success_response(
            data=resumo_schema.dump(resumo),
            message="Resumo gerado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return error_response(str(e), 500)


@posicao_bp.route('/por-ativo/<uuid:ativo_id>', methods=['GET'])
@jwt_required()
def posicao_por_ativo(ativo_id):
    """Consolida posições de um ativo em todas as corretoras"""
    try:
        usuario_id = get_jwt_identity()
        consolidada = PosicaoService.get_por_ativo(usuario_id, ativo_id)
        
        if not consolidada:
            return error_response("Nenhuma posição encontrada para este ativo", 404)
        
        return success_response(
            data=consolidada_schema.dump(consolidada),
            message="Posição consolidada"
        )
        
    except Exception as e:
        logger.error(f"Erro ao consolidar posição: {e}")
        return error_response(str(e), 500)


@posicao_bp.route('/atualizar-valores', methods=['POST'])
@jwt_required()
def atualizar_valores():
    """Atualiza valores de mercado de todas as posições"""
    try:
        usuario_id = get_jwt_identity()
        quantidade = PosicaoService.atualizar_valores_atuais(usuario_id)
        
        return success_response(
            data={'posicoes_atualizadas': quantidade},
            message=f"{quantidade} posições atualizadas"
        )
        
    except Exception as e:
        logger.error(f"Erro ao atualizar valores: {e}")
        return error_response(str(e), 500)
