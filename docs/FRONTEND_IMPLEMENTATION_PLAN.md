# 🖥️ Plano de Implementação Frontend — Exitus

**Data:** 09/06/2026 | **Versão:** v1.0 | **Status:** 📋 Planejado  
**Objetivo:** Implementar todas as telas prometidas no menu horizontal, integrando as 156 APIs do backend.

---

## 📊 Estado Atual (Diagnóstico)

### O que existe hoje
| Camada | Arquivo | Rotas | Status |
|--------|---------|-------|--------|
| **Operações** | `operacoes.py` | `/operacoes/`, `/compra`, `/venda`, `/deposito` | ✅ Implementado |
| **Dashboard** | `dashboard.py` | `/dashboard/`, `/transactions`, `/dividends`, `/reports`, `/alerts`, `/buy-signals`, `/portfolios`, `/assets`, `/analytics` | ✅ Rotas criadas |
| **Auth** | `auth.py` | `/login`, `/logout`, `/register`, `/profile` | ✅ Implementado |
| **Admin** | `admin.py` | `/admin/assessoras` | ✅ Implementado |
| **Análises** | `analises.py` | `/analises/` | ⚠️ Stub (sem conteúdo) |

### O que o menu promete (não implementado)
O `menu_horizontal.html` possui ~50 links, dos quais apenas ~15 têm rota real.  
A maioria retorna 404.

---

## 🎯 Estratégia Geral

- **Uma tela por vez** — implementar completo antes de avançar
- **API-first** — mapear endpoints antes de criar template
- **Reutilizar componentes** — `components/` já possui 44 arquivos reutilizáveis
- **Padrão único** — `get_api_headers()` + Alpine.js + Fetch API
- **Documentar junto** — CHANGELOG + PROJECT_STATUS no mesmo commit
- **Modelo IA recomendado:** GPT 5.1 Codex Medium ($) para CRUD simples, Claude Sonnet 4.6 ($$$/$$) para lógica complexa (IR, Planos)

---

## 📋 Sprints de Implementação

### ✅ Sprint 1 — Operações Essenciais (CONCLUÍDO — 05/04/2026)
**Valor:** Alto | **Esforço:** 5 dias

| Tela | Rota | APIs Backend | Status |
|------|------|-------------|--------|
| Compra/Venda Unificado | `/operacoes/` | POST /api/transacoes, GET /api/ativos, GET /api/cotacoes, GET /api/posicoes | ✅ |
| Importação B3 | `/operacoes/` (drag & drop) | POST /api/import/b3 | ✅ |

**APIs integradas:** 5/156

---

### ✅ Sprint 2 — Proventos e Rendimentos (CONCLUÍDO — 09/06/2026)
**Valor:** Alto | **Esforço real:** 1 sessão

| Tela | Rota Frontend | APIs Backend | Status |
|------|--------------|-------------|--------|
| Proventos Recebidos | `/proventos/recebidos` | GET /api/proventos | ✅ |
| Proventos Projetados | `/proventos/projetados` | GET /api/proventos | ✅ |
| Calendário de Dividendos | `/proventos/calendario` | GET /api/proventos | ✅ |

**Artefatos criados:**
- `frontend/app/routes/proventos.py` — 3 rotas
- `frontend/app/templates/proventos/recebidos.html`
- `frontend/app/templates/proventos/projetados.html`
- `frontend/app/templates/proventos/calendario.html`
- `frontend/app/__init__.py` — blueprint registrado
- Fix: `quantidade_ativos` (campo real da API) + `ativo.ticker` mapeado
- Testado com `e2e_user`: 100 proventos reais, 0 erros de console

**APIs integradas:** 1 endpoint (`GET /api/proventos`)

---

### ✅ Sprint 3 — Catálogo de Ativos (CONCLUÍDO — 09/06/2026)
**Valor:** Médio-Alto | **Esforço real:** 1 sessão

| Tela | Rota Frontend | APIs Backend | Status |
|------|--------------|-------------|--------|
| Minhas Ações | `/ativos/acoes` | GET /api/ativos?tipo=acao,stock | ✅ |
| Meus FIIs | `/ativos/fiis` | GET /api/ativos?tipo=fii,reit | ✅ |
| ETFs | `/ativos/etfs` | GET /api/ativos?tipo=etf,etf_intl | ✅ |
| Renda Fixa | `/ativos/renda-fixa` | GET /api/ativos (multi-tipo) | ✅ |
| Criptoativos | `/ativos/cripto` | GET /api/ativos?tipo=cripto | ✅ |
| Detalhe do Ativo | `/ativos/<ticker>` | GET /api/ativos?ticker=X | ✅ |

