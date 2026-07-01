# 🚀 Exitus — Roadmap Consolidado

> **Status atual:** Fases 1-6 ✅ Concluídas | **Próxima:** Fase 7 (Produção)  
> **Progresso Backend:** 53/54 GAPs (98%) + CONCENTRACAO-001 ✅ | **Testes:** ver PROJECT_STATUS  
> **Frontend V2.0:** Lote 7 ✅ (FEAT-IR-COT, SEED-EVENTOS-001) — 43 OK, 0 PARCIAL | **Versão:** v0.9.52 | **Última atualização:** 01/07/2026

---

## 📊 Visão Geral

```
 Backend Fases 1-6: Concluídas ✅
 Backend Fase 7: Produção 🎯 (próxima)
 Backend Fase 8: Futuro 📋
 Frontend V2.0: 43 OK, 0 PARCIAL, 0 QUEBRADO (100%)
 Frontend UX Evolution: 43 OK, 0 PARCIAL, 0 QUEBRADO (100%)
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
| **OPS-GIT-HTTPS-001** | Autenticação Git para `git push` (HTTPS PAT ou SSH) no WSL | 🟡 Baixa | ✅ Resolvido (30/06/2026) | PAT GitHub configurado; Lote 3 + docs ops publicados |
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
- **archive/FRONTEND_INTEGRATION_PLAN.md** — Estratégia de integração API (histórico)
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
| 🟡 Média | **Calculadora IR: cotação automática** | ✅ Concluído (01/07/2026) — `GET /api/cotacoes/<ticker>` em `calculadora_ir_v2.html` |

---

## 🔮 Backend — Fase 8: Futuro

| GAP ID | Funcionalidade | Status |
|--------|---------------|--------|
| **VALUATION-001** | Adicionar EPS e FCF ao modelo Ativo | ✅ Concluído (28/06/2026) |
| **CLEANUP-MIGRATIONS-001** | Remover diretório alembic/ duplicado (dívida técnica) | ✅ Concluído (01/07/2026) |
| **CURSORRULES-001** | Reestruturar `.cursorrules` v3.0 + `docs/AI_OPERATIONS.md`; remover `.windsurfrules` | ✅ Concluído (29/06/2026) |
| **CURSORRULES-001.1** | Plano de controle: ROADMAP + AUDITORIA_FUNCIONAL + índice LESSONS | ✅ Concluído (29/06/2026) |
| **CURSORRULES-001.2** | REGRA #2 Plan/Agent; PERSONAS/INDEX; commit template; validação | ✅ Concluído (29/06/2026) |
| **CURSORRULES-001.3** | Fechamento migração: MODULES stub, links mortos, modelos Cursor, legacy | ✅ Concluído (29/06/2026) |
| **SEED-MACRO-001** | Popular tabela parametros_macro com valores reais BR/US | ✅ Concluído (29/06/2026) |
| **VALUATION-002** | Popular EPS/FCF reais no banco (yfinance ou seed) | ✅ Concluído (29/06/2026) |
| **BUG-VAL-001** | Corrigir fórmulas Bazin/Gordon/Graham (bugs estruturais) | ✅ Concluído (29/06/2026) |
| **BUG-VAL-002** | Valor Justo Médio: usar mediana (absorvido por BUG-VAL-005) | ♻️ Absorvido |
| **BUG-VAL-003** | Componente Margem do Score incoerente (resolvido por BUG-VAL-004) | ♻️ Absorvido |
| **BUG-VAL-004** | Unificar semântica: rename DDL preco_teto → preco_teto_usuario | ✅ Concluído (30/06/2026) |
| **BUG-VAL-005** | Metodologia de agregação: padrão de mercado (valuation_service.py) | ✅ Concluído (30/06/2026) |
| **BUG-VAL-006** | FII: fórmula cap_rate incorreta (1/cap_rate) | ✅ Concluído (30/06/2026) |
| **REBALANCE-001** | Rebalanceamento automático por classe | ✅ Concluído (30/06/2026) |
| CONCENTRACAO-001 | Análise de concentração | ✅ Concluído (01/07/2026) |
| **PLANOVENDA-001** | Planos de Venda Disciplinada | ✅ Concluído (16/03/2026) |

### VALUATION-001 — Adicionar EPS e FCF ao modelo Ativo (✅ Concluído 28/06/2026)

**Problema identificado (28/06/2026):**
- `calculos_blueprint.py` usava valores hardcoded: `eps = 2.50` (linha 71), `fcf = 5.0` (linha 77)
- Graham e DCF calculavam com números fictícios → `pt_medio` incorreto
- **Consequência:** Valuation não confiável (ex: ITUB4 → Valor Justo R$499,51 com preço atual R$42,24)

**Implementação concluída:**
1. ✅ Campos `eps` (Numeric 10,4) e `fcf` (Numeric 15,2) adicionados ao modelo `Ativo`
2. ✅ Migration Alembic `20260628_1800` criada em `migrations/versions/`
3. ✅ Hardcoded corrigido em `calculos_blueprint.py`: usa `ativo.eps` e `ativo.fcf` com fallback 2.50/5.0
4. ✅ Paridade de bancos aplicada (`exitusdb` + `exitusdb_test`)
5. ✅ Endpoint `/api/calculos/preco_teto/ITUB4` validado — Graham e DCF agora leem do banco

**Arquivos modificados:**
- `backend/app/models/ativo.py` — campos `eps`, `fcf` + `to_dict()`
- `backend/migrations/versions/20260628_1800_add_eps_fcf_to_ativo.py` — migration
- `backend/app/blueprints/calculos_blueprint.py` — fix hardcoded
- `docs/EXITUS_DB_STRUCTURE.txt` — schema atualizado

**Modelo IA utilizado:** Claude Sonnet 4.6 Thinking ($$)

**Próximos passos (futuros):**
- Implementar busca de EPS/FCF via API externa (yfinance) para eliminar fallback
- Unificar Buy Score engine para usar `pt_medio` dinâmico em vez de `ativo.preco_teto`

### CLEANUP-MIGRATIONS-001 — Diretório alembic/ arquivado (✅ Concluído 01/07/2026)

- `backend/alembic/` movido para `backend/archive/alembic_legacy/`
- Diretório ativo: **`backend/migrations/versions/`** (Flask-Migrate)
- Ver L-DB-015 em `LESSONS_LEARNED.md`

### VALUATION-002 — Popular EPS/FCF reais no banco (🔴 Alta)

**Problema identificado (28/06/2026):**
- Campos `eps` e `fcf` existem no modelo (VALUATION-001) mas estão NULL no banco
- Fallback (eps=2,50, fcf=5,0) ainda é usado → valuation incorreto
- ITUB4: LPA real ≈ R$ 4,17 (fonte: investidor10.com.br)

**Plano de implementação:**
1. Buscar EPS/FCF via yfinance para ativos BR e US
2. Atualizar seeds com valores realistas para ativos principais
3. Endpoint opcional: `/api/ativos/<ticker>/fundamentalistas` para atualizar manualmente

**Arquivos a modificar:**
- `backend/app/services/ativo_service.py` — buscar e popular EPS/FCF
- `backend/seed_data/ativos_br.json` — adicionar eps/fcf aos seeds
- `backend/seed_data/ativos_us.json` — adicionar eps/fcf aos seeds

**Prioridade:** Alta | **Risco:** Baixo

---

### BUG-VAL-001 — Corrigir fórmulas Bazin/Gordon/Graham (🔴 Alta)

**Problema identificado (28/06/2026 — validação Buy Signals ITUB4):**

**Bug 1 — Graham (linha 73):**
- Fórmula atual: `(eps * (8.5 + 2 * g * 100)) * 4.4 / k`
- `k` está em decimal (0,105) mas a fórmula de Graham espera yield em percentual (10,5)
- Resultado com eps=4,17: R$ 3.232 (absurdo)
- **Fix:** `(eps * (8.5 + 2 * g * 100)) * 4.4 / (k * 100)`
- Resultado corrigido: R$ 32,33 (razoável)

**Bug 2 — Bazin (linha 72):**
- Fórmula atual: `dy / (k - g)` onde `dy` é dividend_yield decimal (0,06)
- **Erro duplo:** usa yield decimal (não dividendo por ação) E usa `k-g` (Gordon) em vez do threshold fixo de Bazin (6%)
- Resultado atual: 0,06 / 0,055 = R$ 1,09 (errado)
- **Fix correto:** `(dy * preco_atual) / 0.06`
  - Décio Bazin: Preço Teto = Dividendo Anual por Ação / 6% (threshold fixo)
  - 6% é o rendimento mínimo exigido por Bazin — independe de k ou g
- Resultado corrigido (ITUB4): (0,06 × 42,24) / 0,06 = **R$ 42,24** (teto = preço quando DY exato 6%)
- **ATENÇÃO:** Não usar `(k - g)` — isso seria Gordon Growth Model, não Bazin. Os dois devem ser métodos distintos.

**Bug 3 — Gordon (linhas 74-75):**
- Fórmula atual: `d1 = dy * (1 + g)` onde `dy` é yield decimal
- Gordon deveria usar dividendo por ação: `d1 = (dy * preco_atual) * (1 + g)`
- Resultado atual: 0,063 / 0,055 = R$ 1,15 (errado)
- **Fix:** `d1 = (dy * preco_atual) * (1 + g); pt_gordon = d1 / (k - g)`
- Resultado corrigido: (0,06 × 42,24 × 1,05) / 0,055 = R$ 48,38 (razoável)

**Arquivo a modificar:**
- `backend/app/blueprints/calculos_blueprint.py:72-75`

**Prioridade:** Alta | **Risco:** Médio (muda resultados de valuation — validar com testes)

---

### BUG-VAL-002 — Valor Justo Médio: usar mediana (♻️ Absorvido por BUG-VAL-005)

**Problema identificado (28/06/2026):**
- Linha 90: `pt_medio = sum([v["pt"] for v in metodos.values()]) / 4`
- Média simples é distorcida por outliers (ex: Graham R$ 1.938 arrasta média para R$ 499)

**Status:** Absorvido por BUG-VAL-005 — `valuation_service.py` implementará mediana ponderada + remoção de outliers (IQR) de forma mais completa. Não implementar isoladamente em `calculos_blueprint.py`.

---

### BUG-VAL-003 — Componente Margem do Score incoerente (🟡 Média)

**Problema identificado (28/06/2026):**
- Tela mostra Margem 91,50% mas componente "Margem" do Score = 0/30 pts
- **Causa raiz confirmada:** componente usa `ativo.preco_teto` (estático, R$ 38,00) enquanto o card usa `pt_medio` (calculado, R$ 499,51)
- ITUB4: preco_atual=42,24, preco_teto=38,00 → margem = (38-42,24)/38 = **-11,2%** → negativa → 0 pts
- Card mostra +91,5% (vs pt_medio) — **contradição total**
- Ver BUG-VAL-004 para solução de unificação

**Arquivo a modificar:**
- `backend/app/services/buy_signals_service.py:14-30` — cálculo do componente Margem

**Prioridade:** Média | **Risco:** Baixo
**Dependências:** BUG-VAL-004 (unificar preco_teto vs pt_medio) resolve este bug também

---

### BUG-VAL-004 — Unificar preco_teto (estático) e pt_medio (calculado) (🔴 Alta)

**Problema identificado (28/06/2026 — investigação aprofundada):**

O sistema mantém **dois conceitos de "valor justo"** que não se comunicam:

**1. `ativo.preco_teto` (campo estático no banco):**
- Populado via seed (`ativos_fundamentalistas.json`) — valores subjetivos manuais
- Exemplos no banco: ITUB4=38,00, PETR4=45,00, VALE3=75,00, AAPL=195,00
- Usado por: `buy_signals_service.py:calcular_margem_seguranca()` → componente Margem do Buy Score
- **Problema:** Valor subjetivo sem metodologia clara — alguém decidiu "teto" sem fórmula

**2. `pt_medio` (calculado dinamicamente):**
- Calculado em `calculos_blueprint.py:90` — média de Bazin+Graham+Gordon+DCF
- Não é persistido no banco — calculado em tempo real
- Usado por: card "Valor Justo" na tela Buy Signals
- **Problema:** Tem bugs estruturais (BUG-VAL-001) mas é metodologicamente correto

**Divergência observada (ITUB4):**
- `preco_teto` (banco): R$ 38,00
- `pt_medio` (calculado): R$ 499,51 (13x diferente!)
- Margem 1 (vs pt_medio): 91,50% → 🟢 COMPRA
- Margem 2 (vs preco_teto): (38-42,24)/38 = -11,2% → deveria ser 🔴 VENDA
- **Contradição total na mesma tela**

**Solução adotada (Opção B):**

**1. Renomear `ativo.preco_teto` → `ativo.preco_teto_usuario`**
- O campo permanece no banco, mas com nome semântico claro: **teto definido manualmente pelo usuário**
- Não será mais usado como fonte de verdade para o Buy Score
- Visível na tela como referência opcional: "Teto definido pelo usuário"

**2. `pt_medio` será sempre calculado em tempo real**
- Não será persistido no banco de dados
- Fonte de verdade: `valuation_service.py` (BUG-VAL-005)
- Recalculado a cada consulta com preço atual, EPS, FCF e parâmetros macro atualizados
- Segue padrão de mercado: Investidor10, Status Invest, GuruFocus e Simply Wall St calculam valor justo sob demanda

**3. Buy Score usará apenas `pt_medio` (valor justo calculado)**
- `calcular_margem_seguranca()` passa a chamar `valuation_service.calcular_valor_justo(ativo)`
- Não há mais duas margens na tela — apenas uma, consistente

**4. Migration DDL obrigatória**
- Renomear coluna `preco_teto` para `preco_teto_usuario` em `ativo`
- Aplicar em `exitusdb` via Flask-Migrate e em `exitusdb_test` via ALTER TABLE (regra de paridade DDL)
- Atualizar modelos, seeds, schemas e documentação

**Arquivos a modificar:**
- `backend/app/models/ativo.py` — renomear coluna
- `backend/migrations/versions/` — migration DDL de rename
- `backend/app/seeds/seed_ativos_fundamentalistas.py` — ajustar campo
- `backend/app/seeds/data/ativos_fundamentalistas.json` — ajustar campo
- `backend/app/services/valuation_service.py` — **novo** serviço central
- `backend/app/services/buy_signals_service.py:14-30` — usar valuation_service
- `backend/app/blueprints/buy_signals_blueprint.py` — endpoint margem-seguranca
- `backend/app/blueprints/calculos_blueprint.py` — delegar para valuation_service
- `frontend/app/templates/analises/buy_signals_v2.html` — renomear labels e mostrar faixa
- `docs/EXITUS_DB_STRUCTURE.txt` — atualizar schema

**Prioridade:** Alta | **Risco:** Médio (muda Buy Score e schema — validar com testes)
**Dependências:** SEED-MACRO-001 + BUG-VAL-001 + VALUATION-002 + BUG-VAL-005 devem ser feitos primeiro
**Nota:** `pt_medio` nunca será coluna no banco. Se necessário histórico, criar tabela separada `historico_valuation` no futuro.

---

### BUG-VAL-005 — Metodologia de agregação: média simples → padrão de mercado (🔴 Alta)

**Problema identificado (28/06/2026):**
- Exitus usa **média aritmética simples** de 4 métodos (Bazin+Graham+Gordon+DCF) com pesos iguais (25% cada)
- Não é o padrão de mercado — sistemas de referência (Investidor10, Status Invest, GuruFocus, Simply Wall St) usam abordagem mais sofisticada
- **Problemas da abordagem atual:**
  1. Média simples é distorcida por outliers (Graham R$ 1.938 arrasta média para R$ 499)
  2. Todos os métodos aplicados a todos os ativos indiscriminadamente
  3. Número único dá falsa precisão — mercado mostra faixa
  4. Pesos iguais ignoram perfil do ativo (dividendos vs crescimento vs value)

**Padrão de mercado (referências: Investidor10, Status Invest, GuruFocus, Simply Wall St):**

**1. Seleção de métodos por perfil do ativo:**
- Nem todo método se aplica a todo ativo
- **Ações de dividendos** (BR comum): Bazin, Gordon, Graham, DCF
- **Ações de crescimento** (US tech): DCF, Graham (com g ajustado)
- **Value stocks**: Graham, DCF
- **FIIs/REITs**: Cap Rate, FFO/AFFO múltiplos
- **Renda Fixa**: Yield to Maturity

**2. Remoção de outliers (método IQR — Interquartile Range):**
- Calcular Q1, Q3 e IQR = Q3 - Q1
- Remover valores fora de [Q1 - 1.5×IQR, Q3 + 1.5×IQR]
- Só então calcular agregação

**3. Mediana ou média ponderada (não média simples):**
- **Mediana** — mais robusta, imune a outliers residuais
- **Média ponderada** — pesos variam por perfil do ativo:

| Perfil | Bazin | Gordon | Graham | DCF |
|--------|-------|--------|--------|-----|
| Dividendos (BR) | 35% | 25% | 20% | 20% |
| Crescimento (US tech) | 10% | 10% | 30% | 50% |
| Value | 10% | 15% | 40% | 35% |
| Bancos (BR) | 35% | 25% | 20% | 20% |

**4. Faixa de valor justo (não número único):**
- Mostrar min, max e tendência central (mediana ou ponderada)
- Usuário vê intervalo: "Valor Justo: R$ 35 – R$ 50 (mediana: R$ 46)"
- Margem de segurança calculada contra a mediana

**5. Margem de segurança conservadora:**
- Usar o **limite inferior** da faixa (cuidado) ou mediana (neutro)
- Sinal: COMPRA se preço < mediana × 0,80 (20% margem), NEUTRO se entre 0,80-1,00, VENDA se > 1,00

**Arquitetura proposta:**

```python
# novo arquivo: backend/app/services/valuation_service.py

