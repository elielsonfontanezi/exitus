# -*- coding: utf-8 -*-
"""
Exitus - Ativo Classifier (BUG-020)

Classificação automática de ativos durante imports (B3 e outros).

Estratégia em camadas (do mais confiável ao menos confiável):
1. Ativo existente no banco de dados local
2. Cache de classificação (seeds, correções manuais, API, heurística)
3. API externa de metadata (yfinance) — quando disponível
4. Inferência por padrão do ticker (sufixo B3, formato US, BDR)
5. Fallback OUTRO com aviso para revisão manual

A função `inferir_classificacao_ativo(ticker)` é pura (não acessa banco)
e retorna um dict com tipo/mercado/moeda/classe/fonte/confianca/aviso.

A função `classificar_ativo(ticker, usuario_id=None)` consulta banco e cache
antes de inferir, e propaga nível de confiança e fonte da classificação.
"""
from __future__ import annotations

import logging
import re
from typing import Optional, TypedDict

from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.models.ativo_classificacao_cache import (
    AtivoClassificacaoCache,
    FonteClassificacao,
    NivelConfianca,
)

logger = logging.getLogger(__name__)


class ClassificacaoAtivo(TypedDict):
    tipo: TipoAtivo
    mercado: str
    moeda: str
    classe: ClasseAtivo
    fonte: FonteClassificacao
    confianca: NivelConfianca
    aviso: Optional[str]


# Tickers que terminam em 11 mas NÃO são FIIs.
# Lista mínima e curada — apenas casos de uso documentados nos seeds do projeto.
# Quando um ETF/Unit novo aparecer, o usuário receberá aviso e poderá ajustar.
_TICKERS_11_NAO_FII = {
    # ETFs BR mais comuns
    'BOVA11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'SMAL11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'IVVB11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'BBSD11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'PIBB11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'DIVO11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'ECOO11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'GOLD11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    'HASH11': (TipoAtivo.ETF, ClasseAtivo.RENDA_VARIAVEL),
    # Units conhecidas
    'KLBN11': (TipoAtivo.UNIT, ClasseAtivo.RENDA_VARIAVEL),
    'TAEE11': (TipoAtivo.UNIT, ClasseAtivo.RENDA_VARIAVEL),
    'SANB11': (TipoAtivo.UNIT, ClasseAtivo.RENDA_VARIAVEL),
}


def _resposta(
    tipo: TipoAtivo,
    mercado: str,
    moeda: str,
    classe: ClasseAtivo,
    fonte: FonteClassificacao,
    confianca: NivelConfianca,
    aviso: Optional[str] = None,
) -> ClassificacaoAtivo:
    """Helper para construir resposta padronizada."""
    return {
        'tipo': tipo,
        'mercado': mercado,
        'moeda': moeda,
        'classe': classe,
        'fonte': fonte,
        'confianca': confianca,
        'aviso': aviso,
    }


def _classificar_via_api_externa(ticker: str, mercado: str = 'BR') -> Optional[ClassificacaoAtivo]:
    """
    Consulta metadata externa (yfinance) para classificar o ativo.

    Returns:
        ClassificacaoAtivo se conseguir identificar, None caso contrário.
    """
    try:
        import yfinance as yf

        suffix = '.SA' if mercado == 'BR' else ''
        info = yf.Ticker(f'{ticker}{suffix}').info or {}

        tipo_str = (info.get('type') or '').upper()
        # yfinance retorna 'ETF', 'REIT', 'STOCK', etc.
        if tipo_str == 'ETF':
            tipo = TipoAtivo.ETF
        elif tipo_str == 'REIT':
            tipo = TipoAtivo.REIT
        elif tipo_str == 'STOCK':
            tipo = TipoAtivo.STOCK
        else:
            return None

        return _resposta(
            tipo=tipo,
            mercado=mercado,
            moeda='USD' if mercado != 'BR' else 'BRL',
            classe=ClasseAtivo.RENDA_VARIAVEL,
            fonte=FonteClassificacao.API,
            confianca=NivelConfianca.MEDIA,
            aviso=(
                f"Ticker {ticker} classificado via API externa ({tipo_str}). "
                "Verifique se está correto."
            ),
        )
    except Exception as e:
        logger.debug(f"API externa falhou para {ticker}: {e}")
        return None


