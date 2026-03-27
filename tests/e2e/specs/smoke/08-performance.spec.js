// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Performance - Smoke Tests @smoke', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/performance');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir cards de métricas', async ({ page }) => {
    await page.goto('/dashboard/performance');
    const cards = page.locator('.card-gradient, .card');
    await expect(cards.first()).toBeVisible();
  });

  test('deve renderizar gráficos Chart.js', async ({ page }) => {
    await page.goto('/dashboard/performance');
    await page.waitForTimeout(2000);
    const charts = page.locator('canvas');
    expect(await charts.count()).toBeGreaterThan(0);
  });

  test('deve ter seletor de período', async ({ page }) => {
    await page.goto('/dashboard/performance');
    const periodSelector = page.locator('select, button[class*="period"]');
    expect(await periodSelector.count()).toBeGreaterThan(0);
  });

  test('deve comparar com benchmark', async ({ page }) => {
    await page.goto('/dashboard/performance');
    const benchmark = page.locator('text=/Benchmark|IBOV|CDI/i');
    expect(await benchmark.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/performance');
    await expect(page.locator('h1')).toBeVisible();
  });
});
