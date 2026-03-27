"""add business CHECK constraints — EXITUS-CONSTRAINT-001

Revision ID: 20260308_1900
Revises: 20260308_1500_add_hash_importacao_validation001
Create Date: 2026-03-08 19:00:00
"""
from alembic import op

revision = '20260308_1900'
down_revision = '20260308_1500'
branch_labels = None
depends_on = None


def upgrade():
    # -----------------------------------------------------------------------
    # transacao — quantidade, preco_unitario e valor_total devem ser > 0
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE transacao
            ADD CONSTRAINT transacao_quantidade_positiva
                CHECK (quantidade > 0),
            ADD CONSTRAINT transacao_preco_unitario_positivo
                CHECK (preco_unitario > 0),
            ADD CONSTRAINT transacao_valor_total_positivo
                CHECK (valor_total > 0)
    """)

    # -----------------------------------------------------------------------
    # evento_custodia — quantidade e valor_operacao devem ser > 0
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE evento_custodia
            ADD CONSTRAINT evento_custodia_quantidade_positiva
                CHECK (quantidade > 0),
            ADD CONSTRAINT evento_custodia_valor_operacao_positivo
                CHECK (valor_operacao > 0)
    """)

    # -----------------------------------------------------------------------
    # projecoes_renda — rendas projetadas não podem ser negativas
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE projecoes_renda
            ADD CONSTRAINT projecao_renda_dividendos_nao_negativo
                CHECK (renda_dividendos_projetada >= 0),
            ADD CONSTRAINT projecao_renda_jcp_nao_negativo
                CHECK (renda_jcp_projetada >= 0),
            ADD CONSTRAINT projecao_renda_rendimentos_nao_negativo
                CHECK (renda_rendimentos_projetada >= 0),
            ADD CONSTRAINT projecao_renda_total_nao_negativo
                CHECK (renda_total_mes >= 0)
    """)

    # -----------------------------------------------------------------------
    # parametros_macro — taxas não podem ser negativas
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE parametros_macro
            ADD CONSTRAINT parametros_taxa_livre_risco_nao_negativa
                CHECK (taxa_livre_risco >= 0),
            ADD CONSTRAINT parametros_inflacao_nao_negativa
                CHECK (inflacao_anual >= 0)
    """)

    # -----------------------------------------------------------------------
    # taxa_cambio — taxa de câmbio deve ser positiva
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE taxa_cambio
            ADD CONSTRAINT taxa_cambio_taxa_positiva
                CHECK (taxa > 0)
    """)

    # -----------------------------------------------------------------------
    # alertas — condicao_valor deve ser positivo
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE alertas
            ADD CONSTRAINT alertas_condicao_valor_positivo
                CHECK (condicao_valor > 0)
    """)


def downgrade():
    op.execute("ALTER TABLE alertas DROP CONSTRAINT IF EXISTS alertas_condicao_valor_positivo")
    op.execute("ALTER TABLE taxa_cambio DROP CONSTRAINT IF EXISTS taxa_cambio_taxa_positiva")
    op.execute("ALTER TABLE parametros_macro DROP CONSTRAINT IF EXISTS parametros_taxa_livre_risco_nao_negativa")
    op.execute("ALTER TABLE parametros_macro DROP CONSTRAINT IF EXISTS parametros_inflacao_nao_negativa")
    op.execute("ALTER TABLE projecoes_renda DROP CONSTRAINT IF EXISTS projecao_renda_dividendos_nao_negativo")
    op.execute("ALTER TABLE projecoes_renda DROP CONSTRAINT IF EXISTS projecao_renda_jcp_nao_negativo")
    op.execute("ALTER TABLE projecoes_renda DROP CONSTRAINT IF EXISTS projecao_renda_rendimentos_nao_negativo")
    op.execute("ALTER TABLE projecoes_renda DROP CONSTRAINT IF EXISTS projecao_renda_total_nao_negativo")
    op.execute("ALTER TABLE evento_custodia DROP CONSTRAINT IF EXISTS evento_custodia_quantidade_positiva")
    op.execute("ALTER TABLE evento_custodia DROP CONSTRAINT IF EXISTS evento_custodia_valor_operacao_positivo")
    op.execute("ALTER TABLE transacao DROP CONSTRAINT IF EXISTS transacao_quantidade_positiva")
    op.execute("ALTER TABLE transacao DROP CONSTRAINT IF EXISTS transacao_preco_unitario_positivo")
    op.execute("ALTER TABLE transacao DROP CONSTRAINT IF EXISTS transacao_valor_total_positivo")
