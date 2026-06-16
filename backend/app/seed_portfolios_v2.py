# -*- coding: utf-8 -*-
"""Seed para criar Portfolios iniciais"""
from app import create_app
from app.database import db
from app.models.usuario import Usuario
from app.models.portfolio import Portfolio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_portfolios():
    app = create_app()
    with app.app_context():
        # Pegar usuário admin
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            logger.error("Usuário admin não encontrado!")
            return

        # Verificar se já existe portfolio
        if Portfolio.query.filter_by(usuario_id=admin.id).first():
            logger.info("Portfolio já existe para admin.")
            return

        # Criar Portfolio Principal
        portfolio = Portfolio(
            usuario_id=admin.id,
            nome=f"Portfolio Principal - {admin.username}",
            descricao="Carteira principal de investimentos",
            objetivo="Crescimento",
            ativo=True
        )
        
        db.session.add(portfolio)
        db.session.commit()
        logger.info(f"✅ Portfolio criado com sucesso! ID: {portfolio.id}")

if __name__ == '__main__':
    seed_portfolios()
