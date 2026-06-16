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
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    mes = request.args.get('mes', '')
    ano = request.args.get('ano', '')

    transacoes = []
    proventos = []
    resumo_ir = {}
    erro = None

    try:
        params = {}
        if mes:
            params['mes'] = mes
        if ano:
            params['ano'] = ano

        r1 = requests.get(f"{Config.BACKEND_API_URL}/api/transacoes",
                          headers=headers, params=params, timeout=10)
        r2 = requests.get(f"{Config.BACKEND_API_URL}/api/proventos",
                          headers=headers, params=params, timeout=10)
        r3 = requests.get(f"{Config.BACKEND_API_URL}/api/ir/apuracao",
                          headers=headers, params=params, timeout=10)

        if r1.status_code == 200:
            d = r1.json()
            transacoes = d.get('data', {}).get('transacoes', d.get('transacoes', []))
        if r2.status_code == 200:
            d = r2.json()
            proventos = d.get('data', {}).get('proventos', d.get('proventos', []))
        if r3.status_code == 200:
            d = r3.json()
            resumo_ir = d.get('data', d) if 'data' in d else d
    except Exception as e:
        erro = str(e)

    return render_template('relatorios/mensal.html',
                           transacoes=transacoes, proventos=proventos,
                           resumo_ir=resumo_ir, mes=mes, ano=ano, erro=erro)


@bp.route('/anual', methods=['GET'])
@login_required
def anual():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    ano = request.args.get('ano', '')

    historico_ir = []
    transacoes_ano = []
    proventos_ano = []
    erro = None

    try:
        params = {}
        if ano:
            params['ano'] = ano

        r1 = requests.get(f"{Config.BACKEND_API_URL}/api/ir/historico",
                          headers=headers, params=params, timeout=10)
        r2 = requests.get(f"{Config.BACKEND_API_URL}/api/transacoes",
                          headers=headers, params=params, timeout=10)
        r3 = requests.get(f"{Config.BACKEND_API_URL}/api/proventos",
                          headers=headers, params=params, timeout=10)

        if r1.status_code == 200:
            d = r1.json()
            historico_ir = d.get('data', {}).get('meses', d.get('meses', []))
        if r2.status_code == 200:
            d = r2.json()
            transacoes_ano = d.get('data', {}).get('transacoes', d.get('transacoes', []))
        if r3.status_code == 200:
            d = r3.json()
            proventos_ano = d.get('data', {}).get('proventos', d.get('proventos', []))
    except Exception as e:
        erro = str(e)

    return render_template('relatorios/anual.html',
                           historico_ir=historico_ir,
                           transacoes_ano=transacoes_ano,
                           proventos_ano=proventos_ano,
                           ano=ano, erro=erro)


@bp.route('/extrato', methods=['GET'])
@login_required
def extrato():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    tipo = request.args.get('tipo', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    page = request.args.get('page', 1, type=int)

    transacoes = []
    total = 0
    erro = None

    try:
        params = {'page': page, 'limit': 50}
        if tipo:
            params['tipo'] = tipo
        if data_inicio:
            params['data_inicio'] = data_inicio
        if data_fim:
            params['data_fim'] = data_fim

        resp = requests.get(f"{Config.BACKEND_API_URL}/api/transacoes",
                            headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            transacoes = d.get('data', {}).get('transacoes', d.get('transacoes', []))
            total = d.get('data', {}).get('total', d.get('total', len(transacoes)))
        else:
            erro = f'API retornou {resp.status_code}'
    except Exception as e:
        erro = str(e)

    return render_template('relatorios/extrato.html',
                           transacoes=transacoes, total=total,
                           tipo=tipo, data_inicio=data_inicio,
                           data_fim=data_fim, page=page, erro=erro)


@bp.route('/ir', methods=['GET'])
@login_required
def ir_completo():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    ano = request.args.get('ano', '')

    historico = []
    dirpf = {}
    apuracao = {}
    erro = None

    try:
        params = {}
        if ano:
            params['ano'] = ano

        r1 = requests.get(f"{Config.BACKEND_API_URL}/api/ir/historico",
                          headers=headers, params=params, timeout=10)
        r2 = requests.get(f"{Config.BACKEND_API_URL}/api/ir/dirpf",
                          headers=headers, params=params, timeout=10)
        r3 = requests.get(f"{Config.BACKEND_API_URL}/api/ir/apuracao",
                          headers=headers, timeout=10)

        if r1.status_code == 200:
            d = r1.json()
            historico = d.get('data', {}).get('meses', d.get('meses', []))
        if r2.status_code == 200:
            dirpf = r2.json().get('data', r2.json())
        if r3.status_code == 200:
            apuracao = r3.json().get('data', r3.json())
    except Exception as e:
        erro = str(e)

    return render_template('relatorios/ir_completo.html',
                           historico=historico, dirpf=dirpf,
                           apuracao=apuracao, ano=ano, erro=erro)


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
