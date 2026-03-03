# Roadmap de Implementação — Sistema Exitus

> **Versão:** 1.0  
> **Data:** 27 de Fevereiro de 2026  
> **Status:** Planejamento  
> **Branch:** `feature/revisao-negocio-vision`

---

## 📍 Onde Estamos (v0.7.10)

### ✅ Implementado e Funcional
- **67 endpoints** RESTful validados
- **21 tabelas** PostgreSQL com constraints robustas
- **Multi-tenant** por usuário (1:1)
- **Autenticação JWT** com 3 roles (ADMIN, USER, READONLY)
- **Relatórios básicos** com auditoria
- **Logs de auditoria** completos
- **Cotações em tempo real** com cache
- **Buy Signals** (readonly)
- **Alertas** configuráveis
- **Dashboards** interativos

### 📊 Métricas Atuais
- **56 ativos reais** no DB (33 BR, 16 US, 3 EU, 4 outros)
- **3 usuários seed** para testes
- **5 módulos PROD** (M0-M7.x)

---

## 🎯 GAPs Identificados

### 1. Funcionalidades Ausentes (Alta Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-SCRIPTS-001** | Otimização e unificação de scripts | ✅ Implementado | Crítico | Crítica |
| **EXITUS-RECOVERY-001** | Sistema de Restore/Recovery Robusto | ✅ Implementado | Crítico | Crítica |
| **EXITUS-IMPORT-001** | Importação/Exportação (CSV, Excel, JSON, PDF) | ✅ Implementado | Alto | Alta |
| **EXITUS-CRUD-001** | CRUD incompleto para entidades | ✅ Implementado | Alto | Alta |
| **EXITUS-BUSINESS-001** | Regras de negócio críticas | ✅ Implementado | Alto | Alta |
| **EXITUS-SEED-001** | Sistema de Seed/Reset Controlado | ✅ Implementado | Alto | Alta |
| **EXITUS-CASHFLOW-001** | Tratamento de "Transferência - Liquidação" B3 | ✅ Implementado | Médio | Média |
| **EXITUS-ASSETS-001** | Massa de Ativos Completa para Testes (dados ricos: preço, DY, P/L, ROE) | ✅ Implementado | Médio | Média |
| **EXITUS-SQLALCHEMY-001** | Padrões e Boas Práticas SQLAlchemy | ✅ Implementado | Alto | Alta |

### 2. Funcionalidades de Expansão (Média Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão | Apenas BRL | Médio | Média |
| **EXITUS-MULTICLIENTE-001** | Multi-cliente para assessoras | Não implementado | Médio-Alto | Média-Alta |
| **EXITUS-MONITOR-001** | Monitoramento/alertas em tempo real | Não implementado | Médio | Média |
| **EXITUS-NEWAPIS-001** | APIs de configuração | Não implementado | Médio | Média |
| **EXITUS-UNITS-001** | Tratamento de UNITS (B3) | Não implementado | Médio | Média |
| **EXITUS-SEED-001** | Sistema de Seed/Reset Controlado | ✅ Implementado | Alto | Alta |

### 3. Funcionalidades Opcionais (Baixa Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-CRIPTO-001** | Criptografia AES-256 | Não implementado | Baixo | Baixa |

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

### EXITUS-IMPORT-001: Importação/Exportação
**Problema:** Usuários não podem migrar dados ou exportar para análise externa

**APIs necessárias:**
```
POST /api/import/csv
POST /api/import/excel
POST /api/import/json
GET /api/export/{relatorio_id}/csv
GET /api/export/{relatorio_id}/excel
GET /api/export/{relatorio_id}/json
GET /api/export/{relatorio_id}/pdf
```

**Validações:**
- Estrutura de arquivo obrigatória
- Rollback automático em erro
- Limite de 10.000 linhas por importação

### EXITUS-CRUD-001: CRUD Incompleto
**Mapeamento real (atualizado 02/03/2026):**

**✅ CRUD Completo (6 entidades):**
- **Usuarios:** GET, POST, PUT, DELETE, PATCH password
- **Ativos:** GET, POST, PUT, DELETE + GET by ticker/mercado
- **Corretoras:** GET, POST, PUT, DELETE + GET saldo-total
- **Transações:** GET, POST, PUT, DELETE + GET resumo-ativo
- **Proventos:** GET, POST, PUT, DELETE ✅
- **Movimentações Caixa:** GET, POST, PUT, DELETE + saldo/extrato ✅

