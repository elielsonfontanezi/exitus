# 🚀 Exitus — Roadmap Consolidado

> **Status atual:** Fases 1-6 ✅ Concluídas | **Próxima:** Fase 7 (Produção)  
> **Progresso Backend:** 48/54 GAPs (87%) + 1 débito técnico (HIST-001) + HIST-002 planejado | **Testes:** 567/574 passando (98.8%) 🟡 — 1 failed (feature 2026+), 6 skipped  
> **Frontend V2.0:** 13 OK, 23 PARCIAL, 0 QUEBRADO (64%) � | **UX Evolution:** 13 OK, 23 PARCIAL, 0 QUEBRADO (64%) � | **Frontend API-Driven:** ✅ 8/8 Sprints Concluídos (09/06/2026) | **UI Consistency:** ✅ Menu limpo (15/06/2026)  
> **Testes E2E v2:** ✅ 127/127 passando (Chromium) — branch `feature/testes-e2e-v2` | **Versão:** v0.9.28 | **Última atualização:** 27/06/2026

---

## 📊 Visão Geral

```
 Backend Fases 1-6: Concluídas ✅
 Backend Fase 7: Produção 🎯 (próxima)
 Backend Fase 8: Futuro 📋
 Frontend V2.0: 13 OK, 23 PARCIAL, 0 QUEBRADO (64%) �
 Frontend UX Evolution: 13 OK, 23 PARCIAL, 0 QUEBRADO (64%) �
 Frontend API-Driven: 8/8 Sprints ✅ (09/06/2026) — 33 telas, 27 APIs
 Testes E2E v2: 127/127 Chromium ✅ — Firefox/Mobile 🎯 (próximo)
 Backend Fase 7: MONITOR-001, RATELIMIT-001, CICD-001, HIST-002 📋
```

---

## ✅ Backend — Fases Concluídas (1-6)

| Fase | GAPs | Status | Data | Principais Entregas |
|------|------|--------|------|-------------------|
| **1** | Setup | ✅ | Fev/2026 | Infraestrutura base |
| **2** | 9 GAPs | ✅ | Fev/2026 | Scripts, CRUD, Importação |
| **3** | 13 GAPs | ✅ | Mar/2026 | Motor IR completo |
| **4** | 9 GAPs | ✅ | Mar/2026 | APIs, Multi-moeda, Planos de Venda |
| **5** | 6 GAPs | ✅ | 08/03/2026 | Rentabilidade, Qualidade |
| **6** | 9 GAPs | ✅ | 09/03/2026 | IOF, Auditoria, Scripts |

### O que está pronto

| Componente | Status | Detalhes |
|------------|--------|----------|
| **Backend** | ✅ | 156 endpoints REST, Flask + SQLAlchemy |
| **Banco** | ✅ | PostgreSQL, 23 tabelas, constraints robustas |
| **Autenticação** | ✅ | JWT, 3 roles (ADMIN/USER/READONLY) |
| **Motor Fiscal** | ✅ | IR completo, IOF, DARF, compensação |
| **Importação** | ✅ | B3 Excel/CSV, 56 ativos seed |
| **APIs** | ✅ | Cotações multi-provider, cache, circuit breaker |
| **Exportação** | ✅ | CSV, Excel, JSON, PDF |
| **Cenários de Teste** | ✅ | 4 cenários predefinidos (E2E, Full expandido, IR, Stress) + carga massiva (30 ativos, 48 transações, 32 proventos) |
| **Histórico Patrimonial** | ✅ | Snapshots mensais, endpoint /api/portfolios/evolucao |
| **Documentação** | ✅ | Swagger/OpenAPI auto-doc |
| **Testes** | 🟡 | 554/574 passando (96.4%) — 14 failed (constraints P6 + feature 2026+), 6 skipped |

---

## 🎯 Backend — Fase 7: Produção e Escala (Próxima)

