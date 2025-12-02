# 📘 Exitus - Módulo 2: API REST CRUD

## Visão Geral

O Módulo 2 implementa a **API REST completa** do sistema Exitus, fornecendo endpoints CRUD para todas as entidades principais do sistema de controle de investimentos.

### Tecnologias Utilizadas

- **Framework**: Flask 3.0+
- **ORM**: SQLAlchemy 2.0+
- **Validação**: Marshmallow 3.20+
- **Autenticação**: Flask-JWT-Extended
- **Database**: PostgreSQL 15
- **Container**: Podman
- **Servidor**: Gunicorn

---

## 🏗️ Arquitetura

### Padrão MVC + Service Layer

```
backend/
├── app/
│   ├── models/          # SQLAlchemy Models (Entidades)
│   ├── schemas/         # Marshmallow Schemas (Validação)
│   ├── services/        # Business Logic
│   ├── blueprints/      # Flask Routes (Controllers)
│   │   ├── auth/
│   │   ├── usuarios/
│   │   ├── corretoras/
│   │   ├── ativos/
│   │   └── transacoes/
│   ├── utils/           # Helpers (responses, decorators)
│   ├── database.py      # SQLAlchemy setup
│   ├── config.py        # Configurações
│   └── __init__.py      # Application Factory
├── tests/               # Scripts de teste
├── run.py               # Entry point
└── requirements.txt
```

---

## 🔐 Fase 2.1 - Autenticação JWT

### Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/auth/login` | Login e geração de tokens | Público |
| `POST` | `/api/auth/refresh` | Renovar access token | Refresh Token |
| `GET` | `/api/auth/me` | Dados do usuário autenticado | JWT |
| `POST` | `/api/auth/logout` | Logout (invalidar token) | Refresh Token |

### Exemplo de Login

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao.silva",
    "password": "user123"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### Uso do Token

Incluir em todas as requisições autenticadas:
```bash
Authorization: Bearer <access_token>
```

---

## 👥 Fase 2.2.1 - CRUD Usuários

### Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/api/usuarios` | Listar usuários (paginado) | Admin |
| `GET` | `/api/usuarios/{id}` | Buscar usuário por ID | JWT (próprio ou Admin) |
| `POST` | `/api/usuarios` | Criar usuário | Público |
| `PUT` | `/api/usuarios/{id}` | Atualizar usuário | JWT (próprio ou Admin) |
| `DELETE` | `/api/usuarios/{id}` | Deletar usuário | Admin |
| `PATCH` | `/api/usuarios/{id}/password` | Trocar senha | JWT (próprio) |

### Model Usuario

```python
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = UUID
    username = String(50, unique=True)
    email = String(120, unique=True)
    password_hash = String(255)
    nome_completo = String(200)
    ativo = Boolean (default=True)
    role = Enum(UserRole)  # ADMIN, USER, READONLY
    created_at = DateTime
    updated_at = DateTime
```

### Exemplo de Criação

**Request:**
```bash
curl -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria.santos",
    "email": "maria@email.com",
    "password": "senha123",
    "nome_completo": "Maria Santos",
    "role": "user"
  }'
```

---

## 🏦 Fase 2.2.2 - CRUD Corretoras

### Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/api/corretoras` | Listar corretoras do usuário | JWT |
| `GET` | `/api/corretoras/{id}` | Buscar corretora por ID | JWT |
| `POST` | `/api/corretoras` | Criar corretora | JWT |
| `PUT` | `/api/corretoras/{id}` | Atualizar corretora | JWT |
| `DELETE` | `/api/corretoras/{id}` | Deletar corretora | JWT |
| `GET` | `/api/corretoras/saldo-total` | Saldo total do usuário | JWT |

### Model Corretora

