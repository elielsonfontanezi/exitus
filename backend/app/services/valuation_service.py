# -*- coding: utf-8 -*-
"""
valuation_service.py — BUG-VAL-005

Serviço central de valuation do Sistema Exitus.
Implementa agregação padrão de mercado:
  1. Classificação de perfil por tipo/mercado/ticker
  2. Cálculo de métodos aplicáveis ao perfil
  3. Remoção de outliers via IQR (k=1.5)
  4. Mediana ponderada por perfil
  5. Faixa de valor justo (min/max/central)

Referências: Investidor10, Status Invest, GuruFocus, Simply Wall St.
"""
from __future__ import annotations

import statistics
from typing import Any

from app.services.parametros_macro_service import get_parametros_macro

# ---------------------------------------------------------------------------
# Constantes de perfil
# ---------------------------------------------------------------------------

_PERFIL_BANCOS_BR = {'ITUB', 'BBDC', 'BBAS', 'SANB', 'BPAC', 'BRSR', 'BMGB'}

# Pesos por perfil: (bazin, gordon, graham, dcf)
_PESOS_ACOES: dict[str, dict[str, float]] = {
    'dividendos': {'bazin': 0.35, 'gordon': 0.25, 'graham': 0.20, 'dcf': 0.20},
    'bancos':     {'bazin': 0.35, 'gordon': 0.25, 'graham': 0.20, 'dcf': 0.20},
    'value':      {'bazin': 0.10, 'gordon': 0.15, 'graham': 0.40, 'dcf': 0.35},
    'growth':     {'bazin': 0.10, 'gordon': 0.10, 'graham': 0.30, 'dcf': 0.50},
    'padrao':     {'bazin': 0.25, 'gordon': 0.25, 'graham': 0.25, 'dcf': 0.25},
}

# Pesos FII base: renormalizados se métodos ausentes
_PESOS_FII_BASE = {'cap_rate': 0.50, 'ffo_cap_rate': 0.30, 'affo_cap_rate': 0.20}


# ---------------------------------------------------------------------------
# Classificação de perfil
# ---------------------------------------------------------------------------

def classificar_perfil_valuation(ativo) -> str:
    """
    Classifica o perfil de valuation do ativo.

    Regras (por prioridade):
      - fii / reit → 'fii'
      - tipo 'stock' + mercado 'US' → 'growth'
      - ação + ticker em set curado de bancos BR → 'bancos'
      - ação + p_l < 8 (disponível e positivo) → 'value'
      - ação BR (default) → 'dividendos'
      - demais → 'padrao'
    """
    tipo_raw = getattr(ativo, 'tipo', None)
    tipo = (tipo_raw.value if hasattr(tipo_raw, 'value') else str(tipo_raw or '')).lower()
    mercado = (getattr(ativo, 'mercado', 'BR') or 'BR').upper()
    ticker = (getattr(ativo, 'ticker', '') or '').upper()

    if tipo in ('fii', 'reit'):
        return 'fii'

    is_acao = tipo in ('acao', 'acoes', 'unit', 'stock', 'stock_intl')

    if not is_acao:
        return 'padrao'

    if tipo == 'stock' and mercado == 'US':
        return 'growth'

    raiz = ticker[:4] if len(ticker) >= 4 else ticker
    if raiz in _PERFIL_BANCOS_BR:
        return 'bancos'

    p_l_raw = getattr(ativo, 'p_l', None)
    if p_l_raw is not None:
        try:
            p_l = float(p_l_raw)
            if 0 < p_l < 8:
                return 'value'
        except (TypeError, ValueError):
            pass

    return 'dividendos'


# ---------------------------------------------------------------------------
# Cálculo de métodos individuais
# ---------------------------------------------------------------------------

