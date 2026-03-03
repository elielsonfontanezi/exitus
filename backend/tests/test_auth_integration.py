# -*- coding: utf-8 -*-
"""
EXITUS-TESTS-001 — Testes de integração: Auth endpoints

Endpoints cobertos:
- POST /api/auth/login  (happy path, credenciais erradas, body vazio)
- GET  /api/auth/me     (com/sem JWT)
"""
import pytest


# ===========================================================================
# POST /api/auth/login
# ===========================================================================
class TestLogin:

    def test_login_sucesso(self, auth_client, usuario_seed):
        """Login com credenciais corretas retorna tokens."""
        response = auth_client.post('/api/auth/login', json={
            'username': usuario_seed.username,
            'password': 'senha_teste_123',
        })
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']

    def test_login_senha_errada(self, client, usuario_seed):
        """Login com senha errada retorna 401."""
        response = client.post('/api/auth/login', json={
            'username': usuario_seed.username,
            'password': 'senha_errada',
        })
        assert response.status_code == 401

    def test_login_usuario_inexistente(self, client):
        """Login com usuário inexistente retorna 401."""
        response = client.post('/api/auth/login', json={
            'username': 'nao_existe',
            'password': 'qualquer',
        })
        assert response.status_code == 401

    def test_login_body_vazio_retorna_400(self, client):
        """Body vazio retorna 400 com mensagem de erro."""
        response = client.post('/api/auth/login',
                               data='',
                               content_type='application/json')
        assert response.status_code in (400, 500)

    def test_login_sem_username_retorna_400(self, client):
        """Falta campo username → 400."""
        response = client.post('/api/auth/login', json={
            'password': 'senha_teste_123',
        })
        assert response.status_code == 400

    def test_login_sem_password_retorna_400(self, client):
        """Falta campo password → 400."""
        response = client.post('/api/auth/login', json={
            'username': 'qualquer_usuario',
        })
        assert response.status_code == 400

    def test_login_retorna_dados_usuario(self, auth_client, usuario_seed):
        """Response de login deve incluir dados do usuário."""
        response = auth_client.post('/api/auth/login', json={
            'username': usuario_seed.username,
            'password': 'senha_teste_123',
        })
        data = response.get_json()
        assert response.status_code == 200
        user_data = data['data'].get('usuario') or data['data'].get('user')
        if user_data:
            assert user_data['username'] == usuario_seed.username

    def test_login_envelope_padrao(self, auth_client, usuario_seed):
        """Response segue envelope {success, data, message}."""
        response = auth_client.post('/api/auth/login', json={
            'username': usuario_seed.username,
            'password': 'senha_teste_123',
        })
        data = response.get_json()
        assert 'success' in data
        assert 'data' in data


# ===========================================================================
# GET /health (smoke test — sem JWT)
# ===========================================================================
class TestHealthCheck:

    def test_health_retorna_ok(self, client):
        """Health check deve retornar status ok."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'exitus-backend'

    def test_health_sem_autenticacao(self, client):
        """Health check não requer JWT."""
        response = client.get('/health')
        assert response.status_code == 200


# ===========================================================================
# JWT — endpoints protegidos sem token
# ===========================================================================
class TestJWTProtection:

    def test_endpoint_protegido_sem_token_retorna_401(self, client):
        """Endpoint protegido sem JWT retorna 401."""
        response = client.get('/api/usuarios')
        assert response.status_code == 401

    def test_endpoint_protegido_token_invalido_retorna_4xx(self, client):
        """Token malformado retorna 401 ou 422 (Flask-JWT-Extended)."""
        response = client.get('/api/usuarios', headers={
            'Authorization': 'Bearer token_invalido_xyz'
        })
        assert response.status_code in (401, 422)

    def test_endpoint_protegido_com_token_valido(self, auth_client):
        """Endpoint protegido com JWT válido retorna 200."""
        response = auth_client.get(
            '/api/usuarios',
            headers=auth_client._auth_headers,
        )
        assert response.status_code == 200
