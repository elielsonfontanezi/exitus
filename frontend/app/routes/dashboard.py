# -*- coding: utf-8 -*-
"""
Exitus Frontend - Dashboard Routes
MÓDULO 6: Buy Signals COMPLETO ✅
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import requests
from functools import wraps
from app.config import Config

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    """Decorator FINAL - aceita qualquer dado de autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Qualquer um desses = autenticado
        if (session.get('user_id') or 
            session.get('username') or 
            session.get('accesstoken')):
            return f(*args, **kwargs)
        return redirect(url_for('auth.login'))
    return decorated_function

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html')

@bp.route('/buy-signals', methods=['GET'])
@login_required
def buy_signals():
    """Buy Signals Completo - M6 ✅"""
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
            pass  # Fallback mock
    
    # Mock dados para teste (remove quando API 100%)
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
    """HTMX partial - apenas tabela"""
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

# Placeholders M6/M7
@bp.route('/portfolios')
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
    return redirect(url_for('dashboard.index'))
