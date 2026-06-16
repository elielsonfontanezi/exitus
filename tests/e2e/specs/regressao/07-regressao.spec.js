// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes de Regressão — Fluxos críticos ponta-a-ponta
 * Cobre: navegação completa, menu sem 404, fluxo fiscal, planos e alertas
 */

test.describe('Regressão — Fluxos Críticos @regressao', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // --- Navegação via menu ---

  test('menu deve ter links para todas as seções principais', async ({ page }) => {
    await page.goto('/dashboard/');
    const menuLinks = await page.locator('nav a, [class*="menu"] a').evaluateAll(
      links => links.map(l => ({ text: l.textContent?.trim(), href: l.getAttribute('href') }))
    );
    // Deve ter mais de 5 links no menu
    expect(menuLinks.length).toBeGreaterThan(5);
  });

  test('nenhum link do menu deve apontar para rota 404', async ({ page }) => {
    await page.goto('/dashboard/');
    const hrefs = await page.locator('nav a[href], [class*="menu"] a[href]').evaluateAll(
      links => links
        .map(l => l.getAttribute('href'))
        .filter(h => h && h.startsWith('/') && !h.startsWith('/auth') && !h.includes('#'))
    );

    const erros404 = [];
    for (const href of hrefs.slice(0, 20)) { // limita a 20 para performance
      try {
        const resp = await page.request.get(`http://localhost:8080${href}`);
        if (resp.status() === 404) erros404.push(href);
      } catch (_) { /* ignora erros de rede */ }
    }
    expect(erros404, `Links com 404: ${erros404.join(', ')}`).toHaveLength(0);
  });

  // --- Fluxo: Dashboard → Operações → Dashboard ---

  test('deve navegar Dashboard → Operações → Dashboard sem erro', async ({ page }) => {
    await page.goto('/dashboard/');
    await page.goto('/operacoes/');
    await expect(page).not.toHaveURL(/404/);
    await page.goto('/dashboard/');
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  // --- Fluxo: Dashboard → IR → DARF ---

  test('deve navegar IR Mensal → DARFs → Histórico sem erro', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await expect(page).not.toHaveURL(/404/);
    await page.goto('/imposto-renda/darfs');
    await expect(page).not.toHaveURL(/404/);
    await page.goto('/imposto-renda/historico');
    await expect(page).not.toHaveURL(/404/);
  });

  // --- Fluxo: Planos e Alertas ---

  test('planos de compra devem carregar sem erros', async ({ page }) => {
    await page.goto('/planos-compra/');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('alertas devem carregar e exibir lista', async ({ page }) => {
    await page.goto('/alertas/');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/alerta|ativo|preço|condição|tipo/);
  });

  // --- Fluxo: Catálogo de Ativos ---

  test('catálogo de ações deve carregar e exibir ativos', async ({ page }) => {
    await page.goto('/ativos/acoes');
    await page.waitForTimeout(2000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/ação|ticker|p\/l|dy|roe|ativo/);
  });

  test('catálogo de FIIs deve carregar e exibir ativos', async ({ page }) => {
    await page.goto('/ativos/fiis');
    await page.waitForTimeout(2000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/fii|fundo|imobiliário|dy|p\/vp/);
  });

  // --- Fluxo: Ferramentas ponta a ponta ---

  test('fluxo screener → comparador deve funcionar sem 404', async ({ page }) => {
    await page.goto('/ferramentas/screener');
    await expect(page).not.toHaveURL(/404/);
    await page.goto('/ferramentas/comparador');
    await expect(page).not.toHaveURL(/404/);
  });

  // --- Análises ---

  test('buy signals deve carregar e exibir scores', async ({ page }) => {
    await page.goto('/analises/buy-signals');
    await page.waitForTimeout(2000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/score|signal|buy|ticker|margem/);
  });

  test('performance deve carregar e exibir métricas', async ({ page }) => {
    await page.goto('/analises/performance');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/sharpe|drawdown|rentabilidade|performance/);
  });

  // --- Responsividade global ---

  test('todas as telas principais devem ser responsivas em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    const telas = ['/dashboard/', '/operacoes/', '/analises/alocacao', '/imposto-renda/mensal'];
    for (const tela of telas) {
      await page.goto(tela);
      const overflow = await page.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth
      );
      expect(overflow, `Overflow horizontal em mobile: ${tela}`).toBe(false);
    }
  });
});
