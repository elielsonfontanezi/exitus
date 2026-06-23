# Frontend GAP Analysis — Sistema Exitus

**Branch:** `feature/frontend-gap-analysis`  
**Data:** 16/06/2026  
**Versão:** v1.0  
**Objetivo:** Mapear cada grupo de APIs disponíveis no backend contra o que o frontend expõe hoje, identificar GAPs e propor telas novas ou expansões de telas existentes.

> **Metodologia:** APIs são o inventário. Telas são o produto.
> O estudo parte das APIs (o que foi pensado para o frontend) e determina onde cada capacidade aterra — em tela existente ou nova.

---

## �️ Plano de Execução por Fases

> Status atualizado: **18/06/2026** — Fix visual: `operacoes_v2.html` + `dashboard/index_v2.html` padronizados com `exitus-components.css` (sem CSS custom)

### ✅ Fase 1 — Correções urgentes no menu (CONCLUÍDA — 16/06/2026)
*Sem novas telas, só reorganização do `menu_horizontal.html`.*

- [x] Remover "Planos" do menu (links 404)
- [x] Mover "Alertas" para o sino do header
- [x] Elevar "Fiscal" de sub-item de Análises para nível 1
- [x] Elevar "Proventos" de sub-item de Análises para nível 1
- [x] Criar "Carteira" como item nível 1 (Posições + Movimentações)
- [x] Expandir "Operações" com item Histórico
- [x] Adicionar "Reconciliação" em Ferramentas
- [x] Corrigir `/perfil` → `/configuracoes/perfil` e `/configuracoes` → `/configuracoes/corretoras`

---

### ✅ Fase 2 — Dashboard reformulado (CONCLUÍDA — 17/06/2026)
*Atualizar o template `dashboard/index.html` para usar dados que a API já retorna mas o template ignora.*

> **Nota:** inspeção mostrou que o dashboard já entrega mais do que o esperado.
> Itens G18 (Top 5 por mercado ✅, toggle BRL/USD ✅, alertas recentes ✅, alocação pizza ✅) já implementados.

- [x] Confirmar quais seções do dashboard ainda estão incompletas → removidos 5 cards com dados falsos
- [x] Renderizar `alocacao_geografica` no gráfico pizza (BR/US/INTL) → já estava funcionando
- [x] Verificar se toggle BRL/USD está funcional → funcional (toggleMoeda)
- [x] Remover botões de ação rápida (Nova Operação, Vender, Depositar, Ver Análises)

---

### ✅ Fase 2.5 — Padronização Visual (CONCLUÍDA — 17/06/2026)
*Criar base template e CSS compartilhado para que todas as telas novas nasçam no padrão Investidor10.*

> **Investigação realizada em 17/06/2026** — Telas analisadas no Investidor10:
> Carteira/Resumo, Proventos, Gráficos, Análise, Lançamentos, Metas, Ações (PETR4), FIIs.

#### Padrões visuais do Investidor10 a replicar:

| Elemento | Padrão Investidor10 | Nosso estado atual |
|----------|--------------------|--------------------|
| **Header de métricas** | Barra escura fixa com 3-4 KPIs condensados | ✅ Já temos (resumo-patrimonio) |
| **Abas internas** | Barra horizontal de abas por módulo | ❌ Não temos — cada tela é isolada |
| **Tabelas** | Sem borda lateral, header fixo, hover sutil, cores verde/vermelho | ⚠️ Parcial |
| **Filtros** | Dropdowns inline acima da tabela (período, tipo, ativo) | ❌ Ausentes |
| **Gráficos** | Barras + linhas sobrepostas, legenda acima, sem moldura | ⚠️ Parcial |
| **Fundo** | Branco puro `#fff` com separação por espaçamento | ⚠️ Usamos `#f8f9fa` |
| **Cards** | Mínimo de sombra, separação por espaço branco | ⚠️ Usamos sombra |
| **Ações por linha** | Botão `⋯` contextual | ❌ Não temos |
| **Progresso** | Barra horizontal com % e valores | ✅ Meta de patrimônio |

#### Artefatos criados:

- [x] **`templates/components/base_interna.html`** — extends `base.html`, inclui:
  - CSS do design system (classes compartilhadas)
  - Componente de abas reutilizável (bloco `tabs`)
  - Componente de filtros inline (bloco `filters`)
  - Padrão de tabela (`.data-table`)
  - Loading skeleton padrão
  - Helpers JS: `apiFetch()`, `formatMoney()`, `formatPercent()`, `formatDate()`
- [x] **`static/css/exitus-components.css`** — 400+ linhas com componentes:
  - `.kpi-bar` / `.kpi-card` / `.section-box` / `.data-table`
  - `.tab-bar` / `.tab-item` / `.tab-item.active`
  - `.filter-bar` / `.filter-select` / `.filter-input`
  - `.badge-positivo` / `.badge-negativo` / `.badge-neutro`
  - `.action-menu` / `.action-menu-btn` / `.action-menu-dropdown`
  - `.btn-exitus-primary` / `.btn-exitus-outline` / `.btn-exitus-ghost`
  - `.progress-bar-container` / `.progress-bar-fill`
  - `.empty-state` / `.skeleton-line` / `.skeleton-card`
