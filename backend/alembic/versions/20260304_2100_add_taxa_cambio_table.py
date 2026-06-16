"""add taxa_cambio table (MULTIMOEDA-001)

Revision ID: 20260304_2100
Revises: 20260304_2000
Create Date: 2026-03-04 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260304_2100'
down_revision = '20260304_2000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'taxa_cambio',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('par_moeda', sa.String(7), nullable=False,
                  comment='Par de moeda ISO 4217 (ex: BRL/USD, BRL/EUR, USD/BRL)'),
        sa.Column('moeda_base', sa.String(3), nullable=False,
                  comment='Moeda base do par (ex: BRL)'),
        sa.Column('moeda_cotacao', sa.String(3), nullable=False,
                  comment='Moeda de cotação do par (ex: USD)'),
        sa.Column('taxa', sa.Numeric(precision=18, scale=8), nullable=False,
                  comment='Taxa de câmbio: 1 moeda_base = taxa * moeda_cotacao'),
        sa.Column('data_referencia', sa.Date(), nullable=False,
                  comment='Data de referência da cotação'),
        sa.Column('fonte', sa.String(50), nullable=False, server_default='manual',
                  comment='Fonte da cotação (yfinance, bcb, manual, etc.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('ix_taxa_cambio_par_data',
                    'taxa_cambio', ['par_moeda', 'data_referencia'])
    op.create_index('ix_taxa_cambio_data_referencia',
                    'taxa_cambio', ['data_referencia'])
    op.create_unique_constraint('uq_taxa_cambio_par_data',
                                'taxa_cambio', ['par_moeda', 'data_referencia'])


def downgrade() -> None:
    op.drop_constraint('uq_taxa_cambio_par_data', 'taxa_cambio', type_='unique')
    op.drop_index('ix_taxa_cambio_data_referencia', table_name='taxa_cambio')
    op.drop_index('ix_taxa_cambio_par_data', table_name='taxa_cambio')
    op.drop_table('taxa_cambio')
