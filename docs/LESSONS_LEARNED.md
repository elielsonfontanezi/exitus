# Lições Aprendidas — Sistema Exitus

> **Propósito:** Regras ativas derivadas de erros reais em produção/desenvolvimento.  
> Consultado pela IA **antes de qualquer ação** para evitar repetição de erros.  
> **Atualizado:** 03/03/2026 — unificado de EXITUS-SEED-001 + EXITUS-TESTS-001  
> **Ver também:** `docs/CODING_STANDARDS.md`, `.codeium.rules`

---

## 🗄️ Banco de Dados

### L-DB-001 — Usar DELETE, nunca DROP, para reset de dados
**Origem:** EXITUS-SEED-001 | **Data:** 02/03/2026

```python
# ❌ ERRADO — perde schema, constraints, índices, migrations
db.drop_all()
db.create_all()

# ✅ CORRETO — limpa dados, preserva estrutura
db.session.execute(text("DELETE FROM tabela"))
```
**Regra:** "O que preciso resetar?" → Dados = DELETE. Schema = DROP (raramente).  
**PKs são UUID** neste sistema — não existem sequences para resetar.

---

### L-DB-002 — Nunca deduzir nomes de tabelas — sempre consultar
**Origem:** EXITUS-SEED-001 | **Data:** 02/03/2026

```python
# ❌ ERRADO — 'movimentacao' não existe; é 'movimentacao_caixa'
tables = ['movimentacao', 'transacao', ...]

# ✅ CORRETO — listar do banco
from sqlalchemy import inspect
print(sorted(inspect(db.engine).get_table_names()))
# ou: podman exec exitus-db psql -U exitus -d exitusdb -c "\dt"
```
**Tabelas reais (22):** `ativo`, `alertas`, `auditoria_relatorios`, `configuracoes_alertas`,
`corretora`, `evento_corporativo`, `evento_custodia`, `feriado_mercado`, `fonte_dados`,
`historico_preco`, `log_auditoria`, `movimentacao_caixa`, `parametros_macro`, `portfolio`,
`posicao`, `projecoes_renda`, `provento`, `regra_fiscal`, `relatorios_performance`,
`transacao`, `usuario`, `alembic_version`.

---

### L-DB-003 — PKs são UUID v4 — não existem sequences
**Origem:** EXITUS-SEED-001 | **Data:** 02/03/2026

Todos os models usam `id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`.  
Não há sequences no schema. `ALTER SEQUENCE ... RESTART` vai falhar.

---

### L-DB-004 — ENUMs PostgreSQL têm case inconsistente (bug de design conhecido)
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

| ENUM | No PostgreSQL | No Python (model) | Status |
|------|--------------|-------------------|--------|
| `tipotransacao` | lowercase | lowercase | ✅ ok |
| `tiporelatorio`, `tipoalerta` | lowercase | lowercase | ✅ ok |
| `tipoativo`, `tipoeventocorporativo` | **UPPERCASE** | lowercase | ⚠️ inconsistente |
| `userrole`, `tipoprovento`, `incidenciaimposto` | **UPPERCASE** | lowercase | ⚠️ inconsistente |

O ORM resolve a conversão automaticamente. Queries SQL diretas com `WHERE tipo = 'acao'`
**vão falhar** para ENUMs UPPERCASE — usar `WHERE tipo = 'ACAO'` nesse caso.  
**Fix planejado:** EXITUS-ENUM-001.

---

### L-DB-005 — Banco de teste deve ser criado via pg_dump, não via migrations
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

A cadeia de migrations Alembic **não consegue criar um banco do zero** de forma confiável
(inconsistências acumuladas de ENUM case, migrations quebradas, dependências circulares).

```bash
# ✅ Forma correta de criar/recriar exitusdb_test
podman exec exitus-db pg_dump -U exitus -d exitusdb --schema-only --no-owner --no-acl \
  | podman exec -i exitus-db psql -U exitus -d exitusdb_test
```

**Fix planejado:** Script automatizado EXITUS-TESTDB-001.

---

## 🔧 Alembic / Migrations

### L-MIG-001 — Toda migration criada manualmente precisa das 4 variáveis no corpo
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```python
# ❌ ERRADO — Alembic não lê do docstring
"""Revision ID: 9e4ef61dee5d ..."""

# ✅ CORRETO — variáveis obrigatórias no corpo do módulo
revision = '9e4ef61dee5d'
down_revision = '202602162130'  # ou None para a primeira
branch_labels = None
depends_on = None
```

---

