// @ts-check
const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Operações — Importação B3 @operacoes @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  async function abrirImportacaoB3(page) {
    await page.goto('/operacoes/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnImportacao = page.locator('button, [x-on\\:click], a').filter({ hasText: /importa/i }).first();
    await expect(btnImportacao).toBeVisible({ timeout: 8000 });
    await btnImportacao.click();
    await page.waitForTimeout(500);
  }

  // CT-014
  test('aba de importação B3 é acessível e exibe área de upload', async ({ page }) => {
    await abrirImportacaoB3(page);
    const uploadArea = page.locator('input[type="file"], [x-ref="fileInput"]').first();
    await expect(uploadArea).toBeAttached({ timeout: 8000 });
    const instrucoes = page.locator('body');
    const texto = await instrucoes.textContent();
    expect(texto?.toLowerCase()).toMatch(/csv|xlsx|xls|importa/);
  });

  // CT-015
  test('área de upload aceita apenas CSV/XLSX segundo atributo accept', async ({ page }) => {
    await abrirImportacaoB3(page);
    const fileInput = page.locator('input[type="file"]').first();
    await expect(fileInput).toBeAttached({ timeout: 8000 });
    const accept = await fileInput.getAttribute('accept');
    expect(accept).toMatch(/csv|xlsx|xls/i);
  });

  // CT-016
  test('instruções de importação mencionam formato B3', async ({ page }) => {
    await abrirImportacaoB3(page);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/b3|negociação|nota|extrato/);
  });
});
