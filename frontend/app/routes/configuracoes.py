# -*- coding: utf-8 -*-
"""
Exitus Frontend - Blueprint Configurações
Rotas: /configuracoes/perfil, /configuracoes/corretoras, /configuracoes/fontes-dados
Fase 3 — Telas novas usando base_interna.html
"""
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('configuracoes', __name__, url_prefix='/configuracoes')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username') and not session.get('access_token'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/perfil')
@login_required
def perfil():
    """Configurações — Meu Perfil (API: GET /api/auth/me)"""
    return render_template('configuracoes/perfil.html')


@bp.route('/corretoras')
@login_required
def corretoras():
    """Configurações — Minhas Corretoras (API: GET /api/corretoras)"""
    return render_template('configuracoes/corretoras.html')


@bp.route('/fontes-dados')
@login_required
def fontes_dados():
    """Configurações — Fontes de Dados (API: GET /api/fontes-dados)"""
    return render_template('configuracoes/fontes_dados_v2.html')
