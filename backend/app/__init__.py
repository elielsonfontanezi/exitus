# -*- coding: utf-8 -*-
"""
Exitus Backend - Application Factory
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Habilita CORS
    CORS(app)

    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'exitus-backend'}, 200

    return app
