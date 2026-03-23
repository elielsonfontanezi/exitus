"""
Testes para endpoints de Câmbio
"""
import pytest
from datetime import date
from decimal import Decimal
from app.models.taxa_cambio import TaxaCambio


class TestCambioEndpoints:
    """Testes para /api/cambio/*"""
    
    def test_taxa_atual_sucesso(self, client, db_session):
        """Deve retornar taxa de câmbio atual entre duas moedas"""
        # Criar taxa no banco
        taxa = TaxaCambio(
            par_moeda='USD/BRL',
            taxa=Decimal('5.00'),
            data_referencia=date.today(),
            fonte='teste'
        )
        db_session.add(taxa)
        db_session.commit()
        
        response = client.get('/api/cambio/taxa-atual?de=USD&para=BRL')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['par_moeda'] == 'USD/BRL'
        assert 'taxa' in data['data']
    
    def test_taxa_atual_sem_parametros(self, client):
        """Deve retornar erro 400 quando faltam parâmetros"""
        response = client.get('/api/cambio/taxa-atual')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'obrigatórios' in data['message'].lower()
    
    def test_taxa_atual_moeda_invalida(self, client):
        """Deve retornar erro para moedas com formato inválido"""
        response = client.get('/api/cambio/taxa-atual?de=US&para=BRL')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert '3 caracteres' in data['message']
    
    def test_taxa_atual_case_insensitive(self, client, db_session):
        """Deve aceitar moedas em minúsculas"""
        taxa = TaxaCambio(
            par_moeda='USD/BRL',
            taxa=Decimal('5.00'),
            data_referencia=date.today(),
            fonte='teste'
        )
        db_session.add(taxa)
        db_session.commit()
        
        response = client.get('/api/cambio/taxa-atual?de=usd&para=brl')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
    
    def test_taxa_atual_fallback(self, client):
        """Deve usar taxa fallback quando não há no banco"""
        # Não criar taxa no banco, deve usar fallback
        response = client.get('/api/cambio/taxa-atual?de=USD&para=BRL')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['fonte'] in ['fallback', 'banco', 'cruzamento_brl']
    
    def test_taxa_atual_moedas_iguais(self, client):
        """Deve retornar taxa 1.0 para moedas iguais"""
        response = client.get('/api/cambio/taxa-atual?de=BRL&para=BRL')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['taxa'] == 1.0
        assert data['data']['fonte'] == 'identidade'
    
    def test_taxa_atual_multiplas_moedas(self, client, db_session):
        """Deve funcionar para diferentes pares de moedas"""
        pares = [
            ('USD/BRL', Decimal('5.00')),
            ('EUR/BRL', Decimal('5.50')),
            ('BRL/USD', Decimal('0.20')),
        ]
        
        for par, taxa_valor in pares:
            taxa = TaxaCambio(
                par_moeda=par,
                taxa=taxa_valor,
                data_referencia=date.today(),
                fonte='teste'
            )
            db_session.add(taxa)
        db_session.commit()
        
        # Testar USD -> BRL
        response = client.get('/api/cambio/taxa-atual?de=USD&para=BRL')
        assert response.status_code == 200
        
        # Testar EUR -> BRL
        response = client.get('/api/cambio/taxa-atual?de=EUR&para=BRL')
        assert response.status_code == 200
        
        # Testar BRL -> USD
        response = client.get('/api/cambio/taxa-atual?de=BRL&para=USD')
        assert response.status_code == 200
    
    def test_taxa_atual_sem_autenticacao(self, client):
        """Endpoint /taxa-atual deve ser público (sem JWT)"""
        # Não passar token JWT
        response = client.get('/api/cambio/taxa-atual?de=USD&para=BRL')
        
        # Deve funcionar sem autenticação
        assert response.status_code in [200, 404]  # 200 se tem taxa, 404 se não tem
        data = response.get_json()
        
        # Não deve retornar erro de autenticação
        if not data['success']:
            assert 'autenticação' not in data.get('message', '').lower()
            assert 'token' not in data.get('message', '').lower()


class TestCambioIntegration:
    """Testes de integração para câmbio"""
    
    def test_taxa_atual_com_frontend_format(self, client, db_session):
        """Deve retornar formato esperado pelo frontend"""
        taxa = TaxaCambio(
            par_moeda='USD/BRL',
            taxa=Decimal('5.25'),
            data_referencia=date.today(),
            fonte='teste'
        )
        db_session.add(taxa)
        db_session.commit()
        
        response = client.get('/api/cambio/taxa-atual?de=USD&para=BRL')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estrutura esperada pelo frontend
        assert 'success' in data
        assert 'data' in data
        assert 'taxa' in data['data']
        
        # Taxa deve ser numérica
        assert isinstance(data['data']['taxa'], (int, float))
        assert data['data']['taxa'] > 0
