import pytest
from app.database import db


def test_margem_seguranca_ativo_existente(client, ativo_seed):
    """Endpoint público — retorna dados para ativo existente no banco de teste."""
    response = client.get(f'/api/buy-signals/margem-seguranca/{ativo_seed.ticker}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert 'margem_seguranca' in data['data']


def test_margem_seguranca_ativo_inexistente(client):
    """Ativo não encontrado retorna 404."""
    response = client.get('/api/buy-signals/margem-seguranca/TICKER_FAKE_XYZ')
    assert response.status_code == 404


def test_buy_score_ativo_existente(client, ativo_seed):
    """Endpoint público — retorna buy_score para ativo existente."""
    response = client.get(f'/api/buy-signals/buy-score/{ativo_seed.ticker}')
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert 'buy_score' in data['data']


def test_zscore_ativo_existente(client, ativo_seed):
    """Endpoint público — zscore depende de histórico; 200 ou 400 são válidos no banco de teste."""
    response = client.get(f'/api/buy-signals/zscore/{ativo_seed.ticker}')
    data = response.get_json()
    # 200 com dados ou 400 quando histórico insuficiente (sem rede externa no container de teste)
    assert response.status_code in (200, 400)
    assert data['success'] is (response.status_code == 200)


def test_watchlist_top(client):
    """Endpoint público — retorna lista com até 10 itens."""
    response = client.get('/api/buy-signals/watchlist-top')
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) <= 10
