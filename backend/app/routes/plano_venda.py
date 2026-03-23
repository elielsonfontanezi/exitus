# -*- coding: utf-8 -*-
"""
Exitus API - Planos de Venda Disciplinada
Endpoints para gestão de planos de venda com stop gain/loss e trailing stop
"""

from datetime import datetime, date
from decimal import Decimal

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.models.usuario import Usuario
from app.models.ativo import Ativo
from app.models.posicao import Posicao
from app.utils.exceptions import BusinessRuleError
from app.services.ir_service import calcular_ir_venda

bp = Blueprint('plano_venda', __name__, url_prefix='/api/plano-venda')


@bp.route('', methods=['GET'])
@jwt_required()
def listar_planos():
    """Lista planos de venda do usuário autenticado"""
    usuario_id = get_jwt_identity()
    
    # TODO: Implementar modelo PlanoVenda quando criado
    # Por enquanto, retorna dados mock baseados em posições
    
    # Obter posições do usuário
    posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
    
    planos = []
    for pos in posicoes:
        # Mock: cada posição pode ter um plano de venda
        plano = {
            'id': f"plano_{pos.id}",
            'posicao_id': pos.id,
            'ativo': {
                'ticker': pos.ativo.ticker,
                'nome': pos.ativo.nome
            },
            'quantidade': pos.quantidade,
            'preco_medio': float(pos.preco_medio),
            'stop_gain': float(pos.preco_medio * Decimal('1.2')),  # Mock: +20%
            'stop_loss': float(pos.preco_medio * Decimal('0.9')),   # Mock: -10%
            'trailing_stop': False,
            'status': 'ATIVO',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        planos.append(plano)
    
    return jsonify({
        'success': True,
        'data': planos,
        'total': len(planos)
    })


@bp.route('', methods=['POST'])
@jwt_required()
def criar_plano():
    """Cria novo plano de venda disciplinada"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    
    # Validações básicas
    campos_obrigatorios = ['posicao_id', 'stop_gain', 'stop_loss']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'Campo obrigatório: {campo}'
            }), 400
    
    # Verificar se posição existe e pertence ao usuário
    posicao = Posicao.query.filter_by(
        id=data['posicao_id'], 
        usuario_id=usuario_id
    ).first()
    
    if not posicao:
        return jsonify({
            'success': False,
            'error': 'Posição não encontrada'
        }), 404
    
    # Validações de negócio
    stop_gain = Decimal(str(data['stop_gain']))
    stop_loss = Decimal(str(data['stop_loss']))
    preco_medio = posicao.preco_medio
    
    if stop_gain <= preco_medio:
        return jsonify({
            'success': False,
            'error': 'Stop gain deve ser maior que preço médio'
        }), 400
    
    if stop_loss >= preco_medio:
        return jsonify({
            'success': False,
            'error': 'Stop loss deve ser menor que preço médio'
        }), 400
    
    # TODO: Implementar modelo PlanoVenda
    # Por enquanto, retorna mock
    
    plano_mock = {
        'id': f"plano_new_{datetime.now().timestamp()}",
        'posicao_id': posicao.id,
        'ativo': {
            'ticker': posicao.ativo.ticker,
            'nome': posicao.ativo.nome
        },
        'quantidade': posicao.quantidade,
        'preco_medio': float(preco_medio),
        'stop_gain': float(stop_gain),
        'stop_loss': float(stop_loss),
        'trailing_stop': data.get('trailing_stop', False),
        'status': 'ATIVO',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': plano_mock,
        'message': 'Plano de venda criado com sucesso'
    }), 201


@bp.route('/<plano_id>', methods=['PUT'])
@jwt_required()
def atualizar_plano(plano_id):
    """Atualiza plano de venda existente"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    
    # TODO: Implementar modelo PlanoVenda
    # Por enquanto, retorna mock atualizado
    
    plano_mock = {
        'id': plano_id,
        'posicao_id': data.get('posicao_id', 'mock_pos_id'),
        'ativo': {
            'ticker': 'PETR4',
            'nome': 'Petrobras PN'
        },
        'quantidade': 100,
        'preco_medio': 35.00,
        'stop_gain': float(data.get('stop_gain', 42.00)),
        'stop_loss': float(data.get('stop_loss', 31.50)),
        'trailing_stop': data.get('trailing_stop', False),
        'status': data.get('status', 'ATIVO'),
        'updated_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': plano_mock,
        'message': 'Plano de venda atualizado com sucesso'
    })


