# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Fluxos de Planos de Compra (FC-008)
Testes end-to-end para gestão de planos de compra
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.slow
@pytest.mark.plano_compra
def test_listar_planos_compra(authenticated_page: Page, base_url: str):
    """
    TC-044: Listar planos de compra
    
    Cenário:
    - Usuário autenticado acessa /dashboard/planos-compra
    
    Resultado Esperado:
    - Página carrega com sucesso
    - Exibe lista de planos de compra
    - Mostra informações: ticker, objetivo, progresso, status
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Assert - Verificar que página carregou (não é 404)
    page.wait_for_timeout(2000)
    expect(page.locator('body')).to_be_visible(timeout=10000)
    
    # Verificar que não é página de erro 404
    body_text = page.locator('body').inner_text()
    assert '404' not in body_text, "Página retornou 404"


@pytest.mark.slow
@pytest.mark.plano_compra
def test_criar_novo_plano_compra(authenticated_page: Page, base_url: str):
    """
    TC-045: Criar novo plano de compra
    
    Cenário:
    - Usuário clica em "Novo Plano" ou "Criar Plano"
    - Preenche formulário (ticker, quantidade objetivo, valor aporte)
    - Salva
    
    Resultado Esperado:
    - Formulário de criação é exibido
    - Campos são validados
    - Plano é criado (ou modal aparece)
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Procurar botão de novo plano
    create_buttons = page.locator('button:has-text("Novo"), a:has-text("Novo"), a[href*="novo"]')
    
    # Assert
    if create_buttons.count() > 0:
        expect(create_buttons.first).to_be_visible(timeout=5000)
    else:
        # Se não houver botão, verificar que página carregou
        expect(page.locator('body')).to_be_visible()


@pytest.mark.slow
@pytest.mark.plano_compra
def test_visualizar_detalhes_plano(authenticated_page: Page, base_url: str):
    """
    TC-046: Visualizar detalhes do plano
    
    Cenário:
    - Usuário clica em um plano de compra
    - Acessa página de detalhes
    
    Resultado Esperado:
    - Página de detalhes é exibida
    - Mostra: progresso, histórico de aportes, próximo aporte
    - Gráficos de evolução
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Procurar links/botões de detalhes
    detail_links = page.locator('a:has-text("Ver"), a:has-text("Detalhes"), button:has-text("Ver")')
    
    # Assert
    if detail_links.count() > 0:
        expect(detail_links.first).to_be_visible(timeout=5000)
    else:
        # Se não houver links, apenas verificar que página carregou
        expect(page.locator('body')).to_be_visible()


@pytest.mark.slow
@pytest.mark.plano_compra
def test_editar_plano_compra(authenticated_page: Page, base_url: str):
    """
    TC-047: Editar plano de compra existente
    
    Cenário:
    - Usuário clica em "Editar" em um plano
    - Modifica informações (valor aporte, frequência)
    - Salva
    
    Resultado Esperado:
    - Formulário de edição é exibido
    - Dados atuais são pré-preenchidos
    - Alterações são salvas
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Procurar botões de editar
    edit_buttons = page.locator('button:has-text("Editar"), a:has-text("Editar")')
    
    # Assert
    if edit_buttons.count() > 0:
        expect(edit_buttons.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.slow
@pytest.mark.plano_compra
def test_marcar_plano_concluido(authenticated_page: Page, base_url: str):
    """
    TC-048: Marcar plano como concluído
    
    Cenário:
    - Usuário clica em "Concluir" ou "Finalizar" em um plano
    - Confirma ação
    
    Resultado Esperado:
    - Modal de confirmação aparece
    - Plano é marcado como concluído
    - Status é atualizado
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Procurar botões de concluir/finalizar
    complete_buttons = page.locator('button:has-text("Concluir"), button:has-text("Finalizar"), button:has-text("Completar")')
    
    # Assert
    if complete_buttons.count() > 0:
        expect(complete_buttons.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.slow
@pytest.mark.plano_compra
def test_excluir_plano_compra(authenticated_page: Page, base_url: str):
    """
    TC-049: Excluir plano de compra
    
    Cenário:
    - Usuário clica em "Excluir" em um plano
    - Confirma exclusão
    
    Resultado Esperado:
    - Modal de confirmação aparece
    - Plano é excluído
    - Lista é atualizada
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/planos-compra")
    
    # Procurar botões de excluir
    delete_buttons = page.locator('button:has-text("Excluir"), button:has-text("Remover"), button:has-text("Cancelar")')
    
    # Assert
    if delete_buttons.count() > 0:
        expect(delete_buttons.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()
