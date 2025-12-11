# -*- coding: utf-8 -*-
"""
M7.3 - Alertas Blueprint (7 endpoints)
Endpoints:
- GET    /api/alertas/lista
- GET    /api/alertas/<id> 
- POST   /api/alertas/criar
- PUT    /api/alertas/<id>
- DELETE /api/alertas/<id>
- POST   /api/alertas/<id>/test
- GET    /api/alertas/historico
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from typing import Optional

from app.services.alerta_service import AlertaService

alertas_bp = Blueprint("alertas", __name__, url_prefix="/api/alertas")


@alertas_bp.route("/lista", methods=["GET"])
@jwt_required()
def listar_alertas():
    """Lista alertas do usuário."""
    usuario_id = get_jwt_identity()
    ativo_id = request.args.get("ativo_id")
    apenas_ativos = request.args.get("apenas_ativos", "true").lower() == "true"
    
    try:
        dados = AlertaService.listar_alertas(
            usuario_id=UUID(usuario_id),
            ativo_id=UUID(ativo_id) if ativo_id else None,
            apenas_ativos=apenas_ativos
        )
        return jsonify({"alertas": dados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/<string:alerta_id>", methods=["GET"])
@jwt_required()
def obter_alerta(alerta_id):
    """Obtém alerta específico."""
    usuario_id = get_jwt_identity()
    try:
        dados = AlertaService.obter_alerta(
            usuario_id=UUID(usuario_id),
            alerta_id=UUID(alerta_id)
        )
        return jsonify(dados), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/criar", methods=["POST"])
@jwt_required()
def criar_alerta():
    """
    Cria novo alerta.
    
    Body JSON:
    {
      "nome": "Alerta PETR4 30%",
      "tipo_alerta": "ALTA_PRECO",
      "condicao_valor": 30.0,
      "condicao_operador": "MAIOR",
      "ativo_id": "uuid-do-ativo",
      "frequencia_notificacao": "IMEDIATA"
    }
    """
    usuario_id = get_jwt_identity()
    dados = request.get_json()
    
    try:
        resultado = AlertaService.criar_alerta(
            usuario_id=UUID(usuario_id),
            dados=dados
        )
        return jsonify(resultado), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/<string:alerta_id>", methods=["PUT"])
@jwt_required()
def atualizar_alerta(alerta_id):
    """Atualiza alerta existente."""
    usuario_id = get_jwt_identity()
    dados = request.get_json()
    
    try:
        resultado = AlertaService.atualizar_alerta(
            usuario_id=UUID(usuario_id),
            alerta_id=UUID(alerta_id),
            dados=dados
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/<string:alerta_id>", methods=["DELETE"])
@jwt_required()
def deletar_alerta(alerta_id):
    """Deleta alerta."""
    usuario_id = get_jwt_identity()
    try:
        AlertaService.deletar_alerta(
            usuario_id=UUID(usuario_id),
            alerta_id=UUID(alerta_id)
        )
        return jsonify({"status": "ok", "message": "Alerta deletado"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/<string:alerta_id>/test", methods=["POST"])
@jwt_required()
def testar_alerta(alerta_id):
    """Testa se alerta seria disparado (sem notificação)."""
    usuario_id = get_jwt_identity()
    try:
        resultado = AlertaService.testar_alerta(
            usuario_id=UUID(usuario_id),
            alerta_id=UUID(alerta_id)
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alertas_bp.route("/historico", methods=["GET"])
@jwt_required()
def historico_alertas():
    """Histórico de alertas acionados."""
    usuario_id = get_jwt_identity()
    limite = request.args.get("limite", 20, type=int)
    
    try:
        dados = AlertaService.obter_historico_acionamentos(
            usuario_id=UUID(usuario_id),
            limite=limite
        )
        return jsonify({"historico": dados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
