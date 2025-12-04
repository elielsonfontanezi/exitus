# -*- coding: utf-8 -*-
"""
Exitus Frontend - Dashboard Routes
Módulo 5: Frontend Base + Autenticação
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
import requests

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def login_required(f):
    """Decorator para rotas que exigem autenticação"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Você precisa fazer login para acessar esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
def index():
    """Dashboard principal com Buy Signals"""
    return render_template('dashboard/index.html')


@bp.route('/buy-signals')
@login_required
def buy_signals():
    """Página dedicada aos Buy Signals (Módulo 6)"""
    flash('Funcionalidade completa em desenvolvimento - Módulo 6', 'info')
    return render_template('dashboard/index.html')


@bp.route('/portfolios')
@login_required
def portfolios():
    """Página de carteiras (Módulo 6)"""
    flash('Funcionalidade em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/assets')
@login_required
def assets():
    """Página de ativos (Módulo 6)"""
    flash('Funcionalidade em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/assets/<ticker>')
@login_required
def asset_detail(ticker):
    """Detalhes de um ativo específico (Módulo 6)"""
    flash(f'Detalhes do ativo {ticker} em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/transactions')
@login_required
def transactions():
    """Página de transações (Módulo 6)"""
    flash('Funcionalidade em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/transactions/new')
@login_required
def new_transaction():
    """Nova transação (Módulo 6)"""
    flash('Funcionalidade em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/dividends')
@login_required
def dividends():
    """Página de proventos (Módulo 6)"""
    flash('Funcionalidade em desenvolvimento - Módulo 6', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/reports')
@login_required
def reports():
    """Página de relatórios (Módulo 7)"""
    flash('Funcionalidade em desenvolvimento - Módulo 7', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/analytics')
@login_required
def analytics():
    """Página de análises (Módulo 7)"""
    flash('Funcionalidade em desenvolvimento - Módulo 7', 'info')
    return redirect(url_for('dashboard.index'))


@bp.route('/settings')
@login_required
def settings():
    """Página de configurações (Módulo 7)"""
    flash('Funcionalidade em desenvolvimento - Módulo 7', 'info')
    return redirect(url_for('dashboard.index'))
