from flask import Blueprint, jsonify, request

feriadosbp = Blueprint('feriados', __name__, url_prefix='/api/feriados')

# Simples lista estática como exemplo
feriados = [
    {"id": "1", "pais": "BR", "data": "2025-01-01", "nome": "Ano Novo"},
    {"id": "2", "pais": "BR", "data": "2025-04-21", "nome": "Tiradentes"}
]

@feriadosbp.route('/', methods=['GET'])
def listar_feriados():
    return jsonify(feriados), 200

@feriadosbp.route('/<string:id>', methods=['GET'])
def buscar_feriado(id):
    feriado = next((f for f in feriados if f["id"] == id), None)
    if feriado:
        return jsonify(feriado), 200
    return jsonify({"error": "Feriado não encontrado"}), 404

@feriadosbp.route('/', methods=['POST'])
def criar_feriado():
    data = request.json
    feriados.append(data)
    return jsonify(data), 201

@feriadosbp.route('/<string:id>', methods=['DELETE'])
def deletar_feriado(id):
    global feriados
    feriados = [f for f in feriados if f["id"] != id]
    return jsonify({"message": "Feriado deletado"}), 200

