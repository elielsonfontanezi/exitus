# Plano de Execução — 18/06/2026

> **Criado em:** 17/06/2026  
> **Branch atual:** `feature/frontend-gap-analysis`  
> **Versão:** v0.9.19  
> **Objetivo:** 3 atividades para finalizar frontend e mapear cobertura de APIs

---

## Atividade 1 — Migrar 2 templates finais para `base_interna.html`

**Branch:** `feature/migrate-base-interna-final` (a partir de `feature/frontend-gap-analysis`)

### Contexto
Os 2 últimos templates que herdam de `base.html` em vez de `base_interna.html`:
- `operacoes/operacoes.html` — 946 linhas (formulário compra/venda + import B3)
- `dashboard/index.html` — 647 linhas (dashboard principal)

Ambos já usam Alpine.js inline. A migração é estrutural (trocar base + reorganizar blocos).

### Passos
1. Ler `operacoes/operacoes.html` e mapear seções
2. Criar `operacoes/operacoes_v2.html` estendendo `base_interna.html`
3. Mover Alpine.js para `pageDataExtend()` e usar blocos padrão
4. Atualizar rota em `operacoes.py`
5. Testar fluxos: compra manual, venda, import B3
6. Repetir para `dashboard/index.html` → `dashboard/index_v2.html`
7. Testar dashboard: KPIs, gráficos, toggle moeda, alertas
8. Remover templates antigos
9. Atualizar docs + commit

### Riscos
- **Alto:** Formulário de operações é o fluxo mais crítico do sistema
- **Médio:** Dashboard tem gráficos e toggle de moeda que podem quebrar
- **Mitigação:** Testar cada fluxo individualmente antes de remover o antigo

### Estimativa
~2-3 horas de trabalho focado

---

## Atividade 2 — Walkthrough tela a tela (roteiro de uso)

**Branch:** Sem branch dedicada (é documentação pura)  
**Entregável:** `docs/WALKTHROUGH_USUARIO.md`

### Contexto
Criar um roteiro sequencial que simula o uso completo do sistema por um investidor real, passando por todas as telas na ordem lógica de uso.

### Roteiro proposto

| # | Módulo | URL | O que faz | APIs consumidas |
|---|--------|-----|-----------|-----------------|
| 1 | **Login** | `/login` | Autenticação | `/api/auth/login` |
| 2 | **Dashboard** | `/dashboard/` | Visão geral: patrimônio, alocação, top ativos | `/api/portfolios/dashboard`, `/api/alertas/recentes` |
| 3 | **Configurações** | `/configuracoes/perfil` | Editar perfil | `/api/auth/me` |
| 4 | **Corretoras** | `/configuracoes/corretoras` | CRUD corretoras | `/api/corretoras` |
| 5 | **Operações — Import B3** | `/operacoes/` | Upload CSV/Excel do Portal B3 | `/api/import/b3` |
| 6 | **Operações — Compra** | `/operacoes/` | Compra manual de ativo | `/api/transacoes`, `/api/ativos`, `/api/cotacoes` |
| 7 | **Operações — Venda** | `/operacoes/` | Venda com validação de posição | `/api/transacoes`, `/api/posicoes` |
| 8 | **Operações — Histórico** | `/operacoes/historico` | Lista de transações com filtros | `/api/transacoes` |
| 9 | **Carteira — Posições** | `/carteira/posicoes` | Posições atuais + resumo | `/api/posicoes`, `/api/posicoes/resumo` |
| 10 | **Carteira — Movimentações** | `/carteira/movimentacoes` | Depósitos/retiradas/caixa | `/api/movimentacoes-caixa`, `/api/carteira/saldo-caixa` |
| 11 | **Ativos — Catálogo** | `/ativos/acoes` | Lista por tipo (ações, FIIs, ETFs...) | `/api/ativos` |
| 12 | **Ativos — Detalhe** | `/ativos/<TICKER>` | Fundamentalistas, cotação, eventos | `/api/ativos/ticker`, `/api/cotacoes`, `/api/buy-signals/*` |
| 13 | **Ativos — Eventos** | `/ativos/eventos-corporativos` | Eventos corporativos | `/api/eventos-corporativos` |
| 14 | **Proventos — Calendário** | `/proventos/calendario` | Calendário + gerar automático | `/api/calendario-dividendos/*` |
| 15 | **Análises — Evolução** | `/analises/evolucao` | Evolução patrimonial | `/api/portfolios/evolucao` |
| 16 | **Análises — Performance** | `/analises/performance` | Rentabilidade, Sharpe, Drawdown | `/api/performance/performance` |
| 17 | **Análises — Alocação** | `/analises/alocacao` | Alocação por classe + desvio | `/api/portfolios/alocacao`, `/api/performance/desvio-alocacao` |
| 18 | **Análises — Buy Signals** | `/analises/buy-signals` | Top 10 oportunidades | `/api/buy-signals/watchlist-top` |
| 19 | **Análises — Rentabilidade** | `/analises/rentabilidade` | Por período + benchmark | `/api/portfolios/rentabilidade` |
| 20 | **Fiscal — IR Mensal** | `/imposto-renda/mensal` | Apuração mensal IR | `/api/ir/apuracao` |
| 21 | **Fiscal — DARFs** | `/imposto-renda/darfs` | DARFs geradas | `/api/ir/darf` |
| 22 | **Fiscal — Histórico** | `/imposto-renda/historico` | Histórico anual IR | `/api/ir/historico` |
| 23 | **Fiscal — DIRPF** | `/imposto-renda/declaracao` | Bens e direitos para declaração | `/api/ir/dirpf` |
| 24 | **Relatórios — Mensal** | `/relatorios/mensal` | Transações + proventos do mês | `/api/transacoes`, `/api/proventos` |
| 25 | **Relatórios — Anual** | `/relatorios/anual` | Resumo anual | `/api/transacoes`, `/api/proventos` |
| 26 | **Relatórios — Extrato** | `/relatorios/extrato` | Extrato de movimentações | `/api/transacoes`, `/api/proventos` |
| 27 | **Relatórios — IR Completo** | `/relatorios/ir` | Consolidação IR + DIRPF | `/api/ir/historico`, `/api/ir/dirpf`, `/api/ir/apuracao` |
| 28 | **Relatórios — Exportação** | `/relatorios/exportar` | CSV/Excel/PDF | `/api/export/*` |
| 29 | **Ferramentas — Screener** | `/ferramentas/screener` | Filtrar ativos por indicadores | `/api/ativos` |
| 30 | **Ferramentas — Comparador** | `/ferramentas/comparador` | Comparar até 3 ativos | `/api/ativos/ticker`, `/api/cotacoes` |
| 31 | **Ferramentas — Calculadora IR** | `/ferramentas/calculadora-ir` | Simular ganho/perda e IR | `/api/posicoes` |
| 32 | **Ferramentas — Simulador** | `/ferramentas/simulador` | Aportes com juros compostos | Client-side (sem API) |
| 33 | **Ferramentas — Reconciliação** | `/ferramentas/reconciliacao` | Diagnóstico de integridade | `/api/reconciliacao/*` |
| 34 | **Estratégia — Planos** | `/estrategia/planos` | Planos compra/venda unificados | `/api/plano-compra`, `/api/plano-venda` |
| 35 | **Alertas** | `/alertas/` | CRUD de alertas de preço | `/api/alertas` |

