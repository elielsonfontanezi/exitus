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
| **EXITUS-IMPORT-001** | Importação/Exportação (CSV, Excel, JSON, PDF) | Apenas stub JSON | Alto | Alta |
| **EXITUS-CRUD-001** | CRUD incompleto para entidades | Faltam POST/PUT/DELETE | Alto | Alta |
| **EXITUS-BUSINESS-001** | Regras de negócio críticas | Não implementado | Alto | Alta |

### 2. Funcionalidades de Expansão (Média Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-MULTIMOEDA-001** | Multi-moeda com conversão | Apenas BRL | Médio | Média |
| **EXITUS-MULTICLIENTE-001** | Multi-cliente para assessoras | Não implementado | Médio-Alto | Média-Alta |
| **EXITUS-MONITOR-001** | Monitoramento/alertas em tempo real | Não implementado | Médio | Média |
| **EXITUS-NEWAPIS-001** | APIs de configuração | Não implementado | Médio | Média |

### 3. Funcionalidades Opcionais (Baixa Prioridade)

| GAP ID | Funcionalidade | Status Real | Impacto | Prioridade |
|--------|---------------|-------------|---------|------------|
| **EXITUS-CRIPTO-001** | Criptografia AES-256 | Não implementado | Baixo | Baixa |

---

## 🔍 Detalhamento dos GAPs

### EXITUS-IMPORT-001: Importação/Exportação
**Problema:** Usuários não podem migrar dados ou exportar para análise externa

**Abordagem aprovada:** Script padrão + APIs
```
# Script principal (recomendado)
python scripts/import_b3.py <movimentacoes.csv> <negociacoes.csv>

# APIs (opcionais, para integrações)
POST /api/import/b3/movimentacoes
POST /api/import/b3/negociacoes
```

**Foco:** Importação de arquivos CSV da B3 (movimentacao-*.csv, negociacao-*.csv)

**Validações:**
- Estrutura CSV da B3 obrigatória
- Rollback automático em erro
- Criação automática de ativos (API híbrida)
- Sobrescrever duplicatas

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

---

## 📅 Plano de Implementação Sugerido

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
| EXITUS-IMPORT-001 | 📋 Análise | 27/02/2026 | IA | Proposta enviada |
| EXITUS-CRUD-001 | 📋 Análise | 27/02/2026 | IA | Mapeado 5 entidades |
| EXITUS-BUSINESS-001 | 📋 Análise | 27/02/2026 | IA | 5 regras críticas |
| EXITUS-MULTIMOEDA-001 | 📋 Análise | 27/02/2026 | IA | Esperando decisão |
| EXITUS-MONITOR-001 | 📋 Análise | 27/02/2026 | IA | Prioridade média |
| EXITUS-NEWAPIS-001 | 📋 Análise | 27/02/2026 | IA | 3 APIs básicas |
| EXITUS-MULTICLIENTE-001 | 📋 Análise | 27/02/2026 | IA | Discussão necessária |
| EXITUS-CRIPTO-001 | 📋 Análise | 27/02/2026 | IA | Prioridade baixa |

---

## 📝 Histórico de Decisões

### 27/02/2026 - Análise GAPs
- **Fase 1 concluída:** Documentação reorganizada
- **Fase 2 iniciada:** Análise sistemática de GAPs
- **8 GAPs identificados** com priorização
- **Decisão:** Multi-cliente reclassificado para Média-Alta (potencial comercial)

---

## 🚀 Próximos Passos

1. **Aprovar priorização** dos GAPs
2. **Iniciar Fase 3** com primeiro GAP aprovado (sugerido: EXITUS-IMPORT-001)

---

*Este arquivo é o controle central do roadmap. Atualizar após cada decisão/desenvolvimento.*
