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
    """App de teste apontando para exitusdb_test (paridade total com produção)"""
    app = create_app(testing=True)
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Client de teste"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Headers de autenticação para testes"""
    import uuid
    from app.models.usuario import Usuario, UserRole
    from flask_jwt_extended import create_access_token
    suffix = str(uuid.uuid4())[:8]
    username = f'newapi_{suffix}'
    user = Usuario(
        username=username,
        email=f'{username}@test.exitus',
        nome_completo='Test User NEWAPI',
        role=UserRole.ADMIN,
    )
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    yield {'Authorization': f'Bearer {token}'}
    db.session.delete(user)
    db.session.commit()


_PARES_PM = [
    ('AU', 'TSX'), ('CA', 'LSE'), ('CN', 'Shanghai'), ('GB', 'Tokyo'),
    ('JP', 'Euronext'), ('EU', 'NASDAQ'), ('US', 'NYSE'),
]
_pm_counter = [0]


@pytest.fixture
def sample_parametro_macro(app):
    """Parâmetro macro com par país/mercado único — faz cleanup após o teste."""
    idx = _pm_counter[0] % len(_PARES_PM)
    _pm_counter[0] += 1
    pais, mercado = _PARES_PM[idx]
    # Limpar registro pré-existente com este par (pode existir de run anterior)
    from app.models.parametros_macro import ParametrosMacro
    existente = ParametrosMacro.query.filter_by(pais=pais, mercado=mercado).first()
    if existente:
        db.session.delete(existente)
        db.session.commit()
    data = {
        'pais': pais,
        'mercado': mercado,
        'taxa_livre_risco': '0.105000',
        'crescimento_medio': '0.045000',
        'custo_capital': '0.125000',
        'inflacao_anual': '0.042000',
        'cap_rate_fii': '0.085000',
        'ytm_rf': '0.115000',
        'ativo': True,
    }
    yield data
    # Cleanup pós-teste
    registro = ParametrosMacro.query.filter_by(pais=pais, mercado=mercado).first()
    if registro:
        db.session.delete(registro)
        db.session.commit()


@pytest.fixture
def sample_fonte_dados():
    """Fonte de dados de exemplo com nome único para evitar conflito com seeds"""
    import uuid
    suffix = str(uuid.uuid4())[:8]
    return {
        'nome': f'Test API {suffix}',
        'tipo_fonte': 'api',
        'url_base': f'https://api-{suffix}.example.com',
        'requer_autenticacao': True,
        'rate_limit': '100/hour',
        'ativa': True,
        'prioridade': 99,
        'observacoes': 'API de teste'
    }


