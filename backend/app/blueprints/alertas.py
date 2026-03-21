# backend/app/blueprints/alertas.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from app.services.alerta_service import AlertaService
from app.models.configuracao_alerta import ConfiguracaoAlerta
from app.database import db

# Prefixo definido. Rotas abaixo serão relativas a /api/alertas
bp = Blueprint('alertas', __name__, url_prefix='/api/alertas')

# CORREÇÃO: strict_slashes=False permite acesso com ou sem barra final (/api/alertas ou /api/alertas/)
@bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_alertas():
    try:
        usuario_id = UUID(get_jwt_identity())
        # Busca alertas e ordena por criação
        alertas = ConfiguracaoAlerta.query.filter_by(usuario_id=usuario_id)\
            .order_by(ConfiguracaoAlerta.timestamp_criacao.desc()).all()
        
        result = [a.to_dict() for a in alertas]
        return jsonify({"success": True, "data": result, "message": f"{len(result)} alerta(s) encontrado(s)"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def criar_alerta():
    try:
        usuario_id = UUID(get_jwt_identity())
        dados = request.json
        
        if not dados.get('nome'):
            return jsonify({"message": "Nome é obrigatório"}), 400

        # CORREÇÃO CRÍTICA: Converter Enum para minúsculo para compatibilidade com DB
        if dados.get('tipo_alerta'):
            dados['tipo_alerta'] = dados['tipo_alerta'].lower()

        if dados.get('frequencia_notificacao'):
            dados['frequencia_notificacao'] = dados['frequencia_notificacao'].lower()

        novo_alerta = AlertaService.criar_alerta(usuario_id, dados)
        return jsonify({"success": True, "message": "Alerta criado com sucesso", "data": novo_alerta}), 201
    except Exception as e:
        print(f"Erro criar alerta: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route('/recentes', methods=['GET'])
@jwt_required()
def listar_alertas_recentes():
    """
    Retorna alertas disparados recentemente.
    
    Query params:
        - limit: Número máximo de alertas (default: 5)
    
    Returns:
        Lista de alertas disparados ordenados por data
    """
    try:
        usuario_id = UUID(get_jwt_identity())
        limit = request.args.get('limit', 5, type=int)
        
        # Buscar alertas ativos disparados recentemente
        alertas = ConfiguracaoAlerta.query.filter_by(
            usuario_id=usuario_id,
            ativo=True
        ).order_by(
            ConfiguracaoAlerta.timestamp_criacao.desc()
        ).limit(limit).all()
        
        result = [{
            'id': str(a.id),
            'nome': a.nome,
            'tipo': a.tipo_alerta,
            'mensagem': a.mensagem or f"Alerta {a.tipo_alerta}",
            'data': a.timestamp_criacao.isoformat() if a.timestamp_criacao else None
        } for a in alertas]
        
        return jsonify({
            "success": True,
            "data": result,
            "message": f"{len(result)} alerta(s) recente(s)"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route('/<alerta_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_alerta(alerta_id):
    try:
        usuario_id = UUID(get_jwt_identity())
        alerta = ConfiguracaoAlerta.query.filter_by(id=alerta_id, usuario_id=usuario_id).first()
        if not alerta: return jsonify({"success": False, "message": "Alerta não encontrado"}), 404
            
        AlertaService.atualizar_alerta(usuario_id, UUID(alerta_id), {'ativo': not alerta.ativo})
        return jsonify({"success": True, "message": "Status atualizado"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route('/<alerta_id>', methods=['DELETE'])
@jwt_required()
def deletar_alerta(alerta_id):
    try:
        usuario_id = UUID(get_jwt_identity())
        AlertaService.deletar_alerta(usuario_id, UUID(alerta_id))
        return jsonify({"success": True, "message": "Alerta removido"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
