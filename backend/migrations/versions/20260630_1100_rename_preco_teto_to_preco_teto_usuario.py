"""rename preco_teto to preco_teto_usuario in ativo

BUG-VAL-004: Torna explícita a distinção entre:
  - preco_teto_usuario: teto/preço justo definido manualmente pelo usuário (campo estático)
  - valor_justo: calculado em tempo real pelo valuation_service (não persistido)

Revision ID: 20260630_1100
Revises: 20260628_1800
Create Date: 2026-06-30 11:00:00
"""
from alembic import op

# revision identifiers
revision = '20260630_1100'
down_revision = '20260628_1800'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('ativo', 'preco_teto', new_column_name='preco_teto_usuario')


def downgrade():
    op.alter_column('ativo', 'preco_teto_usuario', new_column_name='preco_teto')
