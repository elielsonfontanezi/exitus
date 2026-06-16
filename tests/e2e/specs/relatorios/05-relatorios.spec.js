// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes — Módulo Relatórios e Exportação (Sprint 7)
 */

test.describe('Relatórios — Mensal, Anual, Extrato, IR, CSV @relatorios', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  test('relatório mensal deve carregar sem erros', async ({ page }) => {
    await page.goto('/relatorios/mensal');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('relatório mensal deve exibir transações ou proventos', async ({ page }) => {
    await page.goto('/relatorios/mensal');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/transaç|provento|mensal|receita|gasto/);
  });

  test('relatório anual deve carregar sem erros', async ({ page }) => {
    await page.goto('/relatorios/anual');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('relatório anual deve exibir histórico de IR', async ({ page }) => {
    await page.goto('/relatorios/anual');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/anual|2024|2025|2026|histórico|ir/);
  });

  test('extrato deve carregar sem erros', async ({ page }) => {
    await page.goto('/relatorios/extrato');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('extrato deve exibir filtros de data', async ({ page }) => {
    await page.goto('/relatorios/extrato');
    await page.waitForTimeout(1500);
    const hasFilter = await page.locator('input[type="date"], select, [class*="filter"]').count();
    expect(hasFilter).toBeGreaterThan(0);
  });

  test('relatório IR completo deve carregar sem erros', async ({ page }) => {
    await page.goto('/relatorios/ir');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('relatório IR deve exibir DIRPF ou apuração', async ({ page }) => {
    await page.goto('/relatorios/ir');
    await page.waitForTimeout(1500);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/dirpf|declaração|bem|direito|apuração|ir/);
  });

  test('exportar CSV deve carregar sem erros', async ({ page }) => {
    await page.goto('/relatorios/exportar/csv');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    await expect(page).not.toHaveURL(/404/);
  });

  test('exportar CSV deve exibir botão de download', async ({ page }) => {
    await page.goto('/relatorios/exportar/csv');
    await page.waitForTimeout(1000);
    const body = await page.textContent('body');
    expect(body?.toLowerCase()).toMatch(/baixar|download|exportar|csv/);
  });

  test('relatórios não devem ter erros de console JS', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/relatorios/mensal');
    await page.waitForTimeout(1500);
    const critical = errors.filter(e => !e.includes('favicon') && !e.includes('net::ERR_'));
    expect(critical).toHaveLength(0);
  });
});
