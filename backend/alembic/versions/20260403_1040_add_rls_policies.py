"""add Row-Level Security policies — MULTICLIENTE-001 Parte 5

Revision ID: 20260403_1040
Revises: 20260308_1900
Create Date: 2026-04-03 10:40:00

Implementa políticas de Row-Level Security (RLS) no PostgreSQL para garantir
isolamento automático de dados por assessora no nível do banco de dados.

Tabelas com RLS:
- portfolio
- transacao
- posicao
- provento
- movimentacao_caixa
- plano_compra
- plano_venda
- alerta
- evento_custodia
- projecoes_renda

Políticas criadas:
- SELECT: Permite acesso apenas a registros da assessora atual
- INSERT: Força assessora_id = assessora atual
- UPDATE: Permite atualizar apenas registros da assessora atual
- DELETE: Permite deletar apenas registros da assessora atual

Contexto: app.current_assessora_id deve ser setado via SET LOCAL antes de queries
"""
from alembic import op

revision = '20260403_1040'
down_revision = '20260322_1830'
branch_labels = None
depends_on = None


def upgrade():
    """
    Habilita Row-Level Security (RLS) nas tabelas multi-tenant e cria políticas
    de acesso baseadas em assessora_id.
    """
    
    # Lista de tabelas que possuem assessora_id e precisam de RLS
    tables_with_rls = [
        'portfolio',
        'transacao',
        'posicao',
        'provento',
        'movimentacao_caixa',
        'plano_compra',
        'plano_venda',
        'alerta',
        'evento_custodia',
        'projecoes_renda'
    ]
    
    for table in tables_with_rls:
        # -----------------------------------------------------------------------
        # 1. Habilitar RLS na tabela
        # -----------------------------------------------------------------------
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        
        # -----------------------------------------------------------------------
        # 2. Política SELECT: Ver apenas registros da própria assessora
        # -----------------------------------------------------------------------
        op.execute(f"""
            CREATE POLICY {table}_select_policy ON {table}
                FOR SELECT
                USING (
                    assessora_id::text = current_setting('app.current_assessora_id', true)
                    OR current_setting('app.current_assessora_id', true) IS NULL
                )
        """)
        
        # -----------------------------------------------------------------------
        # 3. Política INSERT: Inserir apenas com assessora_id da sessão
        # -----------------------------------------------------------------------
        op.execute(f"""
            CREATE POLICY {table}_insert_policy ON {table}
                FOR INSERT
                WITH CHECK (
                    assessora_id::text = current_setting('app.current_assessora_id', true)
                    OR current_setting('app.current_assessora_id', true) IS NULL
                )
        """)
        
        # -----------------------------------------------------------------------
        # 4. Política UPDATE: Atualizar apenas registros da própria assessora
        # -----------------------------------------------------------------------
        op.execute(f"""
            CREATE POLICY {table}_update_policy ON {table}
                FOR UPDATE
                USING (
                    assessora_id::text = current_setting('app.current_assessora_id', true)
                    OR current_setting('app.current_assessora_id', true) IS NULL
                )
        """)
        
        # -----------------------------------------------------------------------
        # 5. Política DELETE: Deletar apenas registros da própria assessora
        # -----------------------------------------------------------------------
        op.execute(f"""
            CREATE POLICY {table}_delete_policy ON {table}
                FOR DELETE
                USING (
                    assessora_id::text = current_setting('app.current_assessora_id', true)
                    OR current_setting('app.current_assessora_id', true) IS NULL
                )
        """)
    
    # -----------------------------------------------------------------------
    # Criar função helper para setar o contexto de assessora
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION set_current_assessora(assessora_uuid TEXT)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_assessora_id', assessora_uuid, false);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # -----------------------------------------------------------------------
    # Criar função helper para limpar o contexto
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION clear_current_assessora()
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_assessora_id', NULL, false);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade():
    """
    Remove políticas RLS e desabilita RLS nas tabelas.
    """
    
    tables_with_rls = [
        'portfolio',
        'transacao',
        'posicao',
        'provento',
        'movimentacao_caixa',
        'plano_compra',
        'plano_venda',
        'alerta',
        'evento_custodia',
        'projecoes_renda'
    ]
    
    # Remover funções helper
    op.execute("DROP FUNCTION IF EXISTS set_current_assessora(TEXT)")
    op.execute("DROP FUNCTION IF EXISTS clear_current_assessora()")
    
    for table in tables_with_rls:
        # Remover políticas
        op.execute(f"DROP POLICY IF EXISTS {table}_select_policy ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_insert_policy ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_update_policy ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_delete_policy ON {table}")
        
        # Desabilitar RLS
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
