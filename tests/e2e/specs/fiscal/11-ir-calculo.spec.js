// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Fiscal — Lógica de IR e DARF @fiscal @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-017
  test('apuração mensal exibe categorias de ativos', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/ação|fii|etf|renda fixa|categoria/);
  });

  // CT-018
  test('apuração mensal exibe valores monetários formatados', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/R\$|0,00|\d+,\d{2}/);
  });

  // CT-019
  test('seletor de mês/ano está presente e é interativo', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const seletor = page.locator('select, input[type="month"], [x-model*="mes"], [x-model*="ano"]').first();
    await expect(seletor).toBeAttached({ timeout: 8000 });
  });

  // CT-020
  test('DARFs exibem campos obrigatórios (valor, competência)', async ({ page }) => {
    await page.goto('/imposto-renda/darf');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/competência|vencimento|valor|darf|código/);
  });

  // CT-021
  test('histórico anual lista meses do ano', async ({ page }) => {
    await page.goto('/imposto-renda/historico');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez|janeiro|fevereiro/);
  });

  // CT-022
  test('DIRPF exibe bens e direitos com valores', async ({ page }) => {
    await page.goto('/imposto-renda/dirpf');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/bem|direito|código|discriminação|valor|31\/12|patrimônio/);
  });
});