def _calcular_metodos_acao(ativo, params: dict) -> dict[str, dict]:
    """Calcula Bazin, Graham, Gordon e DCF para ações."""
    k = params['taxa_livre_risco']
    g = params['crescimento_medio']
    wacc = params['custo_capital']
    preco_atual = float(getattr(ativo, 'preco_atual', None) or 30)
    dy = float(getattr(ativo, 'dividend_yield', None) or 0.06)
    eps_raw = getattr(ativo, 'eps', None)
    eps = float(eps_raw) if eps_raw is not None else 2.50
    fcf_raw = getattr(ativo, 'fcf', None)
    fcf = float(fcf_raw) if fcf_raw is not None else 5.0

    dpa = dy * preco_atual

    # Bazin: DPA / 6% (threshold fixo Décio Bazin)
    pt_bazin = dpa / 0.06 if dy > 0 else 0.0

    # Graham: EPS × (8.5 + 2g%) × 4.4 / Y%
    pt_graham = (eps * (8.5 + 2 * g * 100)) * 4.4 / (k * 100) if eps > 0 else 0.0

    # Gordon: D₁ / (k - g)
    d1 = dpa * (1 + g)
    pt_gordon = d1 / (k - g) if (k > g and dy > 0) else 0.0

    # DCF: Σ FCF_t / (1+WACC)^t + Valor Terminal
    anos = 5
    fluxos = [fcf * (1 + g) ** i for i in range(1, anos + 1)]
    valor_terminal = fluxos[-1] * 1.03 / (wacc - 0.03)
    fluxos.append(valor_terminal)
    pt_dcf = sum(fluxo / (1 + wacc) ** (i + 1) for i, fluxo in enumerate(fluxos))

    return {
        'bazin':  {'pt': round(pt_bazin,  2), 'k': f'{k:.1%}', 'descricao': 'Bazin (DY≥6%)'},
        'graham': {'pt': round(pt_graham, 2), 'descricao': 'Graham (EPS/crescimento)'},
        'gordon': {'pt': round(pt_gordon, 2), 'descricao': 'Gordon (dividendos perpétuos)'},
        'dcf':    {'pt': round(pt_dcf,    2), 'wacc': f'{wacc:.1%}', 'descricao': 'DCF (fluxo de caixa)'},
    }


def _calcular_metodos_fii(ativo, params: dict) -> dict[str, dict]:
    """Calcula Cap Rate, FFO/Cap Rate e AFFO/Cap Rate para FIIs/REITs."""
    cap_rate = params['cap_rate_fii']
    preco_atual = float(getattr(ativo, 'preco_atual', None) or 30)
    dy = float(getattr(ativo, 'dividend_yield', None) or 0.06)

    metodos: dict[str, dict] = {}

    # Cap Rate via DY: pt = (dy × preco_atual) / cap_rate
    if cap_rate > 0 and dy > 0:
        dy_anual = dy * preco_atual
        pt_cap_rate = dy_anual / cap_rate
    else:
        pt_cap_rate = 0.0
    metodos['cap_rate'] = {
        'pt': round(pt_cap_rate, 2),
        'cap_rate': f'{cap_rate:.1%}',
        'descricao': 'Cap Rate via DY',
    }

    # FFO/Cap Rate: pt = ffo_por_cota / cap_rate
    ffo_raw = getattr(ativo, 'ffo_por_cota', None)
    if ffo_raw is not None:
        try:
            ffo = float(ffo_raw)
            if ffo > 0 and cap_rate > 0:
                metodos['ffo_cap_rate'] = {
                    'pt': round(ffo / cap_rate, 2),
                    'cap_rate': f'{cap_rate:.1%}',
                    'descricao': 'Cap Rate via FFO',
                }
        except (TypeError, ValueError):
            pass

    # AFFO/Cap Rate: pt = affo_por_cota / cap_rate
    affo_raw = getattr(ativo, 'affo_por_cota', None)
    if affo_raw is not None:
        try:
            affo = float(affo_raw)
            if affo > 0 and cap_rate > 0:
                metodos['affo_cap_rate'] = {
                    'pt': round(affo / cap_rate, 2),
                    'cap_rate': f'{cap_rate:.1%}',
                    'descricao': 'Cap Rate via AFFO',
                }
        except (TypeError, ValueError):
            pass

    return metodos


