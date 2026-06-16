// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Testes de Autenticação
 * Cobre: login, logout, redirect não autenticado, sessão
 */

test.describe('Auth — Login e Sessão @auth', () => {

  test('deve exibir tela de login', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('deve redirecionar / para /auth/login quando não autenticado', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/auth\/login/);
  });

  test('deve redirecionar /dashboard/ para /auth/login quando não autenticado', async ({ page }) => {
    await page.goto('/dashboard/');
    await expect(page).toHaveURL(/auth\/login/);
  });

  test('deve redirecionar rota protegida para login quando não autenticado', async ({ page }) => {
    await page.goto('/operacoes/');
    await expect(page).toHaveURL(/auth\/login/);
  });

  test('deve rejeitar credenciais inválidas', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'usuario_inexistente');
    await page.fill('input[name="password"]', 'senha_errada');
    await page.click('button[type="submit"]');
    // Deve permanecer na tela de login
    await expect(page).toHaveURL(/auth\/login/);
  });

  test('deve autenticar e2e_user com sucesso', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
    await expect(page).toHaveURL(/dashboard/);
  });

  test('deve autenticar e2e_admin com sucesso', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'e2e_admin');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
    await expect(page).toHaveURL(/dashboard/);
  });

  test('deve fazer logout e redirecionar para login', async ({ page }) => {
    // Login
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });

    // Logout
    await page.goto('/auth/logout');
    await expect(page).toHaveURL(/auth\/login/);
  });

  test('deve persistir sessão após reload da página', async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });

    // Reload e verificar que ainda está autenticado
    await page.reload();
    await expect(page).not.toHaveURL(/auth\/login/);
    await expect(page).toHaveURL(/dashboard/);
  });

  test('/health deve retornar status ok sem autenticação', async ({ page }) => {
    const response = await page.goto('/health');
    expect(response?.status()).toBe(200);
    const body = await page.textContent('body');
    expect(body).toContain('ok');
  });
});
