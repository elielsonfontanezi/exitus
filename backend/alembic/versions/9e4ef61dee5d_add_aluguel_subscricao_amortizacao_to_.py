"""add_aluguel_subscricao_amortizacao_to_tipotransacao

Revision ID: 9e4ef61dee5d
Revises: 202602162130
Create Date: 2026-02-23
"""
from alembic import op

revision = '9e4ef61dee5d'
down_revision = '202602162130'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipotransacao') THEN
                ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'aluguel';
                ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'subscricao';
                ALTER TYPE tipotransacao ADD VALUE IF NOT EXISTS 'amortizacao';
            END IF;
        END $$
    """)


def downgrade():
    pass
