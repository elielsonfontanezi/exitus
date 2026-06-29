# -*- coding: utf-8 -*-
"""
Exitus - SEED-MACRO-001: Popular tabela parametros_macro com valores reais

Insere parâmetros macroeconômicos regionais para valuation.
Operação idempotente: cria se não existe, atualiza se existe.

Uso:
    python -m app.seeds.seed_parametros_macro           # interativo
    python -m app.seeds.seed_parametros_macro --force   # sem confirmação
"""

import sys
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

PARAMETROS = [
    {
        'pais': 'BR', 'mercado': 'B3',
        'taxa_livre_risco': Decimal('0.105000'),
        'crescimento_medio': Decimal('0.050000'),
        'custo_capital':     Decimal('0.120000'),
        'inflacao_anual':    Decimal('0.045000'),
        'cap_rate_fii':      Decimal('0.080000'),
        'ytm_rf':            Decimal('0.115000'),
    },
    {
        'pais': 'US', 'mercado': 'NYSE',
        'taxa_livre_risco': Decimal('0.043000'),
        'crescimento_medio': Decimal('0.070000'),
        'custo_capital':     Decimal('0.090000'),
        'inflacao_anual':    Decimal('0.022000'),
        'cap_rate_fii':      Decimal('0.055000'),
        'ytm_rf':            Decimal('0.045000'),
    },
    {
        'pais': 'US', 'mercado': 'NASDAQ',
        'taxa_livre_risco': Decimal('0.043000'),
        'crescimento_medio': Decimal('0.100000'),
        'custo_capital':     Decimal('0.100000'),
        'inflacao_anual':    Decimal('0.022000'),
        'cap_rate_fii':      Decimal('0.050000'),
        'ytm_rf':            Decimal('0.045000'),
    },
    {
        'pais': 'EU', 'mercado': 'Euronext',
        'taxa_livre_risco': Decimal('0.028000'),
        'crescimento_medio': Decimal('0.018000'),
        'custo_capital':     Decimal('0.072000'),
        'inflacao_anual':    Decimal('0.020000'),
        'cap_rate_fii':      Decimal('0.045000'),
        'ytm_rf':            Decimal('0.032000'),
    },
    {
        'pais': 'JP', 'mercado': 'Tokyo',
        'taxa_livre_risco': Decimal('0.001500'),
        'crescimento_medio': Decimal('0.012000'),
        'custo_capital':     Decimal('0.035000'),
        'inflacao_anual':    Decimal('0.015000'),
        'cap_rate_fii':      Decimal('0.035000'),
        'ytm_rf':            Decimal('0.018000'),
    },
]


def seed_parametros_macro(force=False):
    """Popula parametros_macro com valores reais por mercado (UPSERT idempotente)."""
    from app import create_app
    from app.database import db
    from app.models.parametros_macro import ParametrosMacro

    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("  SEED-MACRO-001: Parâmetros Macroeconômicos")
        print("=" * 60)

        atualizados = 0
        criados = 0

        for p in PARAMETROS:
            existing = ParametrosMacro.query.filter_by(
                pais=p['pais'], mercado=p['mercado']
            ).first()

            if existing:
                for key, value in p.items():
                    if key not in ('pais', 'mercado'):
                        setattr(existing, key, value)
                atualizados += 1
                print(f"  🔄 {p['pais']:2}/{p['mercado']:8} atualizado  "
                      f"(rf={float(p['taxa_livre_risco']):.1%}, g={float(p['crescimento_medio']):.1%}, "
                      f"wacc={float(p['custo_capital']):.1%})")
            else:
                macro = ParametrosMacro(**p)
                db.session.add(macro)
                criados += 1
                print(f"  ✅ {p['pais']:2}/{p['mercado']:8} criado     "
                      f"(rf={float(p['taxa_livre_risco']):.1%}, g={float(p['crescimento_medio']):.1%}, "
                      f"wacc={float(p['custo_capital']):.1%})")

        try:
            db.session.commit()
            print()
            print(f"  Criados: {criados} | Atualizados: {atualizados} | Total: {len(PARAMETROS)}")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar: {e}")
            raise


if __name__ == '__main__':
    force = '--force' in sys.argv
    seed_parametros_macro(force=force)
