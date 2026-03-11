# Documentação do Sistema Exitus

> **Total:** 26 arquivos organizados por contexto  
> **Última atualização:** 11/03/2026  
> **Versão:** v0.9.0

---

## 📁 Estrutura de Documentos por Contexto

### 🔴 **Core Operacional (8 arquivos)**
Documentação crítica para operação e desenvolvimento do sistema.

| Arquivo | Descrição | Prioridade |
|---------|-----------|------------|
| **[ROADMAP.md](ROADMAP.md)** | Visão estratégica, métricas atuais (491 testes), próximos GAPs | 🔴 Crítico |
| **[CHANGELOG.md](CHANGELOG.md)** | Histórico completo, auditoria, rastreabilidade | 🔴 Crítico |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Contratos da API, essencial para desenvolvimento | 🔴 Crítico |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Decisões arquiteturais, stack, containers | 🔴 Crítico |
| **[CODING_STANDARDS.md](CODING_STANDARDS.md)** | Padrões obrigatórios (snake_case, SQLAlchemy) | 🔴 Crítico |
| **[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)** | Scripts, troubleshooting, procedimentos | 🔴 Crítico |
| **[PERSONAS.md](PERSONAS.md)** | Manual da IA, comportamento esperado | 🔴 Crítico |
| **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** | Erros reais, lições valiosas (L-TEST-002 a L-TEST-005) | 🔴 Crítico |

### 🟡 **Referência Técnica (5 arquivos)**
Documentação de referência para desenvolvimento e troubleshooting.

| Arquivo | Descrição | Uso |
|---------|-----------|-----|
| **[ENUMS.md](ENUMS.md)** | 15 TipoAtivo, mapeamentos DB/API/JSON | 🟡 Alto |
| **[SEEDS.md](SEEDS.md)** | Credenciais dev, dados de teste | 🟡 Alto |
| **[MODULES.md](MODULES.md)** | Status M0-M7, 17 blueprints, 23 tabelas | � Alto |
| **[EXITUS_DB_STRUCTURE.txt](EXITUS_DB_STRUCTURE.txt)** | Schema completo gerado automaticamente | 🟡 Alto |
| **[EXITUS_ER_DIAGRAM.md](EXITUS_ER_DIAGRAM.md)** | Visualização do schema, diagramas ER | 🟢 Médio |

### 📋 **GAPs Ativos (7 arquivos)**
Documentação de features implementadas e padrões estabelecidos.

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| **[EXITUS-IR-001.md](EXITUS-IR-001.md)** | Motor IR consolidado (v2.0), fonte de verdade | ✅ Concluído |
| **[EXITUS-IMPORT-001.md](EXITUS-IMPORT-001.md)** | Design B3, parsers, validações | ✅ Concluído |
| **[EXITUS-EXPORT-001.md](EXITUS-EXPORT-001.md)** | Exportação genérica (CSV, Excel, JSON, PDF) | ✅ Concluído |
| **[EXITUS-CASHFLOW-001.md](EXITUS-CASHFLOW-001.md)** | Eventos de custódia, transferências | ✅ Concluído |
| **[EXITUS-ASSETS-001.md](EXITUS-ASSETS-001.md)** | Massa de dados, 56 ativos seed | ✅ Concluído |
| **[EXITUS-CRUD-002.md](EXITUS-CRUD-002.md)** | Padrões Service/Route | ✅ Concluído |
| **[EXITUS-SQLALCHEMY-001.md](EXITUS-SQLALCHEMY-001.md)** | Boas práticas SQLAlchemy | ✅ Concluído |

### 🆕 **GAPs Recentes (2 arquivos)**
Implementações mais recentes com histórico de decisões.

| Arquivo | Descrição | Data |
|---------|-----------|------|
| **[EXITUS-DIVCALENDAR-001.md](EXITUS-DIVCALENDAR-001.md)** | Calendário de dividendos | 10/03/2026 |
| **[EXITUS-BLUEPRINT-CONSOLIDATION-001.md](EXITUS-BLUEPRINT-CONSOLIDATION-001.md)** | Padrões de blueprints | 10/03/2026 |

### � **Guias e Visão (3 arquivos)**
Documentação para usuários e visão de negócio.

