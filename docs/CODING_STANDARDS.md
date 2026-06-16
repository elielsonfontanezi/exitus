# Coding Standards - Sistema Exitus

## 🎯 **Naming Convention**
- **snake_case obrigatório** para todos os identificadores.
- Exemplos:
  | Tipo | Exemplo |
  |------|---------|
  | Tabelas | `historico_preco` |
  | Variáveis | `preco_medio` |
  | Arquivos | `portfolio_service.py` |

---

## 🐍 **Python/Flask Patterns**

### **Imports**
```python
# ✅ PADRÃO CORRETO
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional

from app.database import db
from app.models.ativo import Ativo, TipoAtivo, ClasseAtivo
```

### **Models - SQLAlchemy**
```python
# ✅ PADRÕES SEGUROS

# 1. Enums - SEMPRE validar antes de usar
if ticker.endswith(('11', '12', '13')):
    tipo_ativo = TipoAtivo.FII
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe!
else:
    tipo_ativo = TipoAtivo.ACAO
    classe_ativo = ClasseAtivo.RENDA_VARIAVEL  # ✅ Existe!

# 2. Constraints - SEMPRE validar antes de inserir
if valor_operacao == 0 or quantidade == 0:
    logger.warning(f"Registro com valor/quantidade zero ignorado")
    continue  # ✅ Pular em vez de tentar inserir

# 3. Session Management - PADRÃO SEGURO
try:
    db.session.add(objeto)
    db.session.commit()
except Exception as e:
    db.session.rollback()  # ✅ Limpar estado
    logger.error(f"Erro na operação: {e}")
    raise e

# 4. Flush vs Commit
db.session.add(objeto)
db.session.flush()  # ✅ Para obter ID sem commit final
# ... mais operações ...
db.session.commit()  # ✅ Commit final para persistir
```

### **Services**
```python
# ✅ PADRÃO DE SERVICE
class ImportService:
    def __init__(self):
        self.usuario_id = None
    
    def _validate_constraints(self, **kwargs):
        """Valida constraints comuns antes de inserir"""
        for field, value in kwargs.items():
            if 'quantidade' in field.lower() and value <= 0:
                raise ValueError(f"{field} deve ser positivo")
            if 'valor' in field.lower() and value <= 0:
                raise ValueError(f"{field} deve ser positivo")
    
    def safe_commit(self):
        """Commit seguro com rollback automático"""
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
```

---

## 🔧 **Database Patterns**

### **Migrations**
```python
# ✅ PADRÃO DE MIGRATION
def upgrade():
    # Criar enum primeiro
    op.execute("CREATE TYPE tipo_evento_custodia AS ENUM (...)")
    
    # Criar tabela
    op.create_table('evento_custodia', ...)
    
    # Criar índices
    op.create_index('ix_evento_custodia_tipo', 'evento_custodia', ['tipo'])
```

### **Queries**
```python
# ✅ QUERIES EFICIENTES
# Usar filter_by para campos diretos
ativo = Ativo.query.filter_by(ticker='PETR4').first()

# Usar filter para condições complexas
proventos = Provento.query.filter(
    Provento.data_pagamento >= data_inicio,
    Provento.tipo_provento == TipoProvento.DIVIDENDO
).all()

# ✅ MULTI-TENANT QUERIES (MULTICLIENTE-001)
from app.utils.tenant import filter_by_assessora

# Aplicar filtro de tenant em TODAS as queries
query = Transacao.query.filter_by(usuario_id=usuario_id)
query = filter_by_assessora(query, Transacao)
transacoes = query.all()
```

---

## 🚨 **Anti-Patterns (EVITAR)**

### **❌ NÃO FAZER**
```python
# ❌ Enums sem validar
classe_ativo = ClasseAtivo.ACAO  # AttributeError!

# ❌ Inserir sem validar constraints
provento.quantidade = 0  # CheckViolation!

# ❌ Session sem rollback
try:
    db.session.commit()
except:
    db.session.commit()  # PendingRollbackError!

# ❌ Flush sem commit
db.session.flush()  # Dados perdidos se der erro

# ❌ DROP TABLE para reset de dados (LIÇÃO APRENDIDA 02/03/2026)
db.drop_all()        # 😱 Destrói schema!
db.create_all()      # 😱 Recria do zero!
# → Perde constraints, índices, migrations
```

---

