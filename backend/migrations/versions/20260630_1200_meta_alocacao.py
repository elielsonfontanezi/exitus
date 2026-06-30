"""add meta_alocacao table — REBALANCE-001

Persiste percentuais-alvo por classe de ativo por usuário.
Usado por rebalance_service para calcular desvios e sugestões.

Revision ID: 20260630_1200
Revises: 20260630_1100
Create Date: 2026-06-30 12:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260630_1200'
down_revision = '20260630_1100'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'meta_alocacao',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()'),
                  comment='Identificador único'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('usuario.id', ondelete='CASCADE'),
                  nullable=False, index=True,
                  comment='Usuário proprietário da meta'),
        sa.Column('assessora_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('assessora.id', ondelete='CASCADE'),
                  nullable=True, index=True,
                  comment='Assessora (multi-tenancy)'),
        sa.Column('classe', sa.String(30), nullable=False,
                  comment='Classe de ativo: renda_variavel | renda_fixa | cripto'),
        sa.Column('percentual_target', sa.Numeric(5, 2), nullable=False,
                  comment='Percentual-alvo desta classe (0–100)'),
        sa.Column('tolerancia_pct', sa.Numeric(4, 2), nullable=False,
                  server_default='2.00',
                  comment='Tolerância em pp antes de sinalizar desvio (default 2%)'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('usuario_id', 'classe', name='uq_meta_alocacao_usuario_classe'),
        sa.CheckConstraint(
            "percentual_target >= 0 AND percentual_target <= 100",
            name='chk_meta_alocacao_percentual_valido'
        ),
        sa.CheckConstraint(
            "tolerancia_pct >= 0 AND tolerancia_pct <= 50",
            name='chk_meta_alocacao_tolerancia_valida'
        ),
        sa.CheckConstraint(
            "classe IN ('renda_variavel', 'renda_fixa', 'cripto')",
            name='chk_meta_alocacao_classe_valida'
        ),
    )


def downgrade():
    op.drop_table('meta_alocacao')
