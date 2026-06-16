"""Create plano_venda table

Revision ID: create_plano_venda_table
Revises: add_performance_indexes
Create Date: 2026-03-14 11:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_plano_venda_table'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE statusplanoventa AS ENUM ('ativo', 'pausado', 'concluido', 'cancelado');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipogatilho AS ENUM ('preco_alvo', 'percentual_lucro', 'parcelas_semanais', 'parcelas_mensais', 'data_limite', 'gatilho_misto');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
    """)
    
    # Create plano_venda table
    op.create_table('plano_venda',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ativo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantidade_total', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('quantidade_vendida', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('preco_minimo', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('preco_alvo', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('tipo_gatilho', sa.Enum('preco_alvo', 'percentual_lucro', 'parcelas_semanais', 'parcelas_mensais', 'data_limite', 'gatilho_misto', name='tipogatilho'), nullable=False),
        sa.Column('gatilho_valor', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column('data_limite', sa.Date(), nullable=True),
        sa.Column('parcelas_total', sa.Integer(), nullable=True),
        sa.Column('parcelas_executadas', sa.Integer(), nullable=False),
        sa.Column('valor_parcela_fixo', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('status', sa.Enum('ativo', 'pausado', 'concluido', 'cancelado', name='statusplanoventa'), nullable=False),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('data_conclusao', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ativo_id'], ['ativo.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_plano_venda_usuario_id', 'plano_venda', ['usuario_id'], unique=False)
    op.create_index('ix_plano_venda_ativo_id', 'plano_venda', ['ativo_id'], unique=False)
    op.create_index('ix_plano_venda_status', 'plano_venda', ['status'], unique=False)
    op.create_index('ix_plano_venda_usuario_status', 'plano_venda', ['usuario_id', 'status'], unique=False)


def downgrade():
    # Drop table
    op.drop_table('plano_venda')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS statusplanoventa")
    op.execute("DROP TYPE IF EXISTS tipogatilho")
