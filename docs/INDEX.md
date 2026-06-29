# Índice da Documentação — Sistema Exitus

> **Total:** 16 arquivos ativos + archive  
> **Última atualização:** 29/06/2026  
> **Versão:** v0.9.34

---

## 🎯 Visão de Negócio

**Exitus** é uma plataforma multi-usuário de gestão e análise de investimentos para investidores individuais e assessoras que operam em múltiplos mercados e classes de ativos.

**Diferenciais:** Consolidação multi-mercado (BR/US/INTL), 15 tipos de ativos, análise fundamentalista avançada (Buy Score, Preço Teto, Z-Score), cotações near real-time, motor fiscal completo (IR/IOF/DARF), multi-moeda nativo.

**Mercados:** 🇧🇷 Brasil (Ações, FIIs, CDB, LCI/LCA, Tesouro, Debêntures) | 🇺🇸 EUA (Stocks, REITs, Bonds, ETFs) | 🌍 Internacional (Stocks, ETFs) | 🔷 Cripto

**Stack:** Python/Flask + PostgreSQL 16 + HTMX/Alpine.js/Tailwind CSS | 3 containers Podman rootless

**Status:** Ver [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## 📁 Documentação (16 arquivos)

### 🔴 Core Operacional

| Arquivo | Descrição |
|---------|-----------|
| **[ROADMAP.md](ROADMAP.md)** | Roadmap consolidado — backend, frontend, testes, pendências |
| **[AUDITORIA_FUNCIONAL.md](AUDITORIA_FUNCIONAL.md)** | Auditoria de 36 telas — OK/PARCIAL/QUEBRADO, P-items |
| **[CHANGELOG.md](CHANGELOG.md)** | Histórico completo de mudanças |
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Status consolidado do projeto |
| **[MODULES.md](MODULES.md)** | Índice M0–M7 (métricas em PROJECT_STATUS) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Decisões arquiteturais, stack, containers |
| **[CODING_STANDARDS.md](CODING_STANDARDS.md)** | Padrões obrigatórios (snake_case, SQLAlchemy) |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Contratos da API, endpoints |
| **[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)** | Scripts, troubleshooting, procedimentos |
| **[PERSONAS.md](PERSONAS.md)** | Manual da IA, comportamento esperado |
| **[AI_OPERATIONS.md](AI_OPERATIONS.md)** | Plano de controle, modelos IA, MCPs, índice LESSONS |
| **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** | Erros reais, lições aprendidas |

### 🟡 Referência Técnica

| Arquivo | Descrição |
|---------|-----------|
| **[ENUMS.md](ENUMS.md)** | 15 TipoAtivo, mapeamentos DB/API/JSON |
| **[MULTICLIENTE.md](MULTICLIENTE.md)** | Multi-tenancy, RLS, isolamento assessora |
| **[SEEDS.md](SEEDS.md)** | Credenciais dev, dados de teste |
| **[EXITUS_DB_STRUCTURE.txt](EXITUS_DB_STRUCTURE.txt)** | Schema completo (auto-gerado) |

### 📚 Archive (`docs/archive/`)

32 documentos históricos preservados: GAPs concluídos, roadmaps anteriores, análises de frontend, planos de teste. Acessíveis para consulta mas não fazem parte da documentação ativa.

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
3. **PROJECT_STATUS.md** — Status consolidado, módulos M0-M7

### Para IA Assistente (Cursor Agent)
1. **LESSONS_LEARNED.md** — **Ler PRIMEIRO** (buscar L-* do domínio)
2. **ROADMAP.md** — Próximo GAP e dependências
3. **AUDITORIA_FUNCIONAL.md** — Status das telas (se frontend)
4. **PROJECT_STATUS.md** — Métricas e versão
5. **`.cursorrules`** + **AI_OPERATIONS.md** — Regras e procedimentos
6. **PERSONAS.md** — Comportamento esperado
7. **CODING_STANDARDS.md** — Padrões (CRÍTICO)

---

*Atualizado: 29 de Junho de 2026*  
*Versão: v0.9.34 — Documentação consolidada (16 arquivos)*
