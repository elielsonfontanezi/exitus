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

  test('deve exibir campo de busca de ativo', async ({ page }) => {
    await page.goto('/operacoes/');
    const inputTicker = page.locator('input[name="ticker"], input[placeholder*="ticker"], input[placeholder*="ativo"]').first();
    await expect(inputTicker).toBeVisible();
  });

  test('deve exibir campo de quantidade', async ({ page }) => {
    await page.goto('/operacoes/');
    const inputQtd = page.locator('input[name="quantidade"], input[name="quantity"]').first();
    await expect(inputQtd).toBeVisible();
  });

  test('deve exibir campo de preço', async ({ page }) => {
    await page.goto('/operacoes/');
    const inputPreco = page.locator('input[name="preco"], input[name="price"]').first();
    await expect(inputPreco).toBeVisible();
  });

  test('deve exibir seletor de corretora', async ({ page }) => {
    await page.goto('/operacoes/');
    const selectCorretora = page.locator('select[name="corretora_id"], select[name="corretora"]');
    await expect(selectCorretora.first()).toBeVisible();
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
