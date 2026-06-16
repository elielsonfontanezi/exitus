"""add hash_importacao to provento and transacao (VALIDATION-001)

Revision ID: 20260308_1500
Revises: 20260304_2100
Create Date: 2026-03-08 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260308_1500'
down_revision = '20260304_2100'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('provento', sa.Column(
        'hash_importacao',
        sa.String(64),
        nullable=True,
        comment="Hash MD5 da linha original do arquivo B3 para deduplicação"
    ))
    op.add_column('provento', sa.Column(
        'arquivo_origem',
        sa.String(255),
        nullable=True,
        comment="Nome do arquivo B3 de origem da importação"
    ))
    op.create_index(
        'ix_provento_hash_importacao',
        'provento',
        ['hash_importacao'],
        unique=False
    )

    op.add_column('transacao', sa.Column(
        'hash_importacao',
        sa.String(64),
        nullable=True,
        comment="Hash MD5 da linha original do arquivo B3 para deduplicação"
    ))
    op.add_column('transacao', sa.Column(
        'arquivo_origem',
        sa.String(255),
        nullable=True,
        comment="Nome do arquivo B3 de origem da importação"
    ))
    op.create_index(
        'ix_transacao_hash_importacao',
        'transacao',
        ['hash_importacao'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_transacao_hash_importacao', table_name='transacao')
    op.drop_column('transacao', 'arquivo_origem')
    op.drop_column('transacao', 'hash_importacao')

    op.drop_index('ix_provento_hash_importacao', table_name='provento')
    op.drop_column('provento', 'arquivo_origem')
    op.drop_column('provento', 'hash_importacao')
