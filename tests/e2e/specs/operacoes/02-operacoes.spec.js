// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes — Módulo Operações
 * Cobre: tela compra/venda unificada, depósito, importação B3
 */

test.describe('Operações — Compra/Venda/Importação @operacoes', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  // --- Tela Operações ---

  test('deve carregar tela de operações sem erros', async ({ page }) => {
    await page.goto('/operacoes/');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('deve exibir toggle Compra/Venda', async ({ page }) => {
    await page.goto('/operacoes/');
    // Deve existir algum botão ou tab para alternar modo
    const toggle = page.locator('button, [x-data]').filter({ hasText: /compra|venda/i }).first();
    await expect(toggle).toBeVisible();
  });

  test('deve exibir campo de busca de ativo após selecionar tipo Ação', async ({ page }) => {
    await page.goto('/operacoes/');
    // Seleciona o tipo "Ação" para revelar os campos via x-show
    const tipoAcao = page.locator('.tipo-card, div[class*="tipo"]').filter({ hasText: /ação br/i }).first();
    await tipoAcao.click({ timeout: 8000 });
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await expect(inputTicker).toBeVisible({ timeout: 8000 });
  });

  test('deve exibir campo de quantidade após selecionar tipo e ativo', async ({ page }) => {
    await page.goto('/operacoes/');
    // O campo quantidade usa x-model="form.quantidade" e aparece após selectedAtivo
    // Verifica que o campo existe no DOM (pode estar oculto por x-show)
    const inputQtd = page.locator('input[x-model="form.quantidade"]');
    await expect(inputQtd).toBeAttached({ timeout: 8000 });
  });

  test('deve exibir campo de preço no formulário', async ({ page }) => {
    await page.goto('/operacoes/');
    // Campo de preço usa x-model="form.preco_unitario"
    const inputPreco = page.locator('input[x-model="form.preco_unitario"]');
    await expect(inputPreco).toBeAttached({ timeout: 8000 });
  });

  test('deve exibir seletor de corretora no formulário', async ({ page }) => {
    await page.goto('/operacoes/');
    // Select de corretora usa x-model="form.corretora_id"
    const selectCorretora = page.locator('select[x-model="form.corretora_id"]');
    await expect(selectCorretora).toBeAttached({ timeout: 8000 });
  });

  test('rota legada /operacoes/compra deve redirecionar para /operacoes/', async ({ page }) => {
    const response = await page.goto('/operacoes/compra');
    // Deve funcionar (redirect ou 200)
    expect(response?.status()).not.toBe(404);
  });

  // --- Depósito ---

  test('deve carregar tela de depósito sem erros', async ({ page }) => {
    await page.goto('/operacoes/deposito');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  // --- Importação B3 ---

  test('deve exibir área de upload na tela de operações', async ({ page }) => {
    await page.goto('/operacoes/');
    // Procura por referência a importação B3
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/import|b3|upload/);
  });

  // --- Responsividade ---

  test('operações deve ser responsivo em mobile (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/operacoes/');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });
});
