#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed: Portfolio Padrão
Cria um portfolio inicial para cada usuário existente.
Data: 18/12/2025
"""
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db
from app.models.usuario import Usuario
from app.models.portfolio import Portfolio
from sqlalchemy import text
import uuid


def seed_portfolios():
    """Cria portfolio padrão para todos os usuários."""
    app = create_app()

    with app.app_context():
        print("🚀 Iniciando seed de portfolios...")
        print("")

        # 1. Buscar todos os usuários
        usuarios = Usuario.query.all()

        if not usuarios:
            print("⚠️  Nenhum usuário encontrado no banco.")
            print("   Execute o seed de usuários primeiro.")
            return

        print(f"📊 Total de usuários encontrados: {len(usuarios)}")
        print("")

        portfolios_criados = 0

        for usuario in usuarios:
            # Verificar se usuário já tem portfolio
            portfolio_existente = Portfolio.query.filter_by(usuario_id=usuario.id).first()

            if portfolio_existente:
                print(f"⏭️  Usuário '{usuario.username}' já possui portfolio: '{portfolio_existente.nome}'")
                continue

            # Criar portfolio padrão
            portfolio = Portfolio(
                id=uuid.uuid4(),
                usuario_id=usuario.id,
                nome=f"Portfolio Principal - {usuario.username}",
                descricao=f"Portfolio padrão criado automaticamente para {usuario.nome_completo or usuario.username}",
                objetivo="Crescimento",
                ativo=True,
                valor_inicial=None,  # Usuário define depois
                percentual_alocacao_target=None  # Usuário define depois
            )

            db.session.add(portfolio)
            portfolios_criados += 1

            print(f"✅ Portfolio criado: '{portfolio.nome}' (ID: {portfolio.id})")

        # Commit
        if portfolios_criados > 0:
            try:
                db.session.commit()
                print("")
                print("=" * 60)
                print(f"✅ SEED CONCLUÍDO!")
                print(f"   Total de portfolios criados: {portfolios_criados}")
                print("=" * 60)
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao salvar portfolios: {str(e)}")
        else:
            print("")
            print("ℹ️  Nenhum portfolio novo foi criado (todos os usuários já possuem).")


if __name__ == '__main__':
    seed_portfolios()
