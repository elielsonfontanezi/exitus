# -*- coding: utf-8 -*-
"""
Exitus Frontend - Application Factory
"""

from flask import Flask, render_template_string

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Rota inicial
    @app.route('/')
    def index():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Exitus - Sistema de Investimentos</title>
        </head>
        <body>
            <h1>Exitus - Sistema de Controle e Análise de Investimentos</h1>
            <p>Frontend funcionando corretamente!</p>
        </body>
        </html>
        """
        return render_template_string(html)

    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'exitus-frontend'}, 200

    return app
