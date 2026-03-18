# Documentação do Sistema Exitus

> **Total:** 18 arquivos ativos + archive  
> **Última atualização:** 18/03/2026  
> **Versão:** v0.9.1

---

## 🎯 Visão de Negócio

**Exitus** é uma plataforma multi-usuário de gestão e análise de investimentos para investidores individuais e assessoras que operam em múltiplos mercados e classes de ativos.

**Diferenciais:** Consolidação multi-mercado (BR/US/INTL), 15 tipos de ativos, análise fundamentalista avançada (Buy Score, Preço Teto, Z-Score), cotações near real-time, motor fiscal completo (IR/IOF/DARF), multi-moeda nativo.

**Mercados:** 🇧🇷 Brasil (Ações, FIIs, CDB, LCI/LCA, Tesouro, Debêntures) | 🇺🇸 EUA (Stocks, REITs, Bonds, ETFs) | 🌍 Internacional (Stocks, ETFs) | 🔷 Cripto

**Stack:** Python/Flask + PostgreSQL 16 + HTMX/Alpine.js/Tailwind CSS | 3 containers Podman rootless

**Status:** Ver [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## 📁 Documentação (18 arquivos)

### 🔴 Core Operacional

| Arquivo | Descrição |
|---------|-----------|
| **[ROADMAP.md](ROADMAP.md)** | Roadmap consolidado — backend, frontend, testes, pendências |
| **[CHANGELOG.md](CHANGELOG.md)** | Histórico completo de mudanças |
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Status consolidado do projeto |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Decisões arquiteturais, stack, containers |
| **[CODING_STANDARDS.md](CODING_STANDARDS.md)** | Padrões obrigatórios (snake_case, SQLAlchemy) |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Contratos da API, endpoints |
| **[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)** | Scripts, troubleshooting, procedimentos |
| **[PERSONAS.md](PERSONAS.md)** | Manual da IA, comportamento esperado |
| **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** | Erros reais, lições aprendidas |

### 🟡 Referência Técnica

| Arquivo | Descrição |
|---------|-----------|
| **[ENUMS.md](ENUMS.md)** | 15 TipoAtivo, mapeamentos DB/API/JSON |
| **[SEEDS.md](SEEDS.md)** | Credenciais dev, dados de teste |
| **[MODULES.md](MODULES.md)** | Status M0-M7, 17 blueprints, 23 tabelas |
| **[EXITUS_DB_STRUCTURE.txt](EXITUS_DB_STRUCTURE.txt)** | Schema completo (auto-gerado) |
| **[EXITUS_ER_DIAGRAM.md](EXITUS_ER_DIAGRAM.md)** | Diagramas ER |

### 📋 GAPs e Funcionalidades

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| **[MULTICLIENTE.md](MULTICLIENTE.md)** | Multi-tenancy consolidado (4 partes) | 🟡 85% |
| **[EXITUS-CRUD-002.md](EXITUS-CRUD-002.md)** | Revisão Service/Route | ❌ Pendente |

### 📖 Guias

| Arquivo | Descrição |
|---------|-----------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | Guia do usuário final |

### 📚 Archive (`docs/archive/`)

28 documentos históricos preservados: GAPs concluídos, roadmaps anteriores, análises de frontend, planos de teste. Acessíveis para consulta mas não fazem parte da documentação ativa.

---

## 🔄 Como Usar Esta Documentação

### Para Desenvolvedores
1. **CODING_STANDARDS.md** — Padrões obrigatórios
2. **API_REFERENCE.md** — Contratos dos endpoints
3. **ARCHITECTURE.md** — Decisões arquiteturais
4. **ROADMAP.md** — O que falta implementar
5. **CHANGELOG.md** — O que mudou recentemente

### Para Operações/DevOps
1. **OPERATIONS_RUNBOOK.md** — Comandos e troubleshooting
2. **SEEDS.md** — Credenciais e dados de teste
3. **MODULES.md** — Status de cada módulo

### Para Usuários Finais
1. **USER_GUIDE.md** — Como usar o sistema

### Para IA Assistente (Cascade/Windsurf)
1. **LESSONS_LEARNED.md** — **Ler PRIMEIRO**
2. **PERSONAS.md** — Manual de operação
3. **CODING_STANDARDS.md** — Padrões (CRÍTICO)
4. **API_REFERENCE.md** — Contratos
5. **ENUMS.md** — Valores válidos
6. **ROADMAP.md** — Status dos GAPs
7. **PROJECT_STATUS.md** — Métricas e testes

**Regras operacionais:** `.windsurfrules` na raiz do projeto

**🚨 REGRA CRÍTICA:** A IA **NUNCA** executa mudanças sem aprovação explícita.  
Fluxo: Análise → Modelo IA → Estratégia → "APROVADO" → Implementação → Testes → Docs → Commit

---

## 🧪 Testes

| Tipo | Local | Quantidade | Status |
|------|-------|------------|--------|
| **Backend (pytest)** | `backend/tests/` | 491 | ✅ 100% |
| **E2E (Playwright)** | `tests/e2e/specs/` | 108 | ✅ 96% passando |
| **Validação (shell)** | `tests/` | 6 scripts | ✅ Ativos |

---

*Atualizado: 18 de Março de 2026*  
*Versão: 5.0 — Documentação consolidada (42 → 18 arquivos)*
