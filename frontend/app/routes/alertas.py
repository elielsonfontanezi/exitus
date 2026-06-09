# -*- coding: utf-8 -*-
"""
Alertas Blueprint — Gestão de Alertas de Preço e Dividendos
Sprint 4 — Frontend API-Driven
"""

from flask import Blueprint, render_template, redirect, url_for
import requests

from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('alertas', __name__, url_prefix='/alertas')


def _fetch_alertas(headers):
    try:
        resp = requests.get(
            f'{Config.BACKEND_API_URL}/api/alertas/',
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get('data', [])
    except Exception as e:
        print(f'[alertas] Erro ao buscar alertas: {e}')
    return []


@bp.route('/')
@login_required
def lista():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    alertas = _fetch_alertas(headers)

    stats = {
        'total': len(alertas),
        'ativos': sum(1 for a in alertas if a.get('ativo')),
        'inativos': sum(1 for a in alertas if not a.get('ativo')),
        'acionados': sum(1 for a in alertas if a.get('total_acionamentos', 0) > 0),
    }

    por_tipo = {}
    for a in alertas:
        tipo = a.get('tipo_alerta', 'OUTRO')
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return render_template(
        'alertas/lista.html',
        alertas=alertas,
        stats=stats,
        por_tipo=por_tipo,
    )


@bp.route('/preco')
@login_required
def preco():
    return redirect(url_for('alertas.lista'))


@bp.route('/dividendos')
@login_required
def dividendos():
    return redirect(url_for('alertas.lista'))


@bp.route('/personalizados')
@login_required
def personalizados():
    return redirect(url_for('alertas.lista'))
