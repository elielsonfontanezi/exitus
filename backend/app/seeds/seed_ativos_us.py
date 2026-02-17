"""Exitus - Seed de Ativos dos Estados Unidos"""
from app import create_app
from app.database import db
from app.models import Ativo, TipoAtivo, ClasseAtivo
from decimal import Decimal

def seed_ativos_us():
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Ativos US")
        print("=" * 50)
        
        stocks = [
            ('AAPL', 'Apple Inc.', 'Technology', Decimal('175.50')),
            ('MSFT', 'Microsoft Corporation', 'Technology', Decimal('380.25')),
            ('GOOGL', 'Alphabet Inc. Class A', 'Technology', Decimal('140.30')),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', Decimal('155.80')),
            ('NVDA', 'NVIDIA Corporation', 'Technology', Decimal('720.45')),
            ('TSLA', 'Tesla Inc.', 'Automotive', Decimal('245.60')),
        ]
        
        reits = [
            ('VNQ', 'Vanguard Real Estate ETF', 'Real Estate', Decimal('92.30')),
            ('O', 'Realty Income Corporation', 'Retail REIT', Decimal('58.75')),
            ('PLD', 'Prologis Inc.', 'Industrial REIT', Decimal('125.40')),
        ]
        
        bonds = [
            ('AGG', 'iShares Core US Aggregate Bond ETF', 'Bond Index', Decimal('102.15')),
            ('BND', 'Vanguard Total Bond Market ETF', 'Bond Index', Decimal('75.80')),
        ]
        
        etfs = [
            ('SPY', 'SPDR S&P 500 ETF Trust', 'Large Cap Equity', Decimal('485.20')),
            ('QQQ', 'Invesco QQQ Trust', 'Technology Equity', Decimal('420.35')),
            ('IWM', 'iShares Russell 2000 ETF', 'Small Cap Equity', Decimal('198.50')),
            ('DIA', 'SPDR Dow Jones Industrial Average ETF', 'Large Cap Equity', Decimal('375.90')),
            ('VTI', 'Vanguard Total Stock Market ETF', 'Broad Market Equity', Decimal('245.60')),
        ]
        
        created = 0
        skipped = 0
        
        print("\n📈 Stocks US:")
        for ticker, nome, setor, preco in stocks:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.STOCK, 
                         classe=ClasseAtivo.RENDA_VARIAVEL, mercado='US', moeda='USD',
                         preco_atual=preco, observacoes=f"Setor: {setor}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n🏢 REITs US:")
        for ticker, nome, seg, preco in reits:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.REIT,
                         classe=ClasseAtivo.RENDA_VARIAVEL, mercado='US', moeda='USD',
                         preco_atual=preco, observacoes=f"Segmento: {seg}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n💰 Bonds US:")
        for ticker, nome, tipo, preco in bonds:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.BOND,
                         classe=ClasseAtivo.RENDA_FIXA, mercado='US', moeda='USD',
                         preco_atual=preco, observacoes=f"Tipo: {tipo}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n📊 ETFs US:")
        for ticker, nome, cat, preco in etfs:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.ETF,
                         classe=ClasseAtivo.RENDA_VARIAVEL, mercado='US', moeda='USD',
                         preco_atual=preco, observacoes=f"Categoria: {cat}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        db.session.commit()
        print("=" * 50)
        print(f"✅ Criados: {created} | Pulados: {skipped}")
        print("=" * 50)

if __name__ == '__main__':
    seed_ativos_us()
