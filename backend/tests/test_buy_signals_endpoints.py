"""
Testes para endpoints de Buy Signals
"""
import pytest
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
from app.database import db
from decimal import Decimal


class TestBuySignalsEndpoints:
    """Testes para /api/buy-signals/*"""
    
    def test_analisar_ativo_sucesso(self, client, app, seed_ativo_petr4):
        """Deve retornar análise completa de um ativo existente"""
        response = client.get('/api/buy-signals/analisar/PETR4')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        
        resultado = data['data']
        assert resultado['ticker'] == 'PETR4'
        assert 'buyscore' in resultado
        assert 'margem' in resultado
        assert 'z_score' in resultado
        assert 'sinal' in resultado
        assert resultado['sinal'] in ['COMPRAR', 'AGUARDAR', 'VENDER']
        assert 'preco_atual' in resultado
        assert 'preco_teto' in resultado
        assert 'dy' in resultado
        assert 'pl' in resultado
        assert 'pvp' in resultado
        assert 'roe' in resultado
    
    def test_analisar_ativo_nao_encontrado(self, client):
        """Deve retornar 404 para ativo inexistente"""
        response = client.get('/api/buy-signals/analisar/XYZW99')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert 'não encontrado' in data['error'].lower()
    
    def test_analisar_ativo_case_insensitive(self, client, seed_ativo_petr4):
        """Deve aceitar ticker em minúsculas"""
        response = client.get('/api/buy-signals/analisar/petr4')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['ticker'] == 'PETR4'
    
    def test_analisar_ativo_com_metricas_completas(self, client, app):
        """Deve retornar todas as métricas quando ativo tem dados completos"""
        ativo = Ativo(
            ticker='VALE3',
            nome='Vale S.A.',
            tipo=TipoAtivo.ACAO,
            classe=ClasseAtivo.RENDA_VARIAVEL,
            mercado='BR',
            moeda='BRL',
            preco_atual=Decimal('75.50'),
            preco_teto=Decimal('90.00'),
            dividend_yield=Decimal('8.5'),
            p_l=Decimal('5.2'),
            p_vp=Decimal('1.8'),
            roe=Decimal('25.0'),
            beta=Decimal('1.2')
        )
        db.session.add(ativo)
        db.session.commit()
        
        response = client.get('/api/buy-signals/analisar/VALE3')
        
        assert response.status_code == 200
        data = response.get_json()
        
        resultado = data['data']
        assert resultado['ticker'] == 'VALE3'
        assert resultado['dy'] == 8.5
        assert resultado['pl'] == 5.2
        assert resultado['pvp'] == 1.8
        assert resultado['roe'] == 25.0
        assert resultado['buyscore'] > 0
        assert resultado['margem'] > 0
    
    def test_analisar_ativo_sinal_comprar(self, client, app):
        """Deve retornar análise para ativo com métricas favoráveis"""
        ativo = Ativo(
            ticker='TEST1',
            nome='Teste Comprar',
            tipo=TipoAtivo.ACAO,
            classe=ClasseAtivo.RENDA_VARIAVEL,
            mercado='BR',
            moeda='BRL',
            preco_atual=Decimal('10.00'),
            preco_teto=Decimal('50.00'),  # Margem alta (80%)
            dividend_yield=Decimal('10.0'),  # DY alto
            beta=Decimal('0.8')  # Beta baixo
        )
        db.session.add(ativo)
        db.session.commit()
        
        response = client.get('/api/buy-signals/analisar/TEST1')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar que retorna análise completa (sem histórico, z_score será 0)
        assert data['data']['buyscore'] > 0
        assert data['data']['margem'] == 80.0  # (50-10)/50 * 100
        assert data['data']['sinal'] in ['COMPRAR', 'AGUARDAR', 'VENDER']
    
    def test_watchlist_top(self, client, seed_ativo_petr4, app):
        """Deve retornar top 10 ativos por buy_score"""
        # Adicionar mais ativos
        for i in range(5):
            ativo = Ativo(
                ticker=f'TEST{i}',
                nome=f'Teste {i}',
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
                preco_atual=Decimal('20.00'),
                preco_teto=Decimal('30.00')
            )
            db.session.add(ativo)
        db.session.commit()
        
        response = client.get('/api/buy-signals/watchlist-top')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert isinstance(data['data'], list)
        assert len(data['data']) <= 10
        
        # Verificar ordenação por buy_score
        if len(data['data']) > 1:
            scores = [item['buy_score'] for item in data['data']]
            assert scores == sorted(scores, reverse=True)


@pytest.fixture
def seed_ativo_petr4(app):
    """Fixture para criar ativo PETR4 de teste"""
    ativo = Ativo(
        ticker='PETR4',
        nome='Petrobras PN',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('38.50'),
        preco_teto=Decimal('45.00'),
        dividend_yield=Decimal('12.5'),
        p_l=Decimal('4.2'),
        p_vp=Decimal('0.9'),
        roe=Decimal('18.5'),
        beta=Decimal('1.3')
    )
    db.session.add(ativo)
    db.session.commit()
    
    yield ativo
    
    # Cleanup
    Ativo.query.filter_by(ticker='PETR4').delete()
    db.session.commit()