@bp.route('/<plano_id>', methods=['DELETE'])
@jwt_required()
def excluir_plano(plano_id):
    """Exclui plano de venda"""
    # TODO: Implementar modelo PlanoVenda
    # Por enquanto, apenas retorna sucesso
    
    return jsonify({
        'success': True,
        'message': 'Plano de venda excluído com sucesso'
    })


@bp.route('/simular-venda', methods=['POST'])
@jwt_required()
def simular_venda():
    """Simula IR e resultados de uma venda"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    
    # Validações
    campos_obrigatorios = ['posicao_id', 'quantidade', 'preco_venda']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'Campo obrigatório: {campo}'
            }), 400
    
    # Verificar posição
    posicao = Posicao.query.filter_by(
        id=data['posicao_id'],
        usuario_id=usuario_id
    ).first()
    
    if not posicao:
        return jsonify({
            'success': False,
            'error': 'Posição não encontrada'
        }), 404
    
    quantidade = int(data['quantidade'])
    preco_venda = Decimal(str(data['preco_venda']))
    
    if quantidade > posicao.quantidade:
        return jsonify({
            'success': False,
            'error': 'Quantidade maior que posição disponível'
        }), 400
    
    # Calcular resultados
    preco_medio = posicao.preco_medio
    custo_total = preco_medio * quantidade
    valor_venda = preco_venda * quantidade
    lucro_bruto = valor_venda - custo_total
    
    # Calcular IR (usando service existente)
    # TODO: Adaptar ir_service para venda individual
    # Por enquanto, cálculo simplificado
    
    ir_aliquota = Decimal('0.15')  # 15% para swing trade
    ir_devido = lucro_bruto * ir_aliquota if lucro_bruto > 0 else Decimal('0')
    lucro_liquido = lucro_bruto - ir_devido
    
    simulacao = {
        'posicao': {
            'ticker': posicao.ativo.ticker,
            'nome': posicao.ativo.nome
        },
        'quantidade': quantidade,
        'preco_medio': float(preco_medio),
        'preco_venda': float(preco_venda),
        'custo_total': float(custo_total),
        'valor_venda': float(valor_venda),
        'lucro_bruto': float(lucro_bruto),
        'ir_aliquota': float(ir_aliquota),
        'ir_devido': float(ir_devido),
        'lucro_liquido': float(lucro_liquido),
        'rentabilidade_percentual': float((lucro_bruto / custo_total) * 100) if custo_total > 0 else 0,
        'simulado_em': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': simulacao
    })


@bp.route('/posicoes-disponiveis', methods=['GET'])
@jwt_required()
def listar_posicoes_disponiveis():
    """Lista posições que podem ter plano de venda"""
    usuario_id = get_jwt_identity()
    
    posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
    
    disponiveis = []
    for pos in posicoes:
        if pos.quantidade > 0:  # Apenas posições com quantidade
            disponivel = {
                'id': pos.id,
                'ativo': {
                    'ticker': pos.ativo.ticker,
                    'nome': pos.ativo.nome,
                    'tipo': pos.ativo.tipo.value
                },
                'quantidade': pos.quantidade,
                'preco_medio': float(pos.preco_medio),
                'custo_total': float(pos.preco_medio * pos.quantidade),
                'valor_atual': None,  # TODO: Obter cotação atual
                'lucro_prejuizio': None  # TODO: Calcular com cotação
            }
            disponiveis.append(disponivel)
    
    return jsonify({
        'success': True,
        'data': disponiveis,
        'total': len(disponiveis)
    })
