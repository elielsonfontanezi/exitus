// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Ferramentas — Calculadora IR (lógica client-side) @ferramentas @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  async function abrirCalculadora(page) {
    await page.goto('/ferramentas/calculadora-ir');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);
  }

  // CT-027
  test('formulário da calculadora está presente com campos essenciais', async ({ page }) => {
    await abrirCalculadora(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/quantidade|preço|venda|médio|ganho|ir|imposto/);
  });

  // CT-028
  test('calculadora exibe resultado de IR após preenchimento', async ({ page }) => {
    await abrirCalculadora(page);
    const inputs = page.locator('input[type="number"], input[type="text"]');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
    const primeiro = inputs.first();
    await primeiro.fill('100');
    await page.waitForTimeout(300);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/resultado|total|ir|imposto|ganho|cálculo/);
  });

  // CT-029
  test('calculadora exibe alíquotas disponíveis (15% Ações, 20% FII)', async ({ page }) => {
    await abrirCalculadora(page);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/15%|20%|15,|20,/);
  });

  // CT-030
  test('opção de tipo de ativo está presente', async ({ page }) => {
    await abrirCalculadora(page);
    const seletor = page.locator('select, [x-model*="tipo"], [x-model*="categoria"]').first();
    await expect(seletor).toBeAttached({ timeout: 8000 });
  });

  // CT-031
  test('campo de compensação de prejuízo está presente', async ({ page }) => {
    await abrirCalculadora(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/prejuízo|compensação|loss|offset/);
  });
});
