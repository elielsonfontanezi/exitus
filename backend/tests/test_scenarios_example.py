# -*- coding: utf-8 -*-
"""
Teste exemplo demonstrando uso de cenários de teste
Este arquivo serve como referência para usar os novos cenários
"""

import pytest
from decimal import Decimal


class TestScenariosUsage:
    """Exemplos de uso dos cenários de teste"""
    
    @pytest.mark.parametrize("scenario", ["test_e2e", "test_ir", "test_stress"])
    def test_scenario_loading(self, app, load_scenario, scenario):
        """Testa se cenários carregam corretamente"""
        with app.app_context():
            from app.models.usuario import Usuario
            from app.models.ativo import Ativo
            from app.models.transacao import Transacao
            
            # Verificar dados foram carregados
            assert Usuario.query.count() > 0, f"Nenhum usuário no cenário {scenario}"
            assert Ativo.query.count() > 0, f"Nenhum ativo no cenário {scenario}"
            
            # Cenários específicos devem ter transações
            if scenario in ["test_e2e", "test_ir", "test_stress"]:
                assert Transacao.query.count() > 0, f"Nenhuma transação no cenário {scenario}"
            
            print(f"✅ Cenário {scenario} carregado:")
            print(f"   Usuários: {Usuario.query.count()}")
            print(f"   Ativos: {Ativo.query.count()}")
            print(f"   Transações: {Transacao.query.count()}")
    
    def test_e2e_scenario_data(self, app, load_scenario):
        """Testa dados específicos do cenário E2E"""
        with app.app_context():
            from app.models.usuario import Usuario
            from app.models.ativo import Ativo
            
            # Verificar usuários específicos do cenário E2E
            admin = Usuario.query.filter_by(username='e2e_admin').first()
            user = Usuario.query.filter_by(username='e2e_user').first()
            
            assert admin is not None, "Usuário e2e_admin não encontrado"
            assert user is not None, "Usuário e2e_user não encontrado"
            assert admin.role.value == 'ADMIN', "Role do admin incorreto"
            
            # Verificar ativos específicos
            petr4 = Ativo.query.filter_by(ticker='PETR4').first()
            aapl = Ativo.query.filter_by(ticker='AAPL').first()
            
            assert petr4 is not None, "PETR4 não encontrado"
            assert aapl is not None, "AAPL não encontrado"
            assert petr4.mercado == 'BR', "Mercado do PETR4 incorreto"
            assert aapl.mercado == 'US', "Mercado do AAPL incorreto"
    
    def test_ir_scenario_calculations(self, app, load_scenario):
        """Testa cálculos de IR com cenário específico"""
        with app.app_context():
            from app.models.usuario import Usuario
            from app.models.ativo import Ativo
            from app.models.transacao import Transacao, TipoTransacao
            
            # Buscar dados do cenário IR
            usuario = Usuario.query.filter_by(username='ir_test_user').first()
            ativo = Ativo.query.filter_by(ticker='IRACAO1').first()
            
            assert usuario is not None, "Usuário ir_test_user não encontrado"
            assert ativo is not None, "Ativo IRACAO1 não encontrado"
            
            # Verificar transações do cenário
            transacoes = Transacao.query.filter_by(
                usuario_id=usuario.id,
                ativo_id=ativo.id
            ).order_by(Transacao.data_transacao).all()
            
            assert len(transacoes) >= 3, "Cenário IR deve ter pelo menos 3 transações"
            
            # Verificar sequência: Compra, Compra, Venda
            assert transacoes[0].tipo == TipoTransacao.COMPRA
            assert transacoes[1].tipo == TipoTransacao.COMPRA
            assert transacoes[2].tipo == TipoTransacao.VENDA
            
            # Calcular preço médio manualmente
            total_compras = sum(t.quantidade * t.preco_unitario for t in transacoes[:2])
            total_quantidade = sum(t.quantidade for t in transacoes[:2])
            preco_medio = total_compras / total_quantidade
            
            print(f"✅ Cálculo IR - Cenário test_ir:")
            print(f"   Compras: {total_quantidade} ações")
            print(f"   Custo total: R$ {total_compras:.2f}")
            print(f"   Preço médio: R$ {preco_medio:.4f}")
    
    def test_stress_scenario_volume(self, app, load_scenario):
        """Testa volume de dados do cenário stress"""
        with app.app_context():
            from app.models.usuario import Usuario
            from app.models.ativo import Ativo
            from app.models.transacao import Transacao
            
            # Verificar volume de dados
            usuarios = Usuario.query.all()
            ativos = Ativo.query.all()
            transacoes = Transacao.query.all()
            
            assert len(usuarios) >= 5, f"Cenário stress deve ter >=5 usuários, tem {len(usuarios)}"
            assert len(ativos) >= 5, f"Cenário stress deve ter >=5 ativos, tem {len(ativos)}"
            assert len(transacoes) >= 10, f"Cenário stress deve ter >=10 transações, tem {len(transacoes)}"
            
            # Verificar usuários com prefixo stress_user_
            stress_users = [u for u in usuarios if u.username.startswith('stress_user_')]
            assert len(stress_users) >= 5, f"Deve ter >=5 stress_users, tem {len(stress_users)}"
            
            print(f"✅ Volume stress test:")
            print(f"   Usuários: {len(usuarios)}")
            print(f"   Ativos: {len(ativos)}")
            print(f"   Transações: {len(transacoes)}")
            print(f"   Stress users: {len(stress_users)}")
    
    def test_scenario_isolation(self, app, load_scenario):
        """Testa isolamento entre cenários"""
        with app.app_context():
            from app.models.usuario import Usuario
            
            # Carregar cenário E2E
            # (pytest vai chamar esta função com cada scenario do parametrize)
            
            # Verificar que só existem usuários do cenário atual
            usuarios = Usuario.query.all()
            usernames = [u.username for u in usuarios]
            
            # Não deve ter usuários de outros cenários
            outros_cenarios = ['admin', 'joao.silva', 'viewer']  # do minimal.json
            for username in outros_cenarios:
                assert username not in usernames, f"Usuário {username} de outro cenário encontrado"
            
            print(f"✅ Isolamento OK: {len(usuarios)} usuários únicos do cenário")
    
    @pytest.mark.parametrize("scenario", ["test_e2e"])
    def test_scenario_with_auth(self, app, load_scenario, scenario):
        """Teste usando cenário com autenticação"""
        with app.app_context():
            from app.models.usuario import Usuario
            
            # Buscar usuário do cenário
            usuario = Usuario.query.filter_by(username='e2e_admin').first()
            assert usuario is not None, "Usuário e2e_admin não encontrado"
            
            # Criar cliente de teste autenticado
            client = app.test_client()
            
            # Fazer login
            response = client.post('/api/auth/login', json={
                'username': 'e2e_admin',
                'password': 'e2e_senha_123'
            })
            
            assert response.status_code == 200, "Login falhou"
            token = response.get_json()['data']['access_token']
            
            # Usar token em requisições
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/ativos', headers=headers)
            
            assert response.status_code == 200, "API de ativos falhou"
            data = response.get_json()
            
            # Verificar que retornou ativos do cenário
            assert data['success'] is True
            assert len(data['data']['ativos']) > 0, "Nenhum ativo retornado"
            
            print(f"✅ Teste com autenticação - {len(data['data']['ativos'])} ativos")


# Exemplo de como executar:
# pytest backend/tests/test_scenarios_example.py -v
# pytest backend/tests/test_scenarios_example.py::TestScenariosUsage::test_ir_scenario_calculations -v
