# Lições Aprendidas — Sistema Exitus

> **Propósito:** Regras ativas derivadas de erros reais em produção/desenvolvimento.  
> Consultado pela IA **antes de qualquer ação** para evitar repetição de erros.  
> **Atualizado:** 29/06/2026 — L-OPS-001 adicionada (migração `.windsurfrules` → `.cursorrules`)
> **Atualizado:** 28/06/2026 — L-DB-015 adicionada (diretórios duplicados de migration — alembic/ vs migrations/)
> **Ver também:** `docs/CODING_STANDARDS.md`, `.codeium.rules`

---

## ⚙️ Backend

### L-BE-001 — Services devem usar exceções tipadas em vez de ValueError genérico
**Origem:** TECH-001 — 5 services | **Data:** 26/06/2026

**Erro:** Services `parametros_macro`, `rfcalc`, `cambio`, `ir`, `alerta` usavam `ValueError` genérico para todos os erros (não encontrado, duplicata, validação). Isso impede que o HTTP error handler mapeie corretamente para status codes semânticos (404, 409, 400, 422).

**Correto:** Usar exceções tipadas de `app/utils/exceptions.py`:
```python
from app.utils.exceptions import NotFoundError, ConflictError, ValidationError, BusinessRuleError

# Recurso não encontrado → 404
if not parametro:
    raise NotFoundError("Parâmetro não encontrado")

# Duplicata/conflito → 409
if existing:
    raise ConflictError(f"Parâmetros para {pais}/{mercado} já existem")

# Validação de entrada → 400
if preco_mercado <= 0:
    raise ValidationError("Preço de mercado deve ser positivo")

# Violação de regra de negócio → 422
if quantidade_insuficiente:
    raise BusinessRuleError("Quantidade insuficiente na posição")
```

**Regra:** Ao criar novo service ou modificar existente, sempre usar exceções tipadas. `ValueError` genérico só deve ser usado em casos extremos onde nenhuma exceção tipada se aplica (quase nunca). Testes unitários devem esperar a exceção tipada correta.

---

## 💾 Database

### L-DB-008 — Porta PostgreSQL
**Origem:** Auditoria Funcional | **Data:** 2026

**Erro:** Assumir porta 5432
**Correto:** Sempre usar 5433 (host) → 5432 (container)
**Impacto:** Perda de tempo em troubleshooting de conexão

**Regra:** Ao conectar ao PostgreSQL via Podman, sempre usar porta 5433 no host (mapeada para 5432 no container).

---

### L-DB-009 — Flask-Migrate vs ALTER Direto
**Origem:** Auditoria Funcional | **Data:** 2026

**Problema:** `flask db migrate` falha com erros de conexão
**Solução:** Usar ALTER TABLE direto via psql para mudanças simples
**Quando usar migrate:** Mudanças complexas com múltiplas tabelas

**Regra:** Para mudanças simples (adicionar coluna, constraint), usar ALTER TABLE direto via psql. Para mudanças complexas (múltiplas tabelas, renomear), usar Flask-Migrate.

---

### L-DB-010 — ENUMs Pré-requisitos
**Origem:** Auditoria Funcional | **Data:** 2026

**Erro:** Esquecer de criar ENUMs antes das tabelas
**Solução:** Sempre verificar/criar ENUMs antes de `db.create_all()`
**Checklist:** Verificar pg_enum antes de criar tabelas

**Regra:** Ao criar tabelas com ENUMs, sempre verificar se o ENUM existe no banco antes de criar a tabela. Usar `SELECT typname FROM pg_enum` para listar ENUMs existentes.

---

### L-DB-011 — Scripts de Seed vs. Schema Real
**Origem:** Auditoria Funcional | **Data:** 2026

**Erro:** Script `load_scenario.py` com ENUMs desatualizados
**Causa:** Schema evoluiu, script não foi atualizado
**Solução:** Validar scripts contra schema real antes de executar
**Verificação:** Comparar valores do JSON com limites do banco

