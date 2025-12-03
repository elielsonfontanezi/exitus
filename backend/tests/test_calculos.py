import pytest
from app import create_app
from app.database import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_preco_teto_petr4(client):
    """Testa PETR4 com parâmetros BR"""
    rv = client.get('/api/calculos/preco_teto/PETR4')
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['mercado'] == 'BR'
    assert data['parametros_regiao']['taxa_livre_risco'] == '10.5%'

def test_preco_teto_multi_mercado(client):
    """Testa diferentes mercados"""
    mercados = ['PETR4', 'AAPL', 'LVMH']
    for ticker in mercados:
        rv = client.get(f'/api/calculos/preco_teto/{ticker}')
        assert rv.status_code == 200
