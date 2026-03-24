# Lições Aprendidas — Sistema Exitus

> **Propósito:** Regras ativas derivadas de erros reais em produção/desenvolvimento.  
> Consultado pela IA **antes de qualquer ação** para evitar repetição de erros.  
> **Atualizado:** 23/03/2026 — L-FE-001 adicionado (race condition Chart.js)  
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
```

---

## 🎨 Frontend Templates

### L-FE-001 — Chart.js: nunca usar setTimeout para renderização após Alpine.js
**Origem:** Dashboard race condition | **Data:** 23/03/2026

```javascript
// ❌ ERRADO — race condition entre Alpine.js re-render e Chart.js
setTimeout(() => this.renderizarGraficos(), 100);

// ✅ CORRETO — aguardar ciclo completo do Alpine.js
this.$nextTick(() => this.renderizarGraficos());
```

**Problema:** `setTimeout` não garante que o DOM esteja pronto quando Alpine.js atualiza reativamente `this.dados`. Chart.js pode receber canvas nulo ou destruído durante animação pendente.

**Solução:** 
- Usar `$nextTick` do Alpine.js para aguardar o ciclo de reatividade
- Adicionar `animation: false` nas opções do Chart.js
- Null explícito após `destroy()` para evitar referências órfãs

### L-FE-003 — Histórico patrimonial requer snapshots mensais automáticos
**Origem:** Dashboard inconsistente | **Data:** 23/03/2026

```python
# ❌ PROBLEMA — histórico parado vs patrimônio atual
historico_ultimo = R$ 58.050  # jun/2024
patrimonio_atual = R$ 249.907,10  # mar/2026

# ✅ SOLUÇÃO — snapshot manual (temporário)
snapshot_manual = HistoricoPatrimonio(
    data=date.today(),
    patrimonio_total=patrimonio_atual
)

# 🔄 NECESSÁRIO — job mensal automático (implementação futura)
def job_mensal_historico_patrimonial():
    for usuario in Usuario.query.all():
        patrimonio = PortfolioService.get_dashboard(usuario.id)['resumo']['patrimonio_total']
        # Criar snapshot mensal para cada usuário
```

**Problema:** Tabela `historico_patrimonio` não tinha processo de atualização automática, causando discrepância entre histórico do gráfico e valor atual.

**Solução temporária:** Snapshot manual adicionado para corrigir visualização imediata.

**Ação futura obrigatória:** Implementar job agendado (mensal) para atualizar snapshots de todos os usuários automaticamente.

### L-FE-002 — Sintaxe Jinja2: include não usa 'with' para passar variáveis
**Origem:** Frontend Template Error | **Data:** 17/03/2026

```jinja2
# ❌ ERRADO — 'with' não é sintaxe válida em Jinja2 includes
{% include 'components/cards/stat_card.html' with title='Dashboard' value='R$ 1000' %}

# ✅ CORRETO — include simples, variáveis via contexto
{% include 'components/cards/stat_card.html' %}

# ✅ ALTERNATIVA — passar contexto completo
{% include 'components/cards/stat_card.html' with context %}
```

**Problema:** `jinja2.exceptions.TemplateSyntaxError: expected token 'end of statement block', got 'with'`

**Solução:** Remover `with` dos includes ou usar `with context` para herdar contexto atual. Componentes devem receber dados via contexto do template pai, não via parâmetros no include.
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

### L-DB-004 — ENUMs PostgreSQL devem ser lowercase (resolvido)
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026 | **Resolvido:** 04/03/2026

| ENUM | No PostgreSQL | No Python (model) | Status |
|------|--------------|-------------------|--------|
| Todos os 12 ENUMs | lowercase | lowercase | ✅ normalizado |

**✅ Fix aplicado:** EXITUS-ENUM-001 (04/03/2026) — migration normalizou todos os 12 ENUMs para lowercase. `values_callable` obrigatório em todos os models (verificado por `test_model_standards.py`).

**Regra ativa:** Sempre usar `values_callable=lambda x: [e.value for e in x]` e `create_type=False` em colunas ENUM. Ver `CODING_STANDARDS.md`.

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

## 🧪 Testes

### L-TEST-002 — Fixture cleanup_test_data deve deletar TUDO, fixtures não devem deletar
**Origem:** Correção de 8 ERRORS de teardown | **Data:** 10/03/2026

**Problema:** Fixtures que deletam suas próprias entidades no teardown causam FK violations quando há dados dependentes criados durante os testes.

```python
# ❌ ERRADO — fixture deleta no teardown
@pytest.fixture
def usuario_seed(app):
    u = Usuario(...)
    db.session.add(u)
    db.session.commit()
    yield u
    Usuario.query.filter_by(id=u.id).delete()  # ❌ FK violation se houver transações
    db.session.commit()