**Regra:** Sempre validar scripts de seed contra schema real antes de executar. Comparar valores do JSON com limites do banco (ENUMs, precisão numeric, constraints).

---

### L-DB-012 — ENUMs Case Sensitive
**Origem:** Auditoria Funcional | **Data:** 2026

**Erro:** Usar `'DEPOSITO'` quando banco espera `'deposito'`
**Regra:** ENUMs PostgreSQL são case sensitive
**Solução:** Usar exatamente os valores do `unnest(enum_range())`

**Regra:** ENUMs PostgreSQL são case sensitive. Usar exatamente os valores retornados por `unnest(enum_range('nome_enum'))` para evitar erros.

---

### L-DB-013 — Precisão Numeric
**Origem:** Auditoria Funcional | **Data:** 2026

**Erro:** `dividend_yield: 15.2` em `numeric(5,4)` (máx: 9.9999)
**Impacto:** Overflow impede inserção
**Solução:** Validar precisão antes de carregar dados
**Checklist:** Verificar `numeric(precision, scale)` no schema

**Regra:** Validar precisão de campos `numeric(precision, scale)` antes de carregar dados. O valor máximo é `10^precision - 10^-scale`. Ex: `numeric(5,4)` máximo = 9.9999.

---

### L-DB-014 — Documentação Sincronizada
**Origem:** Auditoria Funcional | **Data:** 2026

**Regra:** Atualizar `EXITUS_DB_STRUCTURE.txt` SEMPRE após mudanças
**Comando:** `./scripts/update_db_structure.sh`
**Impacto:** Evita investigações repetitivas

**Regra:** Sempre que o banco de dados for alterado (nova tabela, migration, ALTER TABLE), executar `./scripts/update_db_structure.sh` para atualizar `docs/EXITUS_DB_STRUCTURE.txt`.

---

### L-DB-015 — Diretório de migrations ativo é migrations/, não alembic/
**Origem:** VALUATION-001 | **Data:** 28/06/2026

**Erro:** Migration criada em `backend/alembic/versions/` (Alembic standalone) em vez de `backend/migrations/versions/` (Flask-Migrate). O projeto usa Flask-Migrate (`flask db upgrade`), que lê apenas `migrations/`. A migration em `alembic/` não seria aplicada.

**Causa raiz:** Projeto começou com Alembic standalone e depois migrou para Flask-Migrate, mas o diretório `alembic/` nunca foi removido — dívida técnica que causa confusão.

**Correto:** Toda migration nova deve ser criada em `backend/migrations/versions/` com `down_revision` apontando para o head atual do Flask-Migrate (`flask db heads`).

**Comando para verificar head ativo:**
```bash
podman exec exitus-backend flask db heads
```

**Dívida técnica registrada:** CLEANUP-MIGRATIONS-001 (ROADMAP.md) — arquivar/remover `backend/alembic/` quando seguro.

---

## ��️ Frontend Jinja2

### L-FE-010 — Chave de config JS em base_interna.html deve espelhar exatamente a chave de Config
**Origem:** BUG-009 — `base_interna.html` | **Data:** 26/06/2026

**Erro:** `base_interna.html` usava `config.get("FRONTEND_API_URL", "http://localhost:5000")` — chave `FRONTEND_API_URL` não existe em `Config`. Resultado: todos os 25 templates _v2 ignoravam `Config.BACKEND_API_URL` e caíam sempre no fallback `http://localhost:5000`, quebrando qualquer ambiente diferente do dev local Podman.

**Correto:** A chave no `config.get()` do template **deve ser idêntica** à chave definida em `Config`:
```python
# Config (frontend/app/config.py)
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
```
```html
<!-- base_interna.html — correto -->
const API_BASE_URL = '{{ config.get("BACKEND_API_URL", "http://localhost:5000") }}';
```

**Regra:** Ao criar nova variável de config exposta ao JavaScript, sempre verificar o nome exato em `Config` antes de usar `config.get()` no template. Nomes errados não geram erro — apenas silenciosamente usam o fallback.

