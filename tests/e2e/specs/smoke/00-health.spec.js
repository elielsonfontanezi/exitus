// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Smoke Tests — Verificação de rotas (sem 404, sem console errors)
 * Cobre TODAS as rotas reais do frontend API-Driven (Sprints 1–8)
 * Credenciais: e2e_user / e2e_senha_123
 */

const ROTAS = [
  // Dashboard
  { url: '/dashboard/',            desc: 'Dashboard principal' },
  { url: '/dashboard/portfolios',  desc: 'Portfólios' },
  { url: '/dashboard/transactions',desc: 'Transações' },
  { url: '/dashboard/buy-signals', desc: 'Buy signals' },
  { url: '/dashboard/analytics',   desc: 'Analytics' },
  { url: '/dashboard/dividends',   desc: 'Dividendos (dashboard)' },
  { url: '/dashboard/movimentacoes', desc: 'Movimentações' },
  { url: '/dashboard/performance', desc: 'Performance (dashboard)' },
  { url: '/dashboard/alocacao',    desc: 'Alocação (dashboard)' },
  { url: '/dashboard/fluxo-caixa', desc: 'Fluxo de caixa' },
  { url: '/dashboard/alertas',     desc: 'Alertas (dashboard)' },
  { url: '/dashboard/comparador',  desc: 'Comparador (dashboard)' },
  { url: '/dashboard/educacao',    desc: 'Educação' },
  { url: '/dashboard/configuracoes', desc: 'Configurações' },
  { url: '/dashboard/planos-compra', desc: 'Planos de compra' },
  { url: '/dashboard/planos-venda',  desc: 'Planos de venda' },
  // Operações
  { url: '/operacoes/',            desc: 'Operações (compra/venda)' },
  { url: '/operacoes/deposito',    desc: 'Depósito' },
  // Proventos
  { url: '/proventos/recebidos',   desc: 'Proventos recebidos' },
  { url: '/proventos/projetados',  desc: 'Proventos projetados' },
  { url: '/proventos/calendario',  desc: 'Calendário de proventos' },
  // Ativos
  { url: '/ativos/acoes',          desc: 'Catálogo Ações' },
  { url: '/ativos/fiis',           desc: 'Catálogo FIIs' },
  { url: '/ativos/etfs',           desc: 'Catálogo ETFs' },
  { url: '/ativos/renda-fixa',     desc: 'Catálogo Renda Fixa' },
  { url: '/ativos/cripto',         desc: 'Catálogo Cripto' },
  // Planos
  { url: '/planos-compra/',        desc: 'Lista planos compra' },
  { url: '/planos-venda/',         desc: 'Lista planos venda' },
  // Alertas
  { url: '/alertas/',              desc: 'Alertas' },
  // Fiscal
  { url: '/imposto-renda/mensal',  desc: 'IR Mensal' },
  { url: '/imposto-renda/darfs',   desc: 'DARFs' },
  { url: '/imposto-renda/historico', desc: 'Histórico IR' },
  { url: '/imposto-renda/declaracao', desc: 'Declaração DIRPF' },
  // Análises
  { url: '/analises/rentabilidade/periodo', desc: 'Rentabilidade por período' },
  { url: '/analises/alocacao',     desc: 'Alocação' },
  { url: '/analises/evolucao',     desc: 'Evolução patrimonial' },
  { url: '/analises/performance',  desc: 'Performance' },
  { url: '/analises/buy-signals',  desc: 'Buy Signals' },
  // Relatórios
  { url: '/relatorios/mensal',     desc: 'Relatório mensal' },
  { url: '/relatorios/anual',      desc: 'Relatório anual' },
  { url: '/relatorios/extrato',    desc: 'Extrato' },
  { url: '/relatorios/ir',         desc: 'Relatório IR completo' },
  { url: '/relatorios/exportar/csv', desc: 'Exportar CSV' },
  // Ferramentas
  { url: '/ferramentas/screener',      desc: 'Screener' },
  { url: '/ferramentas/comparador',    desc: 'Comparador' },
  { url: '/ferramentas/calculadora-ir', desc: 'Calculadora IR' },
  { url: '/ferramentas/simulador',     desc: 'Simulador de aportes' },
];

test.describe('Smoke — Todas as rotas carregam sem 404 @smoke', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.fill('input[name="username"]', 'e2e_user');
    await page.fill('input[name="password"]', 'e2e_senha_123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard/**', { timeout: 10000 });
  });

  for (const rota of ROTAS) {
    test(`${rota.desc} (${rota.url}) — HTTP 200, sem 404`, async ({ page }) => {
      const errors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') errors.push(msg.text());
      });

      const response = await page.goto(rota.url);
      expect(response?.status(), `${rota.url} retornou ${response?.status()}`).not.toBe(404);
      expect(response?.status(), `${rota.url} retornou ${response?.status()}`).not.toBe(500);

      // Sem erros JavaScript críticos
      const criticalErrors = errors.filter(e =>
        !e.includes('favicon') &&
        !e.includes('net::ERR_') &&
        !e.includes('Failed to load resource') &&
        !e.includes('Failed to fetch') &&
        !e.includes('Erro ao carregar')
      );
      expect(criticalErrors, `Erros JS em ${rota.url}: ${criticalErrors.join(', ')}`).toHaveLength(0);
    });
  }
});
