# -*- coding: utf-8 -*-
"""
Exitus - Business Rules (EXITUS-BUSINESS-001)

Regras de negócio para validação de transações:
1. Validação de horário de mercado (warning)
2. Validação de feriados (warning)
3. Validação de saldo antes de venda (bloqueante)
4. Cálculo automático de taxas B3
5. Detecção de day-trade
"""

from decimal import Decimal
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

# Imports de models no topo para permitir mock em testes unitários
# (imports circulares evitados pois db é inicializado antes dos utils)
from app.models.feriado_mercado import FeriadoMercado
from app.models.posicao import Posicao
from app.models.transacao import Transacao


# ---------------------------------------------------------------------------
# Constantes de mercado
# ---------------------------------------------------------------------------
HORARIOS_MERCADO = {
    'B3': {'abertura': time(10, 0), 'fechamento': time(17, 0)},
    'NYSE': {'abertura': time(9, 30), 'fechamento': time(16, 0)},
    'NASDAQ': {'abertura': time(9, 30), 'fechamento': time(16, 0)},
}

# Taxas B3 padrão (mercado à vista, ações)
TAXAS_B3 = {
    'emolumentos': Decimal('0.00003297'),      # 0.003297%
    'taxa_liquidacao': Decimal('0.000275'),     # 0.0275%
}


# ---------------------------------------------------------------------------
# 1. Validação de horário de mercado (warning, não bloqueia)
# ---------------------------------------------------------------------------
def validar_horario_mercado(data_transacao, mercado='B3'):
    """
    Verifica se a transação ocorreu dentro do horário de pregão.

    Args:
        data_transacao: datetime da transação
        mercado: código do mercado (B3, NYSE, NASDAQ)

    Returns:
        str or None: mensagem de warning, ou None se OK
    """
    if not isinstance(data_transacao, datetime):
        return None

    horario = HORARIOS_MERCADO.get(mercado.upper())
    if not horario:
        return None

    hora_transacao = data_transacao.time()
    if hora_transacao < horario['abertura'] or hora_transacao > horario['fechamento']:
        return (
            f"Transação fora do horário de pregão {mercado} "
            f"({horario['abertura'].strftime('%H:%M')}-"
            f"{horario['fechamento'].strftime('%H:%M')}). "
            f"Hora registrada: {hora_transacao.strftime('%H:%M')}"
        )
    return None


# ---------------------------------------------------------------------------
# 2. Validação de feriados (warning, não bloqueia)
# ---------------------------------------------------------------------------
def validar_feriado(data_transacao, mercado=None):
    """
    Verifica se a data da transação cai em um feriado cadastrado.

    Args:
        data_transacao: datetime ou date da transação
        mercado: código do mercado (opcional, para filtrar feriados)

    Returns:
        str or None: mensagem de warning, ou None se OK
    """
    if isinstance(data_transacao, datetime):
        data = data_transacao.date()
    else:
        data = data_transacao

    query = FeriadoMercado.query.filter_by(data_feriado=data)
    if mercado:
        query = query.filter(
            (FeriadoMercado.mercado == mercado.upper()) |
            (FeriadoMercado.mercado.is_(None))
        )

    feriado = query.first()
    if feriado:
        return (
            f"Data da transação ({data.isoformat()}) coincide com feriado: "
            f"{feriado.nome} ({feriado.tipo_feriado.value})"
        )
    return None


# ---------------------------------------------------------------------------
# 3. Validação de saldo antes de venda (BLOQUEANTE)
# ---------------------------------------------------------------------------
def validar_saldo_venda(usuario_id, ativo_id, quantidade_venda, corretora_id=None):
    """
    Verifica se o usuário possui saldo suficiente para a venda.

    Args:
        usuario_id: UUID do usuário
        ativo_id: UUID do ativo
        quantidade_venda: Decimal com quantidade a vender
        corretora_id: UUID da corretora (opcional, para validar saldo na corretora)

    Returns:
        None se OK

    Raises:
        ValueError: se saldo insuficiente
    """
    query = Posicao.query.filter_by(
        usuario_id=usuario_id,
        ativo_id=ativo_id,
    )
    if corretora_id:
        query = query.filter_by(corretora_id=corretora_id)

    posicoes = query.all()

    if not posicoes:
        raise ValueError(
            f"Venda rejeitada: não há posição neste ativo para venda"
        )

    saldo_total = sum(p.quantidade or Decimal('0') for p in posicoes)

    if Decimal(str(quantidade_venda)) > saldo_total:
        raise ValueError(
            f"Saldo insuficiente para venda. "
            f"Disponível: {float(saldo_total)}, "
            f"Solicitado: {float(quantidade_venda)}"
        )


