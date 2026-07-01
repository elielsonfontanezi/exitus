"""add cap_rate field to ativo

Revision ID: 202602162130
Revises: 202602162111
Create Date: 2026-02-16 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '202602162130'
down_revision = '202602162111'
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona campo cap_rate à tabela ativo.
    
    Cap Rate (Capitalization Rate):
    - Usado para valuation de FIIs e REITs
    - Fórmula: Preço Teto = Dividendo Anual / Cap Rate
    - Exemplo: Cap Rate BR FII = 6% (0.06)
    """
    op.add_column('ativo', 
        sa.Column('cap_rate', 
                  sa.Numeric(precision=8, scale=4), 
                  nullable=True,
                  comment='Cap Rate - Taxa de capitalização para FIIs/REITs (ex: 0.06 = 6%)')
    )
    
    print("✅ Campo cap_rate adicionado à tabela ativo")


def downgrade():
    """Remove campo cap_rate"""
    op.drop_column('ativo', 'cap_rate')
    print("✅ Campo cap_rate removido da tabela ativo")