## 🎓 **Lições Aprendidas (Casos Reais)**

### **📋 LIÇÃO 002 - Sempre Verificar Tabelas Existentes (02/03/2026)**

**❌ Problema:** Deduzir nomes de tabelas sem verificar
```python
# ERRADO - causou erro em runtime
tables = ['movimentacao', 'transacao']  # movimentacao não existe!
```

**✅ Solução:** Sempre consultar o banco primeiro
```python
# CORRETO - verificar antes de usar
from sqlalchemy import inspect
tables = inspect(db.engine).get_table_names()
# → confirmar nomes reais antes de iterar
```

**📚 Regra de Ouro:** `"Nunca deduza nomes de tabelas. Sempre consulte o banco."`

**🔍 Impacto do Erro:**
- Um nome errado aborta **toda a transação** PostgreSQL
- Os DELETEs seguintes falham em cascata por `InFailedSqlTransaction`
- Runtime error difícil de debugar

---

### **📋 LIÇÃO 001 - DELETE vs DROP TABLE (02/03/2026)**

**❌ Problema:** Usar `DROP TABLE` para reset de dados
```python
# ERRADO - Destrutivo e desnecessário
db.drop_all()    # Perde schema inteiro
db.create_all()  # Recria do zero (arriscado)
```

**✅ Solução:** Usar `DELETE` para limpar apenas dados
```python
# CORRETO - Seguro e eficiente
db.session.execute(text("DELETE FROM usuario"))
db.session.execute(text("ALTER SEQUENCE usuario_id_seq RESTART WITH 1"))
```

**🎯 Por Que DELETE é Melhor:**
- **Preserva schema** (tabelas, constraints, índices)
- **Mantém migrations** intactas
- **Performance superior** (mais rápido)
- **Mais seguro** (não perde definições)
- **IDs controlados** (reset de sequences)

**📚 Contexto:**
- **Objetivo:** "Seed controlado" = limpar dados, não estrutura
- **Schema:** Gerenciado por Alembic migrations
- **Resultado:** Dados limpos, estrutura intacta

**🔍 Pergunta-Chave:** "O que realmente preciso resetar?"
- **Dados?** → DELETE ✅
- **Schema?** → DROP (raramente necessário) ⚠️

---

## 🚨 **Exceções Tipadas nos Services (CRUD-002)**

Nunca usar `ValueError` para sinalizar erros semânticos — o route não consegue distinguir 404 de 400.

```python
# ❌ ERRADO — ValueError vira 400 mesmo quando deveria ser 404 ou 409
def get_ativo(id):
    ativo = db.session.get(Ativo, id)
    if not ativo:
        raise ValueError("Ativo não encontrado")  # → route captura como 400

# ✅ CORRETO — exceções tipadas em app/utils/exceptions.py
from app.utils.exceptions import NotFoundError, ConflictError

def get_ativo(id):
    ativo = db.session.get(Ativo, id)
    if not ativo:
        raise NotFoundError("Ativo não encontrado")  # → route retorna 404

def criar_ativo(ticker):
    if Ativo.query.filter_by(ticker=ticker).first():
        raise ConflictError("Ticker já existe")  # → route retorna 409
```

**Hierarquia disponível em `app/utils/exceptions.py`:**

| Exceção | HTTP | Uso |
|---|---|---|
| `ExitusError` | base | Erro genérico do sistema |
| `NotFoundError` | 404 | Entidade não encontrada |
| `ConflictError` | 409 | Duplicidade / conflito |
| `ForbiddenError` | 403 | Sem permissão |
| `BusinessRuleError` | 422 | Regra de negócio violada |

**No route — capturar antes do `except Exception`:**
```python
from app.utils.exceptions import ExitusError

@bp.route('/<uuid:id>', methods=['DELETE'])
def delete_ativo(id):
    try:
        AtivoService.delete(id)
        return success({}, "Ativo removido")
    except ExitusError as e:          # ✅ Primeiro — retorna HTTP correto
        return e.to_response()
    except Exception as e:            # ✅ Último — fallback 500
        return error(str(e), 500)
```

---

## 🔍 **SQLAlchemy — `db.session.get()` obrigatório (SQLALCHEMY-002)**

`Model.query.get()` foi depreciado no SQLAlchemy 2.0 e removido no 2.1.

