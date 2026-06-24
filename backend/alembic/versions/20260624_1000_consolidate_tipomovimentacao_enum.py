"""consolidate tipomovimentacao enum

Revision ID: 20260624_1000
Revises: 20260621_1300
Create Date: 2026-06-24 10:00:00.000000

Consolida o enum tipomovimentacao para refletir os valores reais do banco:
- aporte, resgate, transferencia_enviada, transferencia_recebida, credito_provento
- taxa_custodia, taxa_corretagem, imposto, ajuste, outro

Remove valores obsoletos: deposito, saque, transf_env, transf_rec, credito_prov,
pagto_taxa, pagamento_imposto.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260624_1000'
down_revision = '20260621_1300'
branch_labels = None
depends_on = None


def _rename_enum_values(op, enum_name, table_name, column_name, old_to_new, all_values, nullable=False):
    """
    Recria enum com todos os valores desejados e renomeia valores antigos.
    """
    tmp_col = f"{column_name}_tmp"

    # 1. Coluna temporaria TEXT
    op.add_column(table_name, sa.Column(tmp_col, sa.Text(), nullable=True))

    # 2. Copiar valores convertidos (valores nao mapeados ficam como estao)
    values_map = " ".join([f"WHEN '{old}' THEN '{new}'" for old, new in old_to_new.items()])
    if values_map:
        op.execute(f"""
            UPDATE {table_name}
            SET {tmp_col} = CASE {column_name}::text {values_map} ELSE {column_name}::text END
        """)
    else:
        op.execute(f"""
            UPDATE {table_name}
            SET {tmp_col} = {column_name}::text
        """)

    # 3. Dropar coluna original e tipo antigo
    op.drop_column(table_name, column_name)
    op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    # 4. Criar novo tipo com todos os valores
    values_sql = ", ".join([f"'{v}'" for v in all_values])
    op.execute(f"CREATE TYPE {enum_name} AS ENUM ({values_sql})")

    # 5. Adicionar coluna com novo tipo (nullable temporariamente)
    op.add_column(table_name, sa.Column(column_name, sa.Enum(name=enum_name), nullable=True))

    # 6. Preencher a partir do texto temporario
    op.execute(f"""
        UPDATE {table_name}
        SET {column_name} = {tmp_col}::{enum_name}
    """)

    # 7. Restaurar NOT NULL se aplicavel
    if not nullable:
        op.execute(f"""
            ALTER TABLE {table_name}
            ALTER COLUMN {column_name} SET NOT NULL
        """)

    # 8. Dropar coluna temporaria
    op.drop_column(table_name, tmp_col)


def upgrade():
    # Mapeamento de valores antigos (ou ja corretos) para valores finais
    old_to_new = {
        'deposito': 'aporte',
        'saque': 'resgate',
        'transf_env': 'transferencia_enviada',
        'transf_rec': 'transferencia_recebida',
        'credito_prov': 'credito_provento',
        'pagto_taxa': 'taxa_custodia',
        'pagamento_imposto': 'imposto',
    }

    # Valores finais desejados no enum (ordenados)
    all_values = [
        'aporte',
        'resgate',
        'transferencia_enviada',
        'transferencia_recebida',
        'credito_provento',
        'taxa_custodia',
        'taxa_corretagem',
        'imposto',
        'ajuste',
        'outro',
    ]

    _rename_enum_values(
        op,
        enum_name='tipomovimentacao',
        table_name='movimentacao_caixa',
        column_name='tipo_movimentacao',
        old_to_new=old_to_new,
        all_values=all_values,
        nullable=False
    )


def downgrade():
    # Reverte para valores anteriores ao modelo Python antigo
    old_to_new = {
        'aporte': 'deposito',
        'resgate': 'saque',
        'transferencia_enviada': 'transf_env',
        'transferencia_recebida': 'transf_rec',
        'credito_provento': 'credito_prov',
        'taxa_custodia': 'pagto_taxa',
        'taxa_corretagem': 'pagto_taxa',
        'imposto': 'pagamento_imposto',
        'ajuste': 'ajuste',
        'outro': 'outro',
    }

    all_values = [
        'deposito',
        'saque',
        'transf_env',
        'transf_rec',
        'credito_prov',
        'pagto_taxa',
        'pagamento_imposto',
        'ajuste',
        'outro',
    ]

    _rename_enum_values(
        op,
        enum_name='tipomovimentacao',
        table_name='movimentacao_caixa',
        column_name='tipo_movimentacao',
        old_to_new=old_to_new,
        all_values=all_values,
        nullable=False
    )