| GAP ID | Funcionalidade | Prioridade | Status | Detalhe |
|--------|---------------|------------|--------|---------|
| **MULTICLIENTE-001** | Multi-tenancy para assessoras | 🔴 Alta | ✅ Concluído (03/04/2026) | 10 services + testes de isolamento. Ver [MULTICLIENTE.md](MULTICLIENTE.md) |
| **MONITOR-001** | Monitoramento e alertas | 🟡 Média | 📋 Planejado | Prometheus + Grafana vs DataDog |
| **RATELIMIT-001** | Rate limiting | 🟡 Média | 📋 Planejado | — |
| **CICD-001** | CI/CD + deploy | 🟡 Média | 📋 Planejado | GitHub Actions vs GitLab CI |
| **HIST-002** | Histórico de preços — fallback multi-provider | 🟡 Média | ✅ Implementado (28/06/2026) | `buscar_historico()` agora segue o padrão de cascata por mercado (Brapi/Twelve/Alpha/YF para BR; Alpha/Twelve/Finnhub/YF para US). Ver detalhe abaixo |

### MULTICLIENTE-001 — Concluído (03/04/2026)

- [x] Model Assessora (23 campos, 15 relacionamentos)
- [x] 20 models com `assessora_id` (100%)
- [x] Migrations aplicadas (2 migrations, 24 índices)
- [x] Dados migrados para assessora padrão (13 registros)
- [x] Helper de tenant (4 funções utilitárias)
- [x] JWT atualizado com `assessora_id`
- [x] 10 services com `filter_by_assessora()` (100%)
- [x] Banco de testes recriado com schema multi-tenant
- [x] Fixtures atualizados para testes multi-tenant
- [x] **Parte 4: Testes Multi-Tenancy (03/04/2026)**
  - [x] Plano de testes completo (38 casos planejados)
  - [x] Suite de testes de isolamento (5 testes, 100% passando)
  - [x] Validação de filtros automáticos
  - [x] Validação de JWT com assessora_id

**Pendências futuras (outros GAPs):**
- [ ] Implementar row-level security completa
- [ ] Dashboard admin por assessora
- [ ] Testes de isolamento ampliados (transações, posições, proventos)

### Timeline Fase 7 (Atualizado: Junho 2026)

| GAP | Status | Data |
|-----|--------|------|
| **MULTICLIENTE-001** | ✅ Concluído | 03/04/2026 |
| **MONITOR-001** | 🟡 Pendente | — |
| **RATELIMIT-001** | 🟡 Pendente | — |
| **CICD-001** | 🟡 Pendente | — |
| **Testes integrados multi-tenant** | 🟡 Pendente | — |

### HIST-002 — Histórico de preços: fallback multi-provider (✅ Validado no Frontend - 28/06/2026)

**Problema identificado (27/06/2026):**
- `CotacoesService.buscar_historico()` (`backend/app/services/cotacoes_service.py:314-380`) **só usava yfinance** — nenhum fallback
- yfinance falha dentro do container Podman: `Failed to get ticker 'ITUB4.SA' reason: Expecting value: line 1 column 1` (possível problema de rede/DNS ou delisting)
- `CotacoesService.obter_cotacao()` tem 8 providers com fallback (Brapi, HG, yfinance, Twelve Data, Finnhub, Alpha Vantage, Marketstack) — mas `buscar_historico()` não aproveita essa cascata
- **Consequência:** `historico_preco` vazia → `calcular_zscore()` falha → Buy Score artificial (50 para todos) → "Z-Score indisponível" na tela

**Providers disponíveis para histórico (APIs grátis, limitadas):**
- **Brapi.dev** — endpoint `/api/quote/{ticker}?interval=1d&range=1y` retorna histórico OHLCV (testado: funciona no container)
- **Alpha Vantage** — `TIME_SERIES_DAILY` (5 req/dia grátis)
- **Twelve Data** — `/time_series?symbol={ticker}&interval=1day&outputsize=252` (8 req/min grátis)
- **yfinance** — manter como último recurso (sem key, mas instável em container)

