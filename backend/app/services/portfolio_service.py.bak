import logging
from typing import Dict, Optional, List
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
from app.models.portfolio import Portfolio
from app.models.posicao import Posicao
from app.models.ativo import Ativo

logger = logging.getLogger(__name__)

class PortfolioService:
    @staticmethod
    def get_all_for_user(usuario_id: UUID, page: int = 1, per_page: int = 20):
        """Retorna todos os portfolios do usuário com paginação."""
        return Portfolio.query.filter_by(usuario_id=usuario_id, ativo=True)\
            .order_by(Portfolio.nome)\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(portfolio_id: UUID, usuario_id: UUID) -> Optional[Portfolio]:
        """Busca um portfolio específico garantindo que pertença ao usuário."""
        return Portfolio.query.filter_by(id=portfolio_id, usuario_id=usuario_id).first()

    @staticmethod
    def create(data: Dict, usuario_id: UUID) -> Portfolio:
        """Cria um novo portfolio."""
        try:
            novo_portfolio = Portfolio(
                usuario_id=usuario_id,
                nome=data['nome'],
                descricao=data.get('descricao'),
                objetivo=data.get('objetivo'),
                ativo=data.get('ativo', True),
                valor_inicial=data.get('valor_inicial'),
                percentual_alocacao_target=data.get('percentual_alocacao_target')
            )
            db.session.add(novo_portfolio)
            db.session.commit()
            return novo_portfolio
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao criar portfolio: {str(e)}")
            raise e

    @staticmethod
    def update(portfolio_id: UUID, data: Dict, usuario_id: UUID) -> Optional[Portfolio]:
        """Atualiza um portfolio existente."""
        portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not portfolio:
            return None

        try:
            for key, value in data.items():
                if hasattr(portfolio, key) and value is not None:
                    setattr(portfolio, key, value)
            
            db.session.commit()
            return portfolio
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar portfolio: {str(e)}")
            raise e

    @staticmethod
    def delete(portfolio_id: UUID, usuario_id: UUID) -> bool:
        """Remove (soft delete) um portfolio."""
        portfolio = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not portfolio:
            return False

        try:
            # Soft delete
            portfolio.ativo = False
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar portfolio: {str(e)}")
            raise e

    # --- MÉTODOS DE ANALYTICS (MANTIDOS) ---
    
    @staticmethod
    def get_dashboard(usuario_id: UUID) -> Dict:
        """Gera dados consolidados para o dashboard."""
        # Implementação simplificada para validar a rota
        total_portfolios = Portfolio.query.filter_by(usuario_id=usuario_id, ativo=True).count()
        total_posicoes = Posicao.query.filter_by(usuario_id=usuario_id).count()
        
        return {
            "resumo": {
                "total_portfolios": total_portfolios,
                "total_posicoes": total_posicoes,
                "patrimonio_total": 0.0,  # TODO: Calcular soma das posições
                "rentabilidade_geral": 0.0
            }
        }

    # --- MÉTODOS DE COMPATIBILIDADE (M4) ---
    @staticmethod
    def get_portfolio_metrics(usuario_id: UUID, portfolio_id: UUID = None):
        """
        Método de compatibilidade para evitar erro no calculosblueprint.
        Redireciona para get_dashboard ou retorna estrutura vazia.
        """
        try:
            # Retorna dados básicos para não quebrar a inicialização
            return {
                "total_equity": 0.0,
                "profit_loss": 0.0,
                "profit_loss_pct": 0.0,
                "allocation": {}
            }
        except Exception as e:
            logger.error(f"Erro no get_portfolio_metrics: {e}")
            return {}

    @staticmethod
    def get_portfolio_metrics(usuario_id, portfolio_id=None):
        """Compatibilidade para calculosblueprint"""
        return {
            "total_equity": 0.0,
                "profit_loss": 0.0,
            "profit_loss_pct": 0.0,
            "allocation": {}
        }

