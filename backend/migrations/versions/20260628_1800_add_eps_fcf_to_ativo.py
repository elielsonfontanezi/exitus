"""VALUATION-001 — Adiciona campos eps e fcf ao modelo Ativo

Revision ID: 20260628_1800
Revises: 20260625001
Create Date: 2026-06-28 18:00:00.000000

Adiciona campos eps (Earnings Per Share) e fcf (Free Cash Flow) à tabela ativo
para substituir valores hardcoded em calculos_blueprint.py (Graham e DCF).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260628_1800'
down_revision = '20260625001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ativo', sa.Column('eps', sa.Numeric(precision=10, scale=4), nullable=True,
                  comment='Earnings Per Share — usado por Graham (VALUATION-001)'))
    op.add_column('ativo', sa.Column('fcf', sa.Numeric(precision=15, scale=2), nullable=True,
                  comment='Free Cash Flow — usado por DCF (VALUATION-001)'))


def downgrade() -> None:
    op.drop_column('ativo', 'fcf')
    op.drop_column('ativo', 'eps')
