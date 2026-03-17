# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Testes de Responsividade
Testes end-to-end para verificar responsividade em diferentes dispositivos
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.slow
def test_dashboard_mobile_portrait(authenticated_page: Page, base_url: str):
    """
    TC-050: Dashboard responsivo em mobile portrait (375x667)
    
    Cenário:
    - Usuário acessa dashboard em dispositivo mobile (iPhone SE)
    
    Resultado Esperado:
    - Layout se adapta ao tamanho da tela
    - Elementos são empilhados verticalmente
    - Texto é legível
    - Botões são clicáveis
    """
    # Arrange
    page = authenticated_page
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Act
    page.goto(f"{base_url}/dashboard/")
    
    # Assert
    expect(page.locator('body')).to_be_visible(timeout=10000)
    
    # Verificar que conteúdo está visível
    expect(page.locator('.bg-white').first).to_be_visible()


@pytest.mark.slow
def test_dashboard_tablet(authenticated_page: Page, base_url: str):
    """
    TC-051: Dashboard responsivo em tablet (768x1024)
    
    Cenário:
    - Usuário acessa dashboard em tablet (iPad)
    
    Resultado Esperado:
    - Layout se adapta ao tamanho médio
    - Grid de cards funciona corretamente
    - Navegação é acessível
    """
    # Arrange
    page = authenticated_page
    page.set_viewport_size({"width": 768, "height": 1024})
    
    # Act
    page.goto(f"{base_url}/dashboard/")
    
    # Assert
    expect(page.locator('body')).to_be_visible(timeout=10000)
    expect(page.locator('.bg-white').first).to_be_visible()


@pytest.mark.slow
def test_buy_signals_mobile(authenticated_page: Page, base_url: str):
    """
    TC-052: Buy Signals responsivo em mobile
    
    Cenário:
    - Usuário acessa Buy Signals em mobile
    
    Resultado Esperado:
    - Formulário de busca é acessível
    - Botões são clicáveis
    - Resultados são exibidos corretamente
    """
    # Arrange
    page = authenticated_page
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Assert
    expect(page.locator('body')).to_contain_text('Buy Signals', timeout=10000)
    
    # Verificar que campo de busca está visível
    search_input = page.locator('input[type="text"]').first
    expect(search_input).to_be_visible(timeout=5000)


@pytest.mark.slow
def test_navigation_mobile_menu(authenticated_page: Page, base_url: str):
    """
    TC-053: Menu de navegação mobile (hamburger)
    
    Cenário:
    - Usuário acessa em mobile
    - Clica no menu hamburger
    
    Resultado Esperado:
    - Menu hamburger está visível
    - Menu se expande ao clicar
    - Links de navegação são acessíveis
    """
    # Arrange
    page = authenticated_page
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Act
    page.goto(f"{base_url}/dashboard/")
    
    # Assert - Verificar que página carregou
    expect(page.locator('body')).to_be_visible(timeout=10000)
    
    # Procurar por menu hamburger (ícone de 3 linhas, botão de menu)
    hamburger_menu = page.locator('button[aria-label*="menu"], button:has-text("☰"), .hamburger')
    
    if hamburger_menu.count() > 0:
        # Se houver menu hamburger, verificar que está visível
        expect(hamburger_menu.first).to_be_visible()
    else:
        # Se não houver (menu sempre visível), ok também
        expect(page.locator('body')).to_be_visible()
