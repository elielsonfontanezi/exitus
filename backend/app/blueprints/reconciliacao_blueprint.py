# -*- coding: utf-8 -*-
"""
Exitus - Reconciliacao Blueprint
Endpoints para verificação de consistência de dados
GAP: EXITUS-RECONCILIACAO-001
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.reconciliacao_service import ReconciliacaoService
import logging

logger = logging.getLogger(__name__)

reconciliacaobp = Blueprint('reconciliacao', __name__, url_prefix='/api/reconciliacao')


@reconciliacaobp.route('/verificar', methods=['GET'])
@jwt_required()
def verificar_reconciliacao():
    """
    Executa verificação completa de reconciliação.
    
    Returns:
        200: {
            'status': 'OK' | 'WARNING' | 'ERROR',
            'divergencias': [...],
            'resumo': {...}
        }
    """
    try:
        usuario_id = get_jwt_identity()
        
        resultado = ReconciliacaoService.verificar_tudo(usuario_id)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de reconciliação: {e}")
        return jsonify({
            'error': 'Erro ao executar verificação de reconciliação',
            'details': str(e)
        }), 500


@reconciliacaobp.route('/posicoes', methods=['GET'])
@jwt_required()
def verificar_posicoes():
    """
    Verifica apenas reconciliação de posições.
    
    Returns:
        200: Lista de divergências encontradas
    """
    try:
        usuario_id = get_jwt_identity()
        
        divergencias = ReconciliacaoService.verificar_posicoes(usuario_id)
        
        return jsonify({
            'divergencias': divergencias,
            'total': len(divergencias)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de posições: {e}")
        return jsonify({
            'error': 'Erro ao verificar posições',
            'details': str(e)
        }), 500


@reconciliacaobp.route('/saldos', methods=['GET'])
@jwt_required()
def verificar_saldos():
    """
    Verifica apenas saldos de corretoras.
    
    Returns:
        200: Lista de divergências encontradas
    """
    try:
        usuario_id = get_jwt_identity()
        
        divergencias = ReconciliacaoService.verificar_saldos_corretoras(usuario_id)
        
        return jsonify({
            'divergencias': divergencias,
            'total': len(divergencias)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de saldos: {e}")
        return jsonify({
            'error': 'Erro ao verificar saldos',
            'details': str(e)
        }), 500


@reconciliacaobp.route('/integridade', methods=['GET'])
@jwt_required()
def verificar_integridade():
    """
    Verifica integridade geral de transações.
    
    Returns:
        200: Lista de divergências encontradas
    """
    try:
        usuario_id = get_jwt_identity()
        
        divergencias = ReconciliacaoService.verificar_integridade_transacoes(usuario_id)
        
        return jsonify({
            'divergencias': divergencias,
            'total': len(divergencias)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de integridade: {e}")
        return jsonify({
            'error': 'Erro ao verificar integridade',
            'details': str(e)
        }), 500


@reconciliacaobp.route('/ativo/<ativo_id>', methods=['GET'])
@jwt_required()
def verificar_ativo(ativo_id):
    """
    Verifica reconciliação de um ativo específico.
    
    Query params:
        corretora_id (optional): Filtrar por corretora
    
    Returns:
        200: Detalhes da reconciliação do ativo
    """
    try:
        usuario_id = get_jwt_identity()
        corretora_id = request.args.get('corretora_id')
        
        resultado = ReconciliacaoService.verificar_ativo_especifico(
            usuario_id,
            ativo_id,
            corretora_id
        )
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de ativo: {e}")
        return jsonify({
            'error': 'Erro ao verificar ativo',
            'details': str(e)
        }), 500
