# -*- coding: utf-8 -*-
"""
Exitus Frontend - Configuration
Módulo 5: Frontend Base + Autenticação
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações da aplicação Frontend"""
    
    # Backend API
    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'Exitus')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    
    # Session (necessário para autenticação M5)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Templates
    TEMPLATES_AUTO_RELOAD = True if FLASK_ENV == 'development' else False
