#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exitus Frontend - Entry Point
Inicia o servidor Flask do frontend
"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
