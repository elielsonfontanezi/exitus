# -*- coding: utf-8 -*-
"""
EXITUS-ANOMALY-001 — Detecção de preços anômalos.

Regra: alertar quando o preço de um ativo varia ≥ LIMIAR (padrão 20%)
em relação ao último fechamento registrado em historico_preco, sem que
haja evento corporativo registrado na janela de JANELA_DIAS antes e depois
da data de detecção.

Fontes de dados:
  - app.models.historico_preco.HistoricoPreco   — preços históricos diários
  - app.models.evento_corporativo.EventoCorporativo — eventos que justificam variação
  - app.models.ativo.Ativo                       — lista de ativos

Uso principal:
  1. On-demand: GET /api/cotacoes/anomalias
  2. Inline: chamado internamente ao salvar nova cotação (cotacoes_blueprint.py)
"""
import logging
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from app.database import db
from app.models.ativo import Ativo
from app.models.historico_preco import HistoricoPreco
from app.models.evento_corporativo import EventoCorporativo

logger = logging.getLogger(__name__)

LIMIAR_PADRAO = Decimal('0.20')
JANELA_EVENTO_DIAS = 5


def _variacao(preco_novo: Decimal, preco_ref: Decimal) -> Optional[Decimal]:
    """Retorna variação percentual absoluta entre dois preços. None se referência zero."""
    if not preco_ref or preco_ref == 0:
        return None
    return abs((preco_novo - preco_ref) / preco_ref)


def _tem_evento_corporativo(ativo_id, data_ref: date, janela: int = JANELA_EVENTO_DIAS) -> bool:
    """Verifica se há evento corporativo no ativo dentro da janela ao redor da data."""
    data_ini = data_ref - timedelta(days=janela)
    data_fim = data_ref + timedelta(days=janela)
    return db.session.query(
        EventoCorporativo.query
        .filter(
            EventoCorporativo.ativo_id == ativo_id,
            EventoCorporativo.data_evento >= data_ini,
            EventoCorporativo.data_evento <= data_fim,
        )
        .exists()
    ).scalar()


