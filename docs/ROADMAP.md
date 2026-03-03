# Roadmap de Implementação — Sistema Exitus

> **Versão:** 2.0  
> **Data:** 03 de Março de 2026  
> **Status:** Em Implementação (Fase 2 concluída — Fase 3 em andamento)  
> **Branch:** `feature/revisao-negocio-vision`

---

## 📍 Onde Estamos (v0.8.0-dev)

### ✅ Implementado e Funcional
- **67+ endpoints** RESTful validados
- **21 tabelas** PostgreSQL com constraints robustas
- **Multi-tenant** por usuário (1:1)
- **Autenticação JWT** com 3 roles (ADMIN, USER, READONLY) e decorator `admin_required`
- **CRUD completo** para 9 entidades (usuarios, ativos, corretoras, transações, proventos, movimentações, eventos corporativos, feriados, regras fiscais)
- **Regras de negócio** (horário, feriados, saldo, taxas B3, day-trade)
- **Importação B3** (Excel/CSV do Portal do Investidor)
- **56 ativos** com dados fundamentalistas (DY, P/L, P/VP, ROE, beta, preco_teto, cap_rate)
- **Cotações multi-provider** com cache TTL 15min (brapi.dev, yfinance, Alpha Vantage, Finnhub)
- **Buy Signals** (Buy Score 0-100, Preço Teto 4 métodos, Z-Score)
- **Alertas** configuráveis por preço/percentual/indicador
- **Dashboards** interativos (Chart.js + HTMX)
- **Relatórios** com auditoria
- **Recovery enterprise-grade** (backup/restore/rollback com checksum SHA-256)

### 📊 Métricas Atuais
- **56 ativos** no DB (15 ações BR, 10 FIIs, 6 stocks US, 2 REITs, 8 ETFs, 5 RF BR, 10 EU)
- **3 usuários seed** para testes
- **8 módulos PROD** (M0-M7.7)
- **9 GAPs concluídos** na Fase 2 + 1 na Fase 3 (TESTS-001)
- **69 testes automatizados** ✅ (37 unitários + 32 integração)

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

### 2. Fase 3 — Qualidade e Cálculos (Alta Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-TESTS-001** | Testes automatizados (pytest) | ✅ Concluído | **Crítico** | **Alta** |
| **EXITUS-CRUD-002** | Revisão estrutural service/route: exceções tipadas (`NotFoundError`/`ConflictError`), HTTP 404/409 corretos, `delete()` com guarda de integridade referencial — 31 ocorrências em 10 services | ✅ Concluído (03/03/2026) | **Alto** | **Alta** |
| **EXITUS-IR-001** | Engine de cálculo de IR completo (apuração, isenções, DARF) | Não implementado | **Alto** | **Alta** |
| **EXITUS-EXPORT-001** | Exportação genérica (CSV, Excel, JSON, PDF) | Não implementado | Alto | Alta |

### 3. Fase 4 — Expansão de Funcionalidades (Média Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão automática | Apenas BRL | Médio | Média |
| **EXITUS-UNITS-001** | Tratamento de UNITS (B3) | Não implementado | Médio | Média |
| **EXITUS-SWAGGER-001** | Auto-documentação OpenAPI/Swagger | Não implementado | Médio | Média |
| **EXITUS-ANOMALY-001** | Detecção de anomalias em preços (≥20% sem evento) | Não implementado | Médio | Média |
| **EXITUS-RFCALC-001** | Cálculos RF (Duration, YTM) e FII (FFO, AFFO) | Não implementado | Médio | Média |
| **EXITUS-NEWAPIS-001** | APIs de configuração (parametros_macro, fonte_dados) | Não implementado | Médio | Média |
| **EXITUS-ENUM-001** | Padronizar todos ENUMs PostgreSQL para lowercase (migration) | Não implementado | Médio | Média |
| **EXITUS-SQLALCHEMY-002** | Migrar `Query.get()` depreciado para `db.session.get()` em 11 arquivos (27 ocorrências) | ✅ Concluído (03/03/2026) | Médio | Média |

### 4. Fase 5 — Produção e Escala (Média-Alta Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-MULTICLIENTE-001** | Multi-cliente para assessoras (multi-tenancy real) | Não implementado | **Alto** | **Média-Alta** |
| **EXITUS-MONITOR-001** | Monitoramento/alertas operacionais | Não implementado | Médio | Média |
| **EXITUS-RATELIMIT-001** | Rate limiting (Flask-Limiter) | Não implementado | Médio | Média |
| **EXITUS-CICD-001** | CI/CD (GitHub Actions) + Deploy cloud | Não implementado | Médio | Média |

