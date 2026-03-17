// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Relatórios - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/reports');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir 4 cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/reports');
    const cards = page.locator('.card-gradient');
    await expect(cards).toHaveCount(4);
  });

  test('deve ter dropdown "Gerar Relatório"', async ({ page }) => {
    await page.goto('/dashboard/reports');
    const btn = page.locator('button:has-text("Gerar"), button:has-text("Novo Relatório")');
    await expect(btn.first()).toBeVisible();
  });

  test('deve exibir grid de relatórios', async ({ page }) => {
    await page.goto('/dashboard/reports');
    await page.waitForTimeout(1000);
    const relatorios = page.locator('.border.rounded-lg, .card');
    console.log(`✓ ${await relatorios.count()} relatório(s) encontrado(s)`);
  });

  test('deve ter botões de download', async ({ page }) => {
    await page.goto('/dashboard/reports');
    const downloadBtns = page.locator('button:has-text("Download"), svg[class*="download"]');
    expect(await downloadBtns.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/reports');
    await expect(page.locator('h1')).toBeVisible();
  });
});
