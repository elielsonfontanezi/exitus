# Módulos do Sistema Exitus (M0–M7)

> **Versão:** stub ativo — 29/06/2026  
> **Fonte canônica de métricas:** [`PROJECT_STATUS.md`](PROJECT_STATUS.md)  
> **Fonte canônica de endpoints:** [`API_REFERENCE.md`](API_REFERENCE.md)  
> **Histórico detalhado:** [`docs/archive/MODULES.md`](archive/MODULES.md)

---

## Índice M0–M7

| Módulo | Nome | Status | Endpoints |
|--------|------|--------|-----------|
| M0 | Infraestrutura | PROD | — |
| M1 | Database Schema | PROD | — |
| M2 | Backend API Core | PROD | 22 |
| M3 | Portfolio Analytics | PROD | 11 |
| M4 | Buy Signals & Fiscais | PROD | 12 |
| M5 | Frontend Base | PROD | 15 |
| M6 | Dashboards Frontend | PROD | 4 |
| M7.4 | Alertas | PROD | 4 |
| M7.5 | Cotações Live | PROD | 3 |
| M7.6 | Relatórios | PROD | 5 |
| M7.7 | Histórico de Preços | PROD | — |
| M7.8 | Rebalanceamento (REBALANCE-001) | PROD | 3 |

**Total:** 159 rotas RESTful — ver [`PROJECT_STATUS.md`](PROJECT_STATUS.md) para contagens e versão atuais.

### M7.8 — Rebalanceamento (novo — 30/06/2026)
- **`rebalance_service.py`**: fonte única de metas, desvio e sugestões
- **Endpoints** em `portfolio_blueprint.py`:
  - `GET /api/portfolios/meta-alocacao`
  - `PUT /api/portfolios/meta-alocacao`
  - `GET /api/portfolios/rebalanceamento/sugestao`
- **`meta_alocacao`** (tabela): persiste percentuais-alvo por usuário+classe
- **`analise_service.analisar_performance_portfolio`** delega para `rebalance_service.calcular_desvio()`

---

## Quando atualizar este arquivo

Atualizar no mesmo commit quando houver **novo blueprint ou endpoint**. Para métricas de testes, GAPs e progresso geral, usar **`PROJECT_STATUS.md`** e **`ROADMAP.md`** — não duplicar números aqui.
