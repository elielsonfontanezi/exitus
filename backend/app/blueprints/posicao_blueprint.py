# -- coding: utf-8 --
# backend/app/blueprints/posicao_blueprint.py
# Exitus - Posicao Blueprint
# Correcoes aplicadas:
#   GAP EXITUS-POS-002: total corretamente exposto na raiz da resposta
#   GAP EXITUS-POS-003: filtro ?ticker= funcional
#   GAP EXITUS-POS-004: filtro ?lucro_positivo= funcional
#   GAP EXITUS-POS-005: rota GET /<uuid:posicao_id> registrada
#   GAP EXITUS-POS-006: rota POST /calcular registrada
#   GAP EXITUS-POS-007: isolamento retorna 403 vs 404

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from app.services.posicao_service import PosicaoService
from app.schemas.posicao_schema import PosicaoResponseSchema, PosicaoResumoSchema
import logging

logger = logging.getLogger(__name__)

posicao_bp = Blueprint('posicao', __name__, url_prefix='/api/posicoes')

posicoes_schema = PosicaoResponseSchema(many=True)
posicao_schema = PosicaoResponseSchema()
resumo_schema = PosicaoResumoSchema()


# --- 1. GET /api/posicoes — Listar posicoes com filtros e paginacao ---
@posicao_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def listar_posicoes():
    """Lista posicoes do usuario autenticado com filtros e paginacao.

    Query params:
        page (int): pagina atual (default: 1)
        per_page (int): registros por pagina (default: 50, max: 100)
        ativo_id (str): filtrar por UUID do ativo
        corretora_id (str): filtrar por UUID da corretora
        ticker (str): filtrar por ticker do ativo (busca parcial, case-insensitive)
        lucro_positivo (bool): se true, retorna apenas posicoes com lucro > 0

    Returns:
        JSON com lista de posicoes paginada.
    """
    try:
        usuario_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)

        # GAP EXITUS-POS-003 / GAP EXITUS-POS-004: montar dict de filtros
        filters = {}
        ativo_id = request.args.get('ativo_id')
        corretora_id = request.args.get('corretora_id')
        ticker = request.args.get('ticker')
        lucro_positivo_str = request.args.get('lucro_positivo')

        if ativo_id:
            filters['ativo_id'] = ativo_id
        if corretora_id:
            filters['corretora_id'] = corretora_id
        if ticker:
            filters['ticker'] = ticker
        if lucro_positivo_str is not None:
            filters['lucro_positivo'] = lucro_positivo_str.lower() == 'true'

        paginacao = PosicaoService.get_all(
            usuario_id,
            page=page,
            per_page=per_page,
            filters=filters if filters else None
        )

        return jsonify(
            success=True,
            data={
                'posicoes': posicoes_schema.dump(paginacao.items)
            },
            # GAP EXITUS-POS-002: total na raiz da resposta
            total=paginacao.total,
            pages=paginacao.pages,
            page=paginacao.page,
            per_page=paginacao.per_page,
            message=f'{paginacao.total} posicoes encontradas'
        ), 200

    except Exception as e:
        logger.error(f'Erro ao listar posicoes: {e}')
        return jsonify(success=False, error=str(e)), 500


# --- 2. GET /api/posicoes/<id> — Detalhar posicao por ID ---
@posicao_bp.route('/<uuid:posicao_id>', methods=['GET'])
@jwt_required()
def get_posicao(posicao_id):
    """Retorna posicao pelo ID com nested ativo e corretora.

    GAP EXITUS-POS-005: rota registrada.
    GAP EXITUS-POS-007: retorna 403 se posicao pertence a outro usuario,
                        404 se ID nao existe.

    Args:
        posicao_id (UUID): ID da posicao.

    Returns:
        JSON com dados completos da posicao.
    """
    try:
        usuario_id = get_jwt_identity()

        # Busca sem filtro de usuario_id para distinguir 404 de 403
        from app.models import Posicao
        from sqlalchemy.orm import joinedload

        posicao = (
            Posicao.query
            .options(
                joinedload(Posicao.ativo),
                joinedload(Posicao.corretora)
            )
            .filter_by(id=posicao_id)
            .first()
        )

        if not posicao:
            return jsonify(success=False, error='Posicao nao encontrada'), 404

        # GAP EXITUS-POS-007: posicao existe mas pertence a outro usuario -> 403
        if str(posicao.usuario_id) != str(usuario_id):
            return jsonify(success=False, error='Acesso negado a esta posicao'), 403

        return jsonify(
            success=True,
            data=posicao_schema.dump(posicao),
            message='Dados da posicao'
        ), 200

    except Exception as e:
        logger.error(f'Erro ao buscar posicao {posicao_id}: {e}')
        return jsonify(success=False, error=str(e)), 500


# --- 3. POST /api/posicoes/calcular — Recalcular posicoes a partir das transacoes ---
@posicao_bp.route('/calcular', methods=['POST'], strict_slashes=False)
@jwt_required()
def calcular_posicoes():
    """Recalcula todas as posicoes do usuario a partir do historico de transacoes.

    GAP EXITUS-POS-006: rota registrada.

    Quando usar:
        - Apos importacao de transacoes em lote
        - Quando posicoes aparecem inconsistentes
        - Apos correcao manual de transacoes

    Returns:
        JSON com contadores: posicoes_criadas, posicoes_atualizadas, posicoes_zeradas.
    """
    try:
        usuario_id = get_jwt_identity()
        resultado = PosicaoService.calcular_posicoes(usuario_id)

        return jsonify(
            success=True,
            data=resultado,
            message=(
                f"Recalculo concluido: "
                f"{resultado['posicoes_criadas']} criadas, "
                f"{resultado['posicoes_atualizadas']} atualizadas, "
                f"{resultado['posicoes_zeradas']} zeradas"
            )
        ), 200

    except Exception as e:
        logger.error(f'Erro ao calcular posicoes: {e}')
        return jsonify(success=False, error=str(e)), 500


# --- 4. GET /api/posicoes/resumo — Resumo consolidado do portfolio ---
@posicao_bp.route('/resumo', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_resumo():
    """Retorna resumo consolidado das posicoes do usuario.

    Returns:
        JSON com totais: quantidade_posicoes, total_investido,
        total_valor_atual, lucro_total, roi_percentual.
    """
    try:
        usuario_id = get_jwt_identity()
        resumo = PosicaoService.get_resumo(usuario_id)

        return jsonify(
            success=True,
            data=resumo,
            message='Resumo de posicoes'
        ), 200

    except Exception as e:
        logger.error(f'Erro ao gerar resumo: {e}')
        return jsonify(success=False, error=str(e)), 500
