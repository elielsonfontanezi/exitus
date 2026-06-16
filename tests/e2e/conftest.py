# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Configuração e Fixtures Compartilhadas
Playwright + pytest para testes end-to-end do frontend
"""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext, expect


@pytest.fixture(scope="session")
def base_url():
    """URL base do frontend"""
    return "http://localhost:8080"


@pytest.fixture(scope="session")
def api_url():
    """URL base do backend"""
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def test_credentials():
    """Credenciais de teste padrão"""
    return {
        "admin": {"username": "admin", "password": "senha123"},
        "viewer": {"username": "viewer", "password": "senha123"},
        "joao": {"username": "joao.silva", "password": "senha123"}
    }


@pytest.fixture(scope="session")
def test_data():
    """Dados de teste compartilhados"""
    return {
        "tickers": {
            "br": "PETR4",
            "us": "AAPL",
            "intl": "MSFT"
        },
        "portfolio": {
            "nome": "Carteira Teste E2E",
            "descricao": "Portfolio criado por teste automatizado"
        }
    }


@pytest.fixture
def page(page: Page, base_url: str):
    """
    Página Playwright configurada
    - Define timeout padrão
    - Configura viewport
    """
    page.set_default_timeout(10000)  # 10 segundos
    page.set_viewport_size({"width": 1920, "height": 1080})
    return page


@pytest.fixture
def authenticated_page(page: Page, base_url: str, test_credentials: dict):
    """
    Página já autenticada como admin
    
    Uso:
        def test_dashboard(authenticated_page):
            authenticated_page.goto('/dashboard/')
            # Já está logado como admin
    """
    # Fazer login
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', test_credentials["admin"]["username"])
    page.fill('input[name="password"]', test_credentials["admin"]["password"])
    page.click('button[type="submit"]')
    
    # Aguardar redirecionamento para dashboard
    page.wait_for_url(f"{base_url}/dashboard/")
    
    return page


@pytest.fixture
def authenticated_context(context: BrowserContext, base_url: str, test_credentials: dict):
    """
    Contexto de navegador autenticado
    Útil para testes que precisam de múltiplas páginas/tabs
    """
    page = context.new_page()
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', test_credentials["admin"]["username"])
    page.fill('input[name="password"]', test_credentials["admin"]["password"])
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/dashboard/")
    page.close()
    
    return context


def do_login(page: Page, base_url: str, username: str, password: str):
    """
    Helper: Realizar login
    
    Args:
        page: Página Playwright
        base_url: URL base do frontend
        username: Nome de usuário
        password: Senha
    """
    page.goto(f"{base_url}/auth/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')


def do_logout(page: Page):
    """
    Helper: Realizar logout
    
    Args:
        page: Página Playwright
    """
    # Clicar no menu do usuário (navbar)
    page.click('button[aria-label="Menu do usuário"]', timeout=5000)
    # Clicar em logout
    page.click('a[href="/auth/logout"]')


def wait_for_dashboard_load(page: Page):
    """
    Helper: Aguardar carregamento completo do dashboard
    
    Args:
        page: Página Playwright
    """
    # Aguardar título
    expect(page.locator('h1')).to_contain_text('Dashboard', timeout=10000)
    # Aguardar pelo menos um card de estatística
    expect(page.locator('.stat-card').first).to_be_visible(timeout=10000)


def wait_for_api_response(page: Page, url_pattern: str, timeout: int = 10000):
    """
    Helper: Aguardar resposta de API específica
    
    Args:
        page: Página Playwright
        url_pattern: Padrão da URL da API (regex)
        timeout: Timeout em milissegundos
    
    Returns:
        Response object
    """
    with page.expect_response(url_pattern, timeout=timeout) as response_info:
        return response_info.value


def take_screenshot_on_failure(page: Page, request):
    """
    Helper: Tirar screenshot em caso de falha
    
    Uso em teste:
        @pytest.fixture(autouse=True)
        def screenshot_on_failure(page, request):
            yield
            if request.node.rep_call.failed:
                page.screenshot(path=f"screenshots/{request.node.name}.png")
    """
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        screenshot_path = f"screenshots/{request.node.name}.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot salvo: {screenshot_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook do pytest para capturar resultado do teste
    Usado para tirar screenshots em falhas
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
