from flask import Blueprint, jsonify, request

regrasbp = Blueprint('regras_fiscais', __name__, url_prefix='/api/regras-fiscais')

# Dados mock baseados em regrafiscal (DB M3)
regras_fiscais = [
    {
        "id": "1",
        "pais": "BR",
        "tipoativo": "AÇÃO",
        "tipooperacao": "VENDA",
        "aliquotair": 15.0,
        "incidesobre": "GANHO_CAPITAL",
        "descricao": "IR sobre ganho de capital em ações (day trade)",
        "ativa": True
    },
    {
        "id": "2", 
        "pais": "BR",
        "tipoativo": "FII",
        "tipooperacao": "VENDA",
        "aliquotair": 20.0,
        "incidesobre": "GANHO_CAPITAL",
        "descricao": "IR FIIs acima de 20k/mês",
        "ativa": True
    }
]

@regrasbp.route('/', methods=['GET'])
def listar_regras():
    return jsonify(regras_fiscais), 200

@regrasbp.route('/<string:id>', methods=['GET'])
def buscar_regra(id):
    regra = next((r for r in regras_fiscais if r["id"] == id), None)
    if regra:
        return jsonify(regra), 200
    return jsonify({"error": "Regra fiscal não encontrada"}), 404

@regrasbp.route('/', methods=['POST'])
def criar_regra():
    data = request.json
    regras_fiscais.append(data)
    return jsonify(data), 201

@regrasbp.route('/<string:id>', methods=['DELETE'])
def deletar_regra(id):
    global regras_fiscais
    regras_fiscais = [r for r in regras_fiscais if r["id"] != id]
    return jsonify({"message": "Regra fiscal deletada"}), 200