- [x] Paleta documentada no topo do CSS como variáveis `--exitus-*`
- [x] CSS incluído globalmente via `base.html`

#### Decisões de design:

1. **Fundo:** Manter `#f8f9fa` (diferencia do Investidor10 propositalmente — nosso é mais acolhedor)
2. **Sombra:** Reduzir para `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` (mais sutil)
3. **Abas:** Adotar em todas as telas que tenham sub-seções (Carteira, Análises, Fiscal)
4. **Tabelas:** Adotar padrão sem borda lateral, com hover e ações `⋯`
5. **Cor primária:** Manter `#a38c65` — já é idêntico ao Investidor10

---

### 🎯 Fase 3 — Telas novas (PRÓXIMA)
*APIs prontas no backend, telas inexistentes no frontend. Usar `base_interna.html`.*

- [x] **`carteira.py`** → `/carteira/posicoes` (G4) + `/carteira/movimentacoes` (G6) ✅ 17/06/2026
- [x] **`configuracoes.py`** → `/configuracoes/perfil` (G1) + `/configuracoes/corretoras` (G1) ✅ 17/06/2026
- [x] **`/operacoes/historico`** → histórico de transações com filtros (G5) ✅ 17/06/2026
- [x] **`/ferramentas/reconciliacao`** → painel diagnóstico de integridade (G14) ✅ 17/06/2026

---

### 🟡 Fase 4 — Expansões de telas existentes
*Telas existem, mas usam parcialmente as APIs disponíveis.*

- [x] **Alertas** → criar / toggle ativo-inativo / excluir (G9) ✅ 17/06/2026
- [x] **Exportação** → seletor formato + entidades (CSV/Excel/PDF) (G13) ✅ 17/06/2026
- [x] **Buy Signals** → Watchlist Top 10 + Z-Score + Margem Segurança (G8) ✅ 17/06/2026
- [x] **Calendário de Proventos** → botão gerar automático + confirmar pagamento (G7/G16) ✅ 17/06/2026
- [x] **Rentabilidade** → seletor de período + seletor de benchmark (G12) ✅ 17/06/2026

---

### ✅ Fase 5 — Melhorias de menor prioridade (CONCLUÍDA)
*Todas implementadas com APIs reais.*

- [x] Detalhe de ativo com fundamentalistas (G3) ✅ 17/06/2026
- [x] DIRPF — bens e direitos com dados reais (G11) ✅ 17/06/2026
- [x] Eventos corporativos no detalhe do ativo (G15) ✅ 17/06/2026
- [x] Planos de compra/venda — APIs corrigidas + tela unificada (G10) ✅ 17/06/2026

---

### ✅ Fase 6 — Unificação e Limpeza de Templates (17/06/2026)
*Migrar todas as telas restantes para `base_interna.html` + Alpine.js. Remover templates redundantes.*

**Parte A — Remover 8 templates redundantes** (já substituídos por versões novas):
- [x] `dashboard/alertas.html` → redirecionar para `/alertas/`
- [x] `dashboard/buy_signals.html` → redirecionar para `/analises/buy-signals`
- [x] `dashboard/planos_compra.html` → redirecionar para `/planos-compra/`
- [x] `dashboard/planos_compra_novo.html` → redirecionar para `/planos-compra/`
- [x] `dashboard/planos_compra_detalhes.html` → redirecionar para `/planos-compra/`
- [x] `dashboard/planos_venda.html` → redirecionar para `/planos-compra/` (aba venda)
- [x] `dashboard/proventos_calendario.html` → redirecionar para `/proventos/calendario`
- [x] `dashboard/comparador.html` → redirecionar para `/ferramentas/comparador`

**Parte B — Migrar 15 telas para base_interna.html + Alpine.js:**
- [x] Ferramentas (4): screener, comparador, calculadora-ir, simulador
- [x] Fiscal (3): ir_mensal, darfs, historico
- [x] Relatórios (4): mensal, anual, extrato, ir_completo
- [x] Análises (3): evolucao, performance, alocacao
- [x] Ativos (1): lista.html (catálogo por tipo)

**Parte C — Migrados na Fase 7 (18/06/2026):**
- [x] Operações (1): `operacoes_v2.html` — compra/venda, import B3, busca Alpine.js puro
- [x] Dashboard (1): `index_v2.html` — KPIs, Chart.js, multi-mercado, benchmark

> ✅ **100% dos templates ativos herdam de `base_interna.html`** — migração de base concluída.

---

### ✅ Fase 7 — Migração Final para base_interna.html (18/06/2026)
*Migrar os 2 últimos templates que ainda herdavam de `base.html`.*

- [x] `operacoes/operacoes.html` → `operacoes_v2.html` + rota simplificada (server-side fetch removido)
- [x] `dashboard/index.html` → `index_v2.html` + rota simplificada
- [x] Templates antigos removidos (2 arquivos: 946 + 647 linhas)

---

## 📋 Índice de Grupos

