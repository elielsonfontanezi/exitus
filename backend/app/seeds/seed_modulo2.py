# -*- coding: utf-8 -*-
"""Exitus - Seed Módulo 2 - Usuários, Corretoras e Ativos"""

from app.database import db
from app.models import Usuario, UserRole, Corretora, TipoCorretora, Ativo, TipoAtivo, ClasseAtivo
from decimal import Decimal

def seed_usuarios():
    """Seed de usuários"""
    print("\n🔐 Seeding Usuários...")
    
    usuarios = [
        {
            "username": "admin",
            "email": "admin@exitus.com",
            "nome_completo": "Administrador do Sistema",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "joao.silva",
            "email": "joao.silva@email.com",
            "nome_completo": "João Silva",
            "password": "user123",
            "role": UserRole.USER
        },
        {
            "username": "maria.santos",
            "email": "maria.santos@email.com",
            "nome_completo": "Maria Santos",
            "password": "user123",
            "role": UserRole.USER
        }
    ]
    
    for data in usuarios:
        existing = Usuario.query.filter_by(username=data['username']).first()
        if not existing:
            user = Usuario(
                username=data['username'],
                email=data['email'],
                nome_completo=data['nome_completo'],
                role=data['role'],
                ativo=True
            )
            user.set_password(data['password'])
            db.session.add(user)
            print(f"  ✅ Criado: {data['username']}")
        else:
            print(f"  ℹ️  Já existe: {data['username']}")
    
    db.session.commit()
    print("✅ Usuários criados!")

def seed_corretoras():
    """Seed de corretoras para usuário joao.silva"""
    print("\n🏦 Seeding Corretoras...")
    
    user = Usuario.query.filter_by(username='joao.silva').first()
    if not user:
        print("❌ Usuário joao.silva não encontrado")
        return
    
    corretoras = [
        {
            "nome": "XP Investimentos",
            "tipo": TipoCorretora.CORRETORA,
            "pais": "BR",
            "moeda_padrao": "BRL"
        },
        {
            "nome": "Clear Corretora",
            "tipo": TipoCorretora.CORRETORA,
            "pais": "BR",
            "moeda_padrao": "BRL"
        }
    ]
    
    for data in corretoras:
        existing = Corretora.query.filter_by(
            usuario_id=user.id,
            nome=data['nome']
        ).first()
        
        if not existing:
            corretora = Corretora(
                usuario_id=user.id,
                nome=data['nome'],
                tipo=data['tipo'],
                pais=data['pais'],
                moeda_padrao=data['moeda_padrao'],
                saldo_atual=Decimal('0.00'),
                ativa=True
            )
            db.session.add(corretora)
            print(f"  ✅ Criado: {data['nome']}")
        else:
            print(f"  ℹ️  Já existe: {data['nome']}")
    
    db.session.commit()
    print("✅ Corretoras criadas!")

