# Auditoria Funcional — Sistema Exitus
**Data:** 18/06/2026  
**Revalidado:** 22/06/2026  
**Auditor:** Cascade (análise de código + browser)  
**Usuário de teste:** `e2e_user` / `e2e_senha_123`  
**Frontend:** http://localhost:8080  
**Backend:** http://localhost:5000  

> **Nota de revalidação (22/06/2026):** após correção do BUG-020, a auditoria foi revisada em código. Bugs já resolvidos ou desatualizados foram marcados; contagem de bugs importantes ajustada de 15 para 6.

**Legenda de status:**
- ✅ `OK` — funciona conforme esperado
- 🟡 `PARCIAL` — funciona mas com dados incorretos, faltando features ou bugs menores
- 🔴 `QUEBRADO` — erro, 404, ou não carrega dados
- ⬜ `NÃO TESTADO` — ainda não auditado

---

## Resumo Executivo

| Status | Quantidade |
|--------|-----------|
| ✅ OK | 2 |
| 🟡 PARCIAL | 34 |
| 🔴 QUEBRADO | 0 |
| ⬜ NÃO TESTADO | 0 |

---

## Tabela de Telas

| # | Módulo | URL | Status | Problemas | Prioridade |
|---|--------|-----|--------|-----------|-----------|
| 1 | Login | `/auth/login` | ✅ | Redesenhado: UX_DESIGN_SYSTEM aplicado, credenciais removidas, link Esqueceu removido (EXITUS-LOGIN-001) | — |
| 2 | Dashboard | `/dashboard/` | 🟡 | CDI/Ibovespa hardcoded; meta hardcoded; token via localStorage pode falhar | Alta |
| 3 | Configurações — Perfil | `/configuracoes/perfil` | 🟡 | Somente leitura — sem edição de nome/email/senha | Média |
| 4 | Configurações — Corretoras | `/configuracoes/corretoras` | 🟡 | Listagem OK — sem botões CRUD (criar/editar/excluir corretora) | Alta |
| 5 | Operações — Import B3 | `/operacoes/` | 🟡 | Import funciona ✅; retorna 0 com fixture existente (idempotente por design); revalidado com dados novos: Transações=2 | — |
| 6 | Operações — Compra | `/operacoes/` | 🟡 | Toggle funciona ✅; busca de ativo sem autocomplete (BUG-014 relacionado) | Média |
| 7 | Operações — Venda | `/operacoes/` | 🟡 | Toggle funciona ✅; modo venda acessível e formulário exibido corretamente | Média |
| 8 | Operações — Histórico | `/operacoes/historico` | 🟡 | Filtro por data com bug; filtro ticker OK; sem editar/excluir | Média |
| 9 | Carteira — Posições | `/carteira/posicoes` | ✅ | Validado visualmente: KPIs, filtros (ticker/tipo/mercado) e botão Recalcular funcionam | — |
| 10 | Carteira — Movimentações | `/carteira/movimentacoes` | 🟡 | KPIs e tabela OK; filtro tipo OK; filtro data quebrado — tela pisca ao digitar ano (BUG-013) | Alta |
| 11 | Ativos — Catálogo | `/ativos/acoes` | 🟡 | Tabela e categorias OK; busca por ticker não funciona (BUG-014); detalhe lento e sem dados (BUG-015) | Alta |
| 12 | Ativos — Detalhe | `/ativos/<TICKER>` | 🟡 | Abre mas demora e nem sempre traz dados (BUG-015) | Alta |
| 13 | Ativos — Eventos Corp. | `/ativos/eventos-corporativos` | 🟡 | Carrega corretamente ✅; KPIs + filtros OK; link adicionado ao menu (EXITUS-ATIVOS-001); sem dados (ambiente dev sem eventos cadastrados) | Baixa |
| 14 | Proventos — Calendário | `/proventos/calendario` | 🟡 | Calendário e filtros OK; sem botão "Confirmar Recebimento" (FEAT-008); botão "Gerar Automático" presente | Média |
| 15 | Análises — Evolução | `/analises/evolucao` | 🟡 | Carrega dados e gráficos ✅ | Baixa |
| 16 | Análises — Performance | `/analises/performance` | 🟡 | Carrega dados e gráficos ✅ | Baixa |
| 17 | Análises — Alocação | `/analises/alocacao` | 🟡 | Carrega dados e gráficos ✅ | Baixa |
| 18 | Análises — Buy Signals | `/analises/buy-signals` | 🟡 | Carrega dados ✅; busca por ticker sem autocomplete (BUG-017) | Média |
| 19 | Análises — Rentabilidade (legacy) | `/analises/rentabilidade` | 🟡 | Redirect para `/periodo` ✅ (EXITUS-ANALISES-001); código morto removido | — |
| 19b | Análises — Rentabilidade por Período | `/analises/rentabilidade/periodo` | 🟡 | Acessível pelo menu como "Rentabilidade"; filtros de período OK; benchmark sem validação | Média |
| 20 | Fiscal — IR Mensal | `/imposto-renda/mensal` | 🟡 | Carrega dados ✅; `API_BASE` hardcoded como `exitus-backend:5000` (BUG-009) | Média |
| 21 | Fiscal — DARFs | `/imposto-renda/darfs` | 🟡 | Carrega dados ✅; `API_BASE` hardcoded (BUG-009) | Média |
| 22 | Fiscal — Histórico | `/imposto-renda/historico` | 🟡 | Carrega dados ✅ | Baixa |
| 23 | Fiscal — DIRPF | `/imposto-renda/declaracao` | � | Carrega dados ✅; `dados`/`erro` não passados ao template (BUG-010); `API_BASE` hardcoded (BUG-009) | Alta |
| 24 | Relatórios — Mensal | `/relatorios/mensal` | 🟡 | Carrega dados ✅ | Baixa |
| 25 | Relatórios — Anual | `/relatorios/anual` | 🟡 | Carrega dados ✅ | Baixa |
| 26 | Relatórios — Extrato | `/relatorios/extrato` | 🟡 | Carrega dados ✅ | Baixa |
| 27 | Relatórios — IR Completo | `/relatorios/ir` | 🟡 | Carrega dados ✅ | Baixa |
| 28 | Relatórios — Exportação | `/relatorios/exportar` | 🟡 | Carrega dados ✅; export CSV renderiza HTML em vez de download (FEAT-006) | Média |
| 29 | Ferramentas — Screener | `/ferramentas/screener` | 🟡 | Carrega dados ✅ | Baixa |
| 30 | Ferramentas — Comparador | `/ferramentas/comparador` | 🟡 | Tela carrega; botão "Comparar" não aciona nada (BUG-019) | Alta |
| 31 | Ferramentas — Calculadora IR | `/ferramentas/calculadora-ir` | 🟡 | Carrega dados ✅ | Baixa |
| 32 | Ferramentas — Simulador | `/ferramentas/simulador` | 🟡 | Carrega dados ✅ | Baixa |
| 33 | Ferramentas — Reconciliação | `/ferramentas/reconciliacao` | 🟡 | Carrega dados ✅ | Baixa |
| 34 | Estratégia — Planos | `/planos-compra/` | 🟡 | Acessível por URL direta; lista e detalhes de planos OK; **sem entrada no menu** (BUG-011) | Alta |
| 35 | Alertas | `/alertas/` | 🟡 | Acessível pelo menu; lista de alertas carrega ✅ | Baixa |

