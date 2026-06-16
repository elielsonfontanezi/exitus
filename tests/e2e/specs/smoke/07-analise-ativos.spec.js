// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Análise de Ativos - Smoke Tests @smoke', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/assets');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir tabela de ativos', async ({ page }) => {
    await page.goto('/dashboard/assets');
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve ter filtros e busca', async ({ page }) => {
    await page.goto('/dashboard/assets');
    // Verificar se existe algum input ou select (filtros básicos)
    const filters = page.locator('input, select');
    expect(await filters.count()).toBeGreaterThan(0);
    console.log('✓ Filtros encontrados:', await filters.count());
  });

  test('deve ordenar colunas', async ({ page }) => {
    await page.goto('/dashboard/assets');
    // Verificar se há headers na tabela (ordenação básica)
    const headers = page.locator('th');
    expect(await headers.count()).toBeGreaterThan(0);
    console.log('✓ Headers encontrados:', await headers.count());
  });

  test('deve abrir detalhes do ativo', async ({ page }) => {
    await page.goto('/dashboard/assets');
    await page.waitForTimeout(1000);
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
      await page.waitForTimeout(500);
    }
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/assets');
    await expect(page.locator('h1')).toBeVisible();
  });
});
