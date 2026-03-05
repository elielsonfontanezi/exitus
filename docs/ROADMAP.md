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
- **77 testes automatizados** ✅ (0 falhos) — suite completa verde

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
| **EXITUS-IR-001** | Engine de cálculo de IR completo (apuração, isenções, DARF) | ✅ Concluído (03/03/2026) | **Alto** | **Alta** |
| **EXITUS-IR-002** | Custo médio histórico (PM acumulado via tabela `posicao`) | ✅ Concluído (03/03/2026) | **Alto** | **Alta** |
| **EXITUS-IR-003** | Compensação de prejuízo acumulado entre meses (tabela `saldo_prejuizo`) | ✅ Concluído (03/03/2026) | **Alto** | **Alta** |
| **EXITUS-IR-004** | Proventos tributáveis: JCP, dividendos, aluguel, withholding tax US (baseline pré-2026) | ✅ Concluído (04/03/2026) | **Alto** | **Alta** |
| **EXITUS-IR-005** | IR sobre renda fixa: tabela regressiva 22,5%→15% por prazo de aplicação | ✅ Concluído (04/03/2026) | Alto | Alta |
| **EXITUS-IR-006** | DIRPF anual: relatório para Declaração de Ajuste Anual (fichas Renda Variável, Proventos e Bens e Direitos) | ✅ Concluído (04/03/2026) | **Alto** | **Média** |
| **EXITUS-IR-007** | Alíquotas dinâmicas via tabela `regra_fiscal` (atualmente hardcoded em `ir_service.py`) | ✅ Concluído (03/03/2026) | Médio | Média |
| **EXITUS-IR-008** | Tratamento fiscal de UNITs B3 no engine de IR (classificação, isenção R$20k, desmembramento→PM) | ✅ Concluído (04/03/2026) | Médio | Baixa |
| **EXITUS-IR-009** | Atualização regras fiscais 2026 (Lei 15.270/2025): JCP 17,5%, dividendos BR 10% acima R$50k, imposto mínimo | ✅ Concluído (04/03/2026) | **Alto** | **Alta** |
| **EXITUS-EXPORT-001** | Exportação genérica (CSV, Excel, JSON, PDF) | ✅ Concluído (03/03/2026) | Alto | Alta |

### 3. Fase 4 — Expansão de Funcionalidades (Média Prioridade)

| GAP ID | Funcionalidade | Status | Impacto | Prioridade |
|--------|---------------|--------|---------|------------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão automática | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-UNITS-001** | Tratamento de UNITS (B3) | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-SWAGGER-001** | Auto-documentação OpenAPI/Swagger | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-ANOMALY-001** | Detecção de anomalias em preços (≥20% sem evento) | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-RFCALC-001** | Cálculos RF (Duration, YTM) e FII (FFO, AFFO) | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-NEWAPIS-001** | APIs de configuração (parametros_macro, fonte_dados) | ✅ Concluído (04/03/2026) | Médio | Média |
| **EXITUS-ENUM-001** | Padronizar todos ENUMs PostgreSQL para lowercase (migration) | ✅ Concluído (04/03/2026) | Médio | Média |
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
| **EXITUS-TESTDB-001** | Script `create_test_db.sh` — recriação automatizada do banco de teste | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTFIX-001** | `test_calculos.py` — 2 testes sem token JWT retornam 401 em vez de 200 | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTFIX-002** | `test_buy_signals.py` — `ImportError: cannot import name 'db' from 'app'` (importação errada no teste) | ✅ Concluído (03/03/2026) | Baixo | Baixa |
| **EXITUS-TESTENV-001** | 173 testes com `ERROR at setup` — `marshmallow_sqlalchemy` não instalado no ambiente local; testes só funcionam dentro do container | ✅ Won't Fix (04/03/2026) — ambiente canônico é o container; RUNBOOK atualizado com instrução explícita | Médio | Média |
| **EXITUS-ENUMFIX-001** | Migration `_rename_enum_values` não preserva `NOT NULL` ao recriar colunas ENUM — requer `ALTER COLUMN ... SET NOT NULL` pós-migration; corrigir função helper na próxima migration que use ENUMs | ✅ Won't Fix (04/03/2026) — `create_test_db.sh` já usa `pg_dump --schema-only`; problema era operacional; RUNBOOK atualizado com obrigatoriedade pós `alembic upgrade` | Médio | Média |
| **EXITUS-ENUMFIX-002** | Models Python sem `values_callable` causam `LookupError` ao ler ENUMs lowercase do banco — todos corrigidos em ENUM-001, mas padrão deve ser documentado em `CODING_STANDARDS.md` e enforçado em novos models | ✅ Concluído (04/03/2026) — `tests/test_model_standards.py` varre AST de todos os models via pytest | Baixo | Baixa |
| **EXITUS-SCHEMA-001** | `fonte_dados.rate_limit` — campo `Numeric` no schema Marshmallow conflita com valor string (`"2000/hour"`); campo deveria ser `String` — causa `decimal.ConversionSyntax` no endpoint `/api/fontes-dados` | ✅ Concluído (04/03/2026) — `taxa_sucesso`/`taxa_erro`/`health_status` convertidos para `@property`; `tipo_fonte` usa `fields.Method` no schema | Médio | Média |

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
1. **EXITUS-TESTS-001** — Testes automatizados (pytest + fixtures) ✅
2. **EXITUS-IR-001** — Engine de cálculo de IR completo ✅
3. **EXITUS-IR-002** — Custo médio histórico (PM acumulado)
4. **EXITUS-IR-003** — Compensação de prejuízo acumulado entre meses
5. **EXITUS-IR-004** — JCP (15% retido) e withholding tax US
6. **EXITUS-IR-005** — IR renda fixa (tabela regressiva)
7. **EXITUS-IR-006** — DIRPF anual (Declaração de Ajuste Anual)
8. **EXITUS-IR-007** — Alíquotas dinâmicas via `regra_fiscal`
9. **EXITUS-IR-008** — Tratamento fiscal de UNITs B3 (implementar junto com UNITS-001)
10. **EXITUS-EXPORT-001** — Exportação genérica (CSV, Excel, JSON, PDF) ✅

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