def calcular_valor_justo(ativo, params):
    # 1. Classificar perfil do ativo
    perfil = classificar_perfil(ativo)  # dividend, growth, value, fii, bond

    # 2. Selecionar métodos aplicáveis ao perfil
    metodos_aplicaveis = METODOS_POR_PERFIL[perfil]

    # 3. Calcular cada método
    valores = {}
    for metodo in metodos_aplicaveis:
        valores[metodo] = calcular_metodo(metodo, ativo, params)

    # 4. Remover outliers (IQR)
    valores_filtrados = remover_outliers_iqr(valores)

    # 5. Calcular faixa e tendência central
    faixa = (min(valores_filtrados.values()), max(valores_filtrados.values()))
    valor_justo = mediana(valores_filtrados)  # ou ponderada

    # 6. Margem de segurança
    margem = (valor_justo - preco_atual) / valor_justo * 100

    return {
        'valor_justo': valor_justo,
        'faixa_min': faixa[0],
        'faixa_max': faixa[1],
        'margem_seguranca': margem,
        'metodos': valores,
        'perfil': perfil,
        'pesos': PESOS_POR_PERFIL.get(perfil, {}),
        'outliers_removidos': set(valores) - set(valores_filtrados)
    }
```

**Comparação de resultados (ITUB4 com EPS=4,17, após fixes BUG-VAL-001):**

| Método | Valor |
|--------|-------|
| Bazin | R$ 46,08 |
| Graham | R$ 32,33 |
| Gordon | R$ 48,38 |
| DCF | R$ 57,69 |

| Abordagem | Cálculo | Resultado |
|-----------|---------|-----------|
| Exitus atual (média simples) | (46+32+48+58)/4 | R$ 46,00 |
| **Mediana** | meio(32,46,48,58) | **R$ 47,00** |
| **Ponderada (dividendos)** | 46×35%+48×25%+32×20%+58×20% | **R$ 46,80** |
| **Faixa** | min–max | **R$ 32 – R$ 58** |

Todas as abordagens de mercado chegam a **R$ 46-47** — valor razoável para ITUB4 (preço atual R$ 42,24 → margem ~10%).

**Arquivos a criar/modificar:**
- `backend/app/services/valuation_service.py` — **novo** serviço central de valuation
- `backend/app/blueprints/calculos_blueprint.py` — usar valuation_service
- `backend/app/services/buy_signals_service.py` — usar valuation_service para margem
- `frontend/app/templates/analises/buy_signals_v2.html` — mostrar faixa em vez de número único
- `backend/tests/test_valuation_service.py` — **novo** testes unitários

**Prioridade:** Alta | **Risco:** Médio
**Dependências:** SEED-MACRO-001 + BUG-VAL-001 + VALUATION-002 devem ser feitos primeiro

---

### SEED-MACRO-001 — Popular tabela parametros_macro com valores reais BR/US (🔴 Pré-requisito)

**Problema identificado (28/06/2026 — análise crítica do plano de valuation):**
- Tabela `parametros_macro` está **completamente vazia** no banco (0 rows)
- Todo o sistema de valuation usa defaults hardcoded em `parametros_macro_service.py:141-148`:
  - `taxa_livre_risco = 0.105` (10,5%)
  - `crescimento_medio = 0.05` (5%)
  - `custo_capital = 0.12` (12%)
- Os "parâmetros regionais dinâmicos" mencionados no código são uma **ilusão** — BR e US usam os mesmos valores fixos
- BUG-VAL-005 (pesos por perfil) depende de parâmetros reais por mercado para funcionar corretamente

**Plano de implementação:**
1. Seed via `flask shell` ou script: inserir parâmetros para BR/B3 e US/NYSE
2. Valores iniciais sugeridos:

| pais | mercado | taxa_livre_risco | crescimento_medio | custo_capital | cap_rate_fii |
|------|---------|-----------------|-------------------|---------------|-------------|
| BR | B3 | 0.105 (Selic) | 0.050 | 0.120 | 0.080 |
| US | NYSE | 0.043 (T-Bill) | 0.070 | 0.090 | 0.055 |
| US | NASDAQ | 0.043 (T-Bill) | 0.100 | 0.100 | 0.050 |

3. Verificar: `SELECT * FROM parametros_macro;` deve retornar ≥ 2 rows

**Arquivos a modificar:**
- Script de seed ou `backend/app/seeds/seed_parametros_macro.py` — **novo**

**Prioridade:** Pré-requisito para BUG-VAL-001 (regional) e BUG-VAL-005 (pesos por perfil) | **Risco:** Baixo

---

### BUG-VAL-006 — FII: fórmula cap_rate corrigida (✅ Concluído 30/06/2026)

**Problema (identificado 28/06/2026):**
- `calculos_blueprint.py`: `pt_cap_rate = 1 / cap_rate` → para cap=0.089 gerava R$ 11,24 (sem dimensão)

**Solução aplicada (30/06/2026):**
```python
dy_anual = dy * preco_atual          # dividendo anual por cota (R$)
pt_cap_rate = dy_anual / cap_rate    # preço teto implícito
# HGLG11: dy=8,2%, preco=152,30, cap=8,9% → pt=R$ 140,22 ✅
```
- Guard adicionado: `if cap_rate > 0 and dy > 0` (pt=0 se dados ausentes)
- 2 novos testes em `tests/test_calculos.py` (regressão FII + edge-case dy=None)
- Suíte completa: **567 passed, 3 failed (pré-existentes), 6 skipped** — sem regressão

**BUG-VAL-004 concluído (30/06/2026):** rename DDL `preco_teto → preco_teto_usuario` + paridade DBs + labels frontend + aliases removidos

**REBALANCE-001 concluído (30/06/2026):** tabela `meta_alocacao` + `rebalance_service.py` + 3 endpoints + tela `alocacao_v2.html` com editor de metas, barras de desvio e painel de sugestões comprar/vender

**Próximo:** CONCENTRACAO-001 ou GAP de Fase 7 (ver tabela acima)

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

**Pré-requisito:** `SEED-MENU-001` + OK manual do usuário (menu 100%) — ver [`PLANO_MASSA_TESTES_MENU.md`](PLANO_MASSA_TESTES_MENU.md) e [`AUDITORIA_FUNCIONAL.md`](AUDITORIA_FUNCIONAL.md) § Go-Live.

| GAP ID | Funcionalidade | Prioridade | Status |
|--------|---------------|------------|--------|
| **SEED-MENU-001** | Cenário `test_menu_full` — massa para 43 telas do menu | 🔴 Alta | 📋 Planejado (doc 01/07/2026) |

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

*Última atualização: 30/06/2026*  
*Próxima revisão: Início da próxima sessão*  
*Responsável: Elielson Fontanezi + Cursor Agent*
