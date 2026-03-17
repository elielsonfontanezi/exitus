// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Transações - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/transactions');
    await page.waitForLoadState('networkidle');
    expect(Date.now() - startTime).toBeLessThan(3000);
  });

  test('deve exibir 4 cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    const cards = page.locator('.card-gradient');
    await expect(cards).toHaveCount(4);
  });

  test('deve ter filtros avançados', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    const filtros = page.locator('select, input[type="text"], input[type="date"]');
    expect(await filtros.count()).toBeGreaterThan(3);
  });

  test('deve exibir tabela de transações', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve ter botão de exportação CSV', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    const exportBtn = page.locator('button:has-text("CSV"), button:has-text("Exportar")');
    expect(await exportBtn.count()).toBeGreaterThan(0);
  });

  test('deve ter paginação', async ({ page }) => {
    await page.goto('/dashboard/transactions');
    const pagination = page.locator('text=/Página|Anterior|Próxima/i');
    expect(await pagination.count()).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/transactions');
    await expect(page.locator('h1')).toBeVisible();
  });
});
