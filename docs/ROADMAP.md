# Roadmap de Implementação — Sistema Exitus

> **Versão:** 3.0  
> **Data:** 05 de Março de 2026  
> **Status:** Em Implementação (Fases 2–4 concluídas — Fase 5 planejada)  
> **Branch:** `feature/revisao-negocio-vision`

---

## 📍 Onde Estamos (v0.8.0-dev)

### ✅ Implementado e Funcional

- **67+ endpoints** RESTful validados
- **22 tabelas** PostgreSQL com constraints robustas (inclui `taxa_cambio`, `saldo_prejuizo`)
- **Multi-tenant** por usuário (1:1)
- **Autenticação JWT** com 3 roles (ADMIN, USER, READONLY) e decorator `admin_required`
- **CRUD completo** para 9 entidades (usuarios, ativos, corretoras, transações, proventos, movimentações, eventos corporativos, feriados, regras fiscais)
- **Regras de negócio** (horário, feriados, saldo, taxas B3, day-trade)
- **Importação B3** (Excel/CSV do Portal do Investidor)
- **56 ativos** com dados fundamentalistas (DY, P/L, P/VP, ROE, beta, preco_teto, cap_rate)
- **Cotações multi-provider** com cache TTL 15min (brapi.dev, yfinance, Alpha Vantage, Finnhub)
- **Engine de IR completo** — apuração mensal, compensação de prejuízo, DARF, DIRPF anual, regras 2026
- **Multi-moeda** com conversão automática (3 camadas: banco→cruzamento→fallback)
- **Exportação** CSV, Excel, JSON, PDF com filtros e auditoria
- **Detecção de anomalias** em preços (≥20% sem evento corporativo)
- **Cálculos RF/FII** avançados (Duration, YTM, FFO, AFFO, P/FFO)
- **Buy Signals** (Buy Score 0-100, Preço Teto 4 métodos, Z-Score)
- **Alertas** configuráveis por preço/percentual/indicador
- **Swagger/OpenAPI** auto-documentação em `/api/docs`
- **Recovery enterprise-grade** (backup/restore/rollback com checksum SHA-256)

### 📊 Métricas Atuais

- **56 ativos** no DB (15 ações BR, 10 FIIs, 6 stocks US, 2 REITs, 8 ETFs, 5 RF BR, 10 EU)
- **3 usuários seed** para testes
- **8 módulos PROD** (M0-M7.7)
- **30 GAPs concluídos** (Fases 2, 3 e 4 completas)
- **255+ testes automatizados** ✅ (0 falhos no container) — suite completa verde
- **15 tipos de ativo** (TipoAtivo inclui UNIT)
- **12 ENUMs** normalizados para lowercase

### ⚠️ Nota sobre Frontend

O frontend atual (Flask + HTMX + Tailwind) é funcional mas **não consome** as APIs novas (IR, Export, Câmbio, Anomaly, RFCALC, Swagger). **Poderá ser refeito do zero** em framework moderno (React/Next.js ou similar) quando o backend estiver estabilizado. O foco atual é exclusivamente **backend + banco de dados**.

---

## 🎯 GAPs Identificados

### 1. Fase 2 — Concluída ✅ (9 GAPs)

| GAP ID | Funcionalidade | Status | Data |
|--------|---------------|--------|------|
| **EXITUS-SCRIPTS-001** | Otimização e unificação de scripts | ✅ Concluído | 28/02/2026 |
| **EXITUS-RECOVERY-001** | Sistema de Restore/Recovery Robusto | ✅ Concluído | 28/02/2026 |
| **EXITUS-SEED-001** | Sistema de Seed/Reset Controlado | ✅ Concluído | 02/03/2026 |
| **EXITUS-IMPORT-001** | Importação B3 (Excel/CSV Portal do Investidor) | ✅ Concluído | 02/03/2026 |
| **EXITUS-CASHFLOW-001** | Eventos de custódia B3 (Transferência - Liquidação D+2) | ✅ Concluído | 02/03/2026 |
| **EXITUS-SQLALCHEMY-001** | Padrões e helpers SQLAlchemy (`db_utils.py`) | ✅ Concluído | 02/03/2026 |
| **EXITUS-CRUD-001** | CRUD completo para 9 entidades | ✅ Concluído | 02/03/2026 |
| **EXITUS-BUSINESS-001** | 5 regras de negócio críticas (`business_rules.py`) | ✅ Concluído | 02/03/2026 |
| **EXITUS-ASSETS-001** | 56 ativos com dados fundamentalistas | ✅ Concluído | 02/03/2026 |

### 2. Fase 3 — Qualidade e Cálculos ✅ (13 GAPs)

| GAP ID | Funcionalidade | Status | Data |
|--------|---------------|--------|------|
| **EXITUS-TESTS-001** | Testes automatizados (pytest) | ✅ Concluído | 03/03/2026 |
| **EXITUS-CRUD-002** | Revisão estrutural service/route: exceções tipadas | ✅ Concluído | 03/03/2026 |
| **EXITUS-IR-001** | Engine de cálculo de IR completo (apuração, isenções, DARF) | ✅ Concluído | 03/03/2026 |
| **EXITUS-IR-002** | Custo médio histórico (PM acumulado via tabela `posicao`) | ✅ Concluído | 03/03/2026 |
| **EXITUS-IR-003** | Compensação de prejuízo acumulado entre meses (tabela `saldo_prejuizo`) | ✅ Concluído | 03/03/2026 |
| **EXITUS-IR-004** | Proventos tributáveis: JCP, dividendos, aluguel, withholding tax US | ✅ Concluído | 04/03/2026 |
| **EXITUS-IR-005** | IR sobre renda fixa: tabela regressiva 22,5%→15% | ✅ Concluído | 04/03/2026 |
| **EXITUS-IR-006** | DIRPF anual: relatório para Declaração de Ajuste Anual | ✅ Concluído | 04/03/2026 |
| **EXITUS-IR-007** | Alíquotas dinâmicas via tabela `regra_fiscal` | ✅ Concluído | 03/03/2026 |
| **EXITUS-IR-008** | Tratamento fiscal de UNITs B3 no engine de IR | ✅ Concluído | 04/03/2026 |
| **EXITUS-IR-009** | Regras fiscais 2026 (Lei 15.270/2025): JCP 17,5%, dividendos BR 10%>R$50k | ✅ Concluído | 04/03/2026 |
| **EXITUS-EXPORT-001** | Exportação genérica (CSV, Excel, JSON, PDF) | ✅ Concluído | 03/03/2026 |
| **EXITUS-SQLALCHEMY-002** | Migrar `Query.get()` depreciado para `db.session.get()` | ✅ Concluído | 03/03/2026 |

### 3. Fase 4 — Expansão de Funcionalidades ✅ (8 GAPs)

| GAP ID | Funcionalidade | Status | Data |
|--------|---------------|--------|------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão automática | ✅ Concluído | 04/03/2026 |
| **EXITUS-UNITS-001** | Tratamento de UNITS (B3) | ✅ Concluído | 04/03/2026 |
| **EXITUS-SWAGGER-001** | Auto-documentação OpenAPI/Swagger | ✅ Concluído | 04/03/2026 |
| **EXITUS-ANOMALY-001** | Detecção de anomalias em preços (≥20% sem evento) | ✅ Concluído | 04/03/2026 |
| **EXITUS-RFCALC-001** | Cálculos RF (Duration, YTM) e FII (FFO, AFFO) | ✅ Concluído | 04/03/2026 |
| **EXITUS-NEWAPIS-001** | APIs de configuração (parametros_macro, fonte_dados) | ✅ Concluído | 04/03/2026 |
| **EXITUS-ENUM-001** | Padronizar todos ENUMs PostgreSQL para lowercase | ✅ Concluído | 04/03/2026 |
| **EXITUS-DOCS-IRCONSOLIDAR-001** | Consolidar EXITUS-IR-001.md + EXITUS-IR-009.md em doc único | ✅ Concluído | 05/03/2026 |

