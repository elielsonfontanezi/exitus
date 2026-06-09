# -*- coding: utf-8 -*-
"""
Ativos Catálogo Blueprint — Ações, FIIs, ETFs, Renda Fixa, Cripto
Sprint 3 — Frontend API-Driven
"""

from flask import Blueprint, render_template, request, redirect, url_for
import requests

from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('ativos_catalogo', __name__, url_prefix='/ativos')

TIPOS_CONFIG = {
    'acoes': {
        'titulo': 'Minhas Ações',
        'subtitulo': 'Ações e stocks em carteira',
        'icone': 'fas fa-chart-line',
        'cor': 'blue',
        'tipos_api': ['acao', 'stock'],
        'colunas': ['ticker', 'nome', 'mercado', 'preco_atual', 'p_l', 'p_vp', 'roe', 'dividend_yield'],
    },
    'fiis': {
        'titulo': 'Meus FIIs',
        'subtitulo': 'Fundos de Investimento Imobiliário',
        'icone': 'fas fa-building',
        'cor': 'green',
        'tipos_api': ['fii', 'reit'],
        'colunas': ['ticker', 'nome', 'mercado', 'preco_atual', 'p_vp', 'cap_rate', 'dividend_yield'],
    },
    'etfs': {
        'titulo': 'ETFs',
        'subtitulo': 'Exchange Traded Funds',
        'icone': 'fas fa-layer-group',
        'cor': 'purple',
        'tipos_api': ['etf', 'etf_intl'],
        'colunas': ['ticker', 'nome', 'mercado', 'preco_atual', 'dividend_yield'],
    },
    'renda-fixa': {
        'titulo': 'Renda Fixa',
        'subtitulo': 'CDB, LCI/LCA, Tesouro Direto, Debêntures',
        'icone': 'fas fa-shield-alt',
        'cor': 'yellow',
        'tipos_api': ['cdb', 'lci_lca', 'tesouro_direto', 'debenture'],
        'colunas': ['ticker', 'nome', 'preco_atual', 'taxa_cupom', 'data_vencimento', 'valor_nominal'],
    },
    'cripto': {
        'titulo': 'Criptoativos',
        'subtitulo': 'Bitcoin, Ethereum e outros',
        'icone': 'fab fa-bitcoin',
        'cor': 'orange',
        'tipos_api': ['cripto'],
        'colunas': ['ticker', 'nome', 'moeda', 'preco_atual', 'dividend_yield'],
    },
}


def _fetch_ativos(headers, tipos, page=1, per_page=50, search=None):
    """Busca ativos na API filtrando por lista de tipos."""
    todos = []
    for tipo in tipos:
        params = {'tipo': tipo, 'per_page': per_page, 'page': page}
        if search:
            params['ticker'] = search
        try:
            resp = requests.get(
                f'{Config.BACKEND_API_URL}/api/ativos',
                headers=headers,
                params=params,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                todos.extend(data.get('ativos', []))
        except Exception as e:
            print(f'[ativos_catalogo] Erro tipo {tipo}: {e}')
    return todos


def _fetch_ativo_detalhe(headers, ticker):
    """Busca detalhe de um ativo pelo ticker."""
    try:
        resp = requests.get(
            f'{Config.BACKEND_API_URL}/api/ativos',
            headers=headers,
            params={'ticker': ticker, 'per_page': 1},
            timeout=10,
        )
        if resp.status_code == 200:
            ativos = resp.json().get('data', {}).get('ativos', [])
            return ativos[0] if ativos else None
    except Exception as e:
        print(f'[ativos_catalogo] Erro detalhe {ticker}: {e}')
    return None


def _lista_view(categoria):
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    config = TIPOS_CONFIG[categoria]
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip() or None

    ativos = _fetch_ativos(headers, config['tipos_api'], page=page, search=search)

    stats = {
        'total': len(ativos),
        'com_preco': sum(1 for a in ativos if a.get('preco_atual')),
        'dy_medio': 0.0,
    }
    dys = [float(a['dividend_yield']) for a in ativos if a.get('dividend_yield')]
    if dys:
        stats['dy_medio'] = sum(dys) / len(dys)

    return render_template(
        'ativos/lista.html',
        ativos=ativos,
        config=config,
        categoria=categoria,
        stats=stats,
        page=page,
        search=search or '',
    )


@bp.route('/acoes')
@login_required
def acoes():
    return _lista_view('acoes')


@bp.route('/fiis')
@login_required
def fiis():
    return _lista_view('fiis')


@bp.route('/etfs')
@login_required
def etfs():
    return _lista_view('etfs')


@bp.route('/renda-fixa')
@login_required
def renda_fixa():
    return _lista_view('renda-fixa')


@bp.route('/cripto')
@login_required
def cripto():
    return _lista_view('cripto')


@bp.route('/<ticker>')
@login_required
def detalhe(ticker):
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    ativo = _fetch_ativo_detalhe(headers, ticker.upper())
    if not ativo:
        return render_template('ativos/detalhe.html', ativo=None, ticker=ticker.upper())

    return render_template('ativos/detalhe.html', ativo=ativo, ticker=ticker.upper())
