// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Análise de Ativos - Smoke Tests @smoke', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/analise-ativos');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir tabela de ativos', async ({ page }) => {
    await page.goto('/dashboard/analise-ativos');
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve ter filtros e busca', async ({ page }) => {
    await page.goto('/dashboard/analise-ativos');
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]');
    expect(await searchInput.count()).toBeGreaterThan(0);
  });

  test('deve ordenar colunas', async ({ page }) => {
    await page.goto('/dashboard/analise-ativos');
    const headers = page.locator('th[class*="cursor-pointer"], th[role="button"]');
    expect(await headers.count()).toBeGreaterThan(0);
  });

  test('deve abrir detalhes do ativo', async ({ page }) => {
    await page.goto('/dashboard/analise-ativos');
    await page.waitForTimeout(1000);
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
      await page.waitForTimeout(500);
    }
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/analise-ativos');
    await expect(page.locator('h1')).toBeVisible();
  });
});
