# -*- coding: utf-8 -*-
"""
Análises Blueprint - Página de análises e relatórios
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('analises', __name__, url_prefix='/analises')

@bp.route('/', methods=['GET'])
@login_required
def index():
    """Página principal de análises"""
    from .auth import get_api_headers
    from flask import redirect, url_for
    
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do dashboard
    dashboard_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/portfolios/dashboard",
        headers=headers
    )
    
    # Se token inválido mesmo após refresh, logout
    if dashboard_response.status_code in [401, 403]:
        return redirect(url_for('auth.login'))
    
    dashboard_data = {}
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json().get('data', {})
    
    # Buscar proventos
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    proventos_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/proventos",
        headers=headers
    )
    
    if proventos_response.status_code in [401, 403]:
        return redirect(url_for('auth.login'))
    
    proventos = []
    if proventos_response.status_code == 200:
        proventos = proventos_response.json().get('data', {}).get('items', [])
    
    # Buscar transações recentes
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    transacoes_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/transacoes/recentes?limit=10",
        headers=headers
    )
    
    if transacoes_response.status_code in [401, 403]:
        return redirect(url_for('auth.login'))
    
    transacoes = []
    if transacoes_response.status_code == 200:
        data = transacoes_response.json().get('data', [])
        transacoes = list(data)[:10] if data else []
    
    return render_template('analises/index.html',
                         dashboard=dashboard_data,
                         proventos=proventos,
                         transacoes=transacoes)

@bp.route('/proventos', methods=['GET'])
@login_required
def proventos():
    """Análise de proventos"""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    # Buscar proventos com filtros
    ano = request.args.get('ano')
    tipo = request.args.get('tipo')
    
    params = {}
    if ano:
        params['ano'] = ano
    if tipo:
        params['tipo'] = tipo
    
    proventos_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/proventos",
        headers=headers,
        params=params
    )
    
    proventos = []
    if proventos_response.status_code == 200:
        proventos = proventos_response.json().get('data', {}).get('items', [])
    
    return render_template('analises/proventos.html', proventos=proventos)

@bp.route('/rentabilidade', methods=['GET'])
@login_required
def rentabilidade():
    """Análise de rentabilidade"""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do dashboard
    dashboard_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/portfolios/dashboard",
        headers=headers
    )
    
    dashboard_data = {}
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json().get('data', {})
    
    # Buscar evolução patrimonial
    evolucao_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/portfolios/evolucao?meses=12",
        headers=headers
    )
    
    evolucao = []
    if evolucao_response.status_code == 200:
        evolucao = evolucao_response.json().get('data', [])
    
    return render_template('analises/rentabilidade.html',
                         dashboard=dashboard_data,
                         evolucao=evolucao)

@bp.route('/impostos', methods=['GET'])
@login_required
def impostos():
    """Análise de impostos"""
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    # Buscar DARFs acumulados
        # Buscar DARFs acumulados
    darf_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/impostos/darf-acumulado",
        headers=headers
    )
    
    darf_acumulado = []
    if darf_response.status_code == 200:
        darf_acumulado = darf_response.json().get('data', [])
    
    # Buscar movimentações de caixa (pagamentos de imposto)
    movimentacoes_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/movimentacoes-caixa?tipo=pagamento_imposto",
        headers=headers
    )
    
    pagamentos = []
    if movimentacoes_response.status_code == 200:
        pagamentos = movimentacoes_response.json().get('data', {}).get('items', [])
    
    return render_template('analises/impostos.html',
                         darf_acumulado=darf_acumulado,
                         pagamentos=pagamentos)
