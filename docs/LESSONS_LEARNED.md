# Lições Aprendidas — Sistema Exitus

> **Propósito:** Regras ativas derivadas de erros reais em produção/desenvolvimento.  
> Consultado pela IA **antes de qualquer ação** para evitar repetição de erros.  
> **Atualizado:** 03/04/2026 — L-SEC-001 adicionado (RLS vs API/JWT defesa em profundidade)  
> **Ver também:** `docs/CODING_STANDARDS.md`, `.codeium.rules`

---

## 🔐 Autenticação JWT

### L-AUTH-001 — SEMPRE usar `get_api_headers()` nas rotas Flask que chamam a API
**Origem:** Bug corretoras lista vazia | **Data:** 29/03/2026

```python
# ❌ ERRADO — token pode estar expirado, causa 401 silencioso
headers = {'Authorization': f"Bearer {session.get('access_token')}"}

# ✅ CORRETO — renova automaticamente via refresh token se expirado
from .auth import get_api_headers
headers = get_api_headers()
if not headers:
    return redirect(url_for('auth.login'))
```

**Regra:** `get_api_headers()` é a única função autorizada para construir headers de API nas rotas Flask do frontend. Ela verifica expiração, renova o token automaticamente com o refresh token e redireciona para login se não conseguir renovar.

**Arquivos onde deve ser usada:** Toda rota `@login_required` que faz chamada `requests.get/post` para o backend.

---

## � Segurança Multi-Tenant

### L-SEC-001 — RLS é Defesa em Profundidade, não substituto de API
**Origem:** Investigação de testes RLS falhando | **Data:** 03/04/2026

**Problema:** Testes de RLS via SQLAlchemy ORM não funcionam devido ao pool de conexões PostgreSQL.

**Arquitetura Correta:**
```
┌─────────────────────────────────────┐
│  Camada 1: API + JWT                │ ← Proteção principal
│  - before_request seta assessora_id │
│  - Endpoints validam permissões     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Camada 2: RLS no PostgreSQL        │ ← Proteção de backup
│  - Políticas no banco de dados      │
│  - Proteção contra bugs na API      │
└─────────────────────────────────────┘
```

**Por que RLS NÃO é redundante:**
1. **Proteção contra bugs:** Se desenvolvedor esquecer `filter_by_assessora()`
2. **Acesso direto ao banco:** Scripts, psql, pgAdmin, ferramentas BI
3. **Compliance:** Defesa em profundidade para auditorias (LGPD/GDPR)
4. **SQL Injection:** Limita dano ao tenant atual

**Decisão Arquitetural:**
- ✅ **MANTER RLS ATIVO** no banco (defesa em profundidade)
- ✅ **Validar isolamento via API** (como funciona em produção)
- ⏭️ **Testes RLS diretos = skip** (problema técnico, não funcionalidade)

**Regra:** RLS é camada adicional de segurança, nunca substituto da validação via API.

---

## �🗄️ Banco de Dados

### L-DB-001 — Usar DELETE, nunca DROP, para reset de dados
**Origem:** EXITUS-SEED-001 | **Data:** 02/03/2026

```python
# ❌ ERRADO — perde schema, constraints, índices, migrations
db.drop_all()
db.create_all()

# ✅ CORRETO — limpa dados, preserva estrutura
```

---

### L-FE-003 — Telas de Operação: sempre usar seletor de Tipo de Ativo com comportamento dinâmico
**Origem:** Ajuste tela compra para multi-tipo de ativo | **Data:** 29/03/2026

O sistema suporta 15 tipos de ativos em 4 mercados. Toda tela de operação (Compra, Venda) deve:

1. **Exibir seletor de Tipo antes do campo Ativo** — filtra a busca e define comportamento
2. **Campo Quantidade dinâmico** — baseado em `tipoAtualConfig.step`:
   - `step: '1'` → inteiro (Ações BR, FII, Renda Fixa)
   - `step: '0.000001'` → fração (Stocks, REITs, ETFs, Intl)
   - `step: '0.00000001'` → 8 decimais (Cripto)
3. **Moeda dinâmica** — R$ para mercado BR, $ para US/Intl/Cripto
4. **Busca filtrada por tipo** → `GET /api/ativos?search=TICKER&tipo=STOCK`

