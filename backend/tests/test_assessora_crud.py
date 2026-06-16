# -*- coding: utf-8 -*-
"""
Exitus - Testes CRUD de Assessoras
Valida endpoints de gestão de assessoras (admin only)
"""

import pytest
import uuid
from app.models import Assessora, Usuario
from app.models.usuario import UserRole
from app.database import db


@pytest.fixture
def admin_user(app):
    """Usuário admin para testes"""
    from app.models.usuario import Usuario, UserRole
    
    # Usar UUID para garantir unicidade
    suffix = str(uuid.uuid4())[:8]
    
    # Criar assessora se não existir
    from app.models.assessora import Assessora
    assessora = Assessora.query.filter_by(email=f'admin_{suffix}@teste.com').first()
    if not assessora:
        assessora = Assessora(
            id=uuid.uuid4(),
            nome=f'Assessora Teste Admin {suffix}',
            razao_social=f'Assessora Teste Admin Ltda {suffix}',
            cnpj=f'12{suffix[:12]}91',  # 14 caracteres total
            email=f'admin_{suffix}@teste.com',
            ativo=True
        )
        db.session.add(assessora)
        db.session.commit()
    
    admin = Usuario(
        id=uuid.uuid4(),
        assessora_id=assessora.id,
        username=f'admin_test_{suffix}',
        email=f'admin_test_{suffix}@teste.com',
        role=UserRole.ADMIN,
        ativo=True
    )
    admin.set_password('senha123')
    db.session.add(admin)
    db.session.commit()
    
    # Armazenar IDs para cleanup
    admin_id = admin.id
    assessora_id = assessora.id
    
    yield admin
    
    # Cleanup
    Usuario.query.filter_by(id=admin_id).delete()
    Assessora.query.filter_by(id=assessora_id).delete()
    db.session.commit()


@pytest.fixture
def admin_token(client, admin_user):
    """Token JWT de admin"""
    response = client.post('/api/auth/login', json={
        'username': admin_user.username,
        'password': 'senha123'
    })
    return response.json['data']['access_token']


@pytest.fixture
def assessora_data():
    """Dados válidos para criar assessora"""
    import time
    suffix = str(int(time.time() * 1000000))[-8:]
    return {
        'nome': f'Nova Assessora {suffix}',
        'razao_social': f'Nova Assessora Ltda {suffix}',
        'cnpj': f'99{suffix}0001',
        'email': f'nova_{suffix}@teste.com',
        'telefone': '11999999999',
        'plano': 'profissional',
        'max_usuarios': 50,
        'max_portfolios': 100
    }


class TestAssessoraCRUD:
    """Testes de CRUD de assessoras"""

    def test_list_assessoras_admin(self, client, admin_token):
        """Admin pode listar assessoras"""
        response = client.get(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'data' in response.json
        assert 'items' in response.json['data']

    def test_list_assessoras_sem_auth(self, client):
        """Sem autenticação retorna 401"""
        response = client.get('/api/assessoras')
        assert response.status_code == 401

    def test_create_assessora_admin(self, client, admin_token, assessora_data):
        """Admin pode criar assessora"""
        response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        
        assert response.status_code == 201
        assert response.json['success'] is True
        assert 'data' in response.json
        assert response.json['data']['nome'] == assessora_data['nome']
        assert response.json['data']['cnpj'] == assessora_data['cnpj']

    def test_create_assessora_cnpj_duplicado(self, client, admin_token, assessora_data):
        """Não permite CNPJ duplicado"""
        # Criar primeira
        client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        
        # Tentar criar segunda com mesmo CNPJ
        response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        
        assert response.status_code == 400
        assert 'já cadastrado' in response.json['message'].lower()

    def test_get_assessora_by_id(self, client, admin_token, assessora_data):
        """Admin pode buscar assessora por ID"""
        # Criar assessora
        create_response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        assessora_id = create_response.json['data']['id']
        
        # Buscar por ID
        response = client.get(
            f'/api/assessoras/{assessora_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['data']['id'] == assessora_id

    def test_update_assessora(self, client, admin_token, assessora_data):
        """Admin pode atualizar assessora"""
        # Criar assessora
        create_response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        assessora_id = create_response.json['data']['id']
        
        # Atualizar com nome único
        suffix = str(uuid.uuid4())[:8]
        update_data = {'nome': f'Nome Atualizado {suffix}', 'plano': 'enterprise'}
        response = client.put(
            f'/api/assessoras/{assessora_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=update_data
        )
        
        assert response.status_code == 200
        assert response.json['data']['nome'] == f'Nome Atualizado {suffix}'
        assert response.json['data']['plano'] == 'enterprise'

    def test_delete_assessora_soft(self, client, admin_token, assessora_data):
        """Admin pode fazer soft delete de assessora"""
        # Criar assessora
        create_response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        assessora_id = create_response.json['data']['id']
        
        # Soft delete
        response = client.delete(
            f'/api/assessoras/{assessora_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'desativada' in response.json['message'].lower()

    def test_get_assessora_stats(self, client, admin_token, assessora_data):
        """Admin pode obter métricas da assessora"""
        # Criar assessora
        create_response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        assessora_id = create_response.json['data']['id']
        
        # Obter stats
        response = client.get(
            f'/api/assessoras/{assessora_id}/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'total_usuarios' in response.json['data']
        assert 'total_portfolios' in response.json['data']
        assert 'volume_total' in response.json['data']

    def test_toggle_assessora_ativo(self, client, admin_token, assessora_data):
        """Admin pode ativar/desativar assessora"""
        # Criar assessora
        create_response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=assessora_data
        )
        assessora_id = create_response.json['data']['id']
        
        # Toggle (desativar)
        response = client.post(
            f'/api/assessoras/{assessora_id}/toggle',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['data']['ativo'] is False
        
        # Toggle novamente (ativar)
        response = client.post(
            f'/api/assessoras/{assessora_id}/toggle',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['data']['ativo'] is True

    def test_create_assessora_campos_obrigatorios(self, client, admin_token):
        """Validação de campos obrigatórios"""
        response = client.post(
            '/api/assessoras',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'nome': 'Apenas Nome'}
        )
        
        assert response.status_code == 400
        assert 'inválidos' in response.json['message'].lower()
