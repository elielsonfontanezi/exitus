// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Configuração Playwright para testes E2E do Frontend V2.0
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './specs',
  
  /* Timeout para cada teste */
  timeout: 30 * 1000,
  
  /* Configuração de expect */
  expect: {
    timeout: 5000
  },
  
  /* Executar testes em paralelo */
  fullyParallel: true,
  
  /* Falhar build se houver testes com .only */
  forbidOnly: !!process.env.CI,
  
  /* Retry em caso de falha */
  retries: process.env.CI ? 2 : 0,
  
  /* Workers paralelos */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter */
  reporter: [
    ['html', { outputFolder: 'reports/html' }],
    ['json', { outputFile: 'reports/results.json' }],
    ['junit', { outputFile: 'reports/junit.xml' }],
    ['list']
  ],
  
  /* Configuração compartilhada para todos os projetos */
  use: {
    /* URL base */
    baseURL: process.env.BASE_URL || 'http://localhost:8080',
    
    /* Coletar trace em caso de falha */
    trace: 'on-first-retry',
    
    /* Screenshot em caso de falha */
    screenshot: 'only-on-failure',
    
    /* Vídeo em caso de falha */
    video: 'retain-on-failure',
    
    /* Timeout de navegação */
    navigationTimeout: 10000,
    
    /* Timeout de ação */
    actionTimeout: 5000,
  },

  /* Configurar projetos para múltiplos browsers */
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
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Testes Mobile */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Testes Tablet */
    {
      name: 'iPad',
      use: { ...devices['iPad Pro'] },
    },
  ],

  /* Servidor de desenvolvimento */
  webServer: {
    command: 'echo "Usando servidor existente em http://localhost:8080"',
    url: 'http://localhost:8080',
    reuseExistingServer: true,
    timeout: 5 * 1000,
  },
});
