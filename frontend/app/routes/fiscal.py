from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime
import requests

from .auth import login_required, get_api_headers
from ..config import Config

bp = Blueprint('fiscal', __name__, url_prefix='/imposto-renda')


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
    """Apuração Mensal IR — Alpine.js API-driven"""
    return render_template('fiscal/ir_mensal_v2.html')


@bp.route('/darfs')
@login_required
def darfs():
    """DARFs — Alpine.js API-driven"""
    return render_template('fiscal/darfs_v2.html')


@bp.route('/historico')
@login_required
def historico():
    """Histórico IR — Alpine.js API-driven"""
    return render_template('fiscal/historico_v2.html')


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
            f'{Config.BACKEND_API_URL}/api/ir/dirpf',
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

    return render_template('fiscal/declaracao_v2.html', dados=dados, erro=erro, ano=ano)
