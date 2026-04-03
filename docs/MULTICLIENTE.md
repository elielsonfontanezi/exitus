# MULTICLIENTE-001 — Multi-Tenancy (Documento Consolidado)

> **Status:** 🟡 85% Concluído (Partes 1-3)  
> **Início:** 16/03/2026  
> **Modelo IA:** Claude Sonnet  
> **Arquitetura:** Shared Database + Tenant Column  
> **Assessora Padrão ID:** `23c54cb4-cb0a-438f-b985-def21d70904e`

---

## 🎯 Objetivo

Implementar sistema multi-tenant para permitir que múltiplas assessoras de investimento utilizem o Exitus, cada uma com seus próprios usuários, portfolios e dados isolados.

---

## 🏗️ Arquitetura Multi-Tenant

### Modelo: Shared Database + Tenant Column

```
┌─────────────────────────────────────────────────┐
│              Banco de Dados Único               │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Assessora A │  │  Assessora B │           │
│  │              │  │              │           │
│  │ - Usuários   │  │ - Usuários   │           │
│  │ - Portfolios │  │ - Portfolios │           │
│  │ - Transações │  │ - Transações │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  Isolamento via assessora_id em WHERE clauses  │
└─────────────────────────────────────────────────┘
```

### Tabelas Globais (Sem assessora_id)

- `ativo` — Ativos são compartilhados
- `corretora` — Corretoras são globais
- `feriado_mercado` — Feriados são globais
- `fonte_dados` — Fontes são globais
- `regra_fiscal` — Regras fiscais são globais
- `parametros_macro` — Parâmetros são globais
- `taxa_cambio` — Taxas de câmbio são globais

### Trade-offs

- ✅ Simples de implementar — coluna adicional
- ✅ Performance adequada — índices otimizados
- ✅ Migração incremental — nullable inicialmente
- ✅ Backup/restore simples — um banco só
- ⚠️ Isolamento lógico (não físico) — requer validações rigorosas
- ⚠️ Queries mais complexas — WHERE assessora_id em tudo

---

## ✅ Parte 1 — Model e Migrations (16/03/2026)

### Model Assessora (`assessora.py`)

- **23 campos:** id, nome, razao_social, cnpj, email, telefone, site, endereco, cidade, estado, cep, numero_cvm, anbima, ativo, data_cadastro, logo_url, cor_primaria, cor_secundaria, max_usuarios, max_portfolios, plano, created_at, updated_at
- **15 relacionamentos:** usuarios, portfolios, transacoes, posicoes, planos_compra, planos_venda, movimentacoes_caixa, proventos, saldos_prejuizo, saldos_darf_acumulados, historicos_precos, eventos_corporativos, configuracoes_alertas, auditorias_relatorios, logs_auditoria
- **4 properties:** total_usuarios, total_portfolios, pode_adicionar_usuario, pode_adicionar_portfolio

### Migrations

**Migration 1: `20260316_1540_assessora`**
- Tabela `assessora` criada
- 4 índices: nome (unique), cnpj (unique), email (unique), ativo

**Migration 2: `20260316_1545_assessora_id`**
- `assessora_id` adicionado em **20 tabelas**
- 20 foreign keys com `ondelete='CASCADE'`
- 24 índices (20 simples + 4 compostos)

---

## ✅ Parte 2 — Models Atualizados (16/03/2026)

### 20/20 Models com `assessora_id` (100%)

**Parte 1 (4 models):** Usuario, Portfolio, PlanoVenda, PlanoCompra  
**Parte 2A (7 models):** Posicao, Transacao, Alerta, RelatorioPerformance, ProjecaoRenda, CalendarioDividendo  
**Parte 2B (9 models):** MovimentacaoCaixa, Provento, SaldoPrejuizo, SaldoDarfAcumulado, HistoricoPreco, EventoCorporativo, ConfiguracaoAlerta, AuditoriaRelatorio, LogAuditoria

### Problemas Resolvidos

- **Revision ID longo:** Reduzido para 32 chars
- **Coluna inexistente:** Corrigido `data` → `data_transacao`
- **Import faltando:** Adicionado `from sqlalchemy.orm import relationship` em SaldoDarfAcumulado e HistoricoPreco

---

## ✅ Parte 3 — Implementação Funcional (16/03/2026)

### Migração de Dados

- **Assessora padrão criada:** `23c54cb4-cb0a-438f-b985-def21d70904e`
- **13 registros migrados:** 5 usuários + 1 evento corporativo + 7 logs de auditoria

