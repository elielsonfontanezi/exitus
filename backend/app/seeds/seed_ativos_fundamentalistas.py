# -*- coding: utf-8 -*-
"""
Exitus - EXITUS-ASSETS-001: Seed/Enriquecimento de Ativos com Dados Fundamentalistas

Enriquece ativos existentes (ou cria novos) com dados fundamentalistas:
- preco_atual, dividend_yield, p_l, p_vp, roe, beta, preco_teto, cap_rate

Uso:
    python -m app.seeds.seed_ativos_fundamentalistas          # interativo
    python -m app.seeds.seed_ativos_fundamentalistas --force   # sem confirmação
"""

import json
import os
import sys
import logging
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent / 'data' / 'ativos_fundamentalistas.json'

# Mapeamento de categorias JSON → (TipoAtivo, ClasseAtivo, mercado, moeda)
CATEGORY_MAP = {
    'ativos_br_acoes':       ('ACAO',           'RENDA_VARIAVEL', 'BR', 'BRL'),
    'ativos_br_fiis':        ('FII',            'RENDA_VARIAVEL', 'BR', 'BRL'),
    'ativos_us_stocks':      ('STOCK',          'RENDA_VARIAVEL', 'US', 'USD'),
    'ativos_us_reits':       ('REIT',           'RENDA_VARIAVEL', 'US', 'USD'),
    'ativos_us_etfs':        ('ETF',            'RENDA_VARIAVEL', 'US', 'USD'),
    'ativos_br_renda_fixa':  ('TESOURO_DIRETO', 'RENDA_FIXA',    'BR', 'BRL'),
}


def _dec(value):
    """Converte para Decimal ou None."""
    if value is None:
        return None
    return Decimal(str(value))


def seed_ativos_fundamentalistas(force=False):
    """Enriquece/cria ativos com dados fundamentalistas."""
    from app import create_app
    from app.database import db
    from app.models import Ativo, TipoAtivo, ClasseAtivo

    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("  EXITUS-ASSETS-001: Seed de Dados Fundamentalistas")
        print("=" * 60)

        if not DATA_FILE.exists():
            print(f"❌ Arquivo de dados não encontrado: {DATA_FILE}")
            return

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_updated = 0
        total_created = 0
        total_skipped = 0

        for category, (tipo_str, classe_str, mercado, moeda) in CATEGORY_MAP.items():
            items = data.get(category, [])
            if not items:
                continue

            tipo_enum = TipoAtivo[tipo_str]
            classe_enum = ClasseAtivo[classe_str]

            print(f"\n📊 {category} ({len(items)} ativos):")

            for item in items:
                ticker = item['ticker']
                nome = item['nome']

                ativo = Ativo.query.filter_by(ticker=ticker, mercado=mercado).first()

                if ativo:
                    # Enriquecer ativo existente
                    ativo.preco_atual = _dec(item.get('preco_atual'))
                    ativo.dividend_yield = _dec(item.get('dividend_yield'))
                    ativo.p_l = _dec(item.get('p_l'))
                    ativo.p_vp = _dec(item.get('p_vp'))
                    ativo.roe = _dec(item.get('roe'))
                    ativo.beta = _dec(item.get('beta'))
                    ativo.preco_teto = _dec(item.get('preco_teto'))
                    ativo.cap_rate = _dec(item.get('cap_rate'))
                    setor = item.get('setor') or item.get('segmento', '')
                    if setor:
                        ativo.observacoes = f"Setor: {setor}"
                    total_updated += 1
                    print(f"  🔄 {ticker:12} atualizado (DY={item.get('dividend_yield')}, P/L={item.get('p_l')}, ROE={item.get('roe')})")
                else:
                    # Criar novo ativo
                    setor = item.get('setor') or item.get('segmento', '')
                    ativo = Ativo(
                        ticker=ticker,
                        nome=nome,
                        tipo=tipo_enum,
                        classe=classe_enum,
                        mercado=mercado,
                        moeda=moeda,
                        preco_atual=_dec(item.get('preco_atual')),
                        dividend_yield=_dec(item.get('dividend_yield')),
                        p_l=_dec(item.get('p_l')),
                        p_vp=_dec(item.get('p_vp')),
                        roe=_dec(item.get('roe')),
                        beta=_dec(item.get('beta')),
                        preco_teto=_dec(item.get('preco_teto')),
                        cap_rate=_dec(item.get('cap_rate')),
                        observacoes=f"Setor: {setor}" if setor else None,
                        ativo=True,
                    )
                    db.session.add(ativo)
                    total_created += 1
                    print(f"  ✅ {ticker:12} criado")

        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"  ✅ Enriquecimento concluído:")
            print(f"     - {total_updated} ativos atualizados com dados fundamentalistas")
            print(f"     - {total_created} ativos criados")
            print(f"     - {total_skipped} ativos ignorados")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar: {e}")
            raise


if __name__ == '__main__':
    force = '--force' in sys.argv
    seed_ativos_fundamentalistas(force=force)
