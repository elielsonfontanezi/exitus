"""CONSTRAINT-001 — Adiciona CHECK constraints nas tabelas transacao, evento_custodia, projecoes_renda e taxa_cambio

Revision ID: 20260625001
Revises: 
Create Date: 2026-06-25 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '20260625001'
down_revision = '20260624_1100'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # transacao: quantidade > 0, preco_unitario > 0, valor_total > 0
    # ------------------------------------------------------------------
    op.create_check_constraint(
        'ck_transacao_quantidade_positiva',
        'transacao',
        'quantidade > 0'
    )
    op.create_check_constraint(
        'ck_transacao_preco_positivo',
        'transacao',
        'preco_unitario > 0'
    )
    op.create_check_constraint(
        'ck_transacao_valor_total_positivo',
        'transacao',
        'valor_total > 0'
    )

    # ------------------------------------------------------------------
    # evento_custodia: quantidade > 0, valor_operacao > 0
    # ------------------------------------------------------------------
    op.create_check_constraint(
        'ck_evento_custodia_quantidade_positiva',
        'evento_custodia',
        'quantidade > 0'
    )
    op.create_check_constraint(
        'ck_evento_custodia_valor_positivo',
        'evento_custodia',
        'valor_operacao > 0'
    )

    # ------------------------------------------------------------------
    # projecoes_renda: todos os campos >= 0
    # ------------------------------------------------------------------
    op.create_check_constraint(
        'ck_projecoes_renda_dividendos_nao_negativo',
        'projecoes_renda',
        'renda_dividendos_projetada >= 0'
    )
    op.create_check_constraint(
        'ck_projecoes_renda_jcp_nao_negativo',
        'projecoes_renda',
        'renda_jcp_projetada >= 0'
    )
    op.create_check_constraint(
        'ck_projecoes_renda_rendimentos_nao_negativo',
        'projecoes_renda',
        'renda_rendimentos_projetada >= 0'
    )
    op.create_check_constraint(
        'ck_projecoes_renda_total_nao_negativo',
        'projecoes_renda',
        'renda_total_mes >= 0'
    )

    # ------------------------------------------------------------------
    # taxa_cambio: taxa > 0
    # ------------------------------------------------------------------
    op.create_check_constraint(
        'ck_taxa_cambio_taxa_positiva',
        'taxa_cambio',
        'taxa > 0'
    )


def downgrade():
    op.drop_constraint('ck_taxa_cambio_taxa_positiva', 'taxa_cambio', type_='check')

    op.drop_constraint('ck_projecoes_renda_total_nao_negativo', 'projecoes_renda', type_='check')
    op.drop_constraint('ck_projecoes_renda_rendimentos_nao_negativo', 'projecoes_renda', type_='check')
    op.drop_constraint('ck_projecoes_renda_jcp_nao_negativo', 'projecoes_renda', type_='check')
    op.drop_constraint('ck_projecoes_renda_dividendos_nao_negativo', 'projecoes_renda', type_='check')

    op.drop_constraint('ck_evento_custodia_valor_positivo', 'evento_custodia', type_='check')
    op.drop_constraint('ck_evento_custodia_quantidade_positiva', 'evento_custodia', type_='check')

    op.drop_constraint('ck_transacao_valor_total_positivo', 'transacao', type_='check')
    op.drop_constraint('ck_transacao_preco_positivo', 'transacao', type_='check')
    op.drop_constraint('ck_transacao_quantidade_positiva', 'transacao', type_='check')
