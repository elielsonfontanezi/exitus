"""add 7 new tipoativo enums

Revision ID: 202602162111
Revises: ffdaac46cd7a
Create Date: 2026-02-16 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '202602162111'
down_revision = 'ffdaac46cd7a'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona 7 novos tipos ao ENUM tipoativo:
    - CDB, LCI_LCA, TESOURO_DIRETO, DEBENTURE (BR Renda Fixa)
    - STOCK (US Ações)
    - STOCK_INTL, ETF_INTL (Internacionais)
    
    Mantém 7 existentes: ACAO, FII, REIT, BOND, ETF, CRIPTO, OUTRO
    """
    
    connection = op.get_bind()
    
    new_values = [
        'CDB',
        'LCI_LCA',
        'TESOURO_DIRETO',
        'DEBENTURE',
        'STOCK',
        'STOCK_INTL',
        'ETF_INTL'
    ]
    
    for value in new_values:
        result = connection.execute(sa.text(
            f"SELECT 1 FROM pg_enum WHERE enumlabel = '{value}' "
            f"AND enumtypid = 'tipoativo'::regtype"
        ))
        
        if not result.fetchone():
            op.execute(f"ALTER TYPE tipoativo ADD VALUE '{value}'")
            print(f"✅ Adicionado: {value}")
        else:
            print(f"⚠️  Já existe: {value}")


def downgrade():
    """
    PostgreSQL não suporta remoção de valores de ENUM.
    Reversão manual necessária se requerida.
    """
    pass