class TestParametrosMacroAPI:
    """Testes para API de Parâmetros Macro"""
    
    def test_list_parametros_macro_retorna_200(self, client, auth_headers):
        """Lista parâmetros — verifica estrutura da resposta"""
        response = client.get('/api/parametros-macro', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'parametros_macro' in data
        assert isinstance(data['parametros_macro'], list)
    
    def test_create_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Cria novo parâmetro macro"""
        response = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['pais'] == sample_parametro_macro['pais']
        assert data['mercado'] == sample_parametro_macro['mercado']
        assert float(data['taxa_livre_risco']) == 0.105
        # cleanup
        if 'id' in data:
            client.delete(f'/api/parametros-macro/{data["id"]}', headers=auth_headers)
    
    def test_create_parametro_macro_duplicate(self, client, auth_headers, sample_parametro_macro):
        """Tenta criar parâmetro duplicado"""
        r1 = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert r1.status_code == 201
        param_id = json.loads(r1.data).get('id')

        response = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'já existem' in data['error']
        # cleanup
        if param_id:
            client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
    
    def test_get_parametro_by_id(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetro por ID"""
        create_response = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert create_response.status_code == 201
        param_id = json.loads(create_response.data)['id']

        response = client.get(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pais'] == sample_parametro_macro['pais']
        # cleanup
        client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
    
    def test_get_parametro_by_pais_mercado(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetro por país/mercado"""
        r = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert r.status_code == 201
        param_id = json.loads(r.data)['id']
        pais = sample_parametro_macro['pais']
        mercado = sample_parametro_macro['mercado']

        response = client.get(f'/api/parametros-macro/pais/{pais}/mercado/{mercado}',
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pais'] == pais
        assert data['mercado'] == mercado
        # cleanup
        client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
    
    def test_get_parametro_dict(self, client, auth_headers, sample_parametro_macro):
        """Obtém parâmetros como dicionário (compatibilidade legada)"""
        r = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert r.status_code == 201
        param_id = json.loads(r.data)['id']
        pais = sample_parametro_macro['pais']
        mercado = sample_parametro_macro['mercado']

        response = client.get(f'/api/parametros-macro/dict/{pais}/{mercado}',
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'taxa_livre_risco' in data
        assert float(data['taxa_livre_risco']) == 0.105
        # cleanup
        client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
    
    def test_update_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Atualiza parâmetro existente"""
        create_response = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert create_response.status_code == 201
        param_id = json.loads(create_response.data)['id']

        update_data = {'taxa_livre_risco': '0.110000'}
        response = client.put(f'/api/parametros-macro/{param_id}',
            json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert float(data['taxa_livre_risco']) == 0.11
        # cleanup
        client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
    
    def test_delete_parametro_macro(self, client, auth_headers, sample_parametro_macro):
        """Remove parâmetro"""
        create_response = client.post('/api/parametros-macro',
            json=sample_parametro_macro, headers=auth_headers)
        assert create_response.status_code == 201
        param_id = json.loads(create_response.data)['id']

        response = client.delete(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert response.status_code == 200

        get_response = client.get(f'/api/parametros-macro/{param_id}', headers=auth_headers)
        assert get_response.status_code == 404


class TestFonteDadosAPI:
    """Testes para API de Fontes de Dados"""

    def test_list_fontes_dados_retorna_200(self, client, auth_headers):
        """Lista fontes — verifica estrutura da resposta"""
        response = client.get('/api/fontes-dados', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'fontes_dados' in data
        assert isinstance(data['fontes_dados'], list)
    
    def test_create_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Cria nova fonte de dados"""
        response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['nome'] == sample_fonte_dados['nome']
        assert data['tipo_fonte'] == 'api'
        assert data['requer_autenticacao'] is True
        # cleanup
        if 'id' in data:
            client.delete(f'/api/fontes-dados/{data["id"]}', headers=auth_headers)
    
    def test_create_fonte_dados_duplicate(self, client, auth_headers, sample_fonte_dados):
        """Tenta criar fonte duplicada"""
        r1 = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert r1.status_code == 201
        fonte_id = json.loads(r1.data).get('id')

        response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'já existe' in data['error']
        # cleanup
        if fonte_id:
            client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_get_fonte_by_id(self, client, auth_headers, sample_fonte_dados):
        """Obtém fonte por ID"""
        create_response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert create_response.status_code == 201
        fonte_id = json.loads(create_response.data)['id']

        response = client.get(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == sample_fonte_dados['nome']
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_get_fonte_by_nome(self, client, auth_headers, sample_fonte_dados):
        """Obtém fonte por nome"""
        r = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert r.status_code == 201
        fonte_id = json.loads(r.data)['id']
        nome = sample_fonte_dados['nome']

        response = client.get(f'/api/fontes-dados/nome/{nome}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == nome
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)

    def test_get_fontes_por_tipo(self, client, auth_headers, sample_fonte_dados):
        """Lista fontes por tipo"""
        r = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert r.status_code == 201
        fonte_id = json.loads(r.data)['id']

        response = client.get('/api/fontes-dados/tipo/api', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] > 0
        assert data['tipo'] == 'api'
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_get_fontes_ativas(self, client, auth_headers, sample_fonte_dados):
        """Lista fontes ativas"""
        r = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert r.status_code == 201
        fonte_id = json.loads(r.data)['id']

        response = client.get('/api/fontes-dados/ativas', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] > 0
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_registrar_consulta_sucesso(self, client, auth_headers, sample_fonte_dados):
        """Registra consulta bem-sucedida"""
        create_response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert create_response.status_code == 201
        fonte_id = json.loads(create_response.data)['id']

        response = client.post(f'/api/fontes-dados/{fonte_id}/consulta/sucesso',
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_consultas'] == 1
        assert data['total_erros'] == 0
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_registrar_erro(self, client, auth_headers, sample_fonte_dados):
        """Registra erro na consulta"""
        create_response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert create_response.status_code == 201
        fonte_id = json.loads(create_response.data)['id']

        response = client.post(f'/api/fontes-dados/{fonte_id}/consulta/erro',
            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_consultas'] == 1
        assert data['total_erros'] == 1
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_get_health_summary(self, client, auth_headers, sample_fonte_dados):
        """Obtém resumo de saúde das fontes"""
        r = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert r.status_code == 201
        fonte_id = json.loads(r.data)['id']

        response = client.get('/api/fontes-dados/health', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'healthy' in data
        assert 'degraded' in data
        assert 'down' in data
        assert 'unknown' in data
        assert 'detalhes' in data
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_update_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Atualiza fonte existente"""
        create_response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert create_response.status_code == 201
        fonte_id = json.loads(create_response.data)['id']

        update_data = {'ativa': False}
        response = client.put(f'/api/fontes-dados/{fonte_id}',
            json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ativa'] is False
        # cleanup
        client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
    
    def test_delete_fonte_dados(self, client, auth_headers, sample_fonte_dados):
        """Remove fonte de dados"""
        create_response = client.post('/api/fontes-dados',
            json=sample_fonte_dados, headers=auth_headers)
        assert create_response.status_code == 201
        fonte_id = json.loads(create_response.data)['id']

        response = client.delete(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert response.status_code == 200

        get_response = client.get(f'/api/fontes-dados/{fonte_id}', headers=auth_headers)
        assert get_response.status_code == 404


class TestServices:
    """Testes para os services"""
    
    def test_parametros_macro_service_dict_fallback(self, app):
        """Testa fallback do service para par inexistente — deve retornar defaults hardcoded"""
        with app.app_context():
            params = ParametrosMacroService.get_parametros_dict('XX', 'XX')
            assert 'taxa_livre_risco' in params
            assert 'crescimento_medio' in params
            assert isinstance(params['taxa_livre_risco'], float)
            assert isinstance(params['crescimento_medio'], float)
    
    def test_fonte_dados_service_health_retorna_estrutura(self, app):
        """Testa que health summary retorna estrutura correta (com ou sem fontes seedadas)"""
        with app.app_context():
            summary = FonteDadosService.get_health_summary()
            assert 'total' in summary
            assert 'healthy' in summary
            assert 'degraded' in summary
            assert 'down' in summary
            assert 'unknown' in summary
            assert 'detalhes' in summary
            assert isinstance(summary['total'], int)
            assert isinstance(summary['detalhes'], list)
