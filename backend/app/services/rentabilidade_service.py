# -*- coding: utf-8 -*-
"""
Exitus - RentabilidadeService
GAP: EXITUS-RENTABILIDADE-001
Cálculo de rentabilidade TWR, MWR (XIRR) e comparação com benchmarks.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from scipy.optimize import brentq
from sqlalchemy import func

from app.database import db
from app.models.ativo import Ativo
from app.models.historico_preco import HistoricoPreco
from app.models.movimentacao_caixa import MovimentacaoCaixa, TipoMovimentacao
from app.models.parametros_macro import ParametrosMacro
from app.models.posicao import Posicao
from app.models.provento import Provento
from app.models.transacao import Transacao, TipoTransacao

logger = logging.getLogger(__name__)

# Tipos de transação que representam saída de caixa (compra)
_TIPOS_COMPRA = {TipoTransacao.COMPRA}
# Tipos de transação que representam entrada de caixa (venda)
_TIPOS_VENDA = {TipoTransacao.VENDA}

# Mapeamento período → dias
_PERIODOS = {
    '1m': 30,
    '3m': 90,
    '6m': 180,
    '12m': 365,
    '24m': 730,
    'max': None,
}


class RentabilidadeService:
    """Serviço para cálculo de rentabilidade de portfólio."""

    # ------------------------------------------------------------------
    # Método principal — orquestra TWR, MWR e benchmark
    # ------------------------------------------------------------------

    @staticmethod
    def calcular(usuario_id: UUID, periodo: str = '12m',
                 benchmark: str = 'CDI') -> Dict:
        """
        Calcula rentabilidade do portfólio do usuário.

        Args:
            usuario_id: UUID do usuário
            periodo: '1m', '3m', '6m', '12m', '24m', 'ytd', 'max'
            benchmark: 'CDI', 'IBOV', 'IFIX', 'IPCA6', 'SP500'

        Returns:
            Dict com TWR, MWR, benchmark e comparação.
        """
        data_inicio, data_fim = RentabilidadeService._resolver_periodo(periodo)

        # Obter fluxos de caixa do usuário no período
        fluxos = RentabilidadeService._obter_fluxos_caixa(
            usuario_id, data_inicio, data_fim
        )

        # Obter valor do portfólio nas datas-chave
        valores_portfolio = RentabilidadeService._obter_valores_portfolio(
            usuario_id, data_inicio, data_fim, fluxos
        )

        # Calcular TWR
        twr = RentabilidadeService._calcular_twr(valores_portfolio, fluxos)

        # Calcular MWR (XIRR)
        mwr = RentabilidadeService._calcular_mwr(
            fluxos, valores_portfolio, data_inicio, data_fim
        )

        # Obter retorno do benchmark
        retorno_benchmark = RentabilidadeService._obter_benchmark(
            benchmark, data_inicio, data_fim
        )

        # Calcular alpha
        alpha = (twr - retorno_benchmark) if twr is not None and retorno_benchmark is not None else None

        dias = (data_fim - data_inicio).days

        return {
            'periodo': periodo,
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'dias': dias,
            'twr': round(twr, 4) if twr is not None else None,
            'twr_percentual': round(twr * 100, 2) if twr is not None else None,
            'mwr': round(mwr, 4) if mwr is not None else None,
            'mwr_percentual': round(mwr * 100, 2) if mwr is not None else None,
            'benchmark': {
                'nome': benchmark,
                'retorno': round(retorno_benchmark, 4) if retorno_benchmark is not None else None,
                'retorno_percentual': round(retorno_benchmark * 100, 2) if retorno_benchmark is not None else None,
            },
            'alpha': round(alpha, 4) if alpha is not None else None,
            'alpha_percentual': round(alpha * 100, 2) if alpha is not None else None,
            'total_fluxos': len(fluxos),
        }

    # ------------------------------------------------------------------
    # TWR — Time-Weighted Return
    # ------------------------------------------------------------------

    @staticmethod
    def _calcular_twr(valores_portfolio: List[Dict],
                      fluxos: List[Dict]) -> Optional[float]:
        """
        Calcula TWR por sub-períodos entre fluxos de caixa.

        TWR = prod(1 + R_i) - 1
        onde R_i = (V_depois - V_antes - FC_i) / V_antes
        """
        if not valores_portfolio or len(valores_portfolio) < 2:
            return None

        # Ordenar por data
        valores = sorted(valores_portfolio, key=lambda x: x['data'])

        # Mapear fluxos por data
        fluxos_por_data = {}
        for f in fluxos:
            d = f['data']
            if d not in fluxos_por_data:
                fluxos_por_data[d] = 0.0
            fluxos_por_data[d] += f['valor']

        # Calcular retorno de cada sub-período
        produto = 1.0
        for i in range(1, len(valores)):
            v_antes = valores[i - 1]['valor']
            v_depois = valores[i]['valor']
            fc = fluxos_por_data.get(valores[i]['data'], 0.0)

            if v_antes <= 0:
                continue

            # R_i = (V_depois - FC_i) / V_antes - 1
            # FC positivo = aporte (aumenta portfólio sem ser retorno)
            retorno_sub = (v_depois - fc) / v_antes - 1.0
            produto *= (1.0 + retorno_sub)

        twr = produto - 1.0
        return twr

    # ------------------------------------------------------------------
    # MWR — Money-Weighted Return (XIRR)
    # ------------------------------------------------------------------

    @staticmethod
    def _calcular_mwr(fluxos: List[Dict], valores_portfolio: List[Dict],
                      data_inicio: date, data_fim: date) -> Optional[float]:
        """
        Calcula MWR via XIRR (taxa interna de retorno com datas irregulares).

        Fluxo de caixa: compras (-), vendas (+), proventos (+), valor final (+).
        """
        if not fluxos and not valores_portfolio:
            return None

        # Montar lista de (data, valor) para XIRR
        cashflows = []

        # Valor inicial do portfólio (negativo = investimento existente)
        if valores_portfolio:
            v_inicial = valores_portfolio[0]['valor'] if valores_portfolio[0]['valor'] > 0 else 0
            if v_inicial > 0:
                cashflows.append((data_inicio, -v_inicial))

        # Fluxos intermediários
        for f in fluxos:
            cashflows.append((f['data'], f['valor']))

        # Valor final do portfólio (positivo = resgate teórico)
        if valores_portfolio:
            valores_sorted = sorted(valores_portfolio, key=lambda x: x['data'])
            v_final = valores_sorted[-1]['valor']
            if v_final > 0:
                cashflows.append((data_fim, v_final))

        if len(cashflows) < 2:
            return None

        # Calcular XIRR
        return RentabilidadeService._xirr(cashflows)

    @staticmethod
    def _xirr(cashflows: List[Tuple[date, float]],
              guess: float = 0.1) -> Optional[float]:
        """
        Calcula XIRR usando scipy.optimize.brentq.

        Args:
            cashflows: Lista de (data, valor). Negativo = saída, positivo = entrada.
            guess: Estimativa inicial da taxa.

        Returns:
            Taxa anual de retorno ou None se não convergir.
        """
        if not cashflows:
            return None

        # Data base = primeira data
        d0 = min(cf[0] for cf in cashflows)

        def npv(rate):
            total = 0.0
            for d, v in cashflows:
                anos = (d - d0).days / 365.25
                if rate == -1.0 and anos > 0:
                    return float('inf')
                total += v / ((1.0 + rate) ** anos)
            return total

        try:
            taxa = brentq(npv, -0.99, 10.0, maxiter=1000)
            return taxa
        except (ValueError, RuntimeError):
            # Fallback: Newton-Raphson manual
            try:
                rate = guess
                for _ in range(100):
                    f_val = npv(rate)
                    # Derivada numérica
                    h = 1e-6
                    f_deriv = (npv(rate + h) - f_val) / h
                    if abs(f_deriv) < 1e-12:
                        break
                    rate -= f_val / f_deriv
                    if abs(f_val) < 1e-8:
                        return rate
                return rate if abs(npv(rate)) < 1e-4 else None
            except Exception:
                return None

    # ------------------------------------------------------------------
    # Benchmarks
    # ------------------------------------------------------------------

    @staticmethod
    def _obter_benchmark(benchmark: str, data_inicio: date,
                         data_fim: date) -> Optional[float]:
        """Obtém retorno do benchmark no período."""
        benchmark = benchmark.upper()

        if benchmark == 'CDI':
            return RentabilidadeService._benchmark_cdi(data_inicio, data_fim)
        elif benchmark in ('IBOV', 'IFIX', 'IFIX11', 'SP500'):
            ticker = {
                'IBOV': 'BOVA11',
                'IFIX': 'IFIX11',
                'IFIX11': 'IFIX11',
                'SP500': 'IVVB11',
            }.get(benchmark, benchmark)
            return RentabilidadeService._benchmark_por_preco(
                ticker, data_inicio, data_fim
            )
        elif benchmark == 'IPCA6':
            return RentabilidadeService._benchmark_ipca_mais(
                6.0, data_inicio, data_fim
            )
        else:
            logger.warning(f"Benchmark desconhecido: {benchmark}")
            return None

    @staticmethod
    def _benchmark_cdi(data_inicio: date, data_fim: date) -> Optional[float]:
        """CDI acumulado no período usando taxa_livre_risco de parametros_macro."""
        param = ParametrosMacro.query.filter_by(
            pais='BR', mercado='B3', ativo=True
        ).first()

        if not param or not param.taxa_livre_risco:
            logger.warning("Parâmetro CDI não encontrado em parametros_macro")
            return None

        taxa_anual = float(param.taxa_livre_risco)
        dias = (data_fim - data_inicio).days

        if dias <= 0:
            return 0.0

        # CDI acumulado: (1 + taxa_anual)^(dias/252) - 1
        # 252 = dias úteis no ano
        dias_uteis = int(dias * 252 / 365)
        retorno = (1.0 + taxa_anual) ** (dias_uteis / 252.0) - 1.0
        return retorno

    @staticmethod
    def _benchmark_por_preco(ticker: str, data_inicio: date,
                             data_fim: date) -> Optional[float]:
        """Retorno de um ativo-benchmark via historico_preco."""
        ativo = Ativo.query.filter_by(ticker=ticker).first()
        if not ativo:
            logger.warning(f"Ativo benchmark {ticker} não encontrado")
            return None

        preco_inicio = HistoricoPreco.query.filter(
            HistoricoPreco.ativoid == ativo.id,
            HistoricoPreco.data <= data_inicio
        ).order_by(HistoricoPreco.data.desc()).first()

        preco_fim = HistoricoPreco.query.filter(
            HistoricoPreco.ativoid == ativo.id,
            HistoricoPreco.data <= data_fim
        ).order_by(HistoricoPreco.data.desc()).first()

        if not preco_inicio or not preco_fim:
            logger.warning(f"Histórico de preço insuficiente para {ticker}")
            return None

        pi = float(preco_inicio.preco_fechamento)
        pf = float(preco_fim.preco_fechamento)

        if pi <= 0:
            return None

        return (pf / pi) - 1.0

    @staticmethod
    def _benchmark_ipca_mais(spread: float, data_inicio: date,
                             data_fim: date) -> Optional[float]:
        """IPCA + spread fixo (ex: IPCA+6%)."""
        param = ParametrosMacro.query.filter_by(
            pais='BR', mercado='B3', ativo=True
        ).first()

        if not param or not param.inflacao_anual:
            logger.warning("IPCA não encontrado em parametros_macro")
            return None

        ipca_anual = float(param.inflacao_anual)
        taxa_total_anual = ipca_anual + (spread / 100.0)
        dias = (data_fim - data_inicio).days

        return (1.0 + taxa_total_anual) ** (dias / 365.0) - 1.0

    # ------------------------------------------------------------------
    # Helpers — dados do portfólio
    # ------------------------------------------------------------------

    @staticmethod
    def _resolver_periodo(periodo: str) -> Tuple[date, date]:
        """Converte string de período em (data_inicio, data_fim)."""
        hoje = date.today()

        if periodo == 'ytd':
            return date(hoje.year, 1, 1), hoje
        elif periodo == 'max':
            # Usar data da transação mais antiga
            primeira = db.session.query(func.min(Transacao.data_transacao)).scalar()
            if primeira:
                return primeira.date() if hasattr(primeira, 'date') else primeira, hoje
            return date(hoje.year - 1, 1, 1), hoje
        else:
            dias = _PERIODOS.get(periodo, 365)
            if dias is None:
                dias = 365
            return hoje - timedelta(days=dias), hoje

    @staticmethod
    def _obter_fluxos_caixa(usuario_id: UUID, data_inicio: date,
                            data_fim: date) -> List[Dict]:
        """
        Obtém fluxos de caixa do usuário no período.

        Compras = fluxo negativo (saída de caixa)
        Vendas = fluxo positivo (entrada de caixa)
        Proventos = fluxo positivo
        Depósitos/saques em movimentacao_caixa = aportes/resgates
        """
        fluxos = []

        # Transações (compras e vendas)
        transacoes = Transacao.query.filter(
            Transacao.usuario_id == usuario_id,
            func.date(Transacao.data_transacao) >= data_inicio,
            func.date(Transacao.data_transacao) <= data_fim,
        ).order_by(Transacao.data_transacao).all()

        for t in transacoes:
            valor = float(t.valor_total or 0)
            d = t.data_transacao.date() if hasattr(t.data_transacao, 'date') else t.data_transacao

            if t.tipo in _TIPOS_COMPRA:
                fluxos.append({'data': d, 'valor': -valor, 'tipo': 'compra'})
            elif t.tipo in _TIPOS_VENDA:
                fluxos.append({'data': d, 'valor': valor, 'tipo': 'venda'})

        # Proventos
        proventos = Provento.query.join(Ativo).join(
            Posicao, Posicao.ativo_id == Ativo.id
        ).filter(
            Posicao.usuario_id == usuario_id,
            Provento.data_pagamento >= data_inicio,
            Provento.data_pagamento <= data_fim,
        ).all()

        for p in proventos:
            fluxos.append({
                'data': p.data_pagamento,
                'valor': float(p.valor_liquido or 0),
                'tipo': 'provento',
            })

        # Movimentações de caixa (depósitos = aporte, saques = resgate)
        movimentacoes = MovimentacaoCaixa.query.filter(
            MovimentacaoCaixa.usuario_id == usuario_id,
            MovimentacaoCaixa.data_movimentacao >= data_inicio,
            MovimentacaoCaixa.data_movimentacao <= data_fim,
        ).all()

        for m in movimentacoes:
            valor = float(m.valor or 0)
            if m.tipo_movimentacao in (TipoMovimentacao.DEPOSITO, TipoMovimentacao.TRANSFERENCIA_RECEBIDA):
                fluxos.append({'data': m.data_movimentacao, 'valor': -valor, 'tipo': 'aporte'})
            elif m.tipo_movimentacao in (TipoMovimentacao.SAQUE, TipoMovimentacao.TRANSFERENCIA_ENVIADA):
                fluxos.append({'data': m.data_movimentacao, 'valor': valor, 'tipo': 'resgate'})

        # Ordenar por data
        fluxos.sort(key=lambda x: x['data'])
        return fluxos

    @staticmethod
    def _obter_valores_portfolio(usuario_id: UUID, data_inicio: date,
                                 data_fim: date,
                                 fluxos: List[Dict]) -> List[Dict]:
        """
        Obtém valor do portfólio nas datas-chave (início, fluxos, fim).
        """
        # Datas únicas onde precisamos do valor
        datas = {data_inicio, data_fim}
        for f in fluxos:
            datas.add(f['data'])

        datas_ordenadas = sorted(datas)

        # Posições do usuário
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()

        if not posicoes:
            return [{'data': d, 'valor': 0.0} for d in datas_ordenadas]

        valores = []
        for d in datas_ordenadas:
            valor_total = 0.0

            for pos in posicoes:
                # Buscar preço mais recente até a data
                hist = HistoricoPreco.query.filter(
                    HistoricoPreco.ativoid == pos.ativo_id,
                    HistoricoPreco.data <= d
                ).order_by(HistoricoPreco.data.desc()).first()

                if hist:
                    preco = float(hist.preco_fechamento)
                else:
                    # Fallback: usar preço médio da posição
                    preco = float(pos.preco_medio or 0)

                quantidade = float(pos.quantidade or 0)
                valor_total += quantidade * preco

            valores.append({'data': d, 'valor': valor_total})

        return valores
