from flask import Blueprint, jsonify

calculosbp = Blueprint('calculos', __name__, url_prefix='/api/calculos')

@calculosbp.route('/portfolio', methods=['GET'])
def calcular_portfolio():
    # Valores mock iniciais para testes e estrutura JSON
    resultados = {
        "rentabilidade": {
            "YTD": 0.05,
            "1A": 0.12,
            "3A": 0.36
        },
        "volatilidade_anualizada": 0.14,
        "sharpe_ratio": 1.15,
        "drawdown_maximo": 0.10,
        "correlacao_ativos": {
            "PETR4": {"VALE3": 0.6, "ITUB4": 0.3},
            "VALE3": {"ITUB4": 0.5}
        },
        "alocacao": {
            "renda_variavel": 0.60,
            "renda_fixa": 0.30,
            "cripto": 0.10
        },
        "dividend_yield_medio": 0.045
    }
    return jsonify(resultados), 200