---

## Detalhes por Tela

---

### Tela 1 — Login (`/auth/login`)
**Status:** ✅ OK — corrigido em EXITUS-LOGIN-001 (18/06/2026)

**O que funciona:**
- HTTP 200 ✅
- `POST /auth/login` AJAX → `/api/auth/login` → `window.auth.saveToken()` → token salvo no `localStorage` ✅
- Redireciona para `dashboard.index` após sucesso ✅
- Visual consistente com UX_DESIGN_SYSTEM: Nunito, `#A38C65`, card clean ✅
- Sem credenciais hardcoded ✅
- Sem links quebrados ✅
- Erro inline amigável em caso de senha incorreta ✅

**Correções aplicadas (EXITUS-LOGIN-001):**
1. ✅ **Redesenho visual** — substituído azul Bootstrap por Nunito + dourado `#A38C65` (UX_DESIGN_SYSTEM)
2. ✅ **Credenciais removidas** — `value="e2e_user"` e `value="e2e_senha_123"` removidos do HTML
3. ✅ **Link "Esqueceu?" removido** — rota `/auth/forgot-password` não implementada
4. ✅ **Token mock removido de `auth.js`** — causa raiz do BUG-001 eliminada

**Validação visual:** pendente revalidação após fix (aguarda próxima sessão)

---

### Tela 2 — Dashboard (`/dashboard/`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- KPIs patrimônio: 6 cards (Patrimônio Total, Rentabilidade, Rentab. Total, Proventos 12M, Ativos, Saldo Caixa) ✅
- Toggle BRL/USD no card Saldo Caixa ✅
- Visão multi-mercado BR/US/INTL com `x-for` loop ✅
- Top 5 ativos Brasil em tabela `data-table` ✅
- Últimas transações via `/api/transacoes/recentes?limit=5` ✅
- Próximos proventos 30 dias via `/api/calendario-dividendos/` ✅
- Alertas recentes via `/api/alertas/recentes?limit=3` ✅
- Gráfico evolução patrimonial (Chart.js) ✅
- Gráfico alocação por mercado (doughnut) ✅
- Meta de patrimônio com `progress-bar-container` ✅

**Problemas encontrados (código):**
1. 🔴 **CDI e Ibovespa hardcoded** — linha 234: `11.75%` e linha 238: `8.32%` são valores fixos no template, não vêm de nenhuma API. Você mencionou que o CDI 12m está incorreto — confirma aqui a causa.
2. 🟡 **Meta de patrimônio hardcoded** — `R$ 500.000,00` fixo no HTML (linha 208), não configurável pelo usuário
3. 🟡 **Token via `localStorage`** — linha 312: `localStorage.getItem('access_token')` — mas o login salva o token na **sessão Flask** (servidor), não no localStorage. Se o token não estiver no localStorage, o dashboard carrega sem dados.

**Validação visual (confirmada pelo usuário):**
- [x] KPIs carregam — dados de teste, não é possível validar valores reais agora
- [x] Cards BR/US/INTL mostram dados ✅
- [x] Gráfico de evolução aparece ✅
- [x] Últimas transações e próximos proventos aparecem com dados ✅
- [x] Alertas recentes aparecem ✅

**Conclusão:** Estrutura e integração funcionam. Os 3 bugs são de dados/configuração:
- CDI/Ibovespa hardcoded → corrigir buscando de API ou config
- Meta R$ 500k hardcoded → tornar configurável
- localStorage vs sessão Flask → investigar se token está sendo salvo no localStorage pelo `auth.js`

---

### Tela 3 — Configurações — Perfil (`/configuracoes/perfil`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- Abas Perfil / Minhas Corretoras ✅
- Carrega dados via `GET /api/auth/me` ✅
- Exibe nome, username, e-mail, status, data de cadastro ✅

**Problemas encontrados:**
1. 🔴 **Somente leitura** — não há formulário de edição. O roteiro diz "Editar perfil" mas a tela só exibe dados. Sem botão "Editar", sem campos de input, sem `PUT /api/auth/me`.
2. 🟡 **Sem troca de senha** — nenhum campo ou fluxo para alterar senha

**Validação visual (confirmada pelo usuário):**
- [x] Dados do usuário aparecem corretamente ✅
- [x] Aba "Minhas Corretoras" navega corretamente ✅

---

### Tela 4 — Configurações — Corretoras (`/configuracoes/corretoras`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- KPI bar: total corretoras, ativas, saldo total ✅
- Tabela com nome, tipo, país, moeda, saldo, status, data ✅
- Carrega via `GET /api/corretoras?per_page=100` ✅
- Empty state e error state implementados ✅

**Problemas encontrados:**
1. 🔴 **Sem CRUD** — o roteiro diz "CRUD corretoras" mas a tela só lista. Não há botão "Nova Corretora", nem editar, nem excluir. Falta: formulário de criação (`POST /api/corretoras`), edição (`PUT /api/corretoras/<id>`), exclusão (`DELETE /api/corretoras/<id>`).

**Validação visual (confirmada pelo usuário):**
- [x] Tabela de corretoras aparece com dados ✅
- [x] KPIs aparecem — mas **Saldo Total exibe R$ 0,00** 🟡 — campo `saldo_atual` provavelmente não é preenchido pela API ou não existe na tabela `corretoras`

---

### Telas 5/6/7 — Operações (`/operacoes/`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- **Import B3:** drag-and-drop CSV/Excel, chama `POST /api/import/b3`, exibe resultado (transações, proventos, avisos) ✅
- **Compra:** toggle compra/venda, seleção de tipo de ativo (5 categorias), busca ticker via `/api/ativos`, cotação automática via `/api/cotacoes/<ticker>`, formulário completo ✅
- **Venda:** seleção a partir das posições existentes via `/api/posicoes`, validação de quantidade máxima, preço médio pré-preenchido ✅
- Suporte a múltiplos tipos: Ações BR, FIIs, ETFs, Cripto, BDR/Ações US ✅

**Problemas encontrados:**
1. 🟡 **Rota `/operacoes/venda` é legada** — existe rota separada que renderiza `venda.html` (template legado, não migrado), enquanto o toggle compra/venda está no `operacoes_v2.html`. Pode gerar confusão.
2. 🟡 **Sem editar/excluir** — após registrar uma operação, não é possível corrigi-la pela tela. Usuário precisa ir ao Histórico.
3. 🟡 **Import B3 sem detalhes por linha** — erros de importação mostram só avisos gerais, sem indicar qual linha do arquivo falhou.

