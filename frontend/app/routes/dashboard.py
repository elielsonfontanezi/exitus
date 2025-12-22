# -*- coding: utf-8 -*-
"""
Exitus Frontend - Dashboard Routes
MÓDULO 6: Buy Signals + Portfolios + Transações + Proventos ✅
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import requests
from functools import wraps
from app.config import Config
from collections import defaultdict
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def login_required(f):
    """Decorator FINAL - aceita username OU accesstoken"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') or session.get('accesstoken'):
            return f(*args, **kwargs)
        return redirect(url_for('auth.login'))
    return decorated_function


# ========================================
# HELPER: Transformar dados da API
# ========================================

def transform_buy_signal(item):
    """Transforma estrutura da API para formato do template"""
    ticker = item.get('ticker', '')
    preco_atual = item.get('preco_atual', 0)
    preco_teto = item.get('preco_teto', 0)

    margem = 0
    if preco_teto > 0 and preco_atual > 0:
        margem = round(((preco_teto - preco_atual) / preco_atual) * 100, 2)

    mercado = 'BR' if any(c.isdigit() for c in ticker) else 'US'

    return {
        'ticker': ticker,
        'nome': ticker,
        'mercado': mercado,
        'buyscore': item.get('buy_score', 0),
        'margem': margem,
        'preco_atual': preco_atual,
        'preco_teto': preco_teto
    }


# ========================================
# DASHBOARD INDEX
# ========================================

@bp.route('/')
@login_required
def index():
    """Dashboard principal - M6 ✅"""
    return render_template('dashboard/index.html')


# ========================================
# M6.1 BUY SIGNALS
# ========================================

@bp.route('/buy-signals', methods=['GET'])
@login_required
def buy_signals():
    """Buy Signals Completo - M6.1 ✅"""
    token = session.get('accesstoken')
    data = []

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/buy-signals/watchlist-top',
                headers=headers, timeout=5
            )
            if response.status_code == 200:
                raw_data = response.json().get('data', [])
                data = [transform_buy_signal(item) for item in raw_data]
        except Exception as e:
            print(f"❌ Erro ao buscar buy signals: {e}")

    if not data:
        data = [
            {'ticker': 'PETR4', 'nome': 'Petrobras', 'mercado': 'BR', 'buyscore': 87, 'margem': 8.85},
            {'ticker': 'VALE3', 'nome': 'Vale', 'mercado': 'BR', 'buyscore': 72, 'margem': 5.2},
            {'ticker': 'AAPL', 'nome': 'Apple', 'mercado': 'US', 'buyscore': 65, 'margem': 2.1}
        ]

    summary = {
        'mercados': {
            'labels': ['BR', 'US', 'EU'],
            'data': [
                len([s for s in data if s.get('mercado') == 'BR']),
                len([s for s in data if s.get('mercado') == 'US']),
                0
            ]
        }
    }

    return render_template('dashboard/buy_signals.html',
                           signals=data, total_pages=1, current_page=1, summary=summary)


@bp.route('/buy-signals/table', methods=['GET'])
@login_required
def buy_signals_table():
    """HTMX partial - tabela Buy Signals"""
    token = session.get('accesstoken')
    data = []

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/buy-signals/watchlist-top',
                headers=headers, timeout=5
            )
            if response.status_code == 200:
                raw_data = response.json().get('data', [])
                data = [transform_buy_signal(item) for item in raw_data]
        except Exception as e:
            print(f"❌ Erro ao buscar buy signals table: {e}")

    if not data:
        data = [
            {'ticker': 'PETR4', 'nome': 'Petrobras', 'mercado': 'BR', 'buyscore': 87, 'margem': 8.85},
            {'ticker': 'VALE3', 'nome': 'Vale', 'mercado': 'BR', 'buyscore': 72, 'margem': 5.2}
        ]

    return render_template('components/buy_signals_table.html',
                           signals=data, total_pages=1, current_page=1, request=request)


# ========================================
# M6.2 PORTFOLIOS
# ========================================

