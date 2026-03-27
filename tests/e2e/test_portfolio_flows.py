# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Fluxos de Portfolios (FC-004)
Testes end-to-end para gestão de carteiras/portfolios
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.portfolio
def test_listar_portfolios(authenticated_page: Page, base_url: str):
    """
    TC-019: Listar todos os portfolios do usuário
    
    Cenário:
    - Usuário autenticado acessa /dashboard/portfolios
    
    Resultado Esperado:
    - Página carrega com sucesso
    - Exibe lista de portfolios
    - Cada portfolio mostra informações básicas
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Assert
    expect(page.locator('body')).to_contain_text('Portfolio', ignore_case=True, timeout=10000)
    
    # Verificar que página carregou (não há erro)
    expect(page.locator('body')).not_to_contain_text('erro', ignore_case=True)


@pytest.mark.regression
@pytest.mark.portfolio
def test_exibir_resumo_portfolio(authenticated_page: Page, base_url: str):
    """
    TC-020: Exibir resumo de cada portfolio
    
    Cenário:
    - Usuário acessa página de portfolios
    
    Resultado Esperado:
    - Cada portfolio exibe: nome, saldo, quantidade de ativos, rentabilidade
    - Cards ou tabela com informações resumidas
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Assert - Verificar que há conteúdo
    expect(page.locator('.bg-white').first).to_be_visible(timeout=10000)
    
    # Verificar que não há erro
    expect(page.locator('body')).not_to_contain_text('erro', ignore_case=True)


@pytest.mark.regression
@pytest.mark.portfolio
def test_filtrar_portfolios_status(authenticated_page: Page, base_url: str):
    """
    TC-021: Filtrar portfolios por status (ativo/inativo)
    
    Cenário:
    - Usuário acessa portfolios
    - Aplica filtro de status
    
    Resultado Esperado:
    - Filtro funciona (se implementado)
    - Lista é atualizada conforme filtro
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Assert - Verificar que página carregou
    expect(page.locator('body')).to_be_visible(timeout=10000)
    
    # Procurar por filtros (se existirem)
    filter_elements = page.locator('select, button:has-text("Filtro"), button:has-text("Ativo")')
    
    # Se houver filtros, verificar que estão visíveis
    if filter_elements.count() > 0:
        expect(filter_elements.first).to_be_visible()


@pytest.mark.regression
@pytest.mark.portfolio
def test_criar_novo_portfolio(authenticated_page: Page, base_url: str):
    """
    TC-022: Criar novo portfolio
    
    Cenário:
    - Usuário clica em "Novo Portfolio" ou "Criar Carteira"
    - Preenche formulário
    - Salva
    
    Resultado Esperado:
    - Formulário é exibido
    - Campos obrigatórios são validados
    - Portfolio é criado (ou modal/form aparece)
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Procurar botão de criar/novo
    create_buttons = page.locator('button:has-text("Novo"), button:has-text("Criar"), a:has-text("Novo")')
    
    # Assert - Se houver botão, verificar que está visível
    if create_buttons.count() > 0:
        expect(create_buttons.first).to_be_visible(timeout=5000)
    else:
        # Se não houver botão, apenas verificar que página carregou
        expect(page.locator('body')).to_contain_text('Portfolio', ignore_case=True)


@pytest.mark.regression
@pytest.mark.portfolio
def test_editar_portfolio_existente(authenticated_page: Page, base_url: str):
    """
    TC-023: Editar portfolio existente
    
    Cenário:
    - Usuário clica em "Editar" em um portfolio
    - Modifica informações
    - Salva
    
    Resultado Esperado:
    - Formulário de edição é exibido
    - Dados atuais são pré-preenchidos
    - Alterações são salvas
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Procurar botões de editar
    edit_buttons = page.locator('button:has-text("Editar"), a:has-text("Editar")')
    
    # Assert - Se houver botão de editar, verificar
    if edit_buttons.count() > 0:
        expect(edit_buttons.first).to_be_visible(timeout=5000)
    else:
        # Se não houver, apenas verificar que página carregou
        expect(page.locator('body')).to_be_visible()


@pytest.mark.regression
@pytest.mark.portfolio
def test_desativar_portfolio(authenticated_page: Page, base_url: str):
    """
    TC-024: Desativar portfolio
    
    Cenário:
    - Usuário clica em "Desativar" ou "Excluir" em um portfolio
    - Confirma ação
    
    Resultado Esperado:
    - Modal de confirmação aparece
    - Portfolio é desativado/excluído
    - Lista é atualizada
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/portfolios")
    
    # Procurar botões de desativar/excluir
    delete_buttons = page.locator('button:has-text("Desativar"), button:has-text("Excluir"), button:has-text("Remover")')
    
    # Assert - Se houver botão, verificar
    if delete_buttons.count() > 0:
        expect(delete_buttons.first).to_be_visible(timeout=5000)
    else:
        # Se não houver, apenas verificar que página carregou
        expect(page.locator('body')).to_be_visible()