| Arquivo | Descrição | Público |
|---------|-----------|---------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | Guia do usuário final | Usuários |
| **[VISION.md](VISION.md)** | Visão de negócio, proposta de valor | Stakeholders |
| **[README.md](README.md)** | Este arquivo - índice da documentação | Todos |

### 📚 **Histórico (1 arquivo)**
Documentação de correções e lições aprendidas.

| Arquivo | Descrição | Valor |
|---------|-----------|-------|
| **[TESTES_HISTORICO.md](TESTES_HISTORICO.md)** | Histórico de correções de testes (491/491 ✅) | Referência |

---

## 🔄 Como Usar Esta Documentação

### Para Desenvolvedores/Manutenção
1. **PERSONAS.md** — Entender como interagir com a IA assistente
2. **CODING_STANDARDS.md** — Padrões de codificação e SQLAlchemy (OBRIGATÓRIO)
3. **EXITUS-SQLALCHEMY-001.md** — Padrões SQLAlchemy (evitar problemas recorrentes)
4. **API_REFERENCE.md** — Contratos dos endpoints
5. **ARCHITECTURE.md** — Decisões arquiteturais
6. **CHANGELOG.md** — O que mudou recentemente
7. **ROADMAP.md** — O que falta implementar e plano de desenvolvimento

### Para Operações/DevOps
1. **OPERATIONS_RUNBOOK.md** — Comandos e troubleshooting
2. **SEEDS.md** — Credenciais e dados de teste
3. **MODULES.md** — Status de cada módulo

### Para Usuários Finais
1. **USER_GUIDE.md** — Como usar o sistema
2. **VISION.md** — O que o sistema oferece

### Para IA Assistente (Cascade/Windsurf)
1. **LESSONS_LEARNED.md** — **Ler PRIMEIRO — erros reais, regras ativas**
2. **PERSONAS.md** — Manual de operação do Cascade
3. **CODING_STANDARDS.md** — Padrões SQLAlchemy (CRÍTICO para evitar erros)
4. **API_REFERENCE.md** — Contratos para validação
5. **ENUMS.md** — Valores válidos para campos
6. **ROADMAP.md** — Status dos GAPs para planejamento
7. **TESTES_HISTORICO.md** — Histórico de correções de testes

**Regras operacionais da IA:** `.windsurfrules` na raiz do projeto (lido automaticamente pelo Cascade)

**🚨 REGRA CRÍTICA:** A IA pode opinar e propor ideias, mas **NUNCA** deve executar mudanças sem aprovação explícita. Fluxo: 1) Propor → 2) Aguardar "APROVADO" → 3) Implementar

---

## 📈 Fluxo de Trabalho com IA

```
1. .windsurfrules define regras operacionais do Cascade (injetado automaticamente)
2. PERSONAS.md define comportamento, fontes de verdade e fluxo de trabalho
3. LESSONS_LEARNED.md é lido ANTES de qualquer ação
4. Cascade segue: ANÁLISE → MODELO IA → ESTRATÉGIA → APROVADO → IMPLEMENTAÇÃO → TESTES → DOCS → COMMIT
5. Problemas recorrentes? → Criar GAP + registrar em LESSONS_LEARNED.md
6. CHANGELOG.md registra todos os GAPs e correções
```

---

## 🚨 Importante

- **PERSONAS.md** é o manual de controle da IA — não altere sem entender o impacto
- **CODING_STANDARDS.md** é OBRIGATÓRIO para evitar erros SQLAlchemy
- **EXITUS-SQLALCHEMY-001.md** contém soluções para problemas recorrentes
- **API_REFERENCE.md** é sempre a fonte da verdade para contratos de API
- **CHANGELOG.md** mantém o histórico de todas as decisões técnicas
- **OPERATIONS_RUNBOOK.md** contém comandos que podem afetar o sistema em produção

---

## 🎯 **Regras de Ouro para Desenvolvimento**

1. **🔍 SEMPRE consultar** CODING_STANDARDS.md antes de implementar
2. **✅ SEMPRE validar** enums e constraints (EXITUS-SQLAlchemy-001)
3. **📝 SEMPRE documentar** problemas recorrentes como GAPs
4. **🔄 SEMPRE fazer** rollback após erros de session
5. **🚀 SEMPRE seguir** fluxo: Proposta → Aprovação → Implementação

---

*Atualizado: 11 de Março de 2026*  
*Versão: 4.0 — Documentação reorganizada por contexto (26 arquivos)*