# ✅ CORRETO — fixture não deleta, cleanup_test_data faz tudo
@pytest.fixture
def usuario_seed(app):
    u = Usuario(...)
    db.session.add(u)
    db.session.commit()
    yield u
    # Limpeza feita por cleanup_test_data
```

**Solução:** Fixture `cleanup_test_data` (autouse) deleta **todas** as entidades na ordem correta:
1. Posições → 2. Transações → 3. Movimentações → 4. Corretoras → 5. Ativos → 6. Usuários

**Usar `synchronize_session=False`** para forçar delete direto no banco.

---

### L-TEST-003 — auth_client não aplica headers automaticamente
**Origem:** 5 testes com 401 Unauthorized | **Data:** 10/03/2026

**Problema:** O fixture `auth_client` armazena headers em `c._auth_headers`, mas o Flask test_client **não os aplica automaticamente**.

```python
# ❌ ERRADO — 401 Unauthorized
response = auth_client.get('/api/reconciliacao/verificar')

# ✅ CORRETO — passar headers explicitamente
response = auth_client.get('/api/reconciliacao/verificar', headers=auth_client._auth_headers)
```

**Regra:** Sempre passar `headers=auth_client._auth_headers` em **todas** as requisições HTTP nos testes.

---

### L-TEST-004 — Problemas de sessão SQLAlchemy em testes
**Origem:** Teste de saldo falhando | **Data:** 10/03/2026

**Problema:** Modificar objeto de fixture e depois fazer query pode retornar estado desatualizado.

```python
# ❌ ERRADO — modificar fixture diretamente
corretora_seed.saldo_atual = 800.00
db.session.commit()
# Query do serviço pode ver estado antigo

# ✅ CORRETO — buscar novamente antes de modificar
corr = Corretora.query.get(corretora_seed.id)
corr.saldo_atual = 800.00
db.session.commit()
```

**Regra:** Quando modificar entidades em testes, sempre fazer nova query antes de modificar para garantir estado atualizado.

---

### L-TEST-005 — Enum values devem ser comparados com .value
**Origem:** ReconciliacaoService calculando saldo errado | **Data:** 10/03/2026

**Problema:** Comparar `str(enum)` retorna representação diferente do valor real.

```python
# ❌ ERRADO — str(TipoMovimentacao.DEPOSITO) = 'TipoMovimentacao.DEPOSITO'
tipo = str(mov.tipo_movimentacao).upper()
if tipo in ['DEPOSITO', 'SAQUE']:  # Nunca vai bater

# ✅ CORRETO — usar .value
tipo = mov.tipo_movimentacao.value  # 'deposito'
if tipo in ['deposito', 'saque']:  # ✅ Funciona
```

**Regra:** Sempre usar `.value` para obter o valor real de enums Python.

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

### L-SA-004 — `Query.get()` está depreciado no SQLAlchemy 2.x — 27 ocorrências no codebase
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

```python
# ❌ DEPRECIADO — SQLAlchemy 2.x emite warning; será removido
ativo = Ativo.query.get(ativo_id)

# ✅ CORRETO — SQLAlchemy 2.x
ativo = db.session.get(Ativo, ativo_id)
```

Afeta 11 arquivos: `ativo_service.py`, `usuario_service.py`, `corretora_service.py`,
`provento_service.py`, `transacao_service.py`, `feriado_mercado_service.py`,
`regra_fiscal_service.py`, `evento_corporativo_service.py`, `historico_service.py`,
`alerta_service.py`, `decorators.py`, `auth/routes.py`.  
**Fix planejado:** EXITUS-SQLALCHEMY-002.

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

### L-API-004 — `ValueError` usado para 404 E 400 — contrato de exceções ambíguo
**Origem:** EXITUS-TESTS-001 | **Data:** 03/03/2026

Os services lançam `ValueError` para **dois significados distintos**:

```python
# ❌ AMBÍGUO — route não sabe se é 404 ou 400
raise ValueError("Ativo não encontrado")    # deveria ser 404
raise ValueError("Ticker já existe")        # deveria ser 400
```

O route captura tudo como 400:
```python
except ValueError as e:
    return error(str(e), 400)  # ← engloba casos de 404 incorretamente