| # | Grupo | APIs disponíveis | Frontend atual | GAPs | Prioridade |
|---|-------|-----------------|----------------|------|-----------|
| G1 | Auth + Usuário + Corretoras | 6 endpoints | ✅ Login, registro, perfil, corretoras CRUD | ✅ **Implementado Fase 3** | — |
| G2 | Cotações em Tempo Real | 4 endpoints | ⚠️ Usado internamente | 🟡 Widget provider/TTL + badge fallback header | Média |
| G3 | Ativos — Catálogo | 3 endpoints | ✅ Lista + detalhe com fundamentalistas | ✅ **Implementado Fase 5** | — |
| G4 | Posições — Carteira | 4 endpoints | ✅ `/carteira/posicoes` com filtros + resumo | 🟡 Botão recalcular posições pendente | Média |
| G5 | Transações | 2 endpoints | ✅ `/operacoes/historico` com filtros | 🟡 Editar/excluir transação pendente | Baixa |
| G6 | Movimentações de Caixa | 2 endpoints | ✅ `/carteira/movimentacoes` + saldo por corretora | ✅ **Implementado Fase 3** | — |
| G7 | Proventos + Calendário | 8 endpoints | ✅ Recebidos, projetados, calendário | 🟡 Botão gerar auto + confirmar pagamento + badges status | Média |
| G8 | Buy Signals | 4 endpoints | ✅ Busca ticker + score + margem + watchlist Top 10 | 🟡 Z-Score + badge sinal COMPRAR/AGUARDAR/VENDER | Baixa |
| G9 | Alertas | 5 endpoints | ✅ CRUD completo: criar, toggle, excluir, feed recentes | ✅ **Implementado Fase 4** | — |
| G10 | Planos de Compra/Venda | - | ✅ Tela unificada com APIs corrigidas | ✅ **Implementado Fase 5** (APIs limitadas) | — |
| G11 | IR / Fiscal | 3 endpoints | ✅ Apuração, DARFs, histórico, DIRPF com bens reais | 🟡 Seletor mês/ano visual na apuração | Baixa |
| G12 | Rentabilidade + Performance | 3 endpoints | ✅ TWR/MWR + seletor benchmark + seletor período | ✅ **Implementado Fase 4** | — |
| G13 | Relatórios + Exportação | 6 endpoints | ✅ CSV/Excel/PDF + seletor formato + entidades | ✅ **Implementado Fase 4** | — |
| G14 | Reconciliação | 4 endpoints | ✅ `/ferramentas/reconciliacao` — diagnóstico completo | ✅ **Implementado Fase 3** | — |
| G15 | Eventos Corporativos | 6 endpoints | ✅ Exibidos no detalhe do ativo | ✅ **Implementado Fase 5** | — |
| G16 | Calendário de Dividendos | 6 endpoints | ✅ Gerar automático + confirmar pagamento + badges | ✅ **Implementado Fase 4** | — |
| G17 | Carteira — Saldo Caixa | 1 endpoint | ✅ Dashboard + toggle BRL/USD implementado | ✅ **Implementado Fase 7** | — |
| G18 | Dashboard Consolidado | 3 endpoints | ✅ Top 5 por mercado + alocação geo + toggle BRL/USD | ✅ **Implementado Fase 7** | — |

> *G10 — APIs de planos com funcionalidade limitada; CRUD completo aguarda APIs adicionais no backend.

---

## G1 — Auth + Usuário + Corretoras

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/auth/login` | POST | Autenticar e obter JWT |
| `/api/auth/register` | POST | Registrar usuário |
| `/api/usuarios/{id}` | GET/PUT | Perfil do usuário |
| `/api/corretoras` | GET/POST | Lista e criação de corretoras |
| `/api/corretoras/{id}` | GET/PUT/DELETE | CRUD de corretora |

### Frontend Atual
- ✅ `/auth/login` — tela de login funcional
- ✅ `/auth/register` — tela de registro
- ✅ `/configuracoes/perfil` — editar nome, email, senha (**Fase 3 — 17/06/2026**)
- ✅ `/configuracoes/corretoras` — CRUD corretoras (**Fase 3 — 17/06/2026**)

### Status
✅ **G1 CONCLUÍDO** — todas as telas implementadas em Fase 3.

---

## G2 — Cotações em Tempo Real

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/cotacoes/{ticker}` | GET | Cotação individual com provider + cache TTL |
| `/api/cotacoes/batch?symbols=X,Y` | GET | Cotações em lote (máx 10 tickers) |
| `/api/cotacoes/health` | GET | Status do módulo de cotações |

### Frontend Atual
- ⚠️ Cotações usadas internamente (compra, ativos catálogo) mas sem tela dedicada
- ❌ Sem indicação visual do provider (brapi.dev / yfinance / database_cache)
- ❌ Sem aviso de fallback quando APIs externas falham

### GAPs Identificados
1. **Widget de cotação** no detalhe de ativo — ticker, preço, provider, TTL restante
2. **Indicador de saúde das cotações** — badge no header quando em fallback
3. **Batch em screener** — carregar cotações de múltiplos tickers em paralelo

### Proposta
```
Expansão da tela /ativos/catalogo/detalhe  → widget cotação com provider badge
Expansão do /ferramentas/screener          → cotações batch por ticker
Header global                               → badge ⚠️ quando provider=database_fallback
```

