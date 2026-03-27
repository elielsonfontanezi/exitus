# backend/app/database.py
# -*- coding: utf-8 -*-
"""Exitus - Database Configuration - SQLAlchemy + PostgreSQL + Migrate"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <--- IMPORTANTE

# Instância global do SQLAlchemy
db = SQLAlchemy()
migrate = Migrate() # <--- Instância global do Migrate

def init_db(app):
    """
    Inicializa o banco de dados e migrações com a aplicação Flask.

    Args:
        app: Instância Flask
    """
    db.init_app(app)
    migrate.init_app(app, db) # <--- Inicialização do Migrate

    # Importar models DEPOIS de db.init_app para evitar circular imports
    with app.app_context():
        # Import APENAS do pacote - o __init__.py já importa todos os models
        # na ordem correta para resolver foreign keys
        import app.models

        # db.create_all() # Manter comentado, usamos migrations agora
        print("✅ Banco de dados inicializado e tabelas verificadas!")
