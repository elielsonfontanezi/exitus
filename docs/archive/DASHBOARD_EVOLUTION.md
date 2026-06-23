# 📊 Dashboard Evolution Strategy — Exitus

**Data:** 27/03/2026 | **Versão:** v1.0

---

## 🎯 Decisão: EVOLUIR, não substituir

Dashboard atual está **100% funcional** (R$ 257.677,50). Estratégia: **adicionar widgets incrementalmente**.

---

## ✅ Dashboard Atual — MANTER

**Componentes:**
- ✅ 6 Cards (Patrimônio, Rentabilidade, Saldo, Posições, Proventos, Rentabilidade Total)
- ✅ APIs: `/api/portfolios/dashboard`, `/api/carteira/saldo-caixa`
- ✅ UX: Loading skeletons, tooltips, quick actions

**Arquivo:** `/frontend/app/templates/dashboard/index.html`

---

## 🔄 Roadmap de Evolução

### Sprint 3-4: Análises (P0)
- ➕ Gráfico Evolução Patrimonial → `GET /api/portfolios/evolucao`
- ➕ Gráfico Alocação Setorial → `GET /api/portfolios/alocacao`
- ➕ Top 5 Ativos (dados já vêm no dashboard)

### Sprint 5: Rendimentos (P1)
- ➕ Widget Próximos Proventos → `GET /api/proventos/calendario`
- ➕ Calendário Mini

### Sprint 6: Fiscal (P1)
- ➕ Card IR a Pagar → `GET /api/ir/consolidado`
- ➕ Alerta DARF Vencendo → `GET /api/ir/darf`

### Sprint 7-8: Multi-Moeda (Futuro)
- ➕ Toggle BRL/USD/EUR
- ➕ Cards por Mercado (🇧🇷 🇺🇸 🌍)
- **Pré-requisito:** Backend multi-moeda pronto

---

## 🛠️ Metodologia

**Princípios:**
1. Zero Breaking Changes
2. Feature Flags para novos widgets
3. Testes isolados
4. Rollback fácil

**Fluxo:** Criar componente → Integrar API → Testar → Adicionar ao dashboard → Deploy

---

## 🚨 O que NÃO Fazer

❌ Redesign completo  
❌ Substituir APIs funcionais  
❌ Implementar multi-moeda sem backend  

---

## 🔗 Referências

- `FRONTEND_WIREFRAMES.md` — Wireframes completos
- `FRONTEND_INTEGRATION_PLAN.md` — Plano geral
- `API_FRONTEND_MAPPING.md` — Mapeamento APIs
