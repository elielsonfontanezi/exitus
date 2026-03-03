import pytest


def test_preco_teto_ativo_existente(auth_client, ativo_seed):
    """Endpoint protegido — retorna preço teto para ativo existente no banco de teste."""
    rv = auth_client.get(
        f'/api/calculos/preco_teto/{ativo_seed.ticker}',
        headers=auth_client._auth_headers,
    )
    data = rv.get_json()
    assert rv.status_code == 200
    assert data['ativo'] == ativo_seed.ticker
    assert data['mercado'] == ativo_seed.mercado
    assert 'pt_medio' in data
    assert 'parametros_regiao' in data
    assert 'taxa_livre_risco' in data['parametros_regiao']


def test_preco_teto_ativo_inexistente(auth_client):
    """Ativo não encontrado retorna 404."""
    rv = auth_client.get(
        '/api/calculos/preco_teto/TICKER_FAKE_XYZ',
        headers=auth_client._auth_headers,
    )
    assert rv.status_code == 404


def test_preco_teto_sem_auth_retorna_401(client):
    """Endpoint protegido por JWT — sem token retorna 401."""
    rv = client.get('/api/calculos/preco_teto/QUALQUER')
    assert rv.status_code == 401
