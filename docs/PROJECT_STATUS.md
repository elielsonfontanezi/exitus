# 🚀 Exitus — Status do Projeto

> **Data:** 02/07/2026
> **Status:** 🟡 **SEED-MENU-001 implementado — aguarda walkthrough manual do usuário**
> **Versão:** v0.9.54

### 🔧 Últimas entregas (02/07/2026 — walkthrough checklist)
- **Walkthrough browser:** `walkthrough_menu_browser.py` + [`WALKTHROUGH_CHECKLIST_USUARIO.md`](WALKTHROUGH_CHECKLIST_USUARIO.md) (16 obrigatórias / 7 recomendadas / 19 amostra).
- Gate Go-Live: usuário valida no ritmo próprio; correções reportadas → commit por item.

### 🔧 Entregas anteriores (02/07/2026 — SEED-MENU-001)
- **SEED-MENU-001 🟡:** Cenário `test_menu_full` — loader estendido, JSON 47 ativos, scripts verify + walkthrough API.
- Walkthrough API: **36/36 OK** com `e2e_user` / `e2e_senha_123`.
- **4 testes** `test_scenario_loader.py`; suite **664 passed** (+4), falhas pré-existentes inalteradas.
- **Trilha A** permanece bloqueada até OK explícito do usuário no browser.

### 🔧 Entregas anteriores (01/07/2026 — docs VAL-PIPE-001)
- **VAL-PIPE-001 📋:** Plano validação pipeline + Valor Justo — [`PLANO_VALIDACAO_VALOR_JUSTO.md`](PLANO_VALIDACAO_VALOR_JUSTO.md).
- 4 camadas: cotações ≤15min, indicadores, histórico, golden datasets por perfil.
- Lacunas V-GAP-01..07 catalogadas; implementação de testes pendente.

### 🔧 Entregas anteriores (01/07/2026 — docs SEED-MENU-001)
- **SEED-MENU-001 📋:** Plano massa `test_menu_full` — [`PLANO_MASSA_TESTES_MENU.md`](PLANO_MASSA_TESTES_MENU.md).
- **AUDITORIA:** § Critério Go-Live Menu 100%; distinção código ✅ vs seed.
- **SEEDS.md:** `test_full` reclassificado; `test_menu_full` planejado.
- **Trilha A bloqueada** até OK manual do usuário com massa completa.

### 🔧 Entregas anteriores (01/07/2026 — Lote 7 + Trilha C)
- **FEAT-IR-COT ✅:** Calculadora IR — cotação automática via `GET /api/cotacoes/<ticker>`; tela 31 → OK.
- **SEED-EVENTOS-001 ✅:** `_seed_eventos_corporativos()` em `load_scenario.py`; 6 eventos test_full, 4 test_e2e; tela 13 → OK.
- **AUDITORIA encerrada:** 43 OK, 0 PARCIAL, 0 QUEBRADO; FEAT-011+ → `BACKLOG_PRODUTO.md`.
- **CONCENTRACAO-001 ✅:** `concentracao_service.py`, `GET /api/portfolios/concentracao`, painel em `alocacao_v2.html`; 5 testes.
- **CLEANUP-MIGRATIONS-001 ✅:** `backend/alembic/` arquivado em `backend/archive/alembic_legacy/`.
- **Fix testes:** circuit breaker registry + fixture IR 2026+ com regras fiscais.

### 🔧 Entregas anteriores (30/06/2026 — Lote 6)
- **REL-FIX-001 ✅ CONCLUÍDO:** relatórios 24–27 — params `data_inicio`/`data_fim`, `mes=YYYY-MM`, `per_page`; error states; 2 testes smoke.
- **STALE-002 ✅ CONCLUÍDO:** error states em evolução/performance; telas 15, 16, 19, 32, 33 → OK.
- **FISC-002 ✅ CONCLUÍDO:** histórico IR error state + retry; tela 22 → OK.
- **TOOL-001 ✅ CONCLUÍDO:** screener links `/ativos/`, empty/error; tela 29 → OK.
- Suite: **663 passed**, 0 failed, 6 skipped (+8 vs Lote 6).

### 🔧 Entregas anteriores (30/06/2026 — Lote 5)
- **FIX-HIST-001 ✅ CONCLUÍDO:** filtro data histórico — BE `func.date` + FE sem dupla filtragem; tela 8 → OK.
- **NEW-02 ✅ CONCLUÍDO:** `/analises/risco` — `get_metricas_risco()` + `risco_v2.html`; 2 testes.
- **NEW-01 ✅ CONCLUÍDO:** `/analises/projecoes` — projeções patrimoniais; simulador → redirect.
- **STALE-001 ✅ CONCLUÍDO:** telas 7, 10, 28, 35 revalidadas → OK.
- Suite: **653 passed**, 3 failed pré-existentes, 6 skipped (+4 vs Lote 4).

### 🔧 Entregas anteriores (30/06/2026 — Lote 4)
- **NEW-19 ✅ CONCLUÍDO:** `/configuracoes/portfolios` — CRUD portfolios; tab bar + menu; 3 testes endpoint.
- **NEW-20 ✅ CONCLUÍDO:** `/admin/usuarios` — CRUD usuários admin; menu Admin.
- **NEW-08 ✅ CONCLUÍDO:** `/configuracoes/regras-fiscais` — CRUD regras (mutations admin); 3 testes endpoint.
- **NEW-16 ✅ CONCLUÍDO:** Benchmark rentabilidade validado em `rentabilidade_v2.html`; estado de erro; 1 teste.
- Suite: **649 passed**, 3 failed pré-existentes, 6 skipped (+7 vs Lote 3).

