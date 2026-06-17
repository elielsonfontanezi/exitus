# Frontend GAP Analysis — Sistema Exitus

**Branch:** `feature/frontend-gap-analysis`  
**Data:** 16/06/2026  
**Versão:** v1.0  
**Objetivo:** Mapear cada grupo de APIs disponíveis no backend contra o que o frontend expõe hoje, identificar GAPs e propor telas novas ou expansões de telas existentes.

> **Metodologia:** APIs são o inventário. Telas são o produto.
> O estudo parte das APIs (o que foi pensado para o frontend) e determina onde cada capacidade aterra — em tela existente ou nova.

---

## �️ Plano de Execução por Fases

> Status atualizado: **17/06/2026**

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

**Parte C — Já Alpine.js (migração de base adiada):**
- [x] Operações (1): operacoes.html — já usa Alpine.js inline, 946 linhas
- [x] Dashboard (1): index.html — já usa Alpine.js inline, 647 linhas

> Nota: Operações e Dashboard já são reativos com Alpine.js mas herdam de `base.html`.
> Migração para `base_interna.html` seria cosmética e de risco alto — adiada para fase posterior.

---

## 📋 Índice de Grupos

| # | Grupo | APIs disponíveis | Frontend atual | GAPs | Prioridade |
|---|-------|-----------------|----------------|------|-----------|
| G1 | Auth + Usuário + Corretoras | 6 endpoints | ✅ Login, registro | 🔴 Perfil, corretoras CRUD | Alta |
| G2 | Cotações em Tempo Real | 4 endpoints | ⚠️ Usado internamente | 🔴 Tela de cotações dedicada | Alta |
| G3 | Ativos — Catálogo | 3 endpoints | ✅ Lista por categoria | 🟡 Detalhe incompleto | Média |
| G4 | Posições — Carteira | 4 endpoints | ⚠️ Dashboard usa resumo | 🔴 Tela posições completa, recalcular | Alta |
| G5 | Transações | 2 endpoints | ✅ Compra / ⚠️ Venda | 🟡 Editar/excluir, histórico filtrado | Média |
| G6 | Movimentações de Caixa | 2 endpoints | ❌ Não existe | 🔴 Nova tela completa | Alta |
| G7 | Proventos + Calendário | 8 endpoints | ✅ Recebidos, projetados, calendário | 🟡 Confirmar pagamento, gerar auto | Média |
| G8 | Buy Signals | 4 endpoints | ⚠️ Parcial em Análises | 🟡 Watchlist-top, detalhe ticker | Média |
| G9 | Alertas | 5 endpoints | ⚠️ Só lista | 🔴 Criar, toggle, deletar na UI | Alta |
| G10 | Planos de Compra/Venda | - | ⚠️ Stub/redirect | 🔴 CRUD completo pendente de APIs | Baixa* |
| G11 | IR / Fiscal | 3 endpoints | ✅ Apuração, DARFs, histórico, DIRPF | 🟡 DIRPF incompleto | Baixa |
| G12 | Rentabilidade + Performance | 3 endpoints | ✅ TWR/MWR, alocação, performance | 🟡 Seletor benchmark na UI | Baixa |
| G13 | Relatórios + Exportação | 6 endpoints | ✅ Mensal, anual, extrato, IR, CSV | 🟡 Export Excel/PDF, download direto | Média |
| G14 | Reconciliação | 4 endpoints | ❌ Não existe | 🔴 Nova tela Ferramentas | Alta |
| G15 | Eventos Corporativos | 6 endpoints | ❌ Não existe | 🟡 Tela admin ou aviso no detalhe ativo | Baixa |
| G16 | Calendário de Dividendos | 6 endpoints | ⚠️ Parcial em proventos | 🔴 Gerar automático, confirmar pagamento | Alta |
| G17 | Carteira — Saldo Caixa | 1 endpoint | ✅ Usado no dashboard | 🟡 Saldo multi-corretora visível | Baixa |
| G18 | Dashboard Consolidado | 3 endpoints | ✅ Dashboard principal | 🟡 Toggle BRL/USD, Top 5 por mercado | Média |

> *G10 — depende de APIs backend ainda não documentadas para planos CRUD completo.

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
- ❌ Perfil do usuário — não existe tela
- ❌ Corretoras — sem tela de gestão no frontend

### GAPs Identificados
1. **Tela Perfil** — editar nome, email, senha. API: `PUT /api/usuarios/{id}`
2. **Tela Corretoras** — listar, criar, editar, remover corretoras vinculadas ao usuário

