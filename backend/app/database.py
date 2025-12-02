# -*- coding: utf-8 -*-
"""Exitus - Database Configuration - SQLAlchemy + PostgreSQL"""

from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask.

    Args:
        app: Instância Flask
    """
    db.init_app(app)

    # Importar models DEPOIS de db.init_app para evitar circular imports
    with app.app_context():
        # Import APENAS do pacote - o __init__.py já importa todos os models
        # na ordem correta para resolver foreign keys
        import app.models

        # Criar todas as tabelas
        db.create_all()
        print("✅ Banco de dados inicializado e tabelas criadas!")
