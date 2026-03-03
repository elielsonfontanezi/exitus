# EXITUS-TESTS-001 — Lições Aprendidas e Recomendações

> **Data:** 03 de Março de 2026  
> **GAP:** EXITUS-TESTS-001 — Testes Automatizados com Pytest  
> **Status:** Concluído — 69/69 testes passando

---

## 1. Problemas Descobertos na Cadeia de Migrations Alembic

### 1.1 Migration `9e4ef61dee5d` estava quebrada

**Problema:** O arquivo não tinha as variáveis `revision` e `down_revision` como atribuições Python — apenas comentários no docstring. O Alembic não conseguia detectar a revisão.

**Causa:** Migration criada manualmente sem seguir o template padrão do Alembic.

```python
# ❌ ERRADO — Alembic não lê do docstring
"""
Revision ID: 9e4ef61dee5d
Revises: 202602162130
"""

# ✅ CORRETO — variáveis obrigatórias no corpo do módulo
revision = '9e4ef61dee5d'
down_revision = '202602162130'
branch_labels = None
depends_on = None
```

**Regra:** Toda migration criada manualmente **deve** ter as 4 variáveis no corpo do módulo.

---

### 1.2 ENUMs duplicados entre migrations

**Problema:** A migration `b2542b2f7857` (Initial schema) cria ENUMs implicitamente ao criar tabelas com `sa.Enum(...)`. A migration `20251208_1004_m7` tentava criá-los novamente com `ENUM.create()`, falhando com `DuplicateObject` num banco limpo.

**Causa:** Migrations de fases diferentes não consideram que o SQLAlchemy já criou o tipo ENUM ao executar a migration anterior.

**Solução aplicada:**
```python
# ❌ ERRADO — ignora existência prévia
tipo_relatorio_enum = postgresql.ENUM('portfolio', ..., create_type=True)
tipo_relatorio_enum.create(op.get_bind(), checkfirst=True)  # checkfirst é ignorado

# ✅ CORRETO — idempotente via DO block
op.execute("""
    DO $$ BEGIN
        CREATE TYPE tiporelatorio AS ENUM ('portfolio', ...);
    EXCEPTION WHEN duplicate_object THEN NULL; END $$
""")
```

**Regra:** Toda migration que cria ENUMs PostgreSQL deve usar o padrão `DO $$ EXCEPTION WHEN duplicate_object` para ser idempotente.

---

### 1.3 Cadeia de migrations quebrada para banco limpo

**Problema:** A sequência `b2542b2f7857 → 20251208_1004_m7 → ... → 20260223_2110` não consegue criar um banco do zero. Motivos:

1. `tipoativo` criado na migration inicial com valores UPPERCASE (`ACAO`, `FII`...) mas o model Python usa lowercase (`acao`, `fii`...)
2. `tipoeventocorporativo` criado UPPERCASE no initial schema, mas `CheckConstraint` no model usa lowercase
3. `tipotransacao` migrado para lowercase pela `20260223_2110`, mas a `9e4ef61dee5d` tenta `ALTER TYPE` antes da tabela existir

**Solução usada:** `pg_dump --schema-only` do banco de produção para criar o banco de teste. Esta é a forma mais confiável de ter paridade total.

```bash
pg_dump -U exitus -d exitusdb --schema-only --no-owner --no-acl -f /tmp/schema.sql
psql -U exitus -d exitusdb_test -f /tmp/schema.sql
```

**Recomendação:** Criar um script `scripts/create_test_db.sh` que automatiza este processo.

---

## 2. Inconsistência de Case nos ENUMs PostgreSQL

### 2.1 Estado atual (problema de design)

Existe **inconsistência** entre ENUMs criados em diferentes fases do projeto:

