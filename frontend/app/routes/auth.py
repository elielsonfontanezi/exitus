# -*- coding: utf-8 -*-
"""
Exitus Frontend - Authentication Routes
Módulo 5: Frontend Base + Autenticação
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import requests
import json

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Se já está logado, redireciona para dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # POST - processar login via backend API
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Chamar API de login do backend
        backend_url = current_app.config['BACKEND_API_URL']
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json={'email': email, 'password': password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Salvar dados na sessão
            session['user_id'] = data.get('user_id')
            session['user_name'] = data.get('name')
            session['user_email'] = data.get('email')
            session['access_token'] = data.get('access_token')
            session.permanent = True
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('E-mail ou senha inválidos', 'error')
            
    except requests.exceptions.RequestException as e:
        flash(f'Erro ao conectar com o servidor: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')
    
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    # Se já está logado, redireciona para dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    # POST - processar registro via backend API
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validação básica
        if password != password_confirm:
            flash('As senhas não coincidem', 'error')
            return redirect(url_for('auth.register'))
        
        # Chamar API de registro do backend
        backend_url = current_app.config['BACKEND_API_URL']
        response = requests.post(
            f"{backend_url}/api/auth/register",
            json={
                'nome': nome,
                'email': email,
                'password': password
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        else:
            data = response.json()
            flash(data.get('message', 'Erro ao criar conta'), 'error')
            
    except requests.exceptions.RequestException as e:
        flash(f'Erro ao conectar com o servidor: {str(e)}', 'error')
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')
    
    return redirect(url_for('auth.register'))


@bp.route('/profile')
def profile():
    """Página de perfil do usuário"""
    # Verificar se está logado
    if not session.get('user_id'):
        flash('Você precisa fazer login', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/profile.html')


@bp.route('/logout')
def logout():
    """Logout do usuário"""
    # Limpar sessão
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password')
def forgot_password():
    """Página de recuperação de senha (placeholder)"""
    flash('Funcionalidade em desenvolvimento - Módulo 7', 'info')
    return redirect(url_for('auth.login'))
