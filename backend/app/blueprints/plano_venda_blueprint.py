# -*- coding: utf-8 -*-
"""
Exitus - Plano Venda Blueprint
API REST para planos de venda programada
"""

import logging
from uuid import UUID

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.plano_venda_service import PlanoVendaService
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_uuid
from app.models.plano_venda import StatusPlanoVenda, TipoGatilho

logger = logging.getLogger(__name__)

# Criar blueprint
plano_venda_bp = Blueprint('plano_venda', __name__, url_prefix='/api/plano-venda')


@plano_venda_bp.route('', methods=['GET'])
@jwt_required()
def list_planos():
    """Lista planos de venda do usuário"""
    try:
        usuario_id = get_jwt_identity()
        
        # Parâmetros de paginação e filtros
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # Validar status se fornecido
        if status:
            try:
                StatusPlanoVenda(status)
            except ValueError:
                return error_response(
                    f"Status inválido. Use: {[s.value for s in StatusPlanoVenda]}", 
                    400
                )
        
        result = PlanoVendaService.get_all(usuario_id, page, per_page, status)
        
        # Serializar planos
        planos_data = []
        for plano in result['planos']:
            planos_data.append({
                'id': str(plano.id),
                'nome': plano.nome,
                'descricao': plano.descricao,
                'ativo_id': str(plano.ativo_id),
                'ativo_ticker': plano.ativo.ticker if plano.ativo else None,
                'quantidade_total': float(plano.quantidade_total),
                'quantidade_vendida': float(plano.quantidade_vendida),
                'quantidade_restante': float(plano.quantidade_restante),
                'progresso_percentual': plano.progresso_percentual,
                'preco_minimo': float(plano.preco_minimo) if plano.preco_minimo else None,
                'preco_alvo': float(plano.preco_alvo) if plano.preco_alvo else None,
                'tipo_gatilho': plano.tipo_gatilho.value,
                'gatilho_valor': float(plano.gatilho_valor) if plano.gatilho_valor else None,
                'data_limite': plano.data_limite.isoformat() if plano.data_limite else None,
                'parcelas_total': plano.parcelas_total,
                'parcelas_executadas': plano.parcelas_executadas,
                'parcelas_restantes': plano.parcelas_restantes,
                'valor_parcela_fixo': float(plano.valor_parcela_fixo) if plano.valor_parcela_fixo else None,
                'status': plano.status.value,
                'data_inicio': plano.data_inicio.isoformat() if plano.data_inicio else None,
                'data_conclusao': plano.data_conclusao.isoformat() if plano.data_conclusao else None,
                'created_at': plano.created_at.isoformat(),
                'updated_at': plano.updated_at.isoformat()
            })
        
        return success_response(
            data={
                'planos': planos_data,
                'pagination': {
                    'total': result['total'],
                    'pages': result['pages'],
                    'current_page': result['current_page'],
                    'per_page': result['per_page'],
                    'has_next': result['has_next'],
                    'has_prev': result['has_prev']
                }
            },
            message="Planos de venda listados com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar planos de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('', methods=['POST'])
@jwt_required()
def create_plano():
    """Cria um novo plano de venda"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response("Dados não fornecidos", 400)
        
        # Validações básicas
        required_fields = ['nome', 'ativo_id', 'quantidade_total', 'tipo_gatilho']
        for field in required_fields:
            if field not in data or not data[field]:
                return error_response(f"Campo '{field}' é obrigatório", 400)
        
        # Validar UUID
        if not validate_uuid(data['ativo_id']):
            return error_response("ativo_id inválido", 400)
        
        # Validar tipo de gatilho
        try:
            TipoGatilho(data['tipo_gatilho'])
        except ValueError:
            return error_response(
                f"tipo_gatilho inválido. Use: {[g.value for g in TipoGatilho]}", 
                400
            )
        
        # Validações específicas por tipo de gatilho
        tipo_gatilho = TipoGatilho(data['tipo_gatilho'])
        
        if tipo_gatilho == TipoGatilho.PRECO_ALVO and not data.get('preco_alvo'):
            return error_response("preco_alvo é obrigatório para gatilho por preço", 400)
        
        if tipo_gatilho == TipoGatilho.PERCENTUAL_LUCRO and not data.get('gatilho_valor'):
            return error_response("gatilho_valor é obrigatório para gatilho por percentual", 400)
        
        if tipo_gatilho == TipoGatilho.DATA_LIMITE and not data.get('data_limite'):
            return error_response("data_limite é obrigatória para gatilho por data", 400)
        
        if tipo_gatilho in [TipoGatilho.PARCELAS_SEMANAIS, TipoGatilho.PARCELAS_MENSAIS]:
            if not data.get('parcelas_total'):
                return error_response("parcelas_total é obrigatório para gatilho por parcelas", 400)
        
        plano = PlanoVendaService.create(data, usuario_id)
        
        return success_response(
            data={
                'id': str(plano.id),
                'nome': plano.nome,
                'status': plano.status.value,
                'created_at': plano.created_at.isoformat()
            },
            message="Plano de venda criado com sucesso",
            status_code=201
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao criar plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/<plano_id>', methods=['GET'])
@jwt_required()
def get_plano(plano_id):
    """Obtém detalhes de um plano específico"""
    try:
        usuario_id = get_jwt_identity()
        
        if not validate_uuid(plano_id):
            return error_response("ID inválido", 400)
        
        plano = PlanoVendaService.get_by_id(UUID(plano_id), usuario_id)
        
        if not plano:
            return error_response("Plano de venda não encontrado", 404)
        
        return success_response(
            data={
                'id': str(plano.id),
                'nome': plano.nome,
                'descricao': plano.descricao,
                'ativo_id': str(plano.ativo_id),
                'ativo_ticker': plano.ativo.ticker if plano.ativo else None,
                'ativo_nome': plano.ativo.nome if plano.ativo else None,
                'quantidade_total': float(plano.quantidade_total),
                'quantidade_vendida': float(plano.quantidade_vendida),
                'quantidade_restante': float(plano.quantidade_restante),
                'progresso_percentual': plano.progresso_percentual,
                'preco_minimo': float(plano.preco_minimo) if plano.preco_minimo else None,
                'preco_alvo': float(plano.preco_alvo) if plano.preco_alvo else None,
                'tipo_gatilho': plano.tipo_gatilho.value,
                'gatilho_valor': float(plano.gatilho_valor) if plano.gatilho_valor else None,
                'data_limite': plano.data_limite.isoformat() if plano.data_limite else None,
                'parcelas_total': plano.parcelas_total,
                'parcelas_executadas': plano.parcelas_executadas,
                'parcelas_restantes': plano.parcelas_restantes,
                'valor_parcela_fixo': float(plano.valor_parcela_fixo) if plano.valor_parcela_fixo else None,
                'status': plano.status.value,
                'data_inicio': plano.data_inicio.isoformat() if plano.data_inicio else None,
                'data_conclusao': plano.data_conclusao.isoformat() if plano.data_conclusao else None,
                'created_at': plano.created_at.isoformat(),
                'updated_at': plano.updated_at.isoformat(),
                'pode_executar_venda': plano.pode_executar_venda(),
                'quantidade_parcela': float(plano.calcular_quantidade_parcela()) if plano.calcular_quantidade_parcela() else None
            },
            message="Plano de venda encontrado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/<plano_id>', methods=['PUT'])
@jwt_required()
def update_plano(plano_id):
    """Atualiza um plano de venda existente"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response("Dados não fornecidos", 400)
        
        if not validate_uuid(plano_id):
            return error_response("ID inválido", 400)
        
        # Validar tipo_gatilho se fornecido
        if 'tipo_gatilho' in data:
            try:
                TipoGatilho(data['tipo_gatilho'])
            except ValueError:
                return error_response(
                    f"tipo_gatilho inválido. Use: {[g.value for g in TipoGatilho]}", 
                    400
                )
        
        plano = PlanoVendaService.update(UUID(plano_id), data, usuario_id)
        
        if not plano:
            return error_response("Plano de venda não encontrado", 404)
        
        return success_response(
            data={
                'id': str(plano.id),
                'nome': plano.nome,
                'updated_at': plano.updated_at.isoformat()
            },
            message="Plano de venda atualizado com sucesso"
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Erro ao atualizar plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/<plano_id>', methods=['DELETE'])
@jwt_required()
def delete_plano(plano_id):
    """Cancela/remove um plano de venda"""
    try:
        usuario_id = get_jwt_identity()
        
        if not validate_uuid(plano_id):
            return error_response("ID inválido", 400)
        
        success = PlanoVendaService.delete(UUID(plano_id), usuario_id)
        
        if not success:
            return error_response("Plano de venda não encontrado", 404)
        
        return success_response(
            message="Plano de venda cancelado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao cancelar plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/<plano_id>/pausar', methods=['POST'])
@jwt_required()
def pausar_plano(plano_id):
    """Pausa um plano de venda ativo"""
    try:
        usuario_id = get_jwt_identity()
        
        if not validate_uuid(plano_id):
            return error_response("ID inválido", 400)
        
        success = PlanoVendaService.pausar(UUID(plano_id), usuario_id)
        
        if not success:
            return error_response("Plano não encontrado ou não pode ser pausado", 404)
        
        return success_response(
            message="Plano de venda pausado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao pausar plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/<plano_id>/reativar', methods=['POST'])
@jwt_required()
def reativar_plano(plano_id):
    """Reativa um plano de venda pausado"""
    try:
        usuario_id = get_jwt_identity()
        
        if not validate_uuid(plano_id):
            return error_response("ID inválido", 400)
        
        success = PlanoVendaService.reativar(UUID(plano_id), usuario_id)
        
        if not success:
            return error_response("Plano não encontrado ou não pode ser reativado", 404)
        
        return success_response(
            message="Plano de venda reativado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao reativar plano de venda: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Retorna dashboard de planos de venda"""
    try:
        usuario_id = get_jwt_identity()
        dashboard_data = PlanoVendaService.get_dashboard(usuario_id)
        
        return success_response(
            data=dashboard_data,
            message="Dashboard gerado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/verificar-gatilhos', methods=['GET'])
@jwt_required()
def verificar_gatilhos():
    """Verifica quais planos devem disparar vendas"""
    try:
        usuario_id = get_jwt_identity()
        disparos = PlanoVendaService.verificar_gatilhos(usuario_id)
        
        return success_response(
            data={
                'disparos': disparos,
                'total': len(disparos)
            },
            message="Gatilhos verificados com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao verificar gatilhos: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def get_estatisticas():
    """Retorna estatísticas detalhadas"""
    try:
        usuario_id = get_jwt_identity()
        stats = PlanoVendaService.get_estatisticas(usuario_id)
        
        return success_response(
            data=stats,
            message="Estatísticas obtidas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return error_response(str(e), 500)


@plano_venda_bp.route('/tipos-gatilho', methods=['GET'])
@jwt_required()
def get_tipos_gatilho():
    """Retorna os tipos de gatilho disponíveis"""
    tipos = [
        {
            'value': g.value,
            'label': g.value.replace('_', ' ').title(),
            'description': {
                'preco_alvo': 'Dispara quando o preço atinge um valor específico',
                'percentual_lucro': 'Dispara quando o lucro atinge um percentual',
                'parcelas_semanais': 'Vende em parcelas semanais',
                'parcelas_mensais': 'Vende em parcelas mensais',
                'data_limite': 'Dispara em uma data específica',
                'gatilho_misto': 'Combinação de múltiplos gatilhos'
            }.get(g.value, '')
        }
        for g in TipoGatilho
    ]
    
    return success_response(
        data={'tipos_gatilho': tipos},
        message="Tipos de gatilho listados com sucesso"
    )