### L-MIG-002 — ENUMs em migrations devem ser idempotentes
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```python
# ❌ ERRADO — falha com DuplicateObject se ENUM já existe
postgresql.ENUM('a', 'b', name='meuenum', create_type=True).create(op.get_bind())

# ✅ CORRETO — idempotente
op.execute("""
    DO $$ BEGIN
        CREATE TYPE meuenum AS ENUM ('a', 'b');
    EXCEPTION WHEN duplicate_object THEN NULL; END $$
""")
```

Ao referenciar o tipo na coluna, usar `create_type=False`:
```python
sa.Column('campo', postgresql.ENUM(name='meuenum', create_type=False))
```

---

## 🐍 SQLAlchemy + Flask

### L-SA-001 — Imports locais em funções impedem mocking em testes
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```python
# ❌ ERRADO — patch('app.utils.business_rules.Posicao') falha
def validar_saldo(usuario_id):
    from app.models.posicao import Posicao  # não fica no namespace do módulo
    ...

# ✅ CORRETO — import no topo, mockável normalmente
from app.models.posicao import Posicao

def validar_saldo(usuario_id):
    ...
```

**Regra:** Imports de models em `utils/` e `services/` devem estar no **topo do arquivo**.
Exceção aceita apenas para imports circulares comprovados e documentados.

---

### L-SA-002 — session.configure(bind=connection) é incompatível com Flask test_client
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```python
# ❌ NÃO FUNCIONA — Flask test_client abre conexões próprias do pool
connection = db.engine.connect()
db.session.configure(bind=connection)
yield db
connection.rollback()  # não desfaz commits feitos via HTTP request

# ✅ CORRETO — app context session-scoped + DELETE no teardown
@pytest.fixture(scope='session')
def app():
    ctx = application.app_context()
    ctx.push()
    yield application
    ctx.pop()

@pytest.fixture(scope='function')
def auth_client(app):
    u = Usuario(...)
    db.session.add(u)
    db.session.commit()
    yield client
    Usuario.query.filter_by(username=u.username).delete()
    db.session.commit()
```

---

### L-SA-003 — Múltiplos app_context() aninhados causam "Popped wrong app context"
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

Com `app` fixture de escopo `session` que já mantém um contexto ativo via `ctx.push()`,
fixtures de escopo `function` **não devem** abrir `with app.app_context()`.
Operam diretamente no contexto já ativo.

---

## 🌐 Contrato da API

### L-API-001 — Endpoint de listagem usa envelope de paginação aninhado
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```json
// ✅ Endpoints de entidade única (padrão)
{ "success": true, "data": { "id": "...", "ticker": "PETR4" } }

// ⚠️  Endpoints de listagem com paginação (diferente!)
{ "success": true, "data": { "ativos": [...], "total": 65, "pages": 4, "page": 1, "per_page": 20 } }
```

Em testes e no frontend, extrair a lista com:
```python
inner = data.get('data', {})
lista = inner.get('ativos', []) if isinstance(inner, dict) else inner
```

---

### L-API-002 — Flask-JWT-Extended retorna 422 para token malformado, não 401
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

- **401** → token ausente ou expirado
- **422** → token presente mas malformado/inválido

```python
# ✅ Testes devem aceitar ambos
assert response.status_code in (401, 422)
```

---

### L-API-003 — Ticker tem validação restritiva (sem underscore)
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

O endpoint `POST /api/ativos/` aceita apenas letras, números, pontos e hífens.
Underscore (`_`) retorna 400. Em testes, usar sufixos numéricos: `f'TST{uuid4().int[:4]}'`.

---

## 🏗️ Models

### L-MOD-001 — Regra de negócio coerente ≠ campo existente no model
**Origem:** EXITUS-SEED-001 | **Data:** 02/03/2026

```python
# ❌ ERRADO — 'pais' faz sentido no domínio mas não existe em Ativo
ativo = Ativo(ticker='PETR4', pais='BR')

# ✅ CORRETO — Ativo usa 'mercado' para indicar região
ativo = Ativo(ticker='PETR4', mercado='BR')
```

**Regra:** Sempre ler o arquivo `models/nome_model.py` e verificar as `Column(...)` definidas
antes de usar um campo. Nunca assumir campos por analogia com outros models.

---

## 📋 Referências

| Documento | Papel |
|---|---|
| `docs/CODING_STANDARDS.md` | Padrões de código para humanos |
| `docs/ROADMAP.md` | GAPs registrados (ENUM-001, TESTDB-001) |
| `.codeium.rules` | Regras operacionais da IA |
| `docs/EXITUS-SQLALCHEMY-001.md` | Padrões SQLAlchemy detalhados |
