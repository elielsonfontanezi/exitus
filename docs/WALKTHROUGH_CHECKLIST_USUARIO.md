# Checklist Walkthrough — O que você deve verificar

**Data:** 02/07/2026 | **Cenário:** `test_menu_full` | **Login:** `e2e_user` / `e2e_senha_123`

**Correções 02/07/2026 (revalidar):** logout `/auth/logout`; dashboard % pt-BR + macro API; corretoras seed `e2e_user`; CRUD ícones; 9 fontes; portfolios sem duplicata; meta patrimônio BR; regras DAY_TRADE/US/EU.

Legenda de camadas da automação:
- **AUTO_OK** — página/redirect validado sem interação
- **AUTO_OK_VERIFY_UI** — API retornou dados; UI renderizada só no browser
- **NEEDS_MANUAL** — automação não conseguiu validar

Resumo: 45 telas | Obrigatório você: 16 | Recomendado: 7 | Amostra: 19 | Pode pular: 3

```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_menu_full
cd backend && python3 scripts/walkthrough_menu_browser.py
```

## 1. OBRIGATÓRIO — você deve abrir e validar

CRUD, formulários, download, admin ou falha de automação. **Sem isso não feche o gate Go-Live.**

| # | Tela | URL | Automação |
|---|------|-----|-----------|
| 3 | Config Perfil | `/configuracoes/perfil` | AUTO_OK_VERIFY_UI — shell OK |
| 4 | Config Corretoras | `/configuracoes/corretoras` | AUTO_OK_VERIFY_UI — API 200 dados |
| 5 | Operações | `/operacoes/` | AUTO_OK_VERIFY_UI — API 200 dados |
| 6 | Operações Venda | `/operacoes/?venda=true` | AUTO_OK_VERIFY_UI — API 200 dados |
| 14 | Proventos Calendário | `/proventos/calendario` | AUTO_OK_VERIFY_UI — API 200 dados |
| 28 | Relatório Exportar | `/relatorios/exportar` | AUTO_OK_VERIFY_UI — shell OK |
| 30 | Comparador | `/ferramentas/comparador` | AUTO_OK_VERIFY_UI — shell OK |
| 31 | Calculadora IR | `/ferramentas/calculadora-ir` | AUTO_OK_VERIFY_UI — shell OK |
| 35 | Alertas | `/alertas/` | AUTO_OK_VERIFY_UI — API 200 dados |
| 36 | Preço Teto | `/ferramentas/preco-teto` | AUTO_OK_VERIFY_UI — API 200 dados |
| 39 | Fontes Dados | `/configuracoes/fontes-dados` | AUTO_OK_VERIFY_UI — API 200 dados |
| 40 | Portfolios | `/configuracoes/portfolios` | AUTO_OK_VERIFY_UI — API 200 dados |
| 41 | Regras Fiscais | `/configuracoes/regras-fiscais` | AUTO_OK_VERIFY_UI — API 200 dados |
| 42 | Admin Usuários | `/admin/usuarios` | NEEDS_MANUAL — http://localhost:8080/auth/login |
| 44 | Projeções Patrimônio | `/analises/projecoes` | AUTO_OK_VERIFY_UI — API 200 dados |
| — | Carteira Câmbio | `/carteira/cambio` | AUTO_OK_VERIFY_UI — API 200 dados |

## 2. RECOMENDADO — gráficos e KPIs visuais

API OK; confirme que gráficos e cards exibem valores coerentes (não só que a página carregou).

