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

### 🎯 Sprint 2 — Proventos e Rendimentos (PRÓXIMO)
**Valor:** Alto (investidores querem ver dividendos) | **Esforço estimado:** 3–4 dias

| Tela | Rota Frontend | APIs Backend | Blueprint |
|------|--------------|-------------|-----------|
| Proventos Recebidos | `/proventos/recebidos` | GET /api/proventos | `proventos.py` (novo) |
| Proventos Projetados | `/proventos/projetados` | GET /api/proventos?status=PREVISTO | `proventos.py` |
| Calendário de Dividendos | `/proventos/calendario` | GET /api/calendario-dividendos | `proventos.py` |

**Artefatos a criar:**
- `frontend/app/routes/proventos.py` — 3 rotas
- `frontend/app/templates/proventos/recebidos.html`
- `frontend/app/templates/proventos/projetados.html`
- `frontend/app/templates/proventos/calendario.html`
- Registrar blueprint em `__init__.py`
- Atualizar links do menu para rotas reais

**APIs a integrar:** 3 novos endpoints

---

### 📋 Sprint 3 — Catálogo de Ativos
**Valor:** Médio-Alto | **Esforço estimado:** 2–3 dias

| Tela | Rota Frontend | APIs Backend | Filtro |
|------|--------------|-------------|--------|
| Minhas Ações | `/ativos/acoes` | GET /api/ativos?tipo=ACAO | tipo=ACAO |
| Meus FIIs | `/ativos/fiis` | GET /api/ativos?tipo=FII | tipo=FII |
| ETFs | `/ativos/etfs` | GET /api/ativos?tipo=ETF | tipo=ETF |
| Renda Fixa | `/ativos/renda-fixa` | GET /api/ativos?tipo=CDB,LCI_LCA,TESOURO,DEBENTURE | tipo multi |
| Criptoativos | `/ativos/cripto` | GET /api/ativos?tipo=CRIPTO | tipo=CRIPTO |
| Detalhe do Ativo | `/ativos/<ticker>` | GET /api/ativos/ticker/<ticker> | — |

**Artefatos a criar:**
- `frontend/app/routes/ativos.py` — 6 rotas
- `frontend/app/templates/ativos/lista.html` (componente genérico com filtro por tipo)
- `frontend/app/templates/ativos/detalhe.html`
- Registrar blueprint em `__init__.py`

**Nota:** As telas de lista podem compartilhar um único template com parâmetro de tipo — economiza esforço.

**APIs a integrar:** 2 novos endpoints

---

### 📋 Sprint 4 — Planos Disciplinados
**Valor:** Alto (diferencial do produto) | **Esforço estimado:** 4–5 dias

#### Planos de Compra
| Tela | Rota Frontend | APIs Backend |
|------|--------------|-------------|
| Dashboard Planos Compra | `/planos-compra/` | GET /api/plano-compra |
| Novo Plano Compra | `/planos-compra/novo` | POST /api/plano-compra |
| Detalhe Plano | `/planos-compra/<id>` | GET /api/plano-compra/<id> |
| Registrar Aporte | `/planos-compra/<id>/aporte` | POST /api/plano-compra/<id>/aporte |

#### Planos de Venda
| Tela | Rota Frontend | APIs Backend |
|------|--------------|-------------|
| Dashboard Planos Venda | `/planos-venda/` | GET /api/plano-venda |
| Novo Plano Venda | `/planos-venda/novo` | POST /api/plano-venda |
| Detalhe Plano Venda | `/planos-venda/<id>` | GET /api/plano-venda/<id> |

**Artefatos a criar:**
- `frontend/app/routes/planos.py` — 7 rotas
- `frontend/app/templates/planos/compra_lista.html`
- `frontend/app/templates/planos/compra_novo.html`
- `frontend/app/templates/planos/compra_detalhe.html`
- `frontend/app/templates/planos/venda_lista.html`
- `frontend/app/templates/planos/venda_novo.html`
- `frontend/app/templates/planos/venda_detalhe.html`

**APIs a integrar:** ~9 endpoints (CRUD + ações pausar/reativar/cancelar)

---

### 📋 Sprint 5 — Imposto de Renda e DARF
**Valor:** Crítico (obrigação fiscal) | **Esforço estimado:** 3–4 dias

| Tela | Rota Frontend | APIs Backend |
|------|--------------|-------------|
| Cálculo Mensal IR | `/imposto-renda/mensal` | GET /api/ir/calculo-mensal |
| DARFs Pendentes | `/imposto-renda/darfs` | GET /api/ir/darfs-pendentes |
| Declaração Anual | `/imposto-renda/declaracao` | GET /api/ir/declaracao-anual |

**Artefatos a criar:**
- `frontend/app/routes/fiscal.py` — 3 rotas
- `frontend/app/templates/fiscal/ir_mensal.html`
- `frontend/app/templates/fiscal/darfs.html`
- `frontend/app/templates/fiscal/declaracao.html`

**APIs a integrar:** ~6 endpoints (IR + DARF)

---

### 📋 Sprint 6 — Rentabilidade e Análises
**Valor:** Alto (tomada de decisão) | **Esforço estimado:** 3–4 dias

| Tela | Rota Frontend | APIs Backend |
|------|--------------|-------------|
| Rentabilidade por Período | `/rentabilidade/periodo` | GET /api/portfolio/performance |
| Rentabilidade por Ativo | `/rentabilidade/ativo` | GET /api/posicoes + cálculo |
| Alocação de Ativos | `/alocacao` | GET /api/portfolio/alocacao |
| Buy Signals | `/analises/buy-signals` | GET /api/buy-signals/watchlist-top |

**Artefatos a criar:**
- `frontend/app/routes/analises.py` — substituir stub atual (4 rotas)
- `frontend/app/templates/analises/rentabilidade_periodo.html`
- `frontend/app/templates/analises/rentabilidade_ativo.html`
- `frontend/app/templates/analises/alocacao.html`

**APIs a integrar:** ~5 endpoints

---

### 📋 Sprint 7 — Relatórios e Exportação
**Valor:** Médio | **Esforço estimado:** 2–3 dias

| Tela | Rota Frontend | APIs Backend |
|------|--------------|-------------|
| Relatórios Mensais | `/relatorios/mensal` | GET /api/relatorios/lista?tipo=MENSAL |
| Relatórios Anuais | `/relatorios/anual` | GET /api/relatorios/lista?tipo=ANUAL |
| Exportar Excel | `/relatorios/exportar/excel` | POST /api/relatorios/gerar?formato=excel |
| Exportar PDF | `/relatorios/exportar/pdf` | POST /api/relatorios/gerar?formato=pdf |
| Exportar CSV | `/relatorios/exportar/csv` | POST /api/relatorios/gerar?formato=csv |

**Nota:** A rota `/dashboard/reports` já existe — refatorar para servir estas sub-rotas.

**APIs a integrar:** 3–4 endpoints (reaproveitam backend existente)

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
