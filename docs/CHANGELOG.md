# Changelog - Sistema Exitus

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.7.7] - 2026-01-15

### Infrastructure
- **Upgrade PostgreSQL 15.15 → 16.11** ✅
  - Backup completo realizado antes do upgrade
  - Dados migrados sem perda (21 tabelas, 44 ativos, 17 transações)
  - Zero downtime para usuário final
  - Performance verificada: todas as APIs funcionais

### Fixed
- Padronização `POSTGRES_USER=exitus` em toda documentação
- Correção de referências a `exitususer` → `exitus`
- Atualização ARCHITECTURE.md e OPERATIONS_RUNBOOK.md

### Documentation
- Atualização de versão PostgreSQL em docs
- Clarificação: 21 tabelas (20 dados + 1 alembic_version)
- Identificação de rota correta: `/api/portfolios/dashboard`

### Validated
- Backend API REST: 17 blueprints ativos (M2-M7)
- Frontend HTMX: Interface funcional com dados reais
- Conectividade: Frontend ↔ Backend ↔ PostgreSQL 16
- Zero erros em logs após upgrade
- Ref: EXITUS-VAL-INFRA-HEALTH


## [v0.7.6] - 2026-01-06

### Sistema de Histórico de Preços

**Branch**: `feature/lazy-loading-historico` → `main`  
**Commit**: `ab59342`

#### Added
- **Tabela `historico_preco`**: Armazena séries temporais de preços
  - Campos: `ativo_id`, `data`, `preco_fechamento`, `volume`
  - Índice composto: `(ativo_id, data DESC)`
  - Migration: `008_add_historico_preco.py`

- **HistoricoService** (189 linhas):
  - `obter_ou_criar_historico()`: Lazy loading (busca banco → API se necessário)
  - `popular_historico_ativo()`: Integração yfinance multi-mercado
  - Auto-detecção de mercado: Brasil (.SA) vs US (sem sufixo)
  - Fallback gracioso para cache local

- **Script `popular_historico_inicial.py`**:
  - População manual com filtros: `--ticker`, `--dias`, `--incluir-deslistados`
  - Resumo final com estatísticas de sucesso/erro
  - Lazy loading: não repopula se dados já existem
  - Uso: `podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --ticker PETR4 --dias 252`

#### Changed
- **Buy Signal Service - Z-Score Refatorado**:
  - Substituiu array mockado por dados reais de `historico_preco`
  - Validação mínima de 30 dias de histórico
  - Tratamento de erro para `std=0` (preço constante)
  - Parâmetro configurável `dias` (default: 252 = 1 ano)

- **CotacoesService**:
  - Método `buscar_historico()` com parâmetro `mercado`
  - Lazy loading implementado

#### Fixed
- Gap P0 resolvido: Compliance ER x APIs subiu de 50% → 100% para Z-Score

#### Metrics
- **Arquivos modificados**: 8
- **Linhas adicionadas**: +783
- **Performance**: Cache lazy evita chamadas desnecessárias
- **Testes**: ✅ Validação histórico insuficiente, integração com HistoricoService

---

## [v0.7.5] - 2025-12-15

### M7 Completo - Relatórios, Alertas e Cotações

**Commit**: `d1bbfd9d`

#### M7.5 - Cotações Live (09 Dez 2025)

**Added**:
- Sistema de cotações em tempo real com multi-provider fallback
- 3 endpoints:
  - `GET /api/cotacoes/{ticker}` - Cotação individual
  - `GET /api/cotacoes/batch?symbols=A,B,C` - Múltiplos ativos
  - `GET /api/cotacoes/health` - Status do módulo

- **5 Providers** (ordem de fallback):
  1. Cache PostgreSQL (15min TTL) - 85-95% hit rate
  2. brapi.dev (primário - B3)
  3. yfinance (fallback 1 - global)
  4. Alpha Vantage (fallback 2 - US)
  5. Finnhub (fallback 3 - US/EU)

- **Container Hardening**:
  - Non-root user (`exitus:1000`)
  - Healthcheck robusto (30s interval)
  - Rate limit 429 tratado gracefully

