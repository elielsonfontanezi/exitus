# -*- coding: utf-8 -*-
"""
Exitus - Usuario Service - Lógica de negócio
"""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from app.database import db
from app.models import Usuario, UserRole
from app.utils.db_utils import safe_commit, safe_delete_commit


class UsuarioService:
    """Serviço para operações de usuários"""
    
    @staticmethod
    def get_all(page=1, per_page=20, ativo=None, role=None, search=None):
        """
        Lista usuários com paginação e filtros.
        
        Args:
            page: Número da página
            per_page: Itens por página
            ativo: Filtro por status ativo (True/False ou None para todos)
            role: Filtro por role (string: 'ADMIN', 'USER', 'READONLY')
            search: Busca em username e nome_completo
        """
        query = Usuario.query
        
        # FIX GAP-001: Aplicar filtro ativo EXPLICITAMENTE
        if ativo is not None:
            query = query.filter(Usuario.ativo == ativo)
        
        # Filtro por role
        if role:
            try:
                role_enum = UserRole[role.upper()]
                query = query.filter(Usuario.role == role_enum)
            except KeyError:
                pass  # Role inválida, ignora filtro
        
        # Filtro de busca
        if search:
            query = query.filter(or_(
                Usuario.username.ilike(f"%{search}%"),
                Usuario.nome_completo.ilike(f"%{search}%"),
                Usuario.email.ilike(f"%{search}%")
            ))
        
        # Paginação
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(user_id):
        """Busca usuário por ID"""
        return Usuario.query.get(user_id)
    
    @staticmethod
    def create(data):
        """Cria novo usuário."""
        user = Usuario(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            nome_completo=data.get('nome_completo'),
            role=UserRole[data.get('role', 'user').upper()]
        )
        db.session.add(user)
        safe_commit()
        return user
    
    @staticmethod
    def update(user_id, data, current_user):
        """
        Atualiza usuário.
        
        Args:
            user_id: ID do usuário a atualizar
            data: Dict com campos a atualizar
            current_user: Usuário fazendo a atualização
        
        Raises:
            ValueError: Se usuário não encontrado, email duplicado ou 
                       tentativa de alterar campos restritos sem permissão
        """
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        # Verificar se é admin
        is_admin = current_user.role.value.upper() == 'ADMIN'
        
        # 🔧 FIX GAP-005: Bloquear tentativa de alterar campos restritos
        restricted_fields = ['role', 'ativo']
        attempted_restricted = [field for field in restricted_fields if field in data]
        
        if attempted_restricted and not is_admin:
            raise ValueError(
                f"Apenas administradores podem alterar: {', '.join(attempted_restricted)}"
            )
        
        # Atualizar email (verificar duplicidade)
        if 'email' in data:
            existing = Usuario.query.filter_by(email=data['email']).first()
            if existing and existing.id != user.id:
                raise ValueError("Email já existe")
            user.email = data['email']
        
        # Atualizar nome_completo
        if 'nome_completo' in data:
            user.nome_completo = data['nome_completo']
        
        # Apenas admin pode alterar ativo e role
        if 'ativo' in data and is_admin:
            user.ativo = data['ativo']
        
        if 'role' in data and is_admin:
            user.role = UserRole[data['role'].upper()]
        
        safe_commit()
        return user
    
    @staticmethod
    def delete(user_id):
        """Deleta usuário"""
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        safe_delete_commit(user)
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
        safe_commit()
        return True
