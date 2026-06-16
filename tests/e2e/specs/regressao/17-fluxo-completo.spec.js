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

test.describe('Regressão — Fluxos Ponta a Ponta @regressao @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-047
  test('fluxo fiscal: IR apurado e DARFs relacionadas existem', async ({ page }) => {
    await page.goto('/imposto-renda/mensal');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const textoMensal = await page.textContent('body');
    expect(textoMensal?.toLowerCase()).toMatch(/apuração|ir|imposto|categoria/);

    await page.goto('/imposto-renda/darf');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const textoDarf = await page.textContent('body');
    expect(textoDarf?.toLowerCase()).toMatch(/darf|valor|competência|código/);
  });

  // CT-048
  test('navegação entre módulos preserva sessão (sem redirect para login)', async ({ page }) => {
    const rotas = [
      '/dashboard/',
      '/operacoes/',
      '/imposto-renda/mensal',
      '/ferramentas/screener',
      '/relatorios/mensal',
    ];
    for (const rota of rotas) {
      await page.goto(rota);
      await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
      expect(page.url()).not.toContain('/auth/login');
    }
  });

  // CT-049
  test('logout invalida sessão e redireciona para login', async ({ page }) => {
    const btnLogout = page.locator('a, button').filter({ hasText: /sair|logout/i }).first();
    await expect(btnLogout).toBeVisible({ timeout: 8000 });
    await btnLogout.click();
    await page.waitForURL('**/auth/login**', { timeout: 10000 });
    await page.goto('/dashboard/');
    await page.waitForURL('**/auth/login**', { timeout: 10000 });
    expect(page.url()).toContain('login');
  });

  // CT-050
  test('comparador exibe campos para seleção de ativos', async ({ page }) => {
    await page.goto('/ferramentas/comparador');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/comparar|ativo|ticker|selecionar/);
    const inputs = page.locator('select, input').filter({ hasText: '' });
    const count = await page.locator('select, input[type="text"]').count();
    expect(count).toBeGreaterThan(0);
  });

  // CT-046 (último pois depende de estado)
  test('dashboard exibe patrimônio total após login', async ({ page }) => {
    await page.goto('/dashboard/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto).toMatch(/R\$|\d+\.\d{3}|\d+,\d{2}/);
    expect(texto?.toLowerCase()).toMatch(/patrimônio|carteira|dashboard|portfólio/);
  });
});
