# -*- coding: utf-8 -*-
"""
Exitus - Blueprint para FonteDados
Endpoints REST para gerenciamento de fontes de dados externas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.fonte_dados_schema import (
    FonteDadosResponseSchema,
    FonteDadosCreateSchema,
    FonteDadosUpdateSchema,
    FonteDadosListSchema
)
from app.services.fonte_dados_service import FonteDadosService


bp = Blueprint('fonte_dados', __name__, url_prefix='/api/fontes-dados')


@bp.route('', methods=['GET'])
@jwt_required()
def list_fontes_dados():
    """Lista todas as fontes de dados"""
    try:
        ativa_only = request.args.get('ativa_only', 'false').lower() == 'true'
        tipo = request.args.get('tipo')
        
        if tipo:
            fontes = FonteDadosService.get_by_tipo(tipo, ativa_only=ativa_only)
        else:
            fontes = FonteDadosService.get_all(ativa_only=ativa_only)
        
        schema = FonteDadosListSchema(many=True)
        result = schema.dump(fontes)
        
        return jsonify({
            'fontes_dados': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_fonte_dados():
    """Cria nova fonte de dados"""
    try:
        schema = FonteDadosCreateSchema()
        data = schema.load(request.json)
        
        usuario_id = get_jwt_identity()
        fonte = FonteDadosService.create(data, usuario_id=usuario_id)
        
        response_schema = FonteDadosResponseSchema()
        result = response_schema.dump(fonte)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<uuid:fonte_id>', methods=['GET'])
@jwt_required()
def get_fonte_dados(fonte_id):
    """Obtém fonte por ID"""
    try:
        fonte = FonteDadosService.get_by_id(fonte_id)
        
        if not fonte:
            return jsonify({'error': 'Fonte de dados não encontrada'}), 404
        
        schema = FonteDadosResponseSchema()
        result = schema.dump(fonte)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<uuid:fonte_id>', methods=['PUT'])
@jwt_required()
def update_fonte_dados(fonte_id):
    """Atualiza fonte existente"""
    try:
        schema = FonteDadosUpdateSchema()
        data = schema.load(request.json)
        
        if not data:
            return jsonify({'error': 'Nenhum campo fornecido para atualização'}), 400
        
        fonte = FonteDadosService.update(fonte_id, data)
        
        response_schema = FonteDadosResponseSchema()
        result = response_schema.dump(fonte)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<uuid:fonte_id>', methods=['DELETE'])
@jwt_required()
def delete_fonte_dados(fonte_id):
    """Remove fonte de dados"""
    try:
        success = FonteDadosService.delete(fonte_id)
        
        if not success:
            return jsonify({'error': 'Fonte de dados não encontrada'}), 404
        
        return jsonify({'message': 'Fonte de dados removida com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nome/<nome>', methods=['GET'])
@jwt_required()
def get_fonte_por_nome(nome):
    """Obtém fonte por nome"""
    try:
        fonte = FonteDadosService.get_by_nome(nome)
        
        if not fonte:
            return jsonify({'error': 'Fonte de dados não encontrada'}), 404
        
        schema = FonteDadosResponseSchema()
        result = schema.dump(fonte)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tipo/<tipo>', methods=['GET'])
@jwt_required()
def get_fontes_por_tipo(tipo):
    """Lista fontes por tipo"""
    try:
        ativa_only = request.args.get('ativa_only', 'true').lower() == 'true'
        fontes = FonteDadosService.get_by_tipo(tipo, ativa_only=ativa_only)
        
        schema = FonteDadosListSchema(many=True)
        result = schema.dump(fontes)
        
        return jsonify({
            'fontes_dados': result,
            'total': len(result),
            'tipo': tipo
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<uuid:fonte_id>/consulta/sucesso', methods=['POST'])
@jwt_required()
def registrar_consulta_sucesso(fonte_id):
    """Registra consulta bem-sucedida"""
    try:
        fonte = FonteDadosService.registrar_consulta_sucesso(fonte_id)
        
        schema = FonteDadosResponseSchema()
        result = schema.dump(fonte)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<uuid:fonte_id>/consulta/erro', methods=['POST'])
@jwt_required()
def registrar_erro(fonte_id):
    """Registra erro na consulta"""
    try:
        fonte = FonteDadosService.registrar_erro(fonte_id)
        
        schema = FonteDadosResponseSchema()
        result = schema.dump(fonte)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/ativas', methods=['GET'])
@jwt_required()
def get_fontes_ativas():
    """Lista fontes ativas ordenadas por prioridade"""
    try:
        fontes = FonteDadosService.get_ativas_por_prioridade()
        
        schema = FonteDadosListSchema(many=True)
        result = schema.dump(fontes)
        
        return jsonify({
            'fontes_dados': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/health', methods=['GET'])
@jwt_required()
def get_health_summary():
    """Resumo de saúde de todas as fontes ativas"""
    try:
        summary = FonteDadosService.get_health_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