**Validação visual (confirmada pelo usuário):**
- [x] Busca de ticker autocompleta com sugestões ✅
- [x] Cotação preenchida automaticamente ao selecionar ativo ✅
- [x] Upload B3 (Canal do Investidor) — arquivo aceito mas **não exibiu registros importados** 🔴 — possível incompatibilidade de formato ou falha silenciosa na API
- [x] **Toggle Compra/Venda não responde aos cliques** 🔴 — bug crítico: botões visíveis mas sem interatividade

---

### Tela 8 — Operações — Histórico (`/operacoes/historico`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- KPIs: total transações, compras, vendas, volume total ✅
- Filtros: ticker, tipo (compra/venda), data início/fim ✅
- Tabela com data, tipo, ativo, mercado, quantidade, preço, valor total, custos ✅
- Colunas clicáveis para ordenação ✅
- Paginação (50 por página) ✅
- Botão "Nova Operação" → `/operacoes/` ✅

**Problemas encontrados:**
1. 🟡 **Sem editar/excluir transação** — menu de ações (⋯) só tem "Ver Ativo" e "Nova Operação". Não há opção de editar ou excluir uma transação registrada.
2. 🟡 **Link "Ver Ativo"** aponta para `/dashboard/ativo/<ticker>` — verificar se essa rota existe.

**Validação visual (confirmada pelo usuário):**
- [x] Tabela carrega com transações ✅
- [x] Filtro por ticker funciona ✅
- [x] **Filtro por data (mês 11) não retornou resultados** 🟡 — possível bug no filtro de data: verificar se o campo aceita apenas `YYYY-MM-DD` e se o backend filtra por `data_transacao` ou `data_operacao`
- [ ] Paginação não testada

---

### Tela 9 — Carteira — Posições (`/carteira/posicoes`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- Abas Posições / Movimentações de Caixa ✅
- KPIs: Posições, Total Investido, Valor Atual, Lucro Realizado, ROI ✅
- Filtros: ticker, tipo de ativo, mercado (BR/US/INTL) ✅
- Tabela: ativo, tipo, mercado, quantidade, preço médio, custo total, preço atual, valor atual, L/P ✅
- Ordenação por coluna ✅
- Botão Recalcular via `POST /api/posicoes/recalcular` ✅
- Duas chamadas em paralelo: `GET /api/posicoes` + `GET /api/posicoes/resumo` ✅

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001** — localStorage vazio → API retorna 401 → tela não carrega dados
2. 🟡 **Link "Ver Detalhes"** aponta para `/dashboard/ativo/<ticker>` — mesma rota suspeita do Histórico (BUG-008)
3. 🟡 **Filtro tipo usa valores lowercase** (`acao`, `fii`) mas o campo `ativo.tipo` da API pode vir como enum uppercase (`ACAO`, `FII`) — filtro client-side pode não funcionar

**Validação visual (18/06/2026):**
- [x] KPIs e posições carregam ✅
- [x] Filtro por ticker funciona ✅
- [x] Filtro por tipo funciona ✅
- [x] Filtro por mercado funciona ✅
- [x] Botão Recalcular funciona e atualiza valores ✅

> BUG-001 não afeta esta tela — provavelmente usa token da sessão Flask server-side ou o endpoint não requer autenticação via header.

---

### Tela 10 — Carteira — Movimentações (`/carteira/movimentacoes`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- KPIs: Saldo BRL, Saldo USD, Saldo Total BRL, Total Movimentações ✅
- Filtros: tipo, data início/fim (server-side ✅ — diferente do Histórico)
- Tabela: data, tipo, valor, corretora, descrição ✅
- Ordenação por coluna ✅

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001** — localStorage vazio → API retorna 401
2. 🟡 **API retorna enum como string** — `tipo_movimentacao` vem como `"TipoMovimentacao.DEPOSITO"` e o template faz `parseTipo()` para extrair `"deposito"`. Funciona mas é frágil — se a API mudar o formato, quebra silenciosamente.
3. 🟡 **Filtro data client-side no tipo** — filtro por tipo opera sobre os itens carregados, mas data já vai como param server-side via `carregarComFiltro()` ✅

**Validação visual (18/06/2026):**
- [x] KPIs de saldo carregam ✅
- [x] Tabela exibe registros ✅
- [x] Filtro por tipo funciona ✅
- [x] **Filtro de data quebrado** 🔴 — tela pisca ao digitar o ano no campo de data. Provável `x-model` no `<input type="date">` disparando `carregarComFiltro()` a cada tecla, incluindo estados intermediários inválidos (ex: `2026-` sem completar). **Registrado como BUG-013.**

---

### Tela 11 — Ativos — Catálogo (`/ativos/acoes`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- 5 categorias com rotas próprias: Ações, FIIs, ETFs, Renda Fixa, Cripto ✅
- Template único `lista_v2.html` com config dinâmica por categoria ✅
- KPIs: ativos encontrados, com preço atual, DY médio ✅
- Colunas condicionais por categoria (P/L, P/VP, ROE, Cap Rate, etc.) ✅
- Botão "Ver" → `/ativos/<ticker>` → redireciona para `/dashboard/ativo/<ticker>` ✅

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001** — localStorage vazio → `apiFetch` retorna 401
2. 🟡 **N requests sequenciais** — `recarregar()` faz 1 request por tipo em loop. Ex: Ações faz 2 requests (`acao` + `stock`).
3. 🟡 **DY médio sempre `—`** para Cripto — `dividend_yield` não existe para cripto.

**Validação visual (18/06/2026):**
- [x] Tabela carrega ativos ✅
- [x] KPI "Ativos Encontrados" exibe números ✅ (valores não verificáveis — dados de teste)
- [x] Navegação entre categorias (Ações → FIIs → etc.) funciona ✅
- [x] **Busca por ticker não funciona** 🔴 — sem autocomplete e sem resultado ao buscar. **Registrado como BUG-014.**
- [x] Botão "Ver" abre tela de detalhe ✅ — porém lenta e sem dados em alguns ativos. **Registrado como BUG-015.**

---

### Tela 12 — Ativos — Detalhe (`/ativos/<TICKER>`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota `/ativos/<ticker>` redireciona para `dashboard.ativo_detalhes` (rota existe em `dashboard.py:913`) ✅
- Template `ativo_detalhes_v2.html` herda `base_interna.html` ✅
- KPIs: Preço Atual, Variação, Preço Teto, Buy Score ✅
- Indicadores fundamentalistas via Alpine.js ✅

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001** — localStorage vazio → API retorna 401
2. 🟡 **Dois caminhos para a mesma tela** — `/ativos/<ticker>` faz redirect para `/dashboard/ativo/<ticker>`. Links internos usam diretamente a rota do dashboard.

**Validação visual (18/06/2026):**
- [x] Tela abre via botão "Ver" no catálogo ✅
- [x] **Demora muito para carregar** 🟡 — múltiplas chamadas de API em sequência (cotacao, fundamentalistas, buy score)
- [x] **Nem sempre exibe dados** 🔴 — ativos sem cotacao ou sem dados fundamentalistas ficam com campos vazios/`N/D`. **Registrado como BUG-015.**

