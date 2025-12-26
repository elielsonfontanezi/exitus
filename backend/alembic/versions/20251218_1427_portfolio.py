"""Criar tabela portfolio

Revision ID: 20251218_1427_portfolio
Revises: 20251208_1004_m7
Create Date: 2025-12-18 14:27:20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251218_1427_portfolio'
down_revision: Union[str, None] = '20251208_1004_m7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria tabela portfolio para agrupamento de posições.
    """

    # ========================================
    # TABELA: portfolio
    # ========================================
    op.create_table(
        'portfolio',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Identificador único do portfolio'),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuário proprietário'),
        sa.Column('nome', sa.String(length=100), nullable=False, comment='Nome do portfolio'),
        sa.Column('descricao', sa.Text(), nullable=True, comment='Descrição detalhada do portfolio'),
        sa.Column('objetivo', sa.String(length=50), nullable=True, comment='Objetivo do portfolio'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Indica se o portfolio está ativo'),
        sa.Column('valor_inicial', sa.Numeric(precision=18, scale=2), nullable=True, comment='Valor inicial investido (R$)'),
        sa.Column('percentual_alocacao_target', sa.Numeric(precision=5, scale=2), nullable=True, comment='% de alocação desejada (0-100)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data de criação do registro'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Data da última atualização'),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),

        sa.CheckConstraint('LENGTH(nome) >= 3', name='portfolio_nome_min_length'),
        sa.CheckConstraint('valor_inicial IS NULL OR valor_inicial >= 0', name='portfolio_valor_inicial_positivo'),
        sa.CheckConstraint('percentual_alocacao_target IS NULL OR (percentual_alocacao_target >= 0 AND percentual_alocacao_target <= 100)', name='portfolio_percentual_valido'),

        comment='Tabela de portfolios (agrupamento de posições)'
    )

    # Índices portfolio
    op.create_index('ix_portfolio_usuario_id', 'portfolio', ['usuario_id'])
    op.create_index('ix_portfolio_ativo', 'portfolio', ['ativo'])
    op.create_index('ix_portfolio_nome', 'portfolio', ['nome'])

    # ========================================
    # ADICIONAR FK em configuracoes_alertas
    # ========================================
    # Agora que a tabela portfolio existe, podemos criar a FK
    op.create_foreign_key(
        'configuracoes_alertas_portfolio_id_fkey',
        'configuracoes_alertas',
        'portfolio',
        ['portfolio_id'],
        ['id'],
        ondelete='CASCADE'
    )

    print("✅ Tabela 'portfolio' criada com sucesso!")
    print("✅ FK 'portfolio_id' em 'configuracoes_alertas' criada!")


def downgrade() -> None:
    """
    Remove tabela portfolio.
    """
    # Remover FK primeiro
    op.drop_constraint('configuracoes_alertas_portfolio_id_fkey', 'configuracoes_alertas', type_='foreignkey')

    # Remover tabela
    op.drop_table('portfolio')

    print("✅ Tabela 'portfolio' removida!")
