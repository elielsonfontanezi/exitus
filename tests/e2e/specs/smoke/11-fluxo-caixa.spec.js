// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Fluxo de Caixa - Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/fluxo-caixa');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir timeline de movimentações', async ({ page }) => {
    await page.goto('/dashboard/fluxo-caixa');
    const timeline = page.locator('[class*="timeline"], .movimentacao');
    expect(await timeline.count()).toBeGreaterThan(0);
  });

  test('deve mostrar gráfico de evolução', async ({ page }) => {
    await page.goto('/dashboard/fluxo-caixa');
    await page.waitForTimeout(2000);
    const charts = page.locator('canvas');
    expect(await charts.count()).toBeGreaterThan(0);
  });

  test('deve ter filtros por período', async ({ page }) => {
    await page.goto('/dashboard/fluxo-caixa');
    const filtros = page.locator('select, input[type="date"]');
    expect(await filtros.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/fluxo-caixa');
    await expect(page.locator('h1')).toBeVisible();
  });
});
