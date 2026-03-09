# -*- coding: utf-8 -*-
"""
Exitus - IR Service (EXITUS-IR-001 + IR-002 + IR-003 + IR-004 + IR-005 + IR-006)
Engine de cálculo de Imposto de Renda sobre operações de renda variável e renda fixa.

Regras implementadas (Brasil):
- Swing trade ações: 15% sobre lucro mensal, isenção R$20.000/mês em vendas
- Day-trade (ações/FIIs): 20% sobre lucro, sem isenção
- FIIs: 20% sobre lucro, sem isenção
- Custo de aquisição via preço médio ponderado (PM) da tabela `posicao` (IR-002)
- Compensação de prejuízo acumulado entre meses por categoria (IR-003)
- Proventos (IR-004): dividendos BR isentos, JCP 15% retido na fonte, dividendos US 15% CRÉDITO IRS, aluguel 15%
- Renda fixa (IR-005): tabela regressiva 22,5%→15% por prazo; LCI/LCA isento PF
- Alíquotas dinâmicas via tabela `regra_fiscal` (IR-007)
- DARF: código de receita por categoria

Tabelas usadas: transacao, ativo, corretora, posicao, saldo_prejuizo, regra_fiscal
"""

import logging
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import cast, extract
from sqlalchemy.types import Date

from app.database import db
from app.models.transacao import Transacao, TipoTransacao
from app.models.ativo import Ativo, TipoAtivo
from app.models.corretora import Corretora
from app.models.posicao import Posicao
from app.models.saldo_prejuizo import SaldoPrejuizo
from app.models.saldo_darf_acumulado import SaldoDarfAcumulado
from app.models.regra_fiscal import RegraFiscal
from app.utils.exceptions import BusinessRuleError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes fiscais (Brasil — vigência 2024+)
# ---------------------------------------------------------------------------
ISENCAO_SWING_ACAO = Decimal('20000.00')   # Isenção mensal vendas ações swing
ALIQUOTA_SWING_ACAO = Decimal('0.15')      # 15%
ALIQUOTA_DAY_TRADE = Decimal('0.20')       # 20%
ALIQUOTA_FII = Decimal('0.20')             # 20% (sem isenção)
ALIQUOTA_REIT = Decimal('0.15')            # 15% (ETF/REIT US — simplificado)
ALIQUOTA_STOCK_US = Decimal('0.15')        # 15% ganho capital US

# Códigos DARF (Receita Federal)
DARF_SWING_ACAO = '6015'
DARF_DAY_TRADE = '6015'   # mesmo código, campo "day-trade" diferencia
DARF_FII = '6015'
DARF_RENDA_FIXA = '0561'
DARF_JCP_DIVIDENDO = '9453'  # JCP e dividendos tributados (info — retido na fonte)

# Valor mínimo de DARF (abaixo disso acumula para mês seguinte)
DARF_MINIMO = Decimal('10.00')

# Tipos de ativo que se enquadram como "ação BR" para isenção de R$20k
# TipoAtivo.UNIT: UNITs B3 (TAEE11, KLBN11, SANB11) seguem a mesma regra fiscal de ações BR
# — isenção de R$20k/mês para swing trade, alíquota 15%, day-trade 20% (EXITUS-IR-008)
TIPOS_ACAO_BR = {TipoAtivo.ACAO, TipoAtivo.UNIT}
TIPOS_FII = {TipoAtivo.FII}
TIPOS_US = {TipoAtivo.STOCK, TipoAtivo.REIT, TipoAtivo.ETF, TipoAtivo.BOND}
TIPOS_BR = {TipoAtivo.ACAO, TipoAtivo.FII, TipoAtivo.CDB, TipoAtivo.LCI_LCA,
            TipoAtivo.TESOURO_DIRETO, TipoAtivo.DEBENTURE}

# Renda fixa (IR-005)
TIPOS_RF_TRIBUTADO = {TipoAtivo.CDB, TipoAtivo.TESOURO_DIRETO, TipoAtivo.DEBENTURE}
TIPOS_RF_ISENTO    = {TipoAtivo.LCI_LCA}   # Isentos para PF (Lei 12.431)
TIPOS_RF           = TIPOS_RF_TRIBUTADO | TIPOS_RF_ISENTO

# Tabela regressiva IR RF (IN RFB 1.585/2015)
TABELA_REGRESSIVA_RF = [
    (180, Decimal('0.225')),   # ≤180 dias
    (360, Decimal('0.200')),   # 181–360 dias
    (720, Decimal('0.175')),   # 361–720 dias
]  # >720 dias → 15%
ALIQUOTA_RF_MINIMA = Decimal('0.150')

# Tabela regressiva IOF sobre rendimentos de RF (art. 7º do Decreto 6.306/2007)
# Índice = dias corridos desde a aplicação (1 a 29); dia 0 e >=30 → 0%
TABELA_IOF_REGRESSIVA = [
    Decimal('0'),    # dia 0  → 0% (não se aplica)
    Decimal('0.96'), # dia 1  → 96%
    Decimal('0.93'), # dia 2  → 93%
    Decimal('0.90'), # dia 3  → 90%
    Decimal('0.86'), # dia 4  → 86%
    Decimal('0.83'), # dia 5  → 83%
    Decimal('0.80'), # dia 6  → 80%
    Decimal('0.76'), # dia 7  → 76%
    Decimal('0.73'), # dia 8  → 73%
    Decimal('0.70'), # dia 9  → 70%
    Decimal('0.66'), # dia 10 → 66%
    Decimal('0.63'), # dia 11 → 63%
    Decimal('0.60'), # dia 12 → 60%
    Decimal('0.56'), # dia 13 → 56%
    Decimal('0.53'), # dia 14 → 53%
    Decimal('0.50'), # dia 15 → 50%
    Decimal('0.46'), # dia 16 → 46%
    Decimal('0.43'), # dia 17 → 43%
    Decimal('0.40'), # dia 18 → 40%
    Decimal('0.36'), # dia 19 → 36%
    Decimal('0.33'), # dia 20 → 33%
    Decimal('0.30'), # dia 21 → 30%
    Decimal('0.26'), # dia 22 → 26%
    Decimal('0.23'), # dia 23 → 23%
    Decimal('0.20'), # dia 24 → 20%
    Decimal('0.16'), # dia 25 → 16%
    Decimal('0.13'), # dia 26 → 13%
    Decimal('0.10'), # dia 27 → 10%
    Decimal('0.06'), # dia 28 →  6%
    Decimal('0.03'), # dia 29 →  3%
]  # dia 30+ → 0%


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _parse_mes(mes_str: str) -> tuple[int, int]:
    """Valida e converte 'YYYY-MM' → (ano, mes)."""
    try:
        ano, mes = mes_str.split('-')
        ano, mes = int(ano), int(mes)
        if not (1 <= mes <= 12):
            raise ValueError
        return ano, mes
    except Exception:
        raise BusinessRuleError(f"Formato de mês inválido: '{mes_str}'. Use YYYY-MM.")


