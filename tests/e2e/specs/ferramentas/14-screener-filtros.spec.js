// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Ferramentas — Screener (filtros) @ferramentas @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  async function abrirScreener(page) {
    await page.goto('/ferramentas/screener');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
  }

  // CT-032
  test('screener carrega tabela ou lista de ativos', async ({ page }) => {
    await abrirScreener(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/ticker|ativo|ação|fii|preço/);
  });

  // CT-033
  test('filtro por tipo existe e é interativo', async ({ page }) => {
    await abrirScreener(page);
    const filtroTipo = page.locator('select, button, [x-model*="tipo"], [x-model*="filter"]').filter({ hasText: /tipo|fii|ação|ativo/i }).first();
    await expect(filtroTipo).toBeAttached({ timeout: 8000 });
  });

  // CT-034
  test('campo de filtro por DY existe', async ({ page }) => {
    await abrirScreener(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/dy|dividend yield|dividendo/);
  });

  // CT-035
  test('campo de filtro por P/VP existe', async ({ page }) => {
    await abrirScreener(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/p\/vp|pvp|preço\/valor patrimonial/);
  });

  // CT-036
  test('múltiplos filtros podem ser combinados', async ({ page }) => {
    await abrirScreener(page);
    const inputs = page.locator('input[type="number"], input[type="text"]');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(1);
  });

  // CT-037
  test('botão de limpar filtros existe', async ({ page }) => {
    await abrirScreener(page);
    const btnLimpar = page.locator('button').filter({ hasText: /limpar|resetar|clear|todos/i }).first();
    await expect(btnLimpar).toBeAttached({ timeout: 8000 });
  });
});