```python
# ❌ ERRADO — depreciado, emite SADeprecationWarning
ativo = Ativo.query.get(id)

# ✅ CORRETO — padrão SQLAlchemy 2.0
ativo = db.session.get(Ativo, id)
```

**Regra:** Em todo service ou decorator, usar sempre `db.session.get(Model, pk)`.  
`filter_by().first()` continua correto para buscas por campos não-PK.

---

## 🧪 **Padrões de Teste (pytest)**

### **Fixtures — sempre usar as globais do conftest.py**
```python
# ✅ CORRETO — fixture dinâmica, teardown garantido
def test_criar_ativo(auth_client, ativo_seed):
    response = auth_client.get(
        f'/api/ativos/ticker/{ativo_seed.ticker}',
        headers=auth_client._auth_headers,
    )
    assert response.status_code == 200

# ❌ ERRADO — fixture local com db.create_all/drop_all
@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as c:
        with app.app_context():
            db.create_all()   # ❌ destrói ENUMs PostgreSQL
        yield c
        with app.app_context():
            db.drop_all()     # ❌ destrói schema de teste
```

### **Dados — nunca hardcoded**
```python
# ❌ ERRADO — depende de dado do banco de produção
def test_ticker(auth_client):
    rv = auth_client.get('/api/ativos/ticker/PETR4')  # PETR4 só existe em prod!
    assert rv.status_code == 200

# ✅ CORRETO — dado criado pela fixture, independente de prod
def test_ticker(auth_client, ativo_seed):
    rv = auth_client.get(f'/api/ativos/ticker/{ativo_seed.ticker}')
    assert rv.status_code == 200
    assert rv.get_json()['data']['ticker'] == ativo_seed.ticker
```

### **Executar testes — sempre dentro do container**
```bash
# ✅ CORRETO
podman exec exitus-backend python -m pytest tests/ -q --no-cov

# ❌ ERRADO — ModuleNotFoundError no host
python -m pytest tests/
```

### **Recriar banco de teste**
```bash
# Após migrations ou schema corrompido
./scripts/create_test_db.sh

# Nunca usar db.create_all() — falha com ENUMs PostgreSQL (L-TEST-002)
```

### **Fixtures com setup/teardown inline — padrão _setup/_teardown (IR-005)**

Quando um teste precisa criar dados diretamente no banco (sem fixture de módulo),
usar o padrão helper `_setup() / _teardown()` com `decode_token` para garantir
que os dados pertencem ao mesmo usuário do `auth_client`:

```python
def _setup(self, app, auth_client, ...):
    from flask_jwt_extended import decode_token
    token = auth_client._auth_headers['Authorization'].split(' ')[1]
    with app.app_context():
        decoded = decode_token(token)
    usuario_id = decoded['sub']   # ✅ mesmo usuário do token JWT

    # criar objetos com usuario_id correto
    obj = Modelo(usuario_id=usuario_id, ...)
    db.session.add(obj)
    db.session.commit()
    return {'obj_id': obj.id}     # ✅ retornar IDs escalares, não objetos

def _teardown(self, ids):
    Modelo.query.filter_by(id=ids['obj_id']).delete()
    db.session.commit()

def test_algo(self, app, auth_client):
    ids = self._setup(app, auth_client, ...)
    try:
        rv = auth_client.get('/api/...', headers=auth_client._auth_headers)
        assert rv.status_code == 200
    finally:
        self._teardown(ids)        # ✅ teardown garantido mesmo com falha
```

**Regras:**
- Nunca buscar usuário por `query.filter(username.like(...))` em testes — usar `decode_token`
- Nunca acessar atributos de objetos ORM fora do bloco que os criou (ver L-TEST-003)
- Sempre retornar IDs escalares de `_setup()`, nunca objetos SQLAlchemy

---

### **Anti-patterns de teste**
```python
# ❌ Username hardcoded
response = client.post('/api/auth/login', json={'username': 'test_admin', ...})

# ❌ Valor hardcoded
assert float(data['preco_atual']) == 38.50

# ❌ assert sem status code
assert data['success'] is True  # pode mascarar 404/500

# ✅ Sempre verificar status primeiro
assert response.status_code == 200
assert response.get_json()['success'] is True
```

---

## 📋 **GAPs e Documentação**

### **Fluxo Obrigatório**
1. **Problema recorrente?** → Criar GAP
2. **Implementar solução** → Documentar
3. **Testar** → Validar
4. **Atualizar ROADMAP** → Status completo
5. **Fazer commit** → Com mudanças documentadas

