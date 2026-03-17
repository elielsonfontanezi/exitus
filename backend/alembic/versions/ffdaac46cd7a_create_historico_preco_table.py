"""create historico_preco table

Revision ID: ffdaac46cd7a
Revises: 20251218_1427_portfolio
Create Date: 2026-01-06 14:32:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ffdaac46cd7a'
down_revision = '20251218_1427_portfolio'
branch_labels = None
depends_on = None


def upgrade():
    """Cria tabela historico_preco para armazenar histórico diário de preços."""
    
    op.create_table(
        'historico_preco',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ativoid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('preco_abertura', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('preco_fechamento', sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column('preco_minimo', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('preco_maximo', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('createdat', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updatedat', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ativoid'], ['ativo.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ativoid', 'data', name='uq_historico_ativo_data')
    )
    
    # Índice composto para queries por ativo + data descendente
    op.create_index(
        'ix_historico_ativoid_data', 
        'historico_preco', 
        ['ativoid', 'data'],
        unique=False
    )
    
    # Constraints de validação
    op.create_check_constraint(
        'ck_historico_fechamento_positivo',
        'historico_preco',
        'preco_fechamento > 0'
    )
    
    op.create_check_constraint(
        'ck_historico_minmax',
        'historico_preco',
        'preco_minimo IS NULL OR preco_maximo IS NULL OR preco_minimo <= preco_maximo'
    )


def downgrade():
    """Remove tabela historico_preco."""
    
    op.drop_index('ix_historico_ativoid_data', table_name='historico_preco')
    op.drop_table('historico_preco')