| # | Tela | URL | Automação |
|---|------|-----|-----------|
| 2 | Dashboard | `/dashboard/` | AUTO_OK_VERIFY_UI — API 200 dados |
| 15 | Análises Evolução | `/analises/evolucao` | AUTO_OK_VERIFY_UI — API 200 dados |
| 16 | Análises Performance | `/analises/performance` | AUTO_OK_VERIFY_UI — API 200 dados |
| 17 | Análises Alocação | `/analises/alocacao` | AUTO_OK_VERIFY_UI — API 200 dados |
| 19 | Rentabilidade Período | `/analises/rentabilidade/periodo` | AUTO_OK_VERIFY_UI — API 200 dados |
| 37 | Correlação | `/analises/correlacao` | AUTO_OK_VERIFY_UI — API 200 dados |
| 43 | Análises Risco | `/analises/risco` | AUTO_OK_VERIFY_UI — API 200 dados |

## 3. AMOSTRA — confira 5–8 telas (listas read-only)

Automação confirmou API com dados. Faça amostragem: posições, histórico, IR, relatórios, screener, etc.

| # | Tela | URL | Automação |
|---|------|-----|-----------|
| 8 | Operações Histórico | `/operacoes/historico` | AUTO_OK_VERIFY_UI — API 200 dados |
| 9 | Carteira Posições | `/carteira/posicoes` | AUTO_OK_VERIFY_UI — API 200 dados |
| 10 | Carteira Movimentações | `/carteira/movimentacoes` | AUTO_OK_VERIFY_UI — API 200 dados |
| 11 | Ativos Catálogo | `/ativos/acoes` | AUTO_OK_VERIFY_UI — API 200 dados |
| 12 | Ativos Detalhe PETR4 | `/ativos/PETR4` | AUTO_OK_VERIFY_UI — API 200 dados |
| 13 | Eventos Corporativos | `/ativos/eventos-corporativos` | AUTO_OK_VERIFY_UI — API 200 dados |
| 18 | Buy Signals | `/analises/buy-signals` | AUTO_OK_VERIFY_UI — API 200 dados |
| 20 | IR Mensal | `/imposto-renda/mensal` | AUTO_OK_VERIFY_UI — API 200 dados |
| 21 | DARFs | `/imposto-renda/darfs` | AUTO_OK_VERIFY_UI — API 200 dados |
| 22 | IR Histórico | `/imposto-renda/historico` | AUTO_OK_VERIFY_UI — API 200 dados |
| 23 | DIRPF | `/imposto-renda/declaracao` | AUTO_OK_VERIFY_UI — API 200 dados |
| 24 | Relatório Mensal | `/relatorios/mensal` | AUTO_OK_VERIFY_UI — API 200 dados |
| 25 | Relatório Anual | `/relatorios/anual` | AUTO_OK_VERIFY_UI — API 200 dados |
| 26 | Relatório Extrato | `/relatorios/extrato` | AUTO_OK_VERIFY_UI — API 200 dados |
| 27 | Relatório IR | `/relatorios/ir` | AUTO_OK_VERIFY_UI — API 200 dados |
| 29 | Screener | `/ferramentas/screener` | AUTO_OK_VERIFY_UI — API 200 dados |
| 33 | Reconciliação | `/ferramentas/reconciliacao` | AUTO_OK_VERIFY_UI — API 200 dados |
| 34 | Planos | `/planos-compra/` | AUTO_OK_VERIFY_UI — API 200 dados |
| 38 | Projeções Renda | `/analises/projecoes/renda` | AUTO_OK_VERIFY_UI — API 200 dados |

## 4. PODE PULAR — já validado pela automação

Redirects e login; opcional rever em 30 segundos.

| # | Tela | URL | Automação |
|---|------|-----|-----------|
| 1 | Login | `/auth/login` | AUTO_OK — página pública |
| 19 | Rentabilidade legacy | `/analises/rentabilidade` | AUTO_OK — redirect período OK |
| 32 | Simulador | `/ferramentas/simulador` | AUTO_OK — redirect → http://localhost:8080/analises/projecoes |

## Admin (tela 42)

Use **`e2e_admin`** / `e2e_senha_123`. Se redirecionar para login, há bug em `require_admin` (`session.logged_in` vs `user_id`).