### 4. Fase 5 — Robustez, Qualidade e Rentabilidade (Alta Prioridade) 🔴

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-RENTABILIDADE-001** | Rentabilidade TWR + MWR (XIRR) + comparação com benchmarks (CDI, IBOV, IFIX, S&P500) | 📋 Planejado | **Crítico** | **Alta** |
| **EXITUS-VALIDATION-001** | Idempotência na importação B3: deduplicação por chave natural, dry-run, sanitização XSS/SQL Injection | 📋 Planejado | **Alto** | **Alta** |
| **EXITUS-SERVICE-REVIEW-001** | Implementar 4 services stub: `analise_service` (alocação real), `projecao_renda_service` (DY projetado), `relatorio_performance_service` (Sharpe, drawdown), `auditoria_relatorio_service` (fix bug + integrar) | 📋 Planejado | **Alto** | **Alta** |
| **EXITUS-DOCS-SYNC-001** | Sincronizar `API_REFERENCE.md` (v0.7.10→v0.8+), corrigir `MODULES.md`, `LESSONS_LEARNED.md`, consolidar IR docs | 📋 Planejado | **Alto** | **Alta** |
| **EXITUS-COVERAGE-001** | Medir cobertura real (`--cov`) + testes pytest para `import_b3_service.py` (25KB, 0 testes) | 📋 Planejado | **Alto** | **Alta** |

### 5. Fase 6 — Integridade e Infraestrutura (Média Prioridade) 🟡

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-CLEANUP-001** | Remover ~15 arquivos backup/lixo, resolver blueprints duplicados, mover `schemas/ativo_service.py` | 📋 Planejado | Médio | Média |
| **EXITUS-AUDITLOG-001** | Povoar `log_auditoria` em operações CRUD reais (CREATE/UPDATE/DELETE em entidades principais) | 📋 Planejado | Médio | Média |
| **EXITUS-CIRCUITBREAKER-001** | Circuit breaker (pybreaker) + retry com backoff exponencial nos providers de cotação | ✅ Concluído (08/03/2026) | Médio | Média |
| **EXITUS-DARF-ACUMULADO-001** | Persistir DARF < R$10 para acumular entre meses (hoje só informa em alerta) | 📋 Planejado | Médio | Média |
| **EXITUS-RECONCILIACAO-001** | Verificação posição calculada vs importada + saldo corretora vs soma movimentações | 📋 Planejado | Médio | Média |
| **EXITUS-IOF-001** | IOF regressivo (96%→0% em 30 dias) para resgates de RF < 30 dias | 📋 Planejado | Médio | Média |
| **EXITUS-CONSTRAINT-001** | Revisão de CHECK constraints no banco (quantidade>0, valor>=0, saldo>=0, etc.) | ✅ Concluído (08/03/2026) | Médio | Média |
| **EXITUS-SCRIPTS-002** | Revisão/limpeza de `scripts/`: remover obsoletos, resolver duplicidades (.sh vs .py), corrigir `import_b3.py` (shebang bash), melhorar `backup_db.sh` | 📋 Planejado | Médio | Média |
| **EXITUS-TESTFIX-CAMBIO-001** | Corrigir 16 errors em `test_cambio_integration.py` (setup de fixtures, configuração de ambiente) | 📋 Planejado | Baixo | Baixa |

### 6. Fase 7 — Produção e Escala (Média-Alta Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-MULTICLIENTE-001** | Multi-cliente para assessoras (multi-tenancy real) | 📋 Planejado | **Alto** | **Média-Alta** |
| **EXITUS-MONITOR-001** | Monitoramento/alertas operacionais (Prometheus/Grafana) | 📋 Planejado | Médio | Média |
| **EXITUS-RATELIMIT-001** | Rate limiting (Flask-Limiter) | 📋 Planejado | Médio | Média |
| **EXITUS-CICD-001** | CI/CD (GitHub Actions) + Deploy cloud (Railway/Render) | 📋 Planejado | Médio | Média |

### 7. Fase 8 — Expansão Futura e Propostas (Baixa Prioridade) 🟢

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-REBALANCE-001** | Sugestão de rebalanceamento baseada em alocação target vs real | 📋 Planejado | Médio | Baixa |
| **EXITUS-DIVCALENDAR-001** | Calendário de dividendos projetados (baseado em DY histórico + posição atual) | 📋 Planejado | Médio | Baixa |
| **EXITUS-CONCENTRACAO-001** | Métricas de concentração/diversificação (HHI, % máximo por ativo/setor) | 📋 Planejado | Médio | Baixa |
| **EXITUS-BLUEPRINT-CONSOLIDATION-001** | Padronizar blueprints (padrão arquivo vs diretório — unificar) | 📋 Planejado | Baixo | Baixa |
| **EXITUS-ORPHAN-001** | Teste de deleção em cascata + verificação de FKs (dados órfãos) | 📋 Planejado | Baixo | Baixa |
| **EXITUS-FUNDOS-001** | **Proposta futura:** Suporte a Fundos de Investimento (FIAs, FIMs, FIRFs) com come-cotas semestral, gestão de cotas, resgate/aplicação e IR automático | 📋 Proposta | **Alto** | Baixa (futuro) |

### 8. Dívida Técnica e Opcionais

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-CRIPTO-001** | Criptografia AES-256 para dados sensíveis | 📋 Planejado | Baixo | Baixa |
| **EXITUS-AUDIT-001** | Logs de auditoria imutáveis (hash encadeado) | 📋 Planejado | Baixo | Baixa |
| **EXITUS-LGPD-001** | Conformidade LGPD/GDPR (consentimento, esquecimento) | 📋 Planejado | Baixo | Baixa |
| **EXITUS-TESTDB-001** | Script `create_test_db.sh` — recriação automatizada do banco de teste | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTFIX-001** | `test_calculos.py` — 2 testes sem token JWT | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTFIX-002** | `test_buy_signals.py` — `ImportError` | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTFIX-003** | `test_newapis_integration.py` — fixtures corrigidas | ✅ Concluído (04/03/2026) | Baixo | Baixa |
| **EXITUS-TESTENV-001** | Testes só funcionam no container | ✅ Won't Fix (04/03/2026) | Médio | Média |
| **EXITUS-ENUMFIX-001** | Migration `_rename_enum_values` e NOT NULL | ✅ Won't Fix (04/03/2026) | Médio | Média |
| **EXITUS-ENUMFIX-002** | Linter automático `values_callable` em models | ✅ Concluído (04/03/2026) | Baixo | Baixa |
| **EXITUS-SCHEMA-001** | `fonte_dados.rate_limit` — tipo corrigido | ✅ Concluído (04/03/2026) | Médio | Média |

### 9. Registrado para Avaliação Futura (não priorizado)

> Itens identificados no Prompt Mestre ou em análise comparativa com sistemas de mercado.
> Não são GAPs ativos — serão avaliados quando as Fases 5-7 estiverem concluídas.

| Item | Descrição | Origem |
|------|-----------|--------|
| **Redis Cache** | Substituir cache PostgreSQL por Redis — over-engineering sem escala real atual | Prompt Mestre |
| **Hypothesis (property-based tests)** | Testes baseados em propriedades — ROI baixo no estágio atual | Prompt Mestre |
| **Kubernetes manifests** | Prematuro sem CI/CD (CICD-001) | Prompt Mestre |
| **Simulação Monte Carlo** | Otimização de portfólio estocástica | Prompt Mestre (M8) |
| **Otimização Markowitz** | Fronteira eficiente, alocação ótima | Prompt Mestre (M8) |
| **Backtesting** | Testar estratégias contra dados históricos | Prompt Mestre (M8) |
| **WebSocket alertas real-time** | Alertas push via WebSocket — depende de frontend novo | Prompt Mestre (M8) |
| **Come-cotas** | Dedução semestral IR em fundos (maio/novembro) — depende de FUNDOS-001 | Análise de mercado |
| **Reconciliação automática B3 CEI** | Cross-reference com portal B3 — API instável | Análise de mercado |

---

## 🔍 Detalhamento dos GAPs

### EXITUS-SCRIPTS-001: Otimização e Unificação de Scripts

**Problema:** 18 scripts com redundâncias, bugs e falta de padronização

**Impactos críticos:**

- `restore_complete.sh` chama script inexistente (`stop_services.sh`)
- Múltiplos scripts para mesma função (start/stop/restart)
- Inconsistência em validações e tratamento de erros
- Scripts obsoletos (`validate_docs.sh` verifica docs antigos)

**Análise completa:**

- ✅ **13 scripts bem implementados** (backup, rebuild, setup, start, restart, etc.)
- ⚠️ **0 scripts com bugs** (todos resolvidos)
- 🔄 **0 scripts redundantes** (todos têm propósitos distintos)
- 🗑️ **3 scripts removidos** (cleanup_duplicates, restore_complete, validate_docs)
- 📝 **1 script renomeado** (startexitus-local.sh → repair_containers.sh)

**Solução implementada:**