```python
class Corretora(db.Model):
    __tablename__ = 'corretoras'

    id = UUID
    usuario_id = UUID (FK -> usuarios.id)
    nome = String(100)
    tipo = Enum(TipoCorretora)  # CORRETORA, EXCHANGE
    pais = String(2)  # BR, US, etc
    moeda_padrao = String(3)  # BRL, USD, EUR
    saldo_atual = Numeric(18, 2)
    ativa = Boolean
    observacoes = Text
    created_at = DateTime
    updated_at = DateTime
```

### Filtros Disponíveis

- `?page=1&per_page=20` - Paginação
- `?ativa=true` - Apenas corretoras ativas
- `?tipo=corretora` - Filtrar por tipo
- `?pais=BR` - Filtrar por país
- `?search=XP` - Busca textual

---

## 📈 Fase 2.2.3 - CRUD Ativos

### Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/api/ativos` | Listar ativos (paginado) | JWT |
| `GET` | `/api/ativos/{id}` | Buscar ativo por ID | JWT |
| `GET` | `/api/ativos/ticker/{ticker}` | Buscar por ticker | JWT |
| `POST` | `/api/ativos` | Criar ativo | Admin |
| `PUT` | `/api/ativos/{id}` | Atualizar ativo | Admin |
| `DELETE` | `/api/ativos/{id}` | Deletar ativo | Admin |
| `GET` | `/api/ativos/mercado/{mercado}` | Listar por mercado | JWT |

### Model Ativo

```python
class Ativo(db.Model):
    __tablename__ = 'ativos'

    id = UUID
    ticker = String(20)
    nome = String(200)
    tipo = Enum(TipoAtivo)  # ACAO, FII, REIT, BOND, ETF, CRIPTO
    classe = Enum(ClasseAtivo)  # RENDA_VARIAVEL, RENDA_FIXA, CRIPTO
    mercado = String(10)  # BR, US, EUR
    moeda = String(3)  # BRL, USD, EUR
    preco_atual = Numeric(18, 6)
    data_ultima_cotacao = DateTime
    dividend_yield = Numeric(8, 4)
    p_l = Numeric(10, 2)
    p_vp = Numeric(10, 2)
    roe = Numeric(8, 4)
    ativo = Boolean
    deslistado = Boolean
    data_deslistagem = Date
    observacoes = Text
    created_at = DateTime
    updated_at = DateTime
```

### Filtros Disponíveis

- `?page=1&per_page=20` - Paginação
- `?tipo=acao` - Filtrar por tipo (acao, fii, reit, etc)
- `?classe=renda_variavel` - Filtrar por classe
- `?mercado=BR` - Filtrar por mercado
- `?ativo=true` - Apenas ativos negociáveis
- `?deslistado=false` - Excluir deslistados
- `?search=PETR` - Busca textual (ticker ou nome)

### Exemplo de Busca por Ticker

**Request:**
```bash
curl -X GET "http://localhost:5000/api/ativos/ticker/PETR4?mercado=BR" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "success": true,
  "message": "Dados do ativo",
  "data": {
    "id": "d2f6e058-2a32-470f-bd55-3573ad397690",
    "ticker": "PETR4",
    "nome": "Petrobras PN",
    "tipo": "acao",
    "classe": "renda_variavel",
    "mercado": "BR",
    "moeda": "BRL",
    "preco_atual": "38.50",
    "ativo": true,
    "deslistado": false
  }
}
```

---

## 💼 Fase 2.2.4 - CRUD Transações

### Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/api/transacoes` | Listar transações do usuário | JWT |
| `GET` | `/api/transacoes/{id}` | Buscar transação por ID | JWT |
| `POST` | `/api/transacoes` | Criar transação | JWT |
| `PUT` | `/api/transacoes/{id}` | Atualizar transação | JWT |
| `DELETE` | `/api/transacoes/{id}` | Deletar transação | JWT |
| `GET` | `/api/transacoes/resumo/{ativo_id}` | Resumo por ativo | JWT |

### Model Transacao