### 🔧 Entregas anteriores (30/06/2026 — Lote 3)
- **NEW-11 ✅ CONCLUÍDO:** `/ferramentas/preco-teto` — calculadora valor justo + métodos + FII.
- **NEW-15 ✅ CONCLUÍDO:** `/analises/correlacao` — matriz heatmap; 2 testes endpoint.
- **NEW-17 ✅ CONCLUÍDO:** `ProjecaoService` real + `/analises/projecoes/renda`; 4 testes.
- **NEW-18 ✅ CONCLUÍDO:** Aba CRUD proventos em `calendario_v2.html`.
- **NEW-07 ✅ CONCLUÍDO:** `/configuracoes/fontes-dados` — CRUD fontes externas.
- **NEW-21 ✅ RESOLVIDO (stale):** editar/excluir já em histórico.
- Suite: **642 passed**, 3 failed pré-existentes, 6 skipped.
- **OPS-GIT-HTTPS-001 ✅ RESOLVIDO:** push de 6 commits (Lote 3 + docs ops) publicado em `origin/feature/frontend-bug-fixes` via PAT HTTPS (30/06/2026).

### 🔧 Entregas anteriores (30/06/2026 — Lote 2)
- **NEW-06 + FEAT-010 ✅ CONCLUÍDO:** `GET /api/indicadores/dashboard`; Dashboard consome CDI/IPCA/SELIC dinamicamente. 3 novos testes. Suite: **634 passed**.
- **NEW-12 ✅ CONCLUÍDO:** Drawer resumo por ativo em `historico.html` via `/api/transacoes/resumo-ativo/<id>`.
- **NEW-10 ✅ CONCLUÍDO:** Rota `/carteira/posicoes/<id>` + `posicao_detalhe_v2.html`.
- **NEW-22 ✅ CONCLUÍDO:** Drill-down reconciliação por ativo em `reconciliacao.html`.
- **NEW-05 ✅ CONCLUÍDO:** Tela `/carteira/cambio` com conversor, pares e histórico.

### 🔧 Entregas anteriores (30/06/2026 — Lote 1)
- **NEW-04 ✅ CONCLUÍDO:** Tela `/ferramentas/cotacoes` com health enriquecido + anomalias; KPIs, abas desatualizados/sem cotação/anomalias; refresh por ticker. 3 novos testes. Suite: **632 passed** (baseline +3).
- **FEAT-009 ✅ CONCLUÍDO:** Import B3 retorna `tickers_importados` e `ativos_novos`; badges em `operacoes_v2.html`. 3 novos testes. Suite: **629 passed**.
- **NEW-14 ✅ CONCLUÍDO:** Aba Venda em `planos_v2.html` integrada com dashboard, gatilhos e estatísticas. 5 novos testes. Suite: **626 passed**.
- **NEW-13 ✅ CONCLUÍDO:** `planos_v2.html` integrado com `GET /api/plano-compra/dashboard` — KPIs (planos ativos, aporte mensal, total investido, progresso médio, desvio da meta), painel Próximos Aportes, fallback para listagem. Backend: `progresso_medio` + `desvio_meta_percentual` no resumo. Rota `/planos-compra/dashboard`. 2 novos testes. Suite: **621 passed** (baseline +2).
- **NEW-03 ✅ CONCLUÍDO:** `get_distribuicao_classes()` e `get_distribuicao_setores()` implementados em `portfolio_service.py` (endpoints existiam sem service). `alocacao_v2.html` com abas Por Classe | Por Segmento. 7 novos testes. Suite: **619 passed** (baseline +7).
- **REBALANCE-001 ✅ CONCLUÍDO:** Tabela `meta_alocacao` (migration `20260630_1200`) + model + schema. `rebalance_service.py`: metas (upsert), desvio (atual vs target), sugestões (comprar/vender). 3 endpoints novos em `portfolio_blueprint`: `GET/PUT /api/portfolios/meta-alocacao`, `GET /api/portfolios/rebalanceamento/sugestao`. `analise_service.analisar_performance_portfolio` delega para `rebalance_service` — `/api/performance/desvio-alocacao` retorna dados reais. `alocacao_v2.html` reformulada: editor de metas, barras com marcador de target, tabela com Desvio/Ajuste R$, painel sugestões. 19 novos testes. Suite: **612 passed, 3 failed pré-existentes, 6 skipped**.
- **BUG-VAL-004 ✅ CONCLUÍDO:** Migration DDL `20260630_1100` renomeia coluna `preco_teto → preco_teto_usuario`. Paridade `exitusdb + exitusdb_test` verificada. Model, schemas, seeds, blueprints, service e frontend atualizados. Alias confuso `preco_teto = valor_justo` removido das APIs. Labels frontend: "Teto (Usuário)" em detalhe de ativo; watchlist usa `valor_justo`. Suite: **593 passed, 3 failed pré-existentes, 6 skipped — sem regressão**.
- **BUG-VAL-005 ✅ CONCLUÍDO:** `valuation_service.py` criado (fonte única de valuation). Agregação: perfil + IQR ratio + mediana ponderada. API expõe `faixa_min/faixa_max/perfil`. `buy_signals_service` usa `valor_justo` calculado (não `preco_teto_usuario` estático). Frontend exibe faixa. 26 novos testes. Suite: **593 passed, 3 failed pré-existentes, 6 skipped**.
- **BUG-VAL-006 ✅ CONCLUÍDO:** Fórmula `1/cap_rate` substituída por `dy_anual/cap_rate` para FIIs/REITs. Guard defensivo adicionado. 2 novos testes em `test_calculos.py`. Suite: **567 passed**.

