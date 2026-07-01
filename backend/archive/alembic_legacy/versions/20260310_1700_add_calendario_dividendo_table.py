"""Add calendario_dividendo table

Revision ID: 20260310_1700
Revises: 5f0da25a1ee2
Create Date: 2026-03-10 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260310_1700'
down_revision = '5f0da25a1ee2'
branch_labels = None
depends_on = None


def upgrade():
    # Create calendario_dividendo table
    op.create_table('calendario_dividendo',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ativo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_esperada', sa.Date(), nullable=False, comment='Data prevista do provento'),
        sa.Column('tipo_provento', sa.String(20), nullable=False, default='dividendo', comment='Tipo do provento'),
        sa.Column('yield_estimado', sa.Numeric(precision=8, scale=4), nullable=True, comment='Yield percentual estimado'),
        sa.Column('valor_estimado', sa.Numeric(precision=18, scale=2), nullable=True, comment='Valor em R$ estimado'),
        sa.Column('quantidade', sa.Integer(), nullable=False, default=0, comment='Quantidade de ativos'),
        sa.Column('status', sa.String(20), nullable=False, default='previsto', comment='Status do calendário'),
        sa.Column('observacoes', sa.Text(), nullable=True, comment='Observações adicionais'),
        sa.Column('data_pagamento', sa.Date(), nullable=True, comment='Data real do pagamento'),
        sa.Column('valor_real', sa.Numeric(precision=18, scale=2), nullable=True, comment='Valor real pago'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ativo_id'], ['ativo.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('quantidade >= 0', name='ck_calendario_quantidade_positiva'),
        comment='Calendário de proventos futuros para planejamento'
    )
    
    # Create indexes
    op.create_index('idx_calendario_usuario_data', 'calendario_dividendo', ['usuario_id', 'data_esperada'], unique=False)
    op.create_index('idx_calendario_ativo_data', 'calendario_dividendo', ['ativo_id', 'data_esperada'], unique=False)
    op.create_index('idx_calendario_status', 'calendario_dividendo', ['status'], unique=False)
    op.create_index('idx_calendario_usuario_ativo', 'calendario_dividendo', ['usuario_id', 'ativo_id'], unique=False)


def downgrade():
    op.drop_table('calendario_dividendo')
