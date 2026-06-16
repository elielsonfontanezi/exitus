# -*- coding: utf-8 -*-
"""
Proventos Blueprint — Dividendos, JCP e Rendimentos
Sprint 2 — Frontend API-Driven
"""

from collections import defaultdict
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
import requests

from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('proventos', __name__, url_prefix='/proventos')


def _fetch_proventos(headers, status_filter=None, page=1, per_page=100):
    """Busca proventos na API e normaliza os dados."""
    params = {'per_page': per_page, 'page': page}
    if status_filter:
        params['status'] = status_filter

    try:
        resp = requests.get(
            f'{Config.BACKEND_API_URL}/api/proventos',
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code != 200:
            return [], {}, []
    except Exception as e:
        print(f'[proventos] Erro ao buscar API: {e}')
        return [], {}, []

    payload = resp.json()
    data_container = payload.get('data', {})
    raw_list = (
        data_container
        if isinstance(data_container, list)
        else data_container.get('proventos', [])
    )

    proventos = []
    stats = {'total': 0, 'recebido': 0.0, 'previsto': 0.0, 'total_geral': 0.0}
    timeline_acc = defaultdict(float)

    for item in raw_list:
        data_pag = item.get('data_pagamento')
        data_com = item.get('data_com')

        raw_tipo = item.get('tipo_provento', 'TipoProvento.DIVIDENDO')
        tipo = raw_tipo.split('.')[-1]

        valor = float(item.get('valor_liquido') or item.get('valor_bruto') or 0.0)
        valor_unitario = float(item.get('valor_por_acao') or 0.0)
        quantidade = float(item.get('quantidade_ativos') or 0)

        ativo_info = item.get('ativo') or {}
        ticker_label = ativo_info.get('ticker') or item.get('ticker') or f"ID {str(item.get('ativo_id', ''))[:4]}"
        ativo_obj = {'ticker': ticker_label, 'nome': ativo_info.get('nome', ticker_label)}

        status = 'PREVISTO'
        if data_pag:
            try:
                if datetime.strptime(data_pag, '%Y-%m-%d') <= datetime.now():
                    status = 'PAGO'
            except Exception:
                pass

        proventos.append({
            'data_com': data_com,
            'data_pagamento': data_pag,
            'ativo': ativo_obj,
            'tipo': tipo,
            'moeda': 'R$',
            'valor_unitario': valor_unitario,
            'quantidade': quantidade,
            'valor_total': valor,
            'status': status,
        })

        stats['total'] += 1
        stats['total_geral'] += valor
        if status == 'PAGO':
            stats['recebido'] += valor
        else:
            stats['previsto'] += valor

        d_ref = data_pag or data_com
        if d_ref:
            timeline_acc[d_ref[:7]] += valor

    timeline = [{'mes': k, 'valor': v} for k, v in sorted(timeline_acc.items())]
    return proventos, stats, timeline


@bp.route('/recebidos')
@login_required
def recebidos():
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.proventos_calendario'))


@bp.route('/projetados')
@login_required
def projetados():
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.proventos_calendario'))


@bp.route('/calendario')
@login_required
def calendario():
    """Redirect para versão Alpine.js do dashboard."""
    return redirect(url_for('dashboard.proventos_calendario'))