```python
class Transacao(db.Model):
    __tablename__ = 'transacoes'

    id = UUID
    usuario_id = UUID (FK -> usuarios.id)
    ativo_id = UUID (FK -> ativos.id)
    corretora_id = UUID (FK -> corretoras.id)
    tipo = Enum(TipoTransacao)  # COMPRA, VENDA, DIVIDENDO, JCP, etc
    data_transacao = DateTime
    quantidade = Numeric(18, 8)
    preco_unitario = Numeric(18, 6)
    valor_total = Numeric(18, 2)  # quantidade * preco_unitario
    taxa_corretagem = Numeric(18, 2)
    emolumentos = Numeric(18, 2)
    taxa_liquidacao = Numeric(18, 2)
    imposto = Numeric(18, 2)
    outros_custos = Numeric(18, 2)
    custos_totais = Numeric(18, 2)  # soma de todas as taxas
    valor_liquido = Numeric(18, 2)  # valor_total +/- custos
    observacoes = Text
    created_at = DateTime
    updated_at = DateTime
```

### Cálculos Automáticos

O sistema calcula automaticamente:

1. **valor_total** = `quantidade × preco_unitario`
2. **custos_totais** = `taxa_corretagem + emolumentos + taxa_liquidacao + imposto + outros_custos`
3. **valor_liquido**:
   - COMPRA: `valor_total + custos_totais`
   - VENDA: `valor_total - custos_totais`
   - DIVIDENDO/JCP: `valor_total - imposto`

### Filtros Disponíveis

- `?page=1&per_page=20` - Paginação
- `?tipo=compra` - Filtrar por tipo
- `?ativo_id={uuid}` - Filtrar por ativo
- `?corretora_id={uuid}` - Filtrar por corretora
- `?data_inicio=2025-01-01T00:00:00` - Data início (ISO 8601)
- `?data_fim=2025-12-31T23:59:59` - Data fim (ISO 8601)

### Exemplo de Criação de Transação

**Request:**
```bash
curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "compra",
    "ativo_id": "d2f6e058-2a32-470f-bd55-3573ad397690",
    "corretora_id": "73f2032d-59de-4af5-a1e7-0087e1793bf8",
    "data_transacao": "2025-12-01T10:30:00",
    "quantidade": "100",
    "preco_unitario": "38.50",
    "taxa_corretagem": "10.00",
    "emolumentos": "2.50",
    "imposto": "0.50"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Transação criada com sucesso",
  "data": {
    "id": "0188f968-b063-4423-a348-8fd012d7f34f",
    "tipo": "compra",
    "ativo": {
      "id": "d2f6e058-2a32-470f-bd55-3573ad397690",
      "ticker": "PETR4",
      "nome": "Petrobras PN"
    },
    "corretora": {
      "id": "73f2032d-59de-4af5-a1e7-0087e1793bf8",
      "nome": "Clear Corretora"
    },
    "quantidade": "100.00000000",
    "preco_unitario": "38.500000",
    "valor_total": "3850.00",
    "custos_totais": "13.00",
    "valor_liquido": "3863.00",
    "data_transacao": "2025-12-01T10:30:00+00:00"
  }
}
```

### Resumo por Ativo

**Request:**
```bash
curl -X GET "http://localhost:5000/api/transacoes/resumo/{ativo_id}" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "success": true,
  "message": "Resumo do ativo",
  "data": {
    "quantidade_comprada": "100.00000000",
    "quantidade_vendida": "30.00000000",
    "quantidade_total": "70.00000000",
    "preco_medio": "38.65",
    "valor_investido": "3865.00",
    "valor_vendido": "1168.20"
  }
}
```

---

## 🔒 Segurança e Autenticação

### Roles (Perfis de Usuário)

- **ADMIN**: Acesso total ao sistema
- **USER**: Acesso aos próprios recursos
- **READONLY**: Apenas leitura

### Decorators de Autorização

```python
@jwt_required()  # Requer JWT válido
@admin_required  # Requer role ADMIN
@role_required(['ADMIN', 'USER'])  # Requer uma das roles
```

### Isolamento de Dados

