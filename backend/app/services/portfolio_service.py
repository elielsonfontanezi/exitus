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
    def get_by_id(portfolio_id: UUID, usuario_id: UUID) -> Optional[Portfolio]:
        """Busca um portfolio específico garantindo que pertença ao usuário."""
        return Portfolio.query.filter_by(id=portfolio_id, usuario_id=usuario_id).first()

    @staticmethod
    def get_all_for_user(usuario_id: UUID, page: int = 1, per_page: int = 20):
        """Retorna todos os portfolios do usuário com paginação."""
        return Portfolio.query.filter_by(usuario_id=usuario_id, ativo=True)\
            .order_by(Portfolio.nome)\
            .paginate(page=page, per_page=per_page, error_out=False)

    # ADICIONAR APÓS o método get_all_for_user() (linha ~23)
    @staticmethod
    def get_all(usuario_id: UUID, page: int = 1, per_page: int = 20, ativo: bool = None):
        """
        Retorna portfolios do usuário com paginação e filtro de status.
        Alias melhorado de get_all_for_user().
        
        Args:
            usuario_id: UUID do usuário
            page: Página atual (default: 1)
            per_page: Itens por página (default: 20)
            ativo: Filtrar por status (True/False/None para todos)
        """
        query = Portfolio.query.filter_by(usuario_id=usuario_id)
        
        # Filtrar por status se especificado
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        return query.order_by(Portfolio.nome)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
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


# Adicionar no final da classe PortfolioService

    @staticmethod
    def get_alocacao(usuario_id):
        """
        Calcula alocação do portfólio por classe de ativo.
        
        Returns:
            {
                "renda_variavel": {"valor": 0.0, "percentual": 0.0},
                "renda_fixa": {"valor": 0.0, "percentual": 0.0},
                "cripto": {"valor": 0.0, "percentual": 0.0}
            }
        """
        from app.models import Posicao, Ativo
        from app.database import db
        
        # Buscar todas as posições do usuário
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
        
        if not posicoes:
            return {
                "renda_variavel": {"valor": 0.0, "percentual": 0.0},
                "renda_fixa": {"valor": 0.0, "percentual": 0.0},
                "cripto": {"valor": 0.0, "percentual": 0.0}
            }
        
        # Agrupar por classe
        alocacao = {}
        total_patrimonio = 0.0
        
        for posicao in posicoes:
            ativo = posicao.ativo
            if not ativo:
                continue
            
            # Valor da posição = quantidade * preço atual (ou custo médio se preco_atual nulo)
            preco = float(ativo.preco_atual) if ativo.preco_atual else float(posicao.preco_medio)
            valor_posicao = float(posicao.quantidade) * preco
            total_patrimonio += valor_posicao
            
            # Obter classe do ativo (enum -> string lowercase)
            if hasattr(ativo, 'classe'):
                classe = str(ativo.classe.value) if hasattr(ativo.classe, 'value') else str(ativo.classe)
                classe = classe.lower().replace('classeativo.', '')  # Normalizar
            else:
                classe = "renda_variavel"  # Default
            
            if classe not in alocacao:
                alocacao[classe] = 0.0
            
            alocacao[classe] += valor_posicao
        
        # Calcular percentuais
        resultado = {}
        for classe, valor in alocacao.items():
            percentual = (valor / total_patrimonio * 100) if total_patrimonio > 0 else 0
            resultado[classe] = {
                "valor": round(valor, 2),
                "percentual": round(percentual, 2)
            }
        
        # Garantir que classes obrigatórias existam (mesmo zeradas)
        for classe in ["renda_variavel", "renda_fixa", "cripto"]:
            if classe not in resultado:
                resultado[classe] = {"valor": 0.0, "percentual": 0.0}
        
        return resultado

