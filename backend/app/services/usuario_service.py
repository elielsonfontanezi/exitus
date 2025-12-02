# -*- coding: utf-8 -*-
"""Exitus - Usuario Service - Lógica de negócio"""

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from app.database import db
from app.models import Usuario, UserRole

class UsuarioService:
    """Serviço para operações de usuários"""
    
    @staticmethod
    def get_all(page=1, per_page=20, ativo=None, role=None, search=None):
        """
        Lista usuários com paginação e filtros.
        
        Args:
            page: Número da página
            per_page: Itens por página
            ativo: Filtro por status ativo
            role: Filtro por role
            search: Busca em username e nome_completo
        """
        query = Usuario.query
        
        # Filtros
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        if role:
            query = query.filter_by(role=UserRole[role.upper()])
        
        if search:
            query = query.filter(
                or_(
                    Usuario.username.ilike(f'%{search}%'),
                    Usuario.nome_completo.ilike(f'%{search}%')
                )
            )
        
        # Paginação
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(user_id):
        """Busca usuário por ID"""
        return Usuario.query.get(user_id)
    
    @staticmethod
    def create(data):
        """
        Cria novo usuário.
        
        Args:
            data: Dict com username, email, password, nome_completo, role
        """
        user = Usuario(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            nome_completo=data.get('nome_completo'),
            role=UserRole[data.get('role', 'user').upper()]
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update(user_id, data, current_user):
        """
        Atualiza usuário.
        
        Args:
            user_id: ID do usuário a atualizar
            data: Dict com campos a atualizar
            current_user: Usuário fazendo a atualização
        """
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        # Apenas admin pode alterar role e ativo
        is_admin = current_user.role.value.upper() == 'ADMIN'
        
        if 'email' in data:
            # Verifica se email já existe (exceto o próprio)
            existing = Usuario.query.filter_by(email=data['email']).first()
            if existing and existing.id != user.id:
                raise ValueError("Email já existe")
            user.email = data['email']
        
        if 'nome_completo' in data:
            user.nome_completo = data['nome_completo']
        
        if 'ativo' in data and is_admin:
            user.ativo = data['ativo']
        
        if 'role' in data and is_admin:
            user.role = UserRole[data['role'].upper()]
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user_id):
        """Deleta usuário"""
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Troca senha do usuário"""
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        if not check_password_hash(user.password_hash, old_password):
            raise ValueError("Senha atual incorreta")
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True
