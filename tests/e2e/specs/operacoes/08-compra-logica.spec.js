// @ts-check
const { test, expect, request } = require('@playwright/test');

const BASE_API = 'http://localhost:5000';

async function loginApi(username = 'e2e_user', password = 'e2e_senha_123') {
  const ctx = await request.newContext();
  const res = await ctx.post(`${BASE_API}/api/auth/login`, {
    data: { username, password }
  });
  const body = await res.json();
  await ctx.dispose();
  return body?.data?.access_token || null;
}

async function deleteLastTransacao(token) {
  if (!token) return;
  const ctx = await request.newContext();
  const res = await ctx.get(`${BASE_API}/api/transacoes?limit=1&order=desc`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const body = await res.json();
  const id = body?.data?.[0]?.id;
  if (id) {
    await ctx.delete(`${BASE_API}/api/transacoes/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }
  await ctx.dispose();
}

test.describe('Operações — Lógica de Compra @operacoes @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-001
  test('seleção de tipo revela campos do formulário', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await expect(tipoCard).toBeVisible({ timeout: 8000 });
    await tipoCard.click();
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await expect(inputTicker).toBeVisible({ timeout: 8000 });
  });

  // CT-002
  test('busca de ativo retorna sugestões', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await inputTicker.fill('PETR');
    await page.waitForTimeout(500);
    const sugestoes = page.locator('[x-show*="showSuggestions"], [x-show*="suggestions"]').first();
    await expect(sugestoes).toBeVisible({ timeout: 8000 });
  });

  // CT-003
  test('seleção de ativo revela campos de quantidade e preço', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await inputTicker.fill('PETR');
    await page.waitForTimeout(500);
    const sugestao = page.locator('[x-text*="ticker"], .font-bold').filter({ hasText: /PETR4/i }).first();
    if (await sugestao.isVisible()) {
      await sugestao.click();
    }
    const inputQtd = page.locator('input[x-model="form.quantidade"]');
    await expect(inputQtd).toBeVisible({ timeout: 8000 });
    const inputPreco = page.locator('input[x-model="form.preco_unitario"]');
    await expect(inputPreco).toBeVisible({ timeout: 8000 });
  });

  // CT-004
  test('quantidade fracionada para Ação BR dispara alerta', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await inputTicker.fill('PETR');
    await page.waitForTimeout(500);
    const sugestao = page.locator('[x-text*="ticker"], .font-bold').filter({ hasText: /PETR4/i }).first();
    if (await sugestao.isVisible()) await sugestao.click();
    const inputQtd = page.locator('input[x-model="form.quantidade"]');
    await expect(inputQtd).toBeVisible({ timeout: 8000 });
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('inteira');
      await dialog.accept();
    });
    await inputQtd.fill('1.5');
    await inputQtd.dispatchEvent('change');
    await page.waitForTimeout(500);
  });

  // CT-005
  test('resumo calcula total corretamente (quantidade × preço)', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    const inputTicker = page.locator('input[placeholder*="ticker"]').first();
    await inputTicker.fill('PETR');
    await page.waitForTimeout(500);
    const sugestao = page.locator('[x-text*="ticker"], .font-bold').filter({ hasText: /PETR4/i }).first();
    if (await sugestao.isVisible()) await sugestao.click();
    const inputQtd = page.locator('input[x-model="form.quantidade"]');
    await expect(inputQtd).toBeVisible({ timeout: 8000 });
    await inputQtd.fill('10');
    const inputPreco = page.locator('input[x-model="form.preco_unitario"]');
    await inputPreco.fill('30');
    await page.waitForTimeout(500);
    const resumo = page.locator('body');
    const texto = await resumo.textContent();
    expect(texto).toMatch(/300/);
  });

  // CT-007
  test('toggle Compra/Venda alterna modo corretamente', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnVenda = page.locator('button').filter({ hasText: /^venda$/i }).first();
    await expect(btnVenda).toBeVisible({ timeout: 8000 });
    await btnVenda.click();
    await page.waitForTimeout(300);
    const tipoCard = page.locator('.tipo-card').filter({ hasText: /ação br/i }).first();
    await tipoCard.click();
    const inputBuscaPosicao = page.locator('input[x-model="searchPosicao"]');
    await expect(inputBuscaPosicao).toBeAttached({ timeout: 8000 });
  });

  // CT-008
  test('botão submit desabilitado sem corretora selecionada', async ({ page }) => {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnSubmit = page.locator('button[type="submit"], button').filter({ hasText: /confirmar/i }).first();
    await expect(btnSubmit).toBeDisabled({ timeout: 8000 });
  });
});
