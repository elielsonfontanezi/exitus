#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blueprint de Importação B3 Portal Investidor
Endpoint: POST /api/import/b3
"""

import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.import_b3_service import ImportB3Service
from app.utils.auth import token_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('import_b3', __name__, url_prefix='/api/import')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    """Verifica se extensão do arquivo é permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/b3', methods=['POST'])
@token_required
def importar_b3(current_user):
    """
    Importa arquivo de movimentações do Portal B3
    
    Payload: multipart/form-data
    - file: arquivo CSV ou Excel
    
    Returns:
        {
            "success": true,
            "data": {
                "transacoes_criadas": 10,
                "proventos_criados": 5,
                "erros": [],
                "avisos": ["Ativo X não encontrado, criado automaticamente"],
                "resumo": {
                    "total_linhas": 15,
                    "processadas": 15,
                    "ignoradas": 0
                }
            }
        }
    """
    try:
        # Validar arquivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nome de arquivo vazio'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Formato não suportado. Use: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Salvar arquivo temporário
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        file.save(temp_path)
        logger.info(f"Arquivo salvo temporariamente: {temp_path}")
        
        # Processar importação
        service = ImportB3Service()
        service.usuario_id = current_user.id
        service.arquivo_origem = filename
        
        # Parse movimentações
        movimentacoes = service.parse_movimentacoes(temp_path)
        
        if not movimentacoes:
            os.remove(temp_path)
            return jsonify({
                'success': False,
                'error': 'Nenhuma movimentação válida encontrada no arquivo'
            }), 400
        
        # Processar movimentações
        resultado = service.processar_movimentacoes(movimentacoes, current_user.id)
        
        # Remover arquivo temporário
        os.remove(temp_path)
        logger.info(f"Arquivo temporário removido: {temp_path}")
        
        return jsonify({
            'success': True,
            'data': {
                'transacoes_criadas': resultado.get('transacoes_criadas', 0),
                'proventos_criados': resultado.get('proventos_criados', 0),
                'eventos_criados': resultado.get('eventos_criados', 0),
                'erros': resultado.get('erros', []),
                'avisos': resultado.get('avisos', []),
                'resumo': {
                    'total_linhas': len(movimentacoes),
                    'processadas': resultado.get('processadas', 0),
                    'ignoradas': resultado.get('ignoradas', 0)
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao importar arquivo B3: {e}", exc_info=True)
        
        # Remover arquivo temporário em caso de erro
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': False,
            'error': f'Erro ao processar arquivo: {str(e)}'
        }), 500
