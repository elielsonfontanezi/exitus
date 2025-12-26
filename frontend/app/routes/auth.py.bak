# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from app.config import Config
from functools import wraps

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

            # Decodificar JWT para extrair user_id
            import jwt
            access_token = user_data.get('access_token')
            
            if access_token:
                try:
                    # Decodificar sem verificar assinatura (só precisamos do payload)
                    payload = jwt.decode(access_token, options={"verify_signature": False})
                    
                    session['user_id'] = payload.get('sub')  # user_id está no 'sub'
                    session['username'] = username  # Usar o username do form
                    session['role'] = payload.get('role', 'user')
                    session['access_token'] = access_token
                    session.permanent = True
                    
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

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