**Artefatos criados:**
- `frontend/app/routes/ativos_catalogo.py` — 6 rotas
- `frontend/app/templates/ativos/lista.html` — template genérico (1 arquivo para 5 categorias)
- `frontend/app/templates/ativos/detalhe.html` — fundamentos + ações rápidas
- `frontend/app/__init__.py` — blueprint registrado

**Lição registrada:** L-FE-005 — validar campos reais da API antes de mapear (`quantidade_ativos`, `ativo.ticker`)
Testado: 73 ativos reais, 0 erros de console, menu Ativos 404 → funcionais

**APIs integradas:** 1 endpoint (`GET /api/ativos`)

---

### ✅ Sprint 4 — Planos Disciplinados e Alertas (CONCLUÍDO — 09/06/2026)
**Valor:** Alto | **Esforço real:** 1 sessão

| Tela | Rota Frontend | APIs Backend | Status |
|------|--------------|-------------|--------|
| Dashboard Planos Compra | `/planos-compra/` | GET /api/plano-compra/ | ✅ |
| Detalhe Plano Compra | `/planos-compra/<id>` | GET /api/plano-compra/<id> | ✅ |
| Planos de Venda | `/planos-venda/` | API 404 (backend pendente) | ⚠️ stub |
| Alertas | `/alertas/` | GET /api/alertas/ | ✅ |

**Artefatos criados:**
- `frontend/app/routes/planos.py` — blueprints `planos` + `planos_venda`
- `frontend/app/routes/alertas.py` — blueprint `alertas`
- `frontend/app/templates/planos/compra_lista.html` — barras de progresso, stats
- `frontend/app/templates/planos/compra_detalhe.html` — detalhe completo
- `frontend/app/templates/planos/venda_lista.html` — stub com aviso de API pendente
- `frontend/app/templates/alertas/lista.html` — 15 alertas reais
- `menu_horizontal.html` — dropdown "Planos" + links Alertas funcionais

**Nota:** `GET /api/plano-venda` retorna 404. Tela de venda ficou como stub até o backend implementar o endpoint.
Testado: 12 planos reais, 15 alertas reais, 0 erros de console

**APIs integradas:** 2 endpoints (`GET /api/plano-compra/`, `GET /api/alertas/`)

---

### ✅ Sprint 5 — Imposto de Renda e DARF (CONCLUÍDO — 09/06/2026)
**Valor:** Crítico (obrigação fiscal) | **Esforço real:** 1 sessão

| Tela | Rota Frontend | APIs Backend | Status |
|------|--------------|-------------|--------|
| Apuração Mensal IR | `/imposto-renda/mensal` | GET /api/ir/apuracao | ✅ |
| DARFs do Mês | `/imposto-renda/darfs` | GET /api/ir/darf | ✅ |
| Histórico Anual | `/imposto-renda/historico` | GET /api/ir/historico | ✅ (extra) |
| Declaração DIRPF | `/imposto-renda/declaracao` | GET /api/ir/dirpf | ✅ |

**Artefatos criados:**
- `frontend/app/routes/fiscal.py` — 4 rotas
- `frontend/app/templates/fiscal/ir_mensal.html` — categorias + proventos + alertas
- `frontend/app/templates/fiscal/darfs.html` — DARFs geradas + total IR
- `frontend/app/templates/fiscal/historico.html` — 12 meses anuais (extra)
- `frontend/app/templates/fiscal/declaracao.html` — bens e direitos DIRPF

**Nota:** APIs reais no backend: `/api/ir/apuracao`, `/api/ir/darf`, `/api/ir/historico`, `/api/ir/dirpf`.
As rotas planejadas (`/ir/calculo-mensal`, `/ir/darfs-pendentes`) retornavam 404; usados os endpoints reais.
Testado: Custo total carteira R$ 642.084,51 real, apuração com 4 categorias + proventos, 0 erros console.

**APIs integradas:** 4 endpoints (`GET /api/ir/apuracao`, `/api/ir/darf`, `/api/ir/historico`, `/api/ir/dirpf`)

