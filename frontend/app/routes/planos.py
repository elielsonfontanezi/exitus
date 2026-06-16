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
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.planos_compra'))


@bp.route('/<plano_id>')
@login_required
def compra_detalhe(plano_id):
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.planos_compra_detalhes', plano_id=plano_id))


# Blueprint separado para planos de venda (API pendente no backend)
bp_venda = Blueprint('planos_venda', __name__, url_prefix='/planos-venda')


@bp_venda.route('/')
@login_required
def venda_lista():
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.planos_venda'))
