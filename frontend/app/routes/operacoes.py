# -*- coding: utf-8 -*-
"""
Operações Blueprint - Páginas de Compra, Venda e Depósito
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from app.config import Config
from .auth import login_required

bp = Blueprint('operacoes', __name__, url_prefix='/operacoes')

@bp.route('/compra', methods=['GET'])
@login_required
def compra():
    """Página de compra de ativos (integração via API REST no frontend)"""
    headers = {'Authorization': f"Bearer {session.get('access_token')}"}
    
    # Buscar corretoras para popular select
    corretoras_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/corretoras",
        headers=headers
    )
    
    corretoras = []
    if corretoras_response.status_code == 200:
        corretoras = corretoras_response.json().get('data', [])
    
    return render_template('operacoes/compra.html', corretoras=corretoras)

@bp.route('/venda', methods=['GET', 'POST'])
@login_required
def venda():
    """Página de venda de ativos"""
    if request.method == 'POST':
        # Processar formulário de venda
        ativo_id = request.form.get('ativo_id')
        quantidade = request.form.get('quantidade')
        preco = request.form.get('preco')
        corretora_id = request.form.get('corretora_id')
        
        # TODO: Validar e submeter para API
        flash('Operação de venda registrada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # Buscar posições do usuário
    headers = {'Authorization': f"Bearer {session.get('access_token')}"}
    
    posicoes_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/posicoes",
        headers=headers
    )
    
    posicoes = []
    if posicoes_response.status_code == 200:
        posicoes = posicoes_response.json().get('data', {}).get('posicoes', [])
    
    # Buscar corretoras
    corretoras_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/corretoras",
        headers=headers
    )
    
    corretoras = []
    if corretoras_response.status_code == 200:
        corretoras = corretoras_response.json().get('data', [])
    
    return render_template('operacoes/venda.html', 
                         posicoes=posicoes, 
                         corretoras=corretoras)

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
    headers = {'Authorization': f"Bearer {session.get('access_token')}"}
    
    corretoras_response = requests.get(
        f"{Config.BACKEND_API_URL}/api/corretoras",
        headers=headers
    )
    
    corretoras = []
    if corretoras_response.status_code == 200:
        corretoras = corretoras_response.json().get('data', [])
    
    return render_template('operacoes/deposito.html', 
                         corretoras=corretoras)