1. ✅ **Corrigidos bugs críticos** (3 scripts removidos)
2. ✅ **Padronizados volumes** (seguindo setup_containers.sh)
3. ✅ **Renomeado script** (startexitus-local.sh → repair_containers.sh)
4. ✅ **Mantidos todos scripts** (propósitos distintos, não redundantes)
5. ✅ **Atualizada documentação** (README.md, ROADMAP.md)

**Status:** Scripts otimizados e padronizados

### EXITUS-RECOVERY-001: Sistema de Restore/Recovery Robusto

**Problema:** Script de restore removido por ser crítico e mal implementado

**Impactos críticos:**

- Sistema de recovery é essencial para produção
- Script atual era frágil (referências erradas, sem validações)
- Restore envolve DB, containers, seeds - precisa arquitetura robusta
- Risco de corrupção de dados com implementação precária

**Requisitos futuros:**

- **Validação de integridade** antes do restore
- **Backup automático** pré-restore
- **Rollback automático** em caso de falha
- **Múltiplos cenários** (parcial, completo, point-in-time)
- **Interface amigável** e segura
- **Logs detalhados** e auditoria

**Status:** ✅ IMPLEMENTADO - Sistema enterprise-grade completo

**Implementação:**

- ✅ **recovery_manager.sh** - Orquestrador principal com todos os modos
- ✅ **validate_recovery.sh** - Validações abrangentes pós-operação
- ✅ **rollback_recovery.sh** - Rollback automático com segurança
- ✅ **recovery_dashboard.sh** - Interface TUI interativa
- ✅ **Integração** com scripts existentes (backup_db, restore_db, populate_seeds)
- ✅ **Enterprise features** - Compressão, checksum, metadados, agendamento
- ✅ **Segurança** - Backup pré-operação, rollback automático, validações

### EXITUS-IMPORT-001: Importação B3 ✅

**Status:** ✅ IMPLEMENTADO

**Implementação:**

- ✅ Parsing de arquivos Excel/CSV do Portal do Investidor B3
- ✅ Importação de proventos (51 testados) e criação automática de ativos (19 testados)
- ✅ Parsing monetário corrigido (formato European)
- ✅ Opção `--clean` para base limpa
- ✅ Eventos de custódia "Transferência - Liquidação" tratados (EXITUS-CASHFLOW-001)

**Nota:** Exportação genérica (CSV, Excel, JSON, PDF) é escopo do novo GAP EXITUS-EXPORT-001

### EXITUS-CRUD-001: CRUD Completo ✅

**Status:** ✅ IMPLEMENTADO (02/03/2026)

**✅ CRUD Completo (9 entidades):**

- **Usuarios:** GET, POST, PUT, DELETE, PATCH password
- **Ativos:** GET, POST, PUT, DELETE + GET by ticker/mercado
- **Corretoras:** GET, POST, PUT, DELETE + GET saldo-total
- **Transações:** GET, POST, PUT, DELETE + GET resumo-ativo
- **Proventos:** GET, POST, PUT, DELETE
- **Movimentações Caixa:** GET, POST, PUT, DELETE + saldo/extrato
- **Eventos Corporativos:** GET, GET by id, POST, PUT, DELETE + POST /aplicar
- **Feriados:** GET, POST, PUT, DELETE (migrado de mock para banco `feriado_mercado`)
- **Regras Fiscais:** GET, POST, PUT, DELETE (migrado de mock para banco `regra_fiscal`)

**📖 Read-only por design (sem CRUD):**

- **Buy Signals:** Cálculos derivados (margem, buy-score, zscore)
- **Cotações:** Consulta a APIs externas com cache TTL 15min
- **Posições:** Calculadas a partir de transações (POST /calcular)

### EXITUS-BUSINESS-001: Regras de Negócio ✅

**5 regras implementadas em `app/utils/business_rules.py`, integradas no `TransacaoService.create()`:**

1. **Validação de horário de mercado** — warning se fora do pregão (B3: 10h-17h, NYSE: 9:30h-16h)
2. **Validação de feriados** — warning se data coincide com feriado cadastrado (tabela `feriado_mercado`)
3. **Validação de saldo antes de venda** — bloqueante, consulta tabela `posicao`
4. **Cálculo automático de taxas B3** — auto-fill emolumentos (0.003297%) e taxa liquidação (0.0275%)
5. **Detecção de day-trade** — flag + warning quando compra/venda no mesmo dia/ativo (IR 20%)

### EXITUS-UNITS-001: Tratamento de UNITS (B3)

**Problema:** UNITS não são tratadas corretamente no sistema

**Impactos:**

- UNITS são derivadas de ações base (ex: PETR4 → PETR4U)
- Desdobramentos afetam preço médio e quantidade
- Conversões reversíveis (UNITS → ações)
- Proventos geralmente não pagos às UNITS

**Ajustes necessários:**

- Adicionar tipo UNIT ao ENUM TipoAtivo
- Relacionar UNITS com ação base
- Ajustar cálculos de posição
- Tratar conversões em transações

### EXITUS-SEED-001: Sistema de Seed/Reset Controlado ✅

**Status:** ✅ IMPLEMENTADO (02/03/2026)

**Implementação:**

- ✅ Script unificado `reset_and_seed.sh` com modos minimal/full/custom
- ✅ Backup/restore de cenários para debugging
- ✅ Dados migrados para formato JSON
- ✅ Seed fundamentalista (`seed_ativos_fundamentalistas.py`) com 56 ativos ricos

### EXITUS-TESTS-001: Testes Automatizados (pytest)

**Problema:** Zero testes automatizados. O Prompt Mestre promete pytest extensivo, mas nenhum test suite existe.

**Impacto:** Crítico — impossível garantir regressão zero ao implementar novos GAPs.

**Escopo proposto:**

- **Unitários:** Models (validações, constraints), Services (CRUD, business rules), Utils (db_utils, business_rules)
- **Integração:** Endpoints REST (auth, ativos, transações), Schemas (serialização/deserialização)
- **Fixtures:** conftest.py com app de teste, DB in-memory ou transacional com rollback
- **Cobertura alvo:** 70%+ nos services e utils críticos

**Dependências:** Nenhuma — pode ser implementado a qualquer momento

### EXITUS-IR-001: Engine de Cálculo de IR Completo ✅

**Status:** ✅ IMPLEMENTADO (03/03/2026)

**Implementação:**

- ✅ `app/services/ir_service.py` — apuração mensal por categoria (swing ações, day-trade, FIIs, exterior)
- ✅ Isenção R$20.000/mês para swing trade em ações BR
- ✅ Alíquotas: ações 15%, day-trade 20%, FIIs 20%, exterior 15%
- ✅ Geração de DARF com código de receita (6015 BR / 0561 exterior)
- ✅ Histórico anual mês a mês
- ✅ Breakdown por corretora
- ✅ `app/blueprints/ir_blueprint.py` — 3 endpoints em `/api/ir/`
- ✅ `tests/test_ir_integration.py` — 19 testes
- ✅ Documentação detalhada: `docs/EXITUS-IR-001.md`

**Tabelas usadas:** `transacao`, `ativo`, `corretora`

**Limitações rastreadas como GAPs:** EXITUS-IR-002 a EXITUS-IR-007 (ver abaixo)

### EXITUS-IR-002: Custo Médio Histórico (PM Acumulado)

**Problema:** O engine atual usa `preco_unitario` da transação de venda como proxy do custo de aquisição. O correto é usar o preço médio ponderado acumulado de todas as compras anteriores, persistido na tabela `posicao`.

**Impacto:** IR calculado pode divergir do real, subestimando ou superestimando lucro dependendo do histórico de compras.

**Solução:** Integrar `PosicaoService` na apuração — buscar `posicao.preco_medio` para o ativo na data imediatamente anterior à venda.

**Dependências:** `EXITUS-IR-001` (concluído), tabela `posicao` populada via `POST /api/posicoes/calcular`

### EXITUS-IR-003: Compensação de Prejuízo Acumulado entre Meses

**Problema:** Prejuízos de um mês não são persistidos. A regra fiscal (IN RFB 1.585/2015) permite compensar prejuízos de meses anteriores contra lucros futuros da mesma categoria (swing × swing, day-trade × day-trade). Sem persistência, o IR calculado pode ser maior que o real.

**Solução:**

- Criar tabela `saldo_prejuizo` com colunas: `usuario_id`, `categoria` (swing/day_trade/fii/exterior), `ano_mes`, `saldo`
- `apurar_mes()` consulta saldo acumulado antes de calcular IR
- Após apuração, persiste novo saldo (prejudízo acumulado ou zerado)

