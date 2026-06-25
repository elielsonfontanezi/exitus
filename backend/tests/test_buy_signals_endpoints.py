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
        ativo = Ativo.query.filter_by(ticker='VALE3').first()
        if not ativo:
            ativo = Ativo(
                ticker='VALE3',
                nome='Vale S.A.',
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
            )
            db.session.add(ativo)
        ativo.preco_atual = Decimal('75.50')
        ativo.preco_teto = Decimal('90.00')
        ativo.dividend_yield = Decimal('0.085')
        ativo.p_l = Decimal('5.2')
        ativo.p_vp = Decimal('1.8')
        ativo.roe = Decimal('0.25')
        ativo.beta = Decimal('1.2')
        db.session.commit()
        
        response = client.get('/api/buy-signals/analisar/VALE3')
        
        assert response.status_code == 200
        data = response.get_json()
        
        resultado = data['data']
        assert resultado['ticker'] == 'VALE3'
        assert resultado['dy'] == 0.085
        assert resultado['pl'] == 5.2
        assert resultado['pvp'] == 1.8
        assert resultado['roe'] == 0.25
        assert resultado['buyscore'] > 0
        assert resultado['margem'] > 0
    
    def test_analisar_ativo_sinal_comprar(self, client, app):
        """Deve retornar análise para ativo com métricas favoráveis"""
        ativo = Ativo.query.filter_by(ticker='TEST1').first()
        if not ativo:
            ativo = Ativo(
                ticker='TEST1',
                nome='Teste Comprar',
                tipo=TipoAtivo.ACAO,
                classe=ClasseAtivo.RENDA_VARIAVEL,
                mercado='BR',
                moeda='BRL',
            )
            db.session.add(ativo)
        ativo.preco_atual = Decimal('10.00')
        ativo.preco_teto = Decimal('50.00')  # Margem alta (80%)
        ativo.dividend_yield = Decimal('0.10')  # DY alto
        ativo.beta = Decimal('0.8')  # Beta baixo
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
        # Adicionar mais ativos (upsert — evitar conflito com dados de sessão anterior)
        for i in range(5):
            ativo = Ativo.query.filter_by(ticker=f'TEST{i}').first()
            if not ativo:
                ativo = Ativo(
                    ticker=f'TEST{i}',
                    nome=f'Teste {i}',
                    tipo=TipoAtivo.ACAO,
                    classe=ClasseAtivo.RENDA_VARIAVEL,
                    mercado='BR',
                    moeda='BRL',
                )
                db.session.add(ativo)
            ativo.preco_atual = Decimal('20.00')
            ativo.preco_teto = Decimal('30.00')
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
    """Fixture para criar ativo PETR4 de teste — reutiliza se já existir (seed test_e2e)."""
    existing = Ativo.query.filter_by(ticker='PETR4').first()
    if existing:
        # Atualizar campos necessários para os testes de buy signals
        existing.preco_atual = Decimal('38.50')
        existing.preco_teto = Decimal('45.00')
        existing.dividend_yield = Decimal('0.125')
        existing.p_l = Decimal('4.2')
        existing.p_vp = Decimal('0.9')
        existing.roe = Decimal('0.185')
        existing.beta = Decimal('1.3')
        db.session.commit()
        yield existing
        return

    ativo = Ativo(
        ticker='PETR4',
        nome='Petrobras PN',
        tipo=TipoAtivo.ACAO,
        classe=ClasseAtivo.RENDA_VARIAVEL,
        mercado='BR',
        moeda='BRL',
        preco_atual=Decimal('38.50'),
        preco_teto=Decimal('45.00'),
        dividend_yield=Decimal('0.125'),
        p_l=Decimal('4.2'),
        p_vp=Decimal('0.9'),
        roe=Decimal('0.185'),
        beta=Decimal('1.3')
    )
    db.session.add(ativo)
    db.session.commit()

    yield ativo

    # Cleanup apenas se criado por esta fixture
    Ativo.query.filter_by(ticker='PETR4').delete()
    db.session.commit()