| ENUM | Valores no PostgreSQL | Valores no Python (model) | Consistente? |
|------|----------------------|--------------------------|--------------|
| `tipotransacao` | `compra`, `venda`, `dividendo`... | `compra`, `venda`... | ✅ lowercase |
| `tipoeventocorporativo` | `SPLIT`, `GRUPAMENTO`... | `split`, `grupamento`... | ❌ UPPERCASE no DB |
| `tipoativo` | `ACAO`, `FII`, `REIT`... | `acao`, `fii`, `reit`... | ❌ UPPERCASE no DB |
| `tipooperacao` | `COMPRA`, `VENDA` | não confirmado | ❌ UPPERCASE no DB |
| `tipoprovento` | `DIVIDENDO`, `JCP`... | `dividendo`, `jcp`... | ❌ UPPERCASE no DB |
| `userrole` | `ADMIN`, `USER`, `READONLY` | `admin`, `user`, `readonly` | ❌ UPPERCASE no DB |
| `incidenciaimposto` | `LUCRO`, `RECEITA`... | `lucro`, `receita`... | ❌ UPPERCASE no DB |
| `tiporelatorio` | `portfolio`, `performance`... | `portfolio`... | ✅ lowercase |
| `tipoalerta` | `queda_preco`, `alta_preco`... | `queda_preco`... | ✅ lowercase |

**Impacto:** O SQLAlchemy mapeia `TipoAtivo.ACAO` → value `"acao"` (lowercase), mas o PostgreSQL armazena `"ACAO"` (UPPERCASE). Isso funciona **apenas** porque o SQLAlchemy faz a conversão automaticamente via `Enum(TipoAtivo)`. Se alguém fizer uma query SQL direta com `WHERE tipo = 'acao'`, vai falhar.

**Recomendação futura (EXITUS-ENUM-001):** Criar migration que padroniza **todos** os ENUMs para lowercase, similar ao que foi feito para `tipotransacao` na `20260223_2110`.

---

## 3. Problemas no SQLAlchemy + Flask Testing

### 3.1 `session.configure(bind=connection)` é incompatível com Flask test_client

**Problema:** O padrão clássico de rollback transacional em testes SQLAlchemy não funciona com Flask:

```python
# ❌ NÃO FUNCIONA com Flask test_client
connection = db.engine.connect()
transaction = connection.begin()
db.session.configure(bind=connection)
yield db
transaction.rollback()
```

**Causa:** O `Flask test_client` abre suas **próprias conexões** do connection pool para cada request HTTP. A sessão vinculada ao fixture não é a mesma usada pelo app durante o request — os dados commitados pelo endpoint não são visíveis na sessão do fixture, e o rollback não desfaz commits feitos via HTTP.

**Solução correta para testes de integração:**
```python
# ✅ FUNCIONA — contexto único + cleanup explícito
@pytest.fixture(scope='session')
def app():
    application = create_app(testing=True)
    ctx = application.app_context()
    ctx.push()
    yield application
    db.session.remove()
    ctx.pop()

@pytest.fixture(scope='function')
def auth_client(app):
    # Cria dados diretamente, sem binding de sessão
    u = Usuario(...)
    db.session.add(u)
    db.session.commit()
    yield client
    # Cleanup explícito
    Usuario.query.filter_by(username=username).delete()
    db.session.commit()
```

**Regra:** Para testes de integração com Flask test_client, usar **cleanup explícito por DELETE** no teardown, não rollback transacional.

---

### 3.2 Múltiplos `app_context()` causam "Popped wrong app context"

**Problema:** Com `app` fixture de escopo `session` que mantém um contexto ativo, fixtures de escopo `function` não devem abrir novos `with app.app_context()` — isso empilha contextos Flask e causa o erro:

```
AssertionError: Popped wrong app context.
(<flask.ctx.AppContext at 0x...> instead of <flask.ctx.AppContext at 0x...>)
```

**Solução:** Fixtures function-scoped operam diretamente no contexto já ativo pelo `app` fixture de sessão.

---

### 3.3 Imports locais em funções impedem mocking

**Problema encontrado em `business_rules.py`:** Modelos importados **dentro** das funções não ficam no namespace do módulo, tornando `patch('app.utils.business_rules.Posicao')` ineficaz (o atributo não existe).