**❌ CRUD Incompleto (3 entidades):**
- **Eventos Corporativos:** Apenas GET list + POST aplicar → faltam GET id, POST create, PUT, DELETE
- **Feriados:** Mock data (lista estática) → migrar para banco (tabela feriado_mercado)
- **Regras Fiscais:** Mock data (lista estática) → migrar para banco (tabela regra_fiscal)

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

### EXITUS-SEED-001: Sistema de Seed/Reset Controlado
**Problema:** Não há forma de resetar o DB para estado conhecido de testes

**Impactos:**
- Testes inconsistentes com dados acumulados
- Dificuldade de debugar problemas
- Desenvolvimento lento sem reset rápido
- Impossível testar cenários específicos

**Solução proposta:**
```bash
# Script principal
python scripts/reset_and_seed.py [--clean] [--seed-type=full|minimal|custom]

# Backup/Restore de cenários
python scripts/backup_test_data.py --save|--restore scenario_name
```

**Tipos de seed:**
- **minimal:** Usuários, estrutura básica
- **full:** 56 ativos, transações, posições, relatórios
- **custom:** JSON com dados específicos

**Integração com testes:**
- Fixture pytest para reset automático
- Cenários padronizados para testes específicos

---

## 📅 Plano de Implementação Sugerido

### Fase 2.0: Scripts Críticos (Sprint 0 - Prioridade Máxima)
1. **Corrigir bugs críticos** (cleanup_duplicates, restore_complete)
2. **Unificar scripts restart** (único com parâmetros)
3. **Ajustar exitus.sh** para chamar scripts corrigidos
4. **Remover redundantes** após validação

### Fase 2.1: Fundamentos (Sprint 1)
1. **Completar CRUD** para entidades existentes
2. **Implementar regras de negócio** críticas
3. **Criar validações de horário/feriado**

### Fase 2.2: Importação/Exportação (Sprint 2)
1. **Implementar importação CSV/Excel**
2. **Implementar exportação múltiplos formatos**
3. **Validações e rollback**

### Fase 2.3: Expansão (Sprint 3)
1. **Multi-moeda** (se aprovado)
2. **Monitoramento básico**
3. **APIs de configuração**

### Fase 2.4: Opcionais (Sprint 4)
1. **Multi-cliente** (se aprovado)
2. **Criptografia** (se aprovado)

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

## 🔄 Status Atual

| GAP ID | Status | Data | Responsável | Observações |
|--------|--------|------|-------------|-------------|
| EXITUS-SCRIPTS-001 | 📋 Análise | 28/02/2026 | IA | 18 scripts analisados, bugs críticos |
| EXITUS-IMPORT-001 | 📋 Análise | 27/02/2026 | IA | Proposta enviada |
| EXITUS-CRUD-001 | 📋 Análise | 27/02/2026 | IA | Mapeado 5 entidades |
| EXITUS-BUSINESS-001 | 📋 Análise | 27/02/2026 | IA | 5 regras críticas |
| EXITUS-MULTIMOEDA-001 | 📋 Análise | 27/02/2026 | IA | Esperando decisão |
| EXITUS-MONITOR-001 | 📋 Análise | 27/02/2026 | IA | Prioridade média |
| EXITUS-NEWAPIS-001 | 📋 Análise | 27/02/2026 | IA | 3 APIs básicas |
| EXITUS-MULTICLIENTE-001 | 📋 Análise | 27/02/2026 | IA | Reclassificado Média-Alta |
| EXITUS-UNITS-001 | 📋 Análise | 27/02/2026 | IA | Adicionado roadmap |
| EXITUS-SEED-001 | ✅ Implementado | 02/03/2026 | IA | Sistema completo com backup/restore |
| EXITUS-CASHFLOW-001 | ✅ Implementado | 02/03/2026 | IA | Eventos de custódia D+2 |
| EXITUS-ASSETS-001 | ✅ Implementado | 02/03/2026 | IA | 56 ativos com dados fundamentalistas (DY, P/L, P/VP, ROE, beta, preco_teto, cap_rate) |
| EXITUS-SQLALCHEMY-001 | ✅ Implementado | 02/03/2026 | IA | app/utils/db_utils.py — 6 helpers, aplicado em 4 services |
| EXITUS-SCRIPTO-001 | 📋 Análise | 27/02/2026 | IA | Prioridade baixa |

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

---

## 🚀 Próximos Passos

1. **Aprovar priorização** dos GAPs
2. **Iniciar Fase 3** com GAP de prioridade crítica (EXITUS-SCRIPTS-001)
3. **Corrigir bugs críticos** imediatamente
4. **Unificar scripts** restart/start/stop

---

*Este arquivo é o controle central do roadmap. Atualizar após cada decisão/desenvolvimento.*