### Proposta de Telas Novas
```
/configuracoes/perfil        → Dados pessoais + senha
/configuracoes/corretoras    → CRUD corretoras (lista + formulário inline)
```
**Encaixe:** novo blueprint `configuracoes.py` ou expansão de `auth.py`

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
- ⚠️ Dashboard usa dados de posições mas não via `/api/posicoes` diretamente
- ❌ Sem tela dedicada de "Minha Carteira" com lista de posições filtrada
- ❌ `GET /api/posicoes/resumo` não usado em nenhuma tela
- ❌ `POST /api/posicoes/calcular` sem botão na UI

### GAPs Identificados
1. **Tela Minha Carteira** — posições agrupadas por tipo, com PM, valor atual, L/P realizado
2. **Card de resumo** com total investido e ROI (usa `/api/posicoes/resumo`)
3. **Botão "Recalcular Posições"** em Ferramentas (usa `POST /api/posicoes/calcular`)
4. **Filtro por corretora** e por "somente com lucro"

### Proposta de Telas Novas
```
/carteira/posicoes          → lista completa de posições com filtros
/carteira/posicoes/{id}     → detalhe: PM, histórico de compras, L/P
/ferramentas/recalcular     → botão + resultado do recalculo (ou integrar em Ferramentas)
```

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
- ✅ `POST /api/transacoes` — via tela de compra (`/operacoes/`)
- ⚠️ Venda usa a mesma tela unificada mas com lógica de toggle
- ❌ Editar/excluir transação — sem tela
- ❌ Histórico completo com filtros — sem tela dedicada

### GAPs Identificados
1. **Tela Histórico de Transações** — tabela com filtros (período, tipo, ativo, corretora)
2. **Editar transação** — formulário inline ou modal
3. **Excluir transação** — com confirmação

### Proposta
```
/operacoes/historico        → tabela paginada + filtros + ações editar/excluir
```
**Blueprint:** expansão de `operacoes.py`

---

