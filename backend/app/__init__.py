# -*- coding: utf-8 -*-
"""Exitus - Módulo 2 Backend API REST - Application Factory"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .database import init_db

def create_app(testing=False):
    """
    Factory para criar a aplicação Flask do Exitus Backend.
    
    Args:
        testing (bool): Modo de teste (configurações específicas)
    
    Returns:
        Flask: Aplicação Flask configurada
    """
    app = Flask(__name__)
    
    # Carregar configurações
    app.config.from_object(Config)
    
    # Configurações adicionais para JWT
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'super-secret-key-mudar-no-env')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 dias
    
    # Inicializar extensões
    jwt = JWTManager(app)
    cors = CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # Inicializar banco de dados
    init_db(app)
    
    # Health check básico (Módulo 1 + Módulo 2)
    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend",
            "status": "ok",
            "module": "2 - API REST"
        }
    
    # ⭐ Registrar blueprints
    # Blueprint de autenticação (Fase 2.1)
    from .blueprints.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Blueprint de usuários (Fase 2.2.1)
    from .blueprints.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    # Blueprint de corretoras (Fase 2.2.2)
    from .blueprints.corretoras.routes import bp as corretoras_bp
    app.register_blueprint(corretoras_bp)
    
    # Blueprint de ativos (Fase 2.2.3)
    from .blueprints.ativos.routes import bp as ativos_bp
    app.register_blueprint(ativos_bp)
    
    # Blueprint de transações (Fase 2.2.4)
    from .blueprints.transacoes.routes import bp as transacoes_bp
    app.register_blueprint(transacoes_bp)
    
    # Outros blueprints serão adicionados gradualmente nas próximas fases
    from .blueprints.posicoes.routes import bp as posicoes_bp
    app.register_blueprint(posicoes_bp)

    # Blueprint de proventos (Módulo 3 - Fase 2)
    from .blueprints.proventos.routes import bp as proventos_bp
    app.register_blueprint(proventos_bp)

    # Blueprint de movimentacoes (Módulo 3 - Fase 3)
    from .blueprints.movimentacoes.routes import bp as movimentacoes_bp
    app.register_blueprint(movimentacoes_bp)

    # Blueprint de eventos (Módulo 3 - Fase 4)
    from .blueprints.eventos.routes import bp as eventos_bp
    app.register_blueprint(eventos_bp)
    
    print("🚀 Exitus Backend Módulo 2 - Application Factory criada com sucesso!")
    print(f"📍 Environment: {app.config.get('FLASK_ENV')}")
    print(f"🔐 JWT Secret configurado: {'*' * 16}")
    print(f"🌐 CORS configurado para: http://localhost:8080")
    print(f"✅ Blueprints registrados: auth, usuarios, corretoras, ativos, transacoes")
    
    return app
