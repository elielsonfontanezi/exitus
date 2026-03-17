# -*- coding: utf-8 -*-
"""
Exitus - Blueprint para ParametrosMacro
Endpoints REST para gerenciamento de parâmetros macroeconômicos
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.parametros_macro_schema import (
    ParametrosMacroResponseSchema,
    ParametrosMacroCreateSchema,
    ParametrosMacroUpdateSchema
)
from app.services.parametros_macro_service import ParametrosMacroService


bp = Blueprint('parametros_macro', __name__, url_prefix='/api/parametros-macro')


@bp.route('', methods=['GET'])
@jwt_required()
def list_parametros_macro():
    """Lista todos os parâmetros macroeconômicos"""
    try:
        ativo_only = request.args.get('ativo_only', 'true').lower() == 'true'
        parametros = ParametrosMacroService.get_all(ativo_only=ativo_only)
        
        schema = ParametrosMacroResponseSchema(many=True)
        result = schema.dump(parametros)
        
        return jsonify({
            'parametros_macro': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_parametro_macro():
    """Cria novo parâmetro macroeconômico"""
    try:
        schema = ParametrosMacroCreateSchema()
        data = schema.load(request.json)
        
        parametro = ParametrosMacroService.create(data)
        
        response_schema = ParametrosMacroResponseSchema()
        result = response_schema.dump(parametro)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<uuid:param_id>', methods=['GET'])
@jwt_required()
def get_parametro_macro(param_id):
    """Obtém parâmetro por ID"""
    try:
        parametro = ParametrosMacroService.get_by_id(param_id)
        
        if not parametro:
            return jsonify({'error': 'Parâmetro não encontrado'}), 404
        
        schema = ParametrosMacroResponseSchema()
        result = schema.dump(parametro)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<uuid:param_id>', methods=['PUT'])
@jwt_required()
def update_parametro_macro(param_id):
    """Atualiza parâmetro existente"""
    try:
        schema = ParametrosMacroUpdateSchema()
        data = schema.load(request.json)
        
        if not data:
            return jsonify({'error': 'Nenhum campo fornecido para atualização'}), 400
        
        parametro = ParametrosMacroService.update(param_id, data)
        
        response_schema = ParametrosMacroResponseSchema()
        result = response_schema.dump(parametro)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<uuid:param_id>', methods=['DELETE'])
@jwt_required()
def delete_parametro_macro(param_id):
    """Remove parâmetro"""
    try:
        success = ParametrosMacroService.delete(param_id)
        
        if not success:
            return jsonify({'error': 'Parâmetro não encontrado'}), 404
        
        return jsonify({'message': 'Parâmetro removido com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pais/<pais>/mercado/<mercado>', methods=['GET'])
@jwt_required()
def get_parametro_por_pais_mercado(pais, mercado):
    """Obtém parâmetro por país/mercado"""
    try:
        ativo_only = request.args.get('ativo_only', 'true').lower() == 'true'
        parametro = ParametrosMacroService.get_by_pais_mercado(pais, mercado, ativo_only=ativo_only)
        
        if not parametro:
            return jsonify({'error': 'Parâmetro não encontrado'}), 404
        
        schema = ParametrosMacroResponseSchema()
        result = schema.dump(parametro)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/dict/<pais>/<mercado>', methods=['GET'])
@jwt_required()
def get_parametro_dict(pais, mercado):
    """Obtém parâmetros como dicionário (compatível com código legado)"""
    try:
        parametros = ParametrosMacroService.get_parametros_dict(pais, mercado)
        return jsonify(parametros)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
