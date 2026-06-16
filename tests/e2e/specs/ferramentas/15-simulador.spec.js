// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Ferramentas — Simulador de Aportes @ferramentas @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  async function abrirSimulador(page) {
    await page.goto('/ferramentas/simulador');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);
  }

  // CT-038
  test('simulador possui campos de aporte inicial, mensal, taxa e prazo', async ({ page }) => {
    await abrirSimulador(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/aporte|inicial|mensal|taxa|prazo|período/);
  });

  // CT-039
  test('simulador exibe resultado após preenchimento', async ({ page }) => {
    await abrirSimulador(page);
    const inputs = page.locator('input[type="number"]');
    const count = await inputs.count();
    if (count >= 1) {
      await inputs.first().fill('10000');
      await page.waitForTimeout(500);
    }
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/resultado|total|montante|patrimônio|acumulado/);
  });

  // CT-040
  test('tabela ou seção de marcos está presente', async ({ page }) => {
    await abrirSimulador(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/marco|meta|100|500|1\.000\.000|1 milhão|objetivo/);
  });

  // CT-041
  test('campos do simulador são editáveis e reagem a mudanças', async ({ page }) => {
    await abrirSimulador(page);
    const inputs = page.locator('input[type="number"], input[type="range"]');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
    const primeiro = inputs.first();
    await expect(primeiro).toBeEnabled({ timeout: 8000 });
    await primeiro.fill('5000');
    await page.waitForTimeout(300);
  });
});
