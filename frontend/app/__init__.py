# -*- coding: utf-8 -*-
"""Exitus Frontend - Application Factory"""

from flask import Flask, render_template_string
from .config import Config


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Rota inicial simples (será substituída em módulos futuros)
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

    # Health check
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-frontend',
            'env': app.config.get('FLASK_ENV', 'unknown')
        }, 200

    return app
