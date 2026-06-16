"""Add performance indexes

Revision ID: add_performance_indexes
Revises: a3b8454c1468
Create Date: 2026-03-14 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = 'a3b8454c1468'
branch_labels = None
depends_on = None


def upgrade():
    # Índices para tabela posicao
    op.execute("CREATE INDEX IF NOT EXISTS idx_posicao_usuario_id ON posicao(usuario_id);")
    
    # Índices para tabela transacao
    op.execute("CREATE INDEX IF NOT EXISTS idx_transacao_usuario_data ON transacao(usuario_id, data_transacao);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_transacao_usuario_ativo ON transacao(usuario_id, ativo_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_transacao_usuario_tipo ON transacao(usuario_id, tipo);")
    
    # Índices para tabela plano_compra
    op.execute("CREATE INDEX IF NOT EXISTS idx_plano_usuario_status ON plano_compra(usuario_id, status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_plano_status ON plano_compra(status);")
    
    # Índices para tabela ativo
    op.execute("CREATE INDEX IF NOT EXISTS idx_ativo_ticker ON ativo(ticker);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ativo_tipo ON ativo(tipo);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ativo_mercado ON ativo(mercado);")
    
    # Índices para tabela provento (ajustado - não tem usuario_id)
    op.execute("CREATE INDEX IF NOT EXISTS idx_provento_ativo_data ON provento(ativo_id, data_pagamento);")
    
    # Índices para tabela historico_preco (já existe ix_historico_ativoid_data)
    # op.execute("CREATE INDEX IF NOT EXISTS idx_historico_preco_ativo_data ON historico_preco(ativoid, data);")
    
    # Índices compostos para queries comuns
    op.execute("CREATE INDEX IF NOT EXISTS idx_transacao_usuario_data_tipo ON transacao(usuario_id, data_transacao, tipo);")


def downgrade():
    # Remover índices criados
    op.drop_index('idx_posicao_usuario_id', table_name='posicao')
    op.drop_index('idx_transacao_usuario_data', table_name='transacao')
    op.drop_index('idx_transacao_usuario_ativo', table_name='transacao')
    op.drop_index('idx_transacao_usuario_tipo', table_name='transacao')
    op.drop_index('idx_plano_usuario_status', table_name='plano_compra')
    op.drop_index('idx_plano_status', table_name='plano_compra')
    op.drop_index('idx_ativo_ticker', table_name='ativo')
    op.drop_index('idx_ativo_tipo', table_name='ativo')
    op.drop_index('idx_ativo_mercado', table_name='ativo')
    op.drop_index('idx_provento_ativo_data', table_name='provento')
    # op.drop_index('idx_historico_preco_ativo_data', table_name='historico_preco')
    op.drop_index('idx_transacao_usuario_data_tipo', table_name='transacao')
