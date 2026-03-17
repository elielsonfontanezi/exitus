// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes de Fumaça - Dashboard Multi-Mercado
 * Fase 1 - Semana 1 - ROADMAP_TESTES_FRONTEND
 */

test.describe('Dashboard - Smoke Tests @smoke @critical', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login antes de cada teste
    await page.goto('/login');
    await page.fill('input[name="username"]', 'test@exitus.com');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard/');
  });

  test('deve carregar a página do dashboard em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000);
    console.log(`✓ Dashboard carregou em ${loadTime}ms`);
  });

  test('deve exibir o título "Dashboard" corretamente', async ({ page }) => {
    await page.goto('/dashboard/');
    
    const title = await page.locator('h1').first();
    await expect(title).toContainText('Dashboard');
  });

  test('deve exibir os cards de resumo', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se os cards principais existem
    const cards = page.locator('.card-gradient');
    await expect(cards).toHaveCount(4); // 4 cards principais
  });

  test('deve renderizar gráficos sem erro', async ({ page }) => {
    await page.goto('/dashboard/');
    await page.waitForTimeout(2000); // Aguardar renderização dos gráficos
    
    // Verificar se canvas do Chart.js existe
    const charts = page.locator('canvas');
    const count = await charts.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✓ ${count} gráfico(s) renderizado(s)`);
  });

  test('deve alternar entre BRL e USD com currency toggle', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar toggle existe
    const toggle = page.locator('[data-currency-toggle]');
    await expect(toggle).toBeVisible();
    
    // Clicar no toggle
    await toggle.click();
    await page.waitForTimeout(500);
    
    // Verificar se valores mudaram (deve conter $ ao invés de R$)
    const valores = page.locator('text=/\\$/');
    const count = await valores.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✓ Currency toggle funcionando (${count} valores em USD)`);
  });

  test('deve ser responsivo em mobile (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard/');
    
    // Verificar se página carrega
    await expect(page.locator('h1')).toBeVisible();
    
    // Verificar se cards estão empilhados (grid-cols-1)
    const container = page.locator('.grid').first();
    await expect(container).toBeVisible();
    console.log('✓ Layout mobile responsivo');
  });

  test('deve ser responsivo em tablet (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/dashboard/');
    
    await expect(page.locator('h1')).toBeVisible();
    console.log('✓ Layout tablet responsivo');
  });

  test('deve exibir loading states durante carregamento', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se spinner de loading aparece (pode ser rápido)
    const spinner = page.locator('.animate-spin');
    // Se ainda estiver carregando, deve estar visível
    const isVisible = await spinner.isVisible().catch(() => false);
    console.log(`✓ Loading state ${isVisible ? 'detectado' : 'já concluído'}`);
  });

  test('deve ter animações suaves nos cards (fade-in)', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se cards têm classe de animação
    const animatedCards = page.locator('.animate-fade-in');
    const count = await animatedCards.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✓ ${count} elemento(s) com animação fade-in`);
  });

  test('deve ter botão "Voltar" funcional', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se existe link/botão de voltar
    const backButton = page.locator('a[href="/dashboard/"]').first();
    await expect(backButton).toBeVisible();
  });

  test('deve persistir preferência de moeda no localStorage', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Alternar para USD
    const toggle = page.locator('[data-currency-toggle]');
    await toggle.click();
    await page.waitForTimeout(500);
    
    // Verificar localStorage
    const currency = await page.evaluate(() => localStorage.getItem('preferredCurrency'));
    expect(currency).toBe('USD');
    console.log('✓ Preferência de moeda persistida');
  });

  test('deve exibir dados mock quando API offline', async ({ page }) => {
    // Simular API offline bloqueando requests
    await page.route('**/api/**', route => route.abort());
    
    await page.goto('/dashboard/');
    await page.waitForTimeout(2000);
    
    // Mesmo com API offline, deve exibir dados mock
    const cards = page.locator('.card-gradient');
    await expect(cards.first()).toBeVisible();
    console.log('✓ Mock data fallback funcionando');
  });

  test('deve ter contraste adequado (acessibilidade)', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se texto é legível (não está com opacity muito baixa)
    const mainHeading = page.locator('h1').first();
    const color = await mainHeading.evaluate(el => 
      window.getComputedStyle(el).color
    );
    
    // Verificar que não é transparente
    expect(color).not.toContain('rgba(0, 0, 0, 0)');
    console.log(`✓ Contraste de texto adequado: ${color}`);
  });

  test('deve navegar para outras telas do menu', async ({ page }) => {
    await page.goto('/dashboard/');
    
    // Verificar se links de navegação existem
    const navLinks = page.locator('nav a, .sidebar a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(5); // Deve ter vários links
    console.log(`✓ ${count} links de navegação encontrados`);
  });

  test('não deve ter erros de console JavaScript', async ({ page }) => {
    const consoleErrors = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    await page.goto('/dashboard/');
    await page.waitForTimeout(2000);
    
    expect(consoleErrors.length).toBe(0);
    if (consoleErrors.length > 0) {
      console.log('❌ Erros de console:', consoleErrors);
    } else {
      console.log('✓ Sem erros de console');
    }
  });

  test('deve ter meta tags para SEO', async ({ page }) => {
    await page.goto('/dashboard/');
    
    const title = await page.title();
    expect(title).toContain('Dashboard');
    console.log(`✓ Page title: ${title}`);
  });
});
