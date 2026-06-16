// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Planos de Venda - Smoke Tests @smoke @critical', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/planos-venda');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve ter botão Novo Plano', async ({ page }) => {
    await page.goto('/dashboard/planos-venda');
    const btn = page.locator('button:has-text("Novo Plano"), button:has-text("Criar")');
    await expect(btn.first()).toBeVisible();
  });

  test('deve listar planos de venda', async ({ page }) => {
    await page.goto('/dashboard/planos-venda');
    await page.waitForTimeout(1000);
    const planos = page.locator('.plano-item, .card, table tr');
    console.log(`✓ ${await planos.count()} plano(s) encontrado(s)`);
  });

  test('deve ter configuração stop gain/loss', async ({ page }) => {
    await page.goto('/dashboard/planos-venda');
    const stopConfig = page.locator('text=/Stop|Gain|Loss|Trailing/i');
    expect(await stopConfig.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/planos-venda');
    await expect(page.locator('h1')).toBeVisible();
  });
});