**Metrics**:
- Response time (cache): 0.03-0.3s
- Response time (API): 0.25-5s
- Cache hit rate: 85-95%
- Disponibilidade: 99.9% (5 camadas)

#### M7.4 - Relatórios (Jan 2026)

**Added**:
- 5 endpoints de relatórios:
  - `GET /api/relatorios/lista` - Lista paginada
  - `POST /api/relatorios/gerar` - Gerar novo
  - `GET /api/relatorios/{id}` - Detalhar
  - `POST /api/relatorios/{id}/exportar` - Export PDF (stub)
  - `DELETE /api/relatorios/{id}` - Deletar

- **Tipos de Relatório**:
  - PERFORMANCE: Sharpe Ratio 1.45, Max Drawdown -12.3%
  - FISCAL: IR devido, transações tributáveis
  - ALOCACAO: Distribuição por classe/setor

- Frontend: Tabela com 2 páginas, export PDF stub

#### M7.3 - Alertas (Dez 2025)

**Added**:
- 4 endpoints de alertas:
  - `GET /api/alertas` - Listar
  - `POST /api/alertas` - Criar
  - `PATCH /api/alertas/{id}/toggle` - Ativar/desativar
  - `DELETE /api/alertas/{id}` - Deletar

- **6 Tipos de Alerta**:
  1. ALTA_PRECO
  2. BAIXA_PRECO
  3. DY_MINIMO
  4. PL_MAXIMO
  5. VOLUME_ANORMAL
  6. MARGEM_SEGURANCA

- Frontend: CRUD completo, toggle/delete via HTMX
- Seeds: 4 alertas exemplo (PETR4 R$ 35, etc)

#### Documentation Restructure

**Added**:
- 5 documentos centrais:
  - `ARCHITECTURE.md` - Arquitetura técnica
  - `USER_GUIDE.md` - Guia do usuário
  - `API_REFERENCE.md` - Documentação de APIs
  - `OPERATIONS_RUNBOOK.md` - Deploy e troubleshooting
  - `CHANGELOG.md` - Este arquivo

---

## [v0.7.0] - 2025-12-15

### M4 Backend - Production Ready

**Commit**: Várias iterações até validação completa

#### Added
- **Buy Signals** (6 endpoints):
  - Buy Score (0-100) com 5 critérios
  - Preço Teto (4 métodos: Bazin, Graham, Gordon, Médio)
  - Z-Score (mockado - substituído por real em v0.7.6)
  - Margem de Segurança
  - Watchlist Top (planejado)

- **Cálculos Financeiros** (2 endpoints):
  - `GET /api/calculos/portfolio` - Métricas consolidadas
  - `GET /api/calculos/preco-teto/{ticker}` - Preço teto com 4 métodos

- **Regras Fiscais** (4 endpoints):
  - CRUD completo de regras fiscais
  - 6 regras cadastradas: BR (ações 15%, FII 20%), US (dividendos 15%)

- **Feriados** (4 endpoints):
  - Calendário BR/US 2025-2026
  - Validação de operações em dias úteis

- **Fontes de Dados** (4 endpoints):
  - Gestão de APIs externas
  - Prioridades e rate limits

#### Fixed
- **Enums SQLAlchemy**: Serialização para JSON corrigida
  - Antes: `ClasseAtivo.RENDAVARIAVEL` (objeto Python)
  - Depois: `"rendavariavel"` (string JSON-serializável)

- **PortfolioService**: Classe completa implementada com 8 métodos
  - `get_dashboard()`
  - `get_alocacao()`
  - `get_portfolio_metrics()`
  - `get_distribuicao_classes()`
  - `get_distribuicao_setores()`
  - `get_evolucao_patrimonial()`
  - `get_metricas_risco()`
  - `get_performance_ativos()`

- **Blueprints**: 6 novos registrados em `app/__init__.py`
  - `feriados_bp`
  - `fontes_bp`
  - `regras_fiscais_bp`
  - `calculos_bp`
  - `buy_signals_bp`
  - `portfolio_bp` (rota `/alocacao` adicionada)

- **URLs Padronizadas**: Hífens em vez de underscores
  - `/api/regras-fiscais` (antes: `/api/regrasfiscais`)

