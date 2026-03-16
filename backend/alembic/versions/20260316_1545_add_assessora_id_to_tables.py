"""add assessora_id to tables

Revision ID: 20260316_1545_add_assessora_id_to_tables
Revises: 20260316_1540_create_assessora_table
Create Date: 2026-03-16 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260316_1545_add_assessora_id_to_tables'
down_revision = '20260316_1540_create_assessora_table'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona assessora_id em 20 tabelas para implementar multi-tenancy
    """
    
    # Lista de tabelas que receberão assessora_id
    tables_with_assessora = [
        # Dados do Usuário/Portfolio
        'usuario',
        'portfolio',
        'posicao',
        'transacao',
        'movimentacao_caixa',
        'provento',
        'plano_compra',
        'plano_venda',
        
        # Dados Fiscais
        'saldo_prejuizo',
        'saldo_darf_acumulado',
        
        # Alertas e Relatórios
        'configuracoes_alertas',
        'alertas',
        'relatorios_performance',
        'auditoria_relatorios',
        'projecoes_renda',
        
        # Logs
        'log_auditoria',
        'evento_custodia',
        
        # Dados de Mercado (com tracking)
        'historico_preco',
        'calendario_dividendo',
        'evento_corporativo',
    ]
    
    # Adicionar coluna assessora_id em todas as tabelas
    for table in tables_with_assessora:
        # Adiciona coluna (nullable=True inicialmente para permitir migração)
        op.add_column(table, sa.Column('assessora_id', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Cria foreign key
        op.create_foreign_key(
            f'fk_{table}_assessora_id',
            table, 'assessora',
            ['assessora_id'], ['id'],
            ondelete='CASCADE'
        )
        
        # Cria índice para performance
        op.create_index(f'ix_{table}_assessora_id', table, ['assessora_id'], unique=False)
    
    # Índices compostos para queries frequentes
    op.create_index('ix_usuario_assessora_ativo', 'usuario', ['assessora_id', 'ativo'], unique=False)
    op.create_index('ix_transacao_assessora_data', 'transacao', ['assessora_id', 'data'], unique=False)
    op.create_index('ix_posicao_assessora_ativo', 'posicao', ['assessora_id', 'ativo_id'], unique=False)
    op.create_index('ix_portfolio_assessora_usuario', 'portfolio', ['assessora_id', 'usuario_id'], unique=False)


def downgrade():
    """
    Remove assessora_id de todas as tabelas
    """
    
    tables_with_assessora = [
        'usuario', 'portfolio', 'posicao', 'transacao', 'movimentacao_caixa',
        'provento', 'plano_compra', 'plano_venda', 'saldo_prejuizo',
        'saldo_darf_acumulado', 'configuracoes_alertas', 'alertas',
        'relatorios_performance', 'auditoria_relatorios', 'projecoes_renda',
        'log_auditoria', 'evento_custodia', 'historico_preco',
        'calendario_dividendo', 'evento_corporativo',
    ]
    
    # Drop índices compostos
    op.drop_index('ix_portfolio_assessora_usuario', table_name='portfolio')
    op.drop_index('ix_posicao_assessora_ativo', table_name='posicao')
    op.drop_index('ix_transacao_assessora_data', table_name='transacao')
    op.drop_index('ix_usuario_assessora_ativo', table_name='usuario')
    
    # Remove assessora_id de todas as tabelas
    for table in tables_with_assessora:
        # Drop índice
        op.drop_index(f'ix_{table}_assessora_id', table_name=table)
        
        # Drop foreign key
        op.drop_constraint(f'fk_{table}_assessora_id', table, type_='foreignkey')
        
        # Drop coluna
        op.drop_column(table, 'assessora_id')
