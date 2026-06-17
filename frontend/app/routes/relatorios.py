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
    """Exportação multi-formato (CSV/Excel/PDF) via API backend — Alpine.js client-side"""
    return render_template('relatorios/exportar_v2.html')


@bp.route('/exportar/csv', methods=['GET'])
@login_required
def exportar_csv():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    tipo = request.args.get('tipo', 'transacoes')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

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

    return render_template('relatorios/exportar_csv.html',
                           dados=dados, colunas=colunas,
                           tipo=tipo, data_inicio=data_inicio,
                           data_fim=data_fim, erro=erro)