```

**Padrão correto (a implementar em EXITUS-CRUD-002):**
```python
# No service — exceções tipadas
class NotFoundError(Exception): pass
class ConflictError(Exception): pass

raise NotFoundError("Ativo não encontrado")  # → 404
raise ConflictError("Ticker já existe")      # → 409

# No route — mapeamento semântico
except NotFoundError as e:
    return not_found(str(e))      # 404
except ConflictError as e:
    return error(str(e), 409)     # 409
except ValidationError as e:
    return error(str(e), 400)     # 400
```

**Fix planejado:** EXITUS-CRUD-002.

---

### L-TEST-001 — Nunca usar dados hardcoded em testes de integração
**Origem:** EXITUS-TESTDB-001 | **Data:** 03/03/2026

Testes com usernames, tickers ou valores fixos (`'test_admin'`, `'PETR4'`, `38.50`) passam enquanto o banco de teste tem esses dados herdados do banco de produção. Ao zerar o banco (ex: via `create_test_db.sh`), os testes quebram silenciosamente.

```python
# ❌ ERRADO — depende de dado pré-existente no banco
response = client.get('/api/ativos/ticker/PETR4')
assert data['data']['ticker'] == 'PETR4'

# ✅ CORRETO — dado dinâmico criado e destruído pela própria fixture
def test_ticker_existente(auth_client, ativo_seed):
    response = client.get(f'/api/ativos/ticker/{ativo_seed.ticker}')
    assert data['data']['ticker'] == ativo_seed.ticker
```

**Regra:** Toda fixture de entidade deve ser criada no `conftest.py` com sufixo UUID e destruída no teardown. Nenhum teste deve depender de dados que existam apenas no banco de produção.

---

### L-TEST-002 — `db.create_all()` falha com ENUMs PostgreSQL nativos
**Origem:** EXITUS-TESTDB-001 | **Data:** 03/03/2026

`db.create_all()` tenta criar tabelas com CHECK constraints que referenciam valores de ENUMs (`'split'`, `'grupamento'`) antes de criar o tipo ENUM no PostgreSQL, causando `InvalidTextRepresentation`.

```python
# ❌ ERRADO — não respeita ordem de criação de tipos ENUM PostgreSQL
with app.app_context():
    db.create_all()  # DataError: invalid input value for enum tipoeventocorporativo

# ✅ CORRETO — pg_dump garante ordem correta (ENUMs antes das tabelas)
podman exec exitus-db pg_dump -U exitus --schema-only --no-owner exitusdb | \
    podman exec -i exitus-db psql -U exitus -d exitusdb_test
```

**Regra:** Para recriar o banco de teste, usar sempre `pg_dump --schema-only` do banco de produção via `scripts/create_test_db.sh`. Nunca usar `db.create_all()` para setup de banco de teste em projetos com ENUMs PostgreSQL nativos.

---

### L-TEST-003 — `DetachedInstanceError` em teardown de testes — salvar IDs antes de sair do contexto
**Origem:** EXITUS-IR-005 | **Data:** 04/03/2026

```python
# ❌ ERRADO — objeto fica detached ao sair do with app.app_context()
with app.app_context():
    resgate = Transacao(...)
    db.session.commit()
try:
    ...
finally:
    Transacao.query.filter_by(id=resgate.id).delete()  # DetachedInstanceError!

# ✅ CORRETO — salvar IDs escalares antes de sair do contexto
with app.app_context():
    resgate = Transacao(...)
    db.session.commit()
    resgate_id = resgate.id   # UUID copiado enquanto session está ativa
try:
    ...
finally:
    Transacao.query.filter_by(id=resgate_id).delete()  # ID escalar, sem detach
    db.session.commit()
