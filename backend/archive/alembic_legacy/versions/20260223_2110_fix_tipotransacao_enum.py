"""fix_tipotransacao_enum_lowercase_and_add_missing_values

Revision ID: 20260223_2110
Revises: 9e4ef61dee5d
Create Date: 2026-02-23
"""
from alembic import op

revision = '20260223_2110'
down_revision = '9e4ef61dee5d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TYPE tipotransacao_new AS ENUM (
            'compra', 'venda', 'dividendo', 'jcp',
            'aluguel', 'bonificacao', 'split',
            'grupamento', 'subscricao', 'amortizacao'
        )
    """)
    op.execute("""
        ALTER TABLE transacao
            ALTER COLUMN tipo
            TYPE tipotransacao_new
            USING (
                CASE lower(tipo::text)
                    WHEN 'compra'        THEN 'compra'
                    WHEN 'venda'         THEN 'venda'
                    WHEN 'dividendo'     THEN 'dividendo'
                    WHEN 'jcp'           THEN 'jcp'
                    WHEN 'aluguel'       THEN 'aluguel'
                    WHEN 'bonificacao'   THEN 'bonificacao'
                    WHEN 'split'         THEN 'split'
                    WHEN 'desdobramento' THEN 'split'
                    WHEN 'grupamento'    THEN 'grupamento'
                    WHEN 'subscricao'    THEN 'subscricao'
                    WHEN 'amortizacao'   THEN 'amortizacao'
                    ELSE lower(tipo::text)
                END
            )::tipotransacao_new
    """)
    op.execute("DROP TYPE tipotransacao")
    op.execute("ALTER TYPE tipotransacao_new RENAME TO tipotransacao")


def downgrade():
    op.execute("""
        CREATE TYPE tipotransacao_old AS ENUM (
            'COMPRA', 'VENDA', 'DIVIDENDO', 'JCP',
            'BONIFICACAO', 'DESDOBRAMENTO', 'GRUPAMENTO'
        )
    """)
    op.execute("""
        ALTER TABLE transacao
            ALTER COLUMN tipo
            TYPE tipotransacao_old
            USING (
                CASE lower(tipo::text)
                    WHEN 'compra'      THEN 'COMPRA'
                    WHEN 'venda'       THEN 'VENDA'
                    WHEN 'dividendo'   THEN 'DIVIDENDO'
                    WHEN 'jcp'         THEN 'JCP'
                    WHEN 'bonificacao' THEN 'BONIFICACAO'
                    WHEN 'split'       THEN 'DESDOBRAMENTO'
                    WHEN 'grupamento'  THEN 'GRUPAMENTO'
                END
            )::tipotransacao_old
    """)
    op.execute("DROP TYPE tipotransacao")
    op.execute("ALTER TYPE tipotransacao_old RENAME TO tipotransacao")
