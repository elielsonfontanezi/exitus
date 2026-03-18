// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Educação - Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/educacao');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir artigos educacionais', async ({ page }) => {
    await page.goto('/dashboard/educacao');
    const artigos = page.locator('.artigo, .card, article');
    expect(await artigos.count()).toBeGreaterThan(0);
  });

  test('deve ter busca de conteúdo', async ({ page }) => {
    await page.goto('/dashboard/educacao');
    const search = page.locator('input[type="search"], input[placeholder*="Buscar"]');
    expect(await search.count()).toBeGreaterThan(0);
  });

  test('deve categorizar conteúdo', async ({ page }) => {
    await page.goto('/dashboard/educacao');
    const categorias = page.locator('button[class*="category"], .tag');
    expect(await categorias.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/educacao');
    await expect(page.locator('h1')).toBeVisible();
  });
});
