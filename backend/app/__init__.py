"""Exitus Backend - Application Factory"""
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
            "module": "2 - API REST"
        }
    
    # Blueprints existentes (M2-M7)
    from .blueprints.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from .blueprints.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    from .blueprints.relatorios_blueprint import relatorios_bp
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
    
    # M7.5 COTAÇÕES LIVE
    from .blueprints.cotacoes_blueprint import cotacoes_bp
    app.register_blueprint(cotacoes_bp, url_prefix='/api/cotacoes')
    
    print("✅ Exitus Backend M7.5 COMPLETO!")
    print("📍 Blueprints: auth+usuarios+relatorios+cotacoes (52 total)")
    
    return app
