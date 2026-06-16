// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Alertas - Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/alertas');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve ter botão Novo Alerta', async ({ page }) => {
    await page.goto('/dashboard/alertas');
    const btn = page.locator('button:has-text("Novo Alerta"), button:has-text("Criar")');
    await expect(btn.first()).toBeVisible();
  });

  test('deve listar alertas ativos', async ({ page }) => {
    await page.goto('/dashboard/alertas');
    await page.waitForTimeout(1000);
    const alertas = page.locator('.alerta-item, .card, table tr');
    console.log(`✓ ${await alertas.count()} alerta(s) encontrado(s)`);
  });

  test('deve ter filtros por tipo', async ({ page }) => {
    await page.goto('/dashboard/alertas');
    const filtros = page.locator('select, button[class*="filter"]');
    expect(await filtros.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/alertas');
    await expect(page.locator('h1')).toBeVisible();
  });
});
