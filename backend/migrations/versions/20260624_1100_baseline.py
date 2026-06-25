"""Baseline — estado do banco em 24/06/2026 (tabelas criadas via db.create_all)

Revision ID: 20260624_1100
Revises: 
Create Date: 2026-06-24 11:00:00.000000

Este arquivo é um stub de baseline. As tabelas já existem no banco,
criadas via Flask-SQLAlchemy db.create_all(). Esta revision apenas
ancora o histórico do Alembic ao estado real do banco.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260624_1100'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
