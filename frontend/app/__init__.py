# -*- coding: utf-8 -*-
"""
Exitus Frontend - Application Factory
Módulo 5: Frontend Base + Autenticação
"""

from flask import Flask
from .config import Config


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Registrar blueprints
    from .routes import auth, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)

    # Health check
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-frontend',
            'env': app.config.get('FLASK_ENV', 'unknown')
        }, 200

    # Redirect root to dashboard or login
    @app.route('/')
    def index():
        from flask import session, redirect, url_for
        if session.get('user_id'):
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Adicionar funções ao contexto Jinja2
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now}
    
    return app
