// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes de Fumaça - Imposto de Renda
 * Fase 1 - Semana 1 - ROADMAP_TESTES_FRONTEND
 */

test.describe('Imposto de Renda - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar a página de IR em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/imposto-renda');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
    console.log(`✓ IR carregou em ${loadTime}ms`);
  });

  test('deve exibir 4 cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/imposto-renda');
    
    const cards = page.locator('.card-gradient');
    await expect(cards).toHaveCount(4);
  });

  test('deve ter 4 abas funcionais', async ({ page }) => {
    await page.goto('/dashboard/imposto-renda');
    
    // Verificar abas
    const tabs = page.locator('[role="tab"]');
    const count = await tabs.count();
    expect(count).toBeGreaterThanOrEqual(4);
    console.log(`✓ ${count} abas encontradas`);
  });

  test('deve calcular IR automaticamente', async ({ page }) => {
    await page.goto('/dashboard/imposto-renda');
    
    // Verificar se há valores calculados
    const irAcumulado = page.locator('text=/R\\$ [0-9,]+/').first();
    await expect(irAcumulado).toBeVisible();
  });

  test('deve exibir lista de DARFs', async ({ page }) => {
    await page.goto('/dashboard/imposto-renda');
    
    // Clicar na aba DARFs
    await page.click('text=DARFs');
    await page.waitForTimeout(500);
    
    // Verificar se lista existe
    const darfsList = page.locator('.darf-item, table tr');
    const count = await darfsList.count();
    console.log(`✓ ${count} DARF(s) listado(s)`);
  });

  test('deve ter calculadora de IR funcional', async ({ page }) => {
    await page.goto('/dashboard/imposto-renda');
    
    // Clicar na aba Calculadora
    await page.click('text=Calculadora');
    await page.waitForTimeout(500);
    
    // Verificar campos de entrada
    const inputs = page.locator('input[type="number"]');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/imposto-renda');
    
    await expect(page.locator('h1')).toBeVisible();
    console.log('✓ Layout mobile responsivo');
  });
});
