# 🗺️ Mapeamento API ↔ Frontend — Exitus

**Data:** 26/03/2026 | **Versão:** v1.0

---

## 📊 Status Geral

| Categoria | APIs | Integradas | % |
|-----------|------|------------|---|
| Dashboard | 8 | 8 | 100% |
| Operações | 25 | 2 | 8% |
| Análises | 30 | 1 | 3% |
| Rendimentos | 15 | 0 | 0% |
| Fiscal | 20 | 0 | 0% |
| Portfolio | 20 | 1 | 5% |
| Ativos | 15 | 0 | 0% |
| Config | 10 | 0 | 0% |
| **TOTAL** | **143** | **12** | **8%** |

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
- `GET /api/ativos` → Catálogo ⏳
- `GET /api/ativos/search` → Busca ⏳

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

## 💰 P1 — Rendimentos (Sprint 5)

- `GET /api/proventos` → Lista ⏳
- `GET /api/proventos/calendario` → Calendário ⏳
- `GET /api/proventos/timeline` → Timeline ⏳

---

## 📋 P1 — Fiscal (Sprint 6)

- `POST /api/ir/calcular` → Calculadora ⏳
- `GET /api/ir/darf` → DARF ⏳
- `GET /api/ir/consolidado` → Consolidado ⏳

---

## 💼 P1 — Portfolio (Sprint 7)

- `GET /api/posicoes` → Posições ⏳
- `GET /api/portfolios` → Carteiras ⏳
- `POST /api/portfolios` → Criar Carteira ⏳

---

## ⚙️ P3 — Config (Sprint 8)

- `GET /api/alertas` → Alertas ⏳
- `POST /api/alertas` → Criar Alerta ⏳
- `GET /api/usuarios/me` → Perfil ⏳

---

**Consultar:** FRONTEND_INTEGRATION_PLAN.md para detalhes
