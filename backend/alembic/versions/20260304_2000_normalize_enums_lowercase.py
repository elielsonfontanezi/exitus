"""normalize enums to lowercase (ENUM-001)

Revision ID: 20260304_2000
Revises: 20260304_1900
Create Date: 2026-03-04 20:00:00.000000

Converte 12 ENUMs PostgreSQL de UPPERCASE para lowercase.
ENUMs já em lowercase (tipotransacao, tiporelatorio, etc.) não são alterados.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260304_2000'
down_revision = '20260304_1900'
branch_labels = None
depends_on = None


def _rename_enum_values(op, enum_name, table_name, column_name, old_to_new, nullable=False):
    """
    Estratégia segura para renomear valores de ENUM com dados existentes:
    1. Adicionar coluna temporária TEXT
    2. Copiar valores convertidos
    3. Dropar coluna original e tipo antigo
    4. Criar novo tipo ENUM com valores novos
    5. Adicionar coluna com novo tipo
    6. Preencher a partir do texto temporário
    7. Restaurar NOT NULL se aplicável
    8. Dropar coluna temporária

    IMPORTANTE: nullable=False (default) preserva o NOT NULL constraint original.
    """
    tmp_col = f"{column_name}_tmp"

    # 1. Coluna temporária TEXT
    op.add_column(table_name, sa.Column(tmp_col, sa.Text(), nullable=True))

    # 2. Copiar valores convertidos
    values_map = " ".join([f"WHEN '{old}' THEN '{new}'" for old, new in old_to_new.items()])
    op.execute(f"""
        UPDATE {table_name}
        SET {tmp_col} = CASE {column_name}::text {values_map} END
    """)

    # 3. Dropar coluna original e tipo antigo
    op.drop_column(table_name, column_name)
    op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    # 4. Criar novo tipo com valores novos
    new_values = list(old_to_new.values())
    values_sql = ", ".join([f"'{v}'" for v in new_values])
    op.execute(f"CREATE TYPE {enum_name} AS ENUM ({values_sql})")

    # 5. Adicionar coluna com novo tipo (nullable temporariamente para popular)
    op.add_column(table_name, sa.Column(column_name, sa.Enum(name=enum_name), nullable=True))

    # 6. Preencher a partir do texto temporário
    op.execute(f"""
        UPDATE {table_name}
        SET {column_name} = {tmp_col}::{enum_name}
    """)

    # 7. Restaurar NOT NULL se aplicável
    if not nullable:
        op.execute(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL")

    # 8. Dropar coluna temporária
    op.drop_column(table_name, tmp_col)


def upgrade() -> None:

    # ----------------------------------------------------------------
    # 1. tipoativo — tabela: ativo, coluna: tipo
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipoativo', 'ativo', 'tipo', {
        'ACAO': 'acao',
        'FII': 'fii',
        'REIT': 'reit',
        'BOND': 'bond',
        'ETF': 'etf',
        'CRIPTO': 'cripto',
        'OUTRO': 'outro',
        'CDB': 'cdb',
        'LCI_LCA': 'lci_lca',
        'TESOURO_DIRETO': 'tesouro_direto',
        'DEBENTURE': 'debenture',
        'STOCK': 'stock',
        'STOCK_INTL': 'stock_intl',
        'ETF_INTL': 'etf_intl',
        'UNIT': 'unit',
    })

    # ----------------------------------------------------------------
    # 2. classeativo — tabela: ativo, coluna: classe
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'classeativo', 'ativo', 'classe', {
        'RENDA_VARIAVEL': 'renda_variavel',
        'RENDA_FIXA': 'renda_fixa',
        'CRIPTO': 'cripto',
        'COMMODITY': 'commodity',
        'HIBRIDO': 'hibrido',
    })

    # ----------------------------------------------------------------
    # 3. tipoprovento — tabela: provento, coluna: tipo_provento
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipoprovento', 'provento', 'tipo_provento', {
        'DIVIDENDO': 'dividendo',
        'JCP': 'jcp',
        'RENDIMENTO': 'rendimento',
        'CUPOM': 'cupom',
        'BONIFICACAO': 'bonificacao',
        'DIREITO_SUBSCRICAO': 'direito_subscricao',
        'OUTRO': 'outro',
    })

    # ----------------------------------------------------------------
    # 4. tipomovimentacao — tabela: movimentacao_caixa, coluna: tipo_movimentacao
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipomovimentacao', 'movimentacao_caixa', 'tipo_movimentacao', {
        'DEPOSITO': 'deposito',
        'SAQUE': 'saque',
        'TRANSFERENCIA_ENVIADA': 'transferencia_enviada',
        'TRANSFERENCIA_RECEBIDA': 'transferencia_recebida',
        'CREDITO_PROVENTO': 'credito_provento',
        'PAGAMENTO_TAXA': 'pagamento_taxa',
        'PAGAMENTO_IMPOSTO': 'pagamento_imposto',
        'AJUSTE': 'ajuste',
        'OUTRO': 'outro',
    })

    # ----------------------------------------------------------------
    # 5. tipooperacao — tabela: transacao, coluna: tipo
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipooperacao', 'transacao', 'tipo', {
        'COMPRA': 'compra',
        'VENDA': 'venda',
    })

    # ----------------------------------------------------------------
    # 6. tipoferiado — tabela: feriado_mercado, coluna: tipo_feriado
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipoferiado', 'feriado_mercado', 'tipo_feriado', {
        'NACIONAL': 'nacional',
        'BOLSA': 'bolsa',
        'PONTE': 'ponte',
        'FECHAMENTO_ANTECIPADO': 'fechamento_antecipado',
        'MANUTENCAO': 'manutencao',
        'OUTRO': 'outro',
    })

    # ----------------------------------------------------------------
    # 7. tipofontedados — tabela: fonte_dados, coluna: tipo_fonte
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipofontedados', 'fonte_dados', 'tipo_fonte', {
        'API': 'api',
        'SCRAPER': 'scraper',
        'MANUAL': 'manual',
        'ARQUIVO': 'arquivo',
        'OUTRO': 'outro',
    })

    # ----------------------------------------------------------------
    # 8. tipoeventocorporativo — tabela: evento_corporativo, coluna: tipo_evento
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipoeventocorporativo', 'evento_corporativo', 'tipo_evento', {
        'SPLIT': 'split',
        'GRUPAMENTO': 'grupamento',
        'BONIFICACAO': 'bonificacao',
        'DIREITO_SUBSCRICAO': 'direito_subscricao',
        'FUSAO': 'fusao',
        'CISAO': 'cisao',
        'INCORPORACAO': 'incorporacao',
        'MUDANCA_TICKER': 'mudanca_ticker',
        'DESLISTAGEM': 'deslistagem',
        'RELISTING': 'relisting',
        'CANCELAMENTO': 'cancelamento',
        'OUTRO': 'outro',
        'DESMEMBRAMENTO': 'desmembramento',
    })

    # ----------------------------------------------------------------
    # 9. tipocorretora — tabela: corretora, coluna: tipo
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipocorretora', 'corretora', 'tipo', {
        'CORRETORA': 'corretora',
        'EXCHANGE': 'exchange',
    })

    # ----------------------------------------------------------------
    # 10. tipo_evento_custodia — tabela: evento_custodia, coluna: tipo_evento
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'tipo_evento_custodia', 'evento_custodia', 'tipo_evento', {
        'LIQUIDACAO_D2': 'liquidacao_d2',
        'TRANSFERENCIA_ENTRADA': 'transferencia_entrada',
        'TRANSFERENCIA_SAIDA': 'transferencia_saida',
        'AJUSTE_POSICAO': 'ajuste_posicao',
        'DESDOBRAMENTO': 'desdobramento',
        'AGRUPAMENTO': 'agrupamento',
        'AMORTIZACAO': 'amortizacao',
        'OUTRO': 'outro',
    })

    # ----------------------------------------------------------------
    # 11. incidenciaimposto — tabela: regra_fiscal, coluna: incide_sobre
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'incidenciaimposto', 'regra_fiscal', 'incide_sobre', {
        'LUCRO': 'lucro',
        'RECEITA': 'receita',
        'PROVENTO': 'provento',
        'OPERACAO': 'operacao',
    })

    # ----------------------------------------------------------------
    # 12. userrole — tabela: usuario, coluna: role
    # ----------------------------------------------------------------
    _rename_enum_values(op, 'userrole', 'usuario', 'role', {
        'ADMIN': 'admin',
        'USER': 'user',
        'READONLY': 'readonly',
    })


def downgrade() -> None:
    # Downgrade inverte lowercase → UPPERCASE

    _rename_enum_values(op, 'userrole', 'usuario', 'role', {
        'admin': 'ADMIN',
        'user': 'USER',
        'readonly': 'READONLY',
    })

    _rename_enum_values(op, 'incidenciaimposto', 'regra_fiscal', 'incide_sobre', {
        'lucro': 'LUCRO',
        'receita': 'RECEITA',
        'provento': 'PROVENTO',
        'operacao': 'OPERACAO',
    })

    _rename_enum_values(op, 'tipo_evento_custodia', 'evento_custodia', 'tipo_evento', {
        'liquidacao_d2': 'LIQUIDACAO_D2',
        'transferencia_entrada': 'TRANSFERENCIA_ENTRADA',
        'transferencia_saida': 'TRANSFERENCIA_SAIDA',
        'ajuste_posicao': 'AJUSTE_POSICAO',
        'desdobramento': 'DESDOBRAMENTO',
        'agrupamento': 'AGRUPAMENTO',
        'amortizacao': 'AMORTIZACAO',
        'outro': 'OUTRO',
    })

    _rename_enum_values(op, 'tipocorretora', 'corretora', 'tipo', {
        'corretora': 'CORRETORA',
        'exchange': 'EXCHANGE',
    })

    _rename_enum_values(op, 'tipoeventocorporativo', 'evento_corporativo', 'tipo_evento', {
        'split': 'SPLIT',
        'grupamento': 'GRUPAMENTO',
        'bonificacao': 'BONIFICACAO',
        'direito_subscricao': 'DIREITO_SUBSCRICAO',
        'fusao': 'FUSAO',
        'cisao': 'CISAO',
        'incorporacao': 'INCORPORACAO',
        'mudanca_ticker': 'MUDANCA_TICKER',
        'deslistagem': 'DESLISTAGEM',
        'relisting': 'RELISTING',
        'cancelamento': 'CANCELAMENTO',
        'outro': 'OUTRO',
        'desmembramento': 'DESMEMBRAMENTO',
    })

    _rename_enum_values(op, 'tipofontedados', 'fonte_dados', 'tipo_fonte', {
        'api': 'API',
        'scraper': 'SCRAPER',
        'manual': 'MANUAL',
        'arquivo': 'ARQUIVO',
        'outro': 'OUTRO',
    })

    _rename_enum_values(op, 'tipoferiado', 'feriado_mercado', 'tipo_feriado', {
        'nacional': 'NACIONAL',
        'bolsa': 'BOLSA',
        'ponte': 'PONTE',
        'fechamento_antecipado': 'FECHAMENTO_ANTECIPADO',
        'manutencao': 'MANUTENCAO',
        'outro': 'OUTRO',
    })

    _rename_enum_values(op, 'tipooperacao', 'transacao', 'tipo', {
        'compra': 'COMPRA',
        'venda': 'VENDA',
    })

    _rename_enum_values(op, 'tipomovimentacao', 'movimentacao_caixa', 'tipo_movimentacao', {
        'deposito': 'DEPOSITO',
        'saque': 'SAQUE',
        'transferencia_enviada': 'TRANSFERENCIA_ENVIADA',
        'transferencia_recebida': 'TRANSFERENCIA_RECEBIDA',
        'credito_provento': 'CREDITO_PROVENTO',
        'pagamento_taxa': 'PAGAMENTO_TAXA',
        'pagamento_imposto': 'PAGAMENTO_IMPOSTO',
        'ajuste': 'AJUSTE',
        'outro': 'OUTRO',
    })

    _rename_enum_values(op, 'tipoprovento', 'provento', 'tipo_provento', {
        'dividendo': 'DIVIDENDO',
        'jcp': 'JCP',
        'rendimento': 'RENDIMENTO',
        'cupom': 'CUPOM',
        'bonificacao': 'BONIFICACAO',
        'direito_subscricao': 'DIREITO_SUBSCRICAO',
        'outro': 'OUTRO',
    })

    _rename_enum_values(op, 'classeativo', 'ativo', 'classe', {
        'renda_variavel': 'RENDA_VARIAVEL',
        'renda_fixa': 'RENDA_FIXA',
        'cripto': 'CRIPTO',
        'commodity': 'COMMODITY',
        'hibrido': 'HIBRIDO',
    })

    _rename_enum_values(op, 'tipoativo', 'ativo', 'tipo', {
        'acao': 'ACAO',
        'fii': 'FII',
        'reit': 'REIT',
        'bond': 'BOND',
        'etf': 'ETF',
        'cripto': 'CRIPTO',
        'outro': 'OUTRO',
        'cdb': 'CDB',
        'lci_lca': 'LCI_LCA',
        'tesouro_direto': 'TESOURO_DIRETO',
        'debenture': 'DEBENTURE',
        'stock': 'STOCK',
        'stock_intl': 'STOCK_INTL',
        'etf_intl': 'ETF_INTL',
        'unit': 'UNIT',
    })
