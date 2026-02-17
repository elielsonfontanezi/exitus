"""Exitus - Seed de Ativos Europeus"""
from app import create_app
from app.database import db
from app.models import Ativo, TipoAtivo, ClasseAtivo
from decimal import Decimal

def seed_ativos_eu():
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Ativos Europeus")
        print("=" * 50)
        
        stocks_intl = [
            ('ASML', 'ASML Holding NV', 'EURONEXT', 'Technology', Decimal('750.30')),
            ('SAP', 'SAP SE', 'XETRA', 'Technology', Decimal('145.80')),
        ]
        
        etfs_intl = [
            ('VWCE.DE', 'Vanguard FTSE All-World ETF', 'XETRA', 'Global Equity', Decimal('105.40')),
        ]
        
        created = 0
        skipped = 0
        
        print("\n🌍 Stocks Internacionais (EU):")
        for ticker, nome, bolsa, setor, preco in stocks_intl:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.STOCK_INTL,
                         classe=ClasseAtivo.RENDA_VARIAVEL, mercado='EU', moeda='EUR',
                         preco_atual=preco, observacoes=f"Bolsa: {bolsa} | Setor: {setor}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        print("\n📊 ETFs Internacionais (EU):")
        for ticker, nome, bolsa, cat, preco in etfs_intl:
            if Ativo.query.filter_by(ticker=ticker).first():
                print(f"  ⚠️  {ticker} - existe")
                skipped += 1
                continue
            ativo = Ativo(ticker=ticker, nome=nome, tipo=TipoAtivo.ETF_INTL,
                         classe=ClasseAtivo.RENDA_VARIAVEL, mercado='EU', moeda='EUR',
                         preco_atual=preco, observacoes=f"Bolsa: {bolsa} | Categoria: {cat}", ativo=True)
            db.session.add(ativo)
            created += 1
            print(f"  ✅ {ticker} - {nome[:30]}")
        
        db.session.commit()
        print("=" * 50)
        print(f"✅ Criados: {created} | Pulados: {skipped}")
        print("=" * 50)

if __name__ == '__main__':
    seed_ativos_eu()