---

## G3 — Ativos — Catálogo

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/ativos` | GET | Lista paginada com filtros (ticker, tipo, mercado) |
| `/api/ativos/{id}` | GET | Detalhe com fundamentalistas (DY, P/L, P/VP, ROE) |
| `/api/ativos` | POST | Criar ativo (admin only) |

### Frontend Atual
- ✅ `/ativos/` — lista por categoria com filtros (Ações, FIIs, ETFs, RF, Cripto)
- ⚠️ Detalhe do ativo — redireciona para dashboard, não usa `GET /api/ativos/{id}`
- ❌ Fundamentalistas não exibidos (DY, P/L, P/VP, ROE, cap_rate)

### GAPs Identificados
1. **Tela de detalhe real** do ativo com dados fundamentalistas
2. **Filtro por mercado** (BR/US/INTL) não exposto na UI
3. **Cotação ao vivo** integrada no detalhe (G2 + G3 juntos)

### Proposta de Tela Nova
```
/ativos/detalhe/{ticker}  → Dados fundamentalistas + cotação + posição do usuário nesse ativo
```
**Blueprint:** expansão de `ativos_catalogo.py`

---

## G4 — Posições — Carteira

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/posicoes` | GET | Lista posições com filtros (ticker, corretora, lucro_positivo) |
| `/api/posicoes/{id}` | GET | Detalhe de posição individual |
| `/api/posicoes/resumo` | GET | Resumo consolidado (total investido, ROI) |
| `/api/posicoes/calcular` | POST | Recalcular posições a partir das transações |

### Frontend Atual
- ✅ `/carteira/posicoes` — lista com filtros (ticker, tipo, corretora, lucro_positivo), resumo ROI (**Fase 3 — 17/06/2026**)
- ✅ `GET /api/posicoes/resumo` — card de resumo na tela de posições
- ❌ `POST /api/posicoes/calcular` — botão recalcular ainda sem UI

### GAPs Restantes
1. **Botão "Recalcular Posições"** — integrar em `/carteira/posicoes` ou `/ferramentas/reconciliacao`

### Status
🟡 **G4 PARCIALMENTE CONCLUÍDO** — tela principal implementada; botão recalcular pendente (Média prioridade).

---

## G5 — Transações

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/transacoes` | GET | Histórico paginado com filtros |
| `/api/transacoes` | POST | Nova transação (compra, venda, dividendo, etc.) |
| `/api/transacoes/{id}` | PUT | Editar transação |
| `/api/transacoes/{id}` | DELETE | Excluir transação |
| `/api/transacoes/recentes` | GET | Últimas N transações (dashboard) |

### Frontend Atual
- ✅ `POST /api/transacoes` — via tela `/operacoes/` (compra + venda unificada)
- ✅ `/operacoes/historico` — tabela paginada com filtros (período, tipo, ativo, corretora) (**Fase 3 — 17/06/2026**)
- ❌ Editar/excluir transação — sem ação na UI

### GAPs Restantes
1. **Editar transação** — formulário inline ou modal
2. **Excluir transação** — com confirmação

### Status
🟡 **G5 PARCIALMENTE CONCLUÍDO** — histórico implementado; editar/excluir pendentes (Baixa prioridade).

---

## G6 — Movimentações de Caixa

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/movimentacoes` | GET | Lista com filtros (corretora, período) |
| `/api/movimentacoes/saldo/{corretora_id}` | GET | Saldo calculado por corretora |

### Frontend Atual
- ✅ `/carteira/movimentacoes` — tabela filtrada + saldo por corretora + resumo período (**Fase 3 — 17/06/2026**)

### Status
✅ **G6 CONCLUÍDO** — tela completa implementada em Fase 3.

---

## G7 — Proventos + Calendário de Dividendos

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/proventos` | GET | Lista proventos recebidos |
| `/api/proventos/calendario` | GET | Calendário de proventos |
| `/calendario-dividendos/` | GET | Lista com filtros avançados |
| `/calendario-dividendos/resumo` | GET | Estatísticas mensais por ativo |
| `/calendario-dividendos/gerar` | POST | Gerar calendário automático |
| `/calendario-dividendos/{id}/confirmar-pagamento` | POST | Confirmar pagamento real |
| `/calendario-dividendos/{id}` | PUT | Atualizar item do calendário |

### Frontend Atual
- ✅ `/proventos/recebidos` — lista proventos recebidos
- ✅ `/proventos/projetados` — proventos projetados + card resumo estimado vs. real
- ✅ `/proventos/calendario` — calendário com botão "Gerar automático" + confirmar pagamento + badges status previsto/confirmado/pago (**Fase 4 — 17/06/2026**)

### GAPs Restantes
1. **`GET /calendario-dividendos/resumo`** — estatísticas mensais/por ativo não exibidas (nice-to-have)

### Status
✅ **G7 CONCLUÍDO** — todos os GAPs críticos implementados em Fase 4.

---

## G8 — Buy Signals

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/buy-signals/buy-score/{ticker}` | GET | Score 0-100 |
| `/api/buy-signals/margem-seguranca/{ticker}` | GET | Margem de segurança + sinal |
| `/api/buy-signals/zscore/{ticker}` | GET | Z-Score estatístico |
| `/api/buy-signals/watchlist-top` | GET | Top 10 ativos por score |