# ---------------------------------------------------------------------------
# IQR — remoção de outliers
# ---------------------------------------------------------------------------

def remover_outliers_iqr(
    valores: dict[str, float], k: float = 1.5, ratio_max: float = 4.0
) -> dict[str, float]:
    """
    Remove outliers de conjuntos pequenos de métodos de valuation.

    Usa filtragem por ratio em torno da mediana (mais robusto que IQR clássico
    para n=3–6, onde o outlier inflaciona o próprio Q3 e alarga demais a cerca).

    Regra: valor é outlier se > mediana × ratio_max  ou  < mediana / ratio_max.
    Com ratio_max=4.0: aceita valores até 4× ou 1/4× da mediana.

    Com ≤2 valores, retorna tudo (ratio não é significativo).
    Nunca retorna dict vazio.

    Args:
        valores:   {nome: pt} — apenas métodos com pt > 0
        k:         reservado para compatibilidade (não usado nesta implementação)
        ratio_max: fator máximo em relação à mediana (padrão 4.0)

    Returns:
        Subconjunto sem outliers.
    """
    if len(valores) <= 2:
        return valores

    mediana = statistics.median(valores.values())
    if mediana <= 0:
        return valores

    lo = mediana / ratio_max
    hi = mediana * ratio_max
    filtrado = {nome: pt for nome, pt in valores.items() if lo <= pt <= hi}
    return filtrado if filtrado else valores


# ---------------------------------------------------------------------------
# Agregação: mediana ponderada
# ---------------------------------------------------------------------------

def _mediana_ponderada(
    valores_filtrados: dict[str, float],
    pesos: dict[str, float],
) -> float:
    """
    Calcula mediana ponderada dos métodos presentes após IQR.

    Normaliza pesos dos métodos restantes para somar 1.
    Para métodos sem peso definido, usa peso igual (1.0 bruto).
    """
    nomes = list(valores_filtrados.keys())
    pts = [valores_filtrados[n] for n in nomes]
    pesos_brutos = [pesos.get(n, 1.0) for n in nomes]
    total = sum(pesos_brutos)
    pesos_norm = [p / total for p in pesos_brutos] if total > 0 else [1 / len(pesos_brutos)] * len(pesos_brutos)

    # Ordenar por valor; acumular pesos até atingir 50%
    pares = sorted(zip(pts, pesos_norm), key=lambda x: x[0])
    cumsum = 0.0
    for pt, peso in pares:
        cumsum += peso
        if cumsum >= 0.5:
            return pt

    return pares[-1][0]


def _pesos_fii_normalizados(metodos_presentes: list[str]) -> dict[str, float]:
    """Renormaliza pesos FII para os métodos efetivamente calculados."""
    base = {k: v for k, v in _PESOS_FII_BASE.items() if k in metodos_presentes}
    total = sum(base.values())
    if not base or total == 0:
        return {k: 1 / len(metodos_presentes) for k in metodos_presentes}
    return {k: v / total for k, v in base.items()}


# ---------------------------------------------------------------------------
# Função pública principal
# ---------------------------------------------------------------------------

