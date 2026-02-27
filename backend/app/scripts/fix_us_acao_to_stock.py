#!/usr/bin/env python3
"""Fix: Corrige ativos US que estão com tipo=ACAO para tipo=STOCK.

Uso (dry-run por padrão):
  python3 app/scripts/fix_us_acao_to_stock.py

Aplicar de fato:
  python3 app/scripts/fix_us_acao_to_stock.py --apply

Opcional:
  --ticker AAPL   (corrige apenas um ticker)

Observação:
- Este script só altera registros com mercado='US' e tipo=TipoAtivo.ACAO.
- Por segurança, roda em modo dry-run por padrão (não commita alterações).
"""

import argparse
import os
import sys

# Adicionar path do app (2 níveis acima: /app/app/scripts -> /app)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app import create_app
from app.database import db
from app.models import Ativo, TipoAtivo


def fix_us_acao_to_stock(apply: bool, ticker: str | None) -> int:
    app = create_app()

    with app.app_context():
        query = Ativo.query.filter_by(mercado="US", tipo=TipoAtivo.ACAO)
        if ticker:
            query = query.filter_by(ticker=ticker.upper())

        ativos = query.order_by(Ativo.ticker).all()

        if not ativos:
            print("✅ Nenhum ativo US com tipo=ACAO encontrado para corrigir")
            return 0

        print("=" * 60)
        print("FIX: US tipo=ACAO -> STOCK")
        print("=" * 60)
        print(f"Encontrados: {len(ativos)}")

        for a in ativos:
            print(f"- {a.ticker} (id={a.id}) mercado={a.mercado} tipo_atual={a.tipo.name}")

        if not apply:
            print("\nℹ️  Dry-run: nenhuma alteração foi aplicada. Use --apply para commitar.")
            return len(ativos)

        for a in ativos:
            a.tipo = TipoAtivo.STOCK

        db.session.commit()

        print("\n✅ Alterações aplicadas e commitadas com sucesso")
        return len(ativos)


def main() -> None:
    parser = argparse.ArgumentParser(description="Corrigir ativos US com tipo=ACAO para STOCK")
    parser.add_argument("--apply", action="store_true", help="Aplica e commita as alterações")
    parser.add_argument("--ticker", type=str, default=None, help="Ticker específico (ex.: AAPL)")

    args = parser.parse_args()

    fix_us_acao_to_stock(apply=args.apply, ticker=args.ticker)


if __name__ == "__main__":
    main()