**Dependências:** `EXITUS-IR-001` (concluído), migration nova

### EXITUS-IR-004: Proventos Tributáveis (JCP e Withholding Tax US)

**Problema:** O engine não processa proventos. JCP tem 15% retidos na fonte — não está consolidado no resumo fiscal. Dividendos de ações US têm withholding tax (30%, treaty BR-US pode reduzir).

**Solução:**

- JCP: buscar `provento` onde `tipo = 'JCP'`, consolidar IR retido na fonte e incluir em `/api/ir/apuracao`
- Dividendos US: calcular withholding sobre proventos de `TIPOS_US`
- Novo campo `proventos_tributaveis` na resposta de apuração

**Dependências:** `EXITUS-IR-001` (concluído), tabela `provento`

### EXITUS-IR-005: IR sobre Renda Fixa (Tabela Regressiva)

**Problema:** Ativos `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE` não são calculados no engine. A tabela regressiva vigente: até 180d→22,5%; 181-360d→20%; 361-720d→17,5%; >720d→15%. LCI/LCA são isentos para PF.

**Solução:** Calcular IR retido na fonte para resgates de RF, usando `data_vencimento` e `data_compra` dos ativos. Integrar com `EXITUS-RFCALC-001`.

**Dependências:** `EXITUS-IR-001` (concluído), `EXITUS-RFCALC-001` (Fase 4)

### EXITUS-IR-006: DIRPF Anual (Declaração de Ajuste Anual)

**Problema:** O sistema produz dados para DARF mensal mas não gera relatório estruturado para a Declaração de Ajuste Anual (fichas "Renda Variável" e "Bens e Direitos" do programa IRPF da RFB).

**Solução:**

- Novo endpoint `GET /api/ir/declaracao?ano=YYYY` retornando estrutura para DIRPF
- Consolidar custo de aquisição e situação final de cada ativo em 31/12
- Integrar com `EXITUS-EXPORT-001` para geração de PDF/Excel

**Dependências:** `EXITUS-IR-002`, `EXITUS-IR-003`, `EXITUS-EXPORT-001` (concluídos)

### EXITUS-IR-007: Alíquotas Dinâmicas via Tabela `regra_fiscal`

**Problema:** As alíquotas e constantes fiscais estão hardcoded em `ir_service.py` (15%, 20%, R$20.000, etc). A tabela `regra_fiscal` existe no banco para armazenar essas regras dinamicamente, mas não é usada pelo engine de IR.

**Solução:** Carregar alíquotas e limites de isenção da tabela `regra_fiscal` no início de `apurar_mes()`, com fallback para os valores hardcoded caso a tabela esteja vazia.

**Dependências:** `EXITUS-IR-001` (concluído), `EXITUS-CRUD-001` (CRUD de regras fiscais já implementado)

### EXITUS-IR-008: Tratamento Fiscal de UNITs B3 no Engine de IR

**Problema:** O enum `TipoAtivo` (14 tipos) não inclui `UNIT`. UNITs (ex: `TAEE11`, `KLBN11`, `SANB11`) são certificados de depósito compostos por ações ON + PN (± bônus de subscrição). Se uma UNIT entrar no sistema hoje, cai no branch `default` de `apurar_mes()` e é tratada como `swing_acoes` — o que **por acaso** é fiscalmente correto para a maioria dos cenários, mas sem garantia estrutural.

**Regra fiscal (confirmada com a Receita Federal e IN RFB):**

- UNITs são **equiparadas a ações** para fins de IR sobre renda variável
- Alíquota: **15% swing / 20% day-trade** (igual a ações)
- Isenção de **R$20.000/mês** em vendas: **SIM, aplica-se** (Lei 11.033/2004, art. 3º, I)
- Código DARF: **6015** (igual a ações)
- Dividendos/JCP: seguem regime padrão (dividendos isentos, JCP 15% retido)

**Problema real — desmembramento de UNIT:**

Quando o investidor desmembra uma UNIT em ações ON + PN individuais, o **preço médio deve ser rateado proporcionalmente** entre os papéis resultantes. Exemplo:

- Compra 100 TAEE11 a R$40 = PM R$40
- Desmembramento: 1 UNIT = 1 ON + 2 PN
- PM ON = (40 × proporção ON); PM PN = (40 × proporção PN)

Sem esse rateio, o custo de aquisição das ações resultantes fica **zerado**, gerando IR inflado na venda.

**Consequências de NÃO implementar (risco atual):**

1. **Classificação acidental correta** — como UNITs caem no `default` (swing_acoes), a alíquota e isenção estão corretas hoje. O bug só se manifesta se alguém adicionar lógica que exclua tipos desconhecidos.
2. **Desmembramento não tratado** — se o usuário desmembrar UNITs manualmente e registrar as ações resultantes como compras novas, o PM ficará errado e o IR calculado será incorreto.
3. **DIRPF incorreta** — UNITs e ações resultantes precisam aparecer separadamente em "Bens e Direitos" (código 01).

**Análise custo-benefício — vale o esforço?**

| Aspecto | Avaliação |
|---------|----------|
| Impacto fiscal | **Baixo a médio** — UNITs são equiparadas a ações; a classificação acidental já funciona |
| Frequência de uso | **Baixa** — poucos investidores PF compram UNITs diretamente |
| Risco de bug silencioso | **Médio** — funciona hoje por acidente, pode quebrar com mudanças futuras |
| Complexidade | **Média** — adicionar tipo enum é simples; tratar desmembramento exige evento corporativo |
| Dependência de UNITS-001 | **Forte** — 80% do trabalho é do EXITUS-UNITS-001 (Fase 4) |

**Recomendação: Prioridade BAIXA.** O cenário funciona acidentalmente hoje. A implementação real depende de `EXITUS-UNITS-001` (Fase 4) que adiciona o tipo `UNIT` ao enum e trata conversões. Este GAP (IR-008) deve ser implementado **junto** com UNITS-001, não antes. Registrar agora serve para **não esquecer** o aspecto fiscal quando UNITs forem implementadas.

**Solução proposta (quando implementar):**

1. Adicionar `UNIT = "unit"` ao enum `TipoAtivo` (migration) — escopo UNITS-001

2. Incluir `TipoAtivo.UNIT` em `TIPOS_ACAO_BR` no `ir_service.py` → isenção R$20k correta
3. Tratar evento corporativo "desmembramento de UNIT" rateando PM proporcional — escopo UNITS-001
4. Testes: cenário de venda de UNIT (isento < R$20k, tributado > R$20k), cenário de desmembramento + venda

**Dependências:** `EXITUS-IR-001` (concluído), `EXITUS-UNITS-001` (Fase 4 — pré-requisito forte)

### EXITUS-EXPORT-001: Exportação Genérica ✅

**Status:** ✅ IMPLEMENTADO (03/03/2026)

**Implementação:**

- ✅ `app/services/export_service.py` — engine de exportação (queries + renderers)
- ✅ Formatos: CSV (separador `;`, UTF-8-BOM, cabeçalho metadados), Excel (openpyxl, cabeçalho azul, auto-ajuste), JSON (envelope `{meta, dados, total}`), PDF (reportlab, A4 landscape, zebra-stripe)
- ✅ Entidades: `transacoes`, `proventos`, `posicoes`
- ✅ Filtros: `data_inicio`, `data_fim`, `ativo_id`, `corretora_id`, `tipo`
- ✅ Limite: 10.000 registros por exportação
- ✅ Filename automático: `exitus_{entidade}_{YYYYMMDD_HHMM}.{ext}`
- ✅ Isolamento multi-tenant em proventos via subquery de `ativo_id`
- ✅ `app/blueprints/export_blueprint.py` — 3 endpoints em `/api/export/`
- ✅ `tests/test_export_integration.py` — 32 testes
- ✅ Documentação detalhada: `docs/EXITUS-EXPORT-001.md`

**Tabelas usadas:** `transacao`, `ativo`, `corretora`, `provento` + `PortfolioService` (posições)

**Limitações rastreadas:**

- `GET /api/export/relatorio/{id}` não implementado → GAP **EXITUS-EXPORT-002**
- Posições sem snapshot histórico (data passada) → depende de **EXITUS-IR-006**
- Limite de 10.000 registros fixo (futura paginação/streaming)

### EXITUS-SWAGGER-001: Auto-documentação OpenAPI

**Status:** ✅ Concluído (04/03/2026)

**Implementação:**