**Implementação (28/06/2026):**
1. `CotacoesService.buscar_historico()` refatorado para replicar o padrão de cascata por mercado (ver `CHANGELOG.md` → EXITUS-CIRCUITBREAKER-001, 08/03/2026)
2. `get_circuit_breaker()` reaproveitado em todos os providers de histórico; circuitos compartilham telemetria com `obter_cotacao()`
3. Ordem BR: Brapi → Twelve Data → Alpha Vantage → yfinance (.SA)
4. Ordem US: Alpha Vantage → Twelve Data → Finnhub → yfinance
5. Histórico convertido para o mesmo formato do banco (`Decimal`, `date`, campos opcionais) e filtrado pelo intervalo solicitado

**Validação Frontend (28/06/2026):**
- Login com `e2e_user`/`e2e_senha_123` ✅
- Tela Buy Signals carregada com watchlist Top 10 ✅
- ITUB4: Z-Score -2.97 exibido (valor real calculado de 168 dias de histórico) ✅
- ITUB4: Buy Score 100 (FORTE COMPRA) — valor dinâmico, não mais 50 fixo ✅
- ITUB4: Margem de Segurança 14.61% (🟢 COMPRA) ✅

**Correções de bugs encontrados durante validação:**
- `backend/app/services/buy_signals_service.py`: adicionado import de `logging` e `logger` (linha 96 usava logger sem import)
- `backend/app/blueprints/buy_signals_blueprint.py`: campo `z_score` → `zscore` para consistência com frontend (template espera `zscore`)
- `backend/app/services/buy_signals_service.py`: ajustado lógica `calcular_zscore()` para usar histórico existente se ≥30 dias (evita chamadas API desnecessárias quando já há dados suficientes no banco)

**Melhoria sugerida (após medir necessidade):** Caso os limites grátis continuem bloqueando ativos, avaliar provedores adicionais com OHLC diário estável — candidatos: Tiingo (planos acessíveis com dados ajustados), Polygon.io (intraday/stream, custo alto) e IEX Cloud (equities US). Requer business case e orçamento antes da assinatura.

**Atividade futura:** Depois que o fallback multi-provider estiver em produção, monitorar por ~30 dias quantos tickers ficam sem histórico suficiente (falls para último recurso) e registrar métricas em `PROJECT_STATUS.md`. Essa medição orientará se precisamos contratar provider premium ou apenas ajustar seeds/TTL.

**Nota:** APIs grátis têm limites de rate (Brapi: ~10 req/min, Alpha Vantage: 5 req/dia, Twelve Data: 8 req/min). Para produção, avaliar assinatura oficial no final do projeto.

**Dependência:** Nenhum GAP bloqueia, mas resolve indiretamente o "Z-Score indisponível" em Buy Signals.

---

## 🎨 Frontend — Integração API-Driven

**Status:** ✅ TODOS OS 8 SPRINTS CONCLUÍDOS | **Última atualização:** 09/06/2026  
**Referência completa:** `docs/FRONTEND_IMPLEMENTATION_PLAN.md`

### Roadmap de Sprints (Revisado 09/06/2026)

| Sprint | Foco | Telas | APIs | Status | Prazo Est. |
|--------|------|-------|------|--------|------------|
| **1** | Operações Essenciais | 2 | 5 | ✅ Concluído (05/04/2026) | — |
| **2** | Proventos e Rendimentos | 3 | 1 | ✅ Concluído (09/06/2026) | — |
| **3** | Catálogo de Ativos | 6 | 2 | ✅ Concluído (09/06/2026) | — |
| **4** | Planos + Alertas | 4 | 2 | ✅ Concluído (09/06/2026) | — |
| **5** | Imposto de Renda / DARF | 4 | 4 | ✅ Concluído (09/06/2026) | — |
| **6** | Rentabilidade e Análises | 5 | 5 | ✅ Concluído (09/06/2026) | — |
| **7** | Relatórios e Exportação | 5 | 6 | ✅ Concluído (09/06/2026) | — |
| **8** | Ferramentas | 4 | 3 | ✅ Concluído (09/06/2026) | — |

