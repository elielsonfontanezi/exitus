# -*- coding: utf-8 -*-
"""
Exitus Frontend - Rotas Admin
Dashboard administrativo para gestão de assessoras
"""

from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def require_admin(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/assessoras')
@require_admin
def assessoras_list():
    """Lista todas as assessoras (paginado)"""
    return render_template('admin/assessoras_list.html')


@admin_bp.route('/assessoras/nova')
@require_admin
def assessoras_create():
    """Formulário de criação de assessora"""
    return render_template('admin/assessoras_form.html', mode='create')


@admin_bp.route('/assessoras/<assessora_id>/editar')
@require_admin
def assessoras_edit(assessora_id):
    """Formulário de edição de assessora"""
    return render_template('admin/assessoras_form.html', mode='edit', assessora_id=assessora_id)


@admin_bp.route('/assessoras/<assessora_id>/metricas')
@require_admin
def assessoras_stats(assessora_id):
    """Dashboard de métricas da assessora"""
    return render_template('admin/assessoras_stats.html', assessora_id=assessora_id)
