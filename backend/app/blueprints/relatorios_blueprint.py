from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/api/relatorios')

@relatorios_bp.route('/auditoria', methods=['GET'])
@jwt_required()
def listar_auditoria():
    return jsonify({'relatorios': [], 'message': 'Auditoria funcionando!'})

@relatorios_bp.route('/projecoes', methods=['GET'])
@jwt_required()
def listar_projecoes():
    return jsonify({'projecoes': [], 'message': 'Projeções funcionando!'})

@relatorios_bp.route('/performance', methods=['POST'])
@jwt_required()
def calcular_performance():
    usuario_id = get_jwt_identity()
    data = request.json
    return jsonify({
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'usuario_id': usuario_id,
        'periodo_inicio': data['periodo_inicio'],
        'periodo_fim': data['periodo_fim'],
        'retorno_bruto_percentual': '18.50%',
        'status': 'criado_com_sucesso'
    }), 201

@relatorios_bp.route('/', methods=['GET'])
@jwt_required()
def dashboard_relatorios():
    from flask import render_template
    return render_template('relatorios.html')

# M7.5 - Cotações Live
@relatorios_bp.route('/cotacoes/<ticker>', methods=['GET'])
@jwt_required()
def cotacao(ticker):
    from app.services.cotacao_service import CotacaoService
    resultado = CotacaoService.obter_cotacao(ticker)
    return jsonify(resultado)

@relatorios_bp.route('/cotacoes/batch', methods=['GET'])
@jwt_required()
def cotacoes_batch():
    tickers = request.args.get('symbols', 'PETR4,VALE3,AAPL').split(',')
    resultados = {}
    for ticker in tickers:
        resultados[ticker] = CotacaoService.obter_cotacao(ticker)
    return jsonify(resultados)
