// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes — Módulo Portfolio e Dashboard
 * Cobre: dashboard principal, portfólios, posições, alocação, evolução, proventos
 */

test.describe('Portfolio — Dashboard e Posições @portfolio', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  // --- Dashboard principal ---

  test('dashboard deve carregar em menos de 5s', async ({ page }) => {
    const start = Date.now();
    await page.goto('/dashboard/');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - start).toBeLessThan(5000);
  });

  test('dashboard deve exibir título ou header identificável', async ({ page }) => {
    await page.goto('/dashboard/');
    const heading = page.locator('h1, h2, .hero, [class*="header"]').first();
    await expect(heading).toBeVisible();
  });

  test('dashboard deve exibir ao menos um card de resumo', async ({ page }) => {
    await page.goto('/dashboard/');
    await page.waitForTimeout(1500);
    const cards = page.locator('[class*="card"], .rounded-2xl, .rounded-xl').first();
    await expect(cards).toBeVisible();
  });

  test('dashboard deve exibir menu de navegação', async ({ page }) => {
    await page.goto('/dashboard/');
    const nav = page.locator('nav, [class*="menu"], [class*="navbar"]').first();
    await expect(nav).toBeVisible();
  });

  test('dashboard não deve ter erros de console JS', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/dashboard/');
    await page.waitForTimeout(2000);
    const critical = errors.filter(e => !e.includes('favicon') && !e.includes('net::ERR_'));
    expect(critical).toHaveLength(0);
  });

  // --- Portfólios ---

  test('portfólios deve carregar sem erros', async ({ page }) => {
    await page.goto('/dashboard/portfolios');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  // --- Transações ---

  test('transações deve carregar e exibir conteúdo', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    await page.waitForTimeout(1500);
    await expect(page.locator('body')).not.toBeEmpty();
    await expect(page).not.toHaveURL(/404/);
  });

  // --- Proventos ---

  test('proventos recebidos deve carregar', async ({ page }) => {
    await page.goto('/proventos/recebidos');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('proventos projetados deve carregar', async ({ page }) => {
    await page.goto('/proventos/projetados');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('calendário de proventos deve carregar', async ({ page }) => {
    await page.goto('/proventos/calendario');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  // --- Alocação ---

  test('alocação deve exibir gráfico ou tabela de distribuição', async ({ page }) => {
    await page.goto('/analises/alocacao');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/rf|rv|renda|ação|fii|alocação/);
  });

  // --- Evolução ---

  test('evolução patrimonial deve carregar', async ({ page }) => {
    await page.goto('/analises/evolucao');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  // --- Responsividade ---

  test('dashboard deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/');
    await expect(page.locator('body')).toBeVisible();
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(overflow, 'Página com overflow horizontal no mobile').toBe(false);
  });

  test('dashboard deve ser responsivo em tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/dashboard/');
    await expect(page.locator('body')).toBeVisible();
  });
});
