# -*- coding: utf-8 -*-
"""
Ferramentas Blueprint - Sprint 8
Rotas: /ferramentas/comparador, /ferramentas/calculadora-ir,
        /ferramentas/simulador, /ferramentas/screener
"""

from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('ferramentas', __name__, url_prefix='/ferramentas')


@bp.route('/comparador', methods=['GET'])
@login_required
def comparador():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    tickers = request.args.getlist('ticker')
    ativos_lista = []
    comparacao = []
    erro = None

    try:
        resp = requests.get(f"{Config.BACKEND_API_URL}/api/ativos",
                            headers=headers, params={'limit': 200}, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            ativos_lista = d.get('data', {}).get('ativos', [])

        for ticker in tickers[:3]:
            cot = requests.get(f"{Config.BACKEND_API_URL}/api/cotacoes/{ticker}",
                               headers=headers, timeout=10)
            cotacao = {}
            if cot.status_code == 200:
                cotacao = cot.json().get('data', {})

            ativo = next((a for a in ativos_lista if a.get('ticker') == ticker), {})
            if ativo or cotacao:
                comparacao.append({
                    'ticker': ticker,
                    'nome': ativo.get('nome', cotacao.get('nome', ticker)),
                    'tipo': ativo.get('tipo', ''),
                    'preco': cotacao.get('preco_atual', ativo.get('preco_atual', 0)),
                    'variacao': cotacao.get('variacao_dia', 0),
                    'dividend_yield': ativo.get('dividend_yield', 0),
                    'p_vp': ativo.get('p_vp', 0),
                    'p_l': ativo.get('p_l', 0),
                    'beta': ativo.get('beta', 0),
                    'market_cap': ativo.get('market_cap', 0),
                    'roe': ativo.get('roe', 0),
                    'liquidez_corrente': ativo.get('liquidez_corrente', 0),
                })
    except Exception as e:
        erro = str(e)

    return render_template('ferramentas/comparador.html',
                           ativos_lista=ativos_lista, comparacao=comparacao,
                           tickers=tickers, erro=erro)


@bp.route('/calculadora-ir', methods=['GET'])
@login_required
def calculadora_ir():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    posicoes = []
    erro = None

    try:
        resp = requests.get(f"{Config.BACKEND_API_URL}/api/posicoes",
                            headers=headers, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            raw = d.get('data', {}).get('posicoes', d.get('posicoes', []))
            for p in raw:
                atv = p.get('ativo', {})
                posicoes.append({
                    'ticker': atv.get('ticker', ''),
                    'nome': atv.get('nome', ''),
                    'tipo': atv.get('tipo', ''),
                    'quantidade': p.get('quantidade', 0),
                    'preco_medio': p.get('preco_medio', 0),
                    'custo_total': p.get('custo_total', 0),
                })
    except Exception as e:
        erro = str(e)

    return render_template('ferramentas/calculadora_ir.html',
                           posicoes=posicoes, erro=erro)


@bp.route('/simulador', methods=['GET'])
@login_required
def simulador():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    return render_template('ferramentas/simulador.html')


@bp.route('/screener', methods=['GET'])
@login_required
def screener():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    tipo = request.args.get('tipo', '')
    dy_min = request.args.get('dy_min', '')
    pvp_max = request.args.get('pvp_max', '')
    pl_max = request.args.get('pl_max', '')
    erro = None
    ativos = []

    try:
        params = {'limit': 200}
        if tipo:
            params['tipo'] = tipo

        resp = requests.get(f"{Config.BACKEND_API_URL}/api/ativos",
                            headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            ativos = d.get('data', {}).get('ativos', [])

            if dy_min:
                ativos = [a for a in ativos
                          if float(a.get('dividend_yield') or 0) >= float(dy_min)]
            if pvp_max:
                ativos = [a for a in ativos
                          if a.get('p_vp') is not None
                          and float(a.get('p_vp') or 0) <= float(pvp_max)
                          and float(a.get('p_vp') or 0) > 0]
            if pl_max:
                ativos = [a for a in ativos
                          if a.get('p_l') is not None
                          and float(a.get('p_l') or 0) <= float(pl_max)
                          and float(a.get('p_l') or 0) > 0]

        ativos.sort(key=lambda a: float(a.get('dividend_yield') or 0), reverse=True)
    except Exception as e:
        erro = str(e)

    return render_template('ferramentas/screener.html',
                           ativos=ativos, tipo=tipo,
                           dy_min=dy_min, pvp_max=pvp_max, pl_max=pl_max,
                           erro=erro)