**Meta:** ~34 telas integradas com APIs reais | ~38 APIs integradas de 156

> **Sprint 7 concluído (09/06/2026):** `/relatorios/mensal`, `/anual`, `/extrato`, `/ir`, `/exportar/csv` — export CSV client-side (Blob/JS), 6 APIs integradas, menu `/relatórios/*` com 7 rotas reais.

### Objetivo
Implementar **todas as telas prometidas no menu horizontal**, consumindo as 156 APIs do backend.

### Estratégia
- **Uma tela por vez** — completo e testado antes de avançar
- **API-Driven Development:** cada tela consome APIs existentes
- **Reutilizar componentes** — `components/` já tem 44 arquivos prontos
- **Menu honesto** — link só vai ao menu quando a tela existir

### Documentação
- **FRONTEND_IMPLEMENTATION_PLAN.md** — Plano detalhado por sprint ⭐ NOVO
- **FRONTEND_INTEGRATION_PLAN.md** — Estratégia de integração API
- **API_REFERENCE.md** — Contratos das 156 APIs
- **UX_DESIGN_SYSTEM.md** — Componentes visuais

### Progresso Atual
- ✅ Sprint 1: 2 telas, 5 APIs integradas
- ✅ Sprint 2: 3 telas, 1 API integrada (100 proventos reais validados)
- ✅ Sprint 3: 6 telas, 1 API integrada (73 ativos, 5 categorias)
- ✅ Sprint 4: 4 telas, 2 APIs integradas (12 planos, 15 alertas)
- ✅ Sprint 5: 4 telas, 4 APIs integradas (IR real: apuração, DARF, histórico, DIRPF)
- ✅ Sprint 6: 5 telas, 5 APIs integradas (TWR/MWR, alocação, evolução, Sharpe, Buy Score)
- ✅ Sprint 7: 5 telas, 6 APIs integradas (mensal, anual, extrato, IR, CSV export)
- ✅ Sprint 8: 4 telas, 3 APIs integradas (screener, comparador, calculadora IR, simulador)
- **Total APIs:** 27/156 (17.3%)
- **Total Telas com rota real:** ~46 de ~50 prometidas no menu
- **Status Final:** Frontend API-Driven 8/8 Sprints ✅ (09/06/2026)

### 🎯 Próximos Passos Frontend (pós Sprint 8)

| Prioridade | Item | Detalhe |
|------------|------|---------|
| ✅ Concluído | **Testes E2E v2 — Chromium** | 127/127 passando, branch `feature/testes-e2e-v2` (16/06/2026) |
| ✅ Concluído | **Merge feature/frontend-api-integration → main** | Concluído antes de criar branch E2E v2 |
| ✅ Concluído | **Menu limpo (UI Consistency)** | 9 links 404 removidos, headers padronizados (15/06/2026) |
| 🔴 Alta | **E2E multi-browser** | Firefox + Mobile Chrome: `npx playwright test --project=firefox` |
| 🔴 Alta | **Merge feature/testes-e2e-v2 → main** | Após validação multi-browser |
| 🟡 Média | **Dados fundamentalistas nulos no Screener** | Muitos ativos têm `dividend_yield=null`, `p_vp=null` — verificar pipeline |
| 🟡 Média | **Calculadora IR: cotação automática** | Integrar `GET /api/cotacoes/<ticker>` para pré-preencher preço de venda sugerido |

---

## 🔮 Backend — Fase 8: Futuro

| GAP ID | Funcionalidade | Status |
|--------|---------------|--------|
| **VALUATION-001** | Adicionar EPS e FCF ao modelo Ativo | 🎯 PRÓXIMA AÇÃO |
| REBALANCE-001 | Rebalanceamento automático | 📋 Planejado |
| CONCENTRACAO-001 | Análise de concentração | 📋 Planejado |
| **PLANOVENDA-001** | Planos de Venda Disciplinada | ✅ Concluído (16/03/2026) |