class AnomalyService:
    """Detecção de anomalias em preços de ativos (EXITUS-ANOMALY-001)."""

    @staticmethod
    def detectar_anomalias(
        limiar: Decimal = LIMIAR_PADRAO,
        ativo_id=None,
        data_ref: Optional[date] = None,
    ) -> List[dict]:
        """
        Detecta ativos com variação de preço ≥ limiar sem evento corporativo.

        Para cada ativo (ou apenas o ativo_id informado), compara os dois
        registros mais recentes de historico_preco. Se a variação superar
        o limiar e não houver evento corporativo na janela, inclui na lista.

        Args:
            limiar:    Percentual mínimo de variação para considerar anomalia (ex: 0.20 = 20%).
            ativo_id:  Filtrar por ativo específico. None = todos os ativos.
            data_ref:  Data de referência para buscar os dois últimos preços.
                       None = data de hoje.

        Returns:
            Lista de dicts com detalhes de cada anomalia detectada.
        """
        if data_ref is None:
            data_ref = date.today()

        limiar = Decimal(str(limiar))
        anomalias = []

        query = Ativo.query.filter(Ativo.ativo.is_(True))
        if ativo_id is not None:
            query = query.filter(Ativo.id == ativo_id)

        ativos = query.all()

        for ativo in ativos:
            try:
                historico = (
                    HistoricoPreco.query
                    .filter(
                        HistoricoPreco.ativoid == ativo.id,
                        HistoricoPreco.data <= data_ref,
                    )
                    .order_by(HistoricoPreco.data.desc())
                    .limit(2)
                    .all()
                )

                if len(historico) < 2:
                    continue

                preco_atual = Decimal(str(historico[0].preco_fechamento))
                preco_anterior = Decimal(str(historico[1].preco_fechamento))
                data_atual = historico[0].data
                data_anterior = historico[1].data

                variacao = _variacao(preco_atual, preco_anterior)
                if variacao is None or variacao < limiar:
                    continue

                tem_evento = _tem_evento_corporativo(ativo.id, data_atual)
                if tem_evento:
                    logger.debug(
                        f"Variação de {float(variacao):.1%} em {ativo.ticker} justificada por "
                        f"evento corporativo próximo de {data_atual}"
                    )
                    continue

                variacao_pct = float(
                    (variacao * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                )
                direcao = 'alta' if preco_atual > preco_anterior else 'queda'

                anomalias.append({
                    'ativo_id':        str(ativo.id),
                    'ticker':          ativo.ticker,
                    'nome':            ativo.nome,
                    'mercado':         ativo.mercado,
                    'data_referencia': data_atual.isoformat(),
                    'data_anterior':   data_anterior.isoformat(),
                    'preco_atual':     float(preco_atual),
                    'preco_anterior':  float(preco_anterior),
                    'variacao_pct':    variacao_pct,
                    'direcao':         direcao,
                    'limiar_usado':    float(limiar * 100),
                    'tem_evento_corporativo': False,
                })
                logger.warning(
                    f"ANOMALIA: {ativo.ticker} {direcao} {variacao_pct:.2f}% "
                    f"({data_anterior} → {data_atual}) sem evento corporativo"
                )

            except Exception as e:
                logger.error(f"Erro ao analisar {ativo.ticker}: {e}", exc_info=True)
                continue

        anomalias.sort(key=lambda x: x['variacao_pct'], reverse=True)
        return anomalias

    @staticmethod
    def verificar_ativo(
        ativo_id,
        preco_novo: Decimal,
        data_novo: date,
        limiar: Decimal = LIMIAR_PADRAO,
    ) -> Optional[dict]:
        """
        Verifica anomalia pontual ao registrar nova cotação de um ativo.

        Compara preco_novo com o último registro em historico_preco anterior
        a data_novo. Se a variação superar o limiar e não houver evento
        corporativo na janela, retorna o dict da anomalia; caso contrário None.

        Usado internamente pelo cotacoes_blueprint ao salvar novo preco_atual.
        """
        try:
            ultimo = (
                HistoricoPreco.query
                .filter(
                    HistoricoPreco.ativoid == ativo_id,
                    HistoricoPreco.data < data_novo,
                )
                .order_by(HistoricoPreco.data.desc())
                .first()
            )
            if not ultimo:
                return None

            preco_novo = Decimal(str(preco_novo))
            preco_ref = Decimal(str(ultimo.preco_fechamento))
            variacao = _variacao(preco_novo, preco_ref)
            if variacao is None or variacao < Decimal(str(limiar)):
                return None

            if _tem_evento_corporativo(ativo_id, data_novo):
                return None

            ativo = db.session.get(Ativo, ativo_id)
            ticker = ativo.ticker if ativo else str(ativo_id)
            variacao_pct = float(
                (variacao * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            direcao = 'alta' if preco_novo > preco_ref else 'queda'
            logger.warning(
                f"ANOMALIA (inline): {ticker} {direcao} {variacao_pct:.2f}% "
                f"({ultimo.data} → {data_novo}) sem evento corporativo"
            )
            return {
                'ativo_id':        str(ativo_id),
                'ticker':          ticker,
                'data_referencia': data_novo.isoformat(),
                'data_anterior':   ultimo.data.isoformat(),
                'preco_atual':     float(preco_novo),
                'preco_anterior':  float(preco_ref),
                'variacao_pct':    variacao_pct,
                'direcao':         direcao,
                'limiar_usado':    float(Decimal(str(limiar)) * 100),
                'tem_evento_corporativo': False,
            }
        except Exception as e:
            logger.error(f"Erro em verificar_ativo({ativo_id}): {e}", exc_info=True)
            return None
