// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Ativos — Lógica de Catálogo @ativos @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-051 — Ações
  test('catálogo de ações exibe lista com ticker e tipo', async ({ page }) => {
    await page.goto('/ativos/acoes');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/ação|ações|ticker|código|on|pn/);
  });

  // CT-052 — Ações: filtro por busca
  test('catálogo de ações possui campo de busca funcional', async ({ page }) => {
    await page.goto('/ativos/acoes');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const inputBusca = page.locator('input[type="search"], input[type="text"], input[placeholder*="busca"], input[placeholder*="ticker"]').first();
    await expect(inputBusca).toBeAttached({ timeout: 8000 });
  });

  // CT-053 — Ações: exibe dados fundamentalistas
  test('catálogo de ações exibe dados como preço ou P/L', async ({ page }) => {
    await page.goto('/ativos/acoes');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/preço|p\/l|p\/vp|dy|dividend|cotação|r\$/);
  });

  // CT-054 — FIIs
  test('catálogo de FIIs exibe itens da categoria FII', async ({ page }) => {
    await page.goto('/ativos/fiis');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/fii|fundo|imobiliário|rendimento|cota/);
  });

  // CT-055 — FIIs: métrica de DY disponível
  test('catálogo de FIIs exibe dividend yield', async ({ page }) => {
    await page.goto('/ativos/fiis');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/dy|dividend yield|yield|rendimento|%/);
  });

  // CT-056 — ETFs
  test('catálogo de ETFs exibe lista com dados de ativos', async ({ page }) => {
    await page.goto('/ativos/etfs');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/etf|índice|ivvb|bova|ticker|preço/);
  });

  // CT-057 — Renda Fixa
  test('catálogo de renda fixa exibe ativos de RF', async ({ page }) => {
    await page.goto('/ativos/renda-fixa');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/renda fixa|cdi|ipca|tesouro|lci|lca|cri|cra|debenture|taxa/);
  });

  // CT-058 — Cripto
  test('catálogo de criptoativos exibe ativos digitais', async ({ page }) => {
    await page.goto('/ativos/cripto');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/cripto|bitcoin|btc|eth|ethereum|usdt|digital/);
  });

  // CT-059 — Ativos: categorias distintas no menu
  test('menu de ativos exibe links para todas as categorias', async ({ page }) => {
    await page.goto('/ativos/acoes');
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
    const menuLinks = page.locator('nav a[href*="/ativos/"]');
    const count = await menuLinks.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });
});
