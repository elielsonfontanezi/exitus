// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Alertas — Lógica e Sub-páginas @alertas @logica', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  });

  // CT-067 — Todos os alertas: lista do usuário
  test('página de alertas exibe lista de alertas do usuário', async ({ page }) => {
    await page.goto('/alertas/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/alerta|ticker|preço|notificação|ativo/);
  });

  // CT-068 — Todos os alertas: botão de criação
  test('alertas possui ação de criar novo alerta', async ({ page }) => {
    await page.goto('/alertas/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const btnNovo = page.locator('a, button').filter({ hasText: /novo|criar|adicionar/i }).first();
    await expect(btnNovo).toBeAttached({ timeout: 8000 });
  });

  // CT-069 — Alertas de Preço: rota carrega e exibe conteúdo relevante
  test('alertas de preço carrega sem erro e exibe dados', async ({ page }) => {
    await page.goto('/alertas/preco');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    expect(page.url()).not.toContain('/auth/login');
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/alerta|preço|ticker|valor|acima|abaixo/);
  });

  // CT-070 — Alertas de Dividendos: rota carrega e exibe conteúdo relevante
  test('alertas de dividendos carrega sem erro e exibe dados', async ({ page }) => {
    await page.goto('/alertas/dividendos');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    expect(page.url()).not.toContain('/auth/login');
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/alerta|dividendo|provento|yield|ativo/);
  });

  // CT-071 — Alertas Personalizados: rota carrega e exibe conteúdo relevante
  test('alertas personalizados carrega sem erro e exibe dados', async ({ page }) => {
    await page.goto('/alertas/personalizados');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    expect(page.url()).not.toContain('/auth/login');
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/alerta|personalizado|condição|regra|ativo/);
  });

  // CT-072 — Alertas: exibe status ativo/inativo
  test('alertas exibe indicador de status (ativo/inativo)', async ({ page }) => {
    await page.goto('/alertas/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(1000);
    const texto = await page.textContent('body');
    expect(texto?.toLowerCase()).toMatch(/ativo|inativo|status|habilitado|desabilitado|ligado|desligado/);
  });

  // CT-073 — Alertas: filtro ou busca por ticker presente
  test('alertas possui campo de busca ou filtro', async ({ page }) => {
    await page.goto('/alertas/');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
    const filtro = page.locator('input[type="search"], input[type="text"], select, [x-model*="filter"], [x-model*="busca"]').first();
    await expect(filtro).toBeAttached({ timeout: 8000 });
  });
});
