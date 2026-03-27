"""create assessora table

Revision ID: 20260316_1540_create_assessora_table
Revises: create_plano_venda_table, d9777a483f02
Create Date: 2026-03-16 15:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260316_1540_assessora'
down_revision = ('create_plano_venda_table', 'd9777a483f02')
branch_labels = None
depends_on = None


def upgrade():
    # Create assessora table
    op.create_table('assessora',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('razao_social', sa.String(length=200), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('site', sa.String(length=200), nullable=True),
        sa.Column('endereco', sa.Text(), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=True),
        sa.Column('cep', sa.String(length=9), nullable=True),
        sa.Column('numero_cvm', sa.String(length=50), nullable=True),
        sa.Column('anbima', sa.Boolean(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('data_cadastro', sa.DateTime(), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('cor_primaria', sa.String(length=7), nullable=True),
        sa.Column('cor_secundaria', sa.String(length=7), nullable=True),
        sa.Column('max_usuarios', sa.Integer(), nullable=True),
        sa.Column('max_portfolios', sa.Integer(), nullable=True),
        sa.Column('plano', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_assessora_nome', 'assessora', ['nome'], unique=True)
    op.create_index('ix_assessora_cnpj', 'assessora', ['cnpj'], unique=True)
    op.create_index('ix_assessora_email', 'assessora', ['email'], unique=True)
    op.create_index('ix_assessora_ativo', 'assessora', ['ativo'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('ix_assessora_ativo', table_name='assessora')
    op.drop_index('ix_assessora_email', table_name='assessora')
    op.drop_index('ix_assessora_cnpj', table_name='assessora')
    op.drop_index('ix_assessora_nome', table_name='assessora')
    
    # Drop table
    op.drop_table('assessora')