### 🔧 Correções anteriores (29/06/2026)
- **CURSORRULES-001.3 ✅ CONCLUÍDO:** `docs/MODULES.md` stub; links mortos corrigidos; PERSONAS deduplicado; AI_OPERATIONS v1.3 modelos Cursor; INDEX + MULTICLIENTE; limpeza refs legacy.
- **CURSORRULES-001.2 ✅ CONCLUÍDO:** REGRA #2 Plan/Agent; PERSONAS/INDEX alinhados; AI_OPERATIONS v1.2 (commit template, nota modelos Cursor, validação <=200 linhas).
- **CURSORRULES-001.1 ✅ CONCLUÍDO:** `.cursorrules` v3.1 — seção Plano de Controle (ROADMAP, AUDITORIA_FUNCIONAL, PROJECT_STATUS); REGRA #6 expandida; índices em AI_OPERATIONS; PERSONAS alinhado.
- **CURSORRULES-001 ✅ CONCLUÍDO:** `.cursorrules` v3.0 enxuto (~160 linhas) para Cursor Agent; conteúdo extenso migrado para `docs/AI_OPERATIONS.md`; `.windsurfrules` removido; refs atualizadas em PERSONAS, LESSONS_LEARNED, AUDITORIA_FUNCIONAL; L-OPS-001 registrada.
- **BUG-VAL-001 ✅ CONCLUÍDO:** Fórmulas Bazin/Graham/Gordon corrigidas em `calculos_blueprint.py`. Bazin: `dpa / 0.06` (threshold fixo Décio Bazin). Graham: `(eps * ...) * 4.4 / (k * 100)` (guard eps>0). Gordon: `dpa * (1+g)`. Tipo check estendido para `stock`, `stock_intl`, `unit`, `reit`. ITUB4 pt_medio: R$833 → R$49,89 ✅
- **SEED-MACRO-001 ✅ CONCLUÍDO:** `seed_parametros_macro.py` reescrito — UPSERT idempotente, 5 mercados reais: BR/B3 (rf=10.5%, g=5%, wacc=12%), US/NYSE, US/NASDAQ, EU/Euronext, JP/Tokyo. Banco validado: 5 rows em `parametros_macro`.
- **VALUATION-002 ✅ CONCLUÍDO:** `eps`/`fcf` reais populados para 15 ações BR + 6 US stocks via seed. Novas categorias: `ativos_intl_stocks` (ASML, SAP, MC, NESN, NOVO-B) + `ativos_cripto` (BTC, ETH, SOL, BNB). Total: 55 ativos seedados. Suite: **565 passed, 3 failed pré-existentes, 6 skipped**.
- **VALUATION-001 ✅ CONCLUÍDO (28/06/2026):** Campos `eps` (Numeric 10,4) e `fcf` (Numeric 15,2) adicionados ao modelo `Ativo`. Migration Alembic `20260628_1800` criada e aplicada. Suite: 543 passed.
- **BUY-REFINE-001 ✅ RESOLVIDO:** Bug `str(TipoAtivo.ACAO)` retornava `'tipoativo.acao'` → ITUB4 sempre caia no branch `padrao`. Fix: `.value` se Enum. ITUB4 agora mostra 4 métodos reais (Bazin/Graham/Gordon/DCF), Valor Justo R$499,51, Margem 91,5%. Radar chart removido (1 coluna, layout mais limpo). Optional chaining nos `x-text` de `precoTetoDetalhes` eliminou 4 TypeErrors. Manual atualizado com seção sobre as duas fontes de margem.
- **BUY-OPT-A ✅ IMPLEMENTADO:** Refatoração do layout Buy Signals — gauge removido, Score+Label+Barra em linha única no topo, radar na coluna esquerda (240px), card Valor Justo na coluna direita, badge de sinal inline com a porcentagem de margem, strip compacto de 4 componentes no rodapé. Padrão inspirado em Morningstar. Validado com ITUB4 sem erros de console.
- **BUY-VAL-003 ✅ IMPLEMENTADO:** Cartão "Preço vs Valor Justo" no Buy Signals detalha preço atual, valor justo médio, margem e barra comparativa; tabela expansível de métodos (Bazin, Graham, Gordon, DCF, Cap Rate) com parâmetros regionais; grid dos componentes (Margem, Z-Score, DY, Beta) com barras de progresso. Backend `/margem-seguranca/<ticker>` passou a retornar `preco_atual` e `preco_teto`, frontend consome `/api/calculos/preco_teto/<ticker>`. Manual do usuário passou a documentar o cálculo do Preço Teto.
- **Radar Chart ✅ IMPLEMENTADO:** Visualização gráfica dos componentes do Buy Score (Margem, Z-Score, DY, Beta) usando Chart.js. Backend modificado para retornar componentes individuais (value, points, max) via `calcular_buy_score()`. Endpoints `/buy-score/<ticker>` e `/analisar/<ticker>` atualizados. Radar chart mostra percentual de pontos obtidos vs máximo possível para cada componente. Validado com ITUB4 (100% em todos os componentes) e VALE3 (distribuição variada). `obter_watchlist_top()` corrigido para extrair score do novo formato de retorno.
- **HIST-002 ✅ VALIDADO:** Histórico de preços com fallback multi-provider implementado e validado no frontend. Z-Score calculado corretamente (-2.97 para ITUB4 usando 168 dias de histórico), Buy Score dinâmico (100 FORTE COMPRA, não mais 50 fixo). Correções de bugs encontrados durante validação: import de logger em buy_signals_service.py, campo z_score → zscore para consistência com frontend, lógica ajustada para usar histórico existente se ≥30 dias.
- **BUG-014/015/017 ✅ RESOLVIDOS indiretamente via BUG-009v2:** Busca por ticker no catálogo (BUG-014), detalhe de ativo lento/sem dados (BUG-015) e busca em Buy Signals (BUG-017) — todos causados pelo mesmo problema de `BROWSER_API_URL` vs `BACKEND_API_URL`. Após separação, todas as chamadas `apiFetch()` do Alpine.js funcionam. Auditoria: 13 OK, 23 PARCIAL, 0 QUEBRADO.
- **BUG-009v2 ✅ RESOLVIDO:** Dashboard e todas as telas do menu sem dados — `ERR_NAME_NOT_RESOLVED`. Causa raiz: `API_BASE_URL` nos templates usava `BACKEND_API_URL` (hostname interno do container `exitus-backend:5000`), que o browser não resolve. Solução: separar `BACKEND_API_URL` (server-side, container→container) de `BROWSER_API_URL` (client-side, browser→backend). 7 cenários de deploy documentados em `ARCHITECTURE.md`. L-FE-011 adicionada.
- **Dashboard ✅ RESOLVIDO:** CDI/Ibovespa via env vars (não hardcoded); meta via API `/api/auth/me`. FEAT-010 registrada com nota de análise minuciosa do backend antes de implementar endpoint dinâmico. Auditoria: 7 OK, 29 PARCIAL, 0 QUEBRADO.
- **Corretoras CRUD ✅ RESOLVIDO:** Após investigação, CRUD já estava totalmente implementado (frontend + backend). Auditoria desatualizada. Auditoria: 6 OK, 30 PARCIAL, 0 QUEBRADO.
- **BUG-013 ✅ RESOLVIDO:** Filtro de data pisca ao digitar ano. Após investigação, `x-model.lazy` já aplicado em `movimentacoes.html`. Auditoria tinha seções contraditórias — 3 linhas atualizadas para RESOLVIDO.
- **BUG-010 ✅ RESOLVIDO:** DIRPF não passa dados ao template. Após investigação, código já estava correto — rota passa `dados`/`erro`/`ano` e template injeta via `window.__DIRPF_DADOS__`. Auditoria desatualizada. Auditoria: 5 OK, 31 PARCIAL, 0 QUEBRADO.