### Frontend Atual
- ✅ `/analises/buy-signals` — busca por ticker, score, margem + seção Watchlist Top 10 (**Fase 4 — 17/06/2026**)
- ❌ Z-Score — não exibido na tela atual
- ❌ Badge sinal COMPRAR/AGUARDAR/VENDER — não implementado

### GAPs Restantes
1. **Z-Score** — exibir como indicador adicional no detalhe
2. **Badge sinal** COMPRAR/AGUARDAR/VENDER com cor semântica

### Status
🟡 **G8 PARCIALMENTE CONCLUÍDO** — Watchlist Top 10 implementada; Z-Score + badge sinal pendentes (Baixa prioridade).

---

## G9 — Alertas

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/alertas` | GET | Lista alertas do usuário |
| `/api/alertas` | POST | Criar novo alerta |
| `/api/alertas/{id}/toggle` | PATCH | Ativar/desativar |
| `/api/alertas/{id}` | DELETE | Remover alerta |
| `/api/alertas/recentes` | GET | Últimos N alertas disparados |

### Frontend Atual
- ✅ `/alertas/` — CRUD completo: criar, toggle ativo/inativo, excluir, feed de recentes (**Fase 4 — 17/06/2026**)
- ✅ Sub-páginas `/alertas/preco`, `/alertas/dividendos`, `/alertas/personalizados`

### Status
✅ **G9 CONCLUÍDO** — todos os GAPs de interação implementados em Fase 4.

---

## G10 — Planos de Compra/Venda

### Frontend Atual
- ✅ Tela unificada planos compra + venda com APIs corrigidas (**Fase 5 — 17/06/2026**)
- ⚠️ CRUD completo de planos aguarda APIs adicionais no backend

### Status
🟡 **G10 PARCIALMENTE CONCLUÍDO** — tela implementada com APIs disponíveis; CRUD completo depende de expansão do backend.

---

## G11 — IR / Fiscal

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/ir/apuracao?mes=YYYY-MM` | GET | Apuração mensal por categoria |
| `/api/ir/darf?mes=YYYY-MM` | GET | DARFs do mês |
| `/api/ir/historico?ano=YYYY` | GET | Resumo anual 12 meses |

### Frontend Atual
- ✅ `/imposto-renda/mensal` — apuração mensal
- ✅ `/imposto-renda/darfs` — DARFs
- ✅ `/imposto-renda/historico` — histórico anual
- ✅ `/imposto-renda/declaracao` — DIRPF com bens e direitos com valores reais da API (**Fase 5 — 17/06/2026**)
- ❌ Seletor de mês/ano visual na apuração — ainda usa parâmetro URL

### GAPs Restantes
1. **Seletor de mês/ano visual** na tela de apuração (datepicker)

### Status
🟡 **G11 PARCIALMENTE CONCLUÍDO** — DIRPF implementado; seletor visual pendente (Baixa prioridade).

---

## G12 — Rentabilidade + Performance

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/portfolios/rentabilidade?periodo=X&benchmark=Y` | GET | TWR, MWR, alpha vs benchmark |
| `/api/portfolios/evolucao?meses=N` | GET | Evolução patrimonial histórica |
| `/api/portfolios/alocacao` | GET | Alocação geográfica e por tipo |

### Frontend Atual
- ✅ `/analises/rentabilidade` — TWR/MWR + seletor benchmark (CDI/IBOV/IFIX/SP500) + seletor período (1m/3m/6m/12m) (**Fase 4 — 17/06/2026**)
- ✅ `/analises/alocacao` — alocação visual
- ✅ `/analises/evolucao` — gráfico de evolução

### Status
✅ **G12 CONCLUÍDO** — todos os GAPs implementados em Fase 4.

---

## G13 — Relatórios + Exportação

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/export/transacoes?formato=csv\|excel\|json\|pdf` | GET | Exportar transações |
| `/api/export/proventos?formato=X` | GET | Exportar proventos |
| `/api/export/posicoes?formato=X` | GET | Exportar posições |

### Frontend Atual
- ✅ `/relatorios/exportar` — seletor formato (CSV/Excel/PDF) + entidades (transações/proventos/posições) + filtros período/ativo/corretora (**Fase 4 — 17/06/2026**)

### Status
✅ **G13 CONCLUÍDO** — exportação unificada implementada em Fase 4.

---

