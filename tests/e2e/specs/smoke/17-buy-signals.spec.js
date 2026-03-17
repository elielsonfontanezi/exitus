// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Buy Signals - Smoke Tests @smoke @critical', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/buy-signals');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve ter busca de ativo individual', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    const searchInput = page.locator('input[type="search"], input[placeholder*="ticker"]');
    await expect(searchInput.first()).toBeVisible();
  });

  test('deve exibir gráfico radar', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    await page.waitForTimeout(2000);
    const radar = page.locator('canvas');
    expect(await radar.count()).toBeGreaterThan(0);
  });

  test('deve mostrar score de compra', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    const score = page.locator('text=/Score|Pontuação|[0-9]+\\/100/i');
    expect(await score.count()).toBeGreaterThan(0);
  });

  test('deve ter insights da IA', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    const insights = page.locator('text=/Insight|IA|Análise|Recomendação/i');
    expect(await insights.count()).toBeGreaterThan(0);
  });

  test('deve exibir grid de sinais globais', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    const grid = page.locator('.grid, table');
    await expect(grid.first()).toBeVisible();
  });

  test('deve ter filtros compra/aguardar/venda', async ({ page }) => {
    await page.goto('/dashboard/buy-signals');
    const filtros = page.locator('button[class*="filter"], select');
    expect(await filtros.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/buy-signals');
    await expect(page.locator('h1')).toBeVisible();
  });
});