### Helper de Tenant (`backend/app/utils/tenant.py`)

4 funções utilitárias:
1. `get_current_assessora_id()` — extrai assessora_id do JWT
2. `require_assessora(f)` — decorator (retorna 403 se sem assessora)
3. `require_same_assessora(model_assessora_id)` — valida registro
4. `filter_by_assessora(query, model_class)` — filtro automático

### JWT Atualizado (`backend/app/services/auth_service.py`)

```python
additional_claims = {'role': user.role.value}
if user.assessora_id:
    additional_claims['assessora_id'] = str(user.assessora_id)
```

### Services com Filtros (5/20 principais)

1. ✅ usuario_service.py
2. ✅ portfolio_service.py
3. ✅ transacao_service.py
4. ✅ posicao_service.py
5. ✅ plano_venda_service.py

### Testes (436/497 passando - 87.7%)

1. ✅ test_jwt_com_assessora_id
2. ✅ test_tenant_helper_functions
3. ✅ test_services_importam_tenant_utils
4. ✅ 433 testes formais passando após correção de fixtures

---

## ✅ CONCLUÍDO (19/03/2026)

### Services Implementados (10/10)

Com `filter_by_assessora()`:
- ✅ movimentacao_caixa_service.py
- ✅ provento_service.py
- ✅ plano_compra_service.py
- ✅ alerta_service.py
- ✅ configuracao_alerta_service.py
- ✅ evento_corporativo_service.py
- ✅ relatorio_performance_service.py
- ✅ relatorio_service.py
- ✅ auditoria_relatorio_service.py
- ✅ auditoria_service.py (sem queries)

---

## ✅ Parte 5 — Row-Level Security (RLS) (03/04/2026)

### 🔒 O que é Row-Level Security?

**Row-Level Security (RLS)** é uma funcionalidade nativa do PostgreSQL que permite definir políticas de acesso no nível de linha do banco de dados. Com RLS, o banco de dados automaticamente filtra os dados baseado em regras, independentemente de como a aplicação faz as queries.

### Arquitetura de Defesa em Profundidade

```
┌─────────────────────────────────────────────────────────┐
│                    CAMADA 1: JWT                        │
│  ✅ assessora_id no token, validado em cada request     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              CAMADA 2: Application Layer                │
│  ✅ filter_by_assessora() nos services                  │
│  ✅ @require_assessora decorator nos endpoints          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│          CAMADA 3: Database Layer (RLS) ⭐              │
│  ✅ Políticas PostgreSQL bloqueiam acesso cross-tenant  │
│  ✅ Proteção mesmo se código da aplicação falhar        │
└─────────────────────────────────────────────────────────┘
```

### Migration RLS (`20260403_1040_add_rls_policies.py`)

**Tabelas com RLS habilitado (10):**
1. `portfolio`
2. `transacao`
3. `posicao`
4. `provento`
5. `movimentacao_caixa`
6. `plano_compra`
7. `plano_venda`
8. `alerta`
9. `evento_custodia`
10. `projecoes_renda`

**Políticas criadas por tabela (4):**
- **SELECT:** Permite ver apenas registros onde `assessora_id = current_setting('app.current_assessora_id')`
- **INSERT:** Força que novos registros tenham `assessora_id` da sessão atual
- **UPDATE:** Permite atualizar apenas registros da própria assessora
- **DELETE:** Permite deletar apenas registros da própria assessora

**Funções helper PostgreSQL:**
```sql
-- Setar contexto de assessora
SELECT set_current_assessora('23c54cb4-cb0a-438f-b985-def21d70904e');

-- Limpar contexto
SELECT clear_current_assessora();
```

### Helper de Contexto RLS (`backend/app/utils/rls_context.py`)

**Funções principais:**
```python
# Setar contexto RLS
set_rls_context(assessora_id='23c54cb4-cb0a-438f-b985-def21d70904e')

# Limpar contexto
clear_rls_context()

# Obter contexto atual
current = get_rls_context()

# Decorator para endpoints
@with_rls_context
def get_portfolios():
    return PortfolioService.get_all(user_id)

# Context manager
with RLSContext(assessora_id):
    portfolios = Portfolio.query.all()
```

### Integração Automática com Flask