**Padrão complementar:** `base.html` deve sempre injetar `window.API_BASE_URL` para templates admin (que não estendem `base_interna.html`):
```html
window.API_BASE_URL = '{{ config.get("BROWSER_API_URL", "http://localhost:5000") }}';
```

---

### L-FE-012 — Bugs podem ser resolvidos indiretamente por correções de infraestrutura
**Origem:** BUG-014/015/017 — resolvidos por BUG-009v2 | **Data:** 27/06/2026

**Lição:** BUG-014 (busca por ticker no catálogo), BUG-015 (detalhe de ativo lento/sem dados) e BUG-017 (busca em Buy Signals) foram diagnosticados como bugs de UI/autocomplete. Na verdade, eram todos sintomas do mesmo problema de infraestrutura: `API_BASE_URL` nos templates apontava para `BACKEND_API_URL` (hostname interno `exitus-backend:5000`), que o browser não resolvia. Após a separação `BROWSER_API_URL` / `BACKEND_API_URL` (BUG-009v2), todas as chamadas `apiFetch()` do Alpine.js passaram a funcionar, resolvendo 3 bugs simultaneamente sem alteração de código de UI.

**Regra:** Antes de investigar um bug de UI como "autocomplete quebrado" ou "tela lenta", verificar:
1. O `API_BASE_URL` está acessível pelo browser? (abrir DevTools → Network — se houver `ERR_NAME_NOT_RESOLVED`, é problema de URL, não de UI)
2. A chamada `fetch()` retorna 200 ou erro de rede?
3. Outras telas que usam o mesmo padrão `apiFetch()` também estão afetadas?

Se múltiplas telas têm o mesmo sintoma, é provavelmente um problema de infraestrutura (URL, rede, CORS), não um bug individual de cada tela.

---

### L-FE-011 — URLs server-side vs client-side devem ser variáveis separadas
**Origem:** BUG-009v2 — Dashboard sem dados (ERR_NAME_NOT_RESOLVED) | **Data:** 27/06/2026

**Erro:** O frontend Flask roda dentro do container `exitus-frontend` e precisa de duas URLs distintas para o backend:
1. **Server-side** (container→container, rede podman): `http://exitus-backend:5000`
2. **Client-side** (browser→backend, rede host): `http://localhost:5000` (ou URL pública em produção)

Uma única variável `BACKEND_API_URL` não serve para os dois casos. Se apontar para `exitus-backend:5000`, o browser não resolve (ERR_NAME_NOT_RESOLVED). Se apontar para `localhost:5000`, chamadas server-side do container frontend falham.

**Correto:** Duas variáveis de ambiente separadas:
```python
# Config (frontend/app/config.py)
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')  # server-side
BROWSER_API_URL = os.getenv('BROWSER_API_URL', 'http://localhost:5000')  # client-side
```
```html
<!-- base_interna.html — client-side usa BROWSER_API_URL -->
const API_BASE_URL = '{{ config.get("BROWSER_API_URL", "http://localhost:5000") }}';
```
```python
# fiscal.py — server-side usa BACKEND_API_URL
requests.get(f"{Config.BACKEND_API_URL}/api/...")
```

**Regra:** Sempre separar URLs server-side (container→container) de client-side (browser→backend). Em produção (Railway/Render/Fly.io), cada uma aponta para endpoints diferentes (interno vs público). Ver `docs/ARCHITECTURE.md` → "Exemplos de Deploy — Configuração por Cenário".

---

### L-FE-009 — Migração de template para base_interna.html deve replicar padrão visual do sistema
**Origem:** Fase 7 — `operacoes_v2.html` | **Data:** 18/06/2026

**Erro:** Ao migrar template de `base.html` para `base_interna.html`, a IA replicou o CSS custom do original (hero header, classes `.btn-primary-exitus`, `.compra-card`, etc.) em vez de usar as classes do sistema (`exitus-components.css`).

**Consequência:** Visual inconsistente — tela de Operações ficou diferente de todas as outras telas migradas (Screener, Análises, Fiscal, Relatórios, Ativos).

