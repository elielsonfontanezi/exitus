# -*- coding: utf-8 -*-
"""
Exitus Backend M3.3 - Application Factory (Eventos Corporativos)
"""
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database import init_db
from app.database import db
from decimal import Decimal
import json

class DecimalJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json = DecimalJSONProvider(app)
    jwt = JWTManager(app)
    CORS(app, resources={"/*": {"origins": "http://localhost:8080"}})
    init_db(app)

    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend",
            "status": "ok",
            "module": "M3.3 - Eventos Corporativos ✅"
        }

    # Core
    from .blueprints.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)
    from .blueprints.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    from .blueprints.corretoras.routes import bp as corretoras_bp
    app.register_blueprint(corretoras_bp)
    from .blueprints.ativos.routes import bp as ativos_bp
    app.register_blueprint(ativos_bp)
    from .blueprints.transacoes.routes import bp as transacoes_bp
    app.register_blueprint(transacoes_bp)

    # M3
    from .blueprints.posicao_blueprint import posicao_bp
    app.register_blueprint(posicao_bp)
    from .blueprints.provento_blueprint import provento_bp
    app.register_blueprint(provento_bp)
    from .blueprints.movimentacao_blueprint import movimentacao_bp
    app.register_blueprint(movimentacao_bp)
    from .blueprints.evento_corporativo_blueprint import evento_bp
    app.register_blueprint(evento_bp)

    # M7 Legacy/Future
    from .blueprints.cotacoes_blueprint import cotacoes_bp
    app.register_blueprint(cotacoes_bp, url_prefix='/api/cotacoes')
    
    try:
        from .blueprints.relatorios_blueprint import relatorios_bp
        app.register_blueprint(relatorios_bp)
    except ImportError: pass
    try:
        from .blueprints.alertas_blueprint import alertas_bp
        app.register_blueprint(alertas_bp)
    except ImportError: pass
    try:
        from .blueprints.projecoes_blueprint import projecoes_bp
        app.register_blueprint(projecoes_bp)
    except ImportError: pass
    try:
        from .blueprints.performance_blueprint import performance_bp
        app.register_blueprint(performance_bp)
    except ImportError: pass
    try:
        from .blueprints.m7_portfolio import bp_m7
        app.register_blueprint(bp_m7)
    except ImportError: pass

    return app
