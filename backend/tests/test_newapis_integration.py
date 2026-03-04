# -*- coding: utf-8 -*-
"""
Exitus - Testes de Integração - NEWAPIS-001
Testes CRUD para endpoints de parametros_macro e fonte_dados
"""

import pytest
import json
from decimal import Decimal
from app import create_app
from app.database import db
from app.models.parametros_macro import ParametrosMacro
from app.models.fonte_dados import FonteDados, TipoFonteDados
from app.services.parametros_macro_service import ParametrosMacroService
from app.services.fonte_dados_service import FonteDadosService


@pytest.fixture
def app():
    """App de teste com banco em memória"""
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de teste"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Headers de autenticação para testes"""
    # Cria usuário de teste
    from app.models.usuario import Usuario, UserRole
    user = Usuario(
        email="test@example.com",
        nome="Test User",
        role=UserRole.USER
    )
    user.set_senha("test123")
    db.session.add(user)
    db.session.commit()
    
    # Faz login
    response = app.test_client().post('/api/auth/login', 
        json={'username': 'test@example.com', 'password': 'test123'})
    token = json.loads(response.data)['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_parametro_macro():
    """Parâmetro macro de exemplo"""
    return {
        'pais': 'BR',
        'mercado': 'B3',
        'taxa_livre_risco': '0.105000',
        'crescimento_medio': '0.045000',
        'custo_capital': '0.125000',
        'inflacao_anual': '0.042000',
        'cap_rate_fii': '0.085000',
        'ytm_rf': '0.115000',
        'ativo': True
    }


@pytest.fixture
def sample_fonte_dados():
    """Fonte de dados de exemplo"""
    return {
        'nome': 'Test API',
        'tipo_fonte': 'api',
        'url_base': 'https://api.example.com',
        'requer_autenticacao': True,
        'rate_limit': '100/hour',
        'ativa': True,
        'prioridade': 1,
        'observacoes': 'API de teste'
    }


class TestParametrosMacroAPI:
    """Testes para API de Parâmetros Macro"""
    
    def test_list_parametros_macro_empty(self, client, auth_headers):
        """Lista parâmetros quando banco está vazio"""
        response = client.get('/api/parametros-macro', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 0
        assert len(data['parametros_macro']) == 0
    
    def test_create_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Cria novo parâmetro macro"""
        response = client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['pais'] == 'BR'
        assert data['mercado'] == 'B3'
        assert float(data['taxa_livre_risco']) == 0.105
    
    def test_create_parametro_macro_duplicate(self, client, auth_headers, sample_parametro_macro):
        """Tenta criar parâmetro duplicado"""
        # Primeira criação
        client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        
        # Segunda criação (deve falhar)
        response = client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'já existem' in data['error']
    
    def test_get_parametro_by_id(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetro por ID"""
        # Cria parâmetro
        create_response = client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        param_id = json.loads(create_response.data)['id']
        
        # Obtém por ID
        response = client.get(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pais'] == 'BR'
    
    def test_get_parametro_by_pais_mercado(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetro por país/mercado"""
        # Cria parâmetro
        client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        
        # Obtém por país/mercado
        response = client.get('/api/parametros-macro/pais/BR/mercado/B3', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pais'] == 'BR'
        assert data['mercado'] == 'B3'
    
    def test_get_parametro_dict(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetros como dicionário (compatibilidade legada)"""
        # Cria parâmetro
        client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        
        # Obtém como dict
        response = client.get('/api/parametros-macro/dict/BR/B3', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'taxa_livre_risco' in data
        assert float(data['taxa_livre_risco']) == 0.105
    
    def test_update_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Atualiza parâmetro existente"""
        # Cria parâmetro
        create_response = client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        param_id = json.loads(create_response.data)['id']
        
        # Atualiza
        update_data = {'taxa_livre_risco': '0.110000'}
        response = client.put(f'/api/parametros-macro/{param_id}', 
            json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert float(data['taxa_livre_risco']) == 0.11
    
    def test_delete_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Remove parâmetro"""
        # Cria parâmetro
        create_response = client.post('/api/parametros-macro', 
            json=sample_parametro_macro, headers=auth_headers)
        param_id = json.loads(create_response.data)['id']
        
        # Remove
        response = client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verifica que foi removido
        get_response = client.get(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert get_response.status_code == 404


class TestFonteDadosAPI:
    """Testes para API de Fontes de Dados"""
    
    def test_list_fontes_dados_empty(self, client, auth_headers):
        """Lista fontes quando banco está vazio"""
        response = client.get('/api/fontes-dados', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 0
        assert len(data['fontes_dados']) == 0
    
    def test_create_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Cria nova fonte de dados"""
        response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['nome'] == 'Test API'
        assert data['tipo_fonte'] == 'api'
        assert data['requer_autenticacao'] == True
    
    def test_create_fonte_dados_duplicate(self, client, auth_headers, sample_fonte_dados):
        """Tenta criar fonte duplicada"""
        # Primeira criação
        client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        
        # Segunda criação (deve falhar)
        response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'já existe' in data['error']
    
    def test_get_fonte_by_id(self, client, auth_headers, sample_fonte_dados):
        """Obtém fonte por ID"""
        # Cria fonte
        create_response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        fonte_id = json.loads(create_response.data)['id']
        
        # Obtém por ID
        response = client.get(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == 'Test API'
    
    def test_get_fonte_by_nome(self, client, auth_headers, sample_fonte_dados):
        """Obtém fonte por nome"""
        # Cria fonte
        client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        
        # Obtém por nome
        response = client.get('/api/fontes-dados/nome/Test API', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == 'Test API'
    
    def test_get_fontes_por_tipo(self, client, auth_headers, sample_fonte_dados):
        """Lista fontes por tipo"""
        # Cria fonte
        client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        
        # Obtém por tipo
        response = client.get('/api/fontes-dados/tipo/api', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert data['tipo'] == 'api'
    
    def test_get_fontes_ativas(self, client, auth_headers, sample_fonte_dados):
        """Lista fontes ativas ordenadas por prioridade"""
        # Cria fonte
        client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        
        # Obtém ativas
        response = client.get('/api/fontes-dados/ativas', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
    
    def test_registrar_consulta_sucesso(self, client, auth_headers, sample_fonte_dados):
        """Registra consulta bem-sucedida"""
        # Cria fonte
        create_response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        fonte_id = json.loads(create_response.data)['id']
        
        # Registra consulta
        response = client.post(f'/api/fontes-dados/{fonte_id}/consulta/sucesso', 
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_consultas'] == 1
        assert data['total_erros'] == 0
    
    def test_registrar_erro(self, client, auth_headers, sample_fonte_dados):
        """Registra erro na consulta"""
        # Cria fonte
        create_response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        fonte_id = json.loads(create_response.data)['id']
        
        # Registra erro
        response = client.post(f'/api/fontes-dados/{fonte_id}/consulta/erro', 
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_consultas'] == 1
        assert data['total_erros'] == 1
    
    def test_get_health_summary(self, client, auth_headers, sample_fonte_dados):
        """Obtém resumo de saúde das fontes"""
        # Cria fonte
        client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        
        # Obtém health summary
        response = client.get('/api/fontes-dados/health', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'healthy' in data
        assert 'degraded' in data
        assert 'down' in data
        assert 'unknown' in data
        assert 'detalhes' in data
    
    def test_update_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Atualiza fonte existente"""
        # Cria fonte
        create_response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        fonte_id = json.loads(create_response.data)['id']
        
        # Atualiza
        update_data = {'ativa': False}
        response = client.put(f'/api/fontes-dados/{fonte_id}', 
            json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ativa'] == False
    
    def test_delete_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Remove fonte de dados"""
        # Cria fonte
        create_response = client.post('/api/fontes-dados', 
            json=sample_fonte_dados, headers=auth_headers)
        fonte_id = json.loads(create_response.data)['id']
        
        # Remove
        response = client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verifica que foi removida
        get_response = client.get(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert get_response.status_code == 404


class TestServices:
    """Testes para os services"""
    
    def test_parametros_macro_service_dict_fallback(self, app):
        """Testa fallback do service quando tabela está vazia"""
        with app.app_context():
            # Sem dados no banco, deve retornar defaults
            params = ParametrosMacroService.get_parametros_dict('XX', 'XX')
            assert params['taxa_livre_risco'] == 0.105
            assert params['crescimento_medio'] == 0.05
    
    def test_fonte_dados_service_health_empty(self, app):
        """Testa health summary sem fontes ativas"""
        with app.app_context():
            summary = FonteDadosService.get_health_summary()
            assert summary['total'] == 0
            assert summary['healthy'] == 0
            assert len(summary['detalhes']) == 0
