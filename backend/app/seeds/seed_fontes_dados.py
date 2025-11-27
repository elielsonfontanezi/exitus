# -*- coding: utf-8 -*-
"""
Exitus - Seed de Fontes de Dados
Popular tabela fonte_dados com APIs de cotações
"""

from app import create_app
from app.database import db
from app.models import FonteDados, TipoFonteDados


def seed_fontes_dados():
    """Cria fontes de dados (APIs)"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("SEED: Criando Fontes de Dados (APIs)")
        print("=" * 50)
        
        # Verificar se já existem fontes
        count = FonteDados.query.count()
        if count > 0:
            print(f"⚠ Já existem {count} fontes de dados cadastradas.")
            resposta = input("Deseja recriar as fontes? (s/N): ").lower()
            if resposta != 's':
                print("✗ Seed cancelado pelo usuário.")
                return
            
            # Limpar fontes existentes
            FonteDados.query.delete()
            db.session.commit()
            print("✓ Fontes de dados anteriores removidas.")
        
        # Fontes de dados
        fontes = [
            {
                'nome': 'yfinance',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://query1.finance.yahoo.com',
                'requer_autenticacao': False,
                'rate_limit': '2000/hour',
                'ativa': True,
                'prioridade': 1,
                'observacoes': 'Biblioteca Python gratuita para Yahoo Finance. Boa cobertura global, incluindo B3.'
            },
            {
                'nome': 'brapi.dev',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://brapi.dev/api',
                'requer_autenticacao': False,
                'rate_limit': '100/minute',
                'ativa': True,
                'prioridade': 1,
                'observacoes': 'API brasileira gratuita especializada em ativos da B3. Dados em tempo real.'
            },
            {
                'nome': 'Alpha Vantage',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://www.alphavantage.co/query',
                'requer_autenticacao': True,
                'rate_limit': '5/minute',
                'ativa': True,
                'prioridade': 2,
                'observacoes': 'API gratuita com chave. Limite de 5 requisições por minuto (plano free).'
            },
            {
                'nome': 'Finnhub',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://finnhub.io/api/v1',
                'requer_autenticacao': True,
                'rate_limit': '60/minute',
                'ativa': True,
                'prioridade': 2,
                'observacoes': 'API com plano gratuito. Boa cobertura de mercados globais e notícias.'
            },
            {
                'nome': 'IEX Cloud',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://cloud.iexapis.com/stable',
                'requer_autenticacao': True,
                'rate_limit': '50000/month',
                'ativa': True,
                'prioridade': 3,
                'observacoes': 'API focada em mercado americano. Plano gratuito com limite mensal.'
            },
            {
                'nome': 'Polygon.io',
                'tipo_fonte': TipoFonteDados.API,
                'url_base': 'https://api.polygon.io',
                'requer_autenticacao': True,
                'rate_limit': '5/minute',
                'ativa': False,
                'prioridade': 4,
                'observacoes': 'API premium com dados históricos detalhados. Desativada por padrão.'
            },
            {
                'nome': 'Manual',
                'tipo_fonte': TipoFonteDados.MANUAL,
                'url_base': None,
                'requer_autenticacao': False,
                'rate_limit': None,
                'ativa': True,
                'prioridade': 99,
                'observacoes': 'Entrada manual de dados pelo usuário.'
            },
        ]
        
        created_fontes = []
        
        print("\n🔌 Criando Fontes de Dados...")
        for fonte_data in fontes:
            fonte = FonteDados(
                nome=fonte_data['nome'],
                tipo_fonte=fonte_data['tipo_fonte'],
                url_base=fonte_data['url_base'],
                requer_autenticacao=fonte_data['requer_autenticacao'],
                rate_limit=fonte_data['rate_limit'],
                ativa=fonte_data['ativa'],
                prioridade=fonte_data['prioridade'],
                observacoes=fonte_data['observacoes']
            )
            db.session.add(fonte)
            created_fontes.append(fonte)
            
            status_icon = "✓" if fonte.ativa else "✗"
            auth_icon = "🔐" if fonte.requer_autenticacao else "🔓"
            
            print(f"  {status_icon} {auth_icon} {fonte.nome:20} | Prioridade: {fonte.prioridade} | Limite: {fonte.rate_limit or 'N/A'}")
        
        # Commit no banco
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print(f"✓ {len(created_fontes)} fontes de dados criadas!")
            print("=" * 50)
            print("\n📌 LEGENDA:")
            print("  ✓ = Ativa    | ✗ = Inativa")
            print("  🔓 = Sem auth | 🔐 = Requer chave API")
            print("\n💡 PRIORIDADE:")
            print("  1 = Alta (usar primeiro)")
            print("  2-3 = Média (fallback)")
            print("  99 = Baixa (manual)\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar fontes: {e}")
            raise


if __name__ == '__main__':
    seed_fontes_dados()
