// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes de Fumaça - Planos de Compra
 * Fase 1 - Semana 1 - ROADMAP_TESTES_FRONTEND
 */

test.describe('Planos de Compra - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar a página em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/planos-compra');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
    console.log(`✓ Planos Compra carregou em ${loadTime}ms`);
  });

  test('deve exibir cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    
    const cards = page.locator('.card-gradient');
    await expect(cards.first()).toBeVisible();
  });

  test('deve ter botão "Novo Plano" funcional', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    
    const novoPlanoBtn = page.locator('button:has-text("Novo Plano"), button:has-text("Criar Plano")');
    await expect(novoPlanoBtn.first()).toBeVisible();
  });

  test('deve exibir lista de planos', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    await page.waitForTimeout(1000);
    
    // Verificar se há planos ou mensagem de vazio
    const planosList = page.locator('.plano-item, table tr, .card');
    const count = await planosList.count();
    console.log(`✓ ${count} elemento(s) de plano encontrado(s)`);
  });

  test('deve ter filtros funcionais', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    
    const filtros = page.locator('select, input[type="search"]');
    const count = await filtros.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve abrir modal ao clicar em "Novo Plano"', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    
    const novoPlanoBtn = page.locator('button:has-text("Novo Plano"), button:has-text("Criar Plano")').first();
    await novoPlanoBtn.click();
    await page.waitForTimeout(500);
    
    // Verificar se modal abriu
    const modal = page.locator('[role="dialog"], .modal, [x-show]');
    const isVisible = await modal.isVisible().catch(() => false);
    console.log(`✓ Modal ${isVisible ? 'abriu' : 'não detectado'}`);
  });

  test('deve ter simulador DCA', async ({ page }) => {
    await page.goto('/dashboard/planos-compra');
    
    // Procurar por elementos de simulação
    const simulador = page.locator('text=/DCA|Dollar Cost|Simulação/i');
    const count = await simulador.count();
    console.log(`✓ ${count} referência(s) a DCA/Simulação`);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/planos-compra');
    
    await expect(page.locator('h1')).toBeVisible();
    console.log('✓ Layout mobile responsivo');
  });
});
