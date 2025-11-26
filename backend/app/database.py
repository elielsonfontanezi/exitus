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
        # Importa todos os models para que Alembic os detecte
        from app.models import (
            Usuario, UserRole,
            Corretora, TipoCorretora,
            Ativo, TipoAtivo, ClasseAtivo,
            Posicao,
            Transacao, TipoOperacao,
            Provento, TipoProvento,
            MovimentacaoCaixa, TipoMovimentacao,
            EventoCorporativo, TipoEventoCorporativo,
            FonteDados, TipoFonteDados,
            RegraFiscal, IncidenciaImposto,
            FeriadoMercado, TipoFeriado,
            LogAuditoria
        )
    
    return db
