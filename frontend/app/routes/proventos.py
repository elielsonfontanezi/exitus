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
        quantidade = item.get('quantidade', 0)

        ticker_label = item.get('ticker') or f"ID {str(item.get('ativo_id', ''))[:4]}"
        ativo_obj = {'ticker': ticker_label, 'nome': ticker_label}

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
    """Proventos já pagos."""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)
    proventos_todos, stats, timeline = _fetch_proventos(headers, page=page)
    proventos = [p for p in proventos_todos if p['status'] == 'PAGO']

    stats_recebidos = {
        'total': len(proventos),
        'recebido': sum(p['valor_total'] for p in proventos),
        'previsto': 0.0,
        'total_geral': sum(p['valor_total'] for p in proventos),
    }
    timeline_recebidos = []
    acc = defaultdict(float)
    for p in proventos:
        ref = p['data_pagamento'] or p['data_com']
        if ref:
            acc[ref[:7]] += p['valor_total']
    timeline_recebidos = [{'mes': k, 'valor': v} for k, v in sorted(acc.items())]

    return render_template(
        'proventos/recebidos.html',
        proventos=proventos,
        stats=stats_recebidos,
        timeline=timeline_recebidos,
        page=page,
    )


@bp.route('/projetados')
@login_required
def projetados():
    """Proventos previstos (ainda não pagos)."""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)
    proventos_todos, stats, timeline = _fetch_proventos(headers, page=page)
    proventos = [p for p in proventos_todos if p['status'] == 'PREVISTO']

    stats_projetados = {
        'total': len(proventos),
        'recebido': 0.0,
        'previsto': sum(p['valor_total'] for p in proventos),
        'total_geral': sum(p['valor_total'] for p in proventos),
    }
    acc = defaultdict(float)
    for p in proventos:
        ref = p['data_pagamento'] or p['data_com']
        if ref:
            acc[ref[:7]] += p['valor_total']
    timeline_projetados = [{'mes': k, 'valor': v} for k, v in sorted(acc.items())]

    return render_template(
        'proventos/projetados.html',
        proventos=proventos,
        stats=stats_projetados,
        timeline=timeline_projetados,
        page=page,
    )


@bp.route('/calendario')
@login_required
def calendario():
    """Calendário de dividendos — visão mensal de todos os proventos."""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))

    proventos_todos, stats, timeline = _fetch_proventos(headers)

    meses = defaultdict(list)
    for p in proventos_todos:
        ref = p['data_pagamento'] or p['data_com']
        if ref:
            meses[ref[:7]].append(p)

    calendario_data = []
    for mes_key in sorted(meses.keys(), reverse=True):
        itens = meses[mes_key]
        total_mes = sum(i['valor_total'] for i in itens)
        try:
            dt = datetime.strptime(mes_key, '%Y-%m')
            label = dt.strftime('%B %Y').capitalize()
        except Exception:
            label = mes_key
        calendario_data.append({
            'mes_key': mes_key,
            'label': label,
            'itens': itens,
            'total': total_mes,
            'count': len(itens),
        })

    return render_template(
        'proventos/calendario.html',
        calendario=calendario_data,
        stats=stats,
        timeline=timeline,
    )
