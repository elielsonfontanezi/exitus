from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime
import requests

from .auth import login_required, get_api_headers

bp = Blueprint('fiscal', __name__, url_prefix='/imposto-renda')

API_BASE = 'http://exitus-backend:5000/api'


def _mes_atual():
    return datetime.now().strftime('%Y-%m')


def _ano_atual():
    return datetime.now().year


@bp.route('/')
@login_required
def index():
    return redirect(url_for('fiscal.ir_mensal'))


@bp.route('/mensal')
@login_required
def ir_mensal():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    mes = _mes_atual()
    apuracao = {}
    erro = None

    try:
        resp = requests.get(
            f'{API_BASE}/ir/apuracao',
            headers=headers,
            params={'ano': mes[:4], 'mes': mes},
            timeout=10
        )
        if resp.status_code == 200:
            apuracao = resp.json().get('data', {})
        else:
            erro = f'API retornou {resp.status_code}'
    except Exception as e:
        erro = str(e)

    return render_template(
        'fiscal/ir_mensal.html',
        apuracao=apuracao,
        mes_atual=mes,
        erro=erro
    )


@bp.route('/darfs')
@login_required
def darfs():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    mes = _mes_atual()
    dados = {}
    erro = None

    try:
        resp = requests.get(
            f'{API_BASE}/ir/darf',
            headers=headers,
            params={'ano': mes[:4], 'mes': mes},
            timeout=10
        )
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
        else:
            erro = f'API retornou {resp.status_code}'
    except Exception as e:
        erro = str(e)

    return render_template(
        'fiscal/darfs.html',
        dados=dados,
        mes_atual=mes,
        erro=erro
    )


@bp.route('/historico')
@login_required
def historico():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    ano = _ano_atual()
    dados = {}
    erro = None

    try:
        resp = requests.get(
            f'{API_BASE}/ir/historico',
            headers=headers,
            params={'ano': ano},
            timeout=10
        )
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
        else:
            erro = f'API retornou {resp.status_code}'
    except Exception as e:
        erro = str(e)

    return render_template(
        'fiscal/historico.html',
        dados=dados,
        ano_atual=ano,
        erro=erro
    )


@bp.route('/declaracao')
@login_required
def declaracao():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    ano = _ano_atual()
    dados = {}
    erro = None

    try:
        resp = requests.get(
            f'{API_BASE}/ir/dirpf',
            headers=headers,
            params={'ano': ano},
            timeout=10
        )
        if resp.status_code == 200:
            dados = resp.json().get('data', {})
        else:
            erro = f'API retornou {resp.status_code}'
    except Exception as e:
        erro = str(e)

    return render_template('fiscal/declaracao_v2.html')
