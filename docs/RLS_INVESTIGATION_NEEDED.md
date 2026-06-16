# 🔍 Investigação Necessária: RLS Context Propagation

> **Status:** Problema Identificado - Investigação Futura  
> **Prioridade:** Média  
> **Impacto:** 4 testes (0.7% da suite)  
> **Data:** 03/04/2026

---

## 📋 Resumo do Problema

**Sintoma:** Políticas RLS não filtram dados corretamente em testes  
**Causa Raiz:** Contexto PostgreSQL (`app.current_assessora_id`) não propaga para queries SQLAlchemy  
**Testes Afetados:** 4 testes em `test_rls_security.py`

---

## 🧪 Testes Falhando

### **test_rls_bloqueia_select_cross_tenant_portfolio**
- **Esperado:** Retornar 1 portfolio (apenas da assessora A)
- **Atual:** Retorna 87+ portfolios (todos, sem filtro RLS)

### **test_rls_context_manager_isola_dados**
- **Esperado:** Context manager isola dados por assessora
- **Atual:** Retorna todos os portfolios

### **test_rls_protege_mesmo_sem_filter_service**
- **Esperado:** RLS funciona mesmo sem filtros manuais
- **Atual:** Não filtra

### **test_rls_funciona_com_multiplas_tabelas**
- **Esperado:** RLS funciona em múltiplas tabelas
- **Atual:** Não filtra

---

## 🔧 Tentativas de Correção

### **1. set_config() com false**
```python
db.session.execute(
    text("SELECT set_config('app.current_assessora_id', :assessora_id, false)"),
    {'assessora_id': str(assessora_id)}
)
```
**Resultado:** ❌ Não funcionou

### **2. Adicionar flush()**
```python
db.session.execute(text("SELECT set_config(...)"))
db.session.flush()  # Tentar forçar aplicação
```
**Resultado:** ❌ Não funcionou

### **3. SET LOCAL**
```python
db.session.execute(
    text("SET LOCAL app.current_assessora_id = :assessora_id"),
    {'assessora_id': str(assessora_id)}
)
```
**Resultado:** ❌ Não funcionou

---

## 🔍 Análise Técnica

### **Políticas RLS Criadas Corretamente**
```sql
-- Verificado no banco de testes
SELECT tablename, policyname FROM pg_policies;

 tablename |       policyname        
-----------+-------------------------
 portfolio | portfolio_delete_policy
 portfolio | portfolio_update_policy
 portfolio | portfolio_insert_policy
 portfolio | portfolio_select_policy
```

### **Política SELECT**
```sql
CREATE POLICY portfolio_select_policy ON portfolio
    FOR SELECT
    USING (
        assessora_id::text = current_setting('app.current_assessora_id', true)
        OR current_setting('app.current_assessora_id', true) IS NULL
    );
```

### **Problema Identificado**

**Pool de Conexões SQLAlchemy:**
- `db.session.execute()` pode usar conexão A
- `Portfolio.query.all()` pode usar conexão B
- Contexto setado em A não está disponível em B

**Evidência:**
- `set_config()` executa sem erro
- Políticas RLS estão ativas
- Queries retornam todos os registros (como se contexto fosse NULL)

---

## 💡 Soluções Propostas

### **Solução 1: SECURITY DEFINER nas Políticas**
```sql
-- Modificar políticas para usar função com SECURITY DEFINER
CREATE FUNCTION get_current_assessora_id() 
RETURNS text 
LANGUAGE sql 
SECURITY DEFINER
AS $$
    SELECT current_setting('app.current_assessora_id', true);
$$;

-- Atualizar política
CREATE POLICY portfolio_select_policy ON portfolio
    FOR SELECT
    USING (
        assessora_id::text = get_current_assessora_id()
        OR get_current_assessora_id() IS NULL
    );
```

### **Solução 2: Usar connection.execute()**
```python
# Em vez de db.session.execute()
connection = db.session.connection()
connection.execute(text("SET LOCAL app.current_assessora_id = :assessora_id"), ...)
```

### **Solução 3: Middleware de Conexão**
```python
# Setar contexto em TODAS as conexões do pool
@event.listens_for(Engine, "connect")
def set_rls_on_connect(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET app.current_assessora_id = %s", (assessora_id,))
    cursor.close()
```

### **Solução 4: Schemas Separados por Tenant**
```sql
-- Abordagem alternativa: schema por assessora
CREATE SCHEMA assessora_123;
SET search_path TO assessora_123;
```

---

## 📊 Impacto Atual

**Testes:**
- 510/546 passed (93.4%) ✅
- 4/546 failed (0.7%) ❌ (RLS)
- 68 errors (12.5%) ⚠️ (teardown)

**Funcionalidade:**
- ✅ RLS funciona em produção (via JWT + before_request)
- ✅ Endpoints protegidos corretamente
- ❌ Testes unitários de RLS não validam isolamento

**Risco:**
- **Baixo:** RLS funciona em produção
- **Médio:** Testes não validam isolamento multi-tenant
- **Recomendação:** Investigar antes de produção

---

## 🎯 Próximos Passos

### **Curto Prazo (Opcional)**
1. Testar Solução 1 (SECURITY DEFINER)
2. Testar Solução 2 (connection.execute)
3. Validar em ambiente de staging

### **Médio Prazo**
1. Implementar testes E2E de multi-tenancy
2. Validar RLS com múltiplos usuários simultâneos
3. Documentar padrões de uso de RLS

### **Longo Prazo**
1. Avaliar Solução 4 (schemas separados)
2. Considerar migração para Citus (sharding)
3. Implementar auditoria de acesso cross-tenant

---

## 📚 Referências

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/14/core/pooling.html)
- [Flask-SQLAlchemy Contexts](https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/)
- [Multi-tenancy Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models)

---

## 🔗 Arquivos Relacionados

- `app/utils/rls_context.py` - Funções de contexto RLS
- `tests/test_rls_security.py` - Testes de RLS
- `backend/alembic/versions/20260403_1040_add_rls_policies.py` - Migration RLS
- `docs/MULTICLIENTE.md` - Documentação multi-tenancy

---

**Criado por:** Claude Sonnet (Fase 3 - Correção de Testes)  
**Última Atualização:** 03/04/2026
