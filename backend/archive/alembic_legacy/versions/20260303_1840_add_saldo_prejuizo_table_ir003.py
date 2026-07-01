"""add saldo_prejuizo table (IR-003)

Revision ID: 20260303_1840
Revises: 20260223_2110
Create Date: 2026-03-03 18:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260303_1840'
down_revision = '20260223_2110'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'saldo_prejuizo',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('categoria', sa.String(20), nullable=False),
        sa.Column('ano_mes', sa.String(7), nullable=False),
        sa.Column('saldo', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'categoria', 'ano_mes',
                            name='unique_saldo_prejuizo_usuario_categoria_mes'),
        sa.CheckConstraint(
            "categoria IN ('swing_acoes', 'day_trade', 'fiis', 'exterior')",
            name='saldo_prejuizo_categoria_valida'
        ),
        sa.CheckConstraint('saldo >= 0', name='saldo_prejuizo_nao_negativo'),
        comment='Saldo de prejuízo acumulado por categoria fiscal (IR-003)',
    )
    op.create_index('ix_saldo_prejuizo_usuario_id', 'saldo_prejuizo', ['usuario_id'])


def downgrade() -> None:
    op.drop_index('ix_saldo_prejuizo_usuario_id', table_name='saldo_prejuizo')
    op.drop_table('saldo_prejuizo')
