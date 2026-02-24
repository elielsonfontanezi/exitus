"""add_aluguel_subscricao_amortizacao_to_tipotransacao

Revision ID: 9e4ef61dee5d
Revises: 202602162130
Create Date: 2026-02-23
"""
from alembic import op


def upgrade():
    op.execute("ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'aluguel'")
    op.execute("ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'subscricao'")
    op.execute("ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'amortizacao'")


def downgrade():
    # ADD VALUE em ENUM PostgreSQL não é reversível sem recriar o tipo
    pass
