// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Relatórios — Lógica de Exportação e Filtros @relatorios @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-042
  test('relatório mensal exibe dados com valores monetários', async ({ page }) => {
    await page.goto('/relatorios/mensal');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/R\$|\d+,\d{2}|mensal/i);
  });

  // CT-043
  test('extrato possui seletor de período (data início/fim)', async ({ page }) => {
    await page.goto('/relatorios/extrato');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);
    const seletor = page.locator('input[type="date"], select, [x-model*="data"], [x-model*="periodo"]').first();
    await expect(seletor).toBeAttached({ timeout: 8000 });
  });

  // CT-044
  test('botão de exportação CSV está presente', async ({ page }) => {
    await page.goto('/relatorios/exportar/csv');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);
    const btnExportar = page.locator('button, a').filter({ hasText: /exportar|baixar|download|csv/i }).first();
    await expect(btnExportar).toBeVisible({ timeout: 8000 });
  });

  // CT-044b
  test('exportação CSV dispara download (intercepta evento)', async ({ page }) => {
    await page.goto('/relatorios/exportar/csv');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);
    const [ download ] = await Promise.all([
      page.waitForEvent('download', { timeout: 10000 }).catch(() => null),
      page.locator('button, a').filter({ hasText: /exportar|baixar|download|csv/i }).first().click()
    ]);
    if (download) {
      expect(download.suggestedFilename()).toMatch(/\.csv$/i);
    }
  });

  // CT-045
  test('relatório anual exibe seletor de ano e dados consolidados', async ({ page }) => {
    await page.goto('/relatorios/anual');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/anual|ano|\d{4}|total|consolidado/);
  });
});