**Configuração padrão (copiar para novas telas):**
```javascript
tiposAtivo: [
    { key: 'ACAO',       label: 'Ação BR',    emoji: '🇧🇷', tipos: ['ACAO','UNIT'],                               fracao: false, moeda: 'R$', step: '1',          currency: 'BRL' },
    { key: 'FII',        label: 'FII',        emoji: '🏢', tipos: ['FII'],                                       fracao: false, moeda: 'R$', step: '1',          currency: 'BRL' },
    { key: 'RENDA_FIXA', label: 'Renda Fixa', emoji: '📄', tipos: ['CDB','LCI_LCA','TESOURO_DIRETO','DEBENTURE'], fracao: false, moeda: 'R$', step: '0.01',       currency: 'BRL' },
    { key: 'STOCK',      label: 'Stock EUA',  emoji: '🇺🇸', tipos: ['STOCK'],                                     fracao: true,  moeda: '$',  step: '0.000001',   currency: 'USD' },
    { key: 'REIT',       label: 'REIT',       emoji: '🏗️', tipos: ['REIT'],                                      fracao: true,  moeda: '$',  step: '0.000001',   currency: 'USD' },
    { key: 'ETF',        label: 'ETF',        emoji: '📊', tipos: ['ETF','ETF_INTL'],                            fracao: true,  moeda: '$',  step: '0.000001',   currency: 'USD' },
    { key: 'INTL',       label: 'Intl',       emoji: '🌍', tipos: ['STOCK_INTL','BOND'],                         fracao: true,  moeda: '$',  step: '0.000001',   currency: 'USD' },
    { key: 'CRIPTO',     label: 'Cripto',     emoji: '₿',  tipos: ['CRIPTO'],                                   fracao: true,  moeda: '$',  step: '0.00000001', currency: 'USD' },
]
```

---

### L-FE-004 — Telas de Operação: usar Toggle Compra/Venda unificado sempre que possível
**Origem:** Implementação toggle Compra/Venda | **Data:** 29/03/2026

Para evitar duplicação de telas e simplificar UX, prefira unificar Compra/Venda em uma única tela com toggle:

**Padrão Toggle:**
```html
<div class="toggle-container mb-6 max-w-md">
    <button @click="toggleModo('compra')" :class="isCompra ? 'toggle-btn active-compra' : 'toggle-btn inactive'">
        <i class="fas fa-cart-plus"></i> Compra
    </button>
    <button @click="toggleModo('venda')" :class="isVenda ? 'toggle-btn active-venda' : 'toggle-btn inactive'">
        <i class="fas fa-hand-holding-usd"></i> Venda
    </button>
</div>
```

**Seção Ativo Dual:**
- **Modo Compra:** Busca livre em `/api/ativos`
- **Modo Venda:** Lista apenas posições via `/api/posicoes`

**Validação de Venda:**
```html
<span x-show="isVenda && quantidadeMaxima > 0" class="max-qty-badge" @click="usarQuantidadeMaxima()">
    Máx: <strong x-text="quantidadeMaxima"></strong>
</span>
<input :max="isVenda && quantidadeMaxima > 0 ? quantidadeMaxima : undefined" />
```

**JavaScript - Estado e Métodos:**
```javascript
modoOperacao: 'compra',
posicoes: [],
quantidadeMaxima: 0,

get isCompra() { return this.modoOperacao === 'compra'; },
get isVenda() { return this.modoOperacao === 'venda'; },

toggleModo(modo) {
    this.modoOperacao = modo;
    this.form.tipo = modo;
    this.clearAtivo();
    if (modo === 'venda') this.fetchPosicoes();
}
```

**Regra:** Sempre que precisar de Compra/Venda do mesmo ativo, usar toggle em vez de telas separadas.

---

### L-FE-002 — SEMPRE usar máscara DD/MM/AAAA para campos de data
**Origem:** Ajuste tela compra formato americano | **Data:** 29/03/2026