**Correto:** Toda migração para `base_interna.html` DEVE:
1. Usar **exclusivamente** classes de `exitus-components.css` (`section-box`, `btn-exitus`, `kpi-bar`, `filter-bar`, etc.)
2. Referenciar variáveis CSS `--exitus-*` em vez de cores hardcoded
3. Verificar telas já migradas (ex: `screener_v2.html`) como referência visual antes de implementar
4. **Nunca** copiar CSS custom do template original — descartar e reescrever no padrão do sistema

---

### L-FE-008 — Ternário Jinja2 dentro de atributo HTML causa `TemplateSyntaxError`
**Origem:** Sprint 8 Comparador — select `selected` | **Data:** 09/06/2026

**Padrão com erro:**
```html
<option {% if a.ticker == tickers[i] if tickers|length > i else '' %}selected{% endif %}>
```

**Correto — extrair para `{% set %}` antes:**
```html
{% set sel = tickers[i] if tickers|length > i else '' %}
<option {% if a.ticker == sel %}selected{% endif %}>
```

**Regra:** Ternários Jinja2 (`X if COND else Y`) dentro de atributos HTML devem sempre ser extraídos para uma variável `{% set %}` antes.

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

## 🗄️ Banco de Dados

### L-DB-007 — Documentação de ENUM pode estar desatualizada vs banco real
**Origem:** Fluxo de caixa test_full.json | **Data:** 24/06/2026

**Erro:** JSON usava valores da documentação ENUMS.md (`DEPOSITO`, `SAQUE`, `IMPOSTO`) mas banco PostgreSQL só aceitava `aporte` e `resgate`.

**Investigação:**
```sql
-- Verificar valores reais no banco
SELECT DISTINCT tipo_movimentacao FROM movimentacao_caixa;
-- Resultado: apenas 'aporte' e 'resgate'

-- Testar valor da documentação
INSERT INTO movimentacao_caixa (tipo_movimentacao, ...) VALUES ('deposito', ...);
-- ERROR: invalid input value for enum tipomovimentacao: "deposito"
```

**Correto — Fluxo obrigatório antes de usar ENUMs:**
1. **Verificar realidade:** `SELECT DISTINCT coluna_enum FROM tabela`
2. **Testar valores:** Fazer INSERT de teste com cada valor
3. **Adaptar código:** Usar valores validados, não documentação
4. **Documentar:** Atualizar ENUMS.md se necessário

**Mapeamento aplicado:**
- `DEPOSITO` → `aporte` (entradas de dinheiro)
- `SAQUE` → `resgate` (saídas de dinheiro)
- `IMPOSTO` → `resgate` (pagamentos como saídas)
- `CREDITO_PROVENTO` → `aporte` (créditos como entradas)

**Regra:** **SEMPRE** verificar valores reais do ENUM no banco antes de usar em JSON/seeds. Documentação pode estar desatualizada.

---

### L-DB-008 — Banco de testes diverge do banco oficial após migrations
**Origem:** BUG-021 — enum `tipomovimentacao` | **Data:** 24/06/2026

**Erro:** Migration `20260624_1000` adicionou 5 novos valores ao enum `tipomovimentacao` no banco oficial (`exitusdb`). O banco de testes (`exitusdb_test`) não foi recriado após a migration, ficando com apenas 5 dos 10 valores. Resultado: 61 testes falhando por `invalid input value for enum`.

**Diagnóstico:**
```sql
-- Banco oficial: 10 valores
SELECT enumlabel FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
WHERE t.typname='tipomovimentacao';

-- Banco de testes: apenas 5 valores (divergência)
-- Causa: create_test_db.sh não foi executado após a migration
```

**Correto — Fluxo obrigatório após qualquer migration:**
1. Aplicar migration no banco oficial (`alembic upgrade head` ou DDL manual)
2. **Imediatamente** recriar o banco de testes: `./scripts/create_test_db.sh`
3. Validar paridade: `./scripts/check_db_parity.sh --strict`
4. Rodar suite: `podman exec exitus-backend python -m pytest tests/ -q --no-cov`