@bp.route('/portfolios', methods=['GET'])
@login_required
def portfolios():
    """M6.2 - Gestão de Carteiras/Corretoras ✅"""
    token = session.get('accesstoken')
    corretoras = []
    saldo_total = 0

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/corretoras',
                headers=headers, timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                corretoras = result.get('data', {}).get('corretoras', [])
                saldo_total = sum([c.get('saldo_atual', 0) for c in corretoras])
        except Exception:
            pass

    if not corretoras:
        corretoras = [
            {'id': '1', 'nome': 'XP Investimentos', 'tipo': 'corretora',
             'pais': 'BR', 'moeda_padrao': 'BRL', 'saldo_atual': 25430.50, 'ativa': True},
            {'id': '2', 'nome': 'Clear Corretora', 'tipo': 'corretora',
             'pais': 'BR', 'moeda_padrao': 'BRL', 'saldo_atual': 15200.00, 'ativa': True},
            {'id': '3', 'nome': 'Avenue Securities', 'tipo': 'corretora',
             'pais': 'US', 'moeda_padrao': 'USD', 'saldo_atual': 5800.00, 'ativa': True}
        ]
        saldo_total = sum([c['saldo_atual'] for c in corretoras])

    stats = {
        'total': len(corretoras),
        'ativas': len([c for c in corretoras if c.get('ativa', True)]),
        'saldo_total': saldo_total,
        'saldo_br': sum([c.get('saldo_atual', 0) for c in corretoras if c.get('pais') == 'BR']),
        'saldo_us': sum([c.get('saldo_atual', 0) for c in corretoras if c.get('pais') == 'US'])
    }

    return render_template('dashboard/portfolios.html',
                           corretoras=corretoras, stats=stats)


@bp.route('/portfolios/create', methods=['POST'])
@login_required
def portfolios_create():
    """M6.2 - Criar nova carteira via API M3 ✅"""
    try:
        data = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'pais': request.form.get('pais'),
            'moeda_padrao': request.form.get('moeda'),
            'saldo_atual': float(request.form.get('saldo') or 0),
            'ativa': True
        }

        token = session.get('accesstoken')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

        response = requests.post(
            f'{Config.BACKEND_API_URL}/api/corretoras',
            json=data, headers=headers, timeout=10
        )

        if response.status_code in [200, 201]:
            flash('✅ Carteira criada com sucesso!', 'success')
        else:
            flash(f'❌ API Error: {response.status_code}', 'error')
    except Exception as e:
        flash(f'❌ Erro: {str(e)}', 'error')

    return redirect(url_for('dashboard.portfolios'))


# ========================================
# M6.3 TRANSAÇÕES
# ========================================