- `app/swagger.py`: `Api` flask-restx montada em Blueprint `/api` — Swagger UI em `/api/docs`, spec JSON em `/api/swagger.json`
- Namespaces documentados: auth, ativos, transacoes, ir (apuracao/darf/historico/dirpf), export
- Ativado apenas em modo `production`/`development` (desabilitado em `testing` para isolar testes)
- JWT Bearer security scheme configurado na UI

### EXITUS-ANOMALY-001: Detecção de Anomalias em Preços

**Problema:** Citado no Prompt Mestre mas não implementado.

**Regra:** Alertar quando preço de ativo varia ≥20% sem evento corporativo registrado.
Executar via job periódico ou on-demand ao atualizar cotações.

### EXITUS-RFCALC-001: Cálculos Avançados RF e FII

**Problema:** Indicadores avançados de renda fixa e FIIs não implementados.

**Escopo:**

- **Renda Fixa:** Duration (Macaulay, Modified), Yield to Maturity (YTM), curva de juros
- **FIIs/REITs:** FFO (Funds From Operations), AFFO (Adjusted FFO), P/FFO

### EXITUS-RENTABILIDADE-001: Rentabilidade TWR + MWR + Benchmarks ✅ Concluído (08/03/2026)

**Implementado:**

- **`rentabilidade_service.py`** — TWR (sub-períodos), MWR (XIRR via scipy.optimize.brentq + fallback Newton-Raphson)
- **Benchmarks:** CDI (via `parametros_macro`), IBOV/IFIX/SP500 (via `historico_preco`), IPCA+6%
- **Endpoint:** `GET /api/portfolios/rentabilidade?periodo=12m&benchmark=CDI`
- **Períodos:** 1m, 3m, 6m, 12m, 24m, ytd, max
- **Alpha:** diferença TWR - benchmark retornada automaticamente
- **Testes:** 21 passed em `test_rentabilidade.py`

**Dependências:** Tabelas `transacao`, `movimentacao_caixa`, `posicao`, `historico_preco`, `parametros_macro`

### EXITUS-VALIDATION-001: Idempotência na Importação B3 ✅ Concluído (08/03/2026)

**Implementado:**

- **Hash MD5 por linha** (`hash_importacao` + `arquivo_origem`): reimportar o mesmo arquivo é bloqueado; arquivos diferentes com conteúdo igual são permitidos
- **Modo dry_run=False**: preview sem persistir, retorna contagem de inserções e duplicatas
- **Relatório de duplicatas**: `duplicatas_ignoradas` + `duplicatas_lista` com motivo
- **Sanitização**: `_sanitizar_texto()` remove tags HTML, caracteres de controle Unicode, trunca em 500 chars
- **Correção bug**: `TipoAtivo.FII`/`TipoAtivo.ACAO` enum em vez de strings hardcoded
- **Migration**: `20260308_1500` — campos `hash_importacao` e `arquivo_origem` em `provento` e `transacao`
- **Testes**: 18 passed em `test_import_b3_idempotencia.py`

**Dependências:** `EXITUS-IMPORT-001` (concluído)

### EXITUS-SERVICE-REVIEW-001: Implementar Services Stub ✅ Concluído (08/03/2026)

**Implementado:**

| Service | Estado Anterior | Solução |
|---------|----------------|--------|
| `analise_service.py` | Mock 60/25/15 hardcoded | Alocação real por `Posicao`+`Ativo`, correlação Pearson via `historico_preco` |
| `projecao_renda_service.py` | CRUD sem projeção | `qtd × preco × DY / 12` por tipo provento predominante |
| `relatorio_performance_service.py` | CRUD sem cálculo | Sharpe, max drawdown, volatilidade via `historico_preco` |
| `auditoria_relatorio_service.py` | Bug `current_app.db.session` | Corrigido para `db.session` |

- **Testes:** 23 passed em `test_service_review.py`
- **Suite:** 317 passed, 16 errors (baseline mantido)

### EXITUS-DOCS-SYNC-001: Sincronização de Documentação ✅ Concluído (08/03/2026)

**Implementado:**
- `API_REFERENCE.md`: seções 21 (Rentabilidade) e 22 (Importação B3) adicionadas com exemplos completos
- `MODULES.md`: métricas atualizadas (376 testes, 35 GAPs), Fase 5 marcada concluída
- `LESSONS_LEARNED.md`: L-SVC-001 (`current_app.db`), L-TEST-001 (pandas NaN/CSV)

### EXITUS-COVERAGE-001: Cobertura de Testes ✅ Concluído (08/03/2026)

**Implementado:**
- `tests/test_import_b3_parsers.py`: 59 testes novos (59 passed)
- Cobre: `_parse_data`, `_parse_quantidade`, `_parse_monetario`, `_extrair_ticker`, `_gerar_hash_linha`, `_obter_ou_criar_ativo`, `parse_movimentacoes`, `parse_negociacoes`, `importar_movimentacoes`, `importar_negociacoes`
- Suite: 376 passed, 16 errors (baseline mantido)

### EXITUS-CLEANUP-001: Higiene do Codebase ✅ Concluído (08/03/2026)

**Implementado:**

- 11 arquivos lixo/backup deletados (ver CHANGELOG)
- `schemas/ativo_service.py` deletado (cópia obsoleta — original em `services/`)
- `blueprints/fontesblueprint.py` (mock) deletado — `fonte_dados_blueprint.py` (JWT + real) permanece
- `__init__.py` M4.2 limpo — importação de `fontesblueprint` removida
- Blueprints `feriadosblueprint.py` e `regras_fiscaisblueprint.py` mantidos — únicos ativos, sem duplicatas reais
- Suite: 273 passed, 16 errors (baseline mantido)

### EXITUS-AUDITLOG-001: Povoar Log de Auditoria

**Problema:** Model `log_auditoria` (6637 bytes) existe mas nenhum service grava nele. O Prompt Mestre promete "logs imutáveis com hash encadeado" (AUDIT-001), mas o básico de registrar CREATE/UPDATE/DELETE nem existe.

**Escopo:** Registrar operações em entidades principais (transação, provento, movimentação, ativo). Não inclui hash encadeado (escopo de AUDIT-001).

### EXITUS-CIRCUITBREAKER-001: Circuit Breaker para APIs Externas

**Problema:** Cotações usam try/except simples. Um provider lento trava a request inteira sem fallback rápido.

**Escopo:** pybreaker com threshold de N falhas → circuito abre → pula direto para próximo provider. Complementar com retry + backoff exponencial.

### EXITUS-DARF-ACUMULADO-001: Persistir DARF < R$10

**Problema:** Quando IR < R$10 num mês, a regra fiscal exige acumular para o próximo. O engine sabe disso (emite alerta) mas **não persiste o acúmulo** — perde o valor.

**Escopo:** Persistir em `saldo_prejuizo` ou nova tabela, e somar ao DARF do mês seguinte.

### EXITUS-RECONCILIACAO-001: Verificação de Consistência

**Problema:** Sem mecanismo para detectar divergências entre dados calculados e importados.

**Escopo:**

- Posição calculada vs extrato importado da B3
- Saldo da corretora (`corretora.saldo_atual`) vs `SUM(movimentacao_caixa)`
- Endpoint de verificação: `GET /api/reconciliacao/verificar`

### EXITUS-IOF-001: IOF Regressivo para RF

**Problema:** Resgates de RF com prazo < 30 dias têm IOF regressivo (96%→0% em 30 dias). O engine de IR-005 não calcula IOF.

**Escopo:** Tabela IOF regressiva, integrar com `_apurar_renda_fixa()`.

### EXITUS-CONSTRAINT-001: Revisão de CHECK Constraints

**Problema:** Verificar se todas as tabelas têm CHECK constraints adequados no banco (ex: `quantidade > 0`, `valor >= 0`). Fazer diff entre o que os models definem e o que o banco realmente tem.

### EXITUS-SCRIPTS-002: Revisão e Limpeza de Scripts

**Problema:** 28 scripts em `scripts/` com redundâncias, obsolescência e inconsistências acumuladas desde EXITUS-SCRIPTS-001.

**Diagnóstico (05/03/2026):**