### VALUATION-001 — Adicionar EPS e FCF ao modelo Ativo (🎯 PRÓXIMA AÇÃO)

**Problema identificado (28/06/2026):**
- `calculos_blueprint.py` usa valores hardcoded: `eps = 2.50` (linha 71), `fcf = 5.0` (linha 77)
- Graham e DCF calculam com números fictícios → `pt_medio` incorreto
- **Consequência:** Valuation não confiável (ex: ITUB4 → Valor Justo R$499,51 com preço atual R$42,24)

**Plano de implementação:**
1. Adicionar campos `eps` (Numeric 10, 4) e `fcf` (Numeric 15, 2) ao modelo `Ativo`
2. Criar migration Alembic: `alembic revision --autogenerate -m "add_eps_fcf_to_ativo"`
3. Corrigir hardcoded em `calculos_blueprint.py`: usar `ativo.eps` e `ativo.fcf` com fallback
4. (Opcional) Atualizar seed com valores realistas de EPS/FCF para ITUB4
5. Validar `/api/calculos/preco_teto/ITUB4` → Valor Justo deve ser razoável

**Arquivos a modificar:**
- `backend/app/models/ativo.py` — adicionar campos
- `backend/alembic/versions/[nova_migration].py` — migration
- `backend/app/blueprints/calculos_blueprint.py` — corrigir hardcoded
- `docs/CHANGELOG.md` — documentar
- `docs/PROJECT_STATUS.md` — atualizar status

**Modelo IA recomendado:** Claude Sonnet 4.6 Thinking ($$)

**Próximos passos (futuros):**
- Implementar busca de EPS/FCF via API externa (yfinance) para eliminar fallback
- Unificar Buy Score engine para usar `pt_medio` dinâmico em vez de `ativo.preco_teto`
| **DIVCALENDAR-001** | Calendário de dividendos | ✅ Concluído (10/03/2026) |
| **BLUEPRINT-CONSOLIDATION-001** | Consolidação de blueprints | ✅ Concluído (10/03/2026) |
| ORPHAN-001 | Limpeza de código órfão | ❌ Cancelado (arriscado) |

---

## ✅ Frontend V2.0 — Concluído (17/17 telas)

| Fase | Telas | Status | Entregas |
|------|-------|--------|---------|
| **1** | 4 | ✅ | Dashboard, Análise, Performance, Proventos |
| **2** | 4 | ✅ | Alocação, Fluxo Caixa, IR, Alertas |
| **3** | 5 | ✅ | Comparador, Planos Compra/Venda, Educação, Configurações |
| **4** | 4 | ✅ | Buy Signals, Portfolios, Transações, Relatórios |

**Diferenciais:** Multi-moeda nativo, mock data fallback, responsive 100%, design premium.

---

## 🧪 Testes E2E — Roadmap

### ✅ Fase 1: Setup + Testes de Fumaça (17/03/2026) — CONCLUÍDA

- [x] Configurar Playwright + dependências
- [x] 17 specs criados (1 por tela do Frontend V2.0)
- [x] 108 testes de fumaça implementados

**Resultado:** 104/108 passando (96% sucesso) — specs obsoletos (Frontend V2.0 mock data)

### ✅ v2: Replanejamento Completo por Contexto (16/06/2026) — CONCLUÍDA

- [x] 17 specs V2.0 obsoletos removidos (seletores incompatíveis com API-Driven)
- [x] 8 novos specs criados por contexto: smoke, auth, operacoes, portfolio, fiscal, relatorios, ferramentas, regressao
- [x] 127 testes cobrindo 47 rotas reais do frontend API-Driven
- [x] Credenciais corrigidas: `e2e_user`/`e2e_senha_123`
- [x] Seletores Alpine.js corrigidos (`x-model`, `x-show`, `.tipo-card`)
- [x] Race conditions resolvidas (`networkidle`, filtros `Failed to fetch`)
- [x] `playwright.config.js` atualizado — Chromium, Firefox, Mobile Chrome

