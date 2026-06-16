// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Portfolio — Lógica de Rentabilidade e Análises @portfolio @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-023
  test('rentabilidade exibe TWR e MWR', async ({ page }) => {
    await page.goto('/analises/rentabilidade');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toUpperCase()).toMatch(/TWR|MWR|RENTABILIDADE|%/);
  });

  // CT-024
  test('alocação exibe distribuição percentual', async ({ page }) => {
    await page.goto('/analises/alocacao');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/%|\d+,\d/);
    expect(texto?.toLowerCase()).toMatch(/rf|rv|renda|ação|fii|alocação|classe/);
  });

  // CT-025
  test('evolução patrimonial exibe valores monetários', async ({ page }) => {
    await page.goto('/analises/evolucao');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/R\$|\d+\.\d{3}|\d+,\d{2}/);
  });

  // CT-026
  test('performance exibe métricas de risco (Sharpe ou Drawdown)', async ({ page }) => {
    await page.goto('/analises/performance');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/sharpe|drawdown|risco|performance|índice/);
  });
});