### 5. Dívida Técnica e Opcionais (Baixa Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-CRIPTO-001** | Criptografia AES-256 para dados sensíveis | Não implementado | Baixo | Baixa |
| **EXITUS-AUDIT-001** | Logs de auditoria imutáveis (hash encadeado) | Não implementado | Baixo | Baixa |
| **EXITUS-LGPD-001** | Conformidade LGPD/GDPR (consentimento, esquecimento) | Não implementado | Baixo (dev) | Baixa |
| **EXITUS-TESTDB-001** | Script `create_test_db.sh` — recriação automatizada do banco de teste | Não implementado | Baixo | Baixa |
| **EXITUS-TESTFIX-001** | `test_calculos.py` — 2 testes sem token JWT retornam 401 em vez de 200 | Não implementado | Baixo | Baixa |
| **EXITUS-TESTFIX-002** | `test_buy_signals.py` — `ImportError: cannot import name 'db' from 'app'` (importação errada no teste) | Não implementado | Baixo | Baixa |

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

### EXITUS-IR-001: Engine de Cálculo de IR Completo
**Problema:** Day-trade é detectado (BUSINESS-001) mas não há engine de cálculo fiscal real.

**Escopo proposto:**
1. **Apuração mensal** de lucro/prejuízo por tipo de ativo
2. **Isenção de R$20k/mês** para ações swing trade (BR)
3. **Alíquotas diferenciadas:** ações 15%, FIIs 20%, day-trade 20%, RF tabela regressiva
4. **Compensação** de prejuízos acumulados entre meses
5. **Geração de DARF** (valor a pagar, código de receita)
6. **Impostos US:** withholding tax 30% sobre dividendos (treaty BR-US)

**Tabelas envolvidas:** `transacao`, `posicao`, `regra_fiscal`, `provento`

### EXITUS-EXPORT-001: Exportação Genérica
**Problema:** Apenas importação B3 existe. Usuários não conseguem exportar dados para análise externa.

**APIs necessárias:**
```
GET /api/export/transacoes?formato=csv|excel|json
GET /api/export/proventos?formato=csv|excel|json
GET /api/export/posicoes?formato=csv|excel|json
GET /api/export/relatorio/{id}?formato=pdf|excel
```

**Funcionalidades:**
- Filtros por período, ativo, corretora
- Cabeçalhos com metadados (usuário, data geração, filtros aplicados)
- Formatação localizada (BRL, datas dd/mm/yyyy)
- Limite configurável de registros

### EXITUS-SWAGGER-001: Auto-documentação OpenAPI
**Problema:** 67+ endpoints sem documentação interativa. API_REFERENCE.md é estática.

**Implementação:** Flask-RESTX ou flasgger para geração automática de Swagger UI.

### EXITUS-ANOMALY-001: Detecção de Anomalias em Preços
**Problema:** Citado no Prompt Mestre mas não implementado.

**Regra:** Alertar quando preço de ativo varia ≥20% sem evento corporativo registrado.
Executar via job periódico ou on-demand ao atualizar cotações.

### EXITUS-RFCALC-001: Cálculos Avançados RF e FII
**Problema:** Indicadores avançados de renda fixa e FIIs não implementados.

**Escopo:**
- **Renda Fixa:** Duration (Macaulay, Modified), Yield to Maturity (YTM), curva de juros
- **FIIs/REITs:** FFO (Funds From Operations), AFFO (Adjusted FFO), P/FFO

---

## 📅 Plano de Implementação

### Fase 2 — Concluída ✅ (28/02 – 02/03/2026)
1. ✅ Scripts e recovery (SCRIPTS-001, RECOVERY-001)
2. ✅ Seed controlado (SEED-001)
3. ✅ Importação B3 e cashflow (IMPORT-001, CASHFLOW-001)
4. ✅ Padrões SQLAlchemy (SQLALCHEMY-001)
5. ✅ CRUD completo + regras de negócio (CRUD-001, BUSINESS-001)
6. ✅ Massa de ativos fundamentalistas (ASSETS-001)

### Fase 3 — Qualidade e Cálculos (próximo sprint)
1. **EXITUS-TESTS-001** — Testes automatizados (pytest + fixtures)
2. **EXITUS-IR-001** — Engine de cálculo de IR completo
3. **EXITUS-EXPORT-001** — Exportação genérica (CSV, Excel, JSON, PDF)

### Fase 4 — Expansão de Funcionalidades
1. **EXITUS-MULTIMOEDA-001** — Conversão multi-moeda
2. **EXITUS-UNITS-001** — UNITS B3
3. **EXITUS-SWAGGER-001** — OpenAPI/Swagger
4. **EXITUS-ANOMALY-001** — Detecção de anomalias
5. **EXITUS-RFCALC-001** — Cálculos RF/FII avançados
6. **EXITUS-NEWAPIS-001** — APIs de configuração

