## v0.7.6 - Sistema de Histórico de Preços (06/01/2026)

**Commit:** `ab59342` | **Branch:** `feature/lazy-loading-historico` → `main`

### 🎯 Issues Implementados
- **Issue #1:** Model `historico_preco` + Migration Alembic ✅
- **Issue #2:** `HistoricoService` com Lazy Loading (189 linhas) ✅
- **Issue #3:** Refatorar `calcular_zscore()` com dados reais ✅
- **Issue #4:** Script `popular_historico_inicial.py` ✅

### 📦 Arquivos Modificados (8 arquivos, +783 linhas)
- `backend/app/models/historico_preco.py` - Model atualizado
- `backend/app/services/historico_service.py` - **NOVO** (189 linhas)
- `backend/app/services/buy_signals_service.py` - Z-Score refatorado
- `backend/app/services/cotacoes_service.py` - Lazy loading implementado
- `backend/app/scripts/popular_historico_inicial.py` - **NOVO** script
- `backend/app/scripts/README.md` - **NOVO** documentação

### 🚀 Funcionalidades
- **Lazy Loading:** Busca banco primeiro, API apenas se necessário
- **Multi-Mercado:** Brasil (`.SA`), US (sem sufixo), auto-detecção
- **Z-Score Real:** Substituiu array mockado por dados históricos
- **Validações:** Mínimo 30 dias, tratamento std=0
- **Script Manual:** Filtros `--ticker`, `--dias`, `--incluir-deslistados`

### 📊 Impacto
- **Compliance ER x APIs:** 50% → 100% (Z-Score)
- **GAP P0 Resolvido:** Tabela `historico_preco` implementada
- **Performance:** Cache lazy evita chamadas desnecessárias


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
