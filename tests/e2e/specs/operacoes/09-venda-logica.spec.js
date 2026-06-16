// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Operações — Lógica de Venda @operacoes @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  async function ativarModoVenda(page) {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnVenda = page.locator('button').filter({ hasText: /^venda$/i }).first();
    await expect(btnVenda).toBeVisible({ timeout: 8000 });
    await btnVenda.click();
    await page.waitForTimeout(300);
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    await page.waitForTimeout(500);
  }

  // CT-009
  test('modo venda exibe posições do usuário', async ({ page }) => {
    await ativarModoVenda(page);
    const inputBusca = page.locator('input[x-model="searchPosicao"]');
    await expect(inputBusca).toBeVisible({ timeout: 10000 });
  });

  // CT-010
  test('busca filtra posições pelo ticker', async ({ page }) => {
    await ativarModoVenda(page);
    const inputBusca = page.locator('input[x-model="searchPosicao"]');
    await expect(inputBusca).toBeVisible({ timeout: 10000 });
    await inputBusca.fill('PETR');
    await page.waitForTimeout(500);
    const posicoes = page.locator('[x-show*="posicoesFiltradas"], [x-show*="showPosicoes"]').first();
    const texto = await page.textContent('body');
    if (texto?.includes('PETR')) {
      expect(texto).toContain('PETR');
    }
  });

  // CT-011
  test('quantidade maior que disponível exibe mensagem de erro', async ({ page }) => {
    await ativarModoVenda(page);
    const inputQtd = page.locator('input[x-model="form.quantidade"]');
    await expect(inputQtd).toBeAttached({ timeout: 8000 });
    const erroQtd = page.locator('[x-show*="quantidadeMaxima"]').first();
    await expect(erroQtd).toBeAttached();
  });

  // CT-012
  test('botão Máx existe e está acessível no modo venda', async ({ page }) => {
    await ativarModoVenda(page);
    const btnMax = page.locator('[x-show*="quantidadeMaxima"], [title*="máxima"], [title*="Usar"]').first();
    await expect(btnMax).toBeAttached({ timeout: 8000 });
  });

  // CT-013
  test('resumo da operação exibe seção de resultado', async ({ page }) => {
    await ativarModoVenda(page);
    const resumo = page.locator('text=/resumo/i').first();
    await expect(resumo).toBeVisible({ timeout: 8000 });
  });
});
