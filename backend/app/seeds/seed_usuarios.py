# -*- coding: utf-8 -*-
"""
Exitus - Seed de Usuários
Popular tabela usuario com dados iniciais
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from app import create_app
from app.database import db
from app.models import Usuario, UserRole
from datetime import datetime


def seed_usuarios():
    """Cria usuários iniciais do sistema"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Usuários Iniciais")
        print("=" * 50)
        
        # Verificar se já existem usuários
        count = Usuario.query.count()
        if count > 0:
            print(f"⚠ Já existem {count} usuários cadastrados.")
            resposta = input("Deseja recriar os usuários? (s/N): ").lower()
            if resposta != 's':
                print("✗ Seed cancelado pelo usuário.")
                return
            
            # Limpar usuários existentes
            Usuario.query.delete()
            db.session.commit()
            print("✓ Usuários anteriores removidos.")
        
        # Lista de usuários a criar
        usuarios = [
            {
                'username': 'admin',
                'email': 'admin@exitus.com',
                'password': 'admin123',  # Senha padrão para desenvolvimento
                'nome_completo': 'Administrador do Sistema',
                'role': UserRole.ADMIN,
                'ativo': True
            },
            {
                'username': 'joao.silva',
                'email': 'joao.silva@example.com',
                'password': 'user123',
                'nome_completo': 'João Silva',
                'role': UserRole.USER,
                'ativo': True
            },
            {
                'username': 'maria.santos',
                'email': 'maria.santos@example.com',
                'password': 'user123',
                'nome_completo': 'Maria Santos',
                'role': UserRole.USER,
                'ativo': True
            },
            {
                'username': 'viewer',
                'email': 'viewer@exitus.com',
                'password': 'viewer123',
                'nome_completo': 'Usuário Visualizador',
                'role': UserRole.READONLY,
                'ativo': True
            }
        ]
        
        # Criar usuários
        created_users = []
        for user_data in usuarios:
            user = Usuario(
                username=user_data['username'],
                email=user_data['email'],
                nome_completo=user_data.get('nome_completo'),
                role=user_data['role'],
                ativo=user_data['ativo']
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            created_users.append(user)
            
            print(f"✓ Usuário criado: {user.username} ({user.role.value}) - {user.email}")
        
        # Commit no banco
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✓ {len(created_users)} usuários criados com sucesso!")
            print("=" * 50)
            
            # Exibir credenciais
            print("\n📋 CREDENCIAIS DE ACESSO:")
            print("-" * 50)
            for user_data in usuarios:
                print(f"Username: {user_data['username']:<15} | Senha: {user_data['password']}")
            print("-" * 50)
            print("⚠ ATENÇÃO: Altere as senhas em produção!\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar usuários: {e}")
            raise


if __name__ == '__main__':
    seed_usuarios()
