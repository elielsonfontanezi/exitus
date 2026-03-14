"""
Blueprint: PlanoCompra
Endpoints para gerenciamento de planos de compra programada
"""
from flask import Blueprint, request, jsonify
from uuid import UUID
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.plano_compra_service import PlanoCompraService
from app.utils.exceptions import NotFoundError, BusinessRuleError, ConflictError
from app.utils.responses import success_response, error_response

bp = Blueprint('plano_compra', __name__, url_prefix='/api/plano-compra')


@bp.route('/', methods=['POST'])
@jwt_required()
def create_plano():
    """Cria um novo plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        data = request.get_json()
        
        plano = PlanoCompraService.create(usuario_id, data)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano de compra criado com sucesso",
            status_code=201
        )
    except (BusinessRuleError, NotFoundError, ConflictError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_planos():
    """Lista planos de compra do usuário"""
    try:
        usuario_id = UUID(get_jwt_identity())
        status = request.args.get('status')
        
        planos = PlanoCompraService.list_by_usuario(usuario_id, status)
        
        return success_response(
            data=[plano.to_dict() for plano in planos],
            message="Planos listados com sucesso"
        )
    except BusinessRuleError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>', methods=['GET'])
@jwt_required()
def get_plano(plano_id):
    """Busca plano de compra por ID"""
    try:
        usuario_id = UUID(get_jwt_identity())
        plano = PlanoCompraService.get_by_id(UUID(plano_id), usuario_id)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano encontrado com sucesso"
        )
    except (NotFoundError, ValueError) as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>', methods=['PUT'])
@jwt_required()
def update_plano(plano_id):
    """Atualiza plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        data = request.get_json()
        
        plano = PlanoCompraService.update(UUID(plano_id), usuario_id, data)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano atualizado com sucesso"
        )
    except (NotFoundError, BusinessRuleError, ConflictError, ValueError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>/aporte', methods=['POST'])
@jwt_required()
def registrar_aporte(plano_id):
    """Registra um aporte no plano"""
    try:
        usuario_id = UUID(get_jwt_identity())
        data = request.get_json()
        
        quantidade = float(data.get('quantidade', 0))
        if quantidade <= 0:
            raise BusinessRuleError("Quantidade deve ser maior que zero")
        
        plano = PlanoCompraService.registrar_aporte(UUID(plano_id), usuario_id, quantidade)
        
        return success_response(
            data=plano.to_dict(),
            message="Aporte registrado com sucesso"
        )
    except (NotFoundError, BusinessRuleError, ConflictError, ValueError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>/pausar', methods=['POST'])
@jwt_required()
def pausar_plano(plano_id):
    """Pausa um plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        plano = PlanoCompraService.pausar(UUID(plano_id), usuario_id)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano pausado com sucesso"
        )
    except (NotFoundError, BusinessRuleError, ValueError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>/reativar', methods=['POST'])
@jwt_required()
def reativar_plano(plano_id):
    """Reativa um plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        plano = PlanoCompraService.reativar(UUID(plano_id), usuario_id)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano reativado com sucesso"
        )
    except (NotFoundError, BusinessRuleError, ValueError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>/cancelar', methods=['POST'])
@jwt_required()
def cancelar_plano(plano_id):
    """Cancela um plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        plano = PlanoCompraService.cancelar(UUID(plano_id), usuario_id)
        
        return success_response(
            data=plano.to_dict(),
            message="Plano cancelado com sucesso"
        )
    except (NotFoundError, BusinessRuleError, ValueError) as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/<plano_id>', methods=['DELETE'])
@jwt_required()
def delete_plano(plano_id):
    """Remove um plano de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        PlanoCompraService.delete(UUID(plano_id), usuario_id)
        
        return success_response(
            message="Plano removido com sucesso"
        )
    except (NotFoundError, ValueError) as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response("Erro interno no servidor", 500)


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_planos():
    """Dashboard com resumo dos planos de compra"""
    try:
        usuario_id = UUID(get_jwt_identity())
        
        # Buscar todos os planos
        planos = PlanoCompraService.list_by_usuario(usuario_id)
        
        # Calcular estatísticas
        total_planos = len(planos)
        planos_ativos = len([p for p in planos if p.status.value == 'ativo'])
        planos_pausados = len([p for p in planos if p.status.value == 'pausado'])
        planos_concluidos = len([p for p in planos if p.status.value == 'concluido'])
        
        # Calcular valores
        total_aporte_mensal = sum(float(p.valor_aporte_mensal) for p in planos if p.status.value == 'ativo')
        total_investido = sum(float(p.quantidade_acumulada * p.ativo.preco_atual or 0) for p in planos if p.ativo.preco_atual)
        
        # Próximos aportes
        proximos_aportes = []
        for plano in planos:
            if plano.proximo_aporte and plano.status.value == 'ativo':
                proximos_aportes.append({
                    'plano_id': str(plano.id),
                    'nome': plano.nome,
                    'ativo_ticker': plano.ativo.ticker if plano.ativo else None,
                    'data': plano.proximo_aporte.isoformat(),
                    'valor': float(plano.valor_aporte_mensal)
                })
        
        proximos_aportes.sort(key=lambda x: x['data'])
        proximos_aportes = proximos_aportes[:5]  # Próximos 5
        
        dashboard_data = {
            'resumo': {
                'total_planos': total_planos,
                'planos_ativos': planos_ativos,
                'planos_pausados': planos_pausados,
                'planos_concluidos': planos_concluidos,
                'total_aporte_mensal': total_aporte_mensal,
                'total_investido': total_investido
            },
            'proximos_aportes': proximos_aportes,
            'planos': [plano.to_dict() for plano in planos]
        }
        
        return success_response(
            data=dashboard_data,
            message="Dashboard de planos carregado com sucesso"
        )
    except Exception as e:
        return error_response("Erro interno no servidor", 500)
