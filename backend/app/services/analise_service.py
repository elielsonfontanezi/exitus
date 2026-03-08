# -*- coding: utf-8 -*-
"""Exitus - AnaliseService (M7.2) — GAP EXITUS-SERVICE-REVIEW-001"""
import logging
import math
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func

from app.database import db
from app.models.ativo import Ativo, ClasseAtivo
from app.models.historico_preco import HistoricoPreco
from app.models.posicao import Posicao
from app.services.cambio_service import CambioService

logger = logging.getLogger(__name__)


class AnaliseService:

    @staticmethod
    def analisar_performance_portfolio(usuario_id: UUID,
                                       portfolio_id: UUID = None) -> Dict:
        """
        Analisa performance do portfólio com dados reais.
        Retorna alocação atual por classe, total de posições e patrimônio.
        """
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()

        if not posicoes:
            return {
                "total_posicoes": 0,
                "patrimonio_total": 0.0,
                "alocacao_atual": {},
                "alocacao_target": {},
                "desvios": {},
            }

        alocacao = {}
        total = 0.0

        for pos in posicoes:
            ativo = pos.ativo
            if not ativo:
                continue

            preco = float(ativo.preco_atual or pos.preco_medio or 0)
            qtd = float(pos.quantidade or 0)
            moeda = getattr(ativo, 'moeda', 'BRL') or 'BRL'

            valor = qtd * preco
            if moeda.upper() != 'BRL':
                try:
                    convertido = CambioService.converter_para_brl(
                        Decimal(str(valor)), moeda
                    )
                    valor = float(convertido) if convertido is not None else valor
                except Exception:
                    pass

            total += valor
            classe = (
                ativo.classe.value
                if hasattr(ativo.classe, 'value') else str(ativo.classe)
            )
            alocacao[classe] = alocacao.get(classe, 0.0) + valor

        alocacao_pct = {}
        for cls, val in alocacao.items():
            alocacao_pct[cls] = round(val / total * 100, 2) if total > 0 else 0.0

        return {
            "total_posicoes": len(posicoes),
            "patrimonio_total": round(total, 2),
            "alocacao_atual": alocacao_pct,
            "alocacao_target": {},
            "desvios": {},
        }

    @staticmethod
    def comparar_com_benchmark(usuario_id: UUID, benchmark: str = 'CDI',
                               periodo: str = '12m') -> Dict:
        """
        Compara rentabilidade real do portfólio com benchmark.
        Delega para RentabilidadeService (RENTABILIDADE-001).
        """
        try:
            from app.services.rentabilidade_service import RentabilidadeService
            resultado = RentabilidadeService.calcular(usuario_id, periodo, benchmark)
            return {
                "benchmark": benchmark,
                "periodo": periodo,
                "portfolio_retorno": resultado.get('twr_percentual'),
                "benchmark_retorno": resultado['benchmark'].get('retorno_percentual'),
                "alpha": resultado.get('alpha_percentual'),
                "mwr": resultado.get('mwr_percentual'),
            }
        except Exception as e:
            logger.error(f"Erro ao comparar com benchmark: {e}")
            return {
                "benchmark": benchmark,
                "periodo": periodo,
                "portfolio_retorno": None,
                "benchmark_retorno": None,
                "alpha": None,
                "mwr": None,
                "erro": str(e),
            }

    @staticmethod
    def calcular_correlacao_ativos(usuario_id: UUID,
                                   dias: int = 252) -> Dict:
        """
        Calcula matriz de correlação dos retornos diários dos ativos em carteira
        usando historico_preco dos últimos `dias` dias úteis.
        """
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
        if not posicoes:
            return {"ativos": [], "correlacao": []}

        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=int(dias * 1.5))

        # Coletar séries de retornos por ativo
        series: Dict[str, List[float]] = {}
        tickers: List[str] = []

        for pos in posicoes:
            ativo = pos.ativo
            if not ativo:
                continue

            historico = (
                HistoricoPreco.query
                .filter(
                    HistoricoPreco.ativoid == ativo.id,
                    HistoricoPreco.data >= data_inicio,
                    HistoricoPreco.data <= data_fim,
                )
                .order_by(HistoricoPreco.data)
                .all()
            )

            if len(historico) < 10:
                continue

            precos = [float(h.preco_fechamento) for h in historico]
            retornos = [
                (precos[i] / precos[i - 1]) - 1.0
                for i in range(1, len(precos))
                if precos[i - 1] > 0
            ]

            if retornos:
                series[ativo.ticker] = retornos
                tickers.append(ativo.ticker)

        if not tickers:
            return {"ativos": [], "correlacao": []}

        # Alinhar tamanho das séries (usar o mínimo)
        min_len = min(len(series[t]) for t in tickers)
        series = {t: series[t][-min_len:] for t in tickers}

        # Calcular matriz de correlação
        n = len(tickers)
        correlacao = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    correlacao[i][j] = 1.0
                elif j < i:
                    correlacao[i][j] = correlacao[j][i]
                else:
                    r = AnaliseService._correlacao(series[tickers[i]], series[tickers[j]])
                    correlacao[i][j] = round(r, 4) if r is not None else 0.0

        return {"ativos": tickers, "correlacao": correlacao}

    @staticmethod
    def _correlacao(x: List[float], y: List[float]) -> Optional[float]:
        """Coeficiente de correlação de Pearson."""
        n = len(x)
        if n < 2:
            return None
        mx = sum(x) / n
        my = sum(y) / n
        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        dx = math.sqrt(sum((v - mx) ** 2 for v in x))
        dy = math.sqrt(sum((v - my) ** 2 for v in y))
        if dx == 0 or dy == 0:
            return None
        return num / (dx * dy)