def calcular_valor_justo(ativo) -> dict[str, Any]:
    """
    Calcula valor justo do ativo usando metodologia de mercado.

    Pipeline (6 etapas):
      1. Parâmetros macroeconômicos regionais
      2. Classificação de perfil (dividendos/growth/value/bancos/fii/padrao)
      3. Cálculo de métodos aplicáveis
      4. Filtro de inválidos (pt <= 0)
      5. Remoção de outliers via IQR (k=1.5)
      6. Mediana ponderada → valor_justo + faixa min/max

    IMPORTANTE: 'preco_teto_usuario' (campo estático do banco) NÃO entra neste
    cálculo — é referência pessoal do usuário, sem impacto no score ou margem.

    Retorna 'pt_medio' como alias de 'valor_justo' para retrocompatibilidade.
    """
    # 1. Parâmetros regionais
    mercado = getattr(ativo, 'mercado', 'BR') or 'BR'
    params = get_parametros_macro(mercado, mercado)

    # 2. Perfil
    perfil = classificar_perfil_valuation(ativo)

    # 3. Métodos
    tipo_raw = getattr(ativo, 'tipo', None)
    tipo = (tipo_raw.value if hasattr(tipo_raw, 'value') else str(tipo_raw or '')).lower()
    preco_atual = float(getattr(ativo, 'preco_atual', None) or 30)

    if tipo in ('acao', 'acoes', 'stock', 'stock_intl', 'unit'):
        metodos = _calcular_metodos_acao(ativo, params)
    elif tipo in ('fii', 'reit'):
        metodos = _calcular_metodos_fii(ativo, params)
    else:
        pt_padrao = round(preco_atual * 1.1, 2)
        metodos = {'padrao': {'pt': pt_padrao, 'descricao': 'Fallback conservador (+10%)'}}

    # 4. Filtrar inválidos
    valores_validos = {n: d['pt'] for n, d in metodos.items() if d.get('pt', 0) > 0}

    if not valores_validos:
        valor_justo = round(preco_atual * 1.1, 2)
        metodos_agregados: dict[str, Any] = {}
        outliers_removidos: list[str] = []
        faixa_min = valor_justo
        faixa_max = valor_justo
    else:
        # 5. IQR
        valores_filtrados = remover_outliers_iqr(valores_validos)
        outliers_removidos = [n for n in valores_validos if n not in valores_filtrados]

        # 6. Pesos e agregação
        if perfil == 'fii':
            pesos = _pesos_fii_normalizados(list(valores_filtrados.keys()))
        else:
            pesos = _PESOS_ACOES.get(perfil, _PESOS_ACOES['padrao'])

        valor_justo = round(_mediana_ponderada(valores_filtrados, pesos), 2)
        faixa_min = round(min(valores_filtrados.values()), 2)
        faixa_max = round(max(valores_filtrados.values()), 2)

        # Metodos agregados com peso normalizado
        total_p = sum(pesos.get(n, 0) for n in valores_filtrados)
        metodos_agregados = {
            n: {
                **metodos[n],
                'peso': round(pesos.get(n, 0) / total_p, 3) if total_p > 0 else 0,
            }
            for n in valores_filtrados
        }

    # Margem e sinal
    margem = ((valor_justo - preco_atual) / valor_justo) * 100 if valor_justo > 0 else 0.0

    if valor_justo > preco_atual * 1.2:
        sinal, cor = '🟢 COMPRA', 'green'
    elif valor_justo > preco_atual:
        sinal, cor = '🟡 NEUTRO', 'yellow'
    else:
        sinal, cor = '🔴 VENDA', 'red'

    return {
        'valor_justo':        valor_justo,
        'pt_medio':           valor_justo,      # alias retrocompatível
        'faixa_min':          faixa_min,
        'faixa_max':          faixa_max,
        'preco_atual':        round(preco_atual, 2),
        'margem_seguranca':   round(margem, 1),
        'sinal':              sinal,
        'cor':                cor,
        'perfil':             perfil,
        'metodo_agregacao':   'mediana_ponderada',
        'metodos':            metodos,
        'metodos_agregados':  metodos_agregados,
        'outliers_removidos': outliers_removidos,
        'parametros_regiao': {
            'taxa_livre_risco': f"{params['taxa_livre_risco']:.1%}",
            'crescimento':      f"{params['crescimento_medio']:.1%}",
            'wacc':             f"{params['custo_capital']:.1%}",
        },
    }
