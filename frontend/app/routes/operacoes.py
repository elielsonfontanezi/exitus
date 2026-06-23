# -*- coding: utf-8 -*-
"""
Operações Blueprint - Páginas de Compra, Venda e Depósito
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from app.config import Config
from .auth import login_required, get_api_headers

bp = Blueprint('operacoes', __name__, url_prefix='/operacoes')

@bp.route('/', methods=['GET'])
@login_required
def operacoes():
    """Operações de ativos (compra/venda) — Alpine.js API-driven"""
    return render_template('operacoes/operacoes_v2.html')

@bp.route('/compra', methods=['GET'])
@login_required
def compra():
    """Rota legada - redireciona para /operacoes"""
    return redirect(url_for('operacoes.operacoes'))

@bp.route('/venda', methods=['GET', 'POST'])
@login_required
def venda():
    """Página de venda de ativos - redireciona para /operacoes?venda=true"""
    if request.method == 'POST':
        # Processar formulário de venda
        ativo_id = request.form.get('ativo_id')
        quantidade = request.form.get('quantidade')
        preco = request.form.get('preco')
        corretora_id = request.form.get('corretora_id')
        
        # TODO: Validar e submeter para API
        flash('Operação de venda registrada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # Redirecionar para a página de operações com parâmetro venda=true
    return redirect(url_for('operacoes.operacoes', venda='true'))

@bp.route('/historico')
@login_required
def historico():
    """Histórico de transações — API: GET /api/transacoes (client-side via Alpine.js)"""
    return render_template('operacoes/historico.html')


@bp.route('/deposito', methods=['GET', 'POST'])
@login_required
def deposito():
    """Página de depósito em conta"""
    if request.method == 'POST':
        # Processar formulário de depósito
        valor = request.form.get('valor')
        moeda = request.form.get('moeda', 'BRL')
        corretora_id = request.form.get('corretora_id')
        descricao = request.form.get('descricao', 'Depósito')
        
        # TODO: Validar e submeter para API
        flash('Depósito registrado com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # Buscar corretoras
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    corretoras_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/corretoras",
        headers=headers
    )
    
    corretoras = []
    if corretoras_response.status_code == 200:
        corretoras = corretoras_response.json().get('data', [])
    
    return render_template('operacoes/deposito.html', 
                         corretoras=corretoras)
