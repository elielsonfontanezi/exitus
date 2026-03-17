// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Alocação - Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/alocacao');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir gráfico pizza/treemap', async ({ page }) => {
    await page.goto('/dashboard/alocacao');
    await page.waitForTimeout(2000);
    const charts = page.locator('canvas, svg');
    expect(await charts.count()).toBeGreaterThan(0);
  });

  test('deve mostrar índice HHI', async ({ page }) => {
    await page.goto('/dashboard/alocacao');
    const hhi = page.locator('text=/HHI|Herfindahl|Concentração/i');
    expect(await hhi.count()).toBeGreaterThan(0);
  });

  test('deve ter sugestões de rebalanceamento', async ({ page }) => {
    await page.goto('/dashboard/alocacao');
    const sugestoes = page.locator('text=/Rebalance|Sugestões|Recomendações/i');
    expect(await sugestoes.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/alocacao');
    await expect(page.locator('h1')).toBeVisible();
  });
});
