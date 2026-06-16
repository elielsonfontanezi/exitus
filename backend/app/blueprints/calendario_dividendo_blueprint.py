# -*- coding: utf-8 -*-
"""
Exitus - Calendário de Dividendos Blueprint
Endpoints para gerenciamento de calendário de dividendos futuros
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from typing import Dict, Any

from app.services.calendario_dividendo_service import CalendarioDividendoService
from app.schemas.calendario_dividendo_schema import (
    CalendarioDividendoCreateSchema,
    CalendarioDividendoUpdateSchema,
    CalendarioDividendoResponseSchema,
    CalendarioDividendoConfirmarPagamentoSchema,
    CalendarioDividendoGerarSchema
)
import logging

logger = logging.getLogger(__name__)

calendario_dividendo_bp = Blueprint("calendario_dividendo", __name__, url_prefix="/api/calendario-dividendos")

# Schemas
create_schema = CalendarioDividendoCreateSchema()
update_schema = CalendarioDividendoUpdateSchema()
response_schema = CalendarioDividendoResponseSchema()
confirmar_pagamento_schema = CalendarioDividendoConfirmarPagamentoSchema()
gerar_schema = CalendarioDividendoGerarSchema()
response_many_schema = CalendarioDividendoResponseSchema(many=True)


@calendario_dividendo_bp.route("/", methods=["GET"])
@jwt_required()
def listar_calendario():
    """Lista calendário de dividendos do usuário"""
    try:
        usuario_id = get_jwt_identity()
        
        # Parâmetros de filtro
        data_inicio_str = request.args.get("data_inicio")
        data_fim_str = request.args.get("data_fim")
        ativo_id = request.args.get("ativo_id")
        ticker = request.args.get("ticker")
        dias_str = request.args.get("dias")
        limit_str = request.args.get("limit")
        
        # Converter datas
        data_inicio = None
        data_fim = None
        
        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "data_inicio deve estar no formato YYYY-MM-DD"
                }), 400
        
        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "data_fim deve estar no formato YYYY-MM-DD"
                }), 400

        if dias_str:
            try:
                dias = int(dias_str)
                if dias < 1:
                    raise ValueError()
                data_inicio = date.today()
                data_fim = data_inicio + timedelta(days=dias)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "dias deve ser um inteiro positivo"
                }), 400

        limit = None
        if limit_str:
            try:
                limit = int(limit_str)
                if limit < 1:
                    raise ValueError()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "limit deve ser um inteiro positivo"
                }), 400
        
        # Listar calendário
        calendario = CalendarioDividendoService.listar_calendario(
            usuario_id=usuario_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo_id=ativo_id,
            ticker=ticker,
            limit=limit,
        )
        
        return jsonify({
            "success": True,
            "data": {
                "calendario": response_many_schema.dump(calendario),
                "total": len(calendario)
            },
            "message": f"{len(calendario)} itens encontrados"
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/<calendario_id>", methods=["GET"])
@jwt_required()
def buscar_calendario(calendario_id: str):
    """Busca item específico do calendário"""
    try:
        usuario_id = get_jwt_identity()
        
        # Buscar calendário (verificando se pertence ao usuário)
        calendario = CalendarioDividendoService.listar_calendario(
            usuario_id=usuario_id
        )
        
        # Filtrar por ID
        calendario_item = next(
            (c for c in calendario if str(c.id) == calendario_id), 
            None
        )
        
        if not calendario_item:
            return jsonify({
                "success": False,
                "error": "Item do calendário não encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "data": response_schema.dump(calendario_item),
            "message": "Item encontrado"
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/", methods=["POST"])
@jwt_required()
def criar_calendario():
    """Cria novo item no calendário"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não fornecidos"
            }), 400
        
        # Validar dados
        try:
            data_validada = create_schema.load(data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Dados inválidos",
                "details": e.messages
            }), 400
        
        # Garantir que usuário_id seja o do usuário autenticado
        data_validada["usuario_id"] = usuario_id
        
        # Criar calendário
        calendario = CalendarioDividendoService.criar_calendario(data_validada)
        
        return jsonify({
            "success": True,
            "data": response_schema.dump(calendario),
            "message": "Item criado com sucesso"
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/<calendario_id>", methods=["PUT"])
@jwt_required()
def atualizar_calendario(calendario_id: str):
    """Atualiza item do calendário"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não fornecidos"
            }), 400
        
        # Validar dados
        try:
            data_validada = update_schema.load(data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Dados inválidos",
                "details": e.messages
            }), 400
        
        # Atualizar calendário
        calendario = CalendarioDividendoService.atualizar_calendario(
            calendario_id, data_validada
        )
        
        if not calendario:
            return jsonify({
                "success": False,
                "error": "Item do calendário não encontrado"
            }), 404
        
        # Verificar se pertence ao usuário
        if str(calendario.usuario_id) != usuario_id:
            return jsonify({
                "success": False,
                "error": "Não autorizado"
            }), 403
        
        return jsonify({
            "success": True,
            "data": response_schema.dump(calendario),
            "message": "Item atualizado com sucesso"
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/<calendario_id>", methods=["DELETE"])
@jwt_required()
def excluir_calendario(calendario_id: str):
    """Exclui item do calendário"""
    try:
        usuario_id = get_jwt_identity()
        
        # Verificar se item existe e pertence ao usuário
        calendario = CalendarioDividendoService.listar_calendario(
            usuario_id=usuario_id
        )
        
        calendario_item = next(
            (c for c in calendario if str(c.id) == calendario_id), 
            None
        )
        
        if not calendario_item:
            return jsonify({
                "success": False,
                "error": "Item do calendário não encontrado"
            }), 404
        
        # Excluir
        sucesso = CalendarioDividendoService.excluir_calendario(calendario_id)
        
        if sucesso:
            return jsonify({
                "success": True,
                "message": "Item excluído com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Falha ao excluir item"
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao excluir calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/gerar", methods=["POST"])
@jwt_required()
def gerar_calendario():
    """Gera calendário automático baseado em posições"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        payload = data or {}
        payload["usuario_id"] = usuario_id
        
        # Validar dados
        try:
            params = gerar_schema.load(payload)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Parâmetros inválidos",
                "details": e.messages
            }), 400
        
        # Gerar calendário
        calendario = CalendarioDividendoService.gerar_calendario(
            usuario_id=usuario_id,
            meses_futuros=params.get("meses_futuros", 12)
        )
        
        # Filtrar por ativo se especificado
        if params.get("ativo_id"):
            calendario = [
                c for c in calendario 
                if str(c.ativo_id) == params["ativo_id"]
            ]
        
        return jsonify({
            "success": True,
            "data": {
                "calendario": response_many_schema.dump(calendario),
                "total": len(calendario),
                "meses_gerados": params.get("meses_futuros", 12)
            },
            "message": f"Calendário gerado: {len(calendario)} itens"
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar calendário: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/<calendario_id>/confirmar-pagamento", methods=["POST"])
@jwt_required()
def confirmar_pagamento(calendario_id: str):
    """Confirma pagamento de dividendo"""
    try:
        usuario_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Dados não fornecidos"
            }), 400
        
        # Validar dados
        try:
            data_validada = confirmar_pagamento_schema.load(data)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": "Dados inválidos",
                "details": e.messages
            }), 400
        
        # Verificar se item existe e pertence ao usuário
        calendario = CalendarioDividendoService.listar_calendario(
            usuario_id=usuario_id
        )
        
        calendario_item = next(
            (c for c in calendario if str(c.id) == calendario_id), 
            None
        )
        
        if not calendario_item:
            return jsonify({
                "success": False,
                "error": "Item do calendário não encontrado"
            }), 404
        
        # Confirmar pagamento
        calendario_atualizado = CalendarioDividendoService.confirmar_pagamento(
            calendario_id,
            data_validada["data_pagamento"],
            data_validada["valor_real"]
        )
        
        return jsonify({
            "success": True,
            "data": response_schema.dump(calendario_atualizado),
            "message": "Pagamento confirmado com sucesso"
        })
        
    except Exception as e:
        logger.error(f"Erro ao confirmar pagamento: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@calendario_dividendo_bp.route("/resumo", methods=["GET"])
@jwt_required()
def resumo_calendario():
    """Retorna resumo do calendário de dividendos"""
    try:
        usuario_id = get_jwt_identity()
        
        # Parâmetros de filtro
        data_inicio_str = request.args.get("data_inicio")
        data_fim_str = request.args.get("data_fim")
        
        # Converter datas
        data_inicio = None
        data_fim = None
        
        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "data_inicio deve estar no formato YYYY-MM-DD"
                }), 400
        
        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "data_fim deve estar no formato YYYY-MM-DD"
                }), 400
        
        # Listar calendário
        calendario = CalendarioDividendoService.listar_calendario(
            usuario_id=usuario_id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        # Calcular resumo
        total_estimado = sum(
            float(c.valor_estimado or 0) for c in calendario
        )
        total_real = sum(
            float(c.valor_real or 0) for c in calendario
        )
        
        # Agrupar por mês
        resumo_mensal = {}
        for item in calendario:
            mes = item.data_esperada.strftime("%Y-%m")
            if mes not in resumo_mensal:
                resumo_mensal[mes] = {
                    "valor_estimado": 0,
                    "valor_real": 0,
                    "quantidade": 0
                }
            
            resumo_mensal[mes]["valor_estimado"] += float(item.valor_estimado or 0)
            resumo_mensal[mes]["valor_real"] += float(item.valor_real or 0)
            resumo_mensal[mes]["quantidade"] += 1
        
        # Agrupar por ativo
        resumo_ativos = {}
        for item in calendario:
            ticker = item.ticker or "N/A"
            if ticker not in resumo_ativos:
                resumo_ativos[ticker] = {
                    "valor_estimado": 0,
                    "valor_real": 0,
                    "quantidade": 0
                }
            
            resumo_ativos[ticker]["valor_estimado"] += float(item.valor_estimado or 0)
            resumo_ativos[ticker]["valor_real"] += float(item.valor_real or 0)
            resumo_ativos[ticker]["quantidade"] += 1
        
        return jsonify({
            "success": True,
            "data": {
                "total_itens": len(calendario),
                "valor_total_estimado": total_estimado,
                "valor_total_real": total_real,
                "resumo_mensal": resumo_mensal,
                "resumo_ativos": resumo_ativos
            },
            "message": "Resumo calculado"
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular resumo: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
