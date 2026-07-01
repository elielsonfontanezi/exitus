# -*- coding: utf-8 -*-
"""
Ferramentas Blueprint - Sprint 8
Rotas: /ferramentas/comparador, /ferramentas/calculadora-ir,
        /ferramentas/simulador, /ferramentas/screener
"""

from flask import Blueprint, render_template, request, redirect, url_for
import requests
from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('ferramentas', __name__, url_prefix='/ferramentas')


@bp.route('/comparador', methods=['GET'])
@login_required
def comparador():
    """Comparador de Ativos — Alpine.js API-driven"""
    return render_template('ferramentas/comparador_v2.html')


@bp.route('/calculadora-ir', methods=['GET'])
@login_required
def calculadora_ir():
    """Calculadora IR — Alpine.js API-driven"""
    return render_template('ferramentas/calculadora_ir_v2.html')


@bp.route('/simulador', methods=['GET'])
@login_required
def simulador():
    """Alias — redireciona para projeções patrimoniais (NEW-01)"""
    return redirect(url_for('analises.projecoes_patrimonio'))


@bp.route('/reconciliacao')
@login_required
def reconciliacao():
    """Painel de Reconciliação — APIs: GET /api/reconciliacao/* (client-side via Alpine.js)"""
    return render_template('ferramentas/reconciliacao.html')


@bp.route('/screener', methods=['GET'])
@login_required
def screener():
    """Screener de Ativos — Alpine.js API-driven"""
    return render_template('ferramentas/screener_v2.html')


@bp.route('/cotacoes', methods=['GET'])
@login_required
def cotacoes_saude():
    """Saúde das Cotações — APIs: GET /api/cotacoes/health, /anomalias"""
    return render_template('ferramentas/cotacoes_v2.html')


@bp.route('/preco-teto', methods=['GET'])
@login_required
def preco_teto():
    """Calculadora Preço Teto — APIs: GET /api/calculos/preco_teto/<ticker>, /fii/<ticker> — NEW-11"""
    return render_template('ferramentas/preco_teto_v2.html')
