"""Exitus Backend M7.1 - Application Factory COMPLETO"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database import init_db
from app.database import db

def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT + CORS
    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080"]}})

    # Inicializar DB
    init_db(app)

    # Health check
    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend",
            "status": "ok",
            "module": "M7.1 - Relatórios/Alerts/Projeções/Performance"
        }

    # Blueprints M2-M7.1 COMPLETO
    from .blueprints.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .blueprints.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)

    # M7.1 - RELATÓRIOS
    from .blueprints.relatorios_blueprint import relatorios_bp
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')

    # M7.1 - NOVOS BLUEPRINTS
    from .blueprints.alertas_blueprint import alertas_bp
    app.register_blueprint(alertas_bp)

    from .blueprints.projecoes_blueprint import projecoes_bp
    app.register_blueprint(projecoes_bp)

    from .blueprints.performance_blueprint import performance_bp
    app.register_blueprint(performance_bp)

    # M7.5 COTAÇÕES
    from .blueprints.cotacoes_blueprint import cotacoes_bp
    app.register_blueprint(cotacoes_bp, url_prefix='/api/cotacoes')

    print("✅ Exitus Backend M7.1 COMPLETO!")
    print("📍 Blueprints: auth+usuarios+relatorios+alertas+projecoes+performance+cotacoes (60+ total)")

    return app