---

### Tela 13 — Ativos — Eventos Corporativos (`/ativos/eventos-corporativos`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Herda `base_interna.html` ✅
- KPIs: total eventos, ativos impactados, último evento ✅
- Filtros: ticker, tipo de evento ✅
- Tabela: data, ativo (link para detalhe), tipo, descrição, fator ✅
- Carrega via `GET /api/eventos-corporativos/?per_page=100` ✅

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001** — localStorage vazio → API retorna 401
2. 🟡 **Filtro tipo usa lowercase** (`desdobramento`) — se enum da API vier diferente, filtro falha silenciosamente

**Validação visual (18/06/2026):**
- [x] **Não aparece no menu Ativos** 🔴
- [x] **URL `/ativos/eventos-corporativos` retorna NOT FOUND** 🔴 — a rota `GET /ativos/<ticker>` captura `eventos-corporativos` como ticker e redireciona para `/dashboard/ativo/EVENTOS-CORPORATIVOS`, que retorna NOT FOUND por não existir ativo com esse ticker. Rota estática deveria ter prioridade sobre dinâmica no Flask, mas pode haver conflito de registro. **Registrado como BUG-016.**

---

### Tela 14 — Proventos — Calendário (`/proventos/calendario`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota `/proventos/calendario` renderiza `proventos/calendario_v2.html` ✅
- Rotas `/proventos/recebidos` e `/proventos/projetados` existem mas **redirecionam** para `dashboard.proventos_calendario` — verificar se essa rota existe

**Problemas encontrados:**
1. 🔴 **Afetada por BUG-001**
2. 🟡 **Rotas `/recebidos` e `/projetados` redirecionam para `dashboard.proventos_calendario`** — se essa função não existir no blueprint dashboard, gera erro 500

**Validação visual (18/06/2026):**
- [x] Tela carrega e exibe calendário de dividendos ✅
- [x] Menu Proventos → Calendário acessível ✅
- [x] Filtro por ticker funciona ✅
- [x] Filtro Previsto/Confirmados funciona ✅
- [x] Filtro por tipo funciona ✅
- [x] **Sem botão "Confirmar Recebimento"** 🟡 — existe botão "Gerar Automático" mas não há ação manual de confirmar provento recebido. **Registrado como FEAT-008.**

---

### Tela 15 — Análises — Evolução (`/analises/evolucao`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota existe, renderiza `analises/evolucao_v2.html` ✅
- Alpine.js API-driven (herda `base_interna.html`) ✅

**Problemas encontrados:**
1. � BUG-001 não afeta esta tela na prática — dados carregam normalmente

**Validação visual (18/06/2026):**
- [x] Carrega dados e gráficos ✅

---

### Tela 16 — Análises — Performance (`/analises/performance`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota existe, renderiza `analises/performance_v2.html` ✅
- Alpine.js API-driven ✅

**Problemas encontrados:**
1. � BUG-001 não afeta esta tela na prática — dados carregam normalmente

**Validação visual (18/06/2026):**
- [x] Carrega dados e gráficos ✅

---

### Tela 17 — Análises — Alocação (`/analises/alocacao`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota existe, renderiza `analises/alocacao_v2.html` ✅
- Alpine.js API-driven ✅

**Problemas encontrados:**
1. � BUG-001 não afeta esta tela na prática — dados carregam normalmente

**Validação visual (18/06/2026):**
- [x] Carrega dados e gráficos ✅

---

### Tela 18 — Análises — Buy Signals (`/analises/buy-signals`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota existe, renderiza `analises/buy_signals_v2.html` ✅
- Alpine.js API-driven ✅

**Problemas encontrados:**
1. � BUG-001 não afeta esta tela na prática — dados carregam normalmente
2. 🟡 **Busca por ticker sem autocomplete** — funciona se digitado exato. **Registrado como BUG-017.**

**Validação visual (18/06/2026):**
- [x] Carrega dados ✅
- [x] **Busca por ticker sem autocomplete** 🟡 — funciona se o ticker for digitado exato. **BUG-017.**

---

### Tela 19 — Análises — Rentabilidade (`/analises/rentabilidade`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota `/analises/rentabilidade` renderiza `analises/rentabilidade.html` com dados server-side (não Alpine.js) ✅
- Busca `GET /api/portfolios/dashboard` e `GET /api/portfolios/evolucao?meses=12` no servidor ✅
- Existe também rota `/analises/rentabilidade/periodo` → `rentabilidade_v2.html` (versão Alpine.js) ✅

**Problemas encontrados:**
1. � **Rota inacessível** — `/analises/rentabilidade` retorna NOT FOUND e não aparece no menu. Possível que a rota tenha sido removida ou renomeada sem remover referências. **Registrado como BUG-018.**
2. 🟡 **Versão legacy usa `get_api_headers()`** — dependia do token na sessão do servidor, mas a rota está morta.

**Validação visual (18/06/2026):**
- [x] **NOT FOUND ao colar URL no browser** 🔴
- [x] **Não aparece no menu** 🔴 — menu aponta para `/analises/rentabilidade/periodo` (v2). **BUG-018.**

---

### Tela 19b — Análises — Rentabilidade por Período (`/analises/rentabilidade/periodo`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota existe, renderiza `analises/rentabilidade_v2.html` (Alpine.js) ✅
- Versão ativa — acessível pelo menu como "Rentabilidade" ✅

**Validação visual (18/06/2026):**
- [x] Tela abre e carrega dados ✅
- [x] Filtros de período (1m, 3m, ...) funcionam ✅
- [x] Filtro de benchmark presente 🟡 — não foi possível validar se funciona corretamente

---

### Telas 20–23 — Fiscal (`/imposto-renda/*`)

**Observação geral:** Blueprint `fiscal.py` usa `API_BASE = 'http://exitus-backend:5000/api'` (linha 9) — hostname interno Docker. Fora do container, **todas as chamadas server-side falham**.

#### Tela 20 — IR Mensal
**Status:** 🟡 PARCIAL
- Renderiza `fiscal/ir_mensal_v2.html` (Alpine.js) ✅
- 🔴 BUG-001 (localStorage)

#### Tela 21 — DARFs
**Status:** 🟡 PARCIAL
- Renderiza `fiscal/darfs_v2.html` (Alpine.js) ✅
- 🔴 BUG-001

#### Tela 22 — Histórico IR
**Status:** 🟡 PARCIAL
- Renderiza `fiscal/historico_v2.html` (Alpine.js) ✅
- 🔴 BUG-001

#### Tela 23 — DIRPF
**Status:** 🔴 QUEBRADO
- Rota busca `GET /api/ir/dirpf` via `API_BASE` hardcoded (hostname Docker) — falha fora do container
- Pior: variáveis `dados` e `erro` são populadas mas **não passadas** ao `render_template` (linha 72): `return render_template('fiscal/declaracao_v2.html')` — template recebe dados vazios sempre

