from flask import Blueprint, jsonify, request

fontesbp = Blueprint('fontes', __name__, url_prefix='/api/fontes')

# Dados mock baseados em fontedados (DB M3)
fontes_dados = [
    {
        "id": "1", 
        "nome": "yfinance", 
        "tipofonte": "API_GERAL",
        "urlbase": "https://finance.yahoo.com",
        "ativa": True,
        "prioridade": 1
    },
    {
        "id": "2", 
        "nome": "Alpha Vantage", 
        "tipofonte": "API_FINANCEIRA",
        "urlbase": "https://www.alphavantage.co",
        "ativa": True, 
        "prioridade": 2
    }
]

@fontesbp.route('/', methods=['GET'])
def listar_fontes():
    return jsonify(fontes_dados), 200

@fontesbp.route('/<string:id>', methods=['GET'])
def buscar_fonte(id):
    fonte = next((f for f in fontes_dados if f["id"] == id), None)
    if fonte:
        return jsonify(fonte), 200
    return jsonify({"error": "Fonte não encontrada"}), 404

@fontesbp.route('/', methods=['POST'])
def criar_fonte():
    data = request.json
    fontes_dados.append(data)
    return jsonify(data), 201

@fontesbp.route('/<string:id>', methods=['DELETE'])
def deletar_fonte(id):
    global fontes_dados
    fontes_dados = [f for f in fontes_dados if f["id"] != id]
    return jsonify({"message": "Fonte deletada"}), 200