#### Metrics
- **18 endpoints validados**: 100% taxa de sucesso
- **67 rotas totais**: Documentadas em API_REFERENCE_COMPLETE.md
- **Response time**: 50-200ms (cálculos complexos: 100-500ms)

---

## [v0.7.2] - 2025-12-06

### M6 - Dashboards Frontend

**Status**: ✅ PRODUCTION READY

#### Added
- **4 Dashboards Completos**:
  1. Buy Signals (tabela + gráfico barras)
  2. Portfolios (cards + gráfico pizza + tabela)
  3. Transações (tabela + 2 gráficos)
  4. Proventos (tabela + gráfico linha)

- **5 Gráficos Chart.js**:
  - Buy Score (barras horizontais)
  - Alocação por classe (pizza/donut)
  - Evolução patrimonial (linha)
  - Transações por tipo (barras)
  - Proventos mensais (linha)

- **Funcionalidades Frontend**:
  - Modal "Nova Carteira" (Alpine.js)
  - Tabelas paginadas (10 itens/página)
  - Filtros por ticker, tipo, período
  - Fallback para mock data (backend offline)

#### Metrics
- **4 dashboards**: 100% funcionais
- **5 gráficos**: Renderização <1s
- **10 screenshots**: Documentados em validação
- **Response time**: 200-800ms (inclui renderização gráficos)

---

## [v0.7.1] - 2025-12-04

### M5 - Frontend Base

**Status**: ✅ PRODUCTION READY

#### Added
- **15 Rotas Frontend**:
  - Públicas: `/`, `/auth/login`, `/auth/register`
  - Protegidas: `/dashboard`, `/logout`, etc

- **7+ Templates Jinja2**:
  - `base.html` - Layout mestre
  - `auth/login.html`, `auth/register.html`
  - `dashboard/index.html`
  - Partials: navbar, sidebar, flash_messages

- **Stack Frontend**:
  - HTMX 2.0 (partial updates sem reload)
  - Alpine.js 3.14 (dropdowns, modals)
  - TailwindCSS 3.4 (via CDN)
  - Chart.js 4.4 (gráficos)

- **Session Management**:
  - JWT em session Flask
  - Middleware de autenticação
  - Flash messages (sucesso/erro)
  - Logout funcional

#### Metrics
- **15 rotas**: 100% funcionais
- **Response time (SSR)**: 50-150ms
- **Mobile responsive**: ✅ Navbar/Sidebar adaptáveis

---

## [v0.6.x] - 2025-11-12 a Dez 2025

### M0-M3 - Foundation

#### M3 - Portfolio Analytics (Dez 2025)

**Added**:
- 11 endpoints de portfolio:
  - Dashboard consolidado
  - Alocação por classe
  - Performance individual
  - Distribuição por classe/setor
  - Evolução patrimonial (até 24 meses)
  - Métricas de risco

- **PortfolioService**: 8 métodos de cálculo
- **Métricas Implementadas**:
  - Volatilidade anualizada
  - Sharpe Ratio
  - Max Drawdown
  - Beta vs IBOV (planejado)

#### M2 - Backend API Core (Dez 2025)

**Added**:
- Autenticação JWT (1h expiry)
- 16 blueprints registrados
- 20 endpoints CRUD base:
  - Usuários, Corretoras, Ativos
  - Posições, Transações, Proventos
  - Movimentações de Caixa, Eventos Corporativos

- **Validação**: Marshmallow schemas
- **Paginação**: Automática (default: 10 items/página)
- **CORS**: Habilitado para frontend

#### M1 - Database Schema (Nov 2025)

**Added**:
- 20 tabelas PostgreSQL 16:
  - Core: usuario, corretora, ativo
  - Portfolio: posicao, transacao, provento
  - Operations: movimentacao_caixa, evento_corporativo
  - Reference: feriado, fonte_dados, regra_fiscal
  - Analytics: portfolio, alerta, relatorio, projecao
  - System: log_auditoria, parametro

- **86+ índices otimizados**
- **8 migrations Alembic**
- **Seeds de dados**: 2 usuários, 3 corretoras, 17 ativos