**Resultado:** 127/127 passando, 0 flaky (Chromium) — branch `feature/testes-e2e-v2`

### ✅ Merge + Multi-browser (16/06/2026)

- [x] Merge `feature/testes-e2e-v2` → `main` ✅
- [ ] Firefox: `npx playwright test --project=firefox` — pendente
- [ ] Mobile Chrome: `npx playwright test --project="Mobile Chrome"` — pendente
- [ ] Performance audit (Lighthouse) — futuro
- [ ] Testes de acessibilidade (axe-core) — futuro

### 🟡 v3: Lógica de Negócio (em andamento — branch `feature/testes-e2e-v3`)

- [x] `PLANO_TESTES_LOGICA.md` — 73 CTs catalogados
- [x] 13 specs criados: ops (08-10), fiscal (11), portfolio (12), ferramentas (13-15), relatorios (16), regressao (17), ativos (18), planos (19), alertas (20)
- [x] Smoke: +3 rotas alertas (`/alertas/preco`, `/alertas/dividendos`, `/alertas/personalizados`)
- [ ] Execução e validação dos 73 CTs
- [ ] Merge `feature/testes-e2e-v3` → `main`

### ⏳ Fase 3: Validação Final e Go-Live (futuro)

- [ ] Múltiplos usuários simultâneos
- [ ] Grandes volumes de dados
- [ ] Condições de rede adversas
- [ ] Revisão de segurança
- [ ] Checklist de produção
- [ ] Go/No-Go decision

### Critérios de Go para Produção

- [ ] 95%+ testes passando
- [ ] 0 bugs P0/P1
- [ ] Performance Lighthouse > 90
- [ ] Acessibilidade WCAG 2.1 AA
- [ ] Security scan passed

---

## 🎨 Frontend — API-Driven Integration (8 Sprints)

> **Status:** ✅ 8/8 Sprints Concluídos (09/06/2026) | **36+ endpoints integrados** | **36+ templates** | **Telas: 2 OK, 34 PARCIAL, 0 QUEBRADO (94%)**

### Resumo dos Sprints

| Sprint | Título | Status | Endpoints |
|--------|--------|--------|-----------|
| Sprint 1 | Operações Essenciais | ✅ | 5 |
| Sprint 2 | Histórico Transações | ✅ | 6 |
| Sprint 3 | Planos & Alertas | ✅ | 8 |
| Sprint 4 | Análises & Dashboard | ✅ | 5 |
| Sprint 5 | Imposto de Renda | ✅ | 4 |
| Sprint 6 | Rentabilidade | ✅ | 5 |
| Sprint 7 | Relatórios & Exportação | ✅ | 6 |
| Sprint 8 | Ferramentas | ✅ | 4 |

**Total:** 36+ endpoints integrados, 36+ templates Jinja2, 11 blueprints frontend.

**Detalhes:** Ver `archive/FRONTEND_INTEGRATION_PLAN.md` para histórico completo.

---

## 🎨 Frontend — UX Evolution (4 Semanas)

> **Status:** ✅ **CONCLUÍDO COM SUCESSO** | **Início:** 20/03/2026 | **Modelo IA:** SWE-1.5  
> **Objetivo:** Modernizar interface tecnicista → design moderno para público geral  
> **Roadmap completo:** [UX_ROADMAP.md](UX_ROADMAP.md) | **Implementação:** [UX_IMPLEMENTACAO_WEEK1.md](UX_IMPLEMENTACAO_WEEK1.md)

### Fases de Implementação - 4 Semanas

