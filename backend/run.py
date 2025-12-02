#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exitus Backend - Entry Point"""

from app import create_app
import os

# Criar a aplicação Flask (já inicializa o banco internamente)
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.getenv('FLASK_ENV') == 'development'))
