# -*- coding: utf-8 -*-
"""
Planos Blueprint — Planos de Compra e Venda Disciplinada
Sprint 4 — Frontend API-Driven
"""

from flask import Blueprint, render_template, request, redirect, url_for
import requests

from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('planos', __name__, url_prefix='/planos-compra')


def _fetch_planos_compra(headers):
    try:
        resp = requests.get(
            f'{Config.BACKEND_API_URL}/api/plano-compra/',
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get('data', [])
    except Exception as e:
        print(f'[planos] Erro ao buscar planos de compra: {e}')
    return []


def _fetch_plano_detalhe(headers, plano_id):
    try:
        resp = requests.get(
            f'{Config.BACKEND_API_URL}/api/plano-compra/{plano_id}',
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get('data', {})
    except Exception as e:
        print(f'[planos] Erro ao buscar detalhe plano {plano_id}: {e}')
    return None


@bp.route('/')
@login_required
def compra_lista():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    planos = _fetch_planos_compra(headers)

    stats = {
        'total': len(planos),
        'ativos': sum(1 for p in planos if p.get('status') == 'ativo'),
        'concluidos': sum(1 for p in planos if p.get('status') == 'concluido'),
        'progresso_medio': 0.0,
    }
    progressos = [float(p.get('progresso_percentual') or 0) for p in planos]
    if progressos:
        stats['progresso_medio'] = sum(progressos) / len(progressos)

    return render_template(
        'planos/compra_lista.html',
        planos=planos,
        stats=stats,
    )


@bp.route('/<plano_id>')
@login_required
def compra_detalhe(plano_id):
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    plano = _fetch_plano_detalhe(headers, plano_id)
    return render_template('planos/compra_detalhe.html', plano=plano, plano_id=plano_id)


# Blueprint separado para planos de venda (API pendente no backend)
bp_venda = Blueprint('planos_venda', __name__, url_prefix='/planos-venda')


@bp_venda.route('/')
@login_required
def venda_lista():
    return render_template('planos/venda_lista.html')
