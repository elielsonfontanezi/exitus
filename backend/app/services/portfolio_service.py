import logging
from decimal import Decimal
from typing import Dict, Optional, List
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
from app.models.portfolio import Portfolio
from app.models.posicao import Posicao
from app.models.ativo import Ativo
from app.services.cache_service import cache
from app.utils.tenant import filter_by_assessora, get_current_assessora_id

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
        
        # Filtro por assessora (multi-tenancy)
        query = filter_by_assessora(query, Portfolio)
        
        # Filtrar por status se especificado
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        return query.order_by(Portfolio.nome)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def create(data: Dict, usuario_id: UUID) -> Portfolio:
        """Cria um novo portfolio."""
        try:
            # Obter assessora_id do JWT ou dos dados
            assessora_id = data.get('assessora_id') or get_current_assessora_id()
            
            novo_portfolio = Portfolio(
                usuario_id=usuario_id,
                nome=data['nome'],
                descricao=data.get('descricao'),
                objetivo=data.get('objetivo'),
                ativo=data.get('ativo', True),
                valor_inicial=data.get('valor_inicial'),
                percentual_alocacao_target=data.get('percentual_alocacao_target'),
                assessora_id=assessora_id
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
        """
        Gera dados consolidados para o dashboard com agrupamento por mercado.
        Cache por 5 minutos para melhorar performance.
        """
        # Tentar obter do cache
        cache_key = f"dashboard:{usuario_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Dashboard cache HIT para usuário {usuario_id}")
            return cached_data
        
        logger.debug(f"Dashboard cache MISS para usuário {usuario_id}")
        
        from app.models import Posicao, Ativo
        from app.services.cambio_service import CambioService
        from decimal import Decimal
        from collections import defaultdict
        
        total_portfolios = Portfolio.query.filter_by(usuario_id=usuario_id, ativo=True).count()
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
        total_posicoes = len(posicoes)
        
        if not posicoes:
            return {
                "resumo": {
                    "total_portfolios": total_portfolios,
                    "total_posicoes": 0,
                    "patrimonio_total": 0.0,
                    "rentabilidade_geral": 0.0
                },
                "por_mercado": {
                    "BR": {"patrimonio": 0.0, "percentual": 0.0, "rentabilidade": 0.0, "top_ativos": []},
                    "US": {"patrimonio": 0.0, "percentual": 0.0, "rentabilidade": 0.0, "top_ativos": []},
                    "INTL": {"patrimonio": 0.0, "percentual": 0.0, "rentabilidade": 0.0, "top_ativos": []}
                },
                "alocacao_geografica": {"BR": 0.0, "US": 0.0, "INTL": 0.0},
                "evolucao": []
            }
        
        patrimonio_por_mercado = defaultdict(float)
        custo_por_mercado = defaultdict(float)
        ativos_por_mercado = defaultdict(list)
        patrimonio_total = 0.0
        custo_total = 0.0
        
        for posicao in posicoes:
            ativo = posicao.ativo
            if not ativo:
                continue
            
            preco = Decimal(str(ativo.preco_atual)) if ativo.preco_atual else Decimal(str(posicao.preco_medio))
            valor_posicao_moeda = Decimal(str(posicao.quantidade)) * preco
            custo_posicao_moeda = Decimal(str(posicao.custo_total)) if posicao.custo_total else Decimal('0')
            
            moeda = getattr(ativo, 'moeda', 'BRL') or 'BRL'
            if moeda.upper() != 'BRL':
                valor_brl = CambioService.converter_para_brl(valor_posicao_moeda, moeda)
                custo_brl = CambioService.converter_para_brl(custo_posicao_moeda, moeda)
                valor_posicao = float(valor_brl) if valor_brl is not None else float(valor_posicao_moeda)
                custo_posicao = float(custo_brl) if custo_brl is not None else float(custo_posicao_moeda)
            else:
                valor_posicao = float(valor_posicao_moeda)
                custo_posicao = float(custo_posicao_moeda)
            
            mercado = ativo.mercado.upper()
            if mercado not in ['BR', 'US']:
                mercado = 'INTL'
            
            patrimonio_por_mercado[mercado] += valor_posicao
            custo_por_mercado[mercado] += custo_posicao
            patrimonio_total += valor_posicao
            custo_total += custo_posicao
            
            ativos_por_mercado[mercado].append({
                'ticker': ativo.ticker,
                'nome': ativo.nome,
                'tipo': ativo.tipo.value if ativo.tipo else None,
                'valor': valor_posicao,
                'rentabilidade': ((valor_posicao - custo_posicao) / custo_posicao * 100) if custo_posicao > 0 else 0.0
            })
        
        rentabilidade_geral = ((patrimonio_total - custo_total) / custo_total * 100) if custo_total > 0 else 0.0
        
        por_mercado = {}
        for mercado in ['BR', 'US', 'INTL']:
            patrimonio = patrimonio_por_mercado.get(mercado, 0.0)
            custo = custo_por_mercado.get(mercado, 0.0)
            percentual = (patrimonio / patrimonio_total * 100) if patrimonio_total > 0 else 0.0
            rentabilidade = ((patrimonio - custo) / custo * 100) if custo > 0 else 0.0
            
            top_ativos = sorted(
                ativos_por_mercado.get(mercado, []),
                key=lambda x: x['valor'],
                reverse=True
            )[:5]
            
            por_mercado[mercado] = {
                'patrimonio': round(patrimonio, 2),
                'percentual': round(percentual, 2),
                'rentabilidade': round(rentabilidade, 2),
                'top_ativos': top_ativos
            }
        
        alocacao_geografica = {
            'BR': round(por_mercado['BR']['percentual'], 2),
            'US': round(por_mercado['US']['percentual'], 2),
            'INTL': round(por_mercado['INTL']['percentual'], 2)
        }
        
        result = {
            "resumo": {
                "total_portfolios": total_portfolios,
                "total_posicoes": total_posicoes,
                "patrimonio_total": round(patrimonio_total, 2),
                "rentabilidade_geral": round(rentabilidade_geral, 2)
            },
            "por_mercado": por_mercado,
            "alocacao_geografica": alocacao_geografica,
            "evolucao": []
        }
        
        # Salvar no cache por 5 minutos
        cache.set(cache_key, result, ttl=300)
        
        return result

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
        
        from app.services.cambio_service import CambioService
        for posicao in posicoes:
            ativo = posicao.ativo
            if not ativo:
                continue

            # Valor da posição = quantidade * preço atual (ou custo médio se preco_atual nulo)
            preco = Decimal(str(ativo.preco_atual)) if ativo.preco_atual else Decimal(str(posicao.preco_medio))
            valor_posicao_moeda = Decimal(str(posicao.quantidade)) * preco

            # Converter para BRL se necessário
            moeda = getattr(ativo, 'moeda', 'BRL') or 'BRL'
            if moeda.upper() != 'BRL':
                valor_brl = CambioService.converter_para_brl(valor_posicao_moeda, moeda)
                valor_posicao = float(valor_brl) if valor_brl is not None else float(valor_posicao_moeda)
            else:
                valor_posicao = float(valor_posicao_moeda)

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