@bp.route('/transactions', methods=['GET'])
@login_required
def transactions():
    """M6.3 - Gestão de Transações (COMPRA/VENDA) - Todos os tipos de ativos"""
    token = session.get('accesstoken')
    transacoes = []

    tipo_ativo = request.args.get('tipo')
    classe = request.args.get('classe')
    mercado = request.args.get('mercado')
    corretora_id = request.args.get('corretora')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    page = int(request.args.get('page', 1))

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'page': page, 'per_page': 20}

            if tipo_ativo:
                params['tipo_ativo'] = tipo_ativo
            if classe:
                params['classe'] = classe
            if mercado:
                params['mercado'] = mercado
            if corretora_id:
                params['corretora_id'] = corretora_id
            if data_inicio:
                params['data_inicio'] = data_inicio
            if data_fim:
                params['data_fim'] = data_fim

            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/transacoes',
                headers=headers, params=params, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                transacoes = result.get('data', {}).get('transacoes', [])
        except Exception:
            pass

    if not transacoes:
        transacoes = [
            {
                'id': '1', 'data': '2024-12-01', 'tipo_operacao': 'compra',
                'ativo': {'ticker': 'PETR4', 'nome': 'Petrobras', 'tipo': 'acao', 'classe': 'rendavariavel', 'mercado': 'BR'},
                'corretora': {'nome': 'XP Investimentos'},
                'quantidade': 100, 'preco_unitario': 38.50, 'valor_total': 3850.00,
                'taxas': 5.00, 'moeda': 'BRL'
            },
            {
                'id': '2', 'data': '2024-11-28', 'tipo_operacao': 'compra',
                'ativo': {'ticker': 'MXRF11', 'nome': 'Maxi Renda', 'tipo': 'fii', 'classe': 'rendavariavel', 'mercado': 'BR'},
                'corretora': {'nome': 'Clear Corretora'},
                'quantidade': 50, 'preco_unitario': 10.20, 'valor_total': 510.00,
                'taxas': 2.50, 'moeda': 'BRL'
            },
            {
                'id': '3', 'data': '2024-11-25', 'tipo_operacao': 'compra',
                'ativo': {'ticker': 'AAPL', 'nome': 'Apple Inc', 'tipo': 'acao', 'classe': 'rendavariavel', 'mercado': 'US'},
                'corretora': {'nome': 'Avenue Securities'},
                'quantidade': 10, 'preco_unitario': 195.50, 'valor_total': 1955.00,
                'taxas': 1.00, 'moeda': 'USD'
            },
            {
                'id': '4', 'data': '2024-11-20', 'tipo_operacao': 'venda',
                'ativo': {'ticker': 'VALE3', 'nome': 'Vale S.A.', 'tipo': 'acao', 'classe': 'rendavariavel', 'mercado': 'BR'},
                'corretora': {'nome': 'XP Investimentos'},
                'quantidade': 200, 'preco_unitario': 62.30, 'valor_total': 12460.00,
                'taxas': 8.00, 'moeda': 'BRL'
            },
            {
                'id': '5', 'data': '2024-11-15', 'tipo_operacao': 'compra',
                'ativo': {'ticker': 'BTC', 'nome': 'Bitcoin', 'tipo': 'cripto', 'classe': 'cripto', 'mercado': 'US'},
                'corretora': {'nome': 'Binance'},
                'quantidade': 0.05, 'preco_unitario': 42000.00, 'valor_total': 2100.00,
                'taxas': 10.50, 'moeda': 'USD'
            },
        ]

    total_compras = sum(1 for t in transacoes if t['tipo_operacao'] == 'compra')
    total_vendas = sum(1 for t in transacoes if t['tipo_operacao'] == 'venda')
    volume_total = sum(t.get('valor_total', 0) for t in transacoes)

    volume_acoes = sum(t.get('valor_total', 0) for t in transacoes if t.get('ativo', {}).get('tipo') in ['acao', 'stock'])
    volume_fii = sum(t.get('valor_total', 0) for t in transacoes if t.get('ativo', {}).get('tipo') in ['fii', 'reit'])
    volume_cripto = sum(t.get('valor_total', 0) for t in transacoes if t.get('ativo', {}).get('tipo') == 'cripto')
    volume_outros = sum(t.get('valor_total', 0) for t in transacoes if t.get('ativo', {}).get('tipo') not in ['acao', 'stock', 'fii', 'reit', 'cripto'])

    volume_compras = sum(t.get('valor_total', 0) for t in transacoes if t['tipo_operacao'] == 'compra')
    volume_vendas = sum(t.get('valor_total', 0) for t in transacoes if t['tipo_operacao'] == 'venda')

    stats = {
        'total': len(transacoes),
        'compras': total_compras,
        'vendas': total_vendas,
        'volume_total': volume_total,
        'volume_acoes': volume_acoes,
        'volume_fii': volume_fii,
        'volume_cripto': volume_cripto,
        'volume_outros': volume_outros,
        'volume_compras': volume_compras,
        'volume_vendas': volume_vendas
    }

    corretoras = [
        {'id': '1', 'nome': 'XP Investimentos'},
        {'id': '2', 'nome': 'Clear Corretora'},
        {'id': '3', 'nome': 'Avenue Securities'}
    ]

    tipos_ativo = [
        {'value': 'acao', 'label': 'Ação'},
        {'value': 'fii', 'label': 'FII'},
        {'value': 'reit', 'label': 'REIT'},
        {'value': 'bond', 'label': 'Bond'},
        {'value': 'etf', 'label': 'ETF'},
        {'value': 'cripto', 'label': 'Cripto'},
        {'value': 'outro', 'label': 'Outro'}
    ]

    classes_ativo = [
        {'value': 'rendavariavel', 'label': 'Renda Variável'},
        {'value': 'rendafixa', 'label': 'Renda Fixa'},
        {'value': 'cripto', 'label': 'Cripto'},
        {'value': 'hibrido', 'label': 'Híbrido'}
    ]

    mercados = [
        {'value': 'BR', 'label': 'Brasil 🇧🇷'},
        {'value': 'US', 'label': 'EUA 🇺🇸'},
        {'value': 'EUR', 'label': 'Europa 🇪🇺'}
    ]

    return render_template(
        'dashboard/transactions.html',
        transacoes=transacoes,
        stats=stats,
        corretoras=corretoras,
        tipos_ativo=tipos_ativo,
        classes_ativo=classes_ativo,
        mercados=mercados,
        filtros={
            'tipo': tipo_ativo,
            'classe': classe,
            'mercado': mercado,
            'corretora_id': corretora_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        },
        current_page=page,
        total_pages=1
    )


@bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def transactions_new():
    """M6.3 - Form Nova Transação"""
    if request.method == 'POST':
        try:
            data = {
                'tipo_operacao': request.form.get('tipo_operacao'),
                'ativo_id': request.form.get('ativo_id'),
                'corretora_id': request.form.get('corretora_id'),
                'data': request.form.get('data'),
                'quantidade': float(request.form.get('quantidade')),
                'preco_unitario': float(request.form.get('preco_unitario')),
                'taxas': float(request.form.get('taxas', 0)),
                'observacoes': request.form.get('observacoes', '')
            }

            token = session.get('accesstoken')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

            response = requests.post(
                f'{Config.BACKEND_API_URL}/api/transacoes',
                json=data, headers=headers, timeout=10
            )

            if response.status_code in [200, 201]:
                flash('✅ Transação registrada com sucesso!', 'success')
                return redirect(url_for('dashboard.transactions'))
            else:
                flash(f'❌ Erro ao registrar: {response.status_code}', 'error')
        except Exception as e:
            flash(f'❌ Erro: {str(e)}', 'error')

    return redirect(url_for('dashboard.transactions'))


# ========================================
# M6.4 PROVENTOS (DIVIDENDOS/JCP)
# ========================================

@bp.route('/dividends', methods=['GET'])
@login_required
def dividends():
    """M6.4 - Gestão de Proventos (Dividendos, JCP, Rendimentos)"""
    token = session.get('accesstoken')
    proventos = []

    ativo_id = request.args.get('ativo')
    corretora_id = request.args.get('corretora')
    tipo_provento = request.args.get('tipo')
    status = request.args.get('status')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    page = int(request.args.get('page', 1))

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'page': page, 'per_page': 20}

            if ativo_id:
                params['ativo_id'] = ativo_id
            if corretora_id:
                params['corretora_id'] = corretora_id
            if tipo_provento:
                params['tipo'] = tipo_provento
            if status:
                params['status'] = status
            if data_inicio:
                params['data_inicio'] = data_inicio
            if data_fim:
                params['data_fim'] = data_fim

            response = requests.get(
                f'{Config.BACKEND_API_URL}/api/proventos',
                headers=headers, params=params, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                proventos = result.get('data', {}).get('proventos', [])
        except Exception:
            pass

    if not proventos:
        proventos = [
            {
                'id': '1', 'tipo': 'dividendo', 'data_com': '2024-11-15', 'data_pagamento': '2024-12-05',
                'ativo': {'ticker': 'PETR4', 'nome': 'Petrobras', 'mercado': 'BR'},
                'valor_unitario': 1.45, 'quantidade': 100, 'valor_total': 145.00,
                'moeda': 'BRL', 'status': 'pago'
            },
            {
                'id': '2', 'tipo': 'jcp', 'data_com': '2024-10-20', 'data_pagamento': '2024-11-10',
                'ativo': {'ticker': 'VALE3', 'nome': 'Vale', 'mercado': 'BR'},
                'valor_unitario': 0.85, 'quantidade': 200, 'valor_total': 170.00,
                'moeda': 'BRL', 'status': 'pago'
            },
            {
                'id': '3', 'tipo': 'dividendo', 'data_com': '2024-11-01', 'data_pagamento': '2024-12-15',
                'ativo': {'ticker': 'MXRF11', 'nome': 'Maxi Renda', 'mercado': 'BR'},
                'valor_unitario': 0.95, 'quantidade': 50, 'valor_total': 47.50,
                'moeda': 'BRL', 'status': 'previsto'
            },
            {
                'id': '4', 'tipo': 'dividendo', 'data_com': '2024-09-15', 'data_pagamento': '2024-10-05',
                'ativo': {'ticker': 'AAPL', 'nome': 'Apple Inc', 'mercado': 'US'},
                'valor_unitario': 0.24, 'quantidade': 10, 'valor_total': 2.40,
                'moeda': 'USD', 'status': 'pago'
            },
            {
                'id': '5', 'tipo': 'rendimento', 'data_com': '2024-11-20', 'data_pagamento': '2024-12-20',
                'ativo': {'ticker': 'HGLG11', 'nome': 'CSHG Logistica', 'mercado': 'BR'},
                'valor_unitario': 1.12, 'quantidade': 80, 'valor_total': 89.60,
                'moeda': 'BRL', 'status': 'previsto'
            }
        ]

    total_recebido = sum(p.get('valor_total', 0) for p in proventos if p.get('status') == 'pago')
    total_previsto = sum(p.get('valor_total', 0) for p in proventos if p.get('status') == 'previsto')
    total_geral = sum(p.get('valor_total', 0) for p in proventos)

    stats = {
        'total': len(proventos),
        'recebido': total_recebido,
        'previsto': total_previsto,
        'total_geral': total_geral
    }

    timeline_dict = defaultdict(float)
    for p in proventos:
        if p.get('status') == 'pago':
            try:
                data_pag = p.get('data_pagamento', '')
                if data_pag:
                    dt = datetime.strptime(data_pag, '%Y-%m-%d')
                    mes_label = dt.strftime('%b/%y')
                    timeline_dict[mes_label] += p.get('valor_total', 0)
            except Exception:
                pass

    timeline_sorted = sorted(timeline_dict.items(), key=lambda x: datetime.strptime(x[0], '%b/%y'))
    dividends_timeline = [{'mes': mes, 'valor': round(valor, 2)} for mes, valor in timeline_sorted]

    ativos = [
        {'id': '1', 'ticker': 'PETR4', 'nome': 'Petrobras'},
        {'id': '2', 'ticker': 'VALE3', 'nome': 'Vale'},
        {'id': '3', 'ticker': 'MXRF11', 'nome': 'Maxi Renda'}
    ]

    corretoras = [
        {'id': '1', 'nome': 'XP Investimentos'},
        {'id': '2', 'nome': 'Clear Corretora'},
        {'id': '3', 'nome': 'Avenue Securities'}
    ]

    tipos_provento_list = [
        {'value': 'dividendo', 'label': 'Dividendo'},
        {'value': 'jcp', 'label': 'JCP'},
        {'value': 'rendimento', 'label': 'Rendimento'}
    ]

    return render_template(
        'dashboard/dividends.html',
        proventos=proventos,
        stats=stats,
        dividends_timeline=dividends_timeline,
        ativos=ativos,
        corretoras=corretoras,
        tipos_provento=tipos_provento_list,
        filtros={
            'ativo': ativo_id,
            'corretora': corretora_id,
            'tipo': tipo_provento,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        },
        current_page=page,
        total_pages=1
    )


# ========================================
# M7.3 ALERTAS - INTEGRAÇÃO COM BACKEND
# ========================================

@bp.route('/alerts', methods=['GET'])
@login_required
def alerts():
    """
    M7.3 - Lista de alertas consumindo API backend /api/alertas/
    """
    token = session.get('accesstoken')
    alertas = []

    filtros = {
        'tipo': request.args.get('tipo', ''),
        'status': request.args.get('status', ''),
        'ativo': request.args.get('ativo', '')
    }

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.get(
                f'{Config.BACKEND_API_URL}/api/alertas/',
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                alertas = data if isinstance(data, list) else data.get('data', [])
        except Exception as e:
            print(f"[M7.3] Erro ao buscar alertas API: {e}")

    alertas = alertas or []
    ativos = []

    return render_template(
        'dashboard/alerts.html',
        alertas=alertas,
        filtros=filtros,
        ativos=ativos
    )


@bp.route('/alerts/table', methods=['GET'])
@login_required
def alerts_table():
    """
    M7.3 - HTMX partial da tabela de alertas, consumindo /api/alertas/
    """
    token = session.get('accesstoken')
    alertas = []

    tipo_alerta = request.args.get('tipo')
    status_filtro = request.args.get('status')
    ativo_ticker = request.args.get('ativo')

    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.get(
                f'{Config.BACKEND_API_URL}/api/alertas/',
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                alertas = data if isinstance(data, list) else data.get('data', [])
        except Exception as e:
            print(f"[M7.3 HTMX] Erro ao buscar alertas API: {e}")

    alertas_filtrados = alertas or []

    if tipo_alerta:
        alertas_filtrados = [a for a in alertas_filtrados if a.get('tipo') == tipo_alerta]

    if status_filtro:
        ativo_bool = (status_filtro == 'ativo')
        alertas_filtrados = [a for a in alertas_filtrados if a.get('ativo') == ativo_bool]

    if ativo_ticker:
        alertas_filtrados = [a for a in alertas_filtrados if a.get('ticker') == ativo_ticker]

    print(f"[M7.3 HTMX] Filtros: tipo={tipo_alerta}, status={status_filtro}, ativo={ativo_ticker}")
    print(f"[M7.3 HTMX] Resultados: {len(alertas_filtrados)}/{len(alertas)} alertas")

    return render_template('components/alerts_table.html', alertas=alertas_filtrados)


@bp.route('/alerts/toggle/<alert_id>', methods=['POST'])
@login_required
def alerts_toggle(alert_id):
    """
    M7.3 - Ativar/Desativar alerta (Toggle) via API backend
    """
    try:
        token = session.get('accesstoken')
        headers = {'Authorization': f'Bearer {token}'}

        resp_get = requests.get(
            f'{Config.BACKEND_API_URL}/api/alertas/',
            headers=headers,
            timeout=5
        )
        alvo = None
        if resp_get.status_code == 200:
            data = resp_get.json()
            alertas = data if isinstance(data, list) else data.get('data', [])
            alvo = next((a for a in alertas if str(a.get('id')) == str(alert_id)), None)

        if not alvo:
            flash('Alerta não encontrado para toggle.', 'error')
            return redirect(url_for('dashboard.alerts'))

        novo_status = not alvo.get('ativo', True)

        resp_put = requests.put(
            f'{Config.BACKEND_API_URL}/api/alertas/{alert_id}',
            json={'ativo': novo_status},
            headers={**headers, 'Content-Type': 'application/json'},
            timeout=5
        )
        if resp_put.status_code in (200, 204):
            flash('✅ Status do alerta alterado com sucesso!', 'success')
        else:
            flash(f'❌ Erro ao alterar status ({resp_put.status_code})', 'error')

    except Exception as e:
        flash(f'Erro ao alterar status: {str(e)}', 'error')
        print(f"[ERROR] {e}")

    return redirect(url_for('dashboard.alerts'))


@bp.route('/alerts/delete/<alert_id>', methods=['POST'])
@login_required
def alerts_delete(alert_id):
    """
    M7.3 - Deletar alerta via API backend
    """
    try:
        token = session.get('accesstoken')
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.delete(
            f'{Config.BACKEND_API_URL}/api/alertas/{alert_id}',
            headers=headers,
            timeout=5
        )
        if resp.status_code in (200, 204):
            flash('✅ Alerta deletado com sucesso!', 'success')
        else:
            flash(f'❌ Erro ao deletar alerta ({resp.status_code})', 'error')

    except Exception as e:
        flash(f'Erro ao deletar alerta: {str(e)}', 'error')
        print(f"[ERROR] {e}")

    return redirect(url_for('dashboard.alerts'))


@bp.route('/alerts/edit/<alert_id>', methods=['GET', 'POST'])
@login_required
def alerts_edit(alert_id):
    """
    M7.3 - Editar alerta existente (ainda mock; futura integração com API PUT)
    """
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            flash(f'✅ Alerta "{nome}" atualizado com sucesso! (Mock - M7.3)', 'success')
            print(f"[M7.3] Edit alerta: {alert_id} → {nome}")
        except Exception as e:
            flash(f'Erro ao atualizar alerta: {str(e)}', 'error')
            print(f"[ERROR] {e}")
        return redirect(url_for('dashboard.alerts'))

    flash('Edição via modal em desenvolvimento (M7.3)', 'info')
    return redirect(url_for('dashboard.alerts'))


# ========================================
# PLACEHOLDERS M7
# ========================================

@bp.route('/assets')
@bp.route('/assets/<ticker>')
@bp.route('/reports')
@bp.route('/analytics')
@bp.route('/settings')
@login_required
def placeholder():
    flash('Em desenvolvimento - M7', 'info')
    return redirect(url_for('dashboard.buy_signals'))