```html
<!-- ❌ ERRADO — input type="date" mostra formato americano AAAA-MM-DD -->
<input type="date" x-model="form.data_transacao">

<!-- ✅ CORRETO — input type="text" com máscara DD/MM/AAAA -->
<input type="text" x-model="form.data_transacao_display" 
       @input="formatarDataInput($event)" 
       placeholder="DD/MM/AAAA" maxlength="10">
<input type="hidden" x-model="form.data_transacao_iso">
```

**Regra:** O sistema Exitus segue o **padrão Europeu**:
- Display: `DD/MM/AAAA` (ex: 29/03/2026)
- API: `YYYY-MM-DD` (ISO 8601)
- Valores monetários: `R$ 9.999,99` (ponto milhar, vírgula decimal)

**Implementação:** Sempre usar dois campos — um `type="text"` visível com máscara para o usuário, e um `type="hidden"` com valor ISO para envio à API.

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

### L-API-005 — POST /gerar sem persistência causa API vazia no refresh
**Origem:** EXITUS-UX-003 | **Data:** 25/03/2026

**Problema:** Endpoint `POST /calendario-dividendos/gerar` retornava dados corretos mas não persistia. Dashboard recebia lista vazia no refresh porque GET listava apenas itens persistidos.

```python
# ❌ ERRADO — gera mas não persiste
def gerar_calendario(usuario_id, meses_futuros=12):
    calendario = [...]
    return calendario  # 🪦 perdido no próximo refresh

# ✅ CORRETO — persiste com proteção contra duplicidade
def gerar_calendario(usuario_id, meses_futuros=12):
    calendario = [...]
    for item in calendario:
        existente = CalendarioDividendo.query.filter(
            and_(
                CalendarioDividendo.usuario_id == usuario_id,
                CalendarioDividendo.ativo_id == item.ativo_id,
                CalendarioDividendo.data_esperada == item.data_esperada,
                CalendarioDividendo.tipo_provento == item.tipo_provento,
            )
        ).first()
        if existente:
            existente.valor_estimado = item.valor_estimado
            existente.status = 'previsto'
        else:
            db.session.add(item)
    db.session.commit()
    return calendario_persistido
```

**Sintoma relacionado:** Frontend esperava `data.calendario` mas recebia `data` direto, causando undefined no Alpine.js.

---

## 🌐 Frontend Templates

### L-FE-004 — Token JWT expira durante navegação → 500 Internal Server Error
**Origem:** EXITUS-FRONTEND-001 | **Data:** 26/03/2026

```python
# ❌ ERRADO — Token fixo na sessão, sem renovação
headers = {'Authorization': f"Bearer {session.get('access_token')}"}
# API retorna 401 → dashboard_data vazio → template quebra

# ✅ CORRETO — Helper com refresh automático
def get_api_headers():
    if token_expirado_soon():
        new_token = refresh_token()
        session['access_token'] = new_token
    return {'Authorization': f'Bearer {new_token}'}
```

**Problema:** Token JWT expirava na sessão, API retornava 401, `dashboard_data` ficava vazio e template tentava acessar `dashboard.resumo.patrimonio_total`, gerando `jinja2.exceptions.UndefinedError`.

**Solução:**
- Implementar `get_api_headers()` com verificação de expiração
- Renovar token 5 minutos antes de expirar
- Tratar 401/403 com redirect para login
- Usar `.get()` com valores padrão nos templates

**Template defensivo:**
```jinja2
# ❌ ERRADO — Quebra se dashboard estiver vazio
R$ {{ "%.2f"|format(dashboard.resumo.patrimonio_total) }}

# ✅ CORRETO — Resiliente a dados ausentes
R$ {{ "%.2f"|format(dashboard.get('resumo', {}).get('patrimonio_total', 0)) }}
```

---

### L-FE-005 — TypeError: unhashable type: 'slice' em Jinja2
**Origem:** EXITUS-FRONTEND-001 | **Data:** 26/03/2026

```python
# ❌ ERRADO — Slice em template não funciona com todos tipos
{% for tx in transacoes[:10] %}  # TypeError se transacoes não for list

# ✅ CORRETO — Limitar no Python antes do template
transacoes = list(data)[:10] if data else []
{% for tx in transacoes %}
```

**Regra:** Sempre processar dados (slices, filtros) no Python, passar dados prontos para o template.

---

### L-BE-006 — Filtro assessora_id impede exibição de posições do usuário
**Origem:** EXITUS-DASHBOARD-002 | **Data:** 26/03/2026