```

**Regra:** Em testes `function`-scoped com `app` fixture `session`-scoped, objetos SQLAlchemy
não devem ser acessados fora do bloco que os criou. Copiar sempre `.id` (e outros escalares
necessitários) antes de fechar o `with app.app_context()` ou antes do `commit` final.

---

### L-TEST-004 — Usar `decode_token` para obter `usuario_id` do `auth_client` em fixtures
**Origem:** EXITUS-IR-005 | **Data:** 04/03/2026

```python
# ❌ ERRADO — busca um usuário aleatório do banco (pode não ser o do token JWT)
from app.models.usuario import Usuario
u = Usuario.query.filter(Usuario.username.like('ta%')).first()
# Cria dados vinculados a u.id, mas auth_client tem token de outro usuário

# ✅ CORRETO — extrair usuario_id diretamente do token JWT do auth_client
from flask_jwt_extended import decode_token
token = auth_client._auth_headers['Authorization'].split(' ')[1]
with app.app_context():
    decoded = decode_token(token)
usuario_id = decoded['sub']  # UUID do usuário que o endpoint irá usar
```

**Regra:** Em testes que criam dados de setup e chamam endpoints autenticados via `auth_client`,
os dados devem ser criados com o `usuario_id` extraido do token — nunca via query heurística
no banco. Isso garante que a apuração encontre exatamente os dados criados pelo teste.

---

### L-DB-006 — Nunca usar strings hardcoded para ENUMs PostgreSQL em services
**Origem:** EXITUS-VALIDATION-001 | **Data:** 08/03/2026

```python
# ❌ ERRADO — PostgreSQL espera lowercase 'fii', não 'FII'
tipo_ativo = 'FII'
ativo = Ativo(tipo=tipo_ativo, ...)  # psycopg2.errors.InvalidTextRepresentation

# ✅ CORRETO — usar o enum Python, que tem values_callable para lowercase
from app.models.ativo import TipoAtivo
tipo_ativo = TipoAtivo.FII
ativo = Ativo(tipo=tipo_ativo, ...)
```

**Regra:** Em services de importação ou qualquer código que instancie models com campos ENUM,
sempre usar a classe Python do enum (ex: `TipoAtivo.FII`). Nunca strings literais como `'FII'` ou `'fii'`.
O `values_callable` nos models garante a serialização correta para o PostgreSQL.

---

### L-SVC-001 — Nunca usar current_app.db — sempre importar db diretamente
**Origem:** EXITUS-SERVICE-REVIEW-001 | **Data:** 08/03/2026

```python
# ❌ ERRADO — current_app não tem atributo 'db'; levanta AttributeError em runtime
current_app.db.session.add(obj)
current_app.db.session.commit()

# ✅ CORRETO — importar db do módulo correto
from app.database import db
db.session.add(obj)
db.session.commit()
```

**Regra:** `current_app` expõe configurações Flask (ex: `current_app.config`), não extensões.
O SQLAlchemy `db` deve sempre ser importado de `app.database`. Erro silencioso: o service parece funcionar nos testes mas falha em runtime.

---

### L-TEST-001 — pandas converte célula CSV vazia para string 'nan', não string vazia
**Origem:** EXITUS-COVERAGE-001 | **Data:** 08/03/2026

```python
# ❌ ERRADO — assumir que célula CSV vazia vira '' em pandas
csv = "Código de Negociação\n\n"
df = pd.read_csv(...)
assert df.iloc[0]['Código de Negociação'] == ''  # Falha! É 'nan'

# ✅ CORRETO — verificar com pd.isna() ou str() comparado a 'nan'
valor = str(row.get('Código', '')).strip()
if not valor or valor == 'nan':
    continue
```

**Regra:** Ao escrever testes para parsers que usam pandas, nunca assumir que célula vazia
produz string vazia. `pd.read_csv` retorna `float('nan')` que `str()` converte para `'nan'`.
Testar com `pd.isna()` ou filtrar pelo valor string `'nan'` explicitamente.

---

### L-TEST-002 — Testes de CHECK constraint devem usar engine.connect() com rollback explícito
**Origem:** EXITUS-CONSTRAINT-001 | **Data:** 08/03/2026

```python
# ❌ ERRADO — begin_nested() em sessão ORM de escopo 'session' levanta PendingRollbackError
db.session.begin_nested()
db.session.add(obj_invalido)
with pytest.raises(IntegrityError):
    db.session.flush()
