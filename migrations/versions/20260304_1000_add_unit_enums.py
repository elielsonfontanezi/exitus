"""Add UNIT to tipoativo and DESMEMBRAMENTO to tipoeventocorporativo

Revision ID: 20260304_1000
Revises: 20260303_1840
Create Date: 2026-03-04 10:00:00.000000

"""
from alembic import op

revision = '20260304_1000'
down_revision = '20260303_1840'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE tipoativo ADD VALUE IF NOT EXISTS 'UNIT'")
    op.execute("ALTER TYPE tipoeventocorporativo ADD VALUE IF NOT EXISTS 'DESMEMBRAMENTO'")


def downgrade():
    pass
