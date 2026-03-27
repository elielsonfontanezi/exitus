# -- coding: utf-8 --
# Exitus - Seed de Usuários — Popular tabela usuario com dados iniciais

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app import create_app
from app.database import db
from app.models import Usuario, UserRole
from datetime import datetime


def seed_usuarios():
    """Cria usuários iniciais do sistema."""
    app = create_app()
    with app.app_context():
        print('=' * 50)
        print('SEED — Criando Usuários Iniciais')
        print('=' * 50)

        count = Usuario.query.count()
        if count > 0:
            print(f'Já existem {count} usuários cadastrados.')
            resposta = input('Deseja recriar os usuários? (s/N) ').lower()
            if resposta != 's':
                print('Seed cancelado pelo usuário.')
                return
            Usuario.query.delete()
            db.session.commit()
            print('Usuários anteriores removidos.')

        # ----------------------------------------------------------------
        # EXITUS-SEEDS-002 — senhas corrigidas para senha123 (24/02/2026)
        # Antes: admin123 / user123 / viewer123
        # Depois: senha123 (padrão único de desenvolvimento)
        # ----------------------------------------------------------------
        usuarios = [
            {
                'username': 'admin',
                'email': 'admin@exitus.com',
                'password': 'senha123',          # ← corrigido
                'nomecompleto': 'Administrador do Sistema',
                'role': UserRole.ADMIN,
                'ativo': True,
            },
            {
                'username': 'joao.silva',
                'email': 'joao.silva@example.com',
                'password': 'senha123',          # ← corrigido
                'nomecompleto': 'João Silva',
                'role': UserRole.USER,
                'ativo': True,
            },
            {
                'username': 'maria.santos',
                'email': 'maria.santos@example.com',
                'password': 'senha123',          # ← corrigido
                'nomecompleto': 'Maria Santos',
                'role': UserRole.USER,
                'ativo': True,
            },
            {
                'username': 'viewer',
                'email': 'viewer@exitus.com',
                'password': 'senha123',          # ← corrigido
                'nomecompleto': 'Usuário Visualizador',
                'role': UserRole.READONLY,
                'ativo': True,
            },
        ]

        created_users = []
        for userdata in usuarios:
            user = Usuario(
                username=userdata['username'],
                email=userdata['email'],
                nomecompleto=userdata.get('nomecompleto'),
                role=userdata['role'],
                ativo=userdata['ativo'],
            )
            user.set_password(userdata['password'])
            db.session.add(user)
            created_users.append(user)
            print(f"  Usuário criado: {user.username} [{user.role.value}] - {user.email}")

        try:
            db.session.commit()
            print('=' * 50)
            print(f'{len(created_users)} usuários criados com sucesso!')
            print('=' * 50)
            print('\nCREDENCIAIS DE ACESSO')
            print('-' * 50)
            for userdata in usuarios:
                print(f"  Username: {userdata['username']:<15}  Senha: {userdata['password']}")
            print('-' * 50)
            print('  ATENÇÃO: Altere as senhas em produção!')
        except Exception as e:
            db.session.rollback()
            print(f'Erro ao criar usuários: {e}')
            raise


if __name__ == '__main__':
    seed_usuarios()
