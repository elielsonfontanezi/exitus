# -*- coding: utf-8 -*-
"""
Exitus - IR Service (EXITUS-IR-001)
Engine de cálculo de Imposto de Renda sobre operações de renda variável.

Regras implementadas (Brasil):
- Swing trade ações: 15% sobre lucro mensal, isenção R$20.000/mês em vendas
- Day-trade (ações/FIIs): 20% sobre lucro, sem isenção
- FIIs: 20% sobre lucro, sem isenção
- Compensação de prejuízo: acumulado entre meses (por categoria: swing/day-trade)
- Proventos (dividendos BR): isentos; JCP: 15% retido na fonte
- DARF: código de receita por categoria

Tabelas usadas: transacao, ativo, regra_fiscal
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

# Valor mínimo de DARF (abaixo disso acumula para mês seguinte)
DARF_MINIMO = Decimal('10.00')

# Tipos de ativo que se enquadram como "ação BR" para isenção de R$20k
TIPOS_ACAO_BR = {TipoAtivo.ACAO}
TIPOS_FII = {TipoAtivo.FII}
TIPOS_US = {TipoAtivo.STOCK, TipoAtivo.REIT, TipoAtivo.ETF, TipoAtivo.BOND}


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

        # Buscar todas as transações do mês (compras e vendas)
        transacoes = (
            Transacao.query
            .filter(
                Transacao.usuario_id == usuario_id,
                Transacao.tipo.in_([TipoTransacao.COMPRA, TipoTransacao.VENDA]),
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

        # Separar por categoria
        swing_acoes   = []   # vendas swing ações BR
        day_trade     = []   # vendas day-trade (qualquer tipo)
        fiis          = []   # vendas FIIs
        exterior      = []   # vendas US/exterior
        compras_todas = []   # todas as compras (para custo médio)

        # Acumulador por corretora: {corretora_id: {nome, vendas, lucro, ir}}
        por_corretora: dict = {}

        for row in transacoes:
            t, tipo_ativo, ticker, corretora_id, corretora_nome = row
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

        # Apurar cada categoria
        res_swing    = IRService._apurar_swing_acoes(swing_acoes)
        res_dt       = IRService._apurar_day_trade(day_trade)
        res_fii      = IRService._apurar_fiis(fiis)
        res_exterior = IRService._apurar_exterior(exterior)

        # Totais
        ir_swing    = res_swing['ir_devido']
        ir_dt       = res_dt['ir_devido']
        ir_fii      = res_fii['ir_devido']
        ir_exterior = res_exterior['ir_devido']
        ir_total    = ir_swing + ir_dt + ir_fii + ir_exterior

        # DARF
        darf = IRService._calcular_darf(ir_swing + ir_dt + ir_fii, ir_exterior)

        # Alertas
        alertas = []
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
            'por_corretora': corretoras_lista,
            'ir_total': float(ir_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'darf':    darf,
            'alertas': alertas,
        }

    # -----------------------------------------------------------------------
    # Apuração por categoria
    # -----------------------------------------------------------------------

    @staticmethod
    def _apurar_swing_acoes(vendas: list) -> dict:
        """Swing trade ações BR: 15%, isenção R$20k/mês em vendas."""
        total_vendas  = sum(Decimal(str(t.valor_total)) for t, _, _ in vendas)
        total_custos  = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        # Lucro estimado: receita líquida - custo de aquisição (preco_unitario × qtd)
        lucro_bruto   = sum(
            Decimal(str(t.valor_total)) - Decimal(str(t.preco_unitario)) * Decimal(str(t.quantidade))
            for t, _, _ in vendas
        )
        lucro_liquido = lucro_bruto - total_custos

        isento = total_vendas <= ISENCAO_SWING_ACAO
        ir_devido = Decimal('0')
        if not isento and lucro_liquido > 0:
            ir_devido = (lucro_liquido * ALIQUOTA_SWING_ACAO).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'total_vendas':  float(total_vendas),
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(ALIQUOTA_SWING_ACAO * 100),
            'isento':        isento,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
        }

    @staticmethod
    def _apurar_day_trade(vendas: list) -> dict:
        """Day-trade: 20%, sem isenção."""
        lucro_bruto  = sum(
            Decimal(str(t.valor_total)) - Decimal(str(t.preco_unitario)) * Decimal(str(t.quantidade))
            for t, _, _ in vendas
        )
        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * ALIQUOTA_DAY_TRADE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(ALIQUOTA_DAY_TRADE * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
        }

    @staticmethod
    def _apurar_fiis(vendas: list) -> dict:
        """FIIs: 20%, sem isenção."""
        lucro_bruto  = sum(
            Decimal(str(t.valor_total)) - Decimal(str(t.preco_unitario)) * Decimal(str(t.quantidade))
            for t, _, _ in vendas
        )
        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * ALIQUOTA_FII).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(ALIQUOTA_FII * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
        }

    @staticmethod
    def _apurar_exterior(vendas: list) -> dict:
        """Ativos US/exterior: 15% ganho de capital."""
        lucro_bruto  = sum(
            Decimal(str(t.valor_total)) - Decimal(str(t.preco_unitario)) * Decimal(str(t.quantidade))
            for t, _, _ in vendas
        )
        total_custos = sum(Decimal(str(t.custos_totais)) for t, _, _ in vendas)
        lucro_liquido = lucro_bruto - total_custos

        ir_devido = Decimal('0')
        if lucro_liquido > 0:
            ir_devido = (lucro_liquido * ALIQUOTA_STOCK_US).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'lucro_liquido': float(lucro_liquido),
            'aliquota':      float(ALIQUOTA_STOCK_US * 100),
            'isento':        False,
            'ir_devido':     ir_devido,
            'operacoes':     len(vendas),
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