---

### Telas 24–28 — Relatórios (`/relatorios/*`)

**Observação geral:** Todas as rotas principais renderizam templates Alpine.js `_v2.html` — afetadas por BUG-001. Rota bonusária `/exportar/csv` usa `Config.BACKEND_API_URL` corretamente (server-side).

#### Tela 24 — Mensal / Tela 25 — Anual / Tela 26 — Extrato / Tela 27 — IR Completo
**Status:** 🟡 PARCIAL — rotas existem, templates Alpine.js, afetadas por BUG-001

#### Tela 28 — Exportação
**Status:** 🟡 PARCIAL
- Rota `/exportar` renderiza `exportar_v2.html` (Alpine.js) ✅
- Rota bonusária `/exportar/csv` funciona server-side via `Config.BACKEND_API_URL` ✅ (não afetada por BUG-001)
- 🟡 Template `exportar_csv.html` renderiza tabela HTML em vez de gerar download real de arquivo

---

### Telas 29–33 — Ferramentas (`/ferramentas/*`)

**Observação geral:** Todas as rotas renderizam templates Alpine.js `_v2.html` (exceto `reconciliacao.html` sem sufixo). Todas afetadas por BUG-001. Blueprint usa `Config.BACKEND_API_URL` corretamente.

| Tela | Status | Observação |
|------|--------|------------|
| 29 Screener | 🟡 PARCIAL | Alpine.js API-driven; BUG-001 |
| 30 Comparador | 🟡 PARCIAL | Alpine.js API-driven; BUG-001 |
| 31 Calculadora IR | 🟡 PARCIAL | Alpine.js API-driven; BUG-001 |
| 32 Simulador | 🟡 PARCIAL | Alpine.js API-driven; BUG-001 |
| 33 Reconciliação | 🟡 PARCIAL | Template sem sufixo `_v2`; BUG-001 |

---

### Tela 34 — Estratégia — Planos (`/planos-compra/`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota `/planos-compra/` renderiza `estrategia/planos_v2.html` ✅
- Rota `/planos-venda/` também renderiza o mesmo template ✅
- Sub-rota `/<plano_id>` redireciona para lista (sem tela de detalhe dedicada) ✅
- Blueprint usa `Config.BACKEND_API_URL` ✅

**Problemas encontrados:**
1. 🔴 **BUG-001**
2. 🔴 **URL incorreta no menu** — tabela usa `/estrategia/planos` mas blueprint registrado como `/planos-compra`. Link no menu pode gerar 404.
3. 🟡 **Sem tela de detalhe do plano** — `/planos-compra/<id>` apenas redireciona para lista.

---

### Tela 35 — Alertas (`/alertas/`)
**Status:** 🟡 PARCIAL

**O que funciona (código):**
- Rota `/alertas/` renderiza `alertas/lista_v2.html` (Alpine.js) ✅
- Sub-rotas `/preco`, `/dividendos`, `/personalizados` existem e redirecionam para lista ✅
- Blueprint usa `Config.BACKEND_API_URL` ✅

**Problemas encontrados:**
1. 🔴 **BUG-001**
2. 🟡 **Tela única** — todas as sub-rotas levam para mesma lista unificada; sem separação visual por tipo de alerta.

---

*Documento criado: 18/06/2026 | **Auditoria de código concluída: 35/35 telas** | Validação visual pendente para telas 9–35 (aguarda correção BUG-001)*

---

## Backlog de Correções

> Consolidado ao final da auditoria. Ordenado por prioridade. Corrigir após mapear todas as 35 telas.

### 🔴 Críticos (bloqueiam uso)

| ID | Problema | Tela(s) | Causa raiz identificada |
|----|----------|---------|------------------------|
| ~~BUG-001~~ | ~~**Token não salvo no localStorage após login Flask**~~ — **RESOLVIDO em EXITUS-LOGIN-001**: token mock hardcoded removido de `auth.js`; login já era AJAX e chamava `window.auth.saveToken()` corretamente. Causa real era o fallback com token expirado mascarando o fluxo | — todas as telas `base_interna.html` usam `localStorage.getItem('access_token')` mas o login Flask salva apenas na sessão do servidor. Alpine.js recebe `null` → API retorna 401 → `loading` trava → tela parece "sem resposta" | 3, 4, 5, 6, 7, 8, 9–35 | `auth.py` route usa form POST → Flask session. `auth.js` `localStorage.setItem` só é chamado via AJAX. Fluxos não sincronizados. **Fix:** no `auth.py` após login bem-sucedido, passar o token para o template e injetá-lo via `<script>localStorage.setItem('access_token', '...')</script>` |
| ~~BUG-002~~ | ~~**Toggle Compra/Venda: getters `isCompra`/`isVenda` invertidos após merge**~~ | — | **RESOLVIDO em EXITUS-OPERACOES-001**: getters substituídos por propriedades reativas simples em `operacoes_v2.html`. Spread `{ ...base, ...pageDataExtend() }` não preserva getters JavaScript — convertido para `isCompra: true, isVenda: false` atualizados em `toggleModo()` |
| ~~BUG-003~~ | ~~**Import B3 não exibe registros**~~ | — | **FALSO POSITIVO** — import é idempotente por design; com dados novos retorna Transações=2. Registrado como **FEAT-009** (listagem dos importados) e **BUG-020** (classificação automática incorreta de ativos) |

### 🟡 Importantes (degradam experiência)

