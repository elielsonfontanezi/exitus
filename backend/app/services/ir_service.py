# -*- coding: utf-8 -*-
"""
Exitus - IR Service (EXITUS-IR-001 + IR-002 + IR-003 + IR-004)
Engine de cálculo de Imposto de Renda sobre operações de renda variável.

Regras implementadas (Brasil):
- Swing trade ações: 15% sobre lucro mensal, isenção R$20.000/mês em vendas
- Day-trade (ações/FIIs): 20% sobre lucro, sem isenção
- FIIs: 20% sobre lucro, sem isenção
- Custo de aquisição via preço médio ponderado (PM) da tabela `posicao` (IR-002)
- Compensação de prejuízo acumulado entre meses por categoria (IR-003)
- Proventos (IR-004): dividendos BR isentos, JCP 15% retido na fonte, dividendos US 15% CRÉDITO IRS, aluguel 15%
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
TIPOS_ACAO_BR = {TipoAtivo.ACAO}
TIPOS_FII = {TipoAtivo.FII}
TIPOS_US = {TipoAtivo.STOCK, TipoAtivo.REIT, TipoAtivo.ETF, TipoAtivo.BOND}
TIPOS_BR = {TipoAtivo.ACAO, TipoAtivo.FII, TipoAtivo.CDB, TipoAtivo.LCI_LCA,
            TipoAtivo.TESOURO_DIRETO, TipoAtivo.DEBENTURE}


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
    def apurar_mes(usuario_id: str, mes_str: str) -> dict:
        """
        Apura IR de renda variável para um mês/usuário.

        Args:
            usuario_id: UUID do usuário (string)
            mes_str: mês no formato 'YYYY-MM'

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

        # Separar por categoria
        swing_acoes   = []   # vendas swing ações BR
        day_trade     = []   # vendas day-trade (qualquer tipo)
        fiis          = []   # vendas FIIs
        exterior      = []   # vendas US/exterior
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

            if is_dt:
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

            # Persistir novo saldo do mês atual
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

        db.session.commit()

        # Totais (após compensação)
        ir_swing    = resultados['swing_acoes']['ir_devido']
        ir_dt       = resultados['day_trade']['ir_devido']
        ir_fii      = resultados['fiis']['ir_devido']
        ir_exterior = resultados['exterior']['ir_devido']
        ir_total    = ir_swing + ir_dt + ir_fii + ir_exterior

        # DARF
        darf = IRService._calcular_darf(ir_swing + ir_dt + ir_fii, ir_exterior)

        # Alertas
        alertas = []
        if not pm_map:
            alertas.append(
                "Tabela posicao vazia — execute POST /api/posicoes/calcular antes de apurar IR. "
                "Sem PM, o custo de aquisição será zero e o IR calculado pode ser maior que o real."
            )
        # Coletar alertas de PM não encontrado das categorias
        for res in (res_swing, res_dt, res_fii, res_exterior):
            alertas.extend(res.pop('_alertas_pm', []))
        if res_swing.get('isento'):
            alertas.append(f"Vendas de ações em {mes_str} abaixo de R$20.000 — isento de IR (swing trade).")
        if ir_total < DARF_MINIMO and ir_total > 0:
            alertas.append(f"IR total R${ir_total:.2f} abaixo do mínimo de DARF (R$10,00) — acumular para mês seguinte.")

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
            fallback = {'JCP': Decimal('0.15'), 'DIVIDENDO': Decimal('0'), 'ALUGUEL': Decimal('0.15')}
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

        res_div_br  = _sumarizar(dividendos_br, 'BR', 'DIVIDENDO')
        res_jcp     = _sumarizar(jcp,           'BR', 'JCP')
        res_div_us  = _sumarizar(dividendos_us, 'US', 'DIVIDENDO')
        res_aluguel = _sumarizar(aluguel,       'BR', 'ALUGUEL')

        ir_retido_total = (
            Decimal(str(res_jcp['ir_retido']))
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
                'Dividendos BR isentos até 2025. '
                'Declarar na DIRPF anual para crédito/compensação.'
            ),
        }

    # -----------------------------------------------------------------------
    # DARF
    # -----------------------------------------------------------------------

    @staticmethod
    def _calcular_darf(ir_br: Decimal, ir_exterior: Decimal) -> dict:
        """Monta resumo de DARF a pagar."""
        darfs = []

        if ir_br > 0:
            darfs.append({
                'codigo_receita': DARF_SWING_ACAO,
                'descricao':      'Ganho de capital — renda variável BR (ações, FIIs, day-trade)',
                'valor':          float(ir_br.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'pagar':          ir_br >= DARF_MINIMO,
                'obs':            None if ir_br >= DARF_MINIMO else f'Abaixo do mínimo (R$10,00) — acumular',
            })

        if ir_exterior > 0:
            darfs.append({
                'codigo_receita': DARF_RENDA_FIXA,
                'descricao':      'Ganho de capital — renda variável exterior',
                'valor':          float(ir_exterior.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'pagar':          ir_exterior >= DARF_MINIMO,
                'obs':            None if ir_exterior >= DARF_MINIMO else f'Abaixo do mínimo (R$10,00) — acumular',
            })

        return darfs

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
