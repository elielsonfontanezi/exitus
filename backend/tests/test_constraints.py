# -*- coding: utf-8 -*-
"""
Testes — EXITUS-CONSTRAINT-001
Verifica que CHECK constraints do banco rejeitam dados inválidos.

Estratégia: conexão direta via db.engine + SAVEPOINT para isolar cada INSERT
sem interferir na sessão ORM compartilhada do conftest (scope='session').
"""
import uuid
import pytest
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database import db


# ---------------------------------------------------------------------------
# Helper: executa INSERT raw e espera falha de constraint
# ---------------------------------------------------------------------------

def _uid():
    return str(uuid.uuid4())


def _get_ids(app):
    """Retorna (usuario_id, ativo_id, corretora_id) do banco de teste."""
    with db.engine.connect() as conn:
        uid = conn.execute(text("SELECT id FROM usuario LIMIT 1")).scalar()
        aid = conn.execute(text("SELECT id FROM ativo LIMIT 1")).scalar()
        cid = conn.execute(text("SELECT id FROM corretora LIMIT 1")).scalar()
    return str(uid), str(aid), str(cid)


# ---------------------------------------------------------------------------
# Helper central: executa SQL raw com transação própria
# ---------------------------------------------------------------------------

def _exec(app, sql: str, params: dict, expect_constraint_error: bool = True):
    """
    Abre conexão independente da sessão ORM.
    Executa INSERT dentro de transação que SEMPRE faz rollback.
    Verifica se houve ou não violação de CHECK constraint.
    """
    conn = db.engine.connect()
    trans = conn.begin()
    raised = None
    try:
        conn.execute(text(sql), params)
    except Exception as e:
        raised = e
    finally:
        trans.rollback()
        conn.close()

    if expect_constraint_error:
        assert raised is not None, "IntegrityError esperado mas INSERT foi bem-sucedido"
        err = str(raised).lower()
        assert 'check' in err or 'violates' in err, \
            f"Esperava violação de CHECK constraint, mas got: {raised}"
    else:
        assert raised is None, \
            f"INSERT válido falhou inesperadamente: {raised}"


_SQL_TRANSACAO = """
    INSERT INTO transacao
        (id, usuario_id, ativo_id, corretora_id, data_transacao, tipo,
         quantidade, preco_unitario, valor_total,
         taxa_corretagem, taxa_liquidacao, emolumentos,
         imposto, outros_custos, custos_totais, valor_liquido,
         created_at, updated_at)
    VALUES
        (:id, :uid, :aid, :cid, NOW(), 'compra',
         :qtd, :preco, :total,
         0, 0, 0, 0, 0, 0, :total,
         NOW(), NOW())
"""

_SQL_EVENTO = """
    INSERT INTO evento_custodia
        (id, usuario_id, ativo_id, corretora_id, tipo_evento,
         data_evento, quantidade, valor_operacao, fonte, created_at, updated_at)
    VALUES
        (:id, :uid, :aid, :cid, 'liquidacao_d2',
         NOW(), :qtd, :valor, 'B3_IMPORT', NOW(), NOW())
"""

_SQL_PROJECAO = """
    INSERT INTO projecoes_renda
        (id, usuario_id, mes_ano,
         renda_dividendos_projetada, renda_jcp_projetada,
         renda_rendimentos_projetada, renda_total_mes,
         created_at, updated_at)
    VALUES
        (:id, :uid, :mes,
         :div, :jcp, :rend, :total,
         NOW(), NOW())
"""

_SQL_TAXA = """
    INSERT INTO taxa_cambio
        (id, par_moeda, moeda_base, moeda_cotacao,
         taxa, data_referencia, fonte, created_at)
    VALUES
        (:id, 'USD/BRL', 'USD', 'BRL',
         :taxa, '2025-03-15', 'manual', NOW())
"""


# ---------------------------------------------------------------------------
# Testes: transacao
# ---------------------------------------------------------------------------

class TestTransacaoConstraints:
    def test_quantidade_zero_rejeitada(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 0, 'preco': 38.5, 'total': 3850})

    def test_quantidade_negativa_rejeitada(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': -10, 'preco': 38.5, 'total': 3850})

    def test_preco_unitario_zero_rejeitado(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'preco': 0, 'total': 3850})

    def test_preco_unitario_negativo_rejeitado(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'preco': -1, 'total': 3850})

    def test_valor_total_zero_rejeitado(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'preco': 38.5, 'total': 0})

    def test_transacao_valida_aceita(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_TRANSACAO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'preco': 38.5, 'total': 3850},
              expect_constraint_error=False)


# ---------------------------------------------------------------------------
# Testes: evento_custodia
# ---------------------------------------------------------------------------

class TestEventoCustodiaConstraints:
    def test_quantidade_zero_rejeitada(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_EVENTO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 0, 'valor': 3850})

    def test_valor_operacao_zero_rejeitado(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_EVENTO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'valor': 0})

    def test_evento_valido_aceito(self, app):
        uid, aid, cid = _get_ids(app)
        _exec(app, _SQL_EVENTO,
              {'id': _uid(), 'uid': uid, 'aid': aid, 'cid': cid,
               'qtd': 100, 'valor': 3850},
              expect_constraint_error=False)


# ---------------------------------------------------------------------------
# Testes: projecoes_renda
# ---------------------------------------------------------------------------

class TestProjecaoRendaConstraints:
    def test_renda_dividendos_negativa_rejeitada(self, app):
        uid, _, _ = _get_ids(app)
        _exec(app, _SQL_PROJECAO,
              {'id': _uid(), 'uid': uid, 'mes': '2026-03',
               'div': -1, 'jcp': 100, 'rend': 200, 'total': 800})

    def test_renda_jcp_negativa_rejeitada(self, app):
        uid, _, _ = _get_ids(app)
        _exec(app, _SQL_PROJECAO,
              {'id': _uid(), 'uid': uid, 'mes': '2026-04',
               'div': 500, 'jcp': -1, 'rend': 200, 'total': 800})

    def test_renda_total_negativa_rejeitada(self, app):
        uid, _, _ = _get_ids(app)
        _exec(app, _SQL_PROJECAO,
              {'id': _uid(), 'uid': uid, 'mes': '2026-05',
               'div': 500, 'jcp': 100, 'rend': 200, 'total': -0.01})

    def test_renda_zero_aceita(self, app):
        """Renda zero é válida (posição zerada)."""
        uid, _, _ = _get_ids(app)
        _exec(app, _SQL_PROJECAO,
              {'id': _uid(), 'uid': uid, 'mes': '2099-01',
               'div': 0, 'jcp': 0, 'rend': 0, 'total': 0},
              expect_constraint_error=False)

    def test_projecao_valida_aceita(self, app):
        uid, _, _ = _get_ids(app)
        _exec(app, _SQL_PROJECAO,
              {'id': _uid(), 'uid': uid, 'mes': '2099-02',
               'div': 500, 'jcp': 100, 'rend': 200, 'total': 800},
              expect_constraint_error=False)


# ---------------------------------------------------------------------------
# Testes: taxa_cambio
# ---------------------------------------------------------------------------

class TestTaxaCambioConstraints:
    def test_taxa_zero_rejeitada(self, app):
        _exec(app, _SQL_TAXA, {'id': _uid(), 'taxa': 0})

    def test_taxa_negativa_rejeitada(self, app):
        _exec(app, _SQL_TAXA, {'id': _uid(), 'taxa': -1})

    def test_taxa_valida_aceita(self, app):
        _exec(app, _SQL_TAXA, {'id': _uid(), 'taxa': 5.20},
              expect_constraint_error=False)
