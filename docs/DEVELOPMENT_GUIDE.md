# 🎯 DEVELOPMENT GUIDE — Sistema Exitus

> **Propósito:** Quick reference para contexto rápido.  
> **Fontes de verdade completas:** `docs/PROJECT_STATUS.md`, `docs/CODING_STANDARDS.md`, `docs/LESSONS_LEARNED.md`, `.windsurfrules`  
> **Atualizado:** 25/06/2026

---

## 🚀 Fase Atual: Auditoria Funcional & Telas (Finalização)
- **Objetivo:** Tornar o sistema 100% operacional conforme `AUDITORIA_FUNCIONAL_18_06_2026.md`
- **Próximo:** Estabilização antes de retomar `ROADMAP.md`
- **Status Suite:** 567/574 passed (98.8%) — ver `PROJECT_STATUS.md` para métricas atuais

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

## 🧪 Comandos de Validação Obrigatórios

```bash
# Suite completa (alvo: manter >95%)
podman exec exitus-backend python -m pytest --tb=no -q

# Multi-tenancy
podman exec exitus-backend python -m pytest backend/tests/test_multitenancy.py -v

# Constraints (DDL)
podman exec exitus-backend python -m pytest backend/tests/test_constraints.py -v
```

---

## 📚 Fontes de Verdade (Ler ANTES de qualquer ação)

**PRIORIDADE 1 (obrigatório):**
1. `docs/LESSONS_LEARNED.md` — erros reais para não repetir
2. `docs/PROJECT_STATUS.md` — status consolidado
3. `docs/PERSONAS.md` — comportamento da IA
4. `docs/CODING_STANDARDS.md` — padrões de código
5. `docs/ROADMAP.md` — roadmap de GAPs
6. `docs/CHANGELOG.md` — histórico de mudanças

**PRIORIDADE 2 (conforme contexto):**
- `docs/ENUMS.md` — mapeamento de enums
- `docs/AUDITORIA_FUNCIONAL_18_06_2026.md` — bugs pendentes
- `docs/ARCHITECTURE.md` — stack e convenções

---

## 🔗 Portas e URLs

- **Frontend:** http://localhost:8080
- **Backend:** http://localhost:5000
- **Database (host):** 127.0.0.1:5433
- **Database (container):** 5432

---

## 🗄️ Bancos de Dados

- **exitusdb:** produção — usa migrations Alembic
- **exitusdb_test:** testes — usa `db.create_all()` (não usa Alembic)

**Regra de paridade DDL:** Qualquer alteração de schema (constraints, colunas, enums) deve ser aplicada em ambos os bancos. Ver `LESSONS_LEARNED.md (L-DB-009)`.
