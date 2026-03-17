"""add rfcalc fields to ativo (RFCALC-001)

Revision ID: 20260304_1900
Revises: 20260303_1840
Create Date: 2026-03-04 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260304_1900'
down_revision = '20260303_1840'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Campos de Renda Fixa
    op.add_column('ativo', sa.Column('taxa_cupom', sa.Numeric(precision=8, scale=6), nullable=True,
                  comment='Taxa de cupom anual (ex: 0.1050 = 10,50% a.a.)'))
    op.add_column('ativo', sa.Column('valor_nominal', sa.Numeric(precision=15, scale=2), nullable=True,
                  comment='Valor nominal/face do título (ex: 1000.00)'))
    op.add_column('ativo', sa.Column('data_vencimento', sa.Date(), nullable=True,
                  comment='Data de vencimento do título de renda fixa'))

    # Campos de FII/REIT
    op.add_column('ativo', sa.Column('ffo_por_cota', sa.Numeric(precision=10, scale=4), nullable=True,
                  comment='Funds From Operations por cota (FFO — FII/REIT)'))
    op.add_column('ativo', sa.Column('affo_por_cota', sa.Numeric(precision=10, scale=4), nullable=True,
                  comment='Adjusted FFO por cota (AFFO — FFO menos capex de manutenção)'))

    # Índice para busca de títulos com vencimento
    op.create_index('ix_ativo_data_vencimento', 'ativo', ['data_vencimento'])


def downgrade() -> None:
    op.drop_index('ix_ativo_data_vencimento', table_name='ativo')
    op.drop_column('ativo', 'affo_por_cota')
    op.drop_column('ativo', 'ffo_por_cota')
    op.drop_column('ativo', 'data_vencimento')
    op.drop_column('ativo', 'valor_nominal')
    op.drop_column('ativo', 'taxa_cupom')