---

### ✅ Sprint 6 — Rentabilidade e Análises (CONCLUÍDO — 09/06/2026)
**Valor:** Alto (tomada de decisão) | **Esforço real:** 1 sessão

| Tela | Rota Frontend | APIs Backend | Status |
|------|--------------|-------------|--------|
| Rentabilidade por Período | `/analises/rentabilidade/periodo` | GET /api/portfolios/rentabilidade | ✅ |
| Alocação de Ativos | `/analises/alocacao` | GET /api/portfolios/alocacao + /performance/desvio-alocacao | ✅ |
| Evolução Patrimonial | `/analises/evolucao` | GET /api/portfolios/evolucao | ✅ (extra) |
| Performance (Sharpe) | `/analises/performance` | GET /api/performance/performance | ✅ |
| Buy Signals | `/analises/buy-signals` | GET /api/buy-signals/buy-score/<ticker> | ✅ |

**Artefatos criados:**
- `frontend/app/templates/analises/rentabilidade_periodo.html` — TWR, MWR, benchmark, alpha
- `frontend/app/templates/analises/alocacao.html` — RF/RV/Cripto com barras + tabela
- `frontend/app/templates/analises/evolucao.html` — série 2024-2026 + gráfico (extra)
- `frontend/app/templates/analises/performance.html` — Sharpe, drawdown, top ativos
- `frontend/app/templates/analises/buy_signals.html` — score gauge + posições

