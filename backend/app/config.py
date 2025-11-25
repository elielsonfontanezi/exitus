# -*- coding: utf-8 -*-
"""Exitus Backend - Configuration"""

import os
from dotenv import load_dotenv

# Carrega .env se existir
load_dotenv()

class Config:
    """Configurações da aplicação"""

    # Database
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'exitus')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'exitus123')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'exitusdb')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