**Impacto desta falha:** 436/497 (87.7%) → resolvido para 538/566 (95.1%) após recriar banco de testes (+102 testes recuperados).

**Regra:** Toda migration aplicada no `exitusdb` **exige** recriação imediata do `exitusdb_test`. O `create_test_db.sh` agora executa automaticamente `check_db_parity.sh` para detectar divergências no final.

---

### L-TEST-001 — Fixture vs Seed Persistente: usar upsert, não INSERT puro
**Origem:** P4 — UniqueViolation em `test_buy_signals_endpoints.py` e `test_scenarios_example.py` | **Data:** 24/06/2026

**Erro:** Fixtures de teste faziam INSERT direto em entidades (Ativo, Assessora, Corretora) sem verificar existência prévia. Com o banco de testes populado por seed persistente (`test_e2e`), qualquer execução adicional gerava `UniqueViolation`.

**Causa raiz:** Fixtures assumiam banco vazio; seed é persistente entre sessões.

**Fix:**
1. Fixtures de entidades-mestre (Ativo, Assessora, Corretora, Usuário) → **upsert**: buscar por campo único antes de inserir
2. Fixtures de transações → **delete-then-insert**: deletar transações do usuário antes de recriar
3. Fixtures que testam campos de classificação (ex: `classificar_ativo`) → usar ticker que não existe no seed (ex: `PETX4`, não `PETR4`)
4. `load_scenario` → ler `request.node.callspec.params.get('scenario')` (não `request.param`) para capturar parâmetro do `@pytest.mark.parametrize` do teste

**Regra:** Qualquer fixture que insere entidades-mestre deve verificar existência prévia. Transações e proventos: limpar do usuário antes de recriar.

---

## 🛡️ Segurança Multi-Tenant

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

### L-FE-007 — Verificar nomes reais dos endpoints antes de planejar o sprint
**Origem:** Sprint 5 — `/api/ir/calculo-mensal` e `/api/ir/darfs-pendentes` planejados retornaram 404 | **Data:** 09/06/2026

Ao planejar um sprint, o `FRONTEND_IMPLEMENTATION_PLAN.md` pode ter nomes de endpoints desatualizados ou hipotéticos. **Sempre verificar** os endpoints reais do backend antes de implementar:

```bash
# ✅ CORRETO — validar endpoints reais ANTES de escrever o blueprint
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e_user","password":"e2e_senha_123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

# Checar status real
for ep in "ir/calculo-mensal" "ir/apuracao" "ir/darf" "ir/historico" "ir/dirpf"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" \
    "http://localhost:5000/api/$ep")
  echo "$STATUS  /api/$ep"
done
```

**Regra:** Sprint 5 mostrou que `/api/ir/apuracao`, `/api/ir/darf`, `/api/ir/historico` e `/api/ir/dirpf` eram os endpoints reais — os nomes planejados (`calculo-mensal`, `darfs-pendentes`) não existiam. Validar antes evita retrabalho.

---

### L-FE-006 — Quando a API backend não existe, criar stub informativo (não ignorar)
**Origem:** Sprint 4 — `GET /api/plano-venda` retorna 404 | **Data:** 09/06/2026

Quando um endpoint backend ainda não existe, a tela frontend **não deve** ser omitida nem gerar erro 500. Criar um stub com:
1. **Mensagem clara** ao usuário ("Em desenvolvimento")
2. **Código do endpoint** ausente visível (`/api/plano-venda`)
3. **Ações alternativas** (ir para tela correlata que funciona)
4. **Registro no FRONTEND_IMPLEMENTATION_PLAN.md** com ⚠️ e nota explicativa

```python
# ❌ ERRADO — omitir a rota ou deixar cair em erro 500
# (rota não registrada → menu quebrado)

# ✅ CORRETO — stub informativo com redirecionamento
@bp.route('/')
@login_required
def venda_lista():
    return render_template('planos/venda_lista.html')  # template com aviso
```