### **Referências Obrigatórias**
- **[EXITUS-SQLALCHEMY-001.md](EXITUS-SQLALCHEMY-001.md)** - Padrões SQLAlchemy
- **[ROADMAP.md](ROADMAP.md)** - Status dos GAPs
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças

---

## 🔢 **ENUMs — Padrão Obrigatório (EXITUS-ENUM-001)**

### Definição de Enum Python
```python
# ✅ CORRETO — valores em snake_case lowercase
class TipoAtivo(enum.Enum):
    ACAO = "acao"
    FII  = "fii"
    CDB  = "cdb"

# ❌ ERRADO — valores UPPERCASE causam LookupError ao ler do banco lowercase
class TipoAtivo(enum.Enum):
    ACAO = "ACAO"
```

### Coluna SQLAlchemy — values_callable OBRIGATÓRIO
```python
# ✅ CORRETO — usa os .value do Enum (lowercase) no banco
tipo = Column(
    Enum(TipoAtivo, values_callable=lambda x: [e.value for e in x]),
    nullable=False
)

# ❌ ERRADO — SQLAlchemy usa os nomes dos membros (ACAO, FII) causando LookupError
tipo = Column(Enum(TipoAtivo), nullable=False)
```

### Migration de ENUM com dados existentes
```python
# ✅ Usar a função helper _rename_enum_values() — ver migration 20260304_2000
# A função preserva NOT NULL e converte dados existentes em 8 passos seguros.
# Nunca fazer DROP TYPE diretamente sem migrar os dados primeiro.
```

---

## � **Frontend — Padrões de Design Moderno (UX Evolution)**

### **Hero Section Padrão**
```html
<!-- ✅ PADRÃO OBRIGATÓRIO para todas as páginas -->
<section class="bg-gradient-hero rounded-3xl mx-6 mt-6 p-8 text-white shadow-large animate-fade-in relative overflow-hidden">
  <!-- Elementos Decorativos -->
  <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-32 translate-x-32"></div>
  <div class="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full blur-2xl translate-y-24 -translate-x-24"></div>
  
  <div class="relative z-10">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center animate-pulse-slow">
            <span class="text-3xl">[EMOJI]</span>
          </div>
          <div>
            <h1 class="text-5xl font-bold mb-2 bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              [TÍTULO]
            </h1>
            <p class="text-xl text-white/80">[DESCRIÇÃO]</p>
          </div>
        </div>
      </div>
      
      <div class="mt-8 lg:mt-0 lg:ml-8">
        <div class="flex flex-wrap gap-3">
          <!-- BOTÕES AQUI -->
        </div>
      </div>
    </div>
  </div>
</section>
```

### **Cards Modernos Padrão**
```html
<!-- ✅ PADRÃO OBRIGATÓRIO para cards de estatísticas -->
<div class="card-moderno p-6 animate-scale-in hover-lift group cursor-pointer">
  <div class="flex items-center justify-between mb-4">
    <div class="w-12 h-12 bg-[COR]-50 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
      <span class="text-2xl">[EMOJI]</span>
    </div>
    <div class="w-8 h-8 bg-[COR]-100 rounded-full flex items-center justify-center">
      <span class="text-[COR]-600 font-bold text-sm">[VALOR]</span>
    </div>
  </div>
  <div class="space-y-2">
    <p class="text-3xl font-bold text-gray-900">[VALOR PRINCIPAL]</p>
    <p class="text-sm text-gray-600">[DESCRIÇÃO]</p>
  </div>
</div>
```

### **Botões Padrão**
```html
<!-- ✅ BOTÃO PRIMÁRIO -->
<button class="btn-primario">
  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    [ÍCONE SVG]
  </svg>
  [TEXTO]
</button>

<!-- ✅ BOTÃO SECUNDÁRIO -->
<a href="[URL]" class="btn-secundario">
  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    [ÍCONE SVG]
  </svg>
  [TEXTO]
</a>
```

### **Emojis por Página (Obrigatório)**
| Página | Emoji | Cor |
|--------|-------|-----|
| Dashboard | 📊 | primary |
| Carteiras | 📁 | primary |
| Ativos | �🎯 | primary |
| Performance | 📈 | success |
| Movimentações | 💳 | primary |
| Alertas | 🔔 | warning |
| Relatórios | 📄 | primary |
| Imposto de Renda | 🧾 | danger |
| Educação | 🎓 | primary |
| Configurações | ⚙️ | gray |