| Categoria | Script | Problema |
|-----------|--------|----------|
| **Obsoleto** | `generate_api_docs.sh` | Gera para `docs/ARCHIVE/` — substituído por Swagger (SWAGGER-001) |
| **One-time** | `migrate_legacy_seeds.py` | Migração de seeds legados já concluída |
| **Bug** | `import_b3.py` | Shebang `#!/bin/bash` num arquivo `.py` — é bash disfarçado |
| **Frágil** | `backup_db.sh` | 12 linhas, sem validação de container, sem compressão, sem rotação |
| **Duplicidade** | `exitus.sh` (307 linhas) | Script unificado sobrepõe 5 scripts individuais (start/stop/restart/restart_backend/restart_frontend) |
| **Duplicidade** | `import_b3.sh` + `import_b3.py` | Dois scripts para mesma função |
| **Duplicidade** | `reset_and_seed.sh` + `reset_and_seed.py` | Dois scripts para mesma função |

**Escopo:**

1. Remover `generate_api_docs.sh` (substituído por Swagger)
2. Remover ou mover `migrate_legacy_seeds.py` para `scripts/archive/`
3. Corrigir `import_b3.py` — renomear para `.sh` ou reescrever como Python real
4. Decidir: `exitus.sh` substitui scripts individuais ou coexistem?
5. Decidir: versão `.sh` vs `.py` para import_b3 e reset_and_seed (manter apenas 1 de cada)
6. Melhorar `backup_db.sh` — validação de container, compressão gzip, rotação de N backups
7. Atualizar `OPERATIONS_RUNBOOK.md` e `.windsurfrules` após limpeza

**Dependências:** Nenhuma. Quick win paralelo a qualquer fase.

### EXITUS-FUNDOS-001: Suporte a Fundos de Investimento (Proposta Futura)

**Problema:** Fundos de investimento (FIAs, FIMs, FIRFs, multimercado) não são suportados. É uma classe de ativos relevante para investidores BR.

**Escopo proposto (quando implementar):**

- Novo tipo no enum `TipoAtivo`: `FUNDO_ACAO`, `FUNDO_MULTIMERCADO`, `FUNDO_RF`, `FUNDO_CAMBIAL`
- Gestão de cotas: aplicação, resgate, conversão D+N
- **Come-cotas semestral** (maio/novembro): dedução automática de IR sobre rendimento acumulado
- IR na fonte: tabela regressiva para fundos de longo prazo, 15% fixo para curto prazo
- IOF para resgates < 30 dias
- Integração com engine de IR existente

**Dependências:** EXITUS-IOF-001, engine de IR (concluído). Complexidade alta — avaliar após Fase 7.

---

## 📅 Plano de Implementação

### Fase 2 — Concluída ✅ (28/02 – 02/03/2026)

1. ✅ Scripts e recovery (SCRIPTS-001, RECOVERY-001)
2. ✅ Seed controlado (SEED-001)
3. ✅ Importação B3 e cashflow (IMPORT-001, CASHFLOW-001)
4. ✅ Padrões SQLAlchemy (SQLALCHEMY-001)
5. ✅ CRUD completo + regras de negócio (CRUD-001, BUSINESS-001)
6. ✅ Massa de ativos fundamentalistas (ASSETS-001)

### Fase 3 — Concluída ✅ (03/03 – 04/03/2026)

1. ✅ Testes automatizados (TESTS-001)
2. ✅ Engine de IR completo: IR-001 a IR-009 + EXPORT-001
3. ✅ Exceções tipadas (CRUD-002) + `db.session.get()` (SQLALCHEMY-002)

### Fase 4 — Concluída ✅ (04/03/2026)

1. ✅ Multi-moeda (MULTIMOEDA-001), UNITS (UNITS-001)
2. ✅ Swagger (SWAGGER-001), Anomalias (ANOMALY-001)
3. ✅ Cálculos RF/FII (RFCALC-001), APIs config (NEWAPIS-001)
4. ✅ ENUMs lowercase (ENUM-001), Consolidação IR docs (DOCS-IRCONSOLIDAR-001)

### Fase 5 — Robustez, Qualidade e Rentabilidade (próximo sprint) 🔴

1. **EXITUS-RENTABILIDADE-001** — TWR + MWR + benchmarks (prioridade máxima)
2. **EXITUS-VALIDATION-001** — Idempotência + dedup + sanitização na importação
3. **EXITUS-SERVICE-REVIEW-001** — Implementar 4 services stub com lógica real
4. **EXITUS-DOCS-SYNC-001** — Sincronizar toda documentação
5. **EXITUS-COVERAGE-001** — Cobertura de testes + testes para import_b3

### Fase 6 — Integridade e Infraestrutura 🟡

1. **EXITUS-CLEANUP-001** — Higiene do codebase (quick win)
2. **EXITUS-AUDITLOG-001** — Povoar log de auditoria
3. **EXITUS-CIRCUITBREAKER-001** — Circuit breaker + retry
4. **EXITUS-DARF-ACUMULADO-001** — Persistir acúmulo DARF < R$10
5. **EXITUS-RECONCILIACAO-001** — Verificação de consistência
6. **EXITUS-IOF-001** — IOF regressivo para RF
7. **EXITUS-CONSTRAINT-001** — CHECK constraints no banco
8. **EXITUS-SCRIPTS-002** — Revisão/limpeza de scripts (quick win paralelo)

### Fase 7 — Produção e Escala

1. **EXITUS-MULTICLIENTE-001** — Multi-tenancy para assessoras
2. **EXITUS-MONITOR-001** — Monitoramento operacional
3. **EXITUS-RATELIMIT-001** — Rate limiting
4. **EXITUS-CICD-001** — CI/CD + deploy cloud

### Fase 8 — Expansão Futura 🟢

1. **EXITUS-REBALANCE-001** — Rebalanceamento sugerido
2. **EXITUS-DIVCALENDAR-001** — Calendário de dividendos
3. **EXITUS-CONCENTRACAO-001** — Métricas de concentração
4. **EXITUS-BLUEPRINT-CONSOLIDATION-001** — Padronizar blueprints
5. **EXITUS-ORPHAN-001** — Testes de cascata/FKs
6. **EXITUS-FUNDOS-001** — Fundos de investimento (proposta)

---

## 📋 Checklist de Implementação

### Para cada GAP:

- [ ] **Análise detalhada** (impacto, complexidade)
- [ ] **Design da API** (contratos, validações)
- [ ] **Implementação backend** (models, services, blueprints)
- [ ] **Testes unitários** (happy path, edge cases)
- [ ] **Documentação** (API_REFERENCE.md)
- [ ] **Testes de integração** (cURL)
- [ ] **Atualização CHANGELOG.md**
- [ ] **Commit e merge**

---

## �️ Execução de Seeds

### Como popular dados iniciais

Os seeds populam o banco com dados fundamentais para testes e desenvolvimento:

```bash
# Acessar o container e executar seeds individuais
podman exec exitus-backend bash -c "cd /app && PYTHONPATH=/app python app/seeds/seed_parametros_macro.py"
podman exec exitus-backend bash -c "cd /app && echo 's' | PYTHONPATH=/app python app/seeds/seed_fontes_dados.py"

# Ou usar script unificado (recomendado)
bash scripts/populate_seeds.sh
# Responder 's' quando solicitado para recriar dados existentes
```

### Seeds disponíveis

| Seed | Descrição | Registros criados |
|------|-----------|-------------------|
| `seed_parametros_macro.py` | Parâmetros macroeconômicos (CDI, SELIC, etc.) | 4 mercados (BR, US, EU, JP) |
| `seed_fontes_dados.py` | Fontes de dados externas (APIs, scrapers) | 7 fontes (yfinance, brapi.dev, etc.) |
| `seed_ativos_fundamentalistas.py` | Ativos com dados fundamentalistas | 56 ativos brasileiros |
| `seed_feriados_b3.py` | Feriados do calendário B3 | Datas anuais |

### Autenticação para testes de API

```bash
# Obter token JWT (credenciais: admin/senha123)
export TOKEN=$(bash scripts/get_backend_token.sh)

# Usar token em requisições
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/parametros-macro
```

---

## 📊 Status Atual (atualizado 05/03/2026)

### Fases Concluídas

