#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exitus Backend - Entry Point"""

from app import create_app
from app.database import init_db
import os

# Criar a aplicação Flask
app = create_app()

# Inicializar o banco de dados com a aplicação
init_db(app)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.getenv('FLASK_ENV') == 'development'))
