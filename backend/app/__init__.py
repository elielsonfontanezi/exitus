# -*- coding: utf-8 -*-
"""
Exitus Backend M7.3 - Application Factory (M7.2 Services + M7.3 Blueprints Preparado)
"""

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
    CORS(app, resources={"/*": {"origins": "http://localhost:8080"}})
    
    # Inicializar DB
    init_db(app)
    
    # Health check
    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend", 
            "status": "ok",
            "module": "M7.3 - Services OK + Blueprints Preparando"
        }
    
    # M1-M6: Blueprints existentes (estrutura atual)
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
    
    from .blueprints.posicoes.routes import bp as posicoes_bp
    app.register_blueprint(posicoes_bp)
    
    from .blueprints.proventos.routes import bp as proventos_bp
    app.register_blueprint(proventos_bp)
    
    # M7.5: Cotações (estrutura atual - arquivo único)
    from .blueprints.cotacoes_blueprint import cotacoes_bp
    app.register_blueprint(cotacoes_bp, url_prefix='/api/cotacoes')
    
    # M7.1-M7.2: Blueprints existentes (arquivos únicos)
    from .blueprints.relatorios_blueprint import relatorios_bp
    app.register_blueprint(relatorios_bp)
    
    from .blueprints.alertas_blueprint import alertas_bp
    app.register_blueprint(alertas_bp)
    
    from .blueprints.projecoes_blueprint import projecoes_bp
    app.register_blueprint(projecoes_bp) 
    
    from .blueprints.performance_blueprint import performance_bp
    app.register_blueprint(performance_bp)
    
    print("✅ Exitus Backend M7.3 PRONTO!")
    print("📍 Blueprints M1-M7.3: 60+ endpoints operacionais")
    print("🚀 Services M7.2: Relatorio/Alerta/Projecao/Analise (29 métodos)")
    
    return app
