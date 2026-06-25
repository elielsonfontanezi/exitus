# 🎯 00_DEVELOPMENT_GUIDE — Sistema Exitus

> **Propósito:** Quick reference para contexto rápido de desenvolvimento.  
> **Regras completas para IA:** `.windsurfrules` — consultar sempre no início da sessão.  
> **Fontes de verdade:** `docs/PROJECT_STATUS.md`, `docs/CODING_STANDARDS.md`, `docs/LESSONS_LEARNED.md`  
> **Nota:** Este arquivo é um resumo. Para detalhes profundos, consultar as fontes de verdade acima.  
> **Atualizado:** 25/06/2026

---

## 🚀 Fase Atual: Auditoria Funcional & Telas (Finalização)
- **Objetivo:** Tornar o sistema 100% operacional conforme `AUDITORIA_FUNCIONAL.md`
- **Próximo:** Estabilização antes de retomar `ROADMAP.md`
- **Status Suite:** 567/574 passed (98.8%) — ver `PROJECT_STATUS.md` para métricas atuais

---

## 🌐 Princípios Fundamentais

- **Multi-Mercado:** Brasil, EUA, Europa, Ásia
- **Multi-Classe:** Ações, FIIs, REITs, Renda Fixa, Cripto
- **Multi-Corretora:** Abstração de caixa unificado
- **Dados Near Real-Time:** Cotações com delay até 15 min
- **Compliance por Design:** Regras fiscais configuráveis por jurisdição

---

## 🛠️ Regras Inegociáveis (Não Modificar Sem Permissão)

### 1. Multi-Tenancy (Shared Database)
- **Regra:** Todas as queries de service DEVEM usar `filter_by_assessora()`
- **Extração:** `assessora_id` vem do JWT via `get_current_assessora_id()`
- **RLS:** Ativo no PostgreSQL, mas contexto não propaga em testes unitários (pool SQLAlchemy)
- **Se mexer em banco:** Validar `tests/test_multitenancy.py` e ver `LESSONS_LEARNED.md (L-DB-009)`

### 2. Motor Fiscal (IR/IOF/DARF)
- **Status:** 100% funcional
- **Alíquota JCP:** 17.5% (atualização Jun/2026)
- **Não alterar:** `ir_service.py` sem rodar suite completa

### 3. Enums e Seeds
- **Movimentações Caixa:** Estritamente lowercase no JSON (`aporte`, `resgate`, `credito_provento`, `imposto`)
- **Não usar:** Enums legados uppercase (`DEPOSITO`, `SAQUE`)
- **Referência:** `docs/ENUMS.md` para mapeamento completo

---

## 🔄 Fluxo de Trabalho Padrão

### 1. Início de Sessão
```bash
# Verificar status dos containers
podman ps

# Ler fontes de verdade (PRIORIDADE 1)
# docs/LESSONS_LEARNED.md, docs/PROJECT_STATUS.md, docs/CODING_STANDARDS.md
```

### 2. Implementação
- Seguir padrões de `docs/CODING_STANDARDS.md` (snake_case, SQLAlchemy)
- Para alterações DDL (schema): criar migration Alembic
- Para bugs de aplicação: fix no código Python

### 3. Validação
```bash
# Suite completa
podman exec exitus-backend python -m pytest --tb=no -q

# Se mexeu em banco (DDL):
# - exitusdb: flask db upgrade
# - exitusdb_test: scripts/create_test_db.sh (ou ALTER TABLE direto)
# - Verificar paridade: scripts/check_db_parity.sh
```

### 4. Commit
```bash
git add -A
git commit -m "feat/fix/docs: [GAP-XXX] — descrição

GAPs: GAP-XXX
- Artefato A: descrição
- Artefato B: descrição
- docs: arquivos atualizados
- Suite: N passed, 0 failed"
```

### 5. Documentação (no mesmo commit)
- **Obrigatório:** CHANGELOG.md, PROJECT_STATUS.md
- **Se aplicável:** ROADMAP.md, LESSONS_LEARNED.md, ARCHITECTURE.md

---

## 🧪 Comandos de Validação Obrigatórios

