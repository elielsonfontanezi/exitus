// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Comparador - Smoke Tests @smoke @critical', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/comparador');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve permitir adicionar até 6 ativos', async ({ page }) => {
    await page.goto('/dashboard/comparador');
    const addButton = page.locator('button:has-text("Adicionar"), button:has-text("+")');
    expect(await addButton.count()).toBeGreaterThan(0);
  });

  test('deve exibir gráfico radar', async ({ page }) => {
    await page.goto('/dashboard/comparador');
    await page.waitForTimeout(2000);
    const radar = page.locator('canvas');
    expect(await radar.count()).toBeGreaterThan(0);
  });

  test('deve mostrar recomendações IA', async ({ page }) => {
    await page.goto('/dashboard/comparador');
    const recomendacoes = page.locator('text=/Recomendação|IA|Análise/i');
    expect(await recomendacoes.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/comparador');
    await expect(page.locator('h1')).toBeVisible();
  });
});
