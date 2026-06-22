"""add ativo_classificacao_cache table (BUG-020)

Revision ID: 20260621_1300
Revises: 20260322_1830
Create Date: 2026-06-21 13:00:00.000000

Cria tabela de cache para classificações de ativos (seeds, manuais, API,
heurística), com nível de confiança e rastreabilidade de fonte.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20260621_1300'
down_revision: Union[str, None] = '20260322_1830'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria enums de forma idempotente
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE fonteclassificacao AS ENUM ('seed', 'manual', 'api', 'heuristica');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE nivelconfianca AS ENUM ('alta', 'media', 'baixa');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)

    op.create_table(
        'ativo_classificacao_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticker', sa.String(20), nullable=False),
        sa.Column('tipo', postgresql.ENUM(
            'acao', 'fii', 'cdb', 'lci_lca', 'tesouro_direto', 'debenture',
            'stock', 'reit', 'bond', 'etf', 'stock_intl', 'etf_intl', 'unit',
            'cripto', 'outro',
            name='tipoativo',
            create_type=False,
        ), nullable=False),
        sa.Column('classe', postgresql.ENUM(
            'renda_variavel', 'renda_fixa', 'cripto', 'commodity', 'hibrido',
            name='classeativo',
            create_type=False,
        ), nullable=False),
        sa.Column('mercado', sa.String(10), nullable=False),
        sa.Column('moeda', sa.String(3), nullable=False),
        sa.Column('fonte', postgresql.ENUM(
            'seed', 'manual', 'api', 'heuristica',
            name='fonteclassificacao',
            create_type=False,
        ), nullable=False),
        sa.Column('confianca', postgresql.ENUM(
            'alta', 'media', 'baixa',
            name='nivelconfianca',
            create_type=False,
        ), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('observacoes', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'usuario_id', name='uq_ativo_classificacao_cache_ticker_usuario'),
    )
    op.create_index('ix_ativo_classificacao_cache_ticker', 'ativo_classificacao_cache', ['ticker'])
    op.create_index('ix_ativo_classificacao_cache_usuario_id', 'ativo_classificacao_cache', ['usuario_id'])
    op.create_index(
        'ix_ativo_classificacao_cache_ticker_fonte',
        'ativo_classificacao_cache',
        ['ticker', 'fonte'],
    )


def downgrade() -> None:
    op.drop_index('ix_ativo_classificacao_cache_ticker_fonte', table_name='ativo_classificacao_cache')
    op.drop_index('ix_ativo_classificacao_cache_usuario_id', table_name='ativo_classificacao_cache')
    op.drop_index('ix_ativo_classificacao_cache_ticker', table_name='ativo_classificacao_cache')
    op.drop_table('ativo_classificacao_cache')
    op.execute("DROP TYPE IF EXISTS nivelconfianca")
    op.execute("DROP TYPE IF EXISTS fonteclassificacao")