## G14 — Reconciliação

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/reconciliacao/verificar` | GET | Verificação completa (posições, saldos, integridade) |
| `/api/reconciliacao/posicoes` | GET | Apenas posições |
| `/api/reconciliacao/saldos` | GET | Apenas saldos de corretoras |
| `/api/reconciliacao/integridade` | GET | Transações duplicadas, sem ativo, qtd zero |
| `/api/reconciliacao/ativo/{id}` | GET | Reconciliação de ativo específico |

### Frontend Atual
- ✅ `/ferramentas/reconciliacao` — painel completo: status geral (OK/WARNING/ERROR) + lista divergências + abas Posições/Saldos/Integridade/Por Ativo + botão "Verificar Agora" (**Fase 3 — 17/06/2026**)

### Status
✅ **G14 CONCLUÍDO** — tela completa implementada em Fase 3.

---

## G15 — Eventos Corporativos

### APIs Disponíveis
- CRUD completo — GET/POST/PUT/DELETE + POST `aplicar`
- **POST/PUT/DELETE requerem role admin**

### Frontend Atual
- ✅ Eventos corporativos exibidos no detalhe do ativo (`/ativos/detalhe/{ticker}`) (**Fase 5 — 17/06/2026**)
- ❌ `/admin/eventos-corporativos` — tela admin não implementada (baixa prioridade)

### Status
✅ **G15 CONCLUÍDO** para usuário comum — view admin pendente (Baixa prioridade).

---

## G16 — Calendário de Dividendos (Capacidade Avançada)

> Detalhado em G7. Resumo aqui para priorização.

### Status
✅ **G16 CONCLUÍDO** — todos os GAPs críticos implementados em Fase 4 (ver G7).

---

## G17 — Carteira — Saldo Caixa Multi-moeda

### APIs Disponíveis
- `GET /api/carteira/saldo-caixa?moeda=BRL|USD`

### Frontend Atual
- ✅ Usado no dashboard principal
- ✅ Toggle BRL/USD implementado no dashboard (**Fase 7 — 18/06/2026**)

### Status
✅ **G17 CONCLUÍDO** — toggle BRL/USD implementado.

---

## G18 — Dashboard Consolidado

### APIs Disponíveis
- `GET /api/portfolios/dashboard` — por_mercado (BR/US/INTL), top_ativos, alocacao_geografica
- `GET /api/portfolios/evolucao` — histórico patrimonial
- `GET /api/transacoes/recentes` — últimas N transações

### Frontend Atual
- ✅ Dashboard principal com Top 5 ativos por mercado (BR/US/INTL)
- ✅ Gráfico pizza alocação geográfica
- ✅ Toggle BRL/USD
- ✅ Alertas recentes + últimas transações + próximos proventos (**Fase 7 — 18/06/2026**)

### Status
✅ **G18 CONCLUÍDO** — dashboard totalmente reformulado em Fase 2 + Fase 7.

---

## 🎯 Priorização por Valor × Esforço

### ✅ Concluídos (Fases 1–7)

| GAP | Tela | Fase | Data |
|-----|------|------|------|
| G1 | `/configuracoes/perfil` + `/configuracoes/corretoras` | Fase 3 | 17/06/2026 |
| G4 | `/carteira/posicoes` (principal) | Fase 3 | 17/06/2026 |
| G5 | `/operacoes/historico` | Fase 3 | 17/06/2026 |
| G6 | `/carteira/movimentacoes` | Fase 3 | 17/06/2026 |
| G7 | Calendário + gerar auto + confirmar + badges | Fase 4 | 17/06/2026 |
| G8 | Buy Signals + Watchlist Top 10 | Fase 4 | 17/06/2026 |
| G9 | Alertas CRUD + toggle + excluir + feed | Fase 4 | 17/06/2026 |
| G10 | Planos compra/venda unificados | Fase 5 | 17/06/2026 |
| G11 | DIRPF bens e direitos reais | Fase 5 | 17/06/2026 |
| G12 | Rentabilidade + seletor benchmark + período | Fase 4 | 17/06/2026 |
| G13 | Exportação CSV/Excel/PDF multi-entidade | Fase 4 | 17/06/2026 |
| G14 | `/ferramentas/reconciliacao` | Fase 3 | 17/06/2026 |
| G15 | Eventos corporativos no detalhe do ativo | Fase 5 | 17/06/2026 |
| G16 | Calendário dividendos avançado | Fase 4 | 17/06/2026 |
| G17 | Toggle BRL/USD no dashboard | Fase 7 | 18/06/2026 |
| G18 | Dashboard reformulado completo | Fase 2+7 | 17–18/06/2026 |

### 🟡 GAPs Residuais (pendentes)

| GAP | Item | Prioridade |
|-----|------|------------|
| G2 | Widget cotação com provider/TTL + badge fallback no header | Média |
| G4 | Botão "Recalcular Posições" na UI | Média |
| G5 | Editar/excluir transação individual | Baixa |
| G7 | `GET /calendario-dividendos/resumo` — estatísticas mensais | Baixa |
| G8 | Z-Score + badge sinal COMPRAR/AGUARDAR/VENDER | Baixa |
| G10 | CRUD completo de planos (depende de APIs backend) | Baixa |
| G11 | Seletor mês/ano visual na apuração IR | Baixa |
| G15 | `/admin/eventos-corporativos` (tela admin) | Baixa |

---

---

## 🏗️ Rearquitetura do Menu e Dashboard

### Problemas Identificados no Menu Atual

#### 1. "Análises" está sobrecarregado — 3 domínios sem relação
O menu agrupa sob "Análises":
- **Proventos** (renda passiva recebida — domínio próprio)
- **Rentabilidade** (performance da carteira)
- **Imposto de Renda** (obrigação fiscal — domínio próprio)
- **Alocação + Buy Signals** (estratégia)

Esses domínios têm intenções de uso completamente diferentes. Um usuário que quer ver seus DARFs não está "analisando" — está cumprindo obrigação fiscal.

#### 2. "Operações" tem só 1 item
Um dropdown para abrir 1 link é desperdício de clique. Compra/Venda deveria ser acesso direto ou o dropdown expandido com Histórico e Importação B3.

#### 3. "Planos" aponta para rotas 404
`/planos-compra/` e `/planos-venda/` — rotas do blueprint antigo `estrategia.py` que não existem mais. Links mortos no menu.

#### 4. "Carteira" não existe como conceito no menu
O centro do sistema (posições, movimentações de caixa, saldo por corretora) não tem representação no menu. O usuário não encontra "onde estou com minha carteira".

#### 5. "Alertas" como item de nível 1 do menu
Alertas é funcionalidade de configuração/monitoramento, não de navegação primária. Ocupa espaço nobre do menu horizontal.

#### 6. `/perfil` e `/configuracoes` são links mortos
Existem no dropdown do usuário (header) mas não têm blueprint nem rota correspondente.

#### 7. Dashboard descarta dados que chegam da API
`GET /api/portfolios/dashboard` retorna `top_ativos` por mercado e `alocacao_geografica` BR/US/INTL. O template `dashboard/index.html` recebe esses dados mas não os renderiza — seções do wireframe Tela 1 nunca implementadas.

---

### Menu Proposto — Rearquitetura Completa

```
Exitus
│
├── Dashboard                    ← reformulado (ver seção abaixo)
│
├── Carteira                     ← NOVO nível 1 — centro do sistema
│   ├── Minhas Posições          /carteira/posicoes      (G4 — nova)
│   ├── Movimentações de Caixa   /carteira/movimentacoes (G6 — nova)
│   └── Saldo por Corretora      (widget em Movimentações)
│
├── Operações                    ← expandido
│   ├── Compra / Venda           /operacoes/
│   ├── Histórico                /operacoes/historico    (G5 — nova)
│   └── Importar B3              /operacoes/ (aba já existe, destacar)
│
├── Proventos                    ← elevado de sub-item para nível 1
│   ├── Recebidos                /proventos/recebidos
│   ├── Projetados               /proventos/projetados
│   └── Calendário               /proventos/calendario   (+ gerar auto)
│
├── Análises                     ← apenas performance e estratégia
│   ├── Rentabilidade            /analises/rentabilidade (+ benchmark/período)
│   ├── Evolução Patrimonial     /analises/evolucao
│   ├── Performance (Sharpe)     /analises/performance
│   ├── Alocação de Ativos       /analises/alocacao
│   └── Buy Signals              /analises/buy-signals   (+ Watchlist Top 10)
│
├── Fiscal                       ← elevado de sub-item de Análises para nível 1
│   ├── Apuração Mensal          /imposto-renda/mensal
│   ├── DARFs                    /imposto-renda/darfs
│   ├── Histórico Anual          /imposto-renda/historico
│   └── Declaração DIRPF         /imposto-renda/declaracao
│
├── Relatórios                   ← exportação unificada
│   ├── Relatório Mensal         /relatorios/mensal
│   ├── Relatório Anual          /relatorios/anual
│   ├── Extrato Completo         /relatorios/extrato
│   ├── IR Completo              /relatorios/ir
│   └── Exportar Dados           /relatorios/exportar    (CSV/Excel/PDF unificado)
│
├── Ferramentas                  ← expandido com novas capacidades
│   ├── Screener de Ativos       /ferramentas/screener
│   ├── Comparador               /ferramentas/comparador
│   ├── Calculadora IR           /ferramentas/calculadora-ir
│   ├── Simulador de Aportes     /ferramentas/simulador
│   └── Reconciliação            /ferramentas/reconciliacao  (G14 — nova)
│
└── [🔔 sino]  ← Alertas saem do menu e vão para o sino no header
    └── Painel de Alertas        /alertas/  (slide-over ou dropdown rico)
        ├── Feed de alertas recentes
        ├── Criar novo alerta
        └── Gerenciar todos → /alertas/gerenciar
