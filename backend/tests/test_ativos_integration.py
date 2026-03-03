# -*- coding: utf-8 -*-
"""
EXITUS-TESTS-001 — Testes de integração: Ativos endpoints

Endpoints cobertos:
- GET  /api/ativos/          (listagem, filtros)
- GET  /api/ativos/{id}      (por ID)
- GET  /api/ativos/ticker/{ticker}  (por ticker)
- POST /api/ativos/          (criação — admin only)
- PUT  /api/ativos/{id}      (atualização — admin only)
- DELETE /api/ativos/{id}    (remoção — admin only)
"""
import uuid as _uuid
import pytest
from decimal import Decimal


def _unique_ticker(prefix='TST'):
    """Gera ticker único por execução (máx 10 chars, sem underscore)."""
    suffix = str(_uuid.uuid4().int)[:4]
    return f'{prefix}{suffix}'


def _get_ativos(data):
    """Extrai lista de ativos do envelope de resposta da API."""
    inner = data.get('data', {})
    if isinstance(inner, list):
        return inner
    if isinstance(inner, dict):
        return inner.get('ativos', [])
    return data.get('ativos', [])


# ===========================================================================
# GET /api/ativos/ — listagem
# ===========================================================================
class TestListarAtivos:

    def test_listar_sem_auth_retorna_401(self, client):
        response = client.get('/api/ativos/')
        assert response.status_code == 401

    def test_listar_com_auth_retorna_200(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/',
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(_get_ativos(data), list)

    def test_listar_inclui_ativo_criado(self, auth_client):
        """Ativo criado via API aparece na listagem."""
        ticker = _unique_ticker('LST')
        r = auth_client.post(
            '/api/ativos/',
            json={'ticker': ticker, 'nome': 'Ativo Lista Teste', 'tipo': 'acao',
                  'classe': 'renda_variavel', 'mercado': 'BR', 'moeda': 'BRL'},
            headers=auth_client._auth_headers,
        )
        assert r.status_code in (200, 201)
        response = auth_client.get('/api/ativos/', headers=auth_client._auth_headers)
        data = response.get_json()
        tickers = [a['ticker'] for a in _get_ativos(data)]
        assert ticker in tickers

    def test_listar_filtro_mercado_br(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/?mercado=BR',
            headers=auth_client._auth_headers,
        )
        data = response.get_json()
        assert response.status_code == 200
        for ativo in _get_ativos(data):
            assert ativo['mercado'] == 'BR'

    def test_listar_envelope_padrao(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/',
            headers=auth_client._auth_headers,
        )
        data = response.get_json()
        assert 'success' in data
        assert 'data' in data
        assert isinstance(_get_ativos(data), list)


# ===========================================================================
# GET /api/ativos/ticker/{ticker} — por ticker
# ===========================================================================
class TestGetAtivoPorTicker:

    def test_ticker_existente_retorna_200(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/ticker/PETR4',
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['ticker'] == 'PETR4'

    def test_ticker_inexistente_retorna_404(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/ticker/XXXXXX',
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 404

    def test_ticker_retorna_dados_fundamentalistas(self, auth_client, ativo_seed):
        response = auth_client.get(
            '/api/ativos/ticker/PETR4',
            headers=auth_client._auth_headers,
        )
        data = response.get_json()['data']
        assert data['preco_atual'] is not None
        assert float(data['preco_atual']) == pytest.approx(38.50, rel=1e-2)


# ===========================================================================
# POST /api/ativos/ — criação (admin)
# ===========================================================================
class TestCriarAtivo:

    def test_criar_ativo_sem_auth_retorna_401(self, client):
        response = client.post('/api/ativos/', json={
            'ticker': 'VALE3',
            'nome': 'Vale ON',
            'tipo': 'acao',
            'classe': 'renda_variavel',
            'mercado': 'BR',
            'moeda': 'BRL',
        })
        assert response.status_code == 401

    def test_criar_ativo_campos_obrigatorios(self, auth_client):
        ticker = _unique_ticker('VL')
        response = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': 'Vale ON Teste',
                'tipo': 'acao',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
            },
            headers=auth_client._auth_headers,
        )
        assert response.status_code in (200, 201)
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['ticker'] == ticker

    def test_criar_ativo_ticker_duplicado_retorna_erro(self, auth_client):
        """Criar ativo com ticker duplicado retorna erro."""
        ticker = _unique_ticker('DUP')
        payload = {'ticker': ticker, 'nome': 'Ativo Dup', 'tipo': 'acao',
                   'classe': 'renda_variavel', 'mercado': 'BR', 'moeda': 'BRL'}
        r1 = auth_client.post('/api/ativos/', json=payload, headers=auth_client._auth_headers)
        assert r1.status_code in (200, 201)
        r2 = auth_client.post('/api/ativos/', json=payload, headers=auth_client._auth_headers)
        assert r2.status_code in (400, 409, 422)

    def test_criar_ativo_campos_faltando_retorna_400(self, auth_client):
        response = auth_client.post(
            '/api/ativos/',
            json={'ticker': 'INCOMPLETO'},
            headers=auth_client._auth_headers,
        )
        assert response.status_code in (400, 422)

    def test_criar_ativo_com_fundamentalistas(self, auth_client):
        ticker = _unique_ticker('IT')
        response = auth_client.post(
            '/api/ativos/',
            json={
                'ticker': ticker,
                'nome': 'Itau Unibanco Teste',
                'tipo': 'acao',
                'classe': 'renda_variavel',
                'mercado': 'BR',
                'moeda': 'BRL',
                'preco_atual': 35.20,
                'dividend_yield': 8.5,
                'p_l': 8.1,
                'p_vp': 1.9,
            },
            headers=auth_client._auth_headers,
        )
        assert response.status_code in (200, 201)
        data = response.get_json()['data']
        assert float(data['preco_atual']) == pytest.approx(35.20, rel=1e-2)


# ===========================================================================
# PUT /api/ativos/{id} — atualização (admin)
# ===========================================================================
class TestAtualizarAtivo:

    def test_atualizar_preco_ativo(self, auth_client, ativo_seed):
        ativo_id = str(ativo_seed.id)
        response = auth_client.put(
            f'/api/ativos/{ativo_id}',
            json={'preco_atual': 40.00},
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert float(data['data']['preco_atual']) == pytest.approx(40.00, rel=1e-2)

    def test_atualizar_ativo_inexistente_retorna_4xx(self, auth_client):
        import uuid
        response = auth_client.put(
            f'/api/ativos/{uuid.uuid4()}',
            json={'preco_atual': 40.00},
            headers=auth_client._auth_headers,
        )
        assert response.status_code in (400, 404)

    def test_atualizar_sem_auth_retorna_401(self, client, ativo_seed):
        ativo_id = str(ativo_seed.id)
        response = client.put(
            f'/api/ativos/{ativo_id}',
            json={'preco_atual': 40.00},
        )
        assert response.status_code == 401


# ===========================================================================
# DELETE /api/ativos/{id} — remoção (admin)
# ===========================================================================
class TestDeletarAtivo:

    def test_deletar_sem_auth_retorna_401(self, client, ativo_seed):
        ativo_id = str(ativo_seed.id)
        response = client.delete(f'/api/ativos/{ativo_id}')
        assert response.status_code == 401

    def test_deletar_ativo_existente(self, auth_client, ativo_seed):
        ativo_id = str(ativo_seed.id)
        response = auth_client.delete(
            f'/api/ativos/{ativo_id}',
            headers=auth_client._auth_headers,
        )
        assert response.status_code in (200, 204)

    def test_deletar_ativo_inexistente_retorna_404(self, auth_client):
        import uuid
        response = auth_client.delete(
            f'/api/ativos/{uuid.uuid4()}',
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 404
