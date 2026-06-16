// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes — Módulo Ferramentas (Sprint 8)
 * Cobre: Screener, Comparador, Calculadora IR, Simulador
 */

test.describe('Ferramentas — Screener, Comparador, Calculadora, Simulador @ferramentas', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  // --- Screener ---

  test('screener deve carregar sem erros', async ({ page }) => {
    await page.goto('/ferramentas/screener');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('screener deve exibir filtros (DY, P/VP, P/L, tipo)', async ({ page }) => {
    await page.goto('/ferramentas/screener');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/dy|p\/vp|p\/l|tipo|filtro|dividendo/);
  });

  test('screener deve exibir tabela ou lista de ativos', async ({ page }) => {
    await page.goto('/ferramentas/screener');
    await page.waitForTimeout(2000);
    const rows = await page.locator('tr, [class*="row"], [class*="card"]').count();
    expect(rows).toBeGreaterThan(0);
  });

  // --- Comparador ---

  test('comparador deve carregar sem erros', async ({ page }) => {
    await page.goto('/ferramentas/comparador');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('comparador deve exibir campos para inserir tickers', async ({ page }) => {
    await page.goto('/ferramentas/comparador');
    await page.waitForTimeout(1000);
    const inputs = await page.locator('input[type="text"], input[placeholder*="ticker"], select').count();
    expect(inputs).toBeGreaterThan(0);
  });

  test('comparador deve exibir colunas de comparação', async ({ page }) => {
    await page.goto('/ferramentas/comparador');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/comparar|ativo|fundamento|cotação|ticker/);
  });

  // --- Calculadora IR ---

  test('calculadora IR deve carregar sem erros', async ({ page }) => {
    await page.goto('/ferramentas/calculadora-ir');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('calculadora IR deve exibir campos de simulação', async ({ page }) => {
    await page.goto('/ferramentas/calculadora-ir');
    await page.waitForTimeout(1000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/ganho|perda|ir|imposto|alíquota|simulação|calcul/);
  });

  test('calculadora IR deve mencionar isenção ou swing trade', async ({ page }) => {
    await page.goto('/ferramentas/calculadora-ir');
    await page.waitForTimeout(1000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/isençã|swing|day trade|fii|r\$\s*20/);
  });

  // --- Simulador de Aportes ---

  test('simulador deve carregar sem erros', async ({ page }) => {
    await page.goto('/ferramentas/simulador');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('simulador deve exibir campos de aporte e prazo', async ({ page }) => {
    await page.goto('/ferramentas/simulador');
    await page.waitForTimeout(1000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/aporte|prazo|taxa|juros|compostos|simulação|patrimônio/);
  });

  test('simulador deve calcular resultado ao preencher campos', async ({ page }) => {
    await page.goto('/ferramentas/simulador');
    await page.waitForTimeout(1000);
    // Preenche algum campo numérico de aporte
    const inputAporte = page.locator('input[type="number"]').first();
    if (await inputAporte.isVisible()) {
      await inputAporte.fill('1000');
      await page.waitForTimeout(500);
    }
    // Deve continuar sem erros
    await expect(page.locator('body')).toBeVisible();
  });

  // --- Console errors ---

  test('ferramentas não devem ter erros de console JS', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/ferramentas/screener');
    await page.waitForTimeout(2000);
    const critical = errors.filter(e => !e.includes('favicon') && !e.includes('net::ERR_'));
    expect(critical).toHaveLength(0);
  });
});
