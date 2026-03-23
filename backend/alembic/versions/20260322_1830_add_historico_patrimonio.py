"""add historico_patrimonio table

Revision ID: 20260322_1830
Revises: 20260315_2100
Create Date: 2026-03-22 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260322_1830'
down_revision = '20260316_1545'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('historico_patrimonio',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('data', sa.Date(), nullable=False, comment='Último dia do mês do snapshot'),
    sa.Column('patrimonio_total', sa.Numeric(precision=15, scale=2), nullable=False, comment='Patrimônio total (posições + caixa)'),
    sa.Column('patrimonio_renda_variavel', sa.Numeric(precision=15, scale=2), server_default='0', nullable=True, comment='Valor em renda variável'),
    sa.Column('patrimonio_renda_fixa', sa.Numeric(precision=15, scale=2), server_default='0', nullable=True, comment='Valor em renda fixa'),
    sa.Column('saldo_caixa', sa.Numeric(precision=15, scale=2), server_default='0', nullable=True, comment='Saldo disponível em caixa'),
    sa.Column('observacoes', sa.Text(), nullable=True, comment='Observações sobre o período'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id', 'data', name='uq_historico_patrimonio_usuario_data')
    )
    op.create_index('idx_historico_patrimonio_data', 'historico_patrimonio', ['data'], unique=False)
    op.create_index('idx_historico_patrimonio_usuario_data', 'historico_patrimonio', ['usuario_id', 'data'], unique=False)


def downgrade():
    op.drop_index('idx_historico_patrimonio_usuario_data', table_name='historico_patrimonio')
    op.drop_index('idx_historico_patrimonio_data', table_name='historico_patrimonio')
    op.drop_table('historico_patrimonio')
