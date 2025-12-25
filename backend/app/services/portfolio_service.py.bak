# backend/app/services/portfolio_service.py
# -*- coding: utf-8 -*-
"""
Exitus - Portfolio Service (M7 Analytics)
Responsável pelo CRUD de Portfolios e Cálculos de Dashboard/Alocação.
"""
import logging
from decimal import Decimal
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.database import db
from app.models import Portfolio, Usuario, Posicao, Ativo

logger = logging.getLogger(__name__)

class PortfolioService:
    """Serviço para gestão de portfolios e análise de dados financeiros."""

    # =========================================================================
    # CRUD BÁSICO
    # =========================================================================

    @staticmethod
    def get_all_for_user(usuario_id: UUID, page: int = 1, per_page: int = 20):
        """Lista portfolios ativos do usuário com paginação."""
        try:
            return Portfolio.query.filter_by(
                usuario_id=usuario_id, 
                ativo=True
            ).order_by(Portfolio.nome.asc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            logger.error(f"Erro ao listar portfolios: {e}")
            raise

    @staticmethod
    def get_by_id(portfolio_id: UUID, usuario_id: UUID) -> Portfolio | None:
        """Busca portfolio garantindo propriedade."""
        try:
            return Portfolio.query.filter_by(id=portfolio_id, usuario_id=usuario_id).first()
        except Exception as e:
            logger.error(f"Erro ao buscar portfolio {portfolio_id}: {e}")
            raise

    @staticmethod
    def create(data: dict, usuario_id: UUID) -> Portfolio:
        """Cria novo portfolio, validando duplicidade de nome."""
        nome = data.get('nome')
        if Portfolio.query.filter_by(usuario_id=usuario_id, nome=nome).first():
            raise ValueError(f"Portfolio '{nome}' já existe.")

        novo = Portfolio(
            usuario_id=usuario_id,
            nome=nome,
            descricao=data.get('descricao'),
            objetivo=data.get('objetivo')
        )
        try:
            db.session.add(novo)
            db.session.commit()
            logger.info(f"Portfolio '{nome}' criado (ID: {novo.id})")
            return novo
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Erro de integridade ao criar portfolio.")

    @staticmethod
    def update(portfolio_id: UUID, data: dict, usuario_id: UUID) -> Portfolio | None:
        """Atualiza portfolio existente."""
        pf = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not pf: return None

        if 'nome' in data and data['nome'] != pf.nome:
            if Portfolio.query.filter(
                Portfolio.usuario_id == usuario_id,
                Portfolio.nome == data['nome'],
                Portfolio.id != portfolio_id
            ).first():
                raise ValueError(f"Nome '{data['nome']}' já em uso.")
            pf.nome = data['nome']

        if 'descricao' in data: pf.descricao = data['descricao']
        if 'objetivo' in data: pf.objetivo = data['objetivo']

        try:
            db.session.commit()
            return pf
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar portfolio {portfolio_id}: {e}")
            raise

    @staticmethod
    def delete(portfolio_id: UUID, usuario_id: UUID) -> bool:
        """Soft delete (ativo=False)."""
        pf = PortfolioService.get_by_id(portfolio_id, usuario_id)
        if not pf or not pf.ativo: return False

        try:
            pf.ativo = False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar portfolio {portfolio_id}: {e}")
            raise

    # =========================================================================
    # ANALYTICS & DASHBOARD (M7.2)
    # =========================================================================

    @staticmethod
    def get_dashboard(usuario_id: UUID) -> dict:
        """
        Calcula visão geral consolidada de TODOS os portfolios do usuário.
        Utiliza 'Posicao' e 'Ativo' para calcular patrimônio em tempo quase-real.
        """
        try:
            # Buscar todas as posições do usuário com dados do ativo (inner join)
            results = db.session.query(Posicao, Ativo).join(
                Ativo, Posicao.ativo_id == Ativo.id
            ).filter(
                Posicao.usuario_id == usuario_id,
                Posicao.quantidade > 0
            ).all()

            total_patrimonio = Decimal('0.0')
            total_investido = Decimal('0.0')
            maior_posicao = {"ticker": None, "valor": Decimal('0.0')}

            for posicao, ativo in results:
                qtd = posicao.quantidade
                preco_medio = posicao.preco_medio or Decimal('0.0')
                preco_atual = ativo.preco_atual or preco_medio # Fallback se sem cotação
                
                valor_posicao = qtd * preco_atual
                custo_posicao = qtd * preco_medio

                total_patrimonio += valor_posicao
                total_investido += custo_posicao

                if valor_posicao > maior_posicao["valor"]:
                    maior_posicao = {
                        "ticker": ativo.ticker, 
                        "valor": float(valor_posicao)
                    }

            lucro_prejuizo = total_patrimonio - total_investido
            rentabilidade = (
                (lucro_prejuizo / total_investido * 100) 
                if total_investido > 0 else Decimal('0.0')
            )

            return {
                "total_patrimonio": float(total_patrimonio),
                "total_investido": float(total_investido),
                "lucro_prejuizo": float(lucro_prejuizo),
                "rentabilidade_percentual": round(float(rentabilidade), 2),
                "total_ativos": len(results),
                "maior_posicao": maior_posicao
            }

        except Exception as e:
            logger.error(f"Erro no dashboard analytics para {usuario_id}: {e}")
            return {
                "total_patrimonio": 0.0,
                "error": "Falha ao calcular dashboard"
            }

    @staticmethod
    def get_alocacao(usuario_id: UUID) -> dict:
        """
        Retorna distribuição do portfolio por Classe de Ativo (Ação, FII, Renda Fixa).
        Usado para gráficos de pizza (Pie Chart).
        """
        try:
            # Query agregada por Classe
            # Soma (quantidade * preco_atual) agrupado por classe
            query = db.session.query(
                Ativo.classe,
                func.sum(Posicao.quantidade * func.coalesce(Ativo.preco_atual, Posicao.preco_medio))
            ).join(
                Posicao, Posicao.ativo_id == Ativo.id
            ).filter(
                Posicao.usuario_id == usuario_id,
                Posicao.quantidade > 0
            ).group_by(Ativo.classe).all()

            labels = []
            data = []
            details = {}
            total_geral = 0.0

            for classe, valor_total in query:
                # Converter para string/float seguros
                classe_str = str(classe.value) if hasattr(classe, 'value') else str(classe)
                valor_float = float(valor_total or 0)
                
                labels.append(classe_str)
                data.append(valor_float)
                details[classe_str] = valor_float
                total_geral += valor_float

            # Calcular percentuais
            percentages = [
                round((val / total_geral * 100), 2) if total_geral > 0 else 0 
                for val in data
            ]

            return {
                "labels": labels,
                "data_currency": data,
                "data_percent": percentages,
                "total": total_geral
            }

        except Exception as e:
            logger.error(f"Erro na alocação analytics para {usuario_id}: {e}")
            return {"labels": [], "data": []}

    @staticmethod
    def get_portfolio_metrics(usuario_id: UUID) -> dict:
        """
        Retorna métricas técnicas para o módulo de Buy Signals (M4).
        Reutiliza lógica do dashboard para consistência.
        """
        dash = PortfolioService.get_dashboard(usuario_id)
        
        # Simulação de cálculo de risco (Sharpe) - Futuro M7.4
        # Por enquanto retorna 0 ou valor estático
        sharpe_mock = 1.5 if dash['rentabilidade_percentual'] > 10 else 0.8

        return {
            "total_equity": dash['total_patrimonio'],
            "total_invested": dash['total_invested'],
            "profit_loss": dash['lucro_prejuizo'],
            "profit_loss_pct": dash['rentabilidade_percentual'],
            "volatility": 12.5, # Mock: Volatilidade anualizada fictícia
            "sharpe_ratio": sharpe_mock
        }
