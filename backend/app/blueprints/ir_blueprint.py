# -*- coding: utf-8 -*-
"""
Exitus - IR Blueprint (EXITUS-IR-001 + IR-006)
Endpoints para apuração de Imposto de Renda sobre renda variável.

Rotas:
  GET /api/ir/apuracao?mes=YYYY-MM   — apuração detalhada do mês
  GET /api/ir/darf?mes=YYYY-MM       — DARFs a pagar no mês
  GET /api/ir/historico?ano=YYYY     — resumo anual mês a mês
  GET /api/ir/dirpf?ano=YYYY         — relatório DIRPF anual (IR-006)
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.ir_service import IRService
from app.utils.exceptions import ExitusError
from app.utils.responses import success, error

ir_bp = Blueprint('ir', __name__, url_prefix='/api/ir')


# ---------------------------------------------------------------------------
# GET /api/ir/apuracao?mes=YYYY-MM
# ---------------------------------------------------------------------------
@ir_bp.route('/apuracao', methods=['GET'])
@jwt_required()
def apuracao():
    """Apuração detalhada de IR por categoria para o mês informado."""
    usuario_id = get_jwt_identity()
    mes = request.args.get('mes', '')
    if not mes:
        return error("Parâmetro 'mes' obrigatório. Formato: YYYY-MM", 400)

    try:
        resultado = IRService.apurar_mes(usuario_id, mes)
        return success(resultado, f"Apuração de IR — {mes}")
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f"Erro ao apurar IR: {str(e)}", 500)


# ---------------------------------------------------------------------------
# GET /api/ir/darf?mes=YYYY-MM
# ---------------------------------------------------------------------------
@ir_bp.route('/darf', methods=['GET'])
@jwt_required()
def darf():
    """DARFs a pagar no mês informado (código de receita, valor, status)."""
    usuario_id = get_jwt_identity()
    mes = request.args.get('mes', '')
    if not mes:
        return error("Parâmetro 'mes' obrigatório. Formato: YYYY-MM", 400)

    try:
        apuracao = IRService.apurar_mes(usuario_id, mes)
        resultado = {
            'mes':   mes,
            'darfs': apuracao['darf']['darfs'],  # darf retorna {'darfs': [...]}
            'ir_total': apuracao['ir_total'],
            'alertas': apuracao['alertas'],
        }
        return success(resultado, f"DARFs — {mes}")
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f"Erro ao calcular DARFs: {str(e)}", 500)


# ---------------------------------------------------------------------------
# GET /api/ir/historico?ano=YYYY
# ---------------------------------------------------------------------------
@ir_bp.route('/historico', methods=['GET'])
@jwt_required()
def historico():
    """Resumo de apuração IR mês a mês para o ano informado."""
    usuario_id = get_jwt_identity()
    ano_str = request.args.get('ano', '')
    if not ano_str:
        return error("Parâmetro 'ano' obrigatório. Formato: YYYY", 400)

    try:
        ano = int(ano_str)
        if not (2000 <= ano <= 2100):
            return error("Ano inválido.", 400)
    except ValueError:
        return error("Parâmetro 'ano' deve ser um número inteiro (ex: 2025).", 400)

    try:
        resultado = IRService.historico_anual(usuario_id, ano)
        return success({'ano': ano, 'meses': resultado}, f"Histórico IR — {ano}")
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f"Erro ao buscar histórico IR: {str(e)}", 500)


# ---------------------------------------------------------------------------
# GET /api/ir/dirpf?ano=YYYY
# ---------------------------------------------------------------------------
@ir_bp.route('/dirpf', methods=['GET'])
@jwt_required()
def dirpf():
    """Relatório DIRPF anual: Renda Variável, Proventos e Bens e Direitos."""
    usuario_id = get_jwt_identity()
    ano_str = request.args.get('ano', '')
    if not ano_str:
        return error("Parâmetro 'ano' obrigatório. Formato: YYYY", 400)

    try:
        ano = int(ano_str)
        if not (2000 <= ano <= 2100):
            return error("Ano inválido.", 400)
    except ValueError:
        return error("Parâmetro 'ano' deve ser um número inteiro (ex: 2025).", 400)

    try:
        resultado = IRService.gerar_dirpf(usuario_id, ano)
        return success(resultado, f"DIRPF {ano}")
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f"Erro ao gerar DIRPF: {str(e)}", 500)
