# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Fluxos de Autenticação (FC-001)
Testes end-to-end para login, logout e controle de acesso
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.auth
def test_login_credenciais_validas(page: Page, base_url: str, test_credentials: dict):
    """
    TC-001: Login com credenciais válidas
    
    Cenário:
    - Usuário acessa página de login
    - Preenche username e password corretos
    - Clica em "Entrar"
    
    Resultado Esperado:
    - Redirecionado para /dashboard/
    - Dashboard carrega com sucesso
    - Navbar exibe nome do usuário
    """
    # Arrange
    creds = test_credentials["admin"]
    
    # Act
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', creds["username"])
    page.fill('input[name="password"]', creds["password"])
    page.click('button[type="submit"]')
    
    # Assert
    expect(page).to_have_url(f"{base_url}/dashboard/", timeout=10000)
    
    # Verificar que dashboard carregou
    expect(page.locator('body')).to_contain_text('Buy Signals', timeout=10000)
    
    # Verificar que há cards visíveis (sinal de que carregou)
    expect(page.locator('.bg-white').first).to_be_visible(timeout=10000)


@pytest.mark.smoke
@pytest.mark.auth
def test_login_credenciais_invalidas(page: Page, base_url: str):
    """
    TC-002: Login com credenciais inválidas
    
    Cenário:
    - Usuário acessa página de login
    - Preenche username e password incorretos
    - Clica em "Entrar"
    
    Resultado Esperado:
    - Permanece na página de login
    - Exibe mensagem de erro
    - Não redireciona para dashboard
    """
    # Arrange
    invalid_creds = {"username": "usuario_invalido", "password": "senha_errada"}
    
    # Act
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', invalid_creds["username"])
    page.fill('input[name="password"]', invalid_creds["password"])
    page.click('button[type="submit"]')
    
    # Assert
    # Deve permanecer na página de login
    expect(page).to_have_url(f"{base_url}/auth/login", timeout=5000)
    
    # Deve exibir mensagem de erro
    # Nota: Ajustar seletor conforme implementação (flash message, alert, etc)
    expect(page.locator('body')).to_contain_text('Login falhou', timeout=5000)


@pytest.mark.smoke
@pytest.mark.auth
def test_redirect_dashboard_apos_login(page: Page, base_url: str, test_credentials: dict):
    """
    TC-003: Redirecionamento para dashboard após login bem-sucedido
    
    Cenário:
    - Usuário faz login com sucesso
    
    Resultado Esperado:
    - Redirecionado automaticamente para /dashboard/
    - Dashboard carrega completamente
    - Cards de estatísticas são exibidos
    """
    # Arrange
    creds = test_credentials["admin"]
    
    # Act
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', creds["username"])
    page.fill('input[name="password"]', creds["password"])
    page.click('button[type="submit"]')
    
    # Assert
    # Aguardar redirecionamento
    page.wait_for_url(f"{base_url}/dashboard/", timeout=10000)
    
    # Verificar que dashboard carregou
    expect(page.locator('body')).to_contain_text('Buy Signals', timeout=10000)
    
    # Verificar que pelo menos um card está visível
    expect(page.locator('.bg-white').first).to_be_visible(timeout=10000)


@pytest.mark.smoke
@pytest.mark.auth
def test_acesso_rota_protegida_sem_login(page: Page, base_url: str):
    """
    TC-004: Acesso a rota protegida sem autenticação
    
    Cenário:
    - Usuário tenta acessar /dashboard/ diretamente sem estar logado
    
    Resultado Esperado:
    - Redirecionado para /auth/login
    - Não consegue acessar dashboard
    """
    # Act
    page.goto(f"{base_url}/dashboard/")
    
    # Assert
    # Deve ser redirecionado para login
    expect(page).to_have_url(f"{base_url}/auth/login", timeout=5000)
    
    # Deve exibir formulário de login
    expect(page.locator('input[name="username"]')).to_be_visible()
    expect(page.locator('input[name="password"]')).to_be_visible()


@pytest.mark.auth
def test_logout_limpa_sessao(page: Page, base_url: str, test_credentials: dict):
    """
    TC-005: Logout limpa sessão corretamente
    
    Cenário:
    - Usuário faz login
    - Usuário faz logout
    - Usuário tenta acessar dashboard novamente
    
    Resultado Esperado:
    - Após logout, redirecionado para /auth/login
    - Sessão é limpa
    - Não consegue acessar dashboard sem novo login
    """
    # Arrange - Fazer login primeiro
    creds = test_credentials["admin"]
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', creds["username"])
    page.fill('input[name="password"]', creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/dashboard/")
    
    # Act - Fazer logout
    # Nota: Ajustar seletor conforme implementação real do logout
    # Pode ser um link na navbar, dropdown, etc.
    page.goto(f"{base_url}/auth/logout")
    
    # Assert - Verificar redirecionamento para login
    expect(page).to_have_url(f"{base_url}/auth/login", timeout=5000)
    
    # Tentar acessar dashboard novamente (deve redirecionar para login)
    page.goto(f"{base_url}/dashboard/")
    expect(page).to_have_url(f"{base_url}/auth/login", timeout=5000)


@pytest.mark.auth
def test_persistencia_sessao_refresh(page: Page, base_url: str, test_credentials: dict):
    """
    TC-006: Persistência de sessão após refresh da página
    
    Cenário:
    - Usuário faz login
    - Usuário dá refresh na página (F5)
    
    Resultado Esperado:
    - Sessão persiste após refresh
    - Usuário permanece logado
    - Dashboard continua acessível
    """
    # Arrange - Fazer login
    creds = test_credentials["admin"]
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', creds["username"])
    page.fill('input[name="password"]', creds["password"])
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/dashboard/")
    
    # Act - Dar refresh na página
    page.reload()
    
    # Assert - Deve permanecer no dashboard
    expect(page).to_have_url(f"{base_url}/dashboard/", timeout=5000)
    expect(page.locator('h1')).to_contain_text('Dashboard')
    
    # Verificar que ainda está logado
    expect(page.locator('body')).to_contain_text(creds["username"])
