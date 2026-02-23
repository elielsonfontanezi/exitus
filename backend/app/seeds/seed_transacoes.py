# -- coding: utf-8 --
"""
Exitus - Seed de Transações
Popula tabela transacao com dados de teste para admin, joao.silva e teste.user.
IMPORTANTE: Este seed cria a corretora de teste.user se ela não existir.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.database import db
from app.models import (
    Transacao, TipoTransacao,
    Usuario, Ativo, Corretora, TipoCorretora
)
from decimal import Decimal
from datetime import datetime

app = create_app()


def _get_ou_criar_corretora(usuario, nome, tipo=TipoCorretora.CORRETORA,
                             pais='BR', moeda='BRL'):
    """Busca corretora por usuário+nome. Cria se não existir."""
    corretora = Corretora.query.filter_by(
        usuario_id=usuario.id, nome=nome
    ).first()
    if not corretora:
        corretora = Corretora(
            usuario_id   = usuario.id,
            nome         = nome,
            tipo         = tipo,
            pais         = pais,
            moeda_padrao = moeda,
            saldo_atual  = Decimal('0.00'),
            ativa        = True
        )
        db.session.add(corretora)
        db.session.flush()  # garante que corretora.id existe antes das transações
        print(f"  [corretora] CRIADA: {nome} para {usuario.username}")
    else:
        print(f"  [corretora] JÁ EXISTE: {nome} para {usuario.username}")
    return corretora


def _add_trx(usuario_id, tipo, ativo, corretora, data_str,
             quantidade, preco,
             taxa_corretagem='0', taxa_liquidacao='0',
             emolumentos='0', imposto='0', outros_custos='0',
             observacoes=None):
    """
    Cria transação idempotente.
    Chave de idempotência: usuario_id + ativo_id + corretora_id + tipo + data + quantidade.
    """
    if not ativo:
        print(f"  SKIP: ativo não encontrado")
        return
    if not corretora:
        print(f"  SKIP: corretora não encontrada")
        return

    qtd    = Decimal(str(quantidade))
    preco_d = Decimal(str(preco))
    tc     = Decimal(str(taxa_corretagem))
    tl     = Decimal(str(taxa_liquidacao))
    em     = Decimal(str(emolumentos))
    imp    = Decimal(str(imposto))
    oc     = Decimal(str(outros_custos))
    data   = datetime.fromisoformat(data_str)

    # Idempotência: não duplica em re-runs
    existe = Transacao.query.filter_by(
        usuario_id   = usuario_id,
        ativo_id     = ativo.id,
        corretora_id = corretora.id,
        tipo         = tipo,
        data_transacao = data,
        quantidade   = qtd
    ).first()
    if existe:
        print(f"  JÁ EXISTE: {tipo.value:12} {ativo.ticker:8} {float(qtd):>8.0f} uni @ R${float(preco_d):>8.2f}  {data_str[:10]}")
        return

    valor_total   = qtd * preco_d
    custos_totais = tc + tl + em + imp + oc

    if tipo == TipoTransacao.COMPRA:
        valor_liquido = valor_total + custos_totais
    elif tipo == TipoTransacao.VENDA:
        valor_liquido = valor_total - custos_totais
    else:
        # DIVIDENDO, JCP, etc.
        valor_liquido = valor_total - imp

    t = Transacao(
        usuario_id      = usuario_id,
        tipo            = tipo,
        ativo_id        = ativo.id,
        corretora_id    = corretora.id,
        data_transacao  = data,
        quantidade      = qtd,
        preco_unitario  = preco_d,
        valor_total     = valor_total,
        taxa_corretagem = tc,
        taxa_liquidacao = tl,
        emolumentos     = em,
        imposto         = imp,
        outros_custos   = oc,
        custos_totais   = custos_totais,
        valor_liquido   = valor_liquido,
        observacoes     = observacoes
    )
    db.session.add(t)
    print(f"  CRIADO:    {tipo.value:12} {ativo.ticker:8} {float(qtd):>8.0f} uni @ R${float(preco_d):>8.2f}  {data_str[:10]}")


def seed_transacoes():
    with app.app_context():
        print("=" * 60)
        print("SEED Transações")
        print("=" * 60)

        # ── Usuários ────────────────────────────────────────────────
        admin = Usuario.query.filter_by(username='admin').first()
        joao  = Usuario.query.filter_by(username='joao.silva').first()
        teste = Usuario.query.filter_by(username='teste.user').first()

        for nome, u in [('admin', admin), ('joao.silva', joao), ('teste.user', teste)]:
            if not u:
                print(f"AVISO: usuário '{nome}' não encontrado. Execute seed_usuarios primeiro.")

        # ── Ativos ──────────────────────────────────────────────────
        def ativo(ticker):
            return Ativo.query.filter_by(ticker=ticker, mercado='BR').first()

        petr4  = ativo('PETR4')
        vale3  = ativo('VALE3')
        itub4  = ativo('ITUB4')
        knri11 = ativo('KNRI11')
        mxrf11 = ativo('MXRF11')
        wege3  = ativo('WEGE3')

        # ── Corretoras ──────────────────────────────────────────────
        # admin: primeira corretora disponível
        admin_corr = Corretora.query.filter_by(usuario_id=admin.id).first() if admin else None

        # joao.silva: XP + Clear (criadas pelo seed_modulo2)
        joao_xp    = Corretora.query.filter_by(usuario_id=joao.id, nome='XP Investimentos').first() if joao else None
        joao_clear = Corretora.query.filter_by(usuario_id=joao.id, nome='Clear Corretora').first() if joao else None

        # teste.user: cria XP Investimentos se não existir
        teste_corr = _get_ou_criar_corretora(teste, 'XP Investimentos') if teste else None

        # ════════════════════════════════════════════════════════════
        # ADMIN
        # ════════════════════════════════════════════════════════════
        if admin and admin_corr:
            print(f"\n[admin] → corretora: {admin_corr.nome}")
            _add_trx(admin.id, TipoTransacao.COMPRA, petr4, admin_corr,
                     '2025-03-10T10:00:00', 200, '35.20',
                     taxa_corretagem='2.50', emolumentos='0.30',
                     observacoes='Seed admin - compra PETR4')
            _add_trx(admin.id, TipoTransacao.VENDA, petr4, admin_corr,
                     '2025-09-15T14:00:00', 100, '38.50',
                     taxa_corretagem='2.50', emolumentos='0.30',
                     observacoes='Seed admin - venda parcial PETR4')
            _add_trx(admin.id, TipoTransacao.COMPRA, vale3, admin_corr,
                     '2025-04-05T10:30:00', 100, '60.00',
                     taxa_corretagem='2.50', emolumentos='0.30',
                     observacoes='Seed admin - compra VALE3')
        else:
            print("\n[admin] SKIP: usuário ou corretora não encontrados")

        # ════════════════════════════════════════════════════════════
        # JOAO.SILVA — ações (XP) + FII (Clear) + múltiplos aportes
        # ════════════════════════════════════════════════════════════
        if joao and joao_xp:
            print(f"\n[joao.silva] → corretora XP: {joao_xp.nome}")
            _add_trx(joao.id, TipoTransacao.COMPRA, itub4, joao_xp,
                     '2025-05-12T09:30:00', 300, '27.00',
                     taxa_corretagem='3.00', taxa_liquidacao='0.50', emolumentos='0.40',
                     observacoes='Seed joao - compra ITUB4')
            _add_trx(joao.id, TipoTransacao.COMPRA, itub4, joao_xp,
                     '2025-07-20T10:15:00', 200, '28.10',
                     taxa_corretagem='3.00', taxa_liquidacao='0.50', emolumentos='0.40',
                     observacoes='Seed joao - aporte ITUB4')
            _add_trx(joao.id, TipoTransacao.VENDA, itub4, joao_xp,
                     '2025-10-08T11:45:00', 100, '29.50',
                     taxa_corretagem='3.00', taxa_liquidacao='0.50', emolumentos='0.40',
                     observacoes='Seed joao - venda parcial ITUB4')
            _add_trx(joao.id, TipoTransacao.COMPRA, wege3, joao_xp,
                     '2025-09-02T10:00:00', 150, '40.80',
                     taxa_corretagem='3.00', emolumentos='0.30',
                     observacoes='Seed joao - compra WEGE3')
        else:
            print("\n[joao.silva/XP] SKIP: usuário ou corretora XP não encontrados")

        if joao and joao_clear:
            print(f"\n[joao.silva] → corretora Clear: {joao_clear.nome}")
            _add_trx(joao.id, TipoTransacao.COMPRA, knri11, joao_clear,
                     '2025-06-03T10:00:00', 50, '95.00',
                     taxa_corretagem='2.00', emolumentos='0.20',
                     observacoes='Seed joao - compra KNRI11')
            _add_trx(joao.id, TipoTransacao.COMPRA, knri11, joao_clear,
                     '2025-08-18T10:00:00', 30, '97.50',
                     taxa_corretagem='2.00', emolumentos='0.20',
                     observacoes='Seed joao - aporte KNRI11')
        else:
            print("\n[joao.silva/Clear] SKIP: usuário ou corretora Clear não encontrados")

        # ════════════════════════════════════════════════════════════
        # TESTE.USER — perfil simples: valida isolamento multi-tenant
        # ════════════════════════════════════════════════════════════
        if teste and teste_corr:
            print(f"\n[teste.user] → corretora: {teste_corr.nome}")
            _add_trx(teste.id, TipoTransacao.COMPRA, mxrf11, teste_corr,
                     '2025-06-15T09:00:00', 400, '10.10',
                     taxa_corretagem='1.50',
                     observacoes='Seed teste - compra MXRF11')
            _add_trx(teste.id, TipoTransacao.COMPRA, mxrf11, teste_corr,
                     '2025-09-22T09:00:00', 200, '10.20',
                     taxa_corretagem='1.50',
                     observacoes='Seed teste - aporte MXRF11')
            _add_trx(teste.id, TipoTransacao.VENDA, mxrf11, teste_corr,
                     '2025-11-10T14:30:00', 100, '10.30',
                     taxa_corretagem='1.50',
                     observacoes='Seed teste - venda parcial MXRF11')
            _add_trx(teste.id, TipoTransacao.COMPRA, vale3, teste_corr,
                     '2025-07-07T10:00:00', 50, '61.00',
                     taxa_corretagem='2.00',
                     observacoes='Seed teste - compra VALE3')
        else:
            print("\n[teste.user] SKIP: usuário não encontrado")

        # ── Commit final ────────────────────────────────────────────
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("SEED TRANSAÇÕES CONCLUÍDO!")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"ERRO ao commitar: {e}")
            raise


if __name__ == '__main__':
    seed_transacoes()