def _primeiro_ultimo_dia(ano: int, mes: int) -> tuple[date, date]:
    ultimo = monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo)


def _mes_anterior(ano: int, mes: int) -> str:
    """Retorna 'YYYY-MM' do mês anterior."""
    if mes == 1:
        return f'{ano - 1}-12'
    return f'{ano}-{(mes - 1):02d}'


CATEGORIAS_FISCAIS = ('swing_acoes', 'day_trade', 'fiis', 'exterior')


def _is_day_trade(t: Transacao, todas: list) -> bool:
    """Verifica se uma venda tem compra correspondente no mesmo dia."""
    if t.tipo != TipoTransacao.VENDA:
        return False
    data_t = t.data_transacao.date() if hasattr(t.data_transacao, 'date') else t.data_transacao
    for outra in todas:
        if (
            outra.tipo == TipoTransacao.COMPRA
            and outra.ativo_id == t.ativo_id
            and (outra.data_transacao.date() if hasattr(outra.data_transacao, 'date') else outra.data_transacao) == data_t
        ):
            return True
    return False


def _carregar_regras_fiscais(data_ref: date) -> dict:
    """
    Carrega regras fiscais vigentes do banco para a data de referência.
    Retorna dict por chave (pais, tipo_ativo, tipo_operacao) → {aliquota, valor_isencao}.
    Fallback: retorna constantes hardcoded se tabela vazia.
    """
    regras = RegraFiscal.query.filter(
        RegraFiscal.ativa == True,
        RegraFiscal.vigencia_inicio <= data_ref,
        db.or_(
            RegraFiscal.vigencia_fim == None,
            RegraFiscal.vigencia_fim >= data_ref,
        )
    ).all()

    if not regras:
        logger.warning(
            "IR-007: tabela regra_fiscal vazia — usando alíquotas hardcoded como fallback."
        )
        return {
            ('BR', 'ACAO',  'SWING_TRADE'): {'aliquota': ALIQUOTA_SWING_ACAO, 'isencao': ISENCAO_SWING_ACAO},
            ('BR', None,    'DAY_TRADE'):   {'aliquota': ALIQUOTA_DAY_TRADE,  'isencao': None},
            ('BR', 'FII',   'VENDA'):       {'aliquota': ALIQUOTA_FII,         'isencao': None},
            ('US', 'STOCK', 'VENDA'):       {'aliquota': ALIQUOTA_STOCK_US,    'isencao': None},
            ('US', 'REIT',  'VENDA'):       {'aliquota': ALIQUOTA_REIT,        'isencao': None},
        }

    mapa = {}
    for r in regras:
        chave = (r.pais, r.tipo_ativo, r.tipo_operacao)
        mapa[chave] = {
            'aliquota': Decimal(str(r.aliquota_ir)) / Decimal('100'),
            'isencao':  Decimal(str(r.valor_isencao)) if r.valor_isencao else None,
        }
    return mapa


def _regra_para_categoria(regras: dict, categoria: str) -> dict:
    """
    Retorna {aliquota, isencao} para a categoria fiscal, buscando no mapa de regras.
    Fallback por categoria se chave exata não encontrada.
    """
    mapa_categoria = {
        'swing_acoes': ('BR', 'ACAO',  'SWING_TRADE'),
        'day_trade':   ('BR', None,    'DAY_TRADE'),
        'fiis':        ('BR', 'FII',   'VENDA'),
        'exterior':    ('US', 'STOCK', 'VENDA'),
    }
    fallback = {
        'swing_acoes': {'aliquota': ALIQUOTA_SWING_ACAO, 'isencao': ISENCAO_SWING_ACAO},
        'day_trade':   {'aliquota': ALIQUOTA_DAY_TRADE,  'isencao': None},
        'fiis':        {'aliquota': ALIQUOTA_FII,         'isencao': None},
        'exterior':    {'aliquota': ALIQUOTA_STOCK_US,    'isencao': None},
    }
    chave = mapa_categoria.get(categoria)
    return regras.get(chave, fallback[categoria])


def _aliquota_rf(prazo_dias: int) -> Decimal:
    """
    Retorna a alíquota de IR aplicada ao resgate de renda fixa conforme
    tabela regressiva (IN RFB 1.585/2015).

    Args:
        prazo_dias: número de dias corridos entre compra e resgate

    Returns:
        Decimal com a alíquota (0.225, 0.200, 0.175 ou 0.150)
    """
    for limite, aliquota in TABELA_REGRESSIVA_RF:
        if prazo_dias <= limite:
            return aliquota
    return ALIQUOTA_RF_MINIMA


