# -*- coding: utf-8 -*-
"""M7.1 - RelatorioPerformance Service — GAP EXITUS-SERVICE-REVIEW-001"""
import logging
import math
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc

from app.database import db
from app.models import Posicao, Transacao, Provento, MovimentacaoCaixa
from app.utils.exceptions import NotFoundError
from app.utils.tenant import filter_by_assessora
from app.models.ativo import Ativo
from app.models.historico_preco import HistoricoPreco
from app.models.parametros_macro import ParametrosMacro
from app.models.posicao import Posicao
from app.models.relatorio_performance import RelatorioPerformance

logger = logging.getLogger(__name__)

# Dias úteis por ano
_DU_ANO = 252


class RelatorioPerformanceService:

    @staticmethod
    def list_by_usuario(usuario_id, portfolio_id=None, periodo='12m'):
        query = RelatorioPerformance.query.filter_by(usuario_id=usuario_id)
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        return [r.to_dict() for r in query.order_by(desc(RelatorioPerformance.created_at)).all()]

    @staticmethod
    def get_by_id(usuario_id, relatorio_id):
        relatorio = RelatorioPerformance.query.filter_by(
            usuario_id=usuario_id, id=relatorio_id
        ).first()
        return relatorio.to_dict() if relatorio else {}

    @staticmethod
    def calcular(usuario_id: UUID, periodo_inicio: date,
                 periodo_fim: date, portfolio_id: Optional[UUID] = None) -> Dict:
        """
        Calcula métricas reais de performance: Sharpe, max drawdown, volatilidade, retorno.

        Args:
            usuario_id: UUID do usuário
            periodo_inicio: Data de início do período
            periodo_fim: Data de fim do período
            portfolio_id: Opcional — filtrar por portfolio

        Returns:
            Dict com métricas calculadas.
        """
        query = Posicao.query.filter_by(usuario_id=usuario_id)
        query = filter_by_assessora(query, Posicao)
        posicoes = query.all()

        if not posicoes:
            return RelatorioPerformanceService._resultado_vazio(periodo_inicio, periodo_fim)

        # Construir série de valor do portfólio por data
        serie_valor = RelatorioPerformanceService._serie_portfolio(
            posicoes, periodo_inicio, periodo_fim
        )

        if len(serie_valor) < 5:
            return RelatorioPerformanceService._resultado_vazio(periodo_inicio, periodo_fim)

        valores = [v for _, v in serie_valor]
        retornos_diarios = [
            (valores[i] / valores[i - 1]) - 1.0
            for i in range(1, len(valores))
            if valores[i - 1] > 0
        ]

        if not retornos_diarios:
            return RelatorioPerformanceService._resultado_vazio(periodo_inicio, periodo_fim)

        # Retorno bruto do período
        retorno_bruto = (valores[-1] / valores[0]) - 1.0 if valores[0] > 0 else None

        # Volatilidade anualizada
        volatilidade = RelatorioPerformanceService._volatilidade_anualizada(retornos_diarios)

        # Sharpe ratio
        sharpe = RelatorioPerformanceService._sharpe(retornos_diarios, volatilidade)

        # Max drawdown
        max_dd = RelatorioPerformanceService._max_drawdown(valores)

        return {
            'periodo_inicio': periodo_inicio.isoformat(),
            'periodo_fim': periodo_fim.isoformat(),
            'retorno_bruto_percentual': round(retorno_bruto * 100, 4) if retorno_bruto is not None else None,
            'retorno_liquido_percentual': round(retorno_bruto * 100, 4) if retorno_bruto is not None else None,
            'indice_sharpe': round(sharpe, 4) if sharpe is not None else None,
            'max_drawdown_percentual': round(max_dd * 100, 4) if max_dd is not None else None,
            'volatilidade_anualizada': round(volatilidade * 100, 4) if volatilidade is not None else None,
            'total_pontos_serie': len(serie_valor),
        }

    @staticmethod
    def generate(usuario_id: UUID, data: Dict) -> Dict:
        """
        Calcula e persiste relatório de performance.
        Se periodo_inicio/periodo_fim fornecidos, recalcula métricas.
        """
        periodo_inicio = data.get('periodo_inicio')
        periodo_fim = data.get('periodo_fim')

        # Calcular métricas reais se período informado
        if periodo_inicio and periodo_fim:
            di = periodo_inicio if isinstance(periodo_inicio, date) else date.fromisoformat(str(periodo_inicio))
            df = periodo_fim if isinstance(periodo_fim, date) else date.fromisoformat(str(periodo_fim))
            metricas = RelatorioPerformanceService.calcular(usuario_id, di, df)
            data = {**data, **{
                'retorno_bruto_percentual': metricas.get('retorno_bruto_percentual'),
                'retorno_liquido_percentual': metricas.get('retorno_liquido_percentual'),
                'indice_sharpe': metricas.get('indice_sharpe'),
                'max_drawdown_percentual': metricas.get('max_drawdown_percentual'),
            }}

        relatorio = RelatorioPerformance(usuario_id=usuario_id, **{
            k: v for k, v in data.items()
            if hasattr(RelatorioPerformance, k)
        })
        db.session.add(relatorio)
        db.session.commit()
        db.session.refresh(relatorio)
        return relatorio.to_dict()

    # ------------------------------------------------------------------
    # Helpers de cálculo
    # ------------------------------------------------------------------

    @staticmethod
    def _serie_portfolio(posicoes: List, data_inicio: date,
                         data_fim: date) -> List:
        """
        Constrói série temporal do valor total do portfólio.
        Para cada data com dados de historico_preco, soma qtd × preco.
        """
        from collections import defaultdict

        # Coletar todas as datas disponíveis
        datas_com_dados = set()
        for pos in posicoes:
            datas = (
                HistoricoPreco.query
                .filter(
                    HistoricoPreco.ativoid == pos.ativo_id,
                    HistoricoPreco.data >= data_inicio,
                    HistoricoPreco.data <= data_fim,
                )
                .with_entities(HistoricoPreco.data)
                .all()
            )
            for (d,) in datas:
                datas_com_dados.add(d)

        if not datas_com_dados:
            return []

        datas_ordenadas = sorted(datas_com_dados)
        serie = []

        for d in datas_ordenadas:
            valor_total = 0.0
            for pos in posicoes:
                hist = (
                    HistoricoPreco.query
                    .filter(
                        HistoricoPreco.ativoid == pos.ativo_id,
                        HistoricoPreco.data <= d,
                    )
                    .order_by(HistoricoPreco.data.desc())
                    .first()
                )
                preco = float(hist.preco_fechamento) if hist else float(pos.preco_medio or 0)
                valor_total += float(pos.quantidade or 0) * preco

            serie.append((d, valor_total))

        return serie

    @staticmethod
    def _volatilidade_anualizada(retornos: List[float]) -> Optional[float]:
        """Desvio padrão dos retornos diários × √252."""
        n = len(retornos)
        if n < 2:
            return None
        media = sum(retornos) / n
        variancia = sum((r - media) ** 2 for r in retornos) / (n - 1)
        return math.sqrt(variancia) * math.sqrt(_DU_ANO)

    @staticmethod
    def _sharpe(retornos: List[float],
                volatilidade: Optional[float]) -> Optional[float]:
        """
        Sharpe = (retorno_médio_anualizado - taxa_livre_risco) / volatilidade_anualizada
        """
        if not retornos or not volatilidade or volatilidade == 0:
            return None

        param = ParametrosMacro.query.filter_by(pais='BR', mercado='B3', ativo=True).first()
        taxa_livre_risco = float(param.taxa_livre_risco) if param and param.taxa_livre_risco else 0.1365

        media_diaria = sum(retornos) / len(retornos)
        retorno_anualizado = (1.0 + media_diaria) ** _DU_ANO - 1.0
        return (retorno_anualizado - taxa_livre_risco) / volatilidade

    @staticmethod
    def _max_drawdown(valores: List[float]) -> Optional[float]:
        """Máximo decréscimo pico→vale na série de valores."""
        if len(valores) < 2:
            return None
        max_dd = 0.0
        pico = valores[0]
        for v in valores:
            if v > pico:
                pico = v
            if pico > 0:
                dd = (pico - v) / pico
                if dd > max_dd:
                    max_dd = dd
        return max_dd

    @staticmethod
    def _resultado_vazio(periodo_inicio: date, periodo_fim: date) -> Dict:
        return {
            'periodo_inicio': periodo_inicio.isoformat(),
            'periodo_fim': periodo_fim.isoformat(),
            'retorno_bruto_percentual': None,
            'retorno_liquido_percentual': None,
            'indice_sharpe': None,
            'max_drawdown_percentual': None,
            'volatilidade_anualizada': None,
            'total_pontos_serie': 0,
        }
