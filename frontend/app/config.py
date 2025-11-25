# -*- coding: utf-8 -*-
"""Exitus Frontend - Configuration"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações da aplicação"""

    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
