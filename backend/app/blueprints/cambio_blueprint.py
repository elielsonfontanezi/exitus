# -*- coding: utf-8 -*-
"""Exitus - Blueprint Câmbio - Endpoints de conversão e taxas de câmbio"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.cambio_service import CambioService

cambio_bp = Blueprint('cambio', __name__, url_prefix='/api/cambio')


@cambio_bp.route('/taxa-atual', methods=['GET'])
def get_taxa_atual():
    """
    GET /api/cambio/taxa-atual?de=USD&para=BRL
    Retorna a taxa de câmbio atual entre duas moedas (sem autenticação).
    Endpoint público para uso no frontend.
    """
    moeda_origem = request.args.get('de', '').strip().upper()
    moeda_destino = request.args.get('para', '').strip().upper()
    
    if not moeda_origem or not moeda_destino:
        return jsonify({
            'success': False, 
            'message': 'Parâmetros obrigatórios: de e para (ex: ?de=USD&para=BRL)'
        }), 400
    
    if len(moeda_origem) != 3 or len(moeda_destino) != 3:
        return jsonify({
            'success': False,
            'message': 'Moedas devem ter 3 caracteres ISO 4217 (ex: BRL, USD, EUR)'
        }), 400
    
    resultado = CambioService.get_taxa(moeda_origem, moeda_destino)
    
    if resultado.get('erro'):
        return jsonify({'success': False, 'message': resultado['erro']}), 404
    
    return jsonify({'success': True, 'data': resultado}), 200


@cambio_bp.route('/taxa/<par_moeda>', methods=['GET'])
@jwt_required()
def get_taxa(par_moeda):
    """
    GET /api/cambio/taxa/BRL-USD
    Retorna a taxa de câmbio mais recente para o par.
    Query param opcional: ?data=YYYY-MM-DD
    """
    data_str = request.args.get('data')
    data_ref = None
    if data_str:
        try:
            data_ref = date.fromisoformat(data_str)
        except ValueError:
            return jsonify({'success': False, 'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    par_normalizado = par_moeda.upper().replace('-', '/')
    partes = par_normalizado.split('/')
    if len(partes) != 2 or not all(len(p) == 3 for p in partes):
        return jsonify({'success': False, 'message': 'Formato inválido. Use BASE-COTACAO (ex: BRL-USD)'}), 400

    resultado = CambioService.get_taxa(partes[0], partes[1], data_ref)

    if resultado.get('erro'):
        return jsonify({'success': False, 'message': resultado['erro']}), 404

    return jsonify({'success': True, 'data': resultado}), 200


@cambio_bp.route('/converter', methods=['POST'])
@jwt_required()
def converter():
    """
    POST /api/cambio/converter
    Body: { "valor": 100.0, "moeda_origem": "USD", "moeda_destino": "BRL", "data": "2026-03-04" }
    """
    body = request.get_json(silent=True) or {}

    valor_raw = body.get('valor')
    moeda_origem = body.get('moeda_origem', '').strip().upper()
    moeda_destino = body.get('moeda_destino', '').strip().upper()
    data_str = body.get('data')

    if valor_raw is None or not moeda_origem or not moeda_destino:
        return jsonify({'success': False,
                        'message': 'Campos obrigatórios: valor, moeda_origem, moeda_destino'}), 400

    try:
        valor = Decimal(str(valor_raw))
        if valor < 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return jsonify({'success': False, 'message': 'Valor deve ser um número positivo'}), 400

    if len(moeda_origem) != 3 or len(moeda_destino) != 3:
        return jsonify({'success': False,
                        'message': 'Moedas devem ter 3 caracteres ISO 4217 (ex: BRL, USD, EUR)'}), 400

    data_ref = None
    if data_str:
        try:
            data_ref = date.fromisoformat(data_str)
        except ValueError:
            return jsonify({'success': False, 'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    resultado = CambioService.converter(valor, moeda_origem, moeda_destino, data_ref)

    if resultado.get('erro'):
        return jsonify({'success': False, 'message': resultado['erro']}), 404

    return jsonify({'success': True, 'data': resultado}), 200


@cambio_bp.route('/pares', methods=['GET'])
@jwt_required()
def listar_pares():
    """
    GET /api/cambio/pares
    Lista todos os pares disponíveis com taxa mais recente.
    """
    pares = CambioService.listar_pares_disponiveis()
    return jsonify({'success': True, 'data': pares, 'total': len(pares)}), 200


@cambio_bp.route('/taxa/<par_moeda>/historico', methods=['GET'])
@jwt_required()
def historico_taxa(par_moeda):
    """
    GET /api/cambio/taxa/BRL-USD/historico
    Query params opcionais: ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD&limit=30
    """
    from app.models.taxa_cambio import TaxaCambio

    par_normalizado = par_moeda.upper().replace('-', '/')
    partes = par_normalizado.split('/')
    if len(partes) != 2 or not all(len(p) == 3 for p in partes):
        return jsonify({'success': False, 'message': 'Formato inválido. Use BASE-COTACAO (ex: BRL-USD)'}), 400

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    limit = min(int(request.args.get('limit', 30)), 365)

    query = TaxaCambio.query.filter_by(par_moeda=par_normalizado)

    if data_inicio_str:
        try:
            query = query.filter(TaxaCambio.data_referencia >= date.fromisoformat(data_inicio_str))
        except ValueError:
            return jsonify({'success': False, 'message': 'data_inicio inválida. Use YYYY-MM-DD'}), 400

    if data_fim_str:
        try:
            query = query.filter(TaxaCambio.data_referencia <= date.fromisoformat(data_fim_str))
        except ValueError:
            return jsonify({'success': False, 'message': 'data_fim inválida. Use YYYY-MM-DD'}), 400

    registros = query.order_by(TaxaCambio.data_referencia.desc()).limit(limit).all()

    return jsonify({
        'success': True,
        'par_moeda': par_normalizado,
        'total': len(registros),
        'data': [r.to_dict() for r in registros],
    }), 200


@cambio_bp.route('/taxa', methods=['POST'])
@jwt_required()
def registrar_taxa():
    """
    POST /api/cambio/taxa
    Body: { "par_moeda": "BRL/USD", "taxa": 0.178, "data_referencia": "2026-03-04", "fonte": "manual" }
    Registra ou atualiza uma taxa de câmbio manualmente.
    """
    body = request.get_json(silent=True) or {}

    par_moeda = body.get('par_moeda', '').strip().upper()
    taxa_raw = body.get('taxa')
    data_str = body.get('data_referencia')
    fonte = body.get('fonte', 'manual')

    if not par_moeda or taxa_raw is None or not data_str:
        return jsonify({'success': False,
                        'message': 'Campos obrigatórios: par_moeda, taxa, data_referencia'}), 400

    partes = par_moeda.replace('-', '/').split('/')
    if len(partes) != 2 or not all(len(p) == 3 for p in partes):
        return jsonify({'success': False,
                        'message': 'par_moeda inválido. Use BASE/COTACAO (ex: BRL/USD)'}), 400

    try:
        taxa = Decimal(str(taxa_raw))
        if taxa <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return jsonify({'success': False, 'message': 'taxa deve ser um número positivo'}), 400

    try:
        data_ref = date.fromisoformat(data_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'data_referencia inválida. Use YYYY-MM-DD'}), 400

    registro = CambioService.registrar_taxa(
        par_moeda=par_moeda.replace('-', '/'),
        taxa=taxa,
        data_referencia=data_ref,
        fonte=fonte,
    )

    return jsonify({'success': True, 'message': 'Taxa registrada com sucesso', 'data': registro.to_dict()}), 201


@cambio_bp.route('/atualizar', methods=['POST'])
@jwt_required()
def atualizar_taxas():
    """
    POST /api/cambio/atualizar
    Body opcional: { "pares": ["BRL/USD", "BRL/EUR"] }
    Busca taxas atuais via yfinance e atualiza o banco.
    """
    body = request.get_json(silent=True) or {}
    pares = body.get('pares', None)

    resultado = CambioService.atualizar_taxas_yfinance(pares)

    return jsonify({
        'success': True,
        'message': f"{len(resultado['atualizados'])} par(es) atualizado(s)",
        'data': resultado,
    }), 200