- Cada usuário acessa apenas **seus próprios recursos**
- Corretoras, transações e posições são **filtradas por usuario_id**
- Admins podem acessar todos os recursos

---

## 📊 Padrão de Respostas

### Sucesso (2xx)

```json
{
  "success": true,
  "message": "Mensagem descritiva",
  "data": { ... }
}
```

### Erro (4xx / 5xx)

```json
{
  "success": false,
  "message": "Descrição do erro",
  "errors": { ... }  // Opcional (validação)
}
```

### Paginação

```json
{
  "success": true,
  "message": "Lista de recursos",
  "data": {
    "items": [ ... ],
    "total": 100,
    "pages": 5,
    "page": 1,
    "per_page": 20
  }
}
```

---

## 🧪 Testes

### Scripts de Teste Disponíveis

```bash
# Autenticação
./backend/tests/test_auth.sh

# Usuários
./backend/tests/test_usuarios_crud.sh

# Corretoras
./backend/tests/test_corretoras_crud.sh

# Ativos
./backend/tests/test_ativos_crud.sh

# Transações
./backend/tests/test_transacoes_crud.sh
```

### Executar Todos os Testes

```bash
for test in backend/tests/test_*.sh; do
  echo "Executando: $test"
  bash "$test"
  echo "---"
done
```

---

## 🚀 Deploy e Execução

### Iniciar Containers

```bash
./scripts/setup_containers.sh
```

### Rebuild Backend

```bash
cd backend && podman build -t exitus-backend:latest . && cd ..
```

### Popular Seeds

```bash
podman exec -it exitus-backend python -m app.seeds.seed_modulo2
```

### Verificar Status

```bash
podman ps
podman logs --tail 50 exitus-backend
```

### Health Check

```bash
curl http://localhost:5000/health
```

---

## 📦 Dependências Principais

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
marshmallow==3.20.1
marshmallow-sqlalchemy==1.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

## 📋 Checklist de Conclusão - Módulo 2

- [x] **2.1 - Autenticação JWT**
  - [x] Login com geração de tokens
  - [x] Refresh token
  - [x] Endpoint /me
  - [x] Decorators de autorização

- [x] **2.2.1 - CRUD Usuários**
  - [x] Model Usuario
  - [x] Schemas (Create, Update, Response)
  - [x] Service Layer
  - [x] Routes (6 endpoints)
  - [x] Testes completos

- [x] **2.2.2 - CRUD Corretoras**
  - [x] Model Corretora
  - [x] Schemas (Create, Update, Response)
  - [x] Service Layer
  - [x] Routes (6 endpoints)
  - [x] Filtros e paginação
  - [x] Testes completos

- [x] **2.2.3 - CRUD Ativos**
  - [x] Model Ativo
  - [x] Enums (TipoAtivo, ClasseAtivo)
  - [x] Schemas (Create, Update, Response)
  - [x] Service Layer
  - [x] Routes (7 endpoints)
  - [x] Busca por ticker
  - [x] Testes completos

- [x] **2.2.4 - CRUD Transações**
  - [x] Model Transacao
  - [x] Enum TipoTransacao
  - [x] Schemas (Create, Update, Response)
  - [x] Service Layer com cálculos automáticos
  - [x] Routes (6 endpoints)
  - [x] Filtros por tipo, ativo, corretora, período
  - [x] Endpoint de resumo por ativo
  - [x] Testes completos (15 cenários)

---

## 🎯 Próximos Passos

**Módulo 3 - Cálculos e Posições:**
- Cálculo automático de posições (holdings)
- Preço médio ponderado
- Lucro/Prejuízo realizado e não realizado
- Atualização de cotações em tempo real

---

## 📞 Suporte e Contato

- **Desenvolvedor**: Sistema Exitus
- **Data de Conclusão**: 02/12/2025
- **Versão**: 2.0.0
- **Status**: ✅ Produção-Ready

---

**Módulo 2 Completo! 🎉**
