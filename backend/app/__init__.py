"""Exitus - Módulo 2 Backend API REST - Application Factory"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

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
    
    # Health check básico (Módulo 1 + Módulo 2)
    @app.route('/health')
    def health():
        return {
            "env": app.config.get('FLASK_ENV', 'development'),
            "service": "exitus-backend",
            "status": "ok",
            "module": "2 - API REST"
        }
    
    # Registrar blueprints (serão adicionados gradualmente)
    # from .blueprints.auth.routes import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api')
    
    print("🚀 Exitus Backend Módulo 2 - Application Factory criada com sucesso!")
    print(f"📍 Environment: {app.config.get('FLASK_ENV')}")
    print(f"🔐 JWT Secret configurado: {'*' * 16}")
    print(f"🌐 CORS configurado para: http://localhost:8080")
    
    return app
