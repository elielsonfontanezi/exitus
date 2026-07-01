"""Merge RLS and tipomovimentacao heads

Revision ID: 20260624_1100
Revises: 20260403_1040, 20260624_1000
Create Date: 2026-06-24 11:00:00.000000

Merge dos dois heads divergentes:
- 20260403_1040: add Row-Level Security policies (MULTICLIENTE-001 Parte 5)
- 20260624_1000: consolidate tipomovimentacao enum (BUG-021)

Ambas as migrations já foram aplicadas ao banco via DDL manual.
Esta migration apenas unifica a árvore — nenhuma alteração de schema.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260624_1100'
down_revision = ('20260403_1040', '20260624_1000')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