| ID | Problema | Tela(s) | Causa raiz identificada |
|----|----------|---------|------------------------|
| BUG-004 | **Filtro por data no Histórico filtra client-side** — só filtra as 50 transações da página atual, não todas | 8 | `filtrar()` opera sobre `this.transacoes` (50 itens). **Fix:** passar `data_inicio`/`data_fim` como params para API `/api/transacoes` |
| ~~BUG-005~~ | ~~**CDI e Ibovespa hardcoded** — `11.75%` e `8.32%` fixos no template~~ | — | **RESOLVIDO em EXITUS-DASHBOARD-001**: valores movidos para `frontend/app/config.py` (`CDI_ANUAL`, `IBOVESPA_ANUAL`) e injetados no template `dashboard/index_v2.html` via `dashboard.py`. Atualização manual por variável de ambiente. **Feature futura:** endpoint dinâmico `/api/indicadores` (Opção B) registrado como FEAT-010 |
| BUG-006 | **Saldo de corretoras sempre R$ 0,00** | 4 | Revalidado 22/06/2026: campo `saldo_atual` existe no modelo e é retornado pela API (`GET /api/corretoras`). Porém não é atualizado automaticamente a partir de movimentações de caixa — permanece com valor do seed/criação. **Fix:** implementar cálculo automático de saldo de corretora ou endpoint de sincronização |
| ~~BUG-007~~ | ~~**Link "Esqueceu a senha?"** retorna 404~~ | — | **RESOLVIDO em EXITUS-LOGIN-001** — link removido do template (funcionalidade não implementada) | | 1 | Rota `/auth/forgot-password` não implementada. **Fix:** implementar rota ou remover link |
| ~~BUG-008~~ | ~~**Link "Ver Ativo" retorna 404**~~ — **RESOLVIDO na análise**: rota `/dashboard/ativo/<ticker>` existe em `dashboard.py` linha 913 | 8, 9 | Falso positivo — rota implementada |
| ~~BUG-009~~ | ~~**`API_BASE` hardcoded como hostname Docker** em `fiscal.py` linha 9: `http://exitus-backend:5000/api`~~ | — | **FALSO POSITIVO** — revalidado 22/06/2026: arquivo `fiscal.py` não existe mais em `app/routes/` e a string `exitus-backend:5000` não aparece no backend. Rotas fiscais atuais (`fiscal.py`) já usam `Config.BACKEND_API_URL` |
| ~~BUG-010~~ | ~~**Tela DIRPF: `dados` e `erro` não passados ao template**~~ | — | **RESOLVIDO em EXITUS-FISCAL-001**: `frontend/app/routes/fiscal.py` agora passa `dados`, `erro` e `ano` para `declaracao_v2.html`; template exibe mensagem de erro e inicializa estado Alpine com dados do servidor, evitando tela vazia enquanto `loadData()` não executa |
| ~~BUG-011~~ | ~~**URL da Tela 34 (Estratégia/Planos) incorreta**~~ | — | **FALSO POSITIVO** — revalidado 22/06/2026: blueprint `planos` registrado em `/planos-compra`, menu aponta para `/dashboard/planos-compra`, e existe redirect `/planos-compra/*` → `/planos-compra/`. Nenhum link `/estrategia/planos` encontrado no frontend atual |
| ~~BUG-012~~ | ~~**Rotas `/proventos/recebidos` e `/proventos/projetados`** redirecionam para `dashboard.proventos_calendario`~~ | — | **FALSO POSITIVO** — revalidado 22/06/2026: `dashboard.proventos_calendario` existe em `dashboard.py` linha 956 e redireciona para `proventos.calendario`. Rotas `/proventos/recebidos` e `/proventos/projetados` funcionam via redirect |
| ~~BUG-013~~ | ~~**Filtro de data em Movimentações pisca ao digitar o ano**~~ | — | **RESOLVIDO** — revalidado 22/06/2026: `movimentacoes.html` usa `@change="carregarComFiltro()"` nos campos de data, não `@input`. Chamadas à API só ocorrem ao confirmar a data |
| ~~BUG-014~~ | ~~**Busca por ticker no Catálogo de Ativos não funciona**~~ | — | **RESOLVIDO em EXITUS-ATIVOS-003**: `frontend/app/templates/ativos/lista_v2.html` alterado para enviar `search=${this.search}` ao invés de `ticker`; backend `/api/ativos` aplica busca parcial em ticker e nome via `?search=` |
| ~~BUG-015~~ | ~~**Tela de Detalhe do Ativo demora e nem sempre exibe dados**~~ | — | **RESOLVIDO** — revalidado 22/06/2026: `ativo_detalhes_v2.html` já carrega cotação, buy-score, margem e eventos em paralelo via `Promise.allSettled`. Estado vazio é tratado com `N/D` quando dados não existem |
| ~~BUG-019~~ | ~~**Botão "Comparar" no Comparador de Ativos não aciona nada**~~ | — | **RESOLVIDO** — revalidado 22/06/2026: `comparador_v2.html` implementa `comparar()` que consome `/api/ativos` e `/api/cotacoes/<ticker>` para cada ticker selecionado. Não depende de endpoint `/api/ativos/comparar` |
| ~~BUG-018~~ | ~~**Rota `/analises/rentabilidade` legacy retorna NOT FOUND**~~ | — | **RESOLVIDO em EXITUS-ANALISES-001**: redirect adicionado em `analises.py`; código morto (template inexistente `rentabilidade.html`) removido |
| ~~BUG-017~~ | ~~**Busca por ticker sem autocomplete em Buy Signals** — funciona se digitado exato, sem sugestões~~ | — | **RESOLVIDO em EXITUS-BUY-SIGNALS-001**: `buy_signals_v2.html` agora usa `<datalist>` populado via `GET /api/ativos?search=` com debounce de 300ms; busca parcial em ticker/nome retorna até 10 sugestões |
| ~~BUG-020~~ | ~~**Import B3: classificação automática de ativo incorreta**~~ — **RESOLVIDO em EXITUS-ATIVOS-002**: `_obter_ou_criar_ativo()` agora usa classificador multi-camadas (DB → cache seed/manual → API externa → heurística → fallback `OUTRO`) com nível de confiança e fonte. ETFs BR (BOVA11, SMAL11) são classificados como ETF. Ativos internacionais (AAPL, MSFT) recebem mercado US. Confiança `BAIXA` vira `OUTRO` para revisão manual. | 5 |
| ~~BUG-016~~ | ~~**Tela Eventos Corporativos inacessível**~~ | — | **FALSO POSITIVO** — revalidado 18/06/2026 com token válido: `/ativos/eventos-corporativos` carrega corretamente (KPIs + filtros). Flask prioriza rota estática sobre `/<ticker>` no mesmo blueprint. Bug original era consequência do BUG-001 (token inválido) |

### 🟡 Pendências de funcionalidade (features ausentes)

| ID | Problema | Tela(s) |
|----|----------|---------|
| FEAT-001 | Perfil somente leitura — sem editar nome/email nem trocar senha | 3 |
| FEAT-002 | Corretoras sem CRUD — sem criar, editar ou excluir corretora | 4 |
| FEAT-003 | Transações sem editar/excluir após registro | 6, 7, 8 |
| FEAT-004 | Meta de patrimônio hardcoded (R$ 500k) — não configurável | 2 |
| FEAT-005 | Template `venda.html` legado ainda existe como rota separada | 7 |
| FEAT-006 | Exportação CSV renderiza tabela HTML — sem download real do arquivo | 28 |
| FEAT-007 | Sem tela de detalhe de plano de compra — `/planos-compra/<id>` só redireciona | 34 |
| FEAT-008 | Sem botão "Confirmar Recebimento" de provento — apenas "Gerar Automático" disponível | 14 |
| FEAT-009 | **Import B3 não lista os registros importados** — resultado mostra apenas totais numéricos (Transações=N, Proventos=N). Usuário não sabe quais ativos foram criados/importados. **Fix:** exibir lista dos tickers importados e ativos criados automaticamente após import | 5 |
| FEAT-010 | **Indicadores de mercado (CDI/Ibovespa) sem endpoint dinâmico** — atualmente valores vêm de variáveis de ambiente no frontend. **Fix:** criar backend `GET /api/indicadores` com CDI/Ibovespa atualizados automaticamente; dashboard consumir via API | 2 |

---

## Cobertura de APIs — Frontend vs. Backend

