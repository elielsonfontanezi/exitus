# backend/app/services/portfolio_service.py
# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Service
Módulo de serviço para encapsular a lógica de negócio de Portfolios.
"""
import logging
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.database import db
from app.models import Portfolio, Usuario

logger = logging.getLogger(__name__)

class PortfolioService:
    """Serviço para operações relacionadas a portfolios."""

    @staticmethod
    def get_all_for_user(usuario_id: UUID, page: int = 1, per_page: int = 20):
        """
        Lista todos os portfolios de um usuário com paginação.
        Apenas portfolios ativos são retornados por padrão.
        """
        try:
            paginated_portfolios = Portfolio.query.filter_by(
                usuario_id=usuario_id,
                ativo=True
            ).order_by(Portfolio.nome.asc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            return paginated_portfolios
        except Exception as e:
            logger.error(f"Erro ao listar portfolios para usuario_id {usuario_id}: {e}")
            raise

    @staticmethod
    def get_by_id(portfolio_id: UUID, usuario_id: UUID) -> Portfolio | None:
        """
        Busca um portfolio específico pelo seu ID, garantindo que ele pertença
        ao usuário solicitante.
        """
        try:
            return Portfolio.query.filter_by(id=portfolio_id, usuario_id=usuario_id).first()
        except Exception as e:
            logger.error(f"Erro ao buscar portfolio {portfolio_id} para usuario_id {usuario_id}: {e}")
            raise

    @staticmethod
    def create(data: dict, usuario_id: UUID) -> Portfolio:
        """
        Cria um novo portfolio para o usuário.
        Valida se já existe um portfolio com o mesmo nome para o mesmo usuário.
        """
        nome = data.get('nome')
        if Portfolio.query.filter_by(usuario_id=usuario_id, nome=nome).first():
            raise ValueError(f"Portfolio com nome '{nome}' já existe.")

        novo_portfolio = Portfolio(
            usuario_id=usuario_id,
            nome=nome,
            descricao=data.get('descricao'),
            objetivo=data.get('objetivo')
        )
        try:
            db.session.add(novo_portfolio)
            db.session.commit()
            logger.info(f"Portfolio '{nome}' criado para usuario_id {usuario_id}.")
            return novo_portfolio
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Erro de integridade ao criar portfolio: {e}")
            raise ValueError("Erro ao salvar o portfolio. Verifique os dados.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro inesperado ao criar portfolio: {e}")
            raise

    @staticmethod
    def update(portfolio_id: UUID, data: dict, usuario_id: UUID) -> Portfolio | None:
        """
        Atualiza um portfolio existente.
        Permite a atualização de nome, descrição e objetivo.
        """
        portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not portfolio:
            return None # Not found or doesn't belong to user

        if 'nome' in data and data['nome'] != portfolio.nome:
            if Portfolio.query.filter(
                Portfolio.usuario_id == usuario_id,
                Portfolio.nome == data['nome'],
                Portfolio.id != portfolio_id
            ).first():
                raise ValueError(f"Portfolio com nome '{data['nome']}' já existe.")
            portfolio.nome = data['nome']

        if 'descricao' in data:
            portfolio.descricao = data['descricao']
        if 'objetivo' in data:
            portfolio.objetivo = data['objetivo']

        try:
            db.session.commit()
            logger.info(f"Portfolio {portfolio_id} atualizado para usuario_id {usuario_id}.")
            return portfolio
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar portfolio {portfolio_id}: {e}")
            raise

    @staticmethod
    def delete(portfolio_id: UUID, usuario_id: UUID) -> bool:
        """
        Realiza um 'soft delete' de um portfolio, marcando-o como inativo.
        Retorna True se bem-sucedido, False caso contrário.
        """
        portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not portfolio or not portfolio.ativo:
            return False

        try:
            portfolio.ativo = False
            db.session.commit()
            logger.info(f"Portfolio {portfolio_id} desativado (soft delete) para usuario_id {usuario_id}.")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar portfolio {portfolio_id}: {e}")
            raise

    # --- MÉTODOS DE ANALYTICS (STUBS) ---

    @staticmethod
    def get_dashboard(usuario_id: UUID) -> dict:
        logger.warning(f"Analytics (get_dashboard) para usuario {usuario_id} não implementado.")
        return {"status": "Não implementado"}

    @staticmethod
    def get_alocacao(usuario_id: UUID) -> dict:
        logger.warning(f"Analytics (get_alocacao) para usuario {usuario_id} não implementado.")
        return {"status": "Não implementado"}
    
    @staticmethod
    def get_portfolio_metrics(usuario_id: UUID) -> dict:
        """
        Método de compatibilidade para o módulo de Cálculos (M4).
        Retorna métricas vazias por enquanto.
        """
        logger.warning(f"Analytics (get_portfolio_metrics) para usuario {usuario_id} chamado (STUB).")
        return {
            "total_equity": 0.0,
            "total_invested": 0.0,
            "profit_loss": 0.0,
            "profit_loss_pct": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0
        }
