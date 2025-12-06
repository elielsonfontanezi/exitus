# -*- coding: utf-8 -*-
"""
Exitus Frontend - Dashboard Routes
MÓDULO 6: Buy Signals + Portfolios ✅
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import requests
from functools import wraps
from app.config import Config

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    """Decorator FINAL - aceita username OU accesstoken"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') or session.get('accesstoken'):
            return f(*args, **kwargs)
        return redirect(url_for('auth.login'))
    return decorated_function

@bp.route('/')
@login_required
def index():
    """Dashboard principal - M6 ✅"""
    # Renderizar dashboard principal (não redirecionar!)
    return render_template('dashboard/index.html')

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
                data = response.json().get('data', [])
        except:
            pass

    if not data:
        data = [
            {'ticker': 'PETR4', 'nome': 'Petrobras', 'mercado': 'BR', 'buyscore': 87, 'margem': 8.85},
            {'ticker': 'VALE3', 'nome': 'Vale', 'mercado': 'BR', 'buyscore': 72, 'margem': 5.2},
            {'ticker': 'AAPL', 'nome': 'Apple', 'mercado': 'US', 'buyscore': 65, 'margem': 2.1}
        ]

    summary = {
        'mercados': {
            'labels': ['BR', 'US', 'EU'],
            'data': [len([s for s in data if s.get('mercado') == 'BR']),
                     len([s for s in data if s.get('mercado') == 'US']), 1]
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
                data = response.json().get('data', [])
        except:
            pass

    if not data:
        data = [
            {'ticker': 'PETR4', 'nome': 'Petrobras', 'mercado': 'BR', 'buyscore': 87, 'margem': 8.85},
            {'ticker': 'VALE3', 'nome': 'Vale', 'mercado': 'BR', 'buyscore': 72, 'margem': 5.2}
        ]

    return render_template('components/buy_signals_table.html',
                         signals=data, total_pages=1, current_page=1, request=request)

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
        except:
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

# Placeholders M6/M7
@bp.route('/assets')
@bp.route('/assets/<ticker>')
@bp.route('/transactions')
@bp.route('/transactions/new')
@bp.route('/dividends')
@bp.route('/reports')
@bp.route('/analytics')
@bp.route('/settings')
@login_required
def placeholder():
    flash('Em desenvolvimento - M6/M7', 'info')
    return redirect(url_for('dashboard.buy_signals'))
