# -*- coding: utf-8 -*-
"""
Exitus - Seed de Ativos Brasileiros
Popular tabela ativo com ações e FIIs da B3
"""

from app import create_app
from app.database import db
from app.models import Ativo, TipoAtivo, ClasseAtivo
from decimal import Decimal


def seed_ativos_br():
    """Cria ativos brasileiros (B3)"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Ativos Brasileiros (B3)")
        print("=" * 50)
        
        # Verificar se já existem ativos
        count = Ativo.query.filter_by(mercado='BR').count()
        if count > 0:
            print(f"⚠ Já existem {count} ativos brasileiros cadastrados.")
            resposta = input("Deseja recriar os ativos BR? (s/N): ").lower()
            if resposta != 's':
                print("✗ Seed cancelado pelo usuário.")
                return
            
            # Limpar ativos BR existentes
            Ativo.query.filter_by(mercado='BR').delete()
            db.session.commit()
            print("✓ Ativos brasileiros anteriores removidos.")
        
        # Ações mais negociadas da B3
        acoes = [
            # Ticker, Nome, Setor, Preço Inicial
            ('PETR4', 'Petrobras PN', 'Petróleo e Gás', Decimal('38.50')),
            ('VALE3', 'Vale ON', 'Mineração', Decimal('62.80')),
            ('ITUB4', 'Itaú Unibanco PN', 'Bancos', Decimal('28.45')),
            ('BBDC4', 'Bradesco PN', 'Bancos', Decimal('13.20')),
            ('BBAS3', 'Banco do Brasil ON', 'Bancos', Decimal('25.60')),
            ('MGLU3', 'Magazine Luiza ON', 'Varejo', Decimal('8.75')),
            ('WEGE3', 'WEG ON', 'Máquinas e Equipamentos', Decimal('42.30')),
            ('RENT3', 'Localiza ON', 'Locação de Veículos', Decimal('56.90')),
            ('RAIL3', 'Rumo ON', 'Transporte', Decimal('18.45')),
            ('SUZB3', 'Suzano ON', 'Papel e Celulose', Decimal('52.80')),
            ('KLBN11', 'Klabin Units', 'Papel e Celulose', Decimal('22.15')),
            ('ELET3', 'Eletrobras ON', 'Energia Elétrica', Decimal('42.10')),
            ('CMIG4', 'Cemig PN', 'Energia Elétrica', Decimal('10.85')),
            ('CPLE6', 'Copel PNB', 'Energia Elétrica', Decimal('8.95')),
            ('ABEV3', 'Ambev ON', 'Bebidas', Decimal('11.20')),
        ]
        
        # FIIs mais negociados
        fiis = [
            # Ticker, Nome, Segmento, Preço Inicial
            ('HGLG11', 'CSHG Logística FII', 'Logística', Decimal('152.30')),
            ('VISC11', 'Vinci Shopping Centers FII', 'Shopping', Decimal('105.80')),
            ('KNRI11', 'Kinea Renda Imobiliária FII', 'Híbrido', Decimal('98.45')),
            ('BTLG11', 'BTG Pactual Logística FII', 'Logística', Decimal('102.70')),
            ('XPML11', 'XP Malls FII', 'Shopping', Decimal('95.60')),
            ('MXRF11', 'Maxi Renda FII', 'Híbrido', Decimal('10.25')),
            ('TRXF11', 'TRX Real Estate FII', 'Lajes Corporativas', Decimal('95.30')),
            ('KNCR11', 'Kinea Rendimentos Imobiliários FII', 'Papel', Decimal('110.50')),
            ('LVBI11', 'VBI Logístico FII', 'Logística', Decimal('98.20')),
            ('GGRC11', 'GGR Covepi Renda FII', 'Lajes Corporativas', Decimal('105.40')),
        ]
        
        created_ativos = []
        
        # Criar ações
        print("\n📈 Criando Ações...")
        for ticker, nome, setor, preco in acoes:
            ativo = Ativo(
                ticker=ticker,
                nome=nome,
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                preco_atual=preco,
                observacoes=f'Setor: {setor}',
                ativo=True
            )
            db.session.add(ativo)
            created_ativos.append(ativo)
            print(f"  ✓ {ticker:8} - {nome:35} - R$ {preco}")
        
        # Criar FIIs
        print("\n🏢 Criando FIIs...")
        for ticker, nome, segmento, preco in fiis:
            ativo = Ativo(
                ticker=ticker,
                nome=nome,
                tipo=TipoAtivo.FII,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                preco_atual=preco,
                observacoes=f'Segmento: {segmento}',
                ativo=True
            )
            db.session.add(ativo)
            created_ativos.append(ativo)
            print(f"  ✓ {ticker:8} - {nome:40} - R$ {preco}")
        
        # Commit no banco
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✓ {len(created_ativos)} ativos criados com sucesso!")
            print(f"  - {len(acoes)} ações")
            print(f"  - {len(fiis)} FIIs")
            print("=" * 50 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar ativos: {e}")
            raise


if __name__ == '__main__':
    seed_ativos_br()
