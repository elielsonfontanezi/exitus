"""add saldo_darf_acumulado table (DARF-ACUMULADO-001)

Revision ID: 5f0da25a1ee2
Revises: 20260308_1900
Create Date: 2026-03-09 11:03:54.126311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5f0da25a1ee2'
down_revision: Union[str, None] = '20260308_1900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'saldo_darf_acumulado',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('categoria', sa.String(20), nullable=False),
        sa.Column('codigo_receita', sa.String(10), nullable=False),
        sa.Column('ano_mes', sa.String(7), nullable=False),
        sa.Column('saldo', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'categoria', 'codigo_receita', 'ano_mes',
                            name='unique_saldo_darf_usuario_categoria_codigo_mes'),
        sa.CheckConstraint(
            "categoria IN ('swing_acoes', 'day_trade', 'fiis', 'exterior', 'rf')",
            name='saldo_darf_categoria_valida'
        ),
        sa.CheckConstraint(
            "codigo_receita IN ('6015', '0561', '9453')",
            name='saldo_darf_codigo_receita_valido'
        ),
        sa.CheckConstraint('saldo >= 0', name='saldo_darf_nao_negativo'),
        comment='Saldo de DARF acumulado por categoria e código de receita (DARF-ACUMULADO-001)'
    )
    op.create_index('ix_saldo_darf_acumulado_usuario_id', 'saldo_darf_acumulado', ['usuario_id'])


def downgrade() -> None:
    op.drop_index('ix_saldo_darf_acumulado_usuario_id', table_name='saldo_darf_acumulado')
    op.drop_table('saldo_darf_acumulado')
