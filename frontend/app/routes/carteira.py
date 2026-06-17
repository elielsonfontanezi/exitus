# -*- coding: utf-8 -*-
"""
Exitus Frontend - Blueprint Carteira
Rotas: /carteira/posicoes, /carteira/movimentacoes
Fase 3 — Telas novas usando base_interna.html
"""
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('carteira', __name__, url_prefix='/carteira')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username') and not session.get('access_token'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/posicoes')
@login_required
def posicoes():
    """Carteira — Minhas Posições (API: GET /api/posicoes + /api/posicoes/resumo)"""
    return render_template('carteira/posicoes.html')


@bp.route('/movimentacoes')
@login_required
def movimentacoes():
    """Carteira — Movimentações de Caixa (API: GET /api/movimentacoes + /api/carteira/saldo-caixa)"""
    return render_template('carteira/movimentacoes.html')