### Fase 5 — Produção e Escala
1. **EXITUS-MULTICLIENTE-001** — Multi-tenancy para assessoras
2. **EXITUS-MONITOR-001** — Monitoramento operacional
3. **EXITUS-RATELIMIT-001** — Rate limiting
4. **EXITUS-CICD-001** — CI/CD + deploy cloud

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

## 🔄 Status Atual (atualizado 03/03/2026)

| GAP ID | Fase | Status | Data | Observações |
|--------|------|--------|------|-------------|
| EXITUS-SCRIPTS-001 | 2 | ✅ Concluído | 28/02/2026 | 15 scripts padronizados, 3 removidos |
| EXITUS-RECOVERY-001 | 2 | ✅ Concluído | 28/02/2026 | 4 scripts enterprise-grade |
| EXITUS-SEED-001 | 2 | ✅ Concluído | 02/03/2026 | `reset_and_seed.sh` + cenários |
| EXITUS-IMPORT-001 | 2 | ✅ Concluído | 02/03/2026 | B3 Excel/CSV, 51 proventos testados |
| EXITUS-CASHFLOW-001 | 2 | ✅ Concluído | 02/03/2026 | Eventos de custódia D+2 |
| EXITUS-SQLALCHEMY-001 | 2 | ✅ Concluído | 02/03/2026 | `db_utils.py` — 6 helpers |
| EXITUS-CRUD-001 | 2 | ✅ Concluído | 02/03/2026 | 9 entidades com CRUD completo |
| EXITUS-BUSINESS-001 | 2 | ✅ Concluído | 02/03/2026 | 5 regras em `business_rules.py` |
| EXITUS-ASSETS-001 | 2 | ✅ Concluído | 02/03/2026 | 56 ativos com dados fundamentalistas |
| EXITUS-TESTS-001 | 3 | 📋 Planejado | — | pytest + fixtures, cobertura 70%+ |
| EXITUS-IR-001 | 3 | 📋 Planejado | — | Apuração mensal, isenções, DARF |
| EXITUS-EXPORT-001 | 3 | 📋 Planejado | — | CSV, Excel, JSON, PDF |
| EXITUS-MULTIMOEDA-001 | 4 | 📋 Planejado | — | Conversão automática BRL/USD/EUR |
| EXITUS-UNITS-001 | 4 | 📋 Planejado | — | UNITS B3 |
| EXITUS-SWAGGER-001 | 4 | 📋 Planejado | — | OpenAPI auto-documentação |
| EXITUS-ANOMALY-001 | 4 | 📋 Planejado | — | Alertas de preço anômalo |
| EXITUS-RFCALC-001 | 4 | 📋 Planejado | — | Duration, YTM, FFO, AFFO |
| EXITUS-NEWAPIS-001 | 4 | 📋 Planejado | — | `parametros_macro`, `fonte_dados` |
| EXITUS-MULTICLIENTE-001 | 5 | 📋 Planejado | — | Multi-tenancy para assessoras |
| EXITUS-MONITOR-001 | 5 | 📋 Planejado | — | Monitoramento operacional |
| EXITUS-RATELIMIT-001 | 5 | 📋 Planejado | — | Flask-Limiter |
| EXITUS-CICD-001 | 5 | 📋 Planejado | — | GitHub Actions + deploy cloud |
| EXITUS-CRIPTO-001 | 5 | 📋 Planejado | — | AES-256 dados sensíveis |
| EXITUS-AUDIT-001 | 5 | 📋 Planejado | — | Hash encadeado em logs |
| EXITUS-LGPD-001 | 5 | 📋 Planejado | — | LGPD/GDPR compliance |

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

---

## 🚀 Próximos Passos

1. **Fase 3 — Sprint imediato:**
   - EXITUS-TESTS-001 (testes automatizados — dívida técnica crítica)
   - EXITUS-IR-001 (engine de cálculo de IR — regra de negócio essencial)
   - EXITUS-EXPORT-001 (exportação genérica — funcionalidade básica faltante)
2. **Sincronizar documentação:** MODULES.md, ARCHITECTURE.md com estado real v0.8.0-dev
3. **Modelo recomendado para Fase 3:**
   - TESTS-001 → **Sonnet 4.6** (integração moderada com múltiplos arquivos)
   - IR-001 → **Sonnet 4.6** (lógica de negócio com regras fiscais complexas)
   - EXPORT-001 → **SWE-1.5** (CRUD mecânico de endpoints de exportação)

---

*Este arquivo é o controle central do roadmap. Atualizar após cada decisão/desenvolvimento.*