| GAP ID | Fase | Status | Data | Observações |
|--------|------|--------|------|-------------|
| EXITUS-SCRIPTS-001 | 2 | ✅ | 28/02/2026 | 15 scripts padronizados, 3 removidos |
| EXITUS-RECOVERY-001 | 2 | ✅ | 28/02/2026 | 4 scripts enterprise-grade |
| EXITUS-SEED-001 | 2 | ✅ | 02/03/2026 | `reset_and_seed.sh` + cenários |
| EXITUS-IMPORT-001 | 2 | ✅ | 02/03/2026 | B3 Excel/CSV, 51 proventos testados |
| EXITUS-CASHFLOW-001 | 2 | ✅ | 02/03/2026 | Eventos de custódia D+2 |
| EXITUS-SQLALCHEMY-001 | 2 | ✅ | 02/03/2026 | `db_utils.py` — 6 helpers |
| EXITUS-CRUD-001 | 2 | ✅ | 02/03/2026 | 9 entidades com CRUD completo |
| EXITUS-BUSINESS-001 | 2 | ✅ | 02/03/2026 | 5 regras em `business_rules.py` |
| EXITUS-ASSETS-001 | 2 | ✅ | 02/03/2026 | 56 ativos com dados fundamentalistas |
| EXITUS-TESTS-001 | 3 | ✅ | 03/03/2026 | pytest + fixtures — 77 testes iniciais |
| EXITUS-CRUD-002 | 3 | ✅ | 03/03/2026 | Exceções tipadas em 10 services |
| EXITUS-IR-001 | 3 | ✅ | 03/03/2026 | Apuração mensal, isenções, DARF — 19 testes |
| EXITUS-IR-002 | 3 | ✅ | 03/03/2026 | PM da tabela `posicao` — 2 testes |
| EXITUS-IR-003 | 3 | ✅ | 03/03/2026 | Compensação prejuízo — tabela `saldo_prejuizo`, 5 testes |
| EXITUS-IR-004 | 3 | ✅ | 04/03/2026 | Proventos tributáveis — 4 testes |
| EXITUS-IR-005 | 3 | ✅ | 04/03/2026 | IR RF tabela regressiva — 7 testes |
| EXITUS-IR-006 | 3 | ✅ | 04/03/2026 | DIRPF anual — 8 testes |
| EXITUS-IR-007 | 3 | ✅ | 03/03/2026 | Alíquotas dinâmicas — 2 testes |
| EXITUS-IR-008 | 3 | ✅ | 04/03/2026 | UNITs no engine de IR — 4 testes |
| EXITUS-IR-009 | 3 | ✅ | 04/03/2026 | Regras fiscais 2026 — 3 testes |
| EXITUS-EXPORT-001 | 3 | ✅ | 03/03/2026 | CSV, Excel, JSON, PDF — 32 testes |
| EXITUS-SQLALCHEMY-002 | 3 | ✅ | 03/03/2026 | `db.session.get()` em 11 arquivos |
| EXITUS-MULTIMOEDA-001 | 4 | ✅ | 04/03/2026 | `CambioService` 3 camadas — 17 testes |
| EXITUS-UNITS-001 | 4 | ✅ | 04/03/2026 | `TipoAtivo.UNIT` (15º tipo) — 8 testes |
| EXITUS-SWAGGER-001 | 4 | ✅ | 04/03/2026 | Swagger UI `/api/docs` — flask-restx |
| EXITUS-ANOMALY-001 | 4 | ✅ | 04/03/2026 | Detecção inline + endpoint — 17 testes |
| EXITUS-RFCALC-001 | 4 | ✅ | 04/03/2026 | Duration, YTM, FFO, AFFO — 24 testes |
| EXITUS-NEWAPIS-001 | 4 | ✅ | 04/03/2026 | parametros_macro + fonte_dados — 8 endpoints cada |
| EXITUS-ENUM-001 | 4 | ✅ | 04/03/2026 | 12 ENUMs lowercase — migration |
| EXITUS-DOCS-IRCONSOLIDAR-001 | 4 | ✅ | 05/03/2026 | IR-001.md + IR-009.md consolidados |

### Fases Planejadas

| GAP ID | Fase | Status | Prioridade | Estimativa |
|--------|------|--------|------------|------------|
| EXITUS-RENTABILIDADE-001 | 5 | 📋 Planejado | **Alta** | 3-4h |
| EXITUS-VALIDATION-001 | 5 | 📋 Planejado | **Alta** | 2-3h |
| EXITUS-SERVICE-REVIEW-001 | 5 | 📋 Planejado | **Alta** | 3-4h |
| EXITUS-DOCS-SYNC-001 | 5 | 📋 Planejado | **Alta** | 2h |
| EXITUS-COVERAGE-001 | 5 | 📋 Planejado | **Alta** | 2-3h |
| EXITUS-CLEANUP-001 | 6 | 📋 Planejado | Média | 30min |
| EXITUS-AUDITLOG-001 | 6 | 📋 Planejado | Média | 2h |
| EXITUS-CIRCUITBREAKER-001 | 6 | ✅ Concluído | Média | 1-2h |
| EXITUS-DARF-ACUMULADO-001 | 6 | 📋 Planejado | Média | 1h |
| EXITUS-RECONCILIACAO-001 | 6 | 📋 Planejado | Média | 2h |
| EXITUS-IOF-001 | 6 | 📋 Planejado | Média | 1h |
| EXITUS-CONSTRAINT-001 | 6 | ✅ Concluído | Média | 1h |
| EXITUS-SCRIPTS-002 | 6 | 📋 Planejado | Média | 1-2h |
| EXITUS-MULTICLIENTE-001 | 7 | 📋 Planejado | Média-Alta | — |
| EXITUS-MONITOR-001 | 7 | 📋 Planejado | Média | — |
| EXITUS-RATELIMIT-001 | 7 | 📋 Planejado | Média | — |
| EXITUS-CICD-001 | 7 | 📋 Planejado | Média | — |
| EXITUS-REBALANCE-001 | 8 | 📋 Planejado | Baixa | 2h |
| EXITUS-DIVCALENDAR-001 | 8 | 📋 Planejado | Baixa | 1-2h |
| EXITUS-CONCENTRACAO-001 | 8 | 📋 Planejado | Baixa | 1h |
| EXITUS-BLUEPRINT-CONSOLIDATION-001 | 8 | 📋 Planejado | Baixa | 1h |
| EXITUS-ORPHAN-001 | 8 | 📋 Planejado | Baixa | 1h |
| EXITUS-FUNDOS-001 | 8 | 📋 Proposta | Baixa (futuro) | — |
| EXITUS-CRIPTO-001 | DT | 📋 Planejado | Baixa | — |
| EXITUS-AUDIT-001 | DT | 📋 Planejado | Baixa | — |
| EXITUS-LGPD-001 | DT | 📋 Planejado | Baixa | — |

**Resumo:** 30 concluídos + 23 planejados + 1 proposta = **54 GAPs rastreados**

---

## 📝 Histórico de Decisões

### 27/02/2026 - Análise GAPs

- **Fase 1 concluída:** Documentação reorganizada
- **Fase 2 iniciada:** Análise sistemática de GAPs
- **8 GAPs identificados** com priorização
- **Decisão:** Multi-cliente reclassificado para Média-Alta (potencial comercial)
- **Adicionado:** EXITUS-UNITS-001 para tratamento de UNITS B3

### 02/03/2026 - EXITUS-SEED-001 Implementado

- **Implementado:** Script unificado `reset_and_seed.sh` substituindo múltiplos scripts legados
- **Implementado:** Backup/restore de cenários para debugging
- **Migrados:** Dados legacy para formato JSON (usuarios.json, ativos_br.json, full.json)
- **Lição:** DELETE vs DROP TABLE para reset de dados
- **Lição:** Sempre verificar tabelas existentes, nunca deduzir
- **Testado:** Seed minimal (3 usuários, 3 ativos, 2 corretoras) ✅

### 28/02/2026 - Discussão Adicional

- **Analisado:** Arquivos reais B3 (Excel) para importação
- **Adicionado:** EXITUS-SEED-001 para controle de seed/reset
- **Analisado:** 18 scripts existentes detalhadamente
- **Adicionado:** EXITUS-SCRIPTS-001 como prioridade crítica
- **Identificados:** 3 bugs críticos, 5 scripts redundantes
- **Total:** 11 GAPs identificados
- **Design criado:** Sistema completo de seed controlado

### 02/03/2026 - Implementação Importação B3 e Eventos de Custódia

- **Implementado:** EXITUS-IMPORT-001 (100% completo) ✅
- **Implementado:** EXITUS-CASHFLOW-001 (100% completo) ✅
- **Corrigido:** Parsing de valores monetários (formato European)
- **Corrigido:** Parsing diferenciado (quantidade vs monetário)
- **Corrigido:** "Transferência - Liquidação" como evento de custódia D+2
- **Adicionado:** EXITUS-ASSETS-001 para massa de teste
- **Adicionado:** EXITUS-SQLALCHEMY-001 para problemas recorrentes
- **Testado:** Importação real com arquivos B3 (51 proventos, 19 ativos)
- **Implementado:** Opção --clean para base limpa
- **Implementado:** Help detalhado do script
- **Criado:** Modelo EventoCustodia completo
- **Integrado:** Service de eventos na importação

