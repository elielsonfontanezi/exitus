# -*- coding: utf-8 -*-
"""
Exitus - Export Blueprint (EXITUS-EXPORT-001)
Endpoints de exportação de dados em CSV, Excel, JSON e PDF.

Rotas:
  GET /api/export/transacoes?formato=csv|excel|json|pdf
  GET /api/export/proventos?formato=csv|excel|json|pdf
  GET /api/export/posicoes?formato=csv|excel|json|pdf

Filtros opcionais (query string):
  data_inicio=YYYY-MM-DD
  data_fim=YYYY-MM-DD
  ativo_id=<uuid>
  corretora_id=<uuid>
  tipo=<valor>
"""

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.export_service import ExportService
from app.utils.exceptions import ExitusError
from app.utils.responses import error

export_bp = Blueprint('export', __name__, url_prefix='/api/export')


def _exportar(entidade: str):
    """Handler genérico para qualquer entidade exportável."""
    usuario_id = get_jwt_identity()
    formato = request.args.get('formato', 'json').lower()

    params = {
        'data_inicio':  request.args.get('data_inicio'),
        'data_fim':     request.args.get('data_fim'),
        'ativo_id':     request.args.get('ativo_id'),
        'corretora_id': request.args.get('corretora_id'),
        'tipo':         request.args.get('tipo'),
    }

    try:
        conteudo, content_type, filename = ExportService.exportar(
            usuario_id, entidade, formato, params
        )
        return Response(
            conteudo,
            status=200,
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'X-Total-Records': str(len(conteudo)),
            },
        )
    except ExitusError as e:
        return error(str(e), e.http_status)
    except Exception as e:
        return error(f'Erro ao exportar {entidade}: {str(e)}', 500)


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@export_bp.route('/transacoes', methods=['GET'])
@jwt_required()
def exportar_transacoes():
    """Exporta transações do usuário (compras, vendas, dividendos, etc.)."""
    return _exportar('transacoes')


@export_bp.route('/proventos', methods=['GET'])
@jwt_required()
def exportar_proventos():
    """Exporta proventos recebidos (dividendos, JCP, aluguéis)."""
    return _exportar('proventos')


@export_bp.route('/posicoes', methods=['GET'])
@jwt_required()
def exportar_posicoes():
    """Exporta posição consolidada atual do portfólio."""
    return _exportar('posicoes')
