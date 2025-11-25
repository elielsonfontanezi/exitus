# -*- coding: utf-8 -*-
"""Exitus Backend - Application Factory"""

from flask import Flask
from flask_cors import CORS
from .config import Config


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Habilita CORS
    CORS(app)

    # Health check route
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-backend',
            'env': app.config.get('FLASK_ENV', 'unknown')
        }, 200

    return app