## G6 — Movimentações de Caixa

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/movimentacoes` | GET | Lista com filtros (corretora, período) |
| `/api/movimentacoes/saldo/{corretora_id}` | GET | Saldo calculado por corretora |

### Frontend Atual
- ❌ **Nenhuma tela implementada** — wireframe Tela 9 desenhado, nunca construído
- ⚠️ Depósito existe como rota (`/operacoes/deposito`) mas sem listagem

### GAPs Identificados
1. **Tela Movimentações de Caixa** completa (Tela 9 do wireframe)
2. **Saldo por corretora** com tabela histórico entradas/saídas
3. **Resumo do período** (total entradas, total saídas, saldo final)

### Proposta de Tela Nova (alta prioridade — tela 9 do wireframe nunca implementada)
```
/carteira/movimentacoes     → tabela filtrada + saldo por corretora + resumo período
```
**Blueprint:** novo `carteira.py` ou expansão de `operacoes.py`

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
- ✅ `/proventos/projetados` — proventos projetados
- ✅ `/proventos/calendario` — calendário básico
- ❌ `POST /calendario-dividendos/gerar` — sem botão "Gerar automático"
- ❌ `POST /confirmar-pagamento` — sem ação de confirmar na UI
- ❌ `GET /calendario-dividendos/resumo` — estatísticas mensais/por ativo não exibidas

### GAPs Identificados
1. **Botão "Gerar Calendário"** na tela de calendário
2. **Confirmar pagamento** — ação por linha no calendário
3. **Resumo por ativo** — card com total estimado vs. real recebido
4. **Status visual** previsto/confirmado/atrasado/pago nos itens

### Proposta
```
Expansão de /proventos/calendario  → + botão gerar auto + ação confirmar + badges status
Expansão de /proventos/projetados  → + card resumo estimado vs. real por ativo
```

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
- ✅ `/analises/buy-signals` — busca por ticker, score, margem (Tela 2 do wireframe parcialmente implementada)
- ❌ `GET /api/buy-signals/watchlist-top` — top 10 sem tela
- ❌ Z-Score não exibido na tela atual

### GAPs Identificados
1. **Watchlist Top 10** — ranking de oportunidades sem precisar digitar ticker
2. **Z-Score** — exibir como indicador adicional no detalhe
3. **Sinal claro** COMPRAR/AGUARDAR/VENDER com badge colorido

### Proposta
```
Expansão de /analises/buy-signals  → + seção "Top 10 Oportunidades" + Z-Score + badge sinal
```

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
- ✅ `/alertas/` — lista alertas (somente leitura)
- ✅ `/alertas/preco` `/alertas/dividendos` `/alertas/personalizados` — sub-páginas
- ❌ `POST /api/alertas` — sem formulário de criação na UI
- ❌ `PATCH /toggle` — sem botão ativar/desativar
- ❌ `DELETE` — sem ação de excluir

### GAPs Identificados
1. **Botão "Novo Alerta"** com formulário (`nome`, `tipo_alerta`, `frequencia_notificacao`)
2. **Toggle ativo/inativo** por linha
3. **Botão excluir** com confirmação
4. **Alertas recentes** — feed de alertas disparados (já existe em dashboard, expor em tela dedicada)

### Proposta
```
Expansão de /alertas/       → + botão criar + toggle inline + excluir + feed recentes
```
**Esta é a tela com mais GAPs de interação — wireframe Tela 10 completa, UI incompleta.**

---

## G10 — Planos de Compra/Venda

### Frontend Atual
- ⚠️ `/planos/` — lista, redireciona para dashboard
- ⚠️ APIs de backend para planos CRUD não documentadas em `API_REFERENCE.md`

### Status
**Aguardando:** Verificar se há endpoints `/api/plano-compra/*` implementados no backend.
Ação: inspecionar `backend/app/routes/` para confirmar existência antes de desenhar telas.

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
- ⚠️ `/imposto-renda/declaracao` — DIRPF existe mas dados incompletos

### GAPs Identificados
1. **DIRPF** — exibir bens e direitos com valores reais da API
2. **Seletor de mês/ano** interativo na apuração (seletor visual, não só parâmetro URL)

### Proposta
```
Expansão de /imposto-renda/mensal      → + seletor de mês/ano visual (datepicker)
Expansão de /imposto-renda/declaracao  → + seção bens e direitos com valores da API
```

---

## G12 — Rentabilidade + Performance

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/portfolios/rentabilidade?periodo=X&benchmark=Y` | GET | TWR, MWR, alpha vs benchmark |
| `/api/portfolios/evolucao?meses=N` | GET | Evolução patrimonial histórica |
| `/api/portfolios/alocacao` | GET | Alocação geográfica e por tipo |

### Frontend Atual
- ✅ `/analises/rentabilidade` — TWR/MWR exibidos
- ✅ `/analises/alocacao` — alocação visual
- ✅ `/analises/evolucao` — gráfico de evolução
- ⚠️ Benchmarks aceitos: CDI, IBOV, IFIX, IPCA6, SP500 — seletor não exposto na UI

### GAPs Identificados
1. **Seletor de benchmark** na tela de rentabilidade (dropdown CDI/IBOV/IFIX/SP500)
2. **Seletor de período** visual (1m/3m/6m/12m/ytd/max)
3. **Alpha** vs benchmark — não exibido na tela atual

### Proposta
```
Expansão de /analises/rentabilidade  → + seletor período + seletor benchmark + exibir alpha
```

---

## G13 — Relatórios + Exportação

### APIs Disponíveis
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/export/transacoes?formato=csv\|excel\|json\|pdf` | GET | Exportar transações |
| `/api/export/proventos?formato=X` | GET | Exportar proventos |
| `/api/export/posicoes?formato=X` | GET | Exportar posições |

### Frontend Atual
- ✅ `/relatorios/exportar/csv` — exportação CSV de transações
- ❌ Export de **proventos** — sem botão
- ❌ Export de **posições** — sem botão
- ❌ Formatos **Excel** e **PDF** — não expostos na UI

### GAPs Identificados
1. **Exportar proventos** (CSV/Excel/PDF)
2. **Exportar posições** (CSV/Excel/PDF)
3. **Seletor de formato** na tela de exportação (agora só CSV hardcoded)
4. **Filtros de exportação** — período, ativo, corretora

### Proposta
```
Expansão de /relatorios/exportar/csv  → renomear para /relatorios/exportar
                                        + seletor formato + entidades (transações/proventos/posições)
                                        + filtros período/ativo/corretora
```

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
- ❌ **Nenhuma tela existe**

### GAPs Identificados
- Tela nova completa para **diagnóstico de integridade** — muito útil para o usuário detectar inconsistências

### Proposta de Tela Nova (alta prioridade — capacidade única, sem equivalente)
```
/ferramentas/reconciliacao  → painel: status geral (OK/WARNING/ERROR) + lista divergências
                              + abas: Posições | Saldos | Integridade | Por Ativo
                              + botão "Verificar Agora"
```

---

## G15 — Eventos Corporativos

### APIs Disponíveis
- CRUD completo — GET/POST/PUT/DELETE + POST `aplicar`
- **POST/PUT/DELETE requerem role admin**

### Frontend Atual
- ❌ Sem tela (apenas admin backend)

### Proposta
```
Para usuário comum: exibir eventos corporativos relevantes no detalhe do ativo (G3)
Para admin: /admin/eventos-corporativos (expansão do admin.py existente)
```

---

## G16 — Calendário de Dividendos (Capacidade Avançada)

> Detalhado em G7. Resumo aqui para priorização.

### GAPs de maior valor
1. `POST /calendario-dividendos/gerar` — gerar calendário automático com base nas posições
2. `POST /confirmar-pagamento` — fechar o ciclo previsto → confirmado → pago
3. Resumo por ativo com estimado vs. real

---

## G17 — Carteira — Saldo Caixa Multi-moeda

### APIs Disponíveis
- `GET /api/carteira/saldo-caixa?moeda=BRL|USD`

### Frontend Atual
- ✅ Usado no dashboard principal
- ❌ Toggle BRL/USD do wireframe Tela 1 não implementado

### Proposta
```
Dashboard → adicionar toggle BRL ⇄ USD que recarrega saldo via API com moeda=USD
```

---

## G18 — Dashboard Consolidado

### APIs Disponíveis
- `GET /api/portfolios/dashboard` — por_mercado (BR/US/INTL), top_ativos, alocacao_geografica
- `GET /api/portfolios/evolucao` — histórico patrimonial
- `GET /api/transacoes/recentes` — últimas N transações

### Frontend Atual
- ✅ Dashboard principal usa essas APIs
- ❌ **Top 5 ativos por mercado** — não exibido (API retorna, tela ignora)
- ❌ **Alocação geográfica** BR/US/INTL — não exibida (só por tipo de ativo)
- ❌ **Toggle BRL/USD** — wireframe Tela 1, não implementado

### Proposta
```
Expansão do Dashboard  → + seção "Top 5 por Mercado" (BR / US / INTL)
                         + gráfico pizza alocação geográfica
                         + toggle BRL ⇄ USD no header
```

---

## 🎯 Priorização por Valor × Esforço

### 🔴 Alta Prioridade (API pronta + GAP visível para o usuário)

| # | Tela | Rota Proposta | APIs Envolvidas |
|---|------|--------------|----------------|
| 1 | Movimentações de Caixa | `/carteira/movimentacoes` | `GET /api/movimentacoes`, `/saldo/{id}` |
| 2 | Alertas — ações completas | expansão `/alertas/` | `POST`, `PATCH toggle`, `DELETE` |
| 3 | Reconciliação | `/ferramentas/reconciliacao` | `GET /api/reconciliacao/*` |
| 4 | Histórico de Transações | `/operacoes/historico` | `GET /api/transacoes` (filtrado) |
| 5 | Posições — Minha Carteira | `/carteira/posicoes` | `GET /api/posicoes`, `/resumo` |
| 6 | Configurações — Corretoras | `/configuracoes/corretoras` | CRUD `/api/corretoras` |

### 🟡 Média Prioridade (expansão de telas existentes)

| # | Expansão | Tela Existente | GAP |
|---|---------|----------------|-----|
| 1 | Buy Signals + Watchlist Top 10 | `/analises/buy-signals` | Adicionar seção ranking |
| 2 | Rentabilidade + seletor período/benchmark | `/analises/rentabilidade` | Dropdowns |
| 3 | Exportação multi-formato/entidade | `/relatorios/exportar` | Seletor formato + entidade |
| 4 | Calendário + gerar auto + confirmar | `/proventos/calendario` | Botões + badges status |
| 5 | Detalhe ativo real | `/ativos/detalhe/{ticker}` | Fundamentalistas + cotação |
| 6 | Dashboard + top 5 + alocação geo | `/dashboard` | Seções extras |

### 🟢 Baixa Prioridade (nice-to-have ou dependência de outros)

| # | Item | Dependência |
|---|------|-------------|
| 1 | DIRPF — bens e direitos | Dados reais precisam de validação |
| 2 | Toggle BRL/USD global | UX de multi-moeda a definir |
| 3 | Eventos Corporativos — user view | Dados históricos necessários |
| 4 | Planos CRUD | APIs backend a confirmar |

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

## 📋 Próximos Passos

1. **Validar esta análise** com o usuário tela a tela
2. **Inspecionar telas reais** em `localhost:8080` para confirmar o que funciona vs. o que está quebrado
3. **Definir Sprint 9** — quais GAPs implementar primeiro
4. **Corrigir specs E2E v3** após telas novas/expandidas estarem estáveis

---

*Documento criado: 16/06/2026 | Branch: feature/frontend-gap-analysis*
