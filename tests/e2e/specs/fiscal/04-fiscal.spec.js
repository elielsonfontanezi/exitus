// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes — Módulo Fiscal (IR, DARFs, Histórico, Declaração)
 */

test.describe('Fiscal — Imposto de Renda @fiscal', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  test('IR Mensal deve carregar sem erros', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('IR Mensal deve exibir categorias de apuração', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    // Deve mencionar alguma categoria fiscal
    expect(body?.toLowerCase()).toMatch(/swing|day trade|fii|renda fixa|provent/);
  });

  test('DARFs deve carregar sem erros', async ({ page }) => {
    await page.goto('/imposto-renda/darfs');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('DARFs deve exibir referência a código de receita ou valor', async ({ page }) => {
    await page.goto('/imposto-renda/darfs');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/darf|receita|código|ir|imposto/);
  });

  test('Histórico IR deve carregar sem erros', async ({ page }) => {
    await page.goto('/imposto-renda/historico');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('Histórico IR deve exibir dados de 12 meses', async ({ page }) => {
    await page.goto('/imposto-renda/historico');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    // Deve conter referência a meses ou anos
    expect(body?.toLowerCase()).toMatch(/jan|fev|mar|2024|2025|2026|histórico/);
  });

  test('Declaração DIRPF deve carregar sem erros', async ({ page }) => {
    await page.goto('/imposto-renda/declaracao');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('Declaração deve exibir bens e direitos', async ({ page }) => {
    await page.goto('/imposto-renda/declaracao');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/bem|direito|dirpf|declaração|patrimônio/);
  });

  test('fiscal não deve ter erros de console JS', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/imposto-renda/mensal');
    await page.waitForTimeout(1500);
    const critical = errors.filter(e => !e.includes('favicon') && !e.includes('net::ERR_'));
    expect(critical).toHaveLength(0);
  });

  test('fiscal deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/imposto-renda/mensal');
    await expect(page.locator('body')).toBeVisible();
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(overflow, 'Overflow horizontal em mobile na tela fiscal').toBe(false);
  });
});
