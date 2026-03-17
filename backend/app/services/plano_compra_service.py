"""
Service: PlanoCompraService
Lógica de negócio para planos de compra programada
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.database import db
from app.models.plano_compra import PlanoCompra, StatusPlanoCompra
from app.models.ativo import Ativo
from app.utils.exceptions import NotFoundError, BusinessRuleError, ConflictError


class PlanoCompraService:
    """Service para gerenciar planos de compra programada"""

    @staticmethod
    def create(usuario_id: UUID, data: Dict) -> PlanoCompra:
        """
        Cria um novo plano de compra
        
        Args:
            usuario_id: ID do usuário
            data: Dados do plano
            
        Returns:
            PlanoCompra criado
            
        Raises:
            BusinessRuleError: Se dados inválidos
            NotFoundError: Se ativo não existe
        """
        # Validações
        if not data.get('nome'):
            raise BusinessRuleError("Nome do plano é obrigatório")
        
        if not data.get('ativo_id'):
            raise BusinessRuleError("Ativo é obrigatório")
        
        quantidade_alvo = float(data.get('quantidade_alvo', 0))
        if quantidade_alvo <= 0:
            raise BusinessRuleError("Quantidade alvo deve ser maior que zero")
        
        valor_aporte = float(data.get('valor_aporte_mensal', 0))
        if valor_aporte <= 0:
            raise BusinessRuleError("Valor do aporte mensal deve ser maior que zero")
        
        # Verificar se ativo existe
        ativo = Ativo.query.get(data['ativo_id'])
        if not ativo:
            raise NotFoundError(f"Ativo {data['ativo_id']} não encontrado")
        
        # Criar plano
        plano = PlanoCompra(
            usuario_id=usuario_id,
            ativo_id=data['ativo_id'],
            nome=data['nome'],
            descricao=data.get('descricao'),
            quantidade_alvo=quantidade_alvo,
            quantidade_acumulada=data.get('quantidade_acumulada', 0),
            valor_aporte_mensal=valor_aporte,
            data_inicio=datetime.utcnow(),
            status=StatusPlanoCompra.ATIVO
        )
        
        # Calcular próximo aporte (30 dias)
        plano.proximo_aporte = datetime.utcnow() + timedelta(days=30)
        
        # Calcular data fim prevista
        if ativo.preco_atual and ativo.preco_atual > 0:
            meses_estimados = (quantidade_alvo * float(ativo.preco_atual)) / valor_aporte
            plano.data_fim_prevista = datetime.utcnow() + timedelta(days=int(meses_estimados * 30))
        
        try:
            db.session.add(plano)
            db.session.commit()
            return plano
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError(f"Erro ao criar plano: {str(e)}")

    @staticmethod
    def get_by_id(plano_id: UUID, usuario_id: UUID) -> PlanoCompra:
        """
        Busca plano por ID
        
        Args:
            plano_id: ID do plano
            usuario_id: ID do usuário
            
        Returns:
            PlanoCompra encontrado
            
        Raises:
            NotFoundError: Se plano não existe ou não pertence ao usuário
        """
        plano = PlanoCompra.query.filter_by(id=plano_id, usuario_id=usuario_id).first()
        if not plano:
            raise NotFoundError(f"Plano {plano_id} não encontrado")
        return plano

    @staticmethod
    def list_by_usuario(usuario_id: UUID, status: Optional[str] = None) -> List[PlanoCompra]:
        """
        Lista planos do usuário
        
        Args:
            usuario_id: ID do usuário
            status: Filtro por status (opcional)
            
        Returns:
            Lista de PlanoCompra
        """
        query = PlanoCompra.query.filter_by(usuario_id=usuario_id)
        
        if status:
            try:
                status_enum = StatusPlanoCompra(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                raise BusinessRuleError(f"Status inválido: {status}")
        
        return query.order_by(PlanoCompra.created_at.desc()).all()

    @staticmethod
    def update(plano_id: UUID, usuario_id: UUID, data: Dict) -> PlanoCompra:
        """
        Atualiza plano de compra
        
        Args:
            plano_id: ID do plano
            usuario_id: ID do usuário
            data: Dados para atualizar
            
        Returns:
            PlanoCompra atualizado
            
        Raises:
            NotFoundError: Se plano não existe
            BusinessRuleError: Se dados inválidos
        """
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        # Atualizar campos permitidos
        if 'nome' in data:
            plano.nome = data['nome']
        
        if 'descricao' in data:
            plano.descricao = data['descricao']
        
        if 'valor_aporte_mensal' in data:
            valor = float(data['valor_aporte_mensal'])
            if valor <= 0:
                raise BusinessRuleError("Valor do aporte deve ser maior que zero")
            plano.valor_aporte_mensal = valor
        
        if 'quantidade_alvo' in data:
            quantidade = float(data['quantidade_alvo'])
            if quantidade <= 0:
                raise BusinessRuleError("Quantidade alvo deve ser maior que zero")
            plano.quantidade_alvo = quantidade
        
        plano.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return plano
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError(f"Erro ao atualizar plano: {str(e)}")

    @staticmethod
    def registrar_aporte(plano_id: UUID, usuario_id: UUID, quantidade: float) -> PlanoCompra:
        """
        Registra um aporte no plano
        
        Args:
            plano_id: ID do plano
            usuario_id: ID do usuário
            quantidade: Quantidade adquirida
            
        Returns:
            PlanoCompra atualizado
            
        Raises:
            NotFoundError: Se plano não existe
            BusinessRuleError: Se plano não pode receber aporte
        """
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        if not plano.pode_receber_aporte():
            raise BusinessRuleError("Plano não pode receber aportes no status atual")
        
        if quantidade <= 0:
            raise BusinessRuleError("Quantidade deve ser maior que zero")
        
        # Atualizar quantidade acumulada
        plano.quantidade_acumulada += quantidade
        
        # Verificar se atingiu a meta
        if plano.esta_concluido():
            plano.status = StatusPlanoCompra.CONCLUIDO
            plano.data_conclusao = datetime.utcnow()
        else:
            # Atualizar próximo aporte
            plano.proximo_aporte = datetime.utcnow() + timedelta(days=30)
        
        plano.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return plano
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError(f"Erro ao registrar aporte: {str(e)}")

    @staticmethod
    def pausar(plano_id: UUID, usuario_id: UUID) -> PlanoCompra:
        """Pausa um plano ativo"""
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        if plano.status != StatusPlanoCompra.ATIVO:
            raise BusinessRuleError("Apenas planos ativos podem ser pausados")
        
        plano.status = StatusPlanoCompra.PAUSADO
        plano.updated_at = datetime.utcnow()
        
        db.session.commit()
        return plano

    @staticmethod
    def reativar(plano_id: UUID, usuario_id: UUID) -> PlanoCompra:
        """Reativa um plano pausado"""
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        if plano.status != StatusPlanoCompra.PAUSADO:
            raise BusinessRuleError("Apenas planos pausados podem ser reativados")
        
        if plano.esta_concluido():
            raise BusinessRuleError("Plano já foi concluído")
        
        plano.status = StatusPlanoCompra.ATIVO
        plano.proximo_aporte = datetime.utcnow() + timedelta(days=30)
        plano.updated_at = datetime.utcnow()
        
        db.session.commit()
        return plano

    @staticmethod
    def cancelar(plano_id: UUID, usuario_id: UUID) -> PlanoCompra:
        """Cancela um plano"""
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        if plano.status == StatusPlanoCompra.CANCELADO:
            raise BusinessRuleError("Plano já está cancelado")
        
        if plano.status == StatusPlanoCompra.CONCLUIDO:
            raise BusinessRuleError("Plano concluído não pode ser cancelado")
        
        plano.status = StatusPlanoCompra.CANCELADO
        plano.updated_at = datetime.utcnow()
        
        db.session.commit()
        return plano

    @staticmethod
    def delete(plano_id: UUID, usuario_id: UUID) -> None:
        """
        Remove um plano
        
        Args:
            plano_id: ID do plano
            usuario_id: ID do usuário
            
        Raises:
            NotFoundError: Se plano não existe
        """
        plano = PlanoCompraService.get_by_id(plano_id, usuario_id)
        
        try:
            db.session.delete(plano)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError(f"Erro ao remover plano: {str(e)}")