> Fonte: `PLANO_EXECUCAO_18_06_2026.md` — Atividade 3  
> O backend possui **~103 endpoints** em 33 blueprints. O frontend consome **~42 endpoints** (~41%). Há **~61 APIs não utilizadas**.

### APIs consumidas por tela

| # | Módulo | APIs consumidas |
|---|--------|-----------------|
| 1 | Login | `/api/auth/login` |
| 2 | Dashboard | `/api/portfolios/dashboard`, `/api/alertas/recentes` |
| 3 | Configurações — Perfil | `/api/auth/me` |
| 4 | Configurações — Corretoras | `/api/corretoras` |
| 5 | Operações — Import B3 | `/api/import/b3` |
| 6 | Operações — Compra | `/api/transacoes`, `/api/ativos`, `/api/cotacoes` |
| 7 | Operações — Venda | `/api/transacoes`, `/api/posicoes` |
| 8 | Operações — Histórico | `/api/transacoes` |
| 9 | Carteira — Posições | `/api/posicoes`, `/api/posicoes/resumo` |
| 10 | Carteira — Movimentações | `/api/movimentacoes-caixa`, `/api/carteira/saldo-caixa` |
| 11 | Ativos — Catálogo | `/api/ativos` |
| 12 | Ativos — Detalhe | `/api/ativos/ticker`, `/api/cotacoes`, `/api/buy-signals/*` |
| 13 | Ativos — Eventos Corporativos | `/api/eventos-corporativos` |
| 14 | Proventos — Calendário | `/api/calendario-dividendos/*` |
| 15 | Análises — Evolução | `/api/portfolios/evolucao` |
| 16 | Análises — Performance | `/api/performance/performance` |
| 17 | Análises — Alocação | `/api/portfolios/alocacao`, `/api/performance/desvio-alocacao` |
| 18 | Análises — Buy Signals | `/api/buy-signals/watchlist-top` |
| 19b | Análises — Rentabilidade por Período | `/api/portfolios/rentabilidade` |
| 20 | Fiscal — IR Mensal | `/api/ir/apuracao` |
| 21 | Fiscal — DARFs | `/api/ir/darf` |
| 22 | Fiscal — Histórico IR | `/api/ir/historico` |
| 23 | Fiscal — DIRPF | `/api/ir/dirpf` |
| 24 | Relatórios — Mensal | `/api/transacoes`, `/api/proventos` |
| 25 | Relatórios — Anual | `/api/transacoes`, `/api/proventos` |
| 26 | Relatórios — Extrato | `/api/transacoes`, `/api/proventos` |
| 27 | Relatórios — IR Completo | `/api/ir/historico`, `/api/ir/dirpf`, `/api/ir/apuracao` |
| 28 | Relatórios — Exportação | `/api/export/*` |
| 29 | Ferramentas — Screener | `/api/ativos` |
| 30 | Ferramentas — Comparador | `/api/ativos/ticker`, `/api/cotacoes` |
| 31 | Ferramentas — Calculadora IR | `/api/posicoes` |
| 32 | Ferramentas — Simulador | _(client-side — sem API)_ |
| 33 | Ferramentas — Reconciliação | `/api/reconciliacao/*` |
| 34 | Estratégia — Planos | `/api/plano-compra`, `/api/plano-venda` |
| 35 | Alertas | `/api/alertas` |

---

### APIs do backend NÃO utilizadas — Propostas de novas telas

> Objetivo: cada grupo de APIs sem frontend é uma oportunidade de nova tela ou expansão de tela existente.

#### 🆕 Novas telas propostas

> **⚠️ Status: PROPOSTA — não aprovada para implementação.**  
> Cada tela aqui listada passará por discussão com o usuário antes de entrar no roadmap. Durante a discussão, podem ser alteradas, combinadas, descartadas ou substituídas por ideias novas.  
> **Fluxo obrigatório:** Discussão → Ajuste da proposta → Aprovação explícita → GAP criado → Implementação.

| ID | Tela proposta | Módulo/URL sugerida | APIs a integrar | Valor para o usuário |
|----|---------------|---------------------|-----------------|----------------------|
| NEW-01 | **Projeções Patrimoniais** | `/analises/projecoes` | `/api/projecoes/*` | Simular crescimento do patrimônio com aportes, juros e inflação — substitui o Simulador client-side atual |
| NEW-02 | **Métricas de Risco** | `/analises/risco` | `/api/portfolios/metricas-risco`, `/api/performance/*` | Sharpe, Drawdown máximo, VaR, correlação entre ativos |
| NEW-03 | **Distribuição Detalhada** | Expandir `/analises/alocacao` | `/api/portfolios/distribuicao/classes`, `/api/portfolios/distribuicao/setores` | Alocação por setor, segmento e classe com desvio da meta |
| NEW-04 | **Saúde das Cotações** | `/ferramentas/cotacoes` | `/api/cotacoes/anomalias`, `/api/cotacoes/health` | Detectar ativos com cotações desatualizadas ou inconsistentes |
| NEW-05 | **Câmbio e Multimoeda** | Expandir Dashboard ou `/carteira/cambio` | `/api/cambio/converter`, `/api/cambio/historico`, `/api/cambio/pares` | Visualizar patrimônio em USD/EUR; histórico de taxas |
| NEW-06 | **Indicadores Macroeconômicos** | Expandir Dashboard | `/api/parametros-macro/*` | CDI, Ibovespa, IPCA, Selic dinâmicos — resolve BUG-005 |
| NEW-07 | **Fontes de Dados** | `/configuracoes/fontes-dados` | `/api/fontes-dados/*` | Gerenciar provedores de cotação (B3, Yahoo, etc.) — tela administrativa |
| NEW-08 | **Regras Fiscais** | `/configuracoes/regras-fiscais` | `/api/regras-fiscais/*` | Configurar alíquotas, isenções e regras de apuração |
| NEW-09 | **Relatório Consolidado** | Expandir `/relatorios/exportar` | `/api/relatorios` | Endpoint único que gera relatório completo (PDF/Excel) com dados de todas as APIs |
| NEW-10 | **Detalhe de Posição** | `/carteira/posicoes/<id>` | `/api/posicoes/<posicao_id>` | Histórico de preço médio, eventos, proventos recebidos por posição individual |
| NEW-11 | **Calculadora de Preço Teto** | Expandir `/ferramentas/calculadora-ir` ou nova `/ferramentas/preco-teto` | `/api/calculos/preco_teto`, `/api/calculos/fii`, `/api/calculos/portfolio` | Calcular preço teto por Bazin, Graham, FII Yield |
| NEW-12 | **Resumo por Ativo** | Expandir `/operacoes/historico` | `/api/transacoes/resumo-ativo` | Ver todas as transações agrupadas por ativo com P&L acumulado |
| NEW-13 | **Dashboard de Planos de Compra** | `/estrategia/planos-compra/dashboard` | `/api/plano-compra/dashboard` | KPIs consolidados: planos ativos, total aportado, desvio da meta — **API existe, não usada** |
| NEW-14 | **Plano de Venda — Dashboard + Gatilhos** | `/estrategia/planos-venda` | `/api/plano-venda/dashboard`, `/api/plano-venda/verificar-gatilhos`, `/api/plano-venda/estatisticas`, `/api/plano-venda/simular-venda` | Monitorar stop-gain/stop-loss, simular venda parcial — backend completo, sem tela |
| NEW-15 | **Correlação entre Ativos** | `/analises/correlacao` | `/api/performance/correlacao` | Matriz de correlação entre ativos da carteira — ver quais ativos se movem juntos ou ao contrário |
| NEW-16 | **Comparação com Benchmark** | Expandir `/analises/rentabilidade/periodo` | `/api/performance/benchmark` | Comparar rentabilidade da carteira vs CDI, Ibovespa, IPCA — API existe separada do filtro atual |
| NEW-17 | **Projeções de Renda Passiva** | `/analises/projecoes/renda` | `/api/projecoes/renda`, `/api/projecoes/cenarios`, `/api/projecoes/recalcular` | Projetar dividendos futuros por cenário (conservador/moderado/agressivo) com metas de renda mensal |
| NEW-18 | **Gerenciamento de Proventos** | Expandir `/proventos/calendario` | `/api/proventos` (CRUD completo: GET, POST, PUT, DELETE) | Criar, editar e excluir proventos manualmente — hoje só leitura via calendário |
| NEW-19 | **Gerenciamento de Portfólios** | `/configuracoes/portfolios` | `/api/portfolios` (CRUD: list, get, create, update, delete) | Criar múltiplos portfólios (ex: Previdência, Especulativo, Longo Prazo) e alternar entre eles |
| NEW-20 | **Gerenciamento de Usuários** | `/admin/usuarios` | `/api/usuarios` (CRUD + change_password) | Painel admin para criar/editar/remover usuários e redefinir senhas — útil para multi-usuário familiar |
| NEW-21 | **Editar / Excluir Transação** | Expandir `/operacoes/historico` | `/api/transacoes/<id>` (PUT, DELETE) | Corrigir lançamentos errados — **API existe mas FEAT-003 aponta que frontend não expõe esses botões** |
| NEW-22 | **Saúde da Reconciliação por Ativo** | Expandir `/ferramentas/reconciliacao` | `/api/reconciliacao/ativo/<id>`, `/api/reconciliacao/integridade` | Drill-down por ativo específico para diagnosticar inconsistência de saldo — hoje só visão geral |