# ---------------------------------------------------------------------------
# 4. Cálculo automático de taxas B3
# ---------------------------------------------------------------------------
def calcular_taxas_b3(valor_operacao):
    """
    Calcula taxas padrão da B3 (mercado à vista).

    Args:
        valor_operacao: Decimal com valor total da operação

    Returns:
        dict com emolumentos e taxa_liquidacao calculados
    """
    valor = Decimal(str(valor_operacao))
    return {
        'emolumentos': round(valor * TAXAS_B3['emolumentos'], 2),
        'taxa_liquidacao': round(valor * TAXAS_B3['taxa_liquidacao'], 2),
    }


# ---------------------------------------------------------------------------
# 5. Detecção de day-trade
# ---------------------------------------------------------------------------
def detectar_day_trade(usuario_id, ativo_id, data_transacao, tipo_transacao):
    """
    Detecta se a transação configura day-trade (compra e venda no mesmo dia).

    Args:
        usuario_id: UUID do usuário
        ativo_id: UUID do ativo
        data_transacao: datetime da transação
        tipo_transacao: 'compra' ou 'venda'

    Returns:
        bool: True se configura day-trade
    """
    if tipo_transacao not in ('compra', 'venda'):
        return False

    tipo_oposto = 'venda' if tipo_transacao == 'compra' else 'compra'

    if isinstance(data_transacao, datetime):
        data = data_transacao.date()
    else:
        data = data_transacao

    from sqlalchemy import cast
    from sqlalchemy.types import Date

    existe = Transacao.query.filter(
        Transacao.usuario_id == usuario_id,
        Transacao.ativo_id == ativo_id,
        cast(Transacao.data_transacao, Date) == data,
        Transacao.tipo == tipo_oposto,
    ).first()

    return existe is not None


# ---------------------------------------------------------------------------
# Função orquestradora: validar transação completa
# ---------------------------------------------------------------------------
def validar_transacao(usuario_id, data, mercado='B3'):
    """
    Executa todas as regras de negócio para uma transação.

    Args:
        usuario_id: UUID do usuário
        data: dict com dados da transação (tipo, ativo_id, quantidade, etc.)
        mercado: código do mercado

    Returns:
        dict com:
            - warnings: lista de avisos (não bloqueantes)
            - is_day_trade: bool
            - taxas_calculadas: dict com taxas B3 (se aplicável)

    Raises:
        ValueError: se alguma regra bloqueante falhar (ex: saldo insuficiente)
    """
    warnings = []
    resultado = {
        'warnings': warnings,
        'is_day_trade': False,
        'taxas_calculadas': None,
    }

    tipo = data.get('tipo', '').lower()
    data_transacao = data.get('data_transacao')

    # 1. Warning: horário de mercado
    try:
        w = validar_horario_mercado(data_transacao, mercado)
        if w:
            warnings.append(w)
    except Exception as e:
        logger.warning(f"Erro ao validar horário: {e}")

    # 2. Warning: feriado
    try:
        w = validar_feriado(data_transacao, mercado)
        if w:
            warnings.append(w)
    except Exception as e:
        logger.warning(f"Erro ao validar feriado: {e}")

    # 3. BLOQUEANTE: saldo para venda
    if tipo == 'venda':
        validar_saldo_venda(
            usuario_id,
            data.get('ativo_id'),
            data.get('quantidade'),
            data.get('corretora_id'),
        )

    # 4. Cálculo automático de taxas B3
    if tipo in ('compra', 'venda'):
        quantidade = Decimal(str(data.get('quantidade', 0)))
        preco = Decimal(str(data.get('preco_unitario', 0)))
        valor_operacao = quantidade * preco
        resultado['taxas_calculadas'] = calcular_taxas_b3(valor_operacao)

    # 5. Detecção day-trade
    if tipo in ('compra', 'venda'):
        try:
            resultado['is_day_trade'] = detectar_day_trade(
                usuario_id,
                data.get('ativo_id'),
                data_transacao,
                tipo,
            )
            if resultado['is_day_trade']:
                warnings.append(
                    "Day-trade detectado: operação inversa no mesmo ativo/dia. "
                    "Alíquota de IR aplicável: 20% (ao invés de 15%)"
                )
        except Exception as e:
            logger.warning(f"Erro ao detectar day-trade: {e}")

    return resultado