### 03/03/2026 - Revisão Geral: Prompt Mestre × Implementação × ROADMAP

- **Auditoria completa:** Prompt Mestre comparado com implementação real
- **Identificadas 7 lacunas** não rastreadas: TESTS-001, IR-001, EXPORT-001, SWAGGER-001, ANOMALY-001, RATELIMIT-001, RFCALC-001
- **Identificadas 3 dívidas técnicas:** AUDIT-001, LGPD-001, CICD-001
- **Corrigidas inconsistências:** duplicata SEED-001, status desatualizados, seções obsoletas
- **Reorganizado ROADMAP:** 5 fases claras (Fase 2 concluída, Fases 3-5 planejadas)
- **Total GAPs:** 9 concluídos + 16 planejados = 25 GAPs rastreados
- **Decisão:** EXITUS-TESTS-001 é prioridade máxima na Fase 3 (dívida técnica crítica)
- **Decisão:** Separar EXPORT-001 de IMPORT-001 (escopos distintos)
- **Observação:** MODULES.md e ARCHITECTURE.md precisam sincronização com estado real

### 05/03/2026 - ROADMAP v3.0: Revisão Abrangente Pós-Fases 3-4

- **Revisão completa** do backend e banco de dados após conclusão das Fases 3-4
- **30 GAPs concluídos** (Fases 2, 3, 4 completas) — suite em 255+ testes
- **17 novos GAPs identificados** em 4 categorias:
  - **Fase 5 (Alta):** RENTABILIDADE-001, VALIDATION-001, SERVICE-REVIEW-001, DOCS-SYNC-001, COVERAGE-001
  - **Fase 6 (Média):** CLEANUP-001, AUDITLOG-001, CIRCUITBREAKER-001, DARF-ACUMULADO-001, RECONCILIACAO-001, IOF-001, CONSTRAINT-001
  - **Fase 8 (Baixa):** REBALANCE-001, DIVCALENDAR-001, CONCENTRACAO-001, BLUEPRINT-CONSOLIDATION-001, ORPHAN-001
- **Proposta futura registrada:** EXITUS-FUNDOS-001 (Fundos de Investimento — FIAs, FIMs, FIRFs, come-cotas)
- **Decisão:** Frontend pode ser **refeito do zero** — foco exclusivo em backend + banco
- **Decisão:** Itens do Prompt Mestre não priorizados (Redis, Hypothesis, Kubernetes, Monte Carlo, Markowitz, Backtesting, WebSocket) registrados para avaliação futura
- **Consolidado:** EXITUS-IR-001.md + EXITUS-IR-009.md em documento único
- **Reorganizado ROADMAP:** 8 fases + Dívida Técnica + Avaliação Futura
- **Total GAPs:** 30 concluídos + 23 planejados + 1 proposta = **54 GAPs rastreados**

---

## 🚀 ROADMAP EXECUTIVO - Fases 5 & 6

> **Status:** Em Execução  
> **Início:** 07/03/2026  
> **Timeline Estimada:** 2 semanas  
> **Modelo IA:** Claude Opus (1 GAP), Claude Sonnet (8 GAPs), SWE-1.5 (5 GAPs)
> **⚠️ NOTA:** Esta seção será **removida automaticamente** ao concluir todos GAPs das Fases 5 & 6

### 📋 Ordem de Execução Otimizada

| Sprint | GAPs | Status | Modelo IA | Dias Estimados |
|--------|------|--------|-----------|----------------|
| **Setup** | Baseline + Backup | ✅ Concluído | - | 0.5 dia |
| **Sprint 1** | VALIDATION-001 + CLEANUP-001 | ✅ Concluído | Sonnet + SWE-1.5 | 1-2 dias |
| **Sprint 2** | RENTABILIDADE-001 + SERVICE-REVIEW-001 | ✅ Concluído | Opus + Sonnet | 2-3 dias |
| **Sprint 3** | COVERAGE-001 + DOCS-SYNC-001 | ✅ Concluído | Sonnet + SWE-1.5 | 1-2 dias |
| **Sprint 4** | CONSTRAINT-001 + CIRCUITBREAKER-001 | ✅ Concluído (08/03/2026) | Sonnet + Sonnet | 1-2 dias |
| **Sprint 5** | AUDITLOG-001 + RECONCILIACAO-001 | ⏳ Planejado | Sonnet + Sonnet | 1-2 dias |
| Sprint 6 | DARF-ACUMULADO-001 + IOF-001 + SCRIPTS-002 + TESTFIX-CAMBIO-001 | ⏳ Planejado | SWE-1.5 + SWE-1.5 | 1 dia |

### 🔄 Status em Tempo Real

**Fase 5 — Robustez, Qualidade e Rentabilidade:**

- [x] EXITUS-VALIDATION-001 — Idempotência importação B3 ✅ Concluído (08/03/2026)
- [x] EXITUS-CLEANUP-001 — Higiene do codebase ✅ Concluído (08/03/2026)
- [x] EXITUS-RENTABILIDADE-001 — TWR + MWR + benchmarks ✅ Concluído (08/03/2026)
- [x] EXITUS-SERVICE-REVIEW-001 — 4 services stub ✅ Concluído (08/03/2026)
- [x] EXITUS-COVERAGE-001 — 59 testes import_b3_service ✅ Concluído (08/03/2026)
- [x] EXITUS-DOCS-SYNC-001 — Sincronização documentação ✅ Concluído (08/03/2026)

**Fase 6 — Integridade e Infraestrutura:**

- [x] EXITUS-CONSTRAINT-001 — CHECK constraints banco — ✅ Concluído (08/03/2026)
- [x] EXITUS-CIRCUITBREAKER-001 — Resiliência APIs — ✅ Concluído (08/03/2026)
- [ ] EXITUS-AUDITLOG-001 — Log auditoria CRUD
- [ ] EXITUS-RECONCILIACAO-001 — Verificação consistência
- [ ] EXITUS-DARF-ACUMULADO-001 — DARF < R$10 acumulado
- [ ] EXITUS-IOF-001 — IOF regressivo RF < 30 dias
- [ ] EXITUS-SCRIPTS-002 — Limpeza scripts
- [ ] EXITUS-TESTFIX-CAMBIO-001 — Corrigir 16 errors testes câmbio

### 📊 Métricas de Execução

**Baseline Atual:**

- Testes: 376 passed, 16 errors
- Cobertura: ?% (coverage com erro de arquivo .coverage)
- GAPs concluídos: 36/54
- Backup: exitus_backup_20260307_113901.tar.gz (1.9MB)

**Metas Finais:**

- Testes: 300+ passing
- Cobertura: 80%+
- GAPs concluídos: 43/54

---

## 🚀 Próximos Passos

1. **Fase 5 — Sprint imediato (Alta Prioridade):**
   - EXITUS-RENTABILIDADE-001 — TWR + MWR + benchmarks (prioridade máxima — feature #1 que falta)
   - EXITUS-VALIDATION-001 — Idempotência na importação B3
   - EXITUS-SERVICE-REVIEW-001 — Implementar 4 services stub com lógica real
   - EXITUS-DOCS-SYNC-001 — Sincronizar toda documentação (parcialmente iniciado nesta revisão)
   - EXITUS-COVERAGE-001 — Medir cobertura + testes para import_b3
2. **Modelo recomendado para Fase 5:**
   - RENTABILIDADE-001 → **Claude Opus** (design de novo subsistema financeiro, TWR/MWR são algoritmos complexos)
   - VALIDATION-001 → **Claude Sonnet** (lógica de negócio moderada, integração com import_b3)
   - SERVICE-REVIEW-001 → **Claude Sonnet** (lógica de negócio em múltiplos arquivos, Sharpe/drawdown)
   - DOCS-SYNC-001 → **SWE-1.5** (atualização mecânica de documentação)
   - COVERAGE-001 → **Claude Sonnet** (testes de integração, edge cases complexos de parser B3)
3. **Pós-Fase 5:** Avaliar Fase 6 (Integridade) — CLEANUP-001 pode ser quick win paralelo

---

*Este arquivo é o controle central do roadmap. Atualizar após cada decisão/desenvolvimento.*  
*Versão: 3.0 — 05 de Março de 2026*  
*Contribuidores: Elielson Fontanezi, Cascade AI*