**Regra:** Toda rota do menu deve existir. Se a API não existe, a tela existe com stub. Nunca 404 no frontend.

---

### L-FE-005 — Sempre validar campos reais da API antes de mapear no blueprint
**Origem:** Sprint 2 — campo `quantidade` → `quantidade_ativos` | **Data:** 09/06/2026

Ao integrar uma API no frontend, nunca assumir nomes de campos pelo nome intuitivo. Sempre verificar a resposta real com curl antes de codificar o blueprint.

```bash
# Padrão de validação — executar antes de cada blueprint novo
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e_user","password":"e2e_senha_123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5000/api/ENDPOINT?per_page=1" \
  | python3 -c "import sys,json; p=json.load(sys.stdin)['data']['items'][0]; print(list(p.keys()))"
```

**Erros encontrados em Sprint 2 (proventos):**
- `quantidade` → nome real: `quantidade_ativos`
- `ticker` → nome real: `ativo.ticker` (objeto aninhado)
- `tipo` → nome real: `tipo_provento`

**Regra:** Usar `e2e_user` para validar campos reais antes de qualquer mapeamento de blueprint.

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

**Padrão correto (implementado parcialmente — TECH-001 pendente):**
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

**Fix planejado:** TECH-001 (ValueError residual em 5 services).

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

**Problema:** Criar commits de código/documentação separados, violando REGRA #6 do `.cursorrules`. Usuário precisa perguntar "e a documentação?".

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

## Operações / IA

### L-OPS-001 — Fonte única de regras: `.cursorrules` (não `.windsurfrules`)
**Origem:** CURSORRULES-001 — migração Cursor | **Data:** 29/06/2026

**Erro:** Dois arquivos de regras (`.cursorrules` e `.windsurfrules`) divergiam após migração Windsurf → Cursor. Métricas stale (567/574), paths MCP errados (`.windsurf/`), referências a Cascade/Windsurf.

**Correto:**
- **Fonte única:** `.cursorrules` na raiz (carregado automaticamente pelo Cursor)
- **Conteúdo extenso:** `docs/AI_OPERATIONS.md` (modelos IA, scripts, checklists)
- **`.windsurfrules`:** removido — não recriar

**Validação pós-mudança:**
```bash
test ! -f .windsurfrules && echo "OK: legado removido"
rg '\.windsurfrules' --glob '!docs/archive/**' --glob '!docs/CHANGELOG.md'
wc -l .cursorrules
```

---

### L-DB-009 — Alterações DDL devem ser aplicadas em AMBOS os bancos
**Origem:** CONSTRAINT-001 | **Data:** 25/06/2026

**Aplica-se APENAS a DDL (schema):** constraints, colunas, índices, enums, tabelas.
**NÃO se aplica a:** correções de bugs de aplicação (fix vai no código Python), dados de teste (DML/seeds).

**Erro:** CHECK constraints aplicadas em `exitusdb` via migration Alembic, mas `exitusdb_test` não foi atualizado. Os 13 testes de constraints continuaram falhando até aplicação manual via ALTER TABLE.

**Como aplicar DDL:**
- **exitusdb:** via migration Alembic (`flask db upgrade`) — criar `.py` em `migrations/versions/`
- **exitusdb_test:** via ALTER TABLE direto — `podman exec exitus-db psql -U exitus -d exitusdb_test -c "ALTER TABLE ..."`

**Consequência de ignorar:** Schema divergente entre produção e testes — falsos negativos difíceis de diagnosticar.

---

## �� Referências

| Documento | Papel |
|---|---|
| `docs/CODING_STANDARDS.md` | Padrões de código para humanos |
| `docs/ROADMAP.md` | GAPs registrados (ENUM-001, TESTDB-001) |
| `.cursorrules` | Regras inegociáveis do Cursor Agent (fonte única) |
| `docs/AI_OPERATIONS.md` | Manual operacional estendido (modelos IA, MCPs, scripts) |
| `docs/EXITUS-SQLALCHEMY-001.md` | Padrões SQLAlchemy detalhados |
