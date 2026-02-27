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

@fontesbp.route('/', methods=['GET'], strict_slashes=False)
def listar_fontes():
    return jsonify({"success": True, "data": fontes_dados, "message": f"{len(fontes_dados)} fontes encontradas"}), 200

@fontesbp.route('/<string:id>', methods=['GET'])
def buscar_fonte(id):
    fonte = next((f for f in fontes_dados if f["id"] == id), None)
    if fonte:
        return jsonify({"success": True, "data": fonte}), 200
    return jsonify({"success": False, "message": "Fonte não encontrada"}), 404

@fontesbp.route('/', methods=['POST'], strict_slashes=False)
def criar_fonte():
    data = request.json
    fontes_dados.append(data)
    return jsonify({"success": True, "data": data, "message": "Fonte criada"}), 201

@fontesbp.route('/<string:id>', methods=['DELETE'])
def deletar_fonte(id):
    global fontes_dados
    fontes_dados = [f for f in fontes_dados if f["id"] != id]
    return jsonify({"success": True, "message": "Fonte deletada"}), 200
