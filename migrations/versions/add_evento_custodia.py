"""Add evento_custodia table

Revision ID: add_evento_custodia
Revises: 
Create Date: 2026-03-02 18:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'add_evento_custodia'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create evento_custodia table
    op.create_table('evento_custodia',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('usuario_id', sa.UUID(as_uuid=True), sa.ForeignKey('usuario.id'), nullable=False),
        sa.Column('ativo_id', sa.UUID(as_uuid=True), sa.ForeignKey('ativo.id'), nullable=False),
        sa.Column('corretora_id', sa.UUID(as_uuid=True), sa.ForeignKey('corretora.id'), nullable=False),
        sa.Column('tipo_evento', sa.Enum('LIQUIDACAO_D2', 'TRANSFERENCIA_ENTRADA', 'TRANSFERENCIA_SAIDA', 'AJUSTE_POSICAO', 'DESDOBRAMENTO', 'AGRUPAMENTO', 'AMORTIZACAO', 'OUTRO', name='tipo_evento_custodia'), nullable=False),
        sa.Column('data_evento', sa.DateTime(), nullable=False),
        sa.Column('quantidade', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('valor_operacao', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('observacoes', sa.Text()),
        sa.Column('fonte', sa.String(length=50), default='B3_IMPORT'),
        sa.Column('dados_origem', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('preco_unitario', sa.Numeric(precision=18, scale=6), nullable=True),
        sa.ForeignKeyConstraint(['ativo_id'], ['ativo.id'], ),
        sa.ForeignKeyConstraint(['corretora_id'], ['corretora.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], )
    )
    
    # Create indexes
    op.create_index('ix_evento_custodia_usuario_id', 'evento_custodia', ['usuario_id'])
    op.create_index('ix_evento_custodia_ativo_id', 'evento_custodia', ['ativo_id'])
    op.create_index('ix_evento_custodia_tipo_evento', 'evento_custodia', ['tipo_evento'])
    op.create_index('ix_evento_custodia_data_evento', 'evento_custodia', ['data_evento'])


def downgrade():
    op.drop_table('evento_custodia')
    # Drop enum type if it exists
    op.execute("DROP TYPE IF EXISTS tipo_evento_custodia")
