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
| **EXITUS-SCRIPTS-001** | Otimização e unificação de scripts | 18 scripts analisados | Crítico | Crítica |
| **EXITUS-RECOVERY-001** | Sistema de Restore/Recovery Robusto | Implementado | Crítico | Crítica |
| **EXITUS-IMPORT-001** | Importação/Exportação (CSV, Excel, JSON, PDF) | ✅ Implementado | Alto | Alta |
| **EXITUS-CRUD-001** | CRUD incompleto para entidades | Faltan POST/PUT/DELETE | Alto | Alta |
| **EXITUS-BUSINESS-001** | Regras de negócio críticas | Não implementado | Alto | Alta |
| **EXITUS-SEED-001** | Sistema de Seed/Reset Controlado | Não implementado | Alto | Alta |
| **EXITUS-CASHFLOW-001** | Tratamento de "Transferência - Liquidação" B3 | Não implementado | Médio | Média |
| **EXITUS-ASSETS-001** | Importação de Ativos Exemplo (Massa de Teste) | Não implementado | Médio | Média |

### 2. Funcionalidades de Expansão (Média Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão | Apenas BRL | Médio | Média |
| **EXITUS-MULTICLIENTE-001** | Multi-cliente para assessoras | Não implementado | Médio-Alto | Média-Alta |
| **EXITUS-MONITOR-001** | Monitoramento/alertas em tempo real | Não implementado | Médio | Média |
| **EXITUS-NEWAPIS-001** | APIs de configuração | Não implementado | Médio | Média |
| **EXITUS-UNITS-001** | Tratamento de UNITS (B3) | Não implementado | Médio | Média |
| **EXITUS-SEED-001** | Sistema de Seed/Reset Controlado | Não implementado | Alto | Alta |

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
**Entidades afetadas:**
- **Movimentações:** Apenas GET listagem
- **Buy Signals:** Apenas GET cálculos
- **Cotações:** Apenas GET consulta
- **Proventos:** Apenas GET listagem
- **Eventos Corporativos:** Apenas GET listagem

**Métodos faltando:** POST, PUT, DELETE para cada entidade

### EXITUS-BUSINESS-001: Regras de Negócio
**Regras críticas não implementadas:**
1. **Validação de horário de mercado** (B3: 10h-17h, NYSE: 9:30h-16h)
2. **Bloqueio de operações em feriados** (tabela existe mas não usada)
3. **Validação de saldo disponível** antes de transação
4. **Cálculo automático de taxas de corretagem**
5. **Limite de operações day-trade** (fiscal)

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
| EXITUS-SEED-001 | 📋 Análise | 28/02/2026 | IA | Design detalhado criado |
| EXITUS-CASHFLOW-001 | 📋 Análise | 02/03/2026 | IA | Identificado necessidade |
| EXITUS-ASSETS-001 | 📋 Análise | 02/03/2026 | IA | Adicionado ao roadmap |
| EXITUS-SCRIPTO-001 | 📋 Análise | 27/02/2026 | IA | Prioridade baixa |

---

## 📝 Histórico de Decisões

### 27/02/2026 - Análise GAPs
- **Fase 1 concluída:** Documentação reorganizada
- **Fase 2 iniciada:** Análise sistemática de GAPs
- **8 GAPs identificados** com priorização
- **Decisão:** Multi-cliente reclassificado para Média-Alta (potencial comercial)
- **Adicionado:** EXITUS-UNITS-001 para tratamento de UNITS B3

### 28/02/2026 - Discussão Adicional
- **Analisado:** Arquivos reais B3 (Excel) para importação
- **Adicionado:** EXITUS-SEED-001 para controle de seed/reset
- **Analisado:** 18 scripts existentes detalhadamente
- **Adicionado:** EXITUS-SCRIPTS-001 como prioridade crítica
- **Identificados:** 3 bugs críticos, 5 scripts redundantes
- **Total:** 11 GAPs identificados
- **Design criado:** Sistema completo de seed controlado

### 02/03/2026 - Implementação Importação B3
- **Implementado:** EXITUS-IMPORT-001 (100% completo) ✅
- **Corrigido:** Parsing de valores monetários (formato European)
- **Corrigido:** Parsing diferenciado (quantidade vs monetário)
- **Identificado:** "Transferência - Liquidação" como VENDA de ativo
- **Adicionado:** EXITUS-CASHFLOW-001 para tratamento futuro
- **Adicionado:** EXITUS-ASSETS-001 para massa de teste
- **Testado:** Importação real com arquivos B3 (valores corretos)
- **Implementado:** Opção --clean para base limpa
- **Implementado:** Help detalhado do script

---

## 🚀 Próximos Passos

1. **Aprovar priorização** dos GAPs
2. **Iniciar Fase 3** com GAP de prioridade crítica (EXITUS-SCRIPTS-001)
3. **Corrigir bugs críticos** imediatamente
4. **Unificar scripts** restart/start/stop

---

*Este arquivo é o controle central do roadmap. Atualizar após cada decisão/desenvolvimento.*
