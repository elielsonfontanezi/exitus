#!/usr/bin/env python3
"""
EXITUS - Seed de Ativos Internacionais (INTL)
Ativos internacionais diversos (ADRs, GDRs, etc.)
"""

from decimal import Decimal
from app import create_app
from app.database import db
from app.models import Ativo, TipoAtivo, ClasseAtivo


def seed_ativos_intl():
    """Cria ativos internacionais diversos (mercado INTL)."""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Ativos Internacionais (INTL)")
        print("=" * 50)
        
        # ADRs americanos de empresas brasileiras
        adrs_br = [
            ('PBR',    'Petrobras ADR',           'NYSE',     'Oil & Gas', Decimal('18.50')),
            ('VALE',   'Vale ADR',                'NASDAQ',   'Mining',   Decimal('16.80')),
            ('ITUB',   'Itau Unibanco ADR',       'NYSE',     'Banking',  Decimal('5.20')),
            ('BBAS',   'Banco do Brasil ADR',     'OTC',      'Banking',  Decimal('3.80')),
            ('ABEV',   'Ambev ADR',               'NYSE',     'Beverages', Decimal('2.90')),
            ('GGBR',   'Gerdau ADR',              'NYSE',     'Steel',    Decimal('4.10')),
            ('CIG',    'Cia Energetica de Minas Gerais ADR', 'NYSE', 'Utilities', Decimal('2.20')),
            ('BSBR',   'Banco Santander Brasil ADR', 'NYSE', 'Banking', Decimal('4.50')),
            ('BBD',    'Bradesco ADR',            'NASDAQ',   'Banking',  Decimal('3.30')),
            ('EBR',    'Centrais Eletricas Brasileiras ADR', 'NYSE', 'Utilities', Decimal('7.20')),
        ]
        
        # GDRs europeus e outros internacionais
        gdros_outros = [
            ('TSLA34', 'Tesla GDR',              'B3',       'Automotive', Decimal('85.60')),
            ('AAPL34', 'Apple GDR',               'B3',       'Technology', Decimal('125.90')),
            ('GOGL34', 'Alphabet GDR',            'B3',       'Technology', Decimal('145.30')),
            ('MSFT34', 'Microsoft GDR',           'B3',       'Technology', Decimal('165.40')),
            ('AMZN34', 'Amazon GDR',              'B3',       'E-commerce', Decimal('155.80')),
            ('META34', 'Meta GDR',                'B3',       'Social Media', Decimal('315.60')),
            ('NVDA34', 'NVIDIA GDR',              'B3',       'Semiconductors', Decimal('520.90')),
            ('BTC34',  'Bitcoin Tracker GDR',     'B3',       'Crypto', Decimal('285000.00')),
            ('ETH34',  'Ethereum Tracker GDR',    'B3',       'Crypto', Decimal('15500.00')),
            ('COIN34', 'Coinbase GDR',            'B3',       'Crypto', Decimal('285.60')),
        ]
        
        # ETFs internacionais disponíveis no Brasil
        etfs_intl_b3 = [
            ('BOVA11', 'iShares Ibovespa ETF',    'B3',       'Equity',   Decimal('85.40')),
            ('SMAL11', 'iShares Small Cap ETF',   'B3',       'Equity',   Decimal('95.60')),
            ('BRFS11', 'iShares MSCI Brazil ETF', 'NASDAQ',   'Equity',   Decimal('28.90')),
            ('EWZ',    'iShares MSCI Brazil ETF', 'NYSE',     'Equity',   Decimal('28.90')),
            ('EWZS',   'iShares MSCI Brazil Small Cap ETF', 'NYSE', 'Equity', Decimal('18.50')),
            ('BRAQ',   'Global X Brazil ETF',     'NASDAQ',   'Equity',   Decimal('22.30')),
            ('FBRA',   'iShares MSCI Brazil ETF', 'B3',       'Equity',   Decimal('28.90')),
        ]
        
        created = 0
        skipped = 0
        
        print("\n🇺🇸 ADRs de Empresas Brasileiras:")
        for ticker, nome, bolsa, setor, preco in adrs_br:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - já existe, skipped")
                skipped += 1
                continue
            
            ativo = Ativo(
                ticker=ticker, nome=nome,
                tipo=TipoAtivo.STOCK,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='INTL', moeda='USD',
                preco_atual=preco,
                setor=setor,
                bolsa=bolsa
            )
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n🌍 GDRs e Outros Internacionais:")
        for ticker, nome, bolsa, setor, preco in gdros_outros:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - já existe, skipped")
                skipped += 1
                continue
            
            ativo = Ativo(
                ticker=ticker, nome=nome,
                tipo=TipoAtivo.STOCK_INTL,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='INTL', moeda='BRL',
                preco_atual=preco,
                setor=setor,
                bolsa=bolsa
            )
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n📊 ETFs Internacionais:")
        for ticker, nome, bolsa, setor, preco in etfs_intl_b3:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - já existe, skipped")
                skipped += 1
                continue
            
            moeda = 'BRL' if bolsa == 'B3' else 'USD'
            
            ativo = Ativo(
                ticker=ticker, nome=nome,
                tipo=TipoAtivo.ETF,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='INTL', moeda=moeda,
                preco_atual=preco
            )
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✅ Criados: {created} | Pulados: {skipped}")
            print("=" * 50)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro: {e}")
            return False
        
        return True


if __name__ == "__main__":
    seed_ativos_intl()
