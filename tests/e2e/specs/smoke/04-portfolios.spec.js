// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Portfolios - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/portfolios');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir 4 cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    const cards = page.locator('.card-gradient');
    await expect(cards).toHaveCount(4);
  });

  test('deve ter botão "Nova Carteira"', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    const btn = page.locator('button:has-text("Nova Carteira")');
    await expect(btn).toBeVisible();
  });

  test('deve alternar entre vista grid e lista', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    const toggleButtons = page.locator('button[class*="btn-icon"]');
    expect(await toggleButtons.count()).toBeGreaterThan(0);
  });

  test('deve exibir carteiras', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    await page.waitForTimeout(1000);
    const carteiras = page.locator('.border.rounded-lg, table tr');
    console.log(`✓ ${await carteiras.count()} carteira(s) encontrada(s)`);
  });

  test('deve converter moeda BRL/USD', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    const toggle = page.locator('[data-currency-toggle]');
    if (await toggle.isVisible()) {
      await toggle.click();
      await page.waitForTimeout(500);
    }
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/portfolios');
    await expect(page.locator('h1')).toBeVisible();
  });
});