**Artefatos modificados:**
- `frontend/app/routes/analises.py` — 5 novas rotas adicionadas ao stub existente
- `menu_horizontal.html` — prefixos /rentabilidade/* corrigidos para /analises/*

**Nota:** `/api/portfolio/performance` (404), `/api/buy-signals/watchlist-top` (200 mas corpo vazio — backend sem dados).
Usados `/api/portfolios/rentabilidade`, `/api/performance/performance`, `/api/buy-signals/buy-score/<ticker>`.
Testado: TWR 81.14%, R$795k patrimônio, evolução 30 meses, 0 erros console.

**APIs integradas:** 5 endpoints (rentabilidade, alocacao, evolucao, performance, buy-score)

---

### ✅ Sprint 7 — Relatórios e Exportação (CONCLUÍDO 09/06/2026)
**Valor:** Médio | **APIs reais verificadas antes da implementação**

| Tela | Rota Frontend | APIs Usadas | Status |
|------|--------------|-------------|--------|
| Relatório Mensal | `/relatorios/mensal` | GET /api/transacoes + /api/proventos + /api/ir/apuracao | ✅ 200 OK |
| Relatório Anual | `/relatorios/anual` | GET /api/ir/historico + /api/transacoes + /api/proventos | ✅ 200 OK |
| Extrato Completo | `/relatorios/extrato` | GET /api/transacoes (paginado, filtros tipo/data) | ✅ 200 OK |
| IR Completo | `/relatorios/ir` | GET /api/ir/historico + /api/ir/dirpf + /api/ir/apuracao | ✅ 200 OK |
| Exportar CSV | `/relatorios/exportar/csv` | GET /api/transacoes | /api/proventos | /api/posicoes | ✅ 200 OK |

**Artefatos criados:**
- `frontend/app/routes/relatorios.py` — Blueprint com 5 rotas
- `frontend/app/templates/relatorios/mensal.html`
- `frontend/app/templates/relatorios/anual.html`
- `frontend/app/templates/relatorios/extrato.html`
- `frontend/app/templates/relatorios/ir_completo.html`
- `frontend/app/templates/relatorios/exportar_csv.html`

**Artefatos modificados:**
- `frontend/app/__init__.py` — Blueprint registrado
- `menu_horizontal.html` — 7 links mortos substituídos

**Nota:** `/api/relatorios/gerar` (404) e `/api/transacoes/export` (retorna null) não usados.
Export CSV é gerado 100% client-side via JavaScript `Blob` + `URL.createObjectURL`.

**APIs integradas:** 6 endpoints (transacoes, proventos, ir/apuracao, ir/historico, ir/dirpf, posicoes)

---

### 📋 Sprint 8 — Ferramentas (Opcional/Futuro)
**Valor:** Médio-Baixo | **Esforço estimado:** 5–6 dias

| Tela | Rota Frontend | APIs Backend | Observação |
|------|--------------|-------------|-----------|
| Comparador de Ativos | `/comparador` | GET /api/ativos (múltiplos) | Lógica frontend-heavy |
| Calculadora IR | `/calculadora-ir` | GET /api/ir/* | Simulação local |
| Simulador de Investimentos | `/simulador` | GET /api/projecoes/* | Pode ser sem API |
| Screeners | `/screeners` | GET /api/ativos + filtros avançados | |

---

## 📅 Timeline Estimada

```
Junho 2026:
├── Sprint 2: Proventos e Rendimentos (3–4 dias)
│
Julho 2026:
├── Sprint 3: Catálogo de Ativos (2–3 dias)
├── Sprint 4: Planos Disciplinados (4–5 dias)
│
Agosto 2026:
├── Sprint 5: Imposto de Renda (3–4 dias)
├── Sprint 6: Rentabilidade e Análises (3–4 dias)
│
Setembro 2026:
├── Sprint 7: Relatórios e Exportação (2–3 dias)
└── Sprint 8: Ferramentas (5–6 dias) — opcional
```

**Total estimado:** 22–30 dias para ~35 telas novas

---

## 🔧 Metodologia por Tela (Padrão)

1. **Mapear APIs** — verificar contratos em `docs/API_REFERENCE.md`
2. **Criar rota** no blueprint correspondente usando `get_api_headers()`
3. **Criar template** seguindo `docs/UX_DESIGN_SYSTEM.md` (Nunito, #A38C65)
4. **Integrar Alpine.js** para interatividade e Fetch API para dados
5. **Testar** em `localhost:8080` com usuário `admin/senha123`
6. **Atualizar menu** — substituir link morto pela rota real
7. **Documentar** — CHANGELOG.md + PROJECT_STATUS.md no mesmo commit

---

## 📐 Estrutura de Blueprints a Criar

```
frontend/app/routes/
├── operacoes.py   ✅ (existente)
├── dashboard.py   ✅ (existente)
├── auth.py        ✅ (existente)
├── admin.py       ✅ (existente)
├── analises.py    ⚠️ (stub — refatorar)
├── proventos.py   📋 Sprint 2 (novo)
├── ativos.py      📋 Sprint 3 (novo)
├── planos.py      📋 Sprint 4 (novo)
├── fiscal.py      📋 Sprint 5 (novo)
└── ferramentas.py 📋 Sprint 8 (novo, opcional)
```

---

## 📊 Métricas de Progresso

| Sprint | Telas | APIs | Acumulado Telas | Acumulado APIs |
|--------|-------|------|-----------------|---------------|
| 1 ✅ | 2 | 5 | 2 | 5 |
| 2 📋 | 3 | 3 | 5 | 8 |
| 3 📋 | 6 | 2 | 11 | 10 |
| 4 📋 | 7 | 9 | 18 | 19 |
| 5 📋 | 3 | 6 | 21 | 25 |
| 6 📋 | 4 | 5 | 25 | 30 |
| 7 📋 | 5 | 4 | 30 | 34 |
| 8 📋 | 4 | 4 | 34 | 38 |

**Meta final:** ~34 telas integradas com APIs reais

---

## ⚠️ Regras de Ouro

1. **NUNCA** avançar para próxima tela sem a atual testada e documentada
2. **SEMPRE** usar `get_api_headers()` — nunca `session.get('access_token')` direto
3. **SEMPRE** seguir `UX_DESIGN_SYSTEM.md` — Nunito, #A38C65, padrão dashboard
4. **SEMPRE** atualizar menu_horizontal.html quando a rota for implementada
5. **NUNCA** deixar link morto no menu — se a tela não existe, remover do menu até estar pronta

---

## 📚 Documentação de Referência

- **`FRONTEND_INTEGRATION_PLAN.md`** — Estratégia de integração API
- **`API_REFERENCE.md`** — Contratos completos das 156 APIs
- **`UX_DESIGN_SYSTEM.md`** — Componentes visuais, cores, tipografia
- **`CODING_STANDARDS.md`** — Padrões de código Python + Jinja2
- **`LESSONS_LEARNED.md`** — Erros já cometidos (evitar repetição)

---

*Criado em: 09/06/2026 | Responsável: Elielson Fontanezi + Cascade AI*
