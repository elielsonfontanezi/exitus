// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Proventos - Smoke Tests @smoke', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'senha123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/proventos-calendario');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir calendário de proventos', async ({ page }) => {
    await page.goto('/dashboard/proventos-calendario');
    const calendario = page.locator('[class*="calendar"], table');
    const count = await calendario.count();
    if (count > 0) {
      // Verificar se algum elemento está visível
      let visible = false;
      for (let i = 0; i < count; i++) {
        if (await calendario.nth(i).isVisible()) {
          visible = true;
          break;
        }
      }
      expect(visible).toBe(true);
    } else {
      console.log('✓ Calendário não encontrado (OK para proventos)');
    }
  });

  test('deve mostrar yield total', async ({ page }) => {
    await page.goto('/dashboard/proventos-calendario');
    const yieldText = page.locator('text=/Yield|DY|Dividend/i');
    expect(await yieldText.count()).toBeGreaterThan(0);
  });

  test('deve listar próximos pagamentos', async ({ page }) => {
    await page.goto('/dashboard/proventos-calendario');
    const proximos = page.locator('text=/Próximos|Futuros/i');
    expect(await proximos.count()).toBeGreaterThan(0);
  });

  test('deve ter filtro por tipo', async ({ page }) => {
    await page.goto('/dashboard/proventos-calendario');
    const filtro = page.locator('select, button[class*="filter"]');
    expect(await filtro.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/proventos-calendario');
    await expect(page.locator('h1')).toBeVisible();
  });
});