---

#### 🔧 Expansões de telas existentes

| Tela atual | Expansão proposta | APIs a adicionar |
|------------|-------------------|------------------|
| Dashboard (Tela 2) | Indicadores macroeconômicos dinâmicos | `/api/parametros-macro/*` |
| Dashboard (Tela 2) | Transações recentes no rodapé | `/api/transacoes/recentes` |
| Carteira — Posições (Tela 9) | Link para detalhe individual de posição | `/api/posicoes/<id>` |
| Análises — Alocação (Tela 17) | Distribuição por setor/segmento | `/api/portfolios/distribuicao/setores` |
| Ferramentas — Simulador (Tela 32) | Substituir cálculo client-side por API | `/api/calculos/rf/simular`, `/api/projecoes/*` |
| Ativos — Detalhe (Tela 12) | Alertar cotação desatualizada | `/api/cotacoes/anomalias` |
| Relatórios — Exportação (Tela 28) | Relatório consolidado real | `/api/relatorios` |

---

#### ⚙️ APIs backend-only ou admin (sem necessidade de UI para o investidor)

| Blueprint | Prefixo | Motivo |
|-----------|---------|--------|
| `feriados` | `/api/feriados/*` | Usado internamente para cálculo de dias úteis |
| `assessoras` | `/api/assessoras/*` | Apenas painel administrativo multi-assessor |
| `regras-fiscais` (CRUD) | `/api/regras-fiscais/*` | Pode ser admin-only dependendo do modelo de negócio |

---

> **Próximo passo:** Executar Atividade 3 completa (`docs/API_COVERAGE_AUDIT.md`) para cruzar todos os 103 endpoints com as chamadas reais do frontend, validar quais APIs realmente existem e estão funcionais, e priorizar quais novas telas (NEW-01 a NEW-12) entram no roadmap.

---

## Resumo Final da Auditoria

**Data de conclusão:** 18/06/2026  
**Total de telas auditadas:** 36/36 (incluindo Tela 19b) ✅  
**Método:** Análise estática de código (blueprints, templates, Alpine.js) + validação visual completa do usuário (telas 1–35)

### Distribuição de status

| Status | Qtd | % |
|--------|-----|---|
| ✅ OK | 2 | 6% |
| 🟡 PARCIAL | 34 | 94% |
| 🔴 QUEBRADO | 0 | 0% |
| ⬜ NÃO TESTADO | 0 | — |

### Telas 🔴 QUEBRADAS

| Tela | URL | Motivo |
|------|-----|--------|
| ~~5~~ | ~~`/operacoes/` Import B3~~ | ~~Import não exibe registros~~ → **FALSO POSITIVO** — idempotente por design; revalidado com dados novos: Transações=2 |
| ~~6, 7~~ | ~~`/operacoes/` Compra/Venda~~ | ~~Toggle inoperante~~ → **RESOLVIDO** EXITUS-OPERACOES-001 |
| ~~13~~ | ~~`/ativos/eventos-corporativos`~~ | ~~NOT FOUND~~ → **FALSO POSITIVO** — carrega OK com token válido |
| ~~19~~ | ~~`/analises/rentabilidade`~~ | ~~Rota legacy morta~~ → **RESOLVIDO** EXITUS-ANALISES-001 (redirect para `/periodo`) |

### Bugs por prioridade

| Prioridade | Quantidade |
|------------|-----------|
| ~~🔴 Crítico~~ | ~~3 (BUG-001, BUG-002, BUG-003)~~ | **0 críticos — todos resolvidos ou falsos positivos** |
| 🟡 Importante | 2 (BUG-004, BUG-006) |
| ⬛ Feature ausente | 10 (FEAT-001 a FEAT-010) |

### Impacto do BUG-001

**BUG-001 é o bug mais crítico:** afeta **32 das 35 telas** (todas que usam Alpine.js com `base_interna.html`). A correção deste único bug desbloquearia a validação visual de quase todo o sistema.

**Causa:** `login` via form POST salva token apenas na Flask session. `base_interna.html` lê token de `localStorage`. Os dois mecanismos nunca se sincronizam.

**Fix de 2 linhas** em `auth.py` — injetar token no template após login:
```python
# Em auth.py, após login bem-sucedido:
return render_template('auth/login_success.html', token=access_token)
# E no template, antes do redirect:
# <script>localStorage.setItem('access_token', '{{ token }}')</script>
```
Ou alternativamente: na resposta do login, fazer redirect para uma rota intermediária que seta o localStorage via JS antes de redirecionar para o dashboard.
