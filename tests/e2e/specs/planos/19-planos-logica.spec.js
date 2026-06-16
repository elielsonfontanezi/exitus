// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Planos — Lógica de Compra e Venda @planos @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-060 — Planos de Compra: lista existente
  test('planos de compra exibe lista de planos do usuário', async ({ page }) => {
    await page.goto('/planos-compra/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/plano|compra|aporte|ticker|meta|acumulação/);
  });

  // CT-061 — Planos de Compra: exibe dados do plano
  test('planos de compra exibe ticker, aporte e progresso', async ({ page }) => {
    await page.goto('/planos-compra/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/R\$|\d+%|\d+,\d{2}|meta|progresso|aporte/i);
  });

  // CT-062 — Planos de Compra: botão de criação presente
  test('planos de compra possui ação de criar novo plano', async ({ page }) => {
    await page.goto('/planos-compra/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnNovo = page.locator('a, button').filter({ hasText: /novo|criar|adicionar/i }).first();
    await expect(btnNovo).toBeAttached({ timeout: 8000 });
  });

  // CT-063 — Planos de Compra: detalhe do plano é acessível
  test('ao clicar em plano de compra, detalhe é carregado', async ({ page }) => {
    await page.goto('/planos-compra/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const linkDetalhe = page.locator('a[href*="/planos-compra/"]').filter({ hasNotText: /novo|criar/i }).first();
    const exists = await linkDetalhe.count();
    if (exists > 0) {
      await linkDetalhe.click();
      await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
      expect(page.url()).not.toContain('/auth/login');
      const texto = await page.textContent('body');
      expect(texto?.toLowerCase()).toMatch(/plano|detalhe|ticker|aporte|progresso/);
    } else {
      test.skip();
    }
  });

  // CT-064 — Planos de Venda: lista existente
  test('planos de venda exibe lista de planos do usuário', async ({ page }) => {
    await page.goto('/planos-venda/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/plano|venda|stop|preço|alvo|gain|loss/);
  });

  // CT-065 — Planos de Venda: exibe preços de saída
  test('planos de venda exibe preço alvo ou stop loss', async ({ page }) => {
    await page.goto('/planos-venda/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/stop|gain|loss|alvo|parcial|preço|r\$/);
  });

  // CT-066 — Planos de Venda: botão de criação presente
  test('planos de venda possui ação de criar novo plano', async ({ page }) => {
    await page.goto('/planos-venda/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnNovo = page.locator('a, button').filter({ hasText: /novo|criar|adicionar/i }).first();
    await expect(btnNovo).toBeAttached({ timeout: 8000 });
  });
});