### Sempre após qualquer alteração
```bash
# Suite completa (alvo: manter >95%, ideal próximo de 100%)
podman exec exitus-backend python -m pytest --tb=no -q
```

### Após alterações multi-tenancy / RLS
```bash
podman exec exitus-backend python -m pytest backend/tests/test_multitenancy.py -v
```

### Após alterações DDL (schema, migrations, constraints)
```bash
./scripts/check_db_parity.sh --strict
podman exec exitus-backend python -m pytest backend/tests/test_constraints.py -v
```

### Após alterações fiscais (IR / DARF)
```bash
podman exec exitus-backend python -m pytest backend/tests/test_darf_acumulado.py -v
podman exec exitus-backend python -m pytest backend/tests/test_ir_integration.py -v
```

### Após alterações de rentabilidade / importação
```bash
podman exec exitus-backend python -m pytest backend/tests/test_rentabilidade.py -v
podman exec exitus-backend python -m pytest backend/tests/test_import_b3_parsers.py -v
```

---

## 🌱 Comandos de Seed e Reset

> ⚠️ **Apenas para ambiente de desenvolvimento.**

```bash
# Reset completo do banco de testes (exitusdb_test + seed test_e2e + paridade)
./scripts/create_test_db.sh

# Seed específico via load_scenario.py
python backend/load_scenario.py test_full

# Seed específico via reset_and_seed.py (alternativa dentro do container)
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_full

# Verificar paridade de schema
./scripts/check_db_parity.sh --strict
```

**Cenários disponíveis:**
| Cenário | Descrição |
|---------|-----------|
| `test_full` | Cenário completo com histórico patrimonial (16 meses) |
| `test_e2e` | Dados realistas para testes E2E |
| `test_ir` | Dados específicos para testes de IR |
| `test_stress` | Cenário de carga/stress |

**Referência completa:** docs/SEEDS.md, docs/OPERATIONS_RUNBOOK.md

---

## �📚 Fontes de Verdade (Ler ANTES de qualquer ação)

**PRIORIDADE 1 (obrigatório):**
1. `docs/LESSONS_LEARNED.md` — erros reais para não repetir
2. `docs/PROJECT_STATUS.md` — status consolidado
3. `docs/PERSONAS.md` — comportamento da IA
4. `docs/CODING_STANDARDS.md` — padrões de código
5. `docs/ROADMAP.md` — roadmap de GAPs
6. `docs/CHANGELOG.md` — histórico de mudanças

**PRIORIDADE 2 (conforme contexto):**
- `docs/ENUMS.md` — mapeamento de enums
- `docs/AUDITORIA_FUNCIONAL.md` — bugs pendentes
- `docs/ARCHITECTURE.md` — stack e convenções

---

## 🔗 Portas e URLs

- **Frontend:** http://localhost:8080
- **Backend:** http://localhost:5000
- **Database (host):** 127.0.0.1:5433
- **Database (container):** 5432

---

## 🏗️ Stack Tecnológica

- **Backend:** Python 3.11 + Flask + SQLAlchemy
- **Database:** PostgreSQL 16
- **Frontend:** HTMX + Alpine.js + Tailwind CSS
- **Containers:** 3 containers Podman rootless (exitus-db, exitus-backend, exitus-frontend)
- **Network:** exitus-net (bridge customizada)

---

## 🔐 Credenciais de Acesso (Desenvolvimento)

| Username | Senha | Perfil |
|----------|-------|-------|
| e2e_admin | e2e_senha_123 | Administrador |
| e2e_user | e2e_senha_123 | Usuário |
| e2e_viewer | e2e_senha_123 | Visualizador |

**Referência completa:** docs/SEEDS.md

---

## 🗄️ Bancos de Dados

- **exitusdb:** produção — usa migrations Alembic
- **exitusdb_test:** testes — usa `db.create_all()` (não usa Alembic)

**Regra de paridade DDL:** Qualquer alteração de schema (constraints, colunas, enums) deve ser aplicada em ambos os bancos. Ver `LESSONS_LEARNED.md (L-DB-009)`.