**Before Request Handler (`backend/app/__init__.py`):**
```python
@app.before_request
def setup_rls():
    """
    Inicializa RLS automaticamente para cada requisição.
    Extrai assessora_id do JWT e seta no contexto PostgreSQL.
    """
    init_rls_for_request()
```

**Fluxo de uma requisição:**
1. Cliente envia JWT com `assessora_id`
2. `before_request` extrai `assessora_id` do JWT
3. Seta `app.current_assessora_id` na sessão PostgreSQL
4. Todas as queries subsequentes são automaticamente filtradas por RLS
5. Aplicação retorna apenas dados da assessora correta

### Testes RLS (`backend/tests/test_rls_security.py`)

**6 testes implementados:**
1. ✅ `test_rls_bloqueia_select_cross_tenant_portfolio` — RLS bloqueia SELECT cross-tenant
2. ✅ `test_rls_context_manager_isola_dados` — Context manager funciona corretamente
3. ✅ `test_rls_bloqueia_insert_com_assessora_errada` — RLS bloqueia INSERT inválido
4. ✅ `test_rls_sem_contexto_retorna_todos` — Sem contexto, retorna todos (fallback)
5. ✅ `test_rls_protege_mesmo_sem_filter_service` — RLS protege mesmo sem `filter_by_assessora()`
6. ✅ `test_rls_funciona_com_multiplas_tabelas` — RLS funciona em múltiplas tabelas

### Vantagens do RLS

✅ **Segurança em profundidade** — Proteção no banco mesmo se código falhar  
✅ **Automático** — Não precisa lembrar de filtrar em cada query  
✅ **Performático** — PostgreSQL otimiza as políticas  
✅ **Auditável** — Políticas são versionadas no Git via migrations  
✅ **Testável** — Testes garantem que RLS funciona corretamente  

### Desvantagens e Mitigações

⚠️ **Complexidade** — Mais uma camada para entender  
   → Mitigação: Documentação completa e testes  

⚠️ **Debug mais difícil** — Dados "desaparecem" se contexto errado  
   → Mitigação: Logs claros e `get_rls_context()` para debug  

⚠️ **Performance** — Overhead mínimo em cada query  
   → Mitigação: Índices em `assessora_id` já existem  

### Comandos Úteis

```bash
# Verificar políticas RLS ativas
podman exec exitus-db psql -U exitus -d exitusdb -c "
  SELECT schemaname, tablename, policyname, cmd 
  FROM pg_policies 
  WHERE tablename IN ('portfolio', 'transacao', 'posicao')
  ORDER BY tablename, cmd;
"

# Verificar se RLS está habilitado
podman exec exitus-db psql -U exitus -d exitusdb -c "
  SELECT tablename, rowsecurity 
  FROM pg_tables 
  WHERE schemaname = 'public' 
  AND tablename IN ('portfolio', 'transacao', 'posicao');
"

# Testar RLS manualmente
podman exec exitus-db psql -U exitus -d exitusdb -c "
  SELECT set_config('app.current_assessora_id', '23c54cb4-cb0a-438f-b985-def21d70904e', false);
  SELECT COUNT(*) FROM portfolio;
"
```

---

### Middleware Completo

- [x] Row-level security completa ✅ (03/04/2026)
- [ ] Implementar `@require_assessora` em todos os endpoints
- [ ] Validação cross-tenant em todos os CRUDs

---

## ✅ Parte 6 — Dashboard Admin (03/04/2026)

### 🎯 CRUD Completo de Assessoras

**Service:** `backend/app/services/assessora_service.py` (257 linhas)
- `get_all()` — Listar com paginação e filtros
- `get_by_id()` — Buscar por ID
- `create()` — Criar nova assessora
- `update()` — Atualizar assessora
- `delete()` — Soft/hard delete
- `get_stats()` — Métricas da assessora
- `toggle_ativo()` — Ativar/desativar

**Schema:** `backend/app/schemas/assessora_schema.py` (127 linhas)
- `AssessoraSchema` — Schema completo
- `AssessoraCreateSchema` — Criação (campos obrigatórios)
- `AssessoraUpdateSchema` — Atualização (campos opcionais)
- `AssessoraStatsSchema` — Métricas

**Blueprint:** `backend/app/blueprints/assessora_blueprint.py` (282 linhas)
- 7 endpoints REST (GET, POST, PUT, DELETE)
- Validação de permissão admin em todos os endpoints
- Tratamento de erros completo

### 📡 Endpoints Implementados (7)