### **Cores Semânticas**
- **primary:** azul principal
- **success:** verde para positivos
- **warning:** laranja para alertas
- **danger:** vermelho para negativos
- **purple:** roxo para especiais

### **Animações Padrão**
- **animate-fade-in:** para hero sections
- **animate-scale-in:** para cards
- **animate-delay-100/200/300:** delays progressivos
- **animate-pulse-slow:** para emojis principais
- **hover-lift:** elevação no hover
- **group-hover:scale-110:** escala nos ícones

---

## 🎯 **Regras de Ouro**

1. **🔍 SEMPRE validar** enums antes de usar
2. **🎨 USAR SEMPRE** hero section padrão em novas páginas
3. **📊 MANTER** consistência de emojis e cores
4. **⚡ APLICAR** animações com delays progressivos
5. **🔧 USAR** btn-primario/btn-secundario para ações principais
2. **✅ SEMPRE validar** constraints antes de inserir  
3. **🔄 SEMPRE fazer** rollback após erros
4. **📝 SEMPRE documentar** problemas recorrentes
5. **🚀 SEMPRE seguir** fluxo de GAPs

---

---

## 🔐 Padrão Obrigatório — Autenticação JWT no Frontend

### Regra: Toda rota Flask que chama a API backend deve usar `get_api_headers()`

```python
# ✅ PADRÃO OBRIGATÓRIO — frontend/app/routes/*.py
from .auth import login_required, get_api_headers

@bp.route('/minha-rota')
@login_required
def minha_rota():
    headers = get_api_headers()
    if not headers:
        return redirect(url_for('auth.login'))
    
    response = requests.get(f"{Config.BACKEND_API_URL}/api/...", headers=headers)
```

**Por que?**
- `session.get('access_token')` diretamente **ignora a expiração** do token
- `get_api_headers()` verifica expiração, tenta renovar silenciosamente via refresh token
- Se renovação falhar → redireciona para login (nunca silencia o erro)

### Configuração JWT (backend/app/config.py)
```python
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)   # Access token: 30 min
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)       # Refresh token: 7 dias
```

### Inatividade do usuário (frontend/templates/base.html)
- Timer de **15 minutos** de inatividade → modal "Sessão Expirada"
- Eventos que resetam o timer: `click`, `keypress`, `scroll`, `mousemove`, `touchstart`
- Verificação de sessão a cada **1 minuto** via `/auth/check-session`

---

## 🌍 Padrão Europeu — Datas e Valores Monetários

O sistema Exitus segue o **padrão Europeu** para formatação de datas e valores:

| Tipo | Formato | Exemplo |
|------|---------|---------|
| **Data** | DD/MM/AAAA | `29/03/2026` |
| **Data/Hora** | DD/MM/AAAA HH:MM:SS | `29/03/2026 14:30:00` |
| **Valor Monetário** | R$ 9.999,99 (ponto milhar, vírgula decimal) | `R$ 1.234,56` |
| **Percentual** | 99,99% (vírgula decimal) | `12,34%` |
| **Quantidade** | 9.999,99 (ponto milhar, vírgula decimal) | `1.000,50` |

### Implementação Frontend

```javascript
// Data para display (DD/MM/AAAA)
new Date().toLocaleDateString('pt-BR')  // "29/03/2026"

// Data para API (ISO 8601)
new Date().toISOString().split('T')[0]  // "2026-03-29"

// Valor monetário para display
new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
}).format(1234.56)  // "R$ 1.234,56"

// Valor percentual
new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 2
}).format(0.1234)  // "12,34%"
```

### Regras Obrigatórias

1. **Campos de input de data** devem usar máscara `DD/MM/AAAA` com `type="text"`
2. **Campos hidden** devem conter o valor em formato ISO para envio à API
3. **Display de valores** deve sempre usar `Intl.NumberFormat('pt-BR', ...)`
4. **API backend** sempre recebe e retorna datas em ISO 8601 (YYYY-MM-DD)

### Exceções

- Input `type="date"` nativo HTML5 deve ser evitado (mostra formato americano)
- Exportações para CSV/Excel devem usar formato local do usuário quando possível

---

*Adicionado: 29/03/2026*
