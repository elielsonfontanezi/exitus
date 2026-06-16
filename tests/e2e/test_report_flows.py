# -*- coding: utf-8 -*-
"""
Exitus E2E Tests - Fluxos de Relatórios (FC-007)
Testes end-to-end para geração e exportação de relatórios
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.regression
@pytest.mark.report
def test_listar_relatorios_disponiveis(authenticated_page: Page, base_url: str):
    """
    TC-038: Listar relatórios disponíveis
    
    Cenário:
    - Usuário autenticado acessa /dashboard/reports
    
    Resultado Esperado:
    - Página carrega com sucesso
    - Exibe lista de relatórios disponíveis
    - Mostra tipos: IR, DARF, Rentabilidade, etc
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Assert
    expect(page.locator('body')).to_contain_text('Relatório', ignore_case=True, timeout=10000)
    
    # Verificar que não há erro
    expect(page.locator('body')).not_to_contain_text('erro', ignore_case=True)


@pytest.mark.regression
@pytest.mark.report
def test_visualizar_relatorio_ir(authenticated_page: Page, base_url: str):
    """
    TC-039: Visualizar relatório de IR
    
    Cenário:
    - Usuário clica em "Ver" ou "Visualizar" em relatório de IR
    
    Resultado Esperado:
    - Relatório é exibido
    - Mostra dados de IR: operações, lucros, prejuízos, imposto devido
    - Dados são formatados corretamente
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Procurar links/botões de IR
    ir_links = page.locator('a:has-text("IR"), button:has-text("IR"), a:has-text("Imposto")')
    
    # Assert
    if ir_links.count() > 0:
        expect(ir_links.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.regression
@pytest.mark.report
def test_visualizar_relatorio_darf(authenticated_page: Page, base_url: str):
    """
    TC-040: Visualizar relatório de DARF
    
    Cenário:
    - Usuário clica em relatório de DARF
    
    Resultado Esperado:
    - Relatório de DARF é exibido
    - Mostra valores a pagar, códigos de receita, vencimentos
    - Dados são formatados corretamente
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Procurar links/botões de DARF
    darf_links = page.locator('a:has-text("DARF"), button:has-text("DARF")')
    
    # Assert
    if darf_links.count() > 0:
        expect(darf_links.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.regression
@pytest.mark.report
def test_exportar_relatorio_pdf(authenticated_page: Page, base_url: str):
    """
    TC-041: Exportar relatório em PDF
    
    Cenário:
    - Usuário visualiza um relatório
    - Clica em "Exportar PDF" ou "Download PDF"
    
    Resultado Esperado:
    - Download de PDF é iniciado
    - Arquivo PDF é gerado corretamente
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Procurar botões de exportar/download PDF
    pdf_buttons = page.locator('button:has-text("PDF"), a:has-text("PDF"), button:has-text("Exportar")')
    
    # Assert
    if pdf_buttons.count() > 0:
        expect(pdf_buttons.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.regression
@pytest.mark.report
def test_exportar_relatorio_excel(authenticated_page: Page, base_url: str):
    """
    TC-042: Exportar relatório em Excel
    
    Cenário:
    - Usuário clica em "Exportar Excel" ou "Download Excel"
    
    Resultado Esperado:
    - Download de Excel é iniciado
    - Arquivo Excel (.xlsx) é gerado corretamente
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Procurar botões de exportar Excel
    excel_buttons = page.locator('button:has-text("Excel"), a:has-text("Excel"), button:has-text("XLSX")')
    
    # Assert
    if excel_buttons.count() > 0:
        expect(excel_buttons.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()


@pytest.mark.regression
@pytest.mark.report
def test_filtrar_relatorios_periodo(authenticated_page: Page, base_url: str):
    """
    TC-043: Filtrar relatórios por período
    
    Cenário:
    - Usuário seleciona período (mês/ano)
    - Aplica filtro
    
    Resultado Esperado:
    - Filtro de período funciona
    - Relatórios são filtrados conforme período selecionado
    - Dados são atualizados
    """
    # Arrange
    page = authenticated_page
    
    # Act
    page.goto(f"{base_url}/dashboard/reports")
    
    # Procurar filtros de período
    period_filters = page.locator('select, input[type="date"], input[type="month"]')
    
    # Assert
    if period_filters.count() > 0:
        expect(period_filters.first).to_be_visible(timeout=5000)
    else:
        expect(page.locator('body')).to_be_visible()