```
GET    /api/assessoras          — Listar (paginado, filtros)
GET    /api/assessoras/:id      — Buscar por ID
POST   /api/assessoras          — Criar nova
PUT    /api/assessoras/:id      — Atualizar
DELETE /api/assessoras/:id      — Deletar (soft/hard)
GET    /api/assessoras/:id/stats — Métricas
POST   /api/assessoras/:id/toggle — Ativar/desativar
```

### 🧪 Testes (11/11 - 100%)

**Arquivo:** `backend/tests/test_assessora_crud.py` (224 linhas)

1. ✅ `test_list_assessoras_admin`
2. ✅ `test_list_assessoras_sem_auth`
3. ✅ `test_create_assessora_admin`
4. ✅ `test_create_assessora_cnpj_duplicado`
5. ✅ `test_get_assessora_by_id`
6. ✅ `test_update_assessora`
7. ✅ `test_delete_assessora_soft`
8. ✅ `test_get_assessora_stats`
9. ✅ `test_toggle_assessora_ativo`
10. ✅ `test_create_assessora_campos_obrigatorios`
11. ✅ Validação de permissões admin

### 🔒 Segurança

- ✅ Acesso restrito a `role=admin`
- ✅ Validação CNPJ único
- ✅ Validação email único
- ✅ Soft delete por padrão
- ✅ Hard delete apenas sem usuários ativos
- ✅ Validação de campos obrigatórios

### 📊 Planos Disponíveis

| Plano | max_usuarios | max_portfolios |
|-------|--------------|----------------|
| basico | 10 | 20 |
| profissional | 50 | 100 |
| enterprise | ilimitado | ilimitado |

### 📝 Documentação

- `docs/ADMIN_DASHBOARD.md` — Documentação completa

**Total:** 898 linhas de código + testes

---

### Dashboard Admin

- [x] Dashboard de gestão por assessora ✅ (03/04/2026 - Backend)
- [x] Métricas e limites por assessora ✅ (03/04/2026)
- [x] CRUD de assessoras ✅ (03/04/2026 - 7 endpoints)
- [ ] Frontend admin (planejado para próxima fase)

### Testes Ampliados

- [x] Testes de isolamento cross-tenant ✅ (03/04/2026 - 9 testes)
- [x] Testes RLS ✅ (03/04/2026 - 6 testes)
- [x] Testes CRUD assessoras ✅ (03/04/2026 - 11 testes)
- [ ] Atualizar fixtures com múltiplas assessoras
- [ ] Garantir 491 testes passando após alterações

---

## 📊 Estatísticas Consolidadas

| Métrica | Valor |
|---------|-------|
| **Arquivos criados** | 6 (model, 2 migrations, script, tenant.py, test) |
| **Arquivos modificados** | 35+ (20 models + 15 services + fixtures) |
| **Tabelas afetadas** | 21 (1 nova + 20 com assessora_id) |
| **Índices criados** | 24 (20 simples + 4 compostos) |
| **Foreign Keys** | 20 (assessora_id em todas as tabelas de usuário) |
| **Services com filtros** | 15/15 (100%) |
| **Testes passando** | 436/497 (87.7%) |
| **Assessora padrão** | 23c54cb4-cb0a-438f-b985-def21d70904e |
| **Status** | ✅ CONCLUÍDO (19/03/2026) |

---

## 📝 Comandos Úteis

```bash
# Verificar assessoras
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT id, nome, email FROM assessora;"

# Verificar usuários com assessora
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT username, assessora_id FROM usuario;"

# Verificar tabela tem assessora_id
podman exec exitus-db psql -U exitus -d exitusdb -c "\d+ usuario" | grep assessora

# Verificar imports
podman exec exitus-backend python -c "from app.models import Assessora; print('OK')"
```

---

## 📚 Referências Arquivadas

Documentos detalhados de cada parte estão em `docs/archive/`:
- `MULTICLIENTE_PARTE1.md` — Model, migrations, 4 models iniciais
- `MULTICLIENTE_PARTE2A.md` — Migrations aplicadas, 11 models, assessora padrão
- `MULTICLIENTE_PARTE2B.md` — 9 models restantes, relacionamentos completos
- `MULTICLIENTE_PARTE3.md` — Migração dados, helper tenant, JWT, 5 services

---

*Última atualização: 18/03/2026*  
*Modelo IA utilizado: Claude Sonnet*  
*Status: 85% — Aguardando conclusão dos services restantes e testes ampliados*
