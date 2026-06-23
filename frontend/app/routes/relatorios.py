# -*- coding: utf-8 -*-
"""
Relatorios Blueprint - Sprint 7
Rotas: /relatorios/mensal, /relatorios/anual, /relatorios/extrato,
        /relatorios/ir, /relatorios/exportar/csv
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@bp.route('/mensal', methods=['GET'])
@login_required
def mensal():
    """Relatório Mensal — Alpine.js API-driven"""
    return render_template('relatorios/mensal_v2.html')


@bp.route('/anual', methods=['GET'])
@login_required
def anual():
    """Relatório Anual — Alpine.js API-driven"""
    return render_template('relatorios/anual_v2.html')


@bp.route('/extrato', methods=['GET'])
@login_required
def extrato():
    """Extrato de Transações — Alpine.js API-driven"""
    return render_template('relatorios/extrato_v2.html')


@bp.route('/ir', methods=['GET'])
@login_required
def ir_completo():
    """Relatório IR Completo — Alpine.js API-driven"""
    return render_template('relatorios/ir_completo_v2.html')


@bp.route('/exportar', methods=['GET'])
@login_required
def exportar():
    """Página de configuração para exportação de dados"""
    return render_template('relatorios/exportar.html')

@bp.route('/exportar/csv', methods=['GET'])
@login_required
def exportar_csv():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    tipo = request.args.get('tipo', 'transacoes')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    preview = request.args.get('preview', 'false') == 'true'

    dados = []
    colunas = []
    erro = None

    try:
        if tipo == 'transacoes':
            params = {}
            if data_inicio:
                params['data_inicio'] = data_inicio
            if data_fim:
                params['data_fim'] = data_fim
            resp = requests.get(f"{Config.BACKEND_API_URL}/api/transacoes",
                                headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                d = resp.json()
                dados = d.get('data', {}).get('transacoes', d.get('transacoes', []))
                if dados:
                    colunas = ['data', 'tipo', 'ticker', 'quantidade', 'preco_unitario',
                               'valor_total', 'corretagem', 'notas']

        elif tipo == 'proventos':
            resp = requests.get(f"{Config.BACKEND_API_URL}/api/proventos",
                                headers=headers, timeout=10)
            if resp.status_code == 200:
                d = resp.json()
                dados = d.get('data', {}).get('proventos', d.get('proventos', []))
                if dados:
                    colunas = ['data_pagamento', 'ticker', 'tipo', 'valor_por_cota',
                               'quantidade', 'valor_total']

        elif tipo == 'posicoes':
            resp = requests.get(f"{Config.BACKEND_API_URL}/api/posicoes",
                                headers=headers, timeout=10)
            if resp.status_code == 200:
                d = resp.json()
                posicoes_raw = d.get('data', {}).get('posicoes', d.get('posicoes', []))
                for p in posicoes_raw:
                    atv = p.get('ativo', {})
                    dados.append({
                        'ticker': atv.get('ticker', ''),
                        'nome': atv.get('nome', ''),
                        'tipo': atv.get('tipo', ''),
                        'quantidade': p.get('quantidade', 0),
                        'preco_medio': p.get('preco_medio', 0),
                        'custo_total': p.get('custo_total', 0),
                    })
                if dados:
                    colunas = ['ticker', 'nome', 'tipo', 'quantidade', 'preco_medio', 'custo_total']

    except Exception as e:
        erro = str(e)

    # Se preview=True, renderiza página HTML (comportamento antigo)
    if preview:
        return render_template('relatorios/exportar_csv.html',
                               dados=dados, colunas=colunas,
                               tipo=tipo, data_inicio=data_inicio,
                               data_fim=data_fim, erro=erro)

    # Download direto do CSV (novo comportamento)
    if erro:
        return render_template('relatorios/exportar_csv.html',
                               dados=[], colunas=[],
                               tipo=tipo, data_inicio=data_inicio,
                               data_fim=data_fim, erro=erro)

    if not dados:
        return render_template('relatorios/exportar_csv.html',
                               dados=[], colunas=[],
                               tipo=tipo, data_inicio=data_inicio,
                               data_fim=data_fim, erro="Nenhum dado encontrado para exportação")

    # Gerar CSV
    csv_lines = []
    csv_lines.append(','.join(colunas))
    
    for row in dados:
        values = []
        for col in colunas:
            value = row.get(col, '')
            if value is None:
                value = ''
            else:
                value = str(value)
            # Escapar aspas e adicionar aspas se necessário
            if ',' in value or '"' in value or '\n' in value:
                value = '"' + value.replace('"', '""') + '"'
            values.append(value)
        csv_lines.append(','.join(values))
    
    csv_content = '\n'.join(csv_lines)
    
    # Gerar nome do arquivo
    data_str = f"_{data_inicio}_to_{data_fim}" if data_inicio and data_fim else ""
    filename = f"exitus_{tipo}{data_str}.csv"
    
    # Criar resposta HTTP com download
    from flask import Response
    response = Response(
        csv_content,
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )
    
    return response