## �� Status Atual (atualizado 04/03/2026)

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
| EXITUS-IR-001 | 3 | ✅ Concluído | 03/03/2026 | Apuração mensal, isenções, DARF — 19 testes |
| EXITUS-IR-002 | 3 | ✅ Concluído | 03/03/2026 | PM da tabela `posicao` no cálculo de IR — 2 testes |
| EXITUS-IR-003 | 3 | ✅ Concluído | 03/03/2026 | Compensação prejuízo acumulado — tabela `saldo_prejuizo`, 5 testes |
| EXITUS-IR-004 | 3 | ✅ Concluído | 04/03/2026 | Proventos: JCP 15%, dividendos BR isentos, dividendos US 15%, aluguel 15% — seção `proventos` na API, 4 testes |
| EXITUS-IR-005 | 3 | ✅ Concluído | 04/03/2026 | `_apurar_renda_fixa`, `_aliquota_rf`, DARF 0561, ficha renda_fixa no DIRPF — 7 testes |
| EXITUS-IR-006 | 3 | ✅ Concluído | 04/03/2026 | DIRPF anual — endpoint `/api/ir/dirpf`, fichas RV + Proventos + Bens e Direitos, `persist=False`, 8 testes |
| EXITUS-IR-007 | 3 | ✅ Concluído | 03/03/2026 | Alíquotas dinâmicas via `regra_fiscal` — seed 5 regras, fallback hardcoded, 2 testes |
| EXITUS-IR-008 | 3 | ✅ Concluído | 04/03/2026 | `TIPOS_ACAO_BR` inclui `TipoAtivo.UNIT`, isenção R$20k, alíquota 15% — 4 testes |
| EXITUS-IR-009 | 3 | ✅ Concluído | 04/03/2026 | JCP 17,5% (2026+), dividendos BR 10%>R$50k/CNPJ, regras seedadas — 3 testes |
| EXITUS-EXPORT-001 | 3 | ✅ Concluído | 03/03/2026 | CSV, Excel, JSON, PDF — 32 testes |
| EXITUS-MULTIMOEDA-001 | 4 | ✅ Concluído | 04/03/2026 | Tabela `taxa_cambio`, `CambioService` (3 camadas: banco→cruzamento→fallback), 6 endpoints `/api/cambio/*`, integração em `portfolio_service` — 234 passed |
| EXITUS-ENUM-001 | 4 | ✅ Concluído | 04/03/2026 | 12 ENUMs normalizados para lowercase, `values_callable` em 10 models, padrão documentado — 64 passed |
| EXITUS-UNITS-001 | 4 | ✅ Concluído | 04/03/2026 | `TipoAtivo.UNIT` (15º tipo), `DESMEMBRAMENTO` evento, schema + migration — 8 testes |
| EXITUS-SWAGGER-001 | 4 | ✅ Concluído | 04/03/2026 | Swagger UI `/api/docs`, spec JSON `/api/swagger.json`, 5 namespaces (auth, ativos, transacoes, ir, export) — flask-restx 1.3 |
| EXITUS-ANOMALY-001 | 4 | ✅ Concluído | 04/03/2026 | `AnomalyService` + `GET /api/cotacoes/anomalias` + detecção inline — 17 testes |
| EXITUS-RFCALC-001 | 4 | ✅ Concluído | 04/03/2026 | Duration Macaulay/Modificada, YTM (Newton-Raphson), FFO, AFFO, P/FFO — migration + 24 testes |
| EXITUS-NEWAPIS-001 | 4 | ✅ Concluído | 04/03/2026 | CRUD completo para `parametros_macro` e `fonte_dados` — 8 endpoints cada |
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
