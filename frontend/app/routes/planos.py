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
    """Planos disciplinados — compra e venda unificados via Alpine.js"""
    return render_template('estrategia/planos_v2.html')


@bp.route('/dashboard')
@login_required
def compra_dashboard():
    """Dashboard de planos de compra — mesma tela com KPIs via API dashboard."""
    return render_template('estrategia/planos_v2.html')


@bp.route('/<plano_id>')
@login_required
def compra_detalhe(plano_id):
    """Redirect para tela unificada de planos."""
    return redirect(url_for('planos.compra_lista'))


# Blueprint separado para planos de venda (API pendente no backend)
bp_venda = Blueprint('planos_venda', __name__, url_prefix='/planos-venda')


@bp_venda.route('/')
@login_required
def venda_lista():
    """Planos disciplinados — aba venda via Alpine.js"""
    return render_template('estrategia/planos_v2.html')


@bp_venda.route('/dashboard')
@login_required
def venda_dashboard():
    """Dashboard de planos de venda — mesma tela com KPIs e gatilhos."""
    return render_template('estrategia/planos_v2.html')