def inferir_classificacao_ativo(ticker: str) -> ClassificacaoAtivo:
    """
    Infere tipo, mercado, moeda e classe de um ativo a partir do ticker.

    Função pura — não acessa banco. Use `classificar_ativo()` para a versão
    completa com lookup no banco e cache.

    Regras (na ordem):
    1. Lista curada de tickers terminados em 11 que NÃO são FII (ETFs, Units)
    2. BDR/GDR (sufixo 31-36): STOCK_INTL, mercado INTL, moeda BRL
    3. Sufixo 11 não listado: FII por default + aviso de revisão
    4. Sufixos 3/4/5/6/7/8 (B3): AÇÃO, mercado BR, moeda BRL
    5. 1-5 letras puras (sem número): STOCK US + aviso (pode ser ETF/REIT)
    6. Fallback: OUTRO com aviso

    Args:
        ticker: Código do ativo (será normalizado para upper)

    Returns:
        Dict com tipo, mercado, moeda, classe, fonte, confianca, aviso
    """
    if not ticker or not isinstance(ticker, str):
        return _resposta(
            tipo=TipoAtivo.OUTRO,
            mercado='BR',
            moeda='BRL',
            classe=ClasseAtivo.RENDA_VARIAVEL,
            fonte=FonteClassificacao.HEURISTICA,
            confianca=NivelConfianca.BAIXA,
            aviso="Ticker vazio ou inválido — classificado como OUTRO.",
        )

    t = ticker.upper().strip()

    # 1. Lookup curado: tickers terminados em 11 que NÃO são FII
    if t in _TICKERS_11_NAO_FII:
        tipo, classe = _TICKERS_11_NAO_FII[t]
        return _resposta(
            tipo=tipo,
            mercado='BR',
            moeda='BRL',
            classe=classe,
            fonte=FonteClassificacao.HEURISTICA,
            confianca=NivelConfianca.ALTA,
            aviso=None,
        )

    # 2. BDR/GDR — 4 letras + 31..36
    m = re.match(r'^([A-Z]{4})(3[1-6])$', t)
    if m:
        return _resposta(
            tipo=TipoAtivo.STOCK_INTL,
            mercado='INTL',
            moeda='BRL',
            classe=ClasseAtivo.RENDA_VARIAVEL,
            fonte=FonteClassificacao.HEURISTICA,
            confianca=NivelConfianca.ALTA,
            aviso=None,
        )

    # 3-4. Padrão B3: 4 letras + 1-2 dígitos
    m = re.match(r'^([A-Z]{4})(\d{1,2})$', t)
    if m:
        sufixo = m.group(2)
        if sufixo == '11':
            return _resposta(
                tipo=TipoAtivo.FII,
                mercado='BR',
                moeda='BRL',
                classe=ClasseAtivo.RENDA_VARIAVEL,
                fonte=FonteClassificacao.HEURISTICA,
                confianca=NivelConfianca.MEDIA,
                aviso=(
                    f"Ticker {t} classificado como FII por heurística. "
                    "Verifique se não é ETF (ex: BOVA11) ou Unit (ex: KLBN11) — "
                    "se for, edite o ativo manualmente."
                ),
            )
        if sufixo in ('3', '4', '5', '6', '7', '8'):
            return _resposta(
                tipo=TipoAtivo.ACAO,
                mercado='BR',
                moeda='BRL',
                classe=ClasseAtivo.RENDA_VARIAVEL,
                fonte=FonteClassificacao.HEURISTICA,
                confianca=NivelConfianca.ALTA,
                aviso=None,
            )

    # 5. 1-5 letras puras (sem número) → US Stock
    if re.match(r'^[A-Z]{1,5}$', t):
        return _resposta(
            tipo=TipoAtivo.STOCK,
            mercado='US',
            moeda='USD',
            classe=ClasseAtivo.RENDA_VARIAVEL,
            fonte=FonteClassificacao.HEURISTICA,
            confianca=NivelConfianca.BAIXA,
            aviso=(
                f"Ticker {t} classificado como STOCK US por heurística. "
                "Verifique se não é ETF (ex: VTI, SCHD) ou REIT (ex: O, PLD) — "
                "se for, edite o ativo manualmente."
            ),
        )

    # 6. Fallback
    return _resposta(
        tipo=TipoAtivo.OUTRO,
        mercado='BR',
        moeda='BRL',
        classe=ClasseAtivo.RENDA_VARIAVEL,
        fonte=FonteClassificacao.HEURISTICA,
        confianca=NivelConfianca.BAIXA,
        aviso=(
            f"Ticker {t} não corresponde a nenhum padrão conhecido. "
            "Classificado como OUTRO — revise manualmente."
        ),
    )