### 🔧 Correções anteriores (26/06/2026)
- **BUG-019 ✅ RESOLVIDO:** Comparador de ativos não funciona. Causa raiz: `comparador_v2.html` usava `?limit=200` mas endpoint aceita `per_page`. Correção: `?limit=200` → `?per_page=200`. Auditoria: 4 OK, 32 PARCIAL, 0 QUEBRADO.
- **BUG-011 ✅ RESOLVIDO:** Planos de compra/venda sem entrada no menu. Dropdown "Estratégia" adicionado ao menu horizontal com Planos de Compra/Venda e Buy Signals/Alertas. Auditoria: 3 OK, 33 PARCIAL, 0 QUEBRADO.
- **TECH-001 ✅ RESOLVIDO:** ValueError refatorado para exceções tipadas em 5 services (`parametros_macro`, `rfcalc`, `cambio`, `ir`, `alerta`). Mapeamento: `ConflictError` (duplicatas) → 409, `NotFoundError` (não encontrado) → 404, `ValidationError` (validação) → 400. Testes atualizados: 567/574 passando (98.8%).
- **BUG-009 ✅ RESOLVIDO:** API_BASE hardcoded eliminado em 9 artefatos. Causa raiz: `base_interna.html` usava chave `FRONTEND_API_URL` (inexistente) em vez de `BACKEND_API_URL` — todos os 25 templates _v2 caíam no fallback `http://localhost:5000`. Fix: (1) `base_interna.html` corrigido — propaga para todos _v2; (2) `base.html` injeta `window.API_BASE_URL` globalmente — cobre admin templates; (3) `fiscal.py` usa `Config.BACKEND_API_URL`; (4) admin templates + `operacoes.js` usam `window.API_BASE_URL`. Sistema agora respeita `BACKEND_API_URL` do `.env` em todos os ambientes.

### 🔧 Correções anteriores (25/06/2026)
- **CONSTRAINT-001:** 10 CHECK constraints aplicadas em `transacao`, `evento_custodia`, `projecoes_renda`, `taxa_cambio` via migration Alembic; 17/17 testes passando; suite total 567/574 passed (98.8%)
- **P8 — Seed enrichment:** `test_e2e.json` enriquecido com ITUB4/ETFs, 3 planos compra, 2 planos venda, 12 meses histórico patrimônio, 6 eventos calendário dividendos, 3 projeções renda, 3 regras fiscais; `load_scenario.py` com 3 novos `_seed_*`
- **P3 — BUG-013:** `x-model.lazy` em filtros de data (movimentacoes.html); badge-cor corrigido
- **P4 — Fix suite de testes:** 554 passed / 14 failed (dívida técnica) / 6 skipped — upsert em fixtures vs seed persistente; fix `ir_service.py` (DIVIDENDO/JCP/ALUGUEL no filtro); alíquota JCP 15%→17.5%; `conftest.py` campos corretos em `MovimentacaoCaixa` e `Provento`; `load_scenario` conectando ao `exitusdb_test` via env `TESTING`; `test_scenarios_example` com `@pytest.mark.parametrize` correto
- **P1+P2 — DB/Alembic:** banco de testes recriado com enum completo; heads Alembic unificados em `20260624_1100`

### 🔧 Correções anteriores (23/06/2026)
- **Seeds:** Renda Fixa Brasil completa ao cenário test_full — 8 ativos RF (CDBs, Tesouro, Debêntures), 8 transações (R$ 49.599,60), 8 movimentações de caixa, 10 proventos/juros; base de teste agora 100% completa: 38 ativos, 56 transações, 42 proventos
- **FEAT-008:** Botão "Confirmar Recebimento" de provento já estava implementado — documentação atualizada; funcionalidade completa em calendario_v2.html
- **FEAT-007:** Tela de detalhe de plano de compra implementada — modal com informações completas; botão Detalhes na tabela; carregamento via API específica
- **FEAT-006:** Exportação CSV real implementada — download direto via HTTP headers; nova página /exportar com preview automático; compatibilidade mantida com ?preview=true
- **FEAT-005:** Template venda.html legado resolvido — suporte a ?venda=true em operacoes_v2.html; rota /venda redireciona mantendo compatibilidade; modo venda inicializa automaticamente com posições carregadas
- **EXITUS-DB-AUDIT-001:** Auditoria completa concluída — 30 tabelas validadas, seeds corrigidos, 39 arquivos documentação analisados; dados E2E carregados (3 usuários, 7 ativos, 4 transações)
- **EXITUS-PERFIL-001:** FEAT-004 resolvido — campo `meta_patrimonio` adicionado ao modelo Usuario; dashboard exibe meta dinâmica; perfil permite edição; API GET/PUT `/api/auth/me` funcionando
- **Database Investigation:** Plano completo de auditoria criado em `AUDITORIA_FUNCIONAL.md`; lições L-DB-001 a L-DB-006 documentadas
- **EXITUS-ATIVOS-002:** BUG-020 resolvido — classificador multi-camadas (DB → cache seed/manual → API externa → heurística → fallback `OUTRO`) com níveis de confiança e fonte; migration `ativo_classificacao_cache` aplicada com sucesso
- **EXITUS-ANALISES-001:** BUG-018 resolvido + BUG-003 falso positivo (import idempotente) — **0 telas 🔴 QUEBRADAS**
- **EXITUS-ATIVOS-001:** BUG-016 falso positivo; link "Eventos Corporativos" adicionado ao menu — tela funcionava sem link
- **EXITUS-OPERACOES-001:** BUG-002 resolvido — getters Alpine.js não sobrevivem a spread, substituídos por propriedades reativas em `operacoes_v2.html`
- **EXITUS-LOGIN-001:** Redesenho `login.html` (UX_DESIGN_SYSTEM) + remoção token mock de `auth.js` — BUG-001 resolvido
- **Auditoria Funcional:** 36 telas auditadas, 19 bugs documentados, 22 novas telas propostas (`AUDITORIA_FUNCIONAL.md`)

