# 🗺️ Mapeamento API ↔ Frontend — Exitus

**Data:** 09/06/2026 | **Versão:** v1.3 — atualizado após Sprints 2-6

---

## 📊 Status Geral

| Categoria | APIs | Integradas | % | Sprint |
|-----------|------|------------|---|--------|
| Dashboard | 8 | 8 | 100% | ✅ base |
| Operações | 25 | 5 | 20% | ✅ Sprint 1 |
| Proventos | 15 | 2 | 13% | ✅ Sprint 2 |
| Ativos | 15 | 2 | 13% | ✅ Sprint 3 |
| Planos | 10 | 1 | 10% | ✅ Sprint 4 |
| Alertas | 10 | 1 | 10% | ✅ Sprint 4 |
| Fiscal/IR | 20 | 4 | 20% | ✅ Sprint 5 |
| Análises | 30 | 5 | 17% | ✅ Sprint 6 |
| Config | 10 | 0 | 0% | 📋 Sprint 8 |
| **TOTAL** | **143** | **28** | **20%** | — |

---

## 🚀 P0 — Operações (Sprint 1-2)

### Transações
- `GET /api/transacoes` → Histórico ⏳
- `POST /api/transacoes` → Nova Compra ⏳
- `PUT /api/transacoes/{id}` → Editar ⏳
- `DELETE /api/transacoes/{id}` → Excluir ⏳

### Importação B3
- `POST /api/import/b3/upload` → Upload ⏳
- `POST /api/import/b3/preview` → Preview ⏳
- `POST /api/import/b3/confirm` → Confirmar ⏳

### Ativos
- `GET /api/ativos` → Catálogo ✅ (Sprint 3)
- `GET /api/ativos?tipo=X` → Filtro por categoria ✅ (Sprint 3)

---

## 📈 P0 — Análises (Sprint 3-4)

### Dashboard
- `GET /api/portfolios/dashboard` → Dashboard ✅
- `GET /api/carteira/saldo-caixa` → Saldo ✅
- `GET /api/portfolios/evolucao` → Evolução ⏳
- `GET /api/portfolios/alocacao` → Alocação ⏳

### Análises
- `GET /api/analises/rentabilidade` → Rentabilidade ⏳
- `GET /api/analises/setores` → Setores ⏳
- `GET /api/analises/comparacao` → Benchmarks ⏳

---

## 💰 P1 — Rendimentos (Sprint 2)

- `GET /api/proventos` → Lista ✅ (Sprint 2)
- `GET /api/proventos/calendario` → Calendário ✅ (Sprint 2)
- `GET /api/proventos/timeline` → Timeline ⏳

---

## 📋 P1 — Fiscal (✅ Sprint 5)

- `GET /api/ir/apuracao` → Apuração Mensal ✅ (Sprint 5)
- `GET /api/ir/darf` → DARFs do Mês ✅ (Sprint 5)
- `GET /api/ir/historico` → Histórico Anual ✅ (Sprint 5)
- `GET /api/ir/dirpf` → DIRPF / Bens e Direitos ✅ (Sprint 5)
- `POST /api/ir/calcular` → Calculadora ⏳
- `GET /api/ir/consolidado` → Consolidado ⏳

---

## 📊 P1 — Análises (✅ Sprint 6)

- `GET /api/portfolios/rentabilidade` → Rentabilidade TWR/MWR ✅ (Sprint 6)
- `GET /api/portfolios/alocacao` → Alocação de Ativos ✅ (Sprint 6)
- `GET /api/portfolios/evolucao` → Evolução Patrimonial ✅ (Sprint 6)
- `GET /api/performance/performance` → Performance Sharpe/Drawdown ✅ (Sprint 6)
- `GET /api/buy-signals/buy-score/<ticker>` → Buy Score por Ticker ✅ (Sprint 6)
- `GET /api/performance/desvio-alocacao` → Desvio de Alocação ✅ (Sprint 6)
- `GET /api/posicoes` → Posições ✅ (Sprint 6 / usado em Buy Signals)

---

## 💼 P1 — Portfolio (Sprint 7)

- `GET /api/posicoes` → Posições ⏳
- `GET /api/portfolios` → Carteiras ⏳
- `POST /api/portfolios` → Criar Carteira ⏳

---

## ⚙️ P3 — Config (Sprint 8)

- `GET /api/alertas` → Alertas ✅ (Sprint 4)
- `POST /api/alertas` → Criar Alerta ⏳
- `GET /api/plano-compra/` → Planos de Compra ✅ (Sprint 4)
- `GET /api/plano-venda/` → Planos de Venda ⏳ (backend 404)
- `GET /api/usuarios/me` → Perfil ⏳

---

**Consultar:** FRONTEND_INTEGRATION_PLAN.md para detalhes
