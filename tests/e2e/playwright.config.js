// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Configuração Playwright — Testes E2E v2 (Frontend API-Driven)
 *
 * Credenciais de teste:
 *   e2e_user  / e2e_senha_123  — usuário padrão (fluxos completos)
 *   e2e_admin / e2e_senha_123  — administrador (funcionalidades admin)
 *
 * Estrutura de specs:
 *   specs/smoke/       — todas as rotas carregam (sem 404, sem console errors)
 *   specs/auth/        — login, logout, sessão, redirect
 *   specs/operacoes/   — compra, venda, depósito, importação B3
 *   specs/portfolio/   — dashboard, portfólios, posições, proventos
 *   specs/fiscal/      — IR mensal, DARFs, histórico, declaração DIRPF
 *   specs/relatorios/  — mensal, anual, extrato, IR completo, exportar CSV
 *   specs/ferramentas/ — screener, comparador, calculadora IR, simulador
 *   specs/regressao/   — fluxos ponta-a-ponta e navegação global
 *
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './specs',

  /* Timeout para cada teste */
  timeout: 30 * 1000,

  /* Configuração de expect */
  expect: {
    timeout: 8000
  },

  /* Executar testes em paralelo */
  fullyParallel: false,

  /* Falhar build se houver testes com .only */
  forbidOnly: !!process.env.CI,

  /* Retry em caso de falha */
  retries: process.env.CI ? 2 : 1,

  /* Workers: sequencial por padrão (evita conflito de sessão) */
  workers: process.env.CI ? 1 : 2,

  /* Reporter */
  reporter: [
    ['html', { outputFolder: 'reports/html', open: 'never' }],
    ['json', { outputFile: 'reports/results.json' }],
    ['junit', { outputFile: 'reports/junit.xml' }],
    ['list']
  ],

  /* Configuração compartilhada para todos os projetos */
  use: {
    /* URL base — frontend na porta 8080 */
    baseURL: process.env.BASE_URL || 'http://localhost:8080',

    /* Coletar trace em caso de falha */
    trace: 'on-first-retry',

    /* Screenshot em caso de falha */
    screenshot: 'only-on-failure',

    /* Vídeo em caso de falha */
    video: 'retain-on-failure',

    /* Timeouts */
    navigationTimeout: 15000,
    actionTimeout: 8000,
  },

  /* Projetos de teste */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  /* Servidor de desenvolvimento — reutiliza instância existente */
  webServer: {
    command: 'echo "Usando servidor existente em http://localhost:8080"',
    url: 'http://localhost:8080',
    reuseExistingServer: true,
    timeout: 5 * 1000,
  },
});