| Semana | Fase | Status | Deliverables |
|--------|------|--------|--------------|
| **1** | Design System Moderno | ✅ Concluído (20/03/2026) | Cores emocionais, tipografia, componentes |
| **2** | Navegação Simplificada | ✅ Concluído (20/03/2026) | Menu 22→8 itens, abas contextuais |
| **3** | Dashboard Moderno | ✅ Concluído (20/03/2026) | Hero section, cards, ações rápidas |
| **4** | Modernização Completa | ✅ Concluído (20/03/2026) | 10 páginas ultra-modernas |

### Transformação Principal

**ANTES (Técnico):**
```
Dashboard | Buy Signals | Alertas | Carteiras | Ativos | 
Transações | Movimentações | Proventos | Relatórios | Análises |
[... 22 itens totais]
```

**DEPOIS (Intuitivo):**
```
📊 RESUMO: Visão Geral | Meus Investimentos
💰 OPERAÇÕES: Comprar | Vender | Depositar/Sacar  
📈 ANÁLISES: Desempenho | Oportunidades | Alertas
⚙️ CONFIG: Relatórios | Perfil
```

### Métricas de Sucesso UX

- **Tempo de primeira ação:** < 30 segundos
- **Taxa de conclusão:** > 85%
- **Satisfação (NPS):** > 70
- **Engajamento:** +40% tempo na plataforma

---

## 📈 Métricas e KPIs

| Métrica | Atual | Meta | Status |
|---------|-------|------|--------|
| **GAPs Backend** | 48/54 (87%) | 54/54 | 🟡 Em andamento |
| **Testes Backend** | 436/497 (87.7%) | 546 | 🟡 61 falhas (IR/constraints) + 35 erros setup |
| **Endpoints** | 156 | 160 | ✅ |
| **Telas Frontend API-Driven** | 33/~46 (87%) | 46 | 🟡 |
| **Testes E2E (Chromium)** | 127/127 (100%) | 127+ multi-browser | 🟡 Multi-browser pendente |
| **Cobertura** | 85%+ | 90% | 🟡 Medir |

---

## 🎯 Metas de Produção (Q2-2026)

- [x] Backend production-ready
- [x] Motor fiscal completo
- [x] APIs robustas
- [x] Frontend V2.0 completo
- [ ] Multi-tenancy real (85% → 100%)
- [ ] Monitoramento 24/7
- [ ] CI/CD automatizado
- [ ] 80%+ cobertura
- [ ] SLA 99.9%
- [ ] **HIST-001:** Job mensal para histórico patrimonial (débito técnico)

---

## 📚 Referências Arquivadas

Documentos históricos de roadmaps anteriores estão em `docs/archive/`:
- `ROADMAP_BACKEND.md` — Roadmap original do backend
- `ROADMAP_FRONTEND.md` — Roadmap frontend V1 (obsoleto)
- `ROADMAP_FRONTEND_V2.md` — Roadmap frontend V2 (concluído)
- `ROADMAP_TESTES_FRONTEND.md` — Plano detalhado de testes E2E
- `ROADMAP_FASE4.md` — Fase 4 performance (concluída)

---

## 🐛 Bugs e Pendências Abertas

| ID | Tela | Descrição | Prioridade | Status |
|----|------|-----------|------------|--------|
| **BUG-013** | `/carteira/movimentacoes` | Filtro de data pisca ao digitar ano | 🟡 Média | 📋 Aberto |
| **BUG-021** | `/carteira/movimentacoes` | Enum `TipoMovimentacao` inconsistente — API retornava erro `'resgate' is not among the defined enum values` | 🔴 Crítico | ✅ Resolvido (24/06/2026) |

### Pendências de Testes Backend

| Categoria | Quantidade | Causa | Próximo Passo |
|-----------|-----------|-------|---------------|
| **Falhas** | 61 | Motor IR + constraints | Investigar `test_ir_integration.py` |
| **Erros de setup** | 35 | Fixtures + importações | Revisar `conftest.py` e fixtures multi-tenant |

---

*Última atualização: 24/06/2026*  
*Próxima revisão: Após correção BUG-013 e falhas de testes backend*  
*Responsável: Elielson Fontanezi + Cascade AI*