def seed_ativos():
    """Seed de ativos - MANTÉM OS 25 ATIVOS ORIGINAIS"""
    print("\n📈 Seeding Ativos...")
    
    ativos_br = [
        # Ações BR
        {"ticker": "PETR4", "nome": "Petrobras PN", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "38.50", "observacoes": "Setor: Petróleo e Gás"},
        {"ticker": "VALE3", "nome": "Vale ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "62.80", "observacoes": "Setor: Mineração"},
        {"ticker": "ITUB4", "nome": "Itaú Unibanco PN", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "28.45", "observacoes": "Setor: Bancos"},
        {"ticker": "BBDC4", "nome": "Bradesco PN", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "13.20", "observacoes": "Setor: Bancos"},
        {"ticker": "BBAS3", "nome": "Banco do Brasil ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "25.60", "observacoes": "Setor: Bancos"},
        {"ticker": "MGLU3", "nome": "Magazine Luiza ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "8.75", "observacoes": "Setor: Varejo"},
        {"ticker": "WEGE3", "nome": "WEG ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "42.30", "observacoes": "Setor: Máquinas e Equipamentos"},
        {"ticker": "RENT3", "nome": "Localiza ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "56.90", "observacoes": "Setor: Locação de Veículos"},
        {"ticker": "RAIL3", "nome": "Rumo ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "18.45", "observacoes": "Setor: Transporte"},
        {"ticker": "SUZB3", "nome": "Suzano ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "52.80", "observacoes": "Setor: Papel e Celulose"},
        {"ticker": "KLBN11", "nome": "Klabin Units", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "22.15", "observacoes": "Setor: Papel e Celulose"},
        {"ticker": "ELET3", "nome": "Eletrobras ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "42.10", "observacoes": "Setor: Energia Elétrica"},
        {"ticker": "CMIG4", "nome": "Cemig PN", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "10.85", "observacoes": "Setor: Energia Elétrica"},
        {"ticker": "CPLE6", "nome": "Copel PNB", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "8.95", "observacoes": "Setor: Energia Elétrica"},
        {"ticker": "ABEV3", "nome": "Ambev ON", "tipo": TipoAtivo.ACAO, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "11.20", "observacoes": "Setor: Bebidas"},
        
        # FIIs BR
        {"ticker": "HGLG11", "nome": "CSHG Logística FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "152.30", "observacoes": "Segmento: Logística"},
        {"ticker": "KNRI11", "nome": "Kinea Renda Imobiliária FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "98.45", "observacoes": "Segmento: Híbrido"},
        {"ticker": "BTLG11", "nome": "BTG Pactual Logística FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "102.70", "observacoes": "Segmento: Logística"},
        {"ticker": "MXRF11", "nome": "Maxi Renda FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "10.25", "observacoes": "Segmento: Híbrido"},
        {"ticker": "KNCR11", "nome": "Kinea Rendimentos Imobiliários FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "110.50", "observacoes": "Segmento: Papel"},
        {"ticker": "LVBI11", "nome": "VBI Logístico FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "98.20", "observacoes": "Segmento: Logística"},
        {"ticker": "GGRC11", "nome": "GGR Covepi Renda FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "105.40", "observacoes": "Segmento: Lajes Corporativas"},
        {"ticker": "XPML11", "nome": "XP Malls FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "9.85", "observacoes": "Segmento: Shoppings"},
        {"ticker": "VISC11", "nome": "Vinci Shopping Centers FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "7.90", "observacoes": "Segmento: Shoppings"},
        {"ticker": "TRXF11", "nome": "TRX Real Estate FII", "tipo": TipoAtivo.FII, "classe": ClasseAtivo.RENDA_VARIAVEL, "mercado": "BR", "moeda": "BRL", "preco_atual": "92.30", "observacoes": "Segmento: Lajes Corporativas"},
    ]
    
    for data in ativos_br:
        existing = Ativo.query.filter_by(ticker=data['ticker'], mercado=data['mercado']).first()
        if not existing:
            ativo = Ativo(
                ticker=data['ticker'],
                nome=data['nome'],
                tipo=data['tipo'],
                classe=data['classe'],
                mercado=data['mercado'],
                moeda=data['moeda'],
                preco_atual=Decimal(data['preco_atual']) if data.get('preco_atual') else None,
                observacoes=data.get('observacoes'),
                ativo=True,
                deslistado=False
            )
            db.session.add(ativo)
            print(f"  ✅ Criado: {data['ticker']}")
        else:
            print(f"  ℹ️  Já existe: {data['ticker']}")
    
    db.session.commit()
    print("✅ Ativos criados!")

def run_seed_modulo2():
    """Executa todos os seeds do Módulo 2"""
    print("=" * 60)
    print("🌱 SEED MÓDULO 2 - Usuários, Corretoras, Ativos")
    print("=" * 60)
    
    seed_usuarios()
    seed_corretoras()
    seed_ativos()
    
    print("\n" + "=" * 60)
    print("✅ SEED MÓDULO 2 CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        run_seed_modulo2()
