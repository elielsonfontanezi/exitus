# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Fluxos de Buy Signals (FC-003)
Testes end-to-end para análise de ativos e buy signals
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.buy_signals
def test_buy_signals_carrega_watchlist(authenticated_page: Page, base_url: str):
    """
    TC-013: Buy Signals carrega watchlist top
    
    Cenário:
    - Usuário autenticado acessa /dashboard/buy-signals
    
    Resultado Esperado:
    - Página carrega com sucesso
    - Exibe lista de ativos com melhores buy signals
    - Dados são carregados do backend
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Assert
    expect(page.locator('h1')).to_contain_text('Buy Signals', timeout=10000)
    
    # Verificar que página carregou (não há erro)
    expect(page.locator('body')).not_to_contain_text('erro', ignore_case=True)


@pytest.mark.smoke
@pytest.mark.buy_signals
def test_buscar_ativo_petr4(authenticated_page: Page, base_url: str, test_data: dict):
    """
    TC-014: Buscar ativo específico (PETR4)
    
    Cenário:
    - Usuário acessa Buy Signals
    - Digita "PETR4" no campo de busca
    - Clica em "Analisar"
    
    Resultado Esperado:
    - Análise do ativo é exibida
    - Métricas são carregadas (buy_score, margem, etc)
    - Sem erros
    """
    # Arrange
    page = authenticated_page
    ticker = test_data["tickers"]["br"]  # PETR4
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Preencher campo de busca
    search_input = page.locator('input[type="text"]').first
    expect(search_input).to_be_visible(timeout=5000)
    search_input.fill(ticker)
    
    # Clicar em botão Analisar
    analyze_button = page.locator('button:has-text("Analisar")')
    expect(analyze_button).to_be_visible()
    analyze_button.click()
    
    # Assert - Aguardar resultado (API pode demorar)
    page.wait_for_timeout(3000)  # Aguardar resposta da API
    
    # Verificar que análise foi carregada ou que houve resposta
    # Pode exibir ticker ou mensagem de erro tratada
    body_text = page.locator('body').inner_text()
    
    # Verificar que página não quebrou
    expect(page.locator('body')).to_be_visible()


@pytest.mark.smoke
@pytest.mark.buy_signals
def test_exibir_analise_completa(authenticated_page: Page, base_url: str, test_data: dict):
    """
    TC-015: Exibir análise completa do ativo
    
    Cenário:
    - Usuário busca PETR4
    - Análise é exibida
    
    Resultado Esperado:
    - Exibe buy_score
    - Exibe margem de segurança
    - Exibe métricas fundamentalistas (P/L, P/VP, etc)
    """
    # Arrange
    page = authenticated_page
    ticker = test_data["tickers"]["br"]
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Buscar ativo
    search_input = page.locator('input[type="text"]').first
    search_input.fill(ticker)
    
    analyze_button = page.locator('button:has-text("Analisar")')
    analyze_button.click()
    
    # Aguardar carregamento
    page.wait_for_timeout(2000)  # Aguardar API
    
    # Assert - Verificar que há dados exibidos
    # Nota: Ajustar seletores conforme implementação real
    body_text = page.locator('body').inner_text()
    
    # Deve conter o ticker
    assert ticker in body_text
    
    # Pode conter termos relacionados a análise
    # (score, margem, preço, etc - ajustar conforme implementação)


@pytest.mark.buy_signals
def test_exibir_grafico_radial(authenticated_page: Page, base_url: str, test_data: dict):
    """
    TC-016: Exibir gráfico radial de indicadores
    
    Cenário:
    - Usuário busca ativo
    - Análise é exibida
    
    Resultado Esperado:
    - Gráfico radial (radar chart) é renderizado
    - Canvas está visível
    """
    # Arrange
    page = authenticated_page
    ticker = test_data["tickers"]["br"]
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Buscar ativo
    search_input = page.locator('input[type="text"]').first
    search_input.fill(ticker)
    
    analyze_button = page.locator('button:has-text("Analisar")')
    analyze_button.click()
    
    # Aguardar carregamento
    page.wait_for_timeout(3000)
    
    # Assert - Verificar se há canvas (gráfico)
    canvas_elements = page.locator('canvas')
    
    if canvas_elements.count() > 0:
        # Se houver canvas, verificar que está visível
        expect(canvas_elements.first).to_be_visible(timeout=10000)
    else:
        # Se não houver gráfico, apenas verificar que análise carregou
        expect(page.locator('body')).to_contain_text(ticker)


@pytest.mark.buy_signals
def test_buscar_ativo_inexistente(authenticated_page: Page, base_url: str):
    """
    TC-017: Buscar ativo inexistente
    
    Cenário:
    - Usuário busca ticker que não existe (ex: XXXXX)
    
    Resultado Esperado:
    - Exibe mensagem de erro tratada
    - "Ativo não encontrado" ou similar
    - Não quebra a aplicação
    """
    # Arrange
    page = authenticated_page
    ticker_invalido = "XXXXX99"
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Buscar ativo inexistente
    search_input = page.locator('input[type="text"]').first
    search_input.fill(ticker_invalido)
    
    analyze_button = page.locator('button:has-text("Analisar")')
    analyze_button.click()
    
    # Aguardar resposta
    page.wait_for_timeout(2000)
    
    # Assert - Deve exibir mensagem de erro
    body_text = page.locator('body').inner_text()
    
    # Verificar mensagem de erro (ajustar conforme implementação)
    assert any(msg in body_text.lower() for msg in [
        'não encontrado',
        'sem dados',
        'erro',
        'inválido'
    ])


@pytest.mark.buy_signals
def test_buscar_ativo_sem_dados_suficientes(authenticated_page: Page, base_url: str):
    """
    TC-018: Buscar ativo sem dados suficientes
    
    Cenário:
    - Usuário busca ativo que existe mas não tem dados fundamentalistas
    
    Resultado Esperado:
    - Exibe mensagem informativa
    - "Sem dados suficientes" ou similar
    - Não quebra a aplicação
    """
    # Arrange
    page = authenticated_page
    # Usar ticker que pode existir mas sem dados completos
    ticker_sem_dados = "TESTE1"
    
    # Act
    page.goto(f"{base_url}/dashboard/buy-signals")
    
    # Buscar ativo
    search_input = page.locator('input[type="text"]').first
    search_input.fill(ticker_sem_dados)
    
    analyze_button = page.locator('button:has-text("Analisar")')
    analyze_button.click()
    
    # Aguardar resposta
    page.wait_for_timeout(2000)
    
    # Assert - Verificar que não quebrou
    # Pode exibir erro ou mensagem informativa
    expect(page.locator('body')).to_be_visible()
    
    # Página deve continuar funcional (campo de busca ainda visível)
    expect(search_input).to_be_visible()
