# -*- coding: utf-8 -*-
"""
M7.3 - Relatórios Blueprint
Endpoints:
- GET  /api/relatorios/lista
- GET  /api/relatorios/<id>
- POST /api/relatorios/gerar
- POST /api/relatorios/<id>/exportar  (stub, M7.9)
- DELETE /api/relatorios/<id>
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from uuid import UUID

from app.services.relatorio_service import RelatorioService

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/api/relatorios")


def _parse_date(param: str):
    """Converte string YYYY-MM-DD em date ou None."""
    if not param:
        return None
    try:
        return datetime.strptime(param, "%Y-%m-%d").date()
    except ValueError:
        return None


@relatorios_bp.route("/lista", methods=["GET"])
@jwt_required()
def listar_relatorios():
    """Lista relatórios do usuário paginados."""
    usuario_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
        dados = RelatorioService.listar_relatorios(usuario_id=UUID(usuario_id), page=page, per_page=per_page)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@relatorios_bp.route("/<string:relatorio_id>", methods=["GET"])
@jwt_required()
def obter_relatorio(relatorio_id):
    """Obtém um relatório específico."""
    usuario_id = get_jwt_identity()
    try:
        dados = RelatorioService.obter_relatorio(
            usuario_id=UUID(usuario_id),
            relatorio_id=UUID(relatorio_id),
        )
        return jsonify(dados), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@relatorios_bp.route("/gerar", methods=["POST"])
@jwt_required()
def gerar_relatorio():
    """
    Gera relatório de PORTFOLIO ou PERFORMANCE.

    Body JSON:
    {
      "tipo": "PORTFOLIO" | "PERFORMANCE",
      "filtros": { ... },
      "data_inicio": "YYYY-MM-DD",
      "data_fim": "YYYY-MM-DD"
    }
    """
    usuario_id = get_jwt_identity()
    payload = request.get_json() or {}
    tipo = (payload.get("tipo") or "PORTFOLIO").upper()
    filtros = payload.get("filtros") or {}

    try:
        if tipo == "PORTFOLIO":
            resultado = RelatorioService.gerar_relatorio_portfolio(
                usuario_id=UUID(usuario_id),
                filtros=filtros,
            )
        elif tipo == "PERFORMANCE":
            data_inicio = _parse_date(payload.get("data_inicio"))
            data_fim = _parse_date(payload.get("data_fim"))
            if not data_inicio or not data_fim:
                return jsonify({"error": "data_inicio e data_fim são obrigatórias para PERFORMANCE"}), 400

            resultado = RelatorioService.gerar_relatorio_performance(
                usuario_id=UUID(usuario_id),
                data_inicio=data_inicio,
                data_fim=data_fim,
                filtros=filtros,
            )
        else:
            return jsonify({"error": "tipo inválido. Use PORTFOLIO ou PERFORMANCE"}), 400

        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@relatorios_bp.route("/<string:relatorio_id>/exportar", methods=["POST"])
@jwt_required()
def exportar_relatorio(relatorio_id):
    """
    Stub para exportação (PDF/Excel) que será implementada em M7.9.
    Por enquanto, apenas retorna o JSON do relatório.
    """
    usuario_id = get_jwt_identity()
    try:
        dados = RelatorioService.obter_relatorio(
            usuario_id=UUID(usuario_id),
            relatorio_id=UUID(relatorio_id),
        )
        return jsonify(
            {
                "status": "ok",
                "message": "Exportação ainda não implementada. Retornando JSON.",
                "relatorio": dados,
            }
        ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@relatorios_bp.route("/<string:relatorio_id>", methods=["DELETE"])
@jwt_required()
def deletar_relatorio(relatorio_id):
    """Remove um relatório da auditoria (não apaga dados base)."""
    usuario_id = get_jwt_identity()
    try:
        ok = RelatorioService.deletar_relatorio(
            usuario_id=UUID(usuario_id),
            relatorio_id=UUID(relatorio_id),
        )
        if ok:
            return jsonify({"status": "ok", "message": "Relatório deletado"}), 200
        return jsonify({"error": "Falha ao deletar relatório"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
