# -*- coding: utf-8 -*-
"""Exitus Backend - Database Configuration"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instâncias globais
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Importa todos os models (apenas quando existirem)
        # COMENTADO até criarmos os models na Fase 2
        # from app.models import (
        #     usuario, corretora, ativo, posicao, transacao,
        #     provento, movimentacao_caixa, evento_corporativo,
        #     fonte_dados, regra_fiscal, feriado_mercado, log_auditoria
        # )
        pass
    
    return db