db.session.rollback()  # sessão fica corrompida para o próximo teste

# ✅ CORRETO — conexão independente da sessão ORM, transação própria sempre revertida
conn = db.engine.connect()
trans = conn.begin()
raised = None
try:
    conn.execute(text(sql), params)
except Exception as e:
    raised = e
finally:
    trans.rollback()
    conn.close()
assert raised is not None and 'check' in str(raised).lower()
```

**Regra:** O conftest do Exitus usa `scope='session'` sem wrapping transacional por teste.
`begin_nested()` na sessão ORM compartilhada corrompe o estado quando o flush falha.
Para testar constraints do banco, usar `engine.connect()` com transação própria que **sempre** faz rollback no `finally`.

---

### L-CB-001 — Circuit breaker com recovery_timeout=0 nunca fica OPEN via property state
**Origem:** EXITUS-CIRCUITBREAKER-001 | **Data:** 08/03/2026

```python
# Comportamento: recovery_timeout=0 faz state property re-transicionar para HALF_OPEN imediatamente
cb = CircuitBreaker('test', failure_threshold=2, recovery_timeout=0)
cb.record_failure(); cb.record_failure()
assert cb._state == STATE_OPEN     # interno: OPEN
assert cb.state == STATE_HALF_OPEN # property re-avalia: já expirou → HALF_OPEN imediatamente
```

**Regra:** A property `state` do `CircuitBreaker` avalia o timeout a cada acesso.
Com `recovery_timeout=0`, o estado OPEN é instantaneamente convertido para HALF_OPEN.
Para testes de bloqueio real, usar `recovery_timeout` alto (ex: 9999).
Para verificar que `record_failure` abriu o circuito internamente, inspecionar `cb._state`.

---

### L-TEST-003 — Fixtures de teste devem usar identificadores únicos (UUID suffix)
**Origem:** EXITUS-TESTFIX-CAMBIO-001 | **Data:** 09/03/2026

```python
# ❌ ERRADO — email fixo causa UniqueViolation quando o fixture é reutilizado
usuario = Usuario(username='test_cambio', email='test_cambio@exitus.com')

# ✅ CORRETO — sufixo UUID garante unicidade entre execuções e testes
suffix = str(uuid.uuid4())[:8]
username = f'test_cambio_{suffix}'
email = f'{username}@test.exitus'
usuario = Usuario(username=username, email=email)
```

**Regra:** Em suites com `scope='session'` no conftest, fixtures que criam entidades no banco devem usar identificadores únicos. O pytest não isola automaticamente dados entre testes quando a sessão é compartilhada. Use UUID suffix ou contadores para evitar conflitos de chave única.

---

## 🧪 Testes

### L-TEST-001 — Fixtures devem fazer rollback antes de DELETE
**Origem:** Auditoria de testes | **Data:** 09/03/2026

```python
# ❌ ERRADO — PendingRollbackError se teste anterior falhou
@pytest.fixture(scope='function')
def usuario_seed(app):
    u = Usuario(...)
    db.session.add(u)
    db.session.commit()
    yield u
    Usuario.query.filter_by(username=username).delete()
    db.session.commit()

# ✅ CORRETO — rollback antes de DELETE + try/except em commit
@pytest.fixture(scope='function')
def usuario_seed(app):
    u = Usuario(...)
    db.session.add(u)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    yield u
    
    db.session.rollback()  # Limpa transação pendente
    Usuario.query.filter_by(username=username).delete()
    db.session.commit()