def _classificar_do_cache(
    ticker: str,
    usuario_id: Optional[str] = None,
) -> Optional[ClassificacaoAtivo]:
    """Busca classificação no cache (correção manual ou seed)."""
    query = AtivoClassificacaoCache.query.filter_by(ticker=ticker)
    if usuario_id:
        query = query.filter(
            (AtivoClassificacaoCache.usuario_id == usuario_id)
            | (AtivoClassificacaoCache.usuario_id.is_(None))
        )
    else:
        query = query.filter(AtivoClassificacaoCache.usuario_id.is_(None))

    # Prioriza correção manual (fonte=MANUAL) e depois seed/API/heurística
    cache = query.order_by(
        AtivoClassificacaoCache.fonte,
        AtivoClassificacaoCache.updated_at.desc(),
    ).first()

    if not cache:
        return None

    return _resposta(
        tipo=cache.tipo,
        mercado=cache.mercado,
        moeda=cache.moeda,
        classe=cache.classe,
        fonte=cache.fonte,
        confianca=cache.confianca,
        aviso=None if cache.confianca == NivelConfianca.ALTA else (
            f"Classificação obtida do cache ({cache.fonte.value}) — confiança {cache.confianca.value}."
        ),
    )


def classificar_ativo(
    ticker: str,
    usuario_id: Optional[str] = None,
    usar_api_externa: bool = True,
) -> ClassificacaoAtivo:
    """
    Classifica ativo consultando banco e cache primeiro, depois inferindo.

    Ordem de prioridade:
    1. Ativo existente no banco (qualquer mercado) — confiança ALTA, fonte DB
    2. Cache de classificação (manual/seed) — confiança conforme registrado
    3. API externa (yfinance metadata) — confiança MEDIA
    4. Inferência por heurística — confiança variável
    5. Fallback OUTRO — confiança BAIXA

    Args:
        ticker: Código do ativo
        usuario_id: ID do usuário para buscar correções manuais
        usar_api_externa: Se False, pula consulta a APIs externas

    Returns:
        Dict com tipo, mercado, moeda, classe, fonte, confianca, aviso
    """
    if not ticker:
        return inferir_classificacao_ativo(ticker)

    t = ticker.upper().strip()

    # 1. Ativo existente no banco — fonte de verdade máxima
    existente = Ativo.query.filter_by(ticker=t).first()
    if existente:
        return _resposta(
            tipo=existente.tipo,
            mercado=existente.mercado,
            moeda=existente.moeda,
            classe=existente.classe,
            fonte=FonteClassificacao.MANUAL,  # DB é decisão já persistida
            confianca=NivelConfianca.ALTA,
            aviso=None,
        )

    # 2. Cache de classificação (seeds, correções manuais, API/heurística cacheada)
    cache = _classificar_do_cache(t, usuario_id)
    if cache:
        return cache

    # 3. API externa — tenta BR e depois US
    if usar_api_externa:
        api = _classificar_via_api_externa(t, mercado='BR')
        if api:
            return api
        api = _classificar_via_api_externa(t, mercado='US')
        if api:
            return api

    # 4. Heurística pura
    return inferir_classificacao_ativo(t)


def salvar_classificacao_cache(
    ticker: str,
    tipo: TipoAtivo,
    mercado: str,
    moeda: str,
    classe: ClasseAtivo,
    fonte: FonteClassificacao,
    confianca: NivelConfianca,
    usuario_id: Optional[str] = None,
    observacoes: Optional[str] = None,
) -> AtivoClassificacaoCache:
    """
    Persiste uma classificação no cache.

    Útil para:
    - Seeds popularem o cache no startup
    - Usuário corrigir classificação manualmente
    - Cachear resultado de API/heurística
    """
    from app.database import db

    t = ticker.upper().strip()
    cache = AtivoClassificacaoCache.query.filter_by(
        ticker=t, usuario_id=usuario_id
    ).first()

    if cache:
        cache.tipo = tipo
        cache.mercado = mercado
        cache.moeda = moeda
        cache.classe = classe
        cache.fonte = fonte
        cache.confianca = confianca
        cache.observacoes = observacoes
    else:
        cache = AtivoClassificacaoCache(
            ticker=t,
            tipo=tipo,
            mercado=mercado,
            moeda=moeda,
            classe=classe,
            fonte=fonte,
            confianca=confianca,
            usuario_id=usuario_id,
            observacoes=observacoes,
        )
        db.session.add(cache)

    db.session.commit()
    return cache