│
└── [👤 usuário]
    ├── Meu Perfil               /configuracoes/perfil       (G1 — nova)
    ├── Minhas Corretoras        /configuracoes/corretoras   (G1 — nova)
    └── Sair                     /logout
```

### O que muda nos blueprints

| Blueprint | Situação Atual | Situação Proposta |
|-----------|---------------|-------------------|
| `dashboard.py` | `/dashboard/` + múltiplas rotas legadas | `/dashboard/` reformulado |
| `operacoes.py` | Compra/venda | + `/historico` |
| `analises.py` | Proventos + Rentabilidade + IR + Buy Signals | Apenas Rentabilidade + Buy Signals |
| `proventos.py` | `/proventos/*` | Sem alteração de rota, sai de sub-item de Análises |
| `fiscal.py` | `/imposto-renda/*` | Sem alteração de rota, sai de sub-item de Análises |
| `relatorios.py` | `/relatorios/*` | + exportação unificada |
| `ferramentas.py` | Screener, comparador, calculadora, simulador | + `/reconciliacao` |
| `alertas.py` | Lista de alertas | + criar/toggle/deletar + feed recente |
| `planos.py` | Redirects para dashboard (broken) | Remover do menu até APIs estarem prontas |
| `configuracoes.py` | **Não existe** | Criar: perfil + corretoras |
| `carteira.py` | **Não existe** | Criar: posições + movimentações |

---

### Reformulação do Dashboard Principal

O dashboard atual (`/dashboard/`) usa `GET /api/portfolios/dashboard` mas renderiza apenas o resumo numérico. Os dados `top_ativos` e `alocacao_geografica` chegam e são descartados.

#### Dashboard Proposto — Seções

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏠 Exitus Dashboard                    [BRL ⇄ USD] [🔔] [👤]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ROW 1 — Cards de Resumo (4 cards)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Patrimônio│ │Rentab.   │ │Saldo     │ │Posições  │           │
│  │Total     │ │Geral     │ │Caixa     │ │Ativas    │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
│  ROW 2 — Por Mercado (dados de por_mercado da API)              │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐       │
│  │ 🇧🇷 Brasil     │ │ 🇺🇸 EUA        │ │ 🌍 INTL        │      │
│  │ R$ 50k  73%   │ │ $10k   22%    │ │ €2k     5%    │       │
│  │ Top: PETR4    │ │ Top: AAPL     │ │ Top: —        │       │
│  └────────────────┘ └────────────────┘ └────────────────┘       │
│                                                                  │
│  ROW 3 — Gráficos                                               │
│  ┌──────────────────────┐ ┌────────────────────────────┐        │
│  │ 🍕 Alocação Geo      │ │ 📈 Evolução Patrimonial    │        │
│  │ (alocacao_geografica)│ │ (portfolios/evolucao)       │        │
│  └──────────────────────┘ └────────────────────────────┘        │
│                                                                  │
│  ROW 4 — Últimas Transações + Alertas Recentes                  │
│  ┌──────────────────────┐ ┌────────────────────────────┐        │
│  │ 🔄 Transações        │ │ 🔔 Alertas Recentes        │        │
│  │ (transacoes/recentes)│ │ (alertas/recentes)          │        │
│  └──────────────────────┘ └────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

**APIs envolvidas no Dashboard reformulado:**
- `GET /api/portfolios/dashboard` — resumo + por_mercado + alocacao_geografica *(já chamado, dados ignorados)*
- `GET /api/portfolios/evolucao` — gráfico de linha *(já chamado)*
- `GET /api/carteira/saldo-caixa` — saldo caixa card *(já chamado)*
- `GET /api/transacoes/recentes` — últimas transações *(já chamado)*
- `GET /api/alertas/recentes` — alertas recentes *(não chamado)*

**Alterações no template `dashboard/index.html`:**
- Renderizar `dados.por_mercado` nos 3 cards de mercado
- Renderizar `dados.alocacao_geografica` no gráfico pizza
- Adicionar seção alertas recentes
- Adicionar toggle BRL/USD (chama `/api/carteira/saldo-caixa?moeda=USD`)

---

### Ordem de Execução Proposta

A rearquitetura deve ser incremental para não quebrar o que funciona:

**Fase 1 — Correções urgentes (sem novas telas)**
1. Remover "Planos" do menu (links 404)
2. Mover "Alertas" para o sino do header
3. Separar "Fiscal" de "Análises" no menu (só reorganização HTML)
4. Separar "Proventos" de "Análises" no menu
5. Corrigir `/perfil` e `/configuracoes` no dropdown do usuário

**Fase 2 — Dashboard reformulado**
6. Renderizar `top_ativos` por mercado nos cards
7. Renderizar `alocacao_geografica` no gráfico pizza
8. Adicionar alertas recentes (Row 4)
9. Toggle BRL/USD

**Fase 3 — Telas novas (alta prioridade)**
10. `carteira.py` — `/carteira/posicoes` + `/carteira/movimentacoes`
11. `configuracoes.py` — `/configuracoes/perfil` + `/configuracoes/corretoras`
12. `/operacoes/historico`
13. `/ferramentas/reconciliacao`

**Fase 4 — Expansões de telas existentes**
14. Alertas — criar/toggle/deletar
15. Exportação unificada
16. Buy Signals + Watchlist Top 10
17. Calendário + gerar auto + confirmar pagamento
18. Rentabilidade + seletor benchmark/período

---

## 📋 Status Final — 18/06/2026

**16 de 18 GAPs concluídos** (89%). GAPs residuais são todos de baixa/média prioridade.

### Próximos Passos
1. **Discutir GAPs residuais** — priorizar G2 (cotações) e G4 (recalcular posições)
2. **Definir próxima fase** — G2 como candidato natural (widget reutilizável em múltiplas telas)
3. **Corrigir specs E2E v3** após telas estabilizadas

---

*Documento criado: 16/06/2026 | Branch: feature/frontend-gap-analysis*