### Passos
1. Percorrer cada tela logado como `e2e_user`
2. Documentar o que aparece, como interagir, e se funciona
3. Capturar problemas encontrados
4. Gerar o documento final

### Estimativa
~1-2 horas

---

## Atividade 3 — Auditoria de APIs: cobertura frontend vs. backend

**Branch:** `feature/api-coverage-audit`  
**Entregável:** `docs/API_COVERAGE_AUDIT.md`

### Contexto
O backend tem **~103 endpoints de API** em 33 blueprints. O frontend consome **~42 endpoints** (~41%). Há **~61 APIs não utilizadas** pelo frontend.

### APIs NÃO utilizadas pelo frontend (inventário preliminar)

| Blueprint | Prefixo | Endpoints | Status Frontend |
|-----------|---------|-----------|-----------------|
| `calculos` | `/api/calculos/*` | 5 (portfolio, fii, preco_teto, rf/simular, rf/ticker) | ❌ Não usado |
| `cambio` | `/api/cambio/*` | 7 (converter, pares, taxa, atualizar, historico) | ⚠️ Parcial (só taxa-atual) |
| `portfolios` | `/api/portfolios/*` | 9 (dashboard, distribuicao/classes, distribuicao/setores, metricas-risco) | ⚠️ Parcial |
| `fontes-dados` | `/api/fontes-dados/*` | 6 (CRUD completo) | ❌ Não usado |
| `parametros-macro` | `/api/parametros-macro/*` | 3 (CRUD parâmetros macroeconômicos) | ❌ Não usado |
| `regras-fiscais` | `/api/regras-fiscais/*` | 2 (CRUD regras) | ❌ Não usado |
| `feriados` | `/api/feriados/*` | 2 (CRUD feriados) | ❌ Não usado |
| `cotacoes` | `/api/cotacoes/*` | 4 (batch, anomalias, health) | ⚠️ Parcial (só ticker) |
| `projecoes` | `/api/projecoes/*` | ? (projeções financeiras) | ❌ Não usado |
| `assessoras` | `/api/assessoras/*` | 3 (stats, toggle) | ⚠️ Só admin |
| `relatorios` | `/api/relatorios` | 1 (endpoint consolidado) | ❌ Não usado |
| `ativos` | `/api/ativos/*` | mercado, uuid | ⚠️ Parcial |
| `posicoes` | `/api/posicoes/*` | posicao_id (detalhe individual) | ⚠️ Parcial |
| `transacoes` | `/api/transacoes/*` | recentes, resumo-ativo | ⚠️ Parcial |

### Passos
1. Listar TODOS os endpoints do backend com método HTTP e parâmetros
2. Cruzar com chamadas `apiFetch`/`fetch` do frontend
3. Classificar cada API não usada:
   - **Integrar:** criar tela ou adicionar a tela existente
   - **Backend-only:** útil apenas para processamento interno
   - **Admin-only:** apenas painel admin
   - **Deprecar:** sem uso previsto, candidata a remoção
4. Propor novas telas ou expansões para APIs úteis
5. Gerar relatório final

### Estimativa
~2 horas

---

## Resumo de Execução

| # | Atividade | Branch | Estimativa | Dependência |
|---|-----------|--------|------------|-------------|
| 1 | Migrar 2 templates finais | `feature/migrate-base-interna-final` | 2-3h | Nenhuma |
| 2 | Walkthrough tela a tela | mesma branch ou sem branch | 1-2h | Após Ativ. 1 |
| 3 | Auditoria APIs | `feature/api-coverage-audit` | 2h | Independente |

**Total estimado:** 5-7 horas  
**Ordem sugerida:** 1 → 2 → 3 (ou 1 e 3 em paralelo, 2 ao final)

---

## Pré-requisitos

- Backend rodando em `localhost:5000` ✅
- Frontend rodando em `localhost:8080` ✅
- Usuário `e2e_user` / `e2e_senha_123` com dados seedados ✅
- Branch `feature/frontend-gap-analysis` commitada e limpa ✅