#### M0 - Infrastructure (Nov 2025)

**Added**:
- Podman 4.x (rootless)
- 3 containers:
  - exitus-db (PostgreSQL 16)
  - exitus-backend (Flask 3.0 + Python 3.11)
  - exitus-frontend (Flask 3.0 + HTMX)

- Rede bridge customizada: `exitus-net`
- Volumes persistentes
- Scripts de gerenciamento: start, stop, restart, logs

---

## Roadmap Futuro

### [v0.8.0] - M8: Analytics Avançados (Q2 2026)

**Planejado**:
- Simulação Monte Carlo
- Otimização de Portfolio (Markowitz)
- Backtesting de estratégias
- Alertas em tempo real (WebSocket)
- Export PDF/Excel avançado (layout profissional)
- Celery para tarefas assíncronas
- Notificações por e-mail/Telegram
- Suporte a criptomoedas

**Bibliotecas**:
- PyPortfolioOpt
- QuantLib (bonds pricing)
- Celery + Redis

**Duração Estimada**: 20-30 horas

---

### [v0.9.0] - M9: Deploy & Monitoramento (Q1 2026)

**Planejado**:
- CI/CD com GitHub Actions
- Deploy em Railway/Render/Fly.io
- Monitoramento com Prometheus + Grafana
- Logs centralizados (ELK stack ou similar)
- Health checks avançados
- Backups automáticos (diários)
- Testes end-to-end (Selenium/Playwright)

**Duração Estimada**: 10-15 horas

---

## Convenções de Commit

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `refactor:` Refatoração de código
- `test:` Testes
- `chore:` Tarefas de build/config
- `perf:` Melhorias de performance

**Exemplos**:
```
feat(buy-signals): adicionar cálculo de Z-Score com histórico real
fix(portfolio): corrigir serialização de enums para JSON
docs(api): atualizar API_REFERENCE com novos endpoints
```

---

## Breaking Changes

### v0.7.0 → v0.7.6

**Nenhuma mudança quebrando compatibilidade**

Todas as mudanças foram aditivas:
- Novos endpoints adicionados
- Campos novos em tabelas (sem remover existentes)
- APIs mantém retrocompatibilidade

### Futuras Breaking Changes (v0.8.0+)

**Planejado**:
- Migração de JWT expiry: 1h → 24h (requer re-login após update)
- Mudança de formato de datas: ISO 8601 com timezone explícito
- Renomeação de endpoints: `/api/v1/*` versionamento de API

---

## Métricas do Projeto

### Linhas de Código (v0.7.6)

| Componente | Linhas | Arquivos |
|------------|--------|----------|
| **Backend** | ~15.000 | 85 |
| **Frontend** | ~3.500 | 25 |
| **Migrations** | ~1.200 | 8 |
| **Testes** | ~2.000 | 20 |
| **Scripts** | ~800 | 12 |
| **Docs** | ~8.000 | 20+ |
| **Total** | ~30.500 | 170+ |

### Cobertura de Testes

- **Backend**: 45% (planejado: 80% em M8)
- **Frontend**: 10% (planejado: 60% em M8)

### Performance

| Métrica | Valor | Observação |
|---------|-------|------------|
| **Response Time Médio** | 150ms | Endpoints simples |
| **Response Time 95p** | 500ms | Cálculos complexos |
| **Cache Hit Rate** | 90% | Cotações |
| **Uptime** | 99.5% | Desenvolvimento |
| **Concurrent Users** | 20-40 | Teste de stress |

---

## Contribuidores

- **Elielson Fontanezi** - Desenvolvimento inicial e arquitetura
- **Perplexity AI** - Assistência em desenvolvimento e documentação

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../LICENSE) para mais detalhes.

---

## Links Úteis

- **Repositório**: https://github.com/elielsonfontanezi/exitus
- **Issues**: https://github.com/elielsonfontanezi/exitus/issues
- **Documentação**: [docs/](.)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)

---

**Última atualização**: 07 de Janeiro de 2026  
**Versão atual**: v0.7.6  
**Próxima versão**: v0.8.0 (M8 - Deploy & Monitoramento)
