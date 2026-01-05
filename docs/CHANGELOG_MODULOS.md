
# 📜 Changelog por Módulos - Exitus

Histórico consolidado de módulos M0-M7.5. Detalhes completos em `docs/ARCHIVE/`.

## v0.7.5-m7-complete (05/Jan/2026) `d1bbfd9d`

### M7 Completo (Dashboards + Analytics)
- **M7.3 Alertas**: CRUD completo (`/api/alertas`), frontend toggle/delete, 4 seeds (PETR4 >R$35).[file:17]
- **M7.4 Relatórios**: `/api/relatorios/gerar` + lista paginada (15+ itens, PERFORMANCE 2026-01 ID `247e...`). Sharpe 1.45.
- **M7.5 Cotações**: Multi-provider (brapi/yfinance), cache PostgreSQL 15min TTL.

### Docs Reestruturação
- 5 docs centrais: ARCHITECTURE, USER_GUIDE, API_REFERENCE, RUNBOOK, CHANGELOG.[code_file:122-125]

## v0.7.4-reports-complete (Jan/2026)
- **M7.4 Relatórios LIVE**: POST gerar (0.03s), tabela frontend 2 páginas, export PDF stub.

## v0.7.3-alerts-complete (Dez/2025)
- **M7.3 Alertas 100%**: Frontend mock→real, 6 tipos (`alta_preco`), toggle/delete HTMX.

## v0.7.2-m6-dashboards (06/Dez/2025)
- **M6 Dashboards**: 4 telas (buy-signals, portfolios, transactions, dividends), 4 gráficos Chart.js, fallback mock.

## v0.7.1-m5-frontend (04/Dez/2025)
- **M5 Frontend Base**: 15 rotas + 7 templates, Tailwind/HTMX/Alpine, session JWT 1h.

## v0.7.0-m4-backend (15/Dez/2025)
- **M4 Backend 100%**: 67 rotas, 18 endpoints validados, PortfolioService (8 métodos), Buy Score PETR4 80/100.
- Correções: Enums snake_case, joinedload performance.

## v0.6.x - M0-M3 (Nov/Dez/2025)
- **M0 Infra**: Podman 3 containers, PostgreSQL 15, 12 entidades/86 índices.
- **M1 Auth/CRUD**: JWT, usuarios/corretoras/ativos/transacoes.
- **M2 API Core**: Paginação, schemas Marshmallow.
- **M3 Portfolio**: Posicoes, dashboard agregados, recalculo manual PM.

---

**Convenções**:
- ✅ **Production Ready** | 🔄 **WIP** | ❌ **Planejado**
- Métricas de histórico extraídas de `docs/ARCHIVE/` (checklists M4-M7).

**Próximo (M8)**: Analytics Monte Carlo, export PDF/Excel, Celery alertas.