```python
# ❌ ANTES — import local impossibilita mock
def validar_saldo_venda(usuario_id, ativo_id, quantidade):
    from app.models.posicao import Posicao  # nunca visível como atributo do módulo
    ...

# ✅ DEPOIS — import no topo, mockável
from app.models.posicao import Posicao  # pode ser patchado normalmente

def validar_saldo_venda(usuario_id, ativo_id, quantidade):
    ...
```

**Regra:** Imports de models em módulos de utils/services devem estar no **topo do arquivo**, nunca dentro de funções, exceto quando há risco real de import circular documentado.

---

## 4. Contrato da API — Envelope de Resposta

### 4.1 Endpoint de listagem usa envelope aninhado

**Descoberto durante testes:** O endpoint `GET /api/ativos/` não segue o mesmo padrão dos outros endpoints:

```json
// ✅ Padrão da maioria dos endpoints (data é a entidade diretamente)
{ "success": true, "data": { "id": "...", "ticker": "PETR4" } }

// ⚠️  Listagem de ativos (data é um objeto de paginação)
{
  "success": true,
  "data": {
    "ativos": [...],
    "total": 65,
    "pages": 4,
    "page": 1,
    "per_page": 20
  }
}
```

**Impacto:** Clientes que assumem `data` como lista direta vão falhar. O frontend e qualquer consumidor da API precisam lidar com os dois formatos.

**Recomendação:** Padronizar o envelope de paginação em todos os endpoints de listagem — ou documentar explicitamente no Swagger (EXITUS-SWAGGER-001).

---

### 4.2 Comportamento de tokens JWT malformados

**Descoberto:** Flask-JWT-Extended retorna **422** (Unprocessable Entity) para tokens malformados, e **401** apenas para tokens ausentes ou expirados. Não é um bug — é o comportamento correto do padrão JWT.

```python
# Testes devem aceitar ambos os códigos
assert response.status_code in (401, 422)  # ✅
assert response.status_code == 401          # ❌ falha para token malformado
```

---

### 4.3 Validação de ticker tem regex restritivo

**Descoberto:** O endpoint `POST /api/ativos/` valida o ticker com regex que rejeita underscore (`_`). Tickers com `_` retornam 400.

```
"Ticker deve conter apenas letras, números, pontos e hífens"
```

Isso é correto para tickers B3/NYSE, mas é importante documentar para não confundir em testes.

---

## 5. Banco de Dados — Recomendações

### 5.1 Script `create_test_db.sh` (ausente — recomendado)

Atualmente o banco `exitusdb_test` foi criado manualmente. Deve ser automatizado:

```bash
#!/bin/bash
# scripts/create_test_db.sh
podman exec exitus-db psql -U exitus -d postgres -c "DROP DATABASE IF EXISTS exitusdb_test;"
podman exec exitus-db psql -U exitus -d postgres -c "CREATE DATABASE exitusdb_test OWNER exitus;"
podman exec exitus-db pg_dump -U exitus -d exitusdb --schema-only --no-owner --no-acl \
  | podman exec -i exitus-db psql -U exitus -d exitusdb_test
echo "✅ exitusdb_test criado com schema de produção"
```

**Importante:** Este script deve ser executado sempre que houver uma nova migration aplicada em produção.

---

### 5.2 Dados de teste acumulados no `exitusdb_test`

**Problema descoberto:** Durante as iterações de desenvolvimento dos testes, ativos e usuários de teste ficaram acumulados no banco `exitusdb_test` (tickers `LST*`, `IT*`, `VL*`, `DUP*`, usuários `ta*`, `us*`).

**Causa:** Testes que falharam no meio da execução não rodaram o teardown de cleanup.

**Recomendação:** Adicionar ao `conftest.py` uma fixture `autouse` de limpeza pós-sessão:

```python
@pytest.fixture(scope='session', autouse=True)
def cleanup_test_data(app):
    yield
    # Limpa resíduos de execuções anteriores com falha
    from app.models.usuario import Usuario
    from app.models.ativo import Ativo
    Usuario.query.filter(Usuario.email.like('%@test.exitus')).delete(synchronize_session=False)
    Ativo.query.filter(Ativo.nome.like('Ativo%Teste%')).delete(synchronize_session=False)
    _db.session.commit()
```

---

### 5.3 ENUM `tipoeventocorporativo` — inconsistência model vs banco

**Problema de design:** O model Python define valores lowercase (`split`, `grupamento`), mas o banco PostgreSQL armazena UPPERCASE (`SPLIT`, `GRUPAMENTO`). O `CheckConstraint` na tabela usa os valores do modelo Python:

```python
db.CheckConstraint(
    "(tipo_evento IN ('split', 'grupamento', 'bonificacao') AND proporcao IS NOT NULL)",
    name="evento_proporcao_obrigatoria"
)
```

Isso causa `DataError` ao tentar criar a tabela em banco novo (porque o ENUM tem `SPLIT` mas o constraint referencia `split`).

**Recomendação:** Unificar para lowercase via migration (parte do EXITUS-ENUM-001 futuro).

---

## 6. Processo de Desenvolvimento — Recomendações

### 6.1 Todo novo banco de ambiente precisa do script de criação

Fluxo correto para criar qualquer ambiente de banco novo:
1. `pg_dump --schema-only exitusdb > schema.sql`
2. `psql exitusdb_novo < schema.sql`
3. **Não usar** `db.create_all()` nem `alembic upgrade head` em banco limpo — ambos falham por razões diferentes

### 6.2 Regra para migrations com ENUMs

Toda migration que declara ENUMs PostgreSQL deve usar o template:
```python
op.execute("""
    DO $$ BEGIN
        CREATE TYPE <nome> AS ENUM (...);
    EXCEPTION WHEN duplicate_object THEN NULL; END $$
""")
```

E referenciar o tipo com `create_type=False`:
```python
meu_enum = postgresql.ENUM(name='<nome>', create_type=False)
```

### 6.3 Regra para variáveis de migration

Todo arquivo de migration deve ter no corpo do módulo (não apenas no docstring):
```python
revision = '<hash>'
down_revision = '<hash_anterior>'  # ou None para a primeira
branch_labels = None
depends_on = None
```

---

## 7. Resumo dos GAPs Gerados

| GAP Sugerido | Descrição | Prioridade |
|---|---|---|
| **EXITUS-ENUM-001** | Padronizar todos ENUMs para lowercase via migration | Média |
| **EXITUS-TESTDB-001** | Script automatizado `create_test_db.sh` | Baixa |
| **EXITUS-APIDOC-001** | Documentar envelope de paginação no Swagger | Baixa (parte do SWAGGER-001) |

---

## 8. Arquivos Modificados no EXITUS-TESTS-001

| Arquivo | Tipo de mudança | Razão |
|---|---|---|
| `backend/app/__init__.py` | Feat | Suporte a `create_app(testing=True)` |
| `backend/app/config.py` | Feat | `TestingConfig` com `exitusdb_test` |
| `backend/app/utils/business_rules.py` | Fix | Imports movidos para topo do módulo |
| `backend/alembic/versions/9e4ef61dee5d_*.py` | Fix | Adicionadas variáveis `revision`/`down_revision` |
| `backend/alembic/versions/20251208_1004_m7_*.py` | Fix | ENUMs idempotentes via `DO EXCEPTION` |
| `backend/tests/conftest.py` | Feat | Infraestrutura de testes |
| `backend/tests/test_business_rules.py` | Feat | 37 testes unitários |
| `backend/tests/test_auth_integration.py` | Feat | 13 testes de integração |
| `backend/tests/test_ativos_integration.py` | Feat | 19 testes de integração |
| `backend/pytest.ini` | Feat | Configuração pytest |
| `.codeium.rules` | Docs | Regras de processo de IA |