---

## 📊 Status Consolidado

| Componente | Progresso | Detalhe |
|------------|-----------|---------|
| **Backend** | ✅ 87% | 48/54 GAPs, 508/546 testes (93.0%), 156 endpoints |
| **Frontend V2.0** | � 36% | 13 OK, 23 PARCIAL, 0 QUEBRADO (36 telas auditadas) |
| **Frontend UX Evolution** | � 36% | 13 OK, 23 PARCIAL, 0 QUEBRADO (36 telas auditadas) |
| **Testes Backend** | ✅ 98.4% | 565/574 passando, 3 failed (dívida técnica: circuit_breaker ×2 + IR 2026+), 6 skipped |
| **Testes E2E** | 🟡 60% | v2: 127/127 ✅ Chromium (merged main 16/06) — v3 lógica negócio: 50 CTs planejados, specs criados (branch feature/testes-e2e-v3) |
| **Auditoria Funcional** | � 36% | 13 OK, 23 PARCIAL, 0 QUEBRADO (36 telas auditadas em 27/06/2026) |
| **Multi-tenancy** | ✅ 100% | MULTICLIENTE-001 concluído, 10 services + RLS (28 políticas) + isolamento via API |
| **Cenários de Teste** | ✅ 100% | test_full agora completo: 38 ativos (10 BR + 10 US + 10 BDRs + 8 RF), 56 transações, 42 proventos; dados realistas RV + RF |

---

## 🏗️ Módulos do Sistema (M0-M7)

| Módulo | Nome | Status | Endpoints |
|---|---|---|---|
| M0 | Infraestrutura | ✅ PROD | — |
| M1 | Database Schema | ✅ PROD | — |
| M2 | Backend API Core | ✅ PROD | 22 |
| M3 | Portfolio Analytics | ✅ PROD | 11 |
| M4 | Buy Signals & Fiscais | ✅ PROD | 12 |
| M5 | Frontend Base | ✅ PROD | 15 |
| M6 | Dashboards Frontend | ✅ PROD | 4 |
| M7.4 | Alertas | ✅ PROD | 4 |
| M7.5 | Cotações Live | ✅ PROD | 3 |
| M7.6 | Relatórios | ✅ PROD | 5 |
| M7.7 | Histórico de Preços | ✅ PROD | — |

**Total de Endpoints:** 156 rotas RESTful validadas.

---

## 🖥️ Backend — 87% Concluído

- **GAPs:** 48/54 implementados (Fases 1-6 ✅, MULTICLIENTE-001 ✅, HistoricoPatrimonio ✅)
- **Testes:** 105/105 passando nos módulos afetados por BUG-020 (`test_ativo_classifier.py`: 28, `test_import_b3_parsers.py`: 59, `test_import_b3_idempotencia.py`: 18)
- **Endpoints:** 156 funcionais (/api/portfolios/evolucao)
- **Multi-tenancy:** ✅ Concluído — 10 services + RLS (28 políticas PostgreSQL) + isolamento via API/JWT
- **Motor Fiscal:** IR completo, IOF, DARF, compensação
- **Importação:** B3 Excel/CSV, 56 ativos seed; BUG-020 corrigido (classificação multi-camadas de ativos)
- **APIs:** Cotações multi-provider, cache, circuit breaker
- **Exportação:** CSV, Excel, JSON, PDF
- **Próxima Fase:** 7 — Monitoramento, Rate Limiting, CI/CD

---

## ✅ Frontend API-Driven Integration — 100% Concluído

- **Sprints 1-8:** ✅ Todos concluídos (09/06/2026)
- **GAP Analysis Fase 3:** ✅ 4 telas novas (17/06/2026) — posicoes, movimentacoes, perfil, corretoras, historico, reconciliacao
- **GAP Analysis Fase 4:** ✅ 5 expansões (17/06/2026) — alertas CRUD, exportação multi-formato, buy signals top10, calendario proventos, rentabilidade benchmark
- **GAP Analysis Fase 5:** ✅ 4 melhorias (17/06/2026) — detalhe ativo fundamentalistas, DIRPF bens reais, eventos corporativos, planos compra/venda unificados
- **GAP Analysis Fase 6:** ✅ Unificação (17/06/2026) — 8 templates redundantes removidos, 15 telas migradas para base_interna.html + Alpine.js, 19 templates antigos deletados
- **GAP Analysis Fase 7:** ✅ Migração Final (18/06/2026) — operacoes.html + dashboard/index.html migrados; 100% dos templates em base_interna.html
- **Fix Visual Fase 7 (18/06/2026):** `operacoes_v2.html` + `dashboard/index_v2.html` reescritos para usar exclusivamente `exitus-components.css` — sem CSS custom, sem cores hardcoded; visual 100% consistente com todas as telas
- **APIs integradas:** 36+ endpoints (todos os 16 GAPs do GAP Analysis cobertos)
- **Tecnologia:** Alpine.js + Fetch API + API REST + base_interna.html
- **Status:** ✅ COMPLETO — Todas as fases (1-7) finalizadas