```

**Problema:** Quando um teste falha, a transação fica em estado `PendingRollback`. O teardown do fixture tenta fazer DELETE mas falha com `InFailedSqlTransaction`.

**Solução:**
1. Adicionar `db.session.rollback()` **antes** de DELETE no teardown
2. Adicionar `try/except` com rollback em **commits** do setup
3. Criar fixture `autouse` para limpar dados de teste (transações, posições)

**Resultado:** 82 errors resolvidos (90 → 8), taxa de sucesso 96.6% (482/499 testes).

**Testes pendentes:** 17 testes ainda apresentam problemas (9 FAILED + 8 ERRORS). Ver `docs/TESTES_PENDENTES.md` para detalhes e plano de correção.

---

## � Migrations e Testes

### L-MIG-001 — Aplicar migrations em ambos os bancos (dev e teste)
**Origem:** DIVCALENDAR-001 | **Data:** 10/03/2026

**Problema:** Nova migration criada no banco de desenvolvimento, mas testes falham com `UndefinedTable` porque tabela não existe no banco de testes (`exitusdb_test`).

**Solução:**
1. Aplicar migration no banco principal:
   ```bash
   alembic upgrade head
   ```

2. Aplicar migration no banco de testes:
   ```python
   # Criar app com testing=True
   app = create_app(testing=True)
   with app.app_context():
       alembic_cfg = Config('alembic.ini')
       alembic_cfg.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
       command.upgrade(alembic_cfg, 'head')
   ```

3. Ou aplicar manualmente via SQL se necessário:
   ```sql
   -- Criar tabela
   CREATE TABLE calendario_dividendo (...);
   -- Atualizar versão
   UPDATE alembic_version SET version_num = '20260310_1700';
   ```

**Resultado:** Testes passam de 1 failed para 490 passed.

---

## 📝 Documentação

### L-DOCS-001 — Documentação no mesmo commit (REGRA #6)
**Origem:** Planejamento Frontend | **Data:** 13/03/2026

**Problema:** Criar commits de código/documentação separados, violando REGRA #6 do `.windsurfrules`. Usuário precisa perguntar "e a documentação?".

**Solução:**
1. **Sempre** atualizar documentação no mesmo commit:
   - `CHANGELOG.md` - entrada com artefatos criados/modificados
   - `ROADMAP.md` - status atualizado para "Concluído (DD/MM/AAAA)"
   - `CODING_STANDARDS.md` - se introduz novo padrão de código
   - `ARCHITECTURE.md` - se adiciona componentes/endpoints
   - `OPERATIONS_RUNBOOK.md` - se adiciona scripts/procedimentos
   - `LESSONS_LEARNED.md` - se gera lição nova

2. **Fazer squash** se commits já foram criados separados:
   ```bash
   git reset --soft HEAD~N  # N = número de commits para juntar
   git add docs/CHANGELOG.md  # Adicionar documentação faltante
   git commit -m "feat: descrição completa com documentação"
   ```

3. **Antes de qualquer commit**, verificar: "Preciso atualizar algum doc?"

**Resultado:** Usuário nunca precisa perguntar sobre documentação - ela já vem junto.

---

## 🧪 Testes

### L-TEST-001 — Banco de testes precisa de schema sincronizado (MULTICLIENTE-001)
**Origem:** MULTI-CLIENTE-001 | **Data:** 19/03/2026

**Problema:** Banco de testes (`exitusdb_test`) com schema desatualizado, causando erro:
```
psycopg2.errors.UndefinedColumn: column "assessora_id" of relation "usuario" does not exist
```

**Causa:** Script `create_test_db.sh` usa `pg_dump --schema-only` do banco de produção, mas banco de testes não foi recriado após mudanças de schema.

**Solução:**
1. **Recriar banco de testes** após mudanças de schema:
   ```bash
   ./scripts/create_test_db.sh
   ```

2. **Verificar schema sincronizado**:
   ```bash
   # Produção
   podman exec exitus-db psql -U exitus -d exitusdb -c "\d usuario"
   
   # Testes (deve ser idêntico)
   podman exec exitus-db psql -U exitus -d exitusdb_test -c "\d usuario"
   ```

3. **Atualizar fixtures** para incluir assessora:
   ```python
   @pytest.fixture(scope='function')
   def assessora_seed(app):
       # Criar assessora padrão para testes
   
   @pytest.fixture(scope='function')
   def usuario_seed(app, assessora_seed):
       # Usuário com assessora_id
       u = Usuario(..., assessora_id=assessora_seed.id)
   ```

**Resultado:** 436/497 testes passando (87.7%) — +5 testes recuperados.

---

## �� Referências

| Documento | Papel |
|---|---|
| `docs/CODING_STANDARDS.md` | Padrões de código para humanos |
| `docs/ROADMAP.md` | GAPs registrados (ENUM-001, TESTDB-001) |
| `.windsurfrules` | Regras operacionais do Cascade (Windsurf) |
| `docs/EXITUS-SQLALCHEMY-001.md` | Padrões SQLAlchemy detalhados |
