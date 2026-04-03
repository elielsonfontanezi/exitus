# -*- coding: utf-8 -*-
"""
Exitus - Assessora Service
CRUD completo e métricas para gestão de assessoras
"""

from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy import func
from app.models import Assessora, Usuario, Portfolio, Transacao
from app.database import db
from app.utils.exceptions import NotFoundError, ValidationError


class AssessoraService:
    """Service para gestão de assessoras (admin only)"""

    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, ativo: Optional[bool] = None):
        """
        Lista todas as assessoras (admin only)
        
        Args:
            page: Página atual
            per_page: Registros por página
            ativo: Filtrar por status ativo (None = todos)
        
        Returns:
            QueryPagination: Assessoras paginadas
        """
        query = Assessora.query
        
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        query = query.order_by(Assessora.nome)
        
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(assessora_id: UUID) -> Assessora:
        """
        Busca assessora por ID
        
        Args:
            assessora_id: UUID da assessora
        
        Returns:
            Assessora: Assessora encontrada
        
        Raises:
            NotFoundError: Se assessora não existe
        """
        assessora = Assessora.query.get(assessora_id)
        
        if not assessora:
            raise NotFoundError(f"Assessora {assessora_id} não encontrada")
        
        return assessora

    @staticmethod
    def create(data: dict) -> Assessora:
        """
        Cria nova assessora
        
        Args:
            data: Dados da assessora (nome, razao_social, cnpj, email, etc)
        
        Returns:
            Assessora: Assessora criada
        
        Raises:
            ValidationError: Se dados inválidos ou CNPJ/email duplicado
        """
        # Validar campos obrigatórios
        required_fields = ['nome', 'razao_social', 'cnpj', 'email']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Campo obrigatório: {field}")
        
        # Validar CNPJ único
        cnpj = data.get('cnpj')
        if Assessora.query.filter_by(cnpj=cnpj).first():
            raise ValidationError(f"CNPJ {cnpj} já cadastrado")
        
        # Validar email único
        email = data.get('email')
        if Assessora.query.filter_by(email=email).first():
            raise ValidationError(f"Email {email} já cadastrado")
        
        # Criar assessora
        assessora = Assessora(
            nome=data['nome'],
            razao_social=data['razao_social'],
            cnpj=data['cnpj'],
            email=data['email'],
            telefone=data.get('telefone'),
            site=data.get('site'),
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            cep=data.get('cep'),
            numero_cvm=data.get('numero_cvm'),
            anbima=data.get('anbima', False),
            ativo=data.get('ativo', True),
            logo_url=data.get('logo_url'),
            cor_primaria=data.get('cor_primaria', '#3B82F6'),
            cor_secundaria=data.get('cor_secundaria', '#1E40AF'),
            max_usuarios=data.get('max_usuarios'),
            max_portfolios=data.get('max_portfolios'),
            plano=data.get('plano', 'basico')
        )
        
        db.session.add(assessora)
        db.session.commit()
        
        return assessora

    @staticmethod
    def update(assessora_id: UUID, data: dict) -> Assessora:
        """
        Atualiza assessora existente
        
        Args:
            assessora_id: UUID da assessora
            data: Dados a atualizar
        
        Returns:
            Assessora: Assessora atualizada
        
        Raises:
            NotFoundError: Se assessora não existe
            ValidationError: Se dados inválidos
        """
        assessora = AssessoraService.get_by_id(assessora_id)
        
        # Validar CNPJ único (se mudou)
        if 'cnpj' in data and data['cnpj'] != assessora.cnpj:
            if Assessora.query.filter_by(cnpj=data['cnpj']).first():
                raise ValidationError(f"CNPJ {data['cnpj']} já cadastrado")
        
        # Validar email único (se mudou)
        if 'email' in data and data['email'] != assessora.email:
            if Assessora.query.filter_by(email=data['email']).first():
                raise ValidationError(f"Email {data['email']} já cadastrado")
        
        # Atualizar campos permitidos
        updatable_fields = [
            'nome', 'razao_social', 'cnpj', 'email', 'telefone', 'site',
            'endereco', 'cidade', 'estado', 'cep', 'numero_cvm', 'anbima',
            'ativo', 'logo_url', 'cor_primaria', 'cor_secundaria',
            'max_usuarios', 'max_portfolios', 'plano'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(assessora, field, data[field])
        
        db.session.commit()
        
        return assessora

    @staticmethod
    def delete(assessora_id: UUID, hard_delete: bool = False) -> bool:
        """
        Deleta assessora (soft delete por padrão)
        
        Args:
            assessora_id: UUID da assessora
            hard_delete: Se True, deleta fisicamente (CASCADE)
        
        Returns:
            bool: True se deletado com sucesso
        
        Raises:
            NotFoundError: Se assessora não existe
            ValidationError: Se assessora tem usuários ativos
        """
        assessora = AssessoraService.get_by_id(assessora_id)
        
        if not hard_delete:
            # Soft delete - apenas desativa
            assessora.ativo = False
            db.session.commit()
            return True
        
        # Hard delete - verificar se tem usuários ativos
        usuarios_ativos = Usuario.query.filter_by(
            assessora_id=assessora_id,
            ativo=True
        ).count()
        
        if usuarios_ativos > 0:
            raise ValidationError(
                f"Não é possível deletar assessora com {usuarios_ativos} usuários ativos"
            )
        
        # Deletar fisicamente (CASCADE vai deletar relacionamentos)
        db.session.delete(assessora)
        db.session.commit()
        
        return True

    @staticmethod
    def get_stats(assessora_id: UUID) -> Dict:
        """
        Retorna métricas da assessora
        
        Args:
            assessora_id: UUID da assessora
        
        Returns:
            dict: Métricas (total_usuarios, total_portfolios, total_transacoes, etc)
        
        Raises:
            NotFoundError: Se assessora não existe
        """
        assessora = AssessoraService.get_by_id(assessora_id)
        
        # Contar usuários
        total_usuarios = Usuario.query.filter_by(assessora_id=assessora_id).count()
        usuarios_ativos = Usuario.query.filter_by(
            assessora_id=assessora_id,
            ativo=True
        ).count()
        
        # Contar portfolios
        total_portfolios = Portfolio.query.filter_by(assessora_id=assessora_id).count()
        portfolios_ativos = Portfolio.query.filter_by(
            assessora_id=assessora_id,
            ativo=True
        ).count()
        
        # Contar transações
        total_transacoes = Transacao.query.filter_by(assessora_id=assessora_id).count()
        
        # Calcular volume total transacionado
        volume_total = db.session.query(
            func.sum(Transacao.valor_total)
        ).filter_by(assessora_id=assessora_id).scalar() or 0
        
        return {
            'assessora_id': str(assessora_id),
            'nome': assessora.nome,
            'ativo': assessora.ativo,
            'plano': assessora.plano,
            'total_usuarios': total_usuarios,
            'usuarios_ativos': usuarios_ativos,
            'total_portfolios': total_portfolios,
            'portfolios_ativos': portfolios_ativos,
            'total_transacoes': total_transacoes,
            'volume_total': float(volume_total),
            'max_usuarios': assessora.max_usuarios,
            'max_portfolios': assessora.max_portfolios,
            'pode_adicionar_usuario': assessora.pode_adicionar_usuario,
            'pode_adicionar_portfolio': assessora.pode_adicionar_portfolio
        }

    @staticmethod
    def toggle_ativo(assessora_id: UUID) -> Assessora:
        """
        Ativa/desativa assessora
        
        Args:
            assessora_id: UUID da assessora
        
        Returns:
            Assessora: Assessora com status atualizado
        
        Raises:
            NotFoundError: Se assessora não existe
        """
        assessora = AssessoraService.get_by_id(assessora_id)
        assessora.ativo = not assessora.ativo
        db.session.commit()
        
        return assessora