```python
# ❌ ERRADO — Dashboard filtrando por assessora esconde posições do usuário
posicoes_usuario = Posicao.query.filter_by(usuario_id=usuario_id, assessora_id=assessora_id).all()
# Resultado: Dashboard mostra R$ 0,00 mesmo com 7 posições

# ✅ CORRETO — Dashboard mostra TODAS as posições do usuário
posicoes_usuario = Posicao.query.filter_by(usuario_id=usuario_id).all()
# Resultado: Dashboard exibe R$ 249.907,10 corretamente
```

**Problema:** Multi-tenancy com `assessora_id` é útil para isolamento de dados, mas no dashboard do usuário queremos exibir TODAS as posições independentemente da assessora vinculada.

**Solução:**
- Remover filtro `assessora_id` do método `get_dashboard()`
- Manter filtro em outras views onde isolamento é necessário
- Documentar regra: "Dashboard exibe todas as posições do usuário"

**Regra:** Dashboard do usuário = visão consolidada de todos os investimentos, não apenas por assessora.

---

## 🎨 Frontend

### L-FE-001 — Alpine.js + API REST para modernização de telas
**Origem:** SPRINT1-COMPRA | **Data:** 28/03/2026

```javascript
// ❌ PROBLEMA — Form tradicional sem API REST
<form method="POST" action="/operacoes/compra">
  <select name="ativo_id">
    <option value="{{ ativo.id }}">{{ ativo.ticker }}</option>
  </select>
</form>
// Resultado: Sem autocomplete, sem feedback, API não utilizada

// ✅ SOLUÇÃO — Alpine.js + API REST
<div x-data="compraForm()">
  <input x-model="searchTicker" @input.debounce.300ms="searchAtivos">
  <form @submit.prevent="submitCompra">
    <button :disabled="loading || !selectedAtivo">
      <span x-show="!loading">Confirmar</span>
      <span x-show="loading">⏳ Processando...</span>
    </button>
  </form>
</div>
```

**Problema:** Telas de frontend usavam forms tradicionais sem integração com APIs REST, resultando em UX estática e sem feedback visual.

**Solução:**
- Modernizar template existente com Alpine.js para reatividade
- Implementar autocomplete com API `/api/ativos?search=` e debounce (300ms)
- Converter POST tradicional para AJAX via `fetch()`
- Adicionar loading states e validações visuais
- Manter estrutura HTML existente (menos retrabalho)

**Resultado:** Tela de compra 100% API-Driven com UX moderna e performance otimizada.

**Aprendizado:** Alpine.js é ideal para modernizar telas existentes sem rewrite completo.

---

### L-BE-007 — Posições não são geradas automaticamente ao criar transações
**Origem:** EXITUS-POSITIONS-001 | **Data:** 26/03/2026

```python
# ❌ PROBLEMA — Criar transação não atualiza posições
transacao = Transacao(...)
db.session.add(transacao)
db.session.commit()
# Resultado: Dashboard continua zerado (posições não existem)

# ✅ SOLUÇÃO 1 — Hook automático no modelo
def save(self):
    """Salva transação e atualiza posições automaticamente"""
    db.session.add(self)
    db.session.commit()
    PosicaoService.calcular_posicoes(self.usuario_id)

# ✅ SOLUÇÃO 2 — Processamento no seed
def _processar_posicoes_apos_transacoes(self, transacoes_data):
    """Processa posições após criar transações"""
    for username in usuarios_unicos:
        resultado = PosicaoService.calcular_posicoes(usuario.id)
```

**Problema:** Sistema criava transações mas não gerava posições automaticamente, causando dashboard zerado mesmo após `reset_and_seed.py`.

**Solução Híbrida:**
1. **Hook no Modelo:** `Transacao.save()` atualiza posições automaticamente (operações do dia a dia)
2. **Seed Completo:** `reset_and_seed.py` processa posições após criar transações (carga inicial)

**Regra:** Toda transação deve gerar/atualizar posição correspondente automaticamente.

**Regra:** APIs de geração automática devem persistir resultados. Frontend deve consumir contrato exato da API. Testes devem validar persistência e contrato.

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
