// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Configurações - Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/configuracoes');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve ter seções de configuração', async ({ page }) => {
    await page.goto('/dashboard/configuracoes');
    const secoes = page.locator('[role="tab"], .section-title');
    expect(await secoes.count()).toBeGreaterThan(2);
  });

  test('deve permitir editar perfil', async ({ page }) => {
    await page.goto('/dashboard/configuracoes');
    const inputs = page.locator('input[type="text"], input[type="email"]');
    expect(await inputs.count()).toBeGreaterThan(0);
  });

  test('deve ter botão Salvar', async ({ page }) => {
    await page.goto('/dashboard/configuracoes');
    const saveBtn = page.locator('button:has-text("Salvar"), button[type="submit"]');
    await expect(saveBtn.first()).toBeVisible();
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/configuracoes');
    await expect(page.locator('h1')).toBeVisible();
  });
});