### Sprint 8 — Ferramentas (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/ferramentas/screener` — Screener: filtra ativos por DY, P/VP, P/L, tipo; coloração semântica
- ✅ `/ferramentas/comparador` — Compara até 3 ativos lado a lado (fundamentos + cotação real)
- ✅ `/ferramentas/calculadora-ir` — Simula ganho/perda e IR client-side com posições reais
- ✅ `/ferramentas/simulador` — Simulador de aportes: juros compostos, inflação, tabela de marcos
- ✅ Menu `/ferramentas/*` com 4 links reais (5 links mortos removidos)

### Sprint 7 — Relatórios e Exportação (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/relatorios/mensal` — Relatório mensal: transações + proventos + resumo IR
- ✅ `/relatorios/anual` — Histórico IR 12 meses + stats anuais
- ✅ `/relatorios/extrato` — Extrato completo com filtros (tipo, data_inicio, data_fim)
- ✅ `/relatorios/ir` — IR completo: apuração + histórico mensal + DIRPF bens e direitos
- ✅ `/relatorios/exportar/csv` — Export CSV client-side (Blob/JS) para transações, proventos, posições
- ✅ Menu `/relatórios/*` 7 links mortos substituídos por rotas reais

### Sprint 6 — Rentabilidade e Análises (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/analises/rentabilidade/periodo` — TWR 81.14%, MWR -65.4%, benchmark CDI, alpha
- ✅ `/analises/alocacao` — Alocação RF 61.6%/RV 38.4% com barras e tabela
- ✅ `/analises/evolucao` — Série histórica 2024–2026 (R$119k → R$795k)
- ✅ `/analises/performance` — Sharpe 1.45, Drawdown -8.3%, top ativos
- ✅ `/analises/buy-signals` — Buy Score por ticker + tabela de posições
- ✅ Menu Rentabilidade corrigido (rotas /rentabilidade/* fixadas para /analises/*)

### Sprint 5 — Imposto de Renda e DARF (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/imposto-renda/mensal` — Apuração por categoria (Day Trade, Swing, FII, Exterior, RF, Proventos)
- ✅ `/imposto-renda/darfs` — DARFs do mês com total de IR
- ✅ `/imposto-renda/historico` — Histórico anual 12 meses com totais
- ✅ `/imposto-renda/declaracao` — DIRPF completo: bens e direitos (R$ 642k real)
- ✅ Blueprint `fiscal.py` registrado, menu IR com ícones e 4 links funcionais

### Sprint 4 — Planos Disciplinados e Alertas (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/planos-compra/` — 12 planos reais com barras de progresso animadas
- ✅ `/planos-compra/<id>` — detalhe completo: progresso, meta, ativo, ações rápidas
- ✅ `/planos-venda/` — stub informativo (API backend 404)
- ✅ `/alertas/` — 15 alertas reais com tipo, condição, status, acionamentos
- ✅ Menu "Planos" adicionado + links Alertas funcionais

### Sprint 3 — Catálogo de Ativos (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/ativos/acoes` — Ações + stocks com fundamentos (P/L, ROE, DY)
- ✅ `/ativos/fiis` — FIIs + REITs com Cap Rate e FFO
- ✅ `/ativos/etfs` — ETFs nacionais e internacionais
- ✅ `/ativos/renda-fixa` — CDB, LCI/LCA, Tesouro, Debêntures
- ✅ `/ativos/cripto` — Criptoativos
- ✅ `/ativos/<ticker>` — Detalhe completo com ações rápidas
- ✅ Template genérico `lista.html` reutilizado por 5 categorias
- ✅ Links menu Ativos agora funcionais (eram 404)

### Sprint 2 — Proventos e Rendimentos (CONCLUÍDO ✅ — 09/06/2026)
- ✅ `/proventos/recebidos` — Proventos pagos com stats e gráfico de barras
- ✅ `/proventos/projetados` — Proventos previstos com gráfico de projeção
- ✅ `/proventos/calendario` — Visão mensal agrupada com totais por mês
- ✅ Blueprint `proventos.py` registrado em `__init__.py`
- ✅ Integração via `GET /api/proventos` com `get_api_headers()`
- ✅ Links Análises → Proventos no menu agora funcionais (eram 404)

### Sprint 1 — Operações Essenciais (CONCLUÍDO ✅)
- ✅ **Tela Operações:** Toggle Compra/Venda unificado (29/03/2026)
  - Autocomplete de ativos com API `/api/ativos?search=`
  - Binding reativo com Alpine.js
  - POST `/api/transacoes` via AJAX
  - Loading states e validações
  - **Novo:** Integração API cotações (`GET /api/cotacoes/<ticker>`)
  - **Novo:** Quantidade restrita a inteiros (`step=1`, `min=0`)
  - **Novo:** Corretoras dinâmicas via `GET /api/corretoras`
- ✅ **Sincronização Transações-Posições:** Bug crítico corrigido (02/04/2026)
  - Compras não atualizavam posições
  - Multi-tenancy bloqueava posições sem assessora_id
  - Modo VENDA não funcional
- ✅ **Renomeio Tela:** "compra" → "operacoes" (02/04/2026)
  - Nova rota `/operacoes/`
  - Rota legada `/compra` redireciona
  - Dashboard atualizado para "Nova Operação"
- ✅ **Tela Venda:** Integrada com toggle (30 posições visíveis)
- ✅ **Importação B3:** Upload drag & drop + API (05/04/2026)
  - Endpoint POST `/api/import/b3` com autenticação JWT
  - Detecção automática: transações vs proventos
  - Suporte CSV/Excel mistos (Compra/Venda + Dividendos)
  - Teste: 6 transações importadas com sucesso
- ⏳ **Histórico Transações:** Tabela paginada
- ⏳ **Painel de Planos:** Compra/Venda disciplinada

---

## 🎨 Frontend V2.0 — 100% Concluído

- **Telas:** 26/26 implementadas (todas as rotas mapeadas)
- **Framework:** Alpine.js + HTMX + Tailwind CSS
- **Features:** Multi-moeda nativo, mock data fallback, responsive 100%
- **Design:** Premium com gradientes, animações, micro-interações
- **UX:** Comparável a StatusInvest/Investidor10
- **Diferenciais:** Planos de Compra/Venda Disciplinada, Compensação Visual IR
- **Dashboard:** ✅ Novos cards implementados (Proventos 12M, Rentabilidade Total)
- **Auditoria Visual:** ✅ Concluída (P0 corrigido, P1/P2 OK)
- **Documentação:** ✅ Manual do Usuário completo (16 módulos, 800+ linhas)

---

## 🎨 Frontend — UX Evolution (100% Concluído) ✅

### ✅ Modernização Completa - 10 Páginas Ultra-Modernas

**Hero Sections Unificadas:**
- `bg-gradient-hero` com blur effects animados
- Elementos decorativos: blur circles translate
- Emojis 3xl com `animate-pulse-slow`
- Gradient text: `from-white to-white/80`
- Backdrop blur: `bg-white/20 backdrop-blur-sm`

**Páginas Modernizadas (10/10):**
1. **Dashboard** - 📊 Hero + Cards de mercado
2. **Carteiras** - 📁 Hero + Cards de resumo
3. **Ativos** - 🎯 Hero + Cards de estatísticas
4. **Performance** - 📈 Hero + Cards de métricas
5. **Movimentações** - 💳 Hero + Botão primário
6. **Alertas** - 🔔 Hero + Cards prioritários
7. **Relatórios** - 📄 Hero + Dropdown funcional
8. **Imposto de Renda** - 🧾 Hero + Cards DARF
9. **Educação** - 🎓 Hero + Conteúdo educativo
10. **Configurações** - ⚙️ Hero + Abas contextuais

**Design System Aplicado:**
- Botões: `btn-primario` e `btn-secundario`
- Cards: `card-moderno` com hover effects
- Interações: scale transitions, cursor pointers
- Animações: animate-scale-in com delays
- Consistência: 100% em todo o sistema

**Eficiência SWE-1.5:**
- Tempo: ~4 horas para 10 páginas
- Média: 24 minutos por página
- Commits: 11 atômicos
- Resultado: Transformação visual completa

> **Status:** ✅ **Week 1 Concluído** | **Início:** 20/03/2026 | **Modelo IA:** Sonnet  
> **Objetivo:** Modernizar interface tecnicista → design moderno para público geral  
> **Documentação:** [UX_ROADMAP.md](UX_ROADMAP.md) | [UX_IMPLEMENTACAO_WEEK1.md](UX_IMPLEMENTACAO_WEEK1.md)

### Progresso por Semana

| Semana | Status | Data | Deliverables |
|--------|--------|------|--------------|
| **Week 1** | ✅ Concluído | 20/03/2026 | Design System Moderno |
| **Week 2** | ✅ Concluído | - | Navegação Simplificada |
| **Week 3** | 📋 Planejado | - | Dashboard Moderno |
| **Week 4** | 📋 Planejado | - | Polimento e Testes |

### Week 2 Concluído - Navegação Simplificada

**✅ Entregas:**
- **Sidebar:** 22→8 itens com agrupamento lógico (Resumo, Operações, Análises, Config)
- **Busca Inteligente:** 6 atalhos contextuais (dash, cart, ati, comp, rel, conf)
- **Sub-Menus:** 12 sub-itens organizados (Comprar/Vender, Proventos, Planos, Análises)
- **Mobile-First:** Menu hambúrguer responsivo com overlay e slide-in
- **Testes:** Validação completa desktop/mobile com 3 screenshots
- **Animações:** Alpine.js reativo, chevron rotativo, transições suaves

**🎯 Resultados:**
- **Redução:** 64% menos itens (22→8 principais + 12 sub-itens)
- **Experiência:** Busca em tempo real, navegação por contexto
- **Mobile:** Layout responsivo touch-friendly com 85vw max-width
- **Performance:** Componentes otimizados com SWE-1.5 (economia)

### Week 1 Concluído - Design System Moderno

**✅ Entregas:**
- **CSS:** +454 linhas de design system moderno
- **Cores:** Roxo (#8b5cf6), Laranja (#f59e0b) inspiradas em apps populares
- **Componentes:** Cards modernos, botões interativos, animações suaves
- **Dashboard:** Hero section com gradiente, 4 cards de mercado
- **Testes:** Página `/dashboard/ux-test` com 8 seções de validação
- **Screenshots:** 2 capturas de tela (teste + dashboard)

**🎯 Resultados:**
- **Visual:** Transformado de corporativo → moderno e amigável
- **Interação:** Hover effects, animações, microinterações
- **Acessibilidade:** Contraste 4.5:1, tipografia +40% tamanho
- **Performance:** CSS otimizado, animações GPU-aceleradas

### Transformação Principal

- **Menu:** 22 itens → 8 itens intuitivos (Week 2)
- **Design:** Técnico → emocional (cores vivas, tipografia acessível)
- **Interface:** Tabelas densas → cards clicáveis
- **Navegação:** Hierárquica → por contexto

### Métricas Alvo

- **Tempo primeira ação:** < 30 segundos
- **Taxa conclusão:** > 85%
- **Satisfação (NPS):** > 70
- **Engajamento:** +40% tempo na plataforma

---

## 🧪 Testes — Status Detalhado

### Testes Backend (436/497 🟡 87.7%)

| Categoria | Status | Detalhes |
|-----------|--------|---------|
| **Testes passando** | 436 | 87.7% da suíte |
| **Testes falhando** | 61 | Principalmente IR e constraints |
| **Erros de setup** | 35 | Fixtures e importações |
| **Recuperação** | +5 | Após correção de fixtures multi-tenant |

**Principais arquivos de teste:**
- `test_ir_integration.py` — Motor fiscal completo
- `test_import_b3_parsers.py` — 59 testes de parsing
- `test_rentabilidade.py` — 21 testes de cálculo
- `test_darf_acumulado.py` — 8 testes DARF
- `test_import_b3_idempotencia.py` — 18 testes

### Testes E2E Frontend — v2 (16/06/2026)

| Métrica | Valor |
|---------|-------|
| **Testes passando** | 127/127 (100%) |
| **Specs criados** | 8 (por contexto: smoke, auth, operações, portfolio, fiscal, relatórios, ferramentas, regressão) |
| **Rotas cobertas** | 47 rotas reais |
| **Flaky tests** | 0 |
| **Browser** | Chromium ✅ — Firefox/Mobile Chrome 📋 pendente |
| **Framework** | Playwright |
| **Branch** | `feature/testes-e2e-v2` (merged main 16/06/2026) |

**Status v3 (em andamento — branch `feature/testes-e2e-v3`):**
- 73 CTs catalogados em `PLANO_TESTES_LOGICA.md`
- 13 specs criados (ops, fiscal, portfolio, ferramentas, relatórios, ativos, planos, alertas)
- Execução e validação dos 73 CTs: 📋 pendente

---

## 🎯 Dashboard Features (24/03/2026)

| Feature | Descrição | Status |
|---------|-----------|--------|
| **Loading Skeleton** | Animação shimmer durante carregamento | ✅ Implementado |
| **Cards de Ação Rápida** | Nova Compra, Vender, Depositar, Análises | ✅ Implementado |
| **Tooltips Educacionais** | Ícones ℹ️ com explicações contextuais | ✅ Implementado |
| **Meta de Patrimônio** | Barra de progresso visual (R$ 500k) | ✅ Implementado |
| **Benchmark vs CDI** | Comparativo: Carteira vs CDI vs Ibovespa | ✅ Implementado |
| **Próximos Proventos** | Dividendos esperados em 30 dias | ✅ Implementado |
| **API Calendário Dividendos** | Filtros `ticker`, `dias`, `limit` + persistência no `/gerar` | ✅ Implementado |

| **Calendário Econômico** | Próximos eventos (dividendos, vencimentos) | ✅ Implementado |
| **Cash Flow Mensal** | Entradas vs Saídas com saldo líquido | ✅ Implementado |
| **Diversificação Setores** | Distribuição por setor econômico | ✅ Implementado |
| **Resumo Fiscal** | DARF acumulado + IR a pagar | ✅ Implementado |
| **Recomendações** | Sugestões de compra/venda | ✅ Implementado |
---

## 📈 Métricas e KPIs

| Métrica | Atual | Meta | Status |
|---------|-------|------|--------|
| **GAPs Backend** | 47/54 (87%) | 54/54 | ✅ |
| **Testes Backend** | 436/497 (87.7%) | 500+ | 🟡 |
| **Endpoints** | 155 | 160 | ✅ |
| **Telas Frontend** | 17/17 (100%) | 17 | ✅ |
| **Testes E2E** | 108 (Fase 1) | 170+ | 🟡 |
| **Multi-tenancy** | ✅ 100% | 100% | ✅ |
| **Coverage** | 85%+ | 90% | 🟡 |
| **Performance** | <3s | <2s | 🟡 |

---

## 🔄 Dívidas Técnicas Identificadas

| Item | Descrição | Impacto | Prioridade | Sprint |
|------|-----------|---------|------------|--------|
| **HIST-001** | Job mensal para `historico_patrimonio` | Dashboard inconsistente | Média | 7 |

### HIST-001 — Processo Agendado: Histórico Patrimonial

**Problema:** Tabela `historico_patrimonio` não tem processo de atualização automática.
- Último snapshot: jun/2024 (R$ 58.050)
- Patrimônio atual: mar/2026 (R$ 249.907,10)
- Gap: 21 meses de dados ausentes

**Solução temporária:** Snapshot manual adicionado (23/03/2026).

**Implementação futura:**
- Job mensal para criar snapshots automáticos
- Scheduler (APScheduler ou cron) no dia 1 de cada mês
- Logging e monitoramento de falhas

**Detalhes técnicos:** Ver `docs/LESSONS_LEARNED.md` (L-FE-003)

---

## 🎯 Próximos Passos (por prioridade)

1. **Corrigir testes backend** — 61 falhas + 35 erros (IR, constraints)
2. **Executar testes E2E** — `cd tests/e2e && npm install && npm test`
3. **Fase 7 — Monitoramento** — MONITOR-001, RATELIMIT-001, CICD-001
4. **Testes Funcionais (Fase 2)** — CRUD, validações, integrações
4. **Backend Fase 7** — MONITOR-001, RATELIMIT-001, CICD-001
5. **Go-Live** — Validação final + deploy

**Timeline:** Ver [ROADMAP.md](ROADMAP.md)

---

## 🏆 Conquistas

- ✅ Backend com 436/497 testes (87.7%)
- ✅ Multi-tenancy completo (MULTICLIENTE-001)
- ✅ Motor fiscal completo (IR, IOF, DARF)
- ✅ Frontend V2.0 premium (26 telas mapeadas)
- ✅ Auditoria visual completa (P0 corrigido, sistema em excelente estado)
- ✅ Manual do Usuário completo (16 módulos, 800+ linhas)
- ✅ Importação B3 automatizada
- ✅ APIs robustas com cache
- ✅ Exportação multi-formato
- ✅ 47/54 GAPs implementados (87%)
- ✅ 0 console errors no frontend
- ✅ Arquitetura escalável (3 containers Podman)
- ✅ Documentação completa e consolidada (20 arquivos ativos)

---

## 🎯 Critérios de Go-Live

| Critério | Status |
|----------|--------|
| Backend 85%+ concluído | ✅ |
| Frontend 100% implementado | ✅ |
| 95%+ testes E2E passando | ⏳ |
| 0 bugs P0/P1 | ⏳ |
| Performance > 90 Lighthouse | ⏳ |
| Monitoramento ativo | 📋 |
| CI/CD configurado | � |

---

*Última atualização: 19/03/2026*  
*Próxima revisão: Após execução dos testes E2E*
