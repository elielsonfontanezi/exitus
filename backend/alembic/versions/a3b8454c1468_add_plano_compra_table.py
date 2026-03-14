"""Add plano_compra table

Revision ID: a3b8454c1468
Revises: 5f0da25a1ee2
Create Date: 2026-03-14 10:54:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a3b8454c1468'
down_revision = '5f0da25a1ee2'
branch_labels = None
depends_on = None


def upgrade():
    # Criar enum StatusPlanoCompra
    op.execute("CREATE TYPE statusplanocompra AS ENUM ('ativo', 'pausado', 'concluido', 'cancelado')")
    
    # Criar tabela plano_compra
    op.create_table('plano_compra',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ativo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.String(length=500), nullable=True),
        sa.Column('quantidade_alvo', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('quantidade_acumulada', sa.Numeric(precision=15, scale=4), nullable=False, server_default='0'),
        sa.Column('valor_aporte_mensal', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('data_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_fim_prevista', sa.DateTime(), nullable=True),
        sa.Column('data_conclusao', sa.DateTime(), nullable=True),
        sa.Column('status', postgresql.ENUM('ativo', 'pausado', 'concluido', 'cancelado', name='statusplanocompra', create_type=False), nullable=False, server_default='ativo'),
        sa.Column('proximo_aporte', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_plano_compra_usuario_id', 'plano_compra', ['usuario_id'])
    op.create_index('ix_plano_compra_ativo_id', 'plano_compra', ['ativo_id'])
    op.create_index('ix_plano_compra_status', 'plano_compra', ['status'])
    
    # Criar foreign keys
    op.create_foreign_key('fk_plano_compra_usuario', 'plano_compra', 'usuario', ['usuario_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_plano_compra_ativo', 'plano_compra', 'ativo', ['ativo_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Remover foreign keys
    op.drop_constraint('fk_plano_compra_ativo', 'plano_compra', type_='foreignkey')
    op.drop_constraint('fk_plano_compra_usuario', 'plano_compra', type_='foreignkey')
    
    # Remover índices
    op.drop_index('ix_plano_compra_status', table_name='plano_compra')
    op.drop_index('ix_plano_compra_ativo_id', table_name='plano_compra')
    op.drop_index('ix_plano_compra_usuario_id', table_name='plano_compra')
    
    # Remover tabela
    op.drop_table('plano_compra')
    
    # Remover enum
    op.execute("DROP TYPE IF EXISTS statusplanocompra")