def _calcular_iof(prazo_dias: int, rendimento: Decimal) -> Decimal:
    """
    Calcula IOF sobre rendimento de RF conforme tabela regressiva
    (art. 7º do Decreto 6.306/2007).

    Args:
        prazo_dias: número de dias corridos entre aplicação e resgate
        rendimento: rendimento bruto da operação (base de cálculo)

    Returns:
        Decimal com o valor de IOF devido (zero se prazo >= 30 dias ou rendimento <= 0)
    """
    if prazo_dias >= 30 or rendimento <= 0:
        return Decimal('0')
    aliquota = TABELA_IOF_REGRESSIVA[prazo_dias] if prazo_dias < len(TABELA_IOF_REGRESSIVA) else Decimal('0')
    return (rendimento * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _custo_medio(compras: list) -> Decimal:
    """Custo médio ponderado de compras (PEPS simplificado: usa PM geral do mês)."""
    total_qtd = sum(Decimal(str(c.quantidade)) for c in compras)
    total_val = sum(Decimal(str(c.valor_liquido)) for c in compras)
    if total_qtd == 0:
        return Decimal('0')
    return (total_val / total_qtd).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Engine principal
# ---------------------------------------------------------------------------

class IRService:

    @staticmethod
    def apurar_mes(usuario_id: str, mes_str: str, *, persist: bool = True) -> dict:
        """
        Apura IR de renda variável para um mês/usuário.

        Args:
            usuario_id: UUID do usuário (string)
            mes_str: mês no formato 'YYYY-MM'
            persist: se True (default), persiste SaldoPrejuizo no banco.
                     Usar False em chamadas read-only (ex: gerar_dirpf).

        Returns:
            dict com breakdown por categoria, IR devido, DARF e alertas
        """
        ano, mes = _parse_mes(mes_str)
        dt_ini, dt_fim = _primeiro_ultimo_dia(ano, mes)

        # Buscar todas as transações do mês (compras, vendas e proventos)
        transacoes = (
            Transacao.query
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.tipo.in_([
                    TipoTransacao.COMPRA, TipoTransacao.VENDA,
                    TipoTransacao.DIVIDENDO, TipoTransacao.JCP, TipoTransacao.ALUGUEL,
                ]),
                cast(Transacao.data_transacao, Date) >= dt_ini,
                cast(Transacao.data_transacao, Date) <= dt_fim,
            )
            .join(Ativo, Transacao.ativo_id == Ativo.id)
            .join(Corretora, Transacao.corretora_id == Corretora.id)
            .add_columns(
                Ativo.tipo.label('tipo_ativo'),
                Ativo.ticker,
                Corretora.id.label('corretora_id'),
                Corretora.nome.label('corretora_nome'),
            )
            .order_by(Transacao.data_transacao)
            .all()
        )

        # Carregar preço médio da tabela posicao (IR-002)
        # Mapa: (ativo_id_str, corretora_id_str) → preco_medio
        posicoes = Posicao.query.filter_by(usuario_id=usuario_id).all()
        pm_map = {
            (str(p.ativo_id), str(p.corretora_id)): Decimal(str(p.preco_medio))
            for p in posicoes
            if p.preco_medio and p.preco_medio > 0
        }

        # Mapa: (ativo_id_str, corretora_id_str) → data_primeira_compra (IR-005)
        data_compra_map = {
            (str(p.ativo_id), str(p.corretora_id)): p.data_primeira_compra
            for p in posicoes
            if p.data_primeira_compra
        }

        # Separar por categoria
        swing_acoes   = []   # vendas swing ações BR
        day_trade     = []   # vendas day-trade (qualquer tipo)
        fiis          = []   # vendas FIIs
        exterior      = []   # vendas US/exterior
        resgates_rf   = []   # resgates renda fixa (IR-005)
        compras_todas = []   # todas as compras (para custo médio)

        # Acumulador por corretora: {corretora_id: {nome, vendas, lucro, ir}}
        por_corretora: dict = {}

        # Listas de proventos por tipo
        proventos_dividendos_br = []
        proventos_jcp           = []
        proventos_dividendos_us = []
        proventos_aluguel       = []

        for row in transacoes:
            t, tipo_ativo, ticker, corretora_id, corretora_nome = row

            # Proventos (IR-004)
            if t.tipo == TipoTransacao.DIVIDENDO:
                if tipo_ativo in TIPOS_US:
                    proventos_dividendos_us.append((t, tipo_ativo, ticker))
                else:
                    proventos_dividendos_br.append((t, tipo_ativo, ticker))
                continue
            if t.tipo == TipoTransacao.JCP:
                proventos_jcp.append((t, tipo_ativo, ticker))
                continue
            if t.tipo == TipoTransacao.ALUGUEL:
                proventos_aluguel.append((t, tipo_ativo, ticker))
                continue

            if t.tipo == TipoTransacao.COMPRA:
                compras_todas.append(t)
                continue

            # É venda — classificar
            is_dt = _is_day_trade(t, [r[0] for r in transacoes if r[0].tipo == TipoTransacao.COMPRA])

            if tipo_ativo in TIPOS_RF:
                resgates_rf.append((t, tipo_ativo, ticker))
            elif is_dt:
                day_trade.append((t, tipo_ativo, ticker))
            elif tipo_ativo in TIPOS_FII:
                fiis.append((t, tipo_ativo, ticker))
            elif tipo_ativo in TIPOS_US:
                exterior.append((t, tipo_ativo, ticker))
            else:
                swing_acoes.append((t, tipo_ativo, ticker))

            # Acumular por corretora (vendas)
            cid = str(corretora_id)
            if cid not in por_corretora:
                por_corretora[cid] = {
                    'corretora_id':   cid,
                    'corretora_nome': corretora_nome,
                    'total_vendas':   Decimal('0'),
                    'operacoes':      0,
                }
            por_corretora[cid]['total_vendas'] += Decimal(str(t.valor_total))
            por_corretora[cid]['operacoes']    += 1

        # Carregar regras fiscais vigentes do banco (IR-007) — fallback para hardcoded
        regras_fiscais = _carregar_regras_fiscais(dt_fim)

        # Apurar cada categoria (com PM da tabela posicao e regras dinâmicas)
        res_swing    = IRService._apurar_swing_acoes(swing_acoes, pm_map, regras_fiscais)
        res_dt       = IRService._apurar_day_trade(day_trade, pm_map, regras_fiscais)
        res_fii      = IRService._apurar_fiis(fiis, pm_map, regras_fiscais)
        res_exterior = IRService._apurar_exterior(exterior, pm_map, regras_fiscais)
        res_rf       = IRService._apurar_renda_fixa(resgates_rf, pm_map, data_compra_map, dt_fim)

        # Apurar proventos (IR-004)
        res_proventos = IRService._apurar_proventos(
            proventos_dividendos_br, proventos_jcp,
            proventos_dividendos_us, proventos_aluguel,
            regras_fiscais,
        )

        # --- IR-003: Compensação de prejuízo acumulado ---
        mes_ant = _mes_anterior(ano, mes)
        resultados = {
            'swing_acoes': res_swing,
            'day_trade':   res_dt,
            'fiis':        res_fii,
            'exterior':    res_exterior,
        }
        for cat in CATEGORIAS_FISCAIS:
            res = resultados[cat]
            # Buscar saldo de prejuízo do mês anterior
            saldo_ant = (
                SaldoPrejuizo.query
                .filter_by(usuario_id=usuario_id, categoria=cat, ano_mes=mes_ant)
                .first()
            )
            prejuizo_anterior = Decimal(str(saldo_ant.saldo)) if saldo_ant else Decimal('0')

            lucro_liq = Decimal(str(res['lucro_liquido']))

            if lucro_liq < 0:
                # Mês com prejuízo: acumular (somar ao anterior)
                novo_saldo = prejuizo_anterior + abs(lucro_liq)
                res['prejuizo_compensado'] = 0.0
            elif lucro_liq > 0 and prejuizo_anterior > 0:
                # Mês com lucro + prejuízo anterior: compensar
                compensacao = min(lucro_liq, prejuizo_anterior)
                lucro_apos = lucro_liq - compensacao
                novo_saldo = prejuizo_anterior - compensacao

                # Recalcular IR sobre lucro após compensação
                aliquota = Decimal(str(res['aliquota'])) / 100
                ir_recalculado = Decimal('0')
                if lucro_apos > 0:
                    # Para swing_acoes, respeitar isenção
                    if cat == 'swing_acoes' and res.get('isento'):
                        ir_recalculado = Decimal('0')
                    else:
                        ir_recalculado = (lucro_apos * aliquota).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                res['lucro_liquido'] = float(lucro_apos)
                res['ir_devido'] = ir_recalculado
                res['prejuizo_compensado'] = float(compensacao)
            else:
                novo_saldo = prejuizo_anterior
                res['prejuizo_compensado'] = 0.0

            res['prejuizo_acumulado'] = float(novo_saldo)

            # Persistir novo saldo do mês atual (skip em modo read-only)
            if persist:
                saldo_atual = (
                    SaldoPrejuizo.query
                    .filter_by(usuario_id=usuario_id, categoria=cat, ano_mes=mes_str)
                    .first()
                )
                if saldo_atual:
                    saldo_atual.saldo = novo_saldo
                else:
                    saldo_atual = SaldoPrejuizo(
                        usuario_id=usuario_id,
                        categoria=cat,
                        ano_mes=mes_str,
                        saldo=novo_saldo,
                    )
                    db.session.add(saldo_atual)

        if persist:
            db.session.commit()

        # Totais (após compensação) — forçar Decimal para segurança
        ir_swing    = Decimal(str(resultados['swing_acoes']['ir_devido']))
        ir_dt       = Decimal(str(resultados['day_trade']['ir_devido']))
        ir_fii      = Decimal(str(resultados['fiis']['ir_devido']))
        ir_exterior = Decimal(str(resultados['exterior']['ir_devido']))
        ir_rf       = Decimal(str(res_rf['ir_devido']))
        ir_total    = ir_swing + ir_dt + ir_fii + ir_exterior + ir_rf

        # DARF
        darf = IRService._calcular_darf(usuario_id, mes_str, ir_swing + ir_dt + ir_fii, ir_exterior, ir_rf, persist)

        # Alertas
        alertas = []
        if not pm_map:
            alertas.append(
                "Tabela posicao vazia — execute POST /api/posicoes/calcular antes de apurar IR. "
                "Sem PM, o custo de aquisição será zero e o IR calculado pode ser maior que o real."
            )
        # Coletar alertas de PM não encontrado das categorias
        for res in (res_swing, res_dt, res_fii, res_exterior, res_rf):
            alertas.extend(res.pop('_alertas_pm', []))
        if res_swing.get('isento'):
            alertas.append(f"Vendas de ações em {mes_str} abaixo de R$20.000 — isento de IR (swing trade).")
        # Alerta de DARF < R$10 removido - agora é tratado por acúmulo automático

        # Serializar por_corretora
        corretoras_lista = [
            {
                'corretora_id':   v['corretora_id'],
                'corretora_nome': v['corretora_nome'],
                'total_vendas':   float(v['total_vendas'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'operacoes':      v['operacoes'],
            }
            for v in por_corretora.values()
        ]

        return {
            'mes': mes_str,
            'usuario_id': str(usuario_id),
            'categorias': {
                'swing_acoes': res_swing,
                'day_trade':   res_dt,
                'fiis':        res_fii,
                'exterior':    res_exterior,
                'renda_fixa':  res_rf,
            },
            'proventos': res_proventos,
            'por_corretora': corretoras_lista,
            'ir_total': float(ir_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'darf':    darf,
            'alertas': alertas,
        }

    # -----------------------------------------------------------------------
    # Apuração por categoria
    # -----------------------------------------------------------------------

    @staticmethod
    def _apurar_swing_acoes(vendas: list, pm_map: dict, regras: dict) -> dict:
        """Swing trade ações BR: alíquota e isenção via regra_fiscal (IR-007)."""
        regra = _regra_para_categoria(regras, 'swing_acoes')
        aliquota = regra['aliquota']
        isencao  = regra['isencao'] or ISENCAO_SWING_ACAO

        total_vendas  = sum(Decimal(str(t.valor_total)) for t, _, _ in vendas)
        total_custos  = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        alertas_pm = []

        lucro_bruto = Decimal('0')
        for t, _, ticker in vendas:
            pm = pm_map.get((str(t.ativo_id), str(t.corretora_id)), Decimal('0'))
            if pm == 0:
                alertas_pm.append(f"PM não encontrado para {ticker} — custo de aquisição assumido como zero.")
            custo_aquisicao = pm * Decimal(str(t.quantidade))
            lucro_bruto += Decimal(str(t.valor_total)) - custo_aquisicao

        lucro_liquido = lucro_bruto - total_custos

        isento = total_vendas <= isencao
        ir_devido = Decimal('0')
        if not isento and lucro_liquido > 0:
            ir_devido = (lucro_liquido * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'total_vendas':  float(total_vendas),
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(aliquota * 100),
            'isento':        isento,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
            '_alertas_pm':   alertas_pm,
        }

    @staticmethod
    def _apurar_day_trade(vendas: list, pm_map: dict, regras: dict) -> dict:
        """Day-trade: alíquota via regra_fiscal (IR-007), sem isenção."""
        regra = _regra_para_categoria(regras, 'day_trade')
        aliquota = regra['aliquota']

        alertas_pm = []
        lucro_bruto = Decimal('0')
        for t, _, ticker in vendas:
            pm = pm_map.get((str(t.ativo_id), str(t.corretora_id)), Decimal('0'))
            if pm == 0:
                alertas_pm.append(f"PM não encontrado para {ticker} (day-trade) — custo assumido como zero.")
            custo_aquisicao = pm * Decimal(str(t.quantidade))
            lucro_bruto += Decimal(str(t.valor_total)) - custo_aquisicao

        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(aliquota * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
            '_alertas_pm':   alertas_pm,
        }

    @staticmethod
    def _apurar_fiis(vendas: list, pm_map: dict, regras: dict) -> dict:
        """FIIs: alíquota via regra_fiscal (IR-007), sem isenção."""
        regra = _regra_para_categoria(regras, 'fiis')
        aliquota = regra['aliquota']

        alertas_pm = []
        lucro_bruto = Decimal('0')
        for t, _, ticker in vendas:
            pm = pm_map.get((str(t.ativo_id), str(t.corretora_id)), Decimal('0'))
            if pm == 0:
                alertas_pm.append(f"PM não encontrado para {ticker} (FII) — custo assumido como zero.")
            custo_aquisicao = pm * Decimal(str(t.quantidade))
            lucro_bruto += Decimal(str(t.valor_total)) - custo_aquisicao

        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(aliquota * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
            '_alertas_pm':   alertas_pm,
        }

    @staticmethod
    def _apurar_exterior(vendas: list, pm_map: dict, regras: dict) -> dict:
        """Ativos US/exterior: alíquota via regra_fiscal (IR-007)."""
        regra = _regra_para_categoria(regras, 'exterior')
        aliquota = regra['aliquota']

        alertas_pm = []
        lucro_bruto = Decimal('0')
        for t, _, ticker in vendas:
            pm = pm_map.get((str(t.ativo_id), str(t.corretora_id)), Decimal('0'))
            if pm == 0:
                alertas_pm.append(f"PM não encontrado para {ticker} (exterior) — custo assumido como zero.")
            custo_aquisicao = pm * Decimal(str(t.quantidade))
            lucro_bruto += Decimal(str(t.valor_total)) - custo_aquisicao

        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(aliquota * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
            '_alertas_pm':   alertas_pm,
        }

    # -----------------------------------------------------------------------
    # Proventos (IR-004)
    # -----------------------------------------------------------------------

    @staticmethod
    def _apurar_proventos(
        dividendos_br: list,
        jcp: list,
        dividendos_us: list,
        aluguel: list,
        regras: dict,
    ) -> dict:
        """
        Apura proventos recebidos no mês (IR-004).

        - Dividendos BR: isentos (Lei 9.249/1995) — alíquota 0%
        - JCP: 15% retido na fonte pela empresa pagadora
        - Dividendos US: 15% alíquota BR; 30% retido pelo IRS → crédito na DIRPF
        - Aluguel ações: 15% retido pela corretora (tabela RF simplificada)

        O IR já está retido na fonte (campo `imposto` da transação).
        Não gera DARF a pagar pelo contribuinte neste mês.
        """
        def _aliquota_provento(pais: str, tipo_op: str) -> Decimal:
            chave = (pais, None, tipo_op)
            r = regras.get(chave)
            if r:
                return r['aliquota']
            fallback = {'JCP': Decimal('0.175'), 'DIVIDENDO': Decimal('0'), 'ALUGUEL': Decimal('0.15')}
            return fallback.get(tipo_op, Decimal('0'))

        def _sumarizar(lista: list, pais: str, tipo_op: str) -> dict:
            total_bruto   = sum(Decimal(str(t.valor_total)) for t, _, _ in lista)
            total_retido  = sum(Decimal(str(t.imposto or 0)) for t, _, _ in lista)
            aliquota      = _aliquota_provento(pais, tipo_op)
            ir_esperado   = (total_bruto * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return {
                'valor_bruto':   float(total_bruto),
                'ir_retido':     float(total_retido),
                'ir_esperado':   float(ir_esperado),
                'aliquota':      float(aliquota * 100),
                'operacoes':     len(lista),
                'isento':        aliquota == Decimal('0'),
            }

        # --- Dividendos BR (IR-009): lógica de isenção com limite por fonte pagadora ---
        # Regra pré-2026: 100% isento (alíquota 0%, sem valor_isencao relevante)
        # Regra 2026+: isento até R$50k/mês por ativo_id (proxy CNPJ), 10% acima
        regra_div_br = regras.get(('BR', None, 'DIVIDENDO'))
        regra_div_trib = regras.get(('BR', None, 'DIVIDENDO_TRIBUTADO'))

        if regra_div_trib and regra_div_br and regra_div_br.get('isencao'):
            # Modo 2026+: limite R$50k por ativo_id
            limite_isencao = regra_div_br['isencao']
            aliquota_trib  = regra_div_trib['aliquota']
            total_bruto_div_br  = Decimal('0')
            total_retido_div_br = Decimal('0')
            ir_esperado_div_br  = Decimal('0')

            por_ativo: dict = {}
            for t, _, _ in dividendos_br:
                aid = str(t.ativo_id)
                por_ativo.setdefault(aid, Decimal('0'))
                por_ativo[aid] += Decimal(str(t.valor_total))
                total_retido_div_br += Decimal(str(t.imposto or 0))
                total_bruto_div_br  += Decimal(str(t.valor_total))

            for valor_ativo in por_ativo.values():
                if valor_ativo > limite_isencao:
                    ir_esperado_div_br += (valor_ativo * aliquota_trib).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )

            res_div_br = {
                'valor_bruto':   float(total_bruto_div_br),
                'ir_retido':     float(total_retido_div_br),
                'ir_esperado':   float(ir_esperado_div_br),
                'aliquota':      float(aliquota_trib * 100),
                'operacoes':     len(dividendos_br),
                'isento':        ir_esperado_div_br == Decimal('0'),
                'limite_isencao_por_cnpj': float(limite_isencao),
                'regime':        '2026+',
            }
        else:
            # Modo pré-2026: 100% isento
            res_div_br = _sumarizar(dividendos_br, 'BR', 'DIVIDENDO')
            res_div_br['limite_isencao_por_cnpj'] = None
            res_div_br['regime'] = 'pré-2026'

        res_jcp     = _sumarizar(jcp,           'BR', 'JCP')
        res_div_us  = _sumarizar(dividendos_us, 'US', 'DIVIDENDO')
        res_aluguel = _sumarizar(aluguel,       'BR', 'ALUGUEL')

        ir_retido_total = (
            Decimal(str(res_div_br['ir_retido']))
            + Decimal(str(res_jcp['ir_retido']))
            + Decimal(str(res_div_us['ir_retido']))
            + Decimal(str(res_aluguel['ir_retido']))
        )

        return {
            'dividendos_br':   res_div_br,
            'jcp':             res_jcp,
            'dividendos_us':   res_div_us,
            'aluguel':         res_aluguel,
            'ir_retido_total': float(ir_retido_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'obs': (
                'IR de proventos retido na fonte. '
                'A partir de 2026: dividendos BR tributados em 10% acima de R$50k/mês por empresa (CNPJ). '
                'JCP: 17,5% IRRF (2026+). '
                'Declarar na DIRPF anual para crédito/compensação.'
            ),
        }

    # -----------------------------------------------------------------------
    # Renda Fixa (IR-005)
    # -----------------------------------------------------------------------

    @staticmethod
    def _apurar_renda_fixa(
        resgates: list,
        pm_map: dict,
        data_compra_map: dict,
        dt_ref: date,
    ) -> dict:
        """
        Apura IR sobre resgates de renda fixa (IR-005).

        Regras:
        - CDB / Tesouro Direto / Debêntures: tabela regressiva por prazo
          (≤18 dias 22,5% → 181-360d 20% → 361-720d 17,5% → >720d 15%)
        - LCI/LCA: isento para PF (Lei 12.431)
        - Prazo calculado a partir de `posicao.data_primeira_compra`;
          se não encontrado, assume prazo 0 (alíquota máxima 22,5%).
        - IR é retido na fonte; o campo `imposto` da transação registra o retido.
        - Não gera compensação de prejuízo entre meses.

        Args:
            resgates: lista de (Transacao, tipo_ativo, ticker)
            pm_map: mapa (ativo_id, corretora_id) → preco_medio
            data_compra_map: mapa (ativo_id, corretora_id) → data_primeira_compra
            dt_ref: data de referência do mês (usado para calcular prazo)

        Returns:
            dict com breakdown de renda_fixa compatível com as demais categorias
        """
        if not resgates:
            return {
                'valor_resgatado':  0.0,
                'rendimento_bruto': 0.0,
                'ir_devido':        Decimal('0'),
                'ir_retido':        0.0,
                'iof_devido':       0.0,
                'aliquota_media':   0.0,
                'operacoes':        0,
                'isento':           True,
                'detalhes':         [],
                '_alertas_pm':      [],
            }

        total_resgatado  = Decimal('0')
        total_rendimento = Decimal('0')
        total_ir_devido  = Decimal('0')
        total_ir_retido  = Decimal('0')
        total_iof        = Decimal('0')
        alertas_pm       = []
        detalhes         = []

        for t, tipo_ativo, ticker in resgates:
            valor_resgate = Decimal(str(t.valor_total))
            ir_retido_op  = Decimal(str(t.imposto or 0))

            # Isento para LCI/LCA
            if tipo_ativo in TIPOS_RF_ISENTO:
                detalhes.append({
                    'ticker':    ticker,
                    'tipo':      tipo_ativo.value,
                    'valor':     float(valor_resgate),
                    'aliquota':  0.0,
                    'ir_devido': 0.0,
                    'ir_retido': float(ir_retido_op),
                    'iof_devido': 0.0,
                    'prazo_dias': None,
                    'isento':    True,
                    'motivo_isencao': 'LCI/LCA — isento PF (Lei 12.431)',
                })
                total_resgatado  += valor_resgate
                total_ir_retido  += ir_retido_op
                continue

            # Calcular PM e rendimento
            chave = (str(t.ativo_id), str(t.corretora_id))
            pm = pm_map.get(chave, Decimal('0'))
            if pm == 0:
                alertas_pm.append(
                    f"PM não encontrado para {ticker} (RF) — custo de aquisição assumido como zero."
                )
            custo = pm * Decimal(str(t.quantidade))
            rendimento = valor_resgate - custo - Decimal(str(t.custos_totais or 0))

            # Calcular prazo para tabela regressiva
            data_compra = data_compra_map.get(chave)
            if data_compra:
                dt_resgate = t.data_transacao.date() if hasattr(t.data_transacao, 'date') else t.data_transacao
                prazo_dias = (dt_resgate - data_compra).days
            else:
                prazo_dias = 0  # sem info: assume prazo mínimo (alíquota máxima)

            aliquota = _aliquota_rf(prazo_dias)
            ir_op = Decimal('0')
            if rendimento > 0:
                ir_op = (rendimento * aliquota).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # IOF regressivo (art. 7º Decreto 6.306/2007) — só para prazo < 30 dias
            iof_op = _calcular_iof(prazo_dias, rendimento) if rendimento > 0 else Decimal('0')

            total_resgatado  += valor_resgate
            total_rendimento += rendimento
            total_ir_devido  += ir_op
            total_ir_retido  += ir_retido_op
            total_iof        += iof_op

            detalhes.append({
                'ticker':    ticker,
                'tipo':      tipo_ativo.value,
                'valor':     float(valor_resgate),
                'aliquota':  float(aliquota * 100),
                'ir_devido': float(ir_op),
                'ir_retido': float(ir_retido_op),
                'iof_devido': float(iof_op),
                'prazo_dias': prazo_dias,
                'isento':    False,
                'motivo_isencao': None,
            })

        aliquota_media = (
            float((total_ir_devido / total_rendimento * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            if total_rendimento > 0 else 0.0
        )

        return {
            'valor_resgatado':  float(total_resgatado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'rendimento_bruto': float(total_rendimento.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'ir_devido':        total_ir_devido,
            'ir_retido':        float(total_ir_retido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'iof_devido':       float(total_iof.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'aliquota_media':   aliquota_media,
            'operacoes':        len(resgates),
            'isento':           total_ir_devido == Decimal('0'),
            'detalhes':         detalhes,
            '_alertas_pm':      alertas_pm,
        }

    # -----------------------------------------------------------------------
    # DARF
    # -----------------------------------------------------------------------

    @staticmethod
    def _calcular_darf(usuario_id: str, mes_str: str, ir_br: Decimal, ir_exterior: Decimal, ir_rf: Decimal = Decimal('0'), persist: bool = True) -> dict:
        """
        Monta resumo de DARF a pagar com acúmulo de valores < R$10,00.
        
        Args:
            usuario_id: ID do usuário
            mes_str: Mês no formato YYYY-MM
            ir_br: IR de renda variável BR
            ir_exterior: IR de renda variável exterior
            ir_rf: IR de renda fixa (retido na fonte)
            persist: Se True, persiste saldos acumulados
            
        Returns:
            dict com lista de DARFs
        """
        darfs = []
        mes_ant = _mes_anterior(*_parse_mes(mes_str))
        
        # Processar IR BR (swing + day trade + FIIs)
        if ir_br > 0:
            saldo_acumulado = IRService._processar_acumulo_darf(
                usuario_id, mes_str, mes_ant, 'swing_acoes', DARF_SWING_ACAO, ir_br, persist
            )
            if saldo_acumulado['valor_pagar'] > 0:
                darfs.append({
                    'codigo_receita': DARF_SWING_ACAO,
                    'descricao': 'Ganho de capital — renda variável BR (ações, FIIs, day-trade)',
                    'valor': float(saldo_acumulado['valor_pagar'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'pagar': True,
                    'obs': saldo_acumulado.get('obs'),
                })
        
        # Processar IR Exterior
        if ir_exterior > 0:
            saldo_acumulado = IRService._processar_acumulo_darf(
                usuario_id, mes_str, mes_ant, 'exterior', DARF_RENDA_FIXA, ir_exterior, persist
            )
            if saldo_acumulado['valor_pagar'] > 0:
                darfs.append({
                    'codigo_receita': DARF_RENDA_FIXA,
                    'descricao': 'Ganho de capital — renda variável exterior',
                    'valor': float(saldo_acumulado['valor_pagar'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'pagar': True,
                    'obs': saldo_acumulado.get('obs'),
                })
        
        # IR RF é sempre informativo (retido na fonte)
        if ir_rf > 0:
            darfs.append({
                'codigo_receita': DARF_RENDA_FIXA,
                'descricao': 'IR renda fixa — tabela regressiva (retido na fonte)',
                'valor': float(ir_rf.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'pagar': False,
                'obs': 'Retido na fonte pela instituição financeira — informativo',
            })
        
        return {'darfs': darfs}
    
    @staticmethod
    def _processar_acumulo_darf(usuario_id: str, mes_atual: str, mes_anterior: str, categoria: str, codigo_receita: str, ir_mes: Decimal, persist: bool) -> dict:
        """
        Processa acúmulo de DARF para valores < R$10,00.
        
        Returns:
            dict com:
            - valor_pagar: Valor a pagar neste mês (0 se < R$10)
            - obs: Observação sobre acúmulo
        """
        # Buscar saldo acumulado do mês anterior
        saldo_anterior = SaldoDarfAcumulado.query.filter_by(
            usuario_id=usuario_id,
            categoria=categoria,
            codigo_receita=codigo_receita,
            ano_mes=mes_anterior
        ).first()
        
        valor_anterior = saldo_anterior.saldo if saldo_anterior else Decimal('0')
        valor_total = valor_anterior + ir_mes
        
        if valor_total < DARF_MINIMO:
            # Ainda abaixo do mínimo - acumular
            valor_pagar = Decimal('0')
            obs = f'Abaixo do mínimo (R$10,00) — acumulado: R${valor_total:.2f}'
            
            # Persistir acumulado do mês atual
            if persist:
                saldo_atual = SaldoDarfAcumulado.query.filter_by(
                    usuario_id=usuario_id,
                    categoria=categoria,
                    codigo_receita=codigo_receita,
                    ano_mes=mes_atual
                ).first()
                
                if saldo_atual:
                    saldo_atual.saldo = valor_total
                else:
                    saldo_atual = SaldoDarfAcumulado(
                        usuario_id=usuario_id,
                        categoria=categoria,
                        codigo_receita=codigo_receita,
                        ano_mes=mes_atual,
                        saldo=valor_total
                    )
                    db.session.add(saldo_atual)
        else:
            # Alcançou ou ultrapassou o mínimo - pagar tudo
            valor_pagar = valor_total
            obs = None if valor_anterior == 0 else f'Inclui acumulado de meses anteriores: R${valor_anterior:.2f}'
            
            # Zerar saldo acumulado (já pago)
            if persist:
                saldo_atual = SaldoDarfAcumulado.query.filter_by(
                    usuario_id=usuario_id,
                    categoria=categoria,
                    codigo_receita=codigo_receita,
                    ano_mes=mes_atual
                ).first()
                
                if saldo_atual:
                    saldo_atual.saldo = Decimal('0')
                else:
                    saldo_atual = SaldoDarfAcumulado(
                        usuario_id=usuario_id,
                        categoria=categoria,
                        codigo_receita=codigo_receita,
                        ano_mes=mes_atual,
                        saldo=Decimal('0')
                    )
                    db.session.add(saldo_atual)
        
        return {
            'valor_pagar': valor_pagar,
            'obs': obs
        }

    # -----------------------------------------------------------------------
    # Histórico
    # -----------------------------------------------------------------------

    @staticmethod
    def historico_anual(usuario_id: str, ano: int) -> list:
        """
        Retorna resumo de apuração IR mês a mês para o ano.

        Args:
            usuario_id: UUID do usuário
            ano: ano inteiro (ex: 2025)

        Returns:
            lista de 12 dicts (um por mês), com ir_total e flag isento
        """
        resultado = []
        for mes in range(1, 13):
            mes_str = f'{ano}-{mes:02d}'
            try:
                apuracao = IRService.apurar_mes(usuario_id, mes_str)
                resultado.append({
                    'mes':      mes_str,
                    'ir_total': apuracao['ir_total'],
                    'alertas':  apuracao['alertas'],
                    'operacoes': sum(
                        cat['operacoes']
                        for cat in apuracao['categorias'].values()
                    ),
                })
            except Exception as e:
                logger.warning(f"Erro ao apurar {mes_str}: {e}")
                resultado.append({'mes': mes_str, 'ir_total': 0.0, 'alertas': [], 'operacoes': 0})
        return resultado

    # -----------------------------------------------------------------------
    # DIRPF Anual (IR-006)
    # -----------------------------------------------------------------------

    @staticmethod
    def gerar_dirpf(usuario_id: str, ano: int) -> dict:
        """
        Gera relatório anual para Declaração de Ajuste Anual (DIRPF).

        Fichas geradas:
        - renda_variavel: ganhos/perdas realizados por categoria, IR pago mês a mês
        - proventos: JCP, dividendos BR/US, aluguel recebidos no ano
        - bens_e_direitos: posições em carteira ao final de 31/dez do ano

        Args:
            usuario_id: UUID do usuário
            ano: ano-calendário (ex: 2025)

        Returns:
            dict com fichas DIRPF e totais consolidados
        """
        # ------------------------------------------------------------------
        # Ficha: Renda Variável — agregar os 12 meses
        # ------------------------------------------------------------------
        rv_por_categoria: dict = {
            'swing_acoes': {'lucro': Decimal('0'), 'prejuizo': Decimal('0'), 'ir_pago': Decimal('0'), 'operacoes': 0},
            'day_trade':   {'lucro': Decimal('0'), 'prejuizo': Decimal('0'), 'ir_pago': Decimal('0'), 'operacoes': 0},
            'fiis':        {'lucro': Decimal('0'), 'prejuizo': Decimal('0'), 'ir_pago': Decimal('0'), 'operacoes': 0},
            'exterior':    {'lucro': Decimal('0'), 'prejuizo': Decimal('0'), 'ir_pago': Decimal('0'), 'operacoes': 0},
        }
        # Renda fixa: acumulador separado (IR-005) — sem lucro/prejuízo, só rendimento e IR
        rf_total: dict = {
            'valor_resgatado':  Decimal('0'),
            'rendimento_bruto': Decimal('0'),
            'ir_pago':          Decimal('0'),
            'ir_retido':        Decimal('0'),
            'operacoes':        0,
        }
        prov_total: dict = {
            'dividendos_br': {'valor_bruto': Decimal('0'), 'ir_retido': Decimal('0'), 'operacoes': 0},
            'jcp':           {'valor_bruto': Decimal('0'), 'ir_retido': Decimal('0'), 'operacoes': 0},
            'dividendos_us': {'valor_bruto': Decimal('0'), 'ir_retido': Decimal('0'), 'operacoes': 0},
            'aluguel':       {'valor_bruto': Decimal('0'), 'ir_retido': Decimal('0'), 'operacoes': 0},
        }
        ir_total_ano = Decimal('0')

        for mes in range(1, 13):
            mes_str = f'{ano}-{mes:02d}'
            try:
                ap = IRService.apurar_mes(usuario_id, mes_str, persist=False)
            except Exception as e:
                logger.warning(f"IR-006: erro ao apurar {mes_str}: {e}")
                continue

            # Renda variável (categorias swing/dt/fii/exterior)
            for cat_key, cat in ap['categorias'].items():
                if cat_key == 'renda_fixa':
                    # Acumular RF separadamente
                    rf_total['valor_resgatado']  += Decimal(str(cat.get('valor_resgatado', 0) or 0))
                    rf_total['rendimento_bruto'] += Decimal(str(cat.get('rendimento_bruto', 0) or 0))
                    rf_total['ir_pago']          += Decimal(str(cat.get('ir_devido', 0) or 0))
                    rf_total['ir_retido']        += Decimal(str(cat.get('ir_retido', 0) or 0))
                    rf_total['operacoes']        += int(cat.get('operacoes', 0) or 0)
                    continue
                if cat_key not in rv_por_categoria:
                    continue
                acc = rv_por_categoria[cat_key]
                lucro_mes  = Decimal(str(cat.get('lucro_liquido', 0) or 0))
                ir_mes     = Decimal(str(cat.get('ir_devido', 0) or 0))
                ops        = int(cat.get('operacoes', 0) or 0)
                if lucro_mes >= 0:
                    acc['lucro']    += lucro_mes
                else:
                    acc['prejuizo'] += abs(lucro_mes)
                acc['ir_pago']   += ir_mes
                acc['operacoes'] += ops

            ir_total_ano += Decimal(str(ap.get('ir_total', 0) or 0))

            # Proventos
            prov = ap.get('proventos', {})
            for prov_key in prov_total:
                src = prov.get(prov_key, {})
                acc = prov_total[prov_key]
                acc['valor_bruto'] += Decimal(str(src.get('valor_bruto', 0) or 0))
                acc['ir_retido']   += Decimal(str(src.get('ir_retido', 0) or 0))
                acc['operacoes']   += int(src.get('operacoes', 0) or 0)

        # ------------------------------------------------------------------
        # Ficha: Bens e Direitos — posições em carteira em 31/dez do ano
        # ------------------------------------------------------------------
        dt_fim_ano = date(ano, 12, 31)
        posicoes = (
            Posicao.query
            .filter(Posicao.usuario_id == usuario_id)
            .join(Ativo, Posicao.ativo_id == Ativo.id)
            .all()
        )
        bens = []
        for p in posicoes:
            if p.quantidade and Decimal(str(p.quantidade)) > 0:
                ativo = p.ativo
                bens.append({
                    'ticker':            ativo.ticker,
                    'nome':              ativo.nome,
                    'tipo':              ativo.tipo.value if ativo.tipo else None,
                    'mercado':           ativo.mercado,
                    'quantidade':        float(p.quantidade),
                    'preco_medio':       float(p.preco_medio or 0),
                    'custo_total':       float(p.custo_total or 0),
                    'corretora_id':      str(p.corretora_id),
                    'data_primeira_compra': p.data_primeira_compra.isoformat() if p.data_primeira_compra else None,
                })

        custo_total_carteira = sum((Decimal(str(b['custo_total'])) for b in bens), Decimal('0'))

        # ------------------------------------------------------------------
        # Saldo de prejuízo remanescente ao final do ano
        # ------------------------------------------------------------------
        ultimo_mes = f'{ano}-12'
        saldos_pj = (
            SaldoPrejuizo.query
            .filter(
                SaldoPrejuizo.usuario_id == usuario_id,
                SaldoPrejuizo.ano_mes == ultimo_mes,
            )
            .all()
        )
        prejuizo_remanescente = {
            s.categoria: float(s.saldo or 0)
            for s in saldos_pj
            if (s.saldo or 0) > 0
        }

        # ------------------------------------------------------------------
        # Serializar
        # ------------------------------------------------------------------
        def _ser_rv(acc: dict) -> dict:
            return {
                'lucro':      float(acc['lucro'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'prejuizo':   float(acc['prejuizo'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ir_pago':    float(acc['ir_pago'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'operacoes':  acc['operacoes'],
            }

        def _ser_prov(acc: dict) -> dict:
            return {
                'valor_bruto': float(acc['valor_bruto'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ir_retido':   float(acc['ir_retido'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'operacoes':   acc['operacoes'],
            }

        return {
            'ano':        ano,
            'usuario_id': str(usuario_id),
            'renda_variavel': {
                cat: _ser_rv(acc)
                for cat, acc in rv_por_categoria.items()
            },
            'renda_fixa': {
                'valor_resgatado':  float(rf_total['valor_resgatado'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'rendimento_bruto': float(rf_total['rendimento_bruto'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ir_pago':          float(rf_total['ir_pago'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ir_retido':        float(rf_total['ir_retido'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'operacoes':        rf_total['operacoes'],
            },
            'ir_total_ano': float(ir_total_ano.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'proventos': {
                prov_key: _ser_prov(acc)
                for prov_key, acc in prov_total.items()
            },
            'bens_e_direitos': {
                'posicoes':              bens,
                'total_posicoes':        len(bens),
                'custo_total_carteira':  float(custo_total_carteira.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'data_referencia':       dt_fim_ano.isoformat(),
            },
            'prejuizo_remanescente': prejuizo_remanescente,
            'obs': (
                f'Relatório DIRPF {ano}. '
                'Renda variável: preencher Ficha Renda Variável. '
                'Proventos: preencher Ficha Rendimentos Sujeitos à Tributação Exclusiva (JCP) '
                'e Ficha Rendimentos Isentos (dividendos BR). '
                'Bens e Direitos: preencher com custo de aquisição (preço médio × quantidade).'
            ),
        }
