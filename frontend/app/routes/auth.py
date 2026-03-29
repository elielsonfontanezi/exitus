# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from app.config import Config
from functools import wraps
from datetime import datetime, timedelta
import jwt

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aceitar tanto form data quanto JSON
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f'{Config.BACKEND_API_URL}/api/auth/login',
            json={'username': username, 'password': password},
            headers=headers, timeout=10
        )
        
        if response.status_code == 200:
            api_data = response.json()
            user_data = api_data.get('data', {})

            access_token = user_data.get('access_token')
            refresh_token = user_data.get('refresh_token')
            expires_in = user_data.get('expires_in', 3600)  # Default 1 hora
            
            if access_token:
                try:
                    # Decodificar sem verificar assinatura (só precisamos do payload)
                    payload = jwt.decode(access_token, options={"verify_signature": False})
                    
                    # Calcular quando o token expira
                    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    session['user_id'] = payload.get('sub')  # user_id está no 'sub'
                    session['username'] = username
                    session['role'] = payload.get('role', 'user')
                    session['access_token'] = access_token
                    session['refresh_token'] = refresh_token
                    session['expires_at'] = expires_at.isoformat()
                    session.permanent = True
                    
                    # Se for requisição AJAX (JavaScript), retornar JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': True,
                            'token': access_token,
                            'user': {
                                'id': payload.get('sub'),
                                'username': username,
                                'role': payload.get('role', 'user')
                            },
                            'redirect': url_for('dashboard.index')
                        })
                    
                    flash('Login OK!', 'success')
                    return redirect(url_for('dashboard.index'))
                except Exception as e:
                    flash(f'Erro ao processar token: {str(e)}', 'error')
            else:
                flash('Token não recebido do backend', 'error')
        else:
            flash('Login falhou', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        flash('Registro em M7', 'info')
    return render_template('auth/register.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

def get_api_headers():
    """
    Retorna headers com token válido. Renova automaticamente se expirado.
    Retorna None se não conseguir renovar.
    """
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    expires_at_str = session.get('expires_at')
    
    if not access_token:
        return None
    
    # Verificar se o token ainda é válido
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.utcnow() < expires_at - timedelta(minutes=5):  # Renova 5 min antes
                return {'Authorization': f'Bearer {access_token}'}
        except (ValueError, TypeError):
            pass  # Se não conseguir parse, tenta renovar
    
    # Token expirado ou próximo de expirar, tentar renovar
    if refresh_token:
        try:
            response = requests.post(
                f'{Config.BACKEND_API_URL}/api/auth/refresh',
                json={'refresh_token': refresh_token},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                new_access = data.get('access_token')
                new_refresh = data.get('refresh_token')
                expires_in = data.get('expires_in', 3600)
                
                if new_access:
                    # Atualizar sessão
                    session['access_token'] = new_access
                    if new_refresh:
                        session['refresh_token'] = new_refresh
                    
                    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    session['expires_at'] = expires_at.isoformat()
                    
                    return {'Authorization': f'Bearer {new_access}'}
        except Exception:
            pass  # Falha silenciosa, vai retornar None
    
    # Não conseguiu renovar, limpar sessão
    session.clear()
    return None

@bp.route('/check-session', methods=['GET'])
def check_session():
    """Verifica se a sessão ainda é válida e tenta renovar o token se necessário."""
    if not session.get('user_id'):
        return jsonify({'valid': False})
    headers = get_api_headers()
    if not headers:
        return jsonify({'valid': False})
    return jsonify({'valid': True})


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
