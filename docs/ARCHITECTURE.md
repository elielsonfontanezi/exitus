# Arquitetura - Sistema Exitus

## 📋 Índice

1. [Visão Arquitetural](#visão-arquitetural)
2. [Topologia de Containers](#topologia-de-containers)
3. [Stack Tecnológica Detalhada](#stack-tecnológica-detalhada)
4. [Coding Conventions](#coding-conventions)
5. [Modelo de Dados](#modelo-de-dados)
6. [Integrações Externas](#integrações-externas)
7. [Segurança](#segurança)
8. [Performance e Escalabilidade](#performance-e-escalabilidade)

---

## Visão Arquitetural

### Filosofia de Design

O Sistema Exitus foi arquitetado seguindo os princípios:

1. **Separação de Responsabilidades**: Backend, Frontend e Database em containers isolados
2. **Escalabilidade Independente**: Cada camada pode escalar sem afetar as outras
3. **Desenvolvimento Paralelo**: Times podem trabalhar simultaneamente em diferentes camadas
4. **Hot Reload Independente**: Mudanças em Frontend ou Backend não exigem rebuild completo
5. **Segurança por Camadas**: Database isolado, comunicação interna via rede bridge customizada
6. **Debugging Facilitado**: Logs individuais por container, troubleshooting granular
7. **Deploy Flexível**: Podman local → Cloud (Railway/Render/Fly.io) sem mudanças arquiteturais

### Princípios Fundamentais

- **Multi-Mercado**: Suporte nativo a Brasil, EUA, Europa, Ásia
- **Multi-Classe**: Ações, FIIs, REITs, Renda Fixa nacional e internacional
- **Multi-Corretora**: Abstração de caixa unificado, controle por corretora
- **Dados Near Real-Time**: Cotações com delay até 15 minutos (não HFT)
- **Transparência Operacional**: Logs auditáveis, rastreabilidade completa
- **Compliance por Design**: Regras fiscais configuráveis por jurisdição
- **Containerização Rootless**: Segurança adicional com Podman sem daemon root

---

## Topologia de Containers

### Visão Geral da Rede

```
┌───────────────────────────────────────────────────────────────┐
│                    HOST: Ubuntu 22.04 LTS                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         Podman Network: exitus-net (bridge)             │  │
│  │                                                         │  │
│  │  ┌──────────────────┐  ┌──────────────────┐             │  │
│  │  │  Container 1     │  │  Container 2     │             │  │
│  │  │  exitus-db       │  │  exitus-backend  │             │  │
│  │  │  PostgreSQL 16   │◄─┤  Flask API       │             │  │
│  │  │  :5432           │  │  :5000           │             │  │
│  │  └──────────────────┘  └────────▲─────────┘             │  │
│  │                                  │                      │  │
│  │                        ┌─────────┴─────────┐            │  │
│  │                        │  Container 3      │            │  │
│  │                        │  exitus-frontend  │            │  │
│  │                        │  Flask + HTMX     │            │  │
│  │                        │  :8080            │            │  │
│  │                        └───────────────────┘            │  │
│  │                                 │                       │  │
│  └─────────────────────────────────┼───────────────────────┘  │
│                                    │                          │
└────────────────────────────────────┼──────────────────────────┘
                                     │
                                     ▼
                          Browser: localhost:8080
```

### Container 1: PostgreSQL Database

**Imagem**: `docker.io/library/postgres:16`

**Função**: Armazenamento persistente de dados financeiros

**Especificações**:
```yaml
Nome: exitus-db
Porta: 5432 (exposta para host)
Volumes:
  - ./volumes/postgres:/var/lib/postgresql/data
Rede: exitus-net (bridge)
Timezone: America/Sao_Paulo
Encoding: UTF-8
Configurações:
  - max_connections: 100
  - shared_buffers: 256MB
  - effective_cache_size: 1GB
```

**Características**:
- Persistência via volume mapeado
- Backup automático configurável
- Migrations gerenciadas por Alembic
- 20 tabelas + 86+ índices otimizados

### Container 2: Flask Backend API

**Imagem**: Custom build (Python 3.11-slim base)

**Função**: API RESTful + Business Logic

**Especificações**:
```yaml
Nome: exitus-backend
Porta: 5000 (exposta para host)
Dependências:
  - Flask 3.0
  - SQLAlchemy 2.0
  - Alembic 1.13
  - pytest 7.4
  - python-dotenv 1.0
  - Flask-CORS 4.0
  - PyJWT 2.8
  - requests 2.31
Rede: exitus-net (bridge)
Gunicorn Workers: 4
User: non-root (exitus:1000)
Healthcheck: /health (30s interval)
```

**Características**:
- 16 blueprints registrados
- 67 rotas RESTful
- Autenticação JWT (1h expiry)
- Rate limiting configurável
- Logs estruturados (INFO/WARNING/ERROR)

### Container 3: Flask Frontend

**Imagem**: Custom build (Python 3.11-slim base)

**Função**: Renderização de Templates + Assets Estáticos

**Especificações**:
```yaml
Nome: exitus-frontend
Porta: 8080 (exposta para navegador)
Dependências:
  - Flask 3.0
  - Jinja2 3.1
  - python-dotenv 1.0
Assets Frontend:
  - HTMX 2.0 (via CDN)
  - Alpine.js 3.14 (via CDN)
  - TailwindCSS 3.4 (via CDN)
  - Chart.js 4.4 (via CDN)
Rede: exitus-net (bridge)
User: non-root (exitus:1000)
```

**Características**:
- 15 rotas principais
- 7+ templates Jinja2
- Session management (JWT)
- Fallback para mock data
- HTMX para updates parciais (sem reload)

### Comunicação Entre Containers

**Fluxo de Requisição Típica**:

1. **Browser** → `http://localhost:8080/dashboard` → **Container 3 (Frontend)**
2. **Frontend** renderiza template HTML com HTMX
3. **HTMX** faz requisição → `http://exitus-backend:5000/api/portfolio/dashboard`
4. **Backend** consulta PostgreSQL → `exitus-db:5432`
5. **Database** retorna resultados → **Backend**
6. **Backend** serializa JSON → **Frontend**
7. **HTMX** atualiza parcialmente a página (sem reload)

**Vantagens**:
- Latência interna mínima (rede bridge)
- Isolamento de segurança (DB não exposto ao frontend)
- Escalabilidade (cada camada pode ter múltiplas instâncias)

---

## Stack Tecnológica Detalhada

### Backend

| Componente | Versão | Função |
|------------|--------|--------|
| **Python** | 3.11 | Linguagem base |
| **Flask** | 3.0 | Framework web |
| **SQLAlchemy** | 2.0 | ORM (Object-Relational Mapping) |
| **Alembic** | 1.13 | Migrations de database |
| **PyJWT** | 2.8 | Autenticação JWT |
| **Flask-CORS** | 4.0 | Cross-Origin Resource Sharing |
| **Marshmallow** | 3.20 | Serialização/validação de schemas |
| **pytest** | 7.4 | Framework de testes |
| **Gunicorn** | 21.2 | WSGI server (production) |
| **requests** | 2.31 | HTTP client para APIs externas |

**Bibliotecas de Análise Financeira**:
- **pandas** 2.1 - Manipulação de séries temporais
- **numpy** 1.26 - Cálculos numéricos
- **yfinance** 0.2.33 - Cotações globais

### Frontend

| Componente | Versão | Função |
|------------|--------|--------|
| **HTMX** | 2.0 | Interatividade sem JavaScript complexo |
| **Alpine.js** | 3.14 | Reatividade leve (dropdowns, modals) |
| **TailwindCSS** | 3.4 | Framework CSS utility-first |
| **Chart.js** | 4.4 | Gráficos interativos |
| **Jinja2** | 3.1 | Template engine |

**Padrão de Arquitetura**:
- **Server-Side Rendering (SSR)** com Jinja2
- **Progressive Enhancement** com HTMX
- **Zero Build Step** (CDN para assets)

### Database

| Componente | Versão | Função |
|------------|--------|--------|
| **PostgreSQL** | 16 | RDBMS principal |
| **Extensions** | - | - |
| `uuid-ossp` | - | Geração de UUIDs |
| `pg_trgm` | - | Full-text search (futuro) |

**Otimizações**:
- Índices compostos em queries frequentes
- Foreign Keys com `ON DELETE CASCADE`
- Enums para tipos fixos (ClasseAtivo, TipoTransacao)
- Triggers para auditoria (planejado)

### Containerização

| Componente | Versão | Função |
|------------|--------|--------|
| **Podman** | 4.x | Container runtime (rootless) |
| **Podman Compose** | 1.0 | Orquestração multi-container |

**Vantagens do Podman**:
- Sem daemon root (segurança)
- Compatibilidade com Docker Compose
- Geração de Kubernetes manifests (futuro)

---

## Coding Conventions
Todo código segue snake_case (PEP 8 Python + PostgreSQL):
- Tabelas/colunas: `movimentacao_caixa`, `data_ultima_cotacao`
- Variáveis/funções: `get_portfolio_metrics()`
- Endpoints: `api/buy-signals/buy-score`


---

## Modelo de Dados

### Entidades Principais (20 Tabelas)

#### Core Tables

1. **usuario** - Usuários do sistema
   - `id` (UUID, PK)
   - `username`, `email` (unique)
   - `password_hash` (bcrypt)
   - `ativo` (boolean)
   - `created_at`, `updated_at`

2. **corretora** - Corretoras/brokers
   - `id` (UUID, PK)
   - `usuario_id` (FK → usuario)
   - `nome`, `cnpj`
   - `pais`, `moeda_padrao`
   - `saldo_caixa` (Decimal)

3. **ativo** - Ativos financeiros
   - `id` (UUID, PK)
   - `ticker` (unique, indexed)
   - `tipo` (Enum: ACAO, FII, REIT, RENDA_FIXA)
   - `mercado` (BR, US, EU, ASIA)
   - `preco_atual`, `dividend_yield`, `pl`
   - `data_ultima_cotacao`

#### Portfolio Tables

4. **posicao** - Holdings dos usuários
   - `id` (UUID, PK)
   - `usuario_id`, `ativo_id`, `corretora_id` (FKs)
   - `quantidade` (Decimal)
   - `preco_medio` (Decimal, calculado)
   - `custo_total` (Decimal)

5. **transacao** - Compras/Vendas
   - `id` (UUID, PK)
   - `usuario_id`, `ativo_id`, `corretora_id` (FKs)
   - `tipo` (COMPRA, VENDA)
   - `quantidade`, `preco_unitario`
   - `taxas`, `impostos`
   - `data_transacao`

6. **provento** - Dividendos/JCP
   - `id` (UUID, PK)
   - `ativo_id`, `usuario_id` (FKs)
   - `tipo` (DIVIDENDO, JCP, RENDIMENTO)
   - `valor_bruto`, `valor_liquido`
   - `data_pagamento`

#### Financial Operations

7. **movimentacao_caixa** - Depósitos/Saques
   - `id` (UUID, PK)
   - `corretora_id`, `usuario_id` (FKs)
   - `tipo` (DEPOSITO, SAQUE, TRANSFERENCIA)
   - `valor`, `moeda`
   - `data_movimentacao`

8. **evento_corporativo** - Splits, Bonificações
   - `id` (UUID, PK)
   - `ativo_id` (FK)
   - `tipo` (SPLIT, BONIFICACAO, FUSAO, SPINOFF)
   - `fator_ajuste`
   - `data_evento`

#### Reference Data

9. **feriado** - Calendário de mercado
   - `id` (UUID, PK)
   - `data`, `mercado` (BR, US, EU)
   - `descricao`

10. **fonte_dados** - APIs externas
    - `id` (UUID, PK)
    - `nome` (yfinance, brapi.dev, etc)
    - `prioridade`, `ativo`
    - `rate_limit_dia`, `rate_limit_minuto`

11. **regra_fiscal** - Impostos por país
    - `id` (UUID, PK)
    - `pais`, `tipo_ativo`
    - `aliquota_ir`, `incide_sobre`

#### Analytics Tables (M7)

12. **portfolio** - Carteiras customizadas
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `nome`, `descricao`
    - `created_at`

13. **alerta** - Sistema de alertas
    - `id` (UUID, PK)
    - `usuario_id`, `ativo_id` (FKs)
    - `tipo` (ALTA_PRECO, BAIXA_PRECO, DY_MINIMO)
    - `condicao_operador`, `condicao_valor`
    - `ativo` (boolean)

14. **relatorio** - Relatórios salvos
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `tipo` (PERFORMANCE, FISCAL, ALOCACAO)
    - `data_inicio`, `data_fim`
    - `sharpe_ratio`, `max_drawdown`

15. **projecao** - Projeções de renda
    - `id` (UUID, PK)
    - `portfolio_id` (FK)
    - `periodo`, `renda_estimada`
    - `created_at`

16. **historico_preco** - Histórico de preços (M7.6)
    - `id` (UUID, PK)
    - `ativo_id` (FK)
    - `data`, `preco_fechamento`
    - `volume`

#### Audit & System

17. **log_auditoria** - Rastreabilidade
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `acao`, `tabela_afetada`
    - `timestamp`

18. **parametro** - Configurações globais
    - `id` (UUID, PK)
    - `chave`, `valor`
    - `tipo` (STRING, INT, FLOAT, BOOL)

### Relacionamentos Chave

```
usuario (1) ─────> (N) corretora
usuario (1) ─────> (N) posicao
usuario (1) ─────> (N) transacao
usuario (1) ─────> (N) alerta
usuario (1) ─────> (N) portfolio

ativo (1) ─────> (N) posicao
ativo (1) ─────> (N) transacao
ativo (1) ─────> (N) provento
ativo (1) ─────> (N) evento_corporativo
ativo (1) ─────> (N) historico_preco

corretora (1) ─────> (N) posicao
corretora (1) ─────> (N) transacao
corretora (1) ─────> (N) movimentacao_caixa
```

### Índices e Performance

**Índices Críticos** (86+ total):
- `ativo.ticker` (UNIQUE, BTREE)
- `transacao(usuario_id, data_transacao DESC)`
- `posicao(usuario_id, ativo_id)` (UNIQUE)
- `provento(ativo_id, data_pagamento DESC)`
- `historico_preco(ativo_id, data DESC)`

**Otimizações Aplicadas**:
- Índices compostos em joins frequentes
- `ON DELETE CASCADE` em FKs (cleanup automático)
- Enums nativos do PostgreSQL (performance + validação)

---

## Integrações Externas

### APIs de Cotações (M7.5)

O sistema implementa **Multi-Provider Fallback** com 4 provedores + cache:

#### 1. brapi.dev (Primário - B3)

**Características**:
- **Tier**: FREE (10 req/min) | PREMIUM (60 req/min)
- **Mercados**: Brasil (B3)
- **Latência**: 0.25-5s
- **Rate Limit**: Tratado gracefully (429)

**Uso**:
```bash
GET https://brapi.dev/api/quote/PETR4?token=YOUR_TOKEN
```

#### 2. yfinance (Fallback 1 - Global)

**Características**:
- **Tier**: FREE (sem token)
- **Mercados**: Global (US, BR, EU, ASIA)
- **Latência**: 1-30s (cold start)
- **Rate Limit**: 429 após ~20 requests rápidas

**Uso**:
```python
import yfinance as yf
data = yf.Ticker("AAPL").info
```

#### 3. Alpha Vantage (Fallback 2 - US)

**Características**:
- **Tier**: FREE (500 req/dia)
- **Mercados**: US, principais índices
- **Latência**: 2-5s
- **Requer Token**: Sim

**Uso**:
```bash
GET https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY
```

#### 4. Finnhub (Fallback 3 - US/EU)

**Características**:
- **Tier**: FREE (60 req/min)
- **Mercados**: US, EU
- **Latência**: 2-5s
- **Token Opcional**: Sim (FREE tier suficiente)

#### 5. PostgreSQL Cache (Fallback Final)

**Características**:
- **TTL**: 15 minutos (conforme Prompt Mestre)
- **Update**: On-demand (sem polling/cron)
- **Latência**: 0.03-0.3s (query local)
- **Hit Rate**: 85-95% (uso normal)

### Estratégia de Fallback

```
Requisição → Cache PostgreSQL (15min)?
    ├─ HIT (85%) → Retorna 0.03-0.3s
    └─ MISS (15%) → Tenta Providers:
        ├─ 1. brapi.dev (B3) → OK? → Atualiza cache
        ├─ 2. yfinance (Global) → OK? → Atualiza cache
        ├─ 3. Alpha Vantage (US) → OK? → Atualiza cache
        ├─ 4. Finnhub (US/EU) → OK? → Atualiza cache
        └─ 5. Cache Local (fallback final) → Retorna último valor
```

**Vantagens**:
- **99.9% disponibilidade** (5 camadas de fallback)
- **Performance**: 85-95% requests em <0.3s (cache)
- **Zero downtime**: Funciona mesmo com todas APIs offline
- **Cost-effective**: FREE tiers suficientes para uso normal

---

## Segurança

### Autenticação e Autorização

#### JWT (JSON Web Tokens)

**Características**:
- **Algoritmo**: HS256
- **Expiry**: 1 hora (renovação automática planejada)
- **Claims**: `user_id`, `username`, `exp`, `iat`
- **Secret**: Variável de ambiente (`JWT_SECRET_KEY`)

**Fluxo**:
```
1. POST /api/auth/login → Token JWT
2. Headers: Authorization: Bearer <token>
3. Backend valida assinatura + expiry
4. Extrai user_id → Isolamento de dados
```

#### RBAC (Role-Based Access Control)

**Planejado para M8**:
- Roles: `admin`, `user`, `readonly`
- Permissions granulares por endpoint
- Middleware Flask-JWT-Extended

### Container Hardening

#### Non-Root User

**Dockerfile**:
```dockerfile
ARG APP_USER=exitus
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} ${APP_USER} &&     useradd -u ${APP_UID} -g ${APP_GID} -m ${APP_USER}

USER ${APP_USER}
```

**Verificação**:
```bash
podman exec -it exitus-backend whoami
# Output: exitus
```

#### Healthcheck Robusto

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3   CMD curl -f http://localhost:5000/health || exit 1
```

### Secrets Management

**Variáveis de Ambiente (.env)**:
```bash
# Database
POSTGRES_USER=exitus
POSTGRES_PASSWORD=<gerado_aleatoriamente>

# JWT
JWT_SECRET_KEY=<256_bits_random>

# APIs Externas
BRAPI_TOKEN=<seu_token>
ALPHAVANTAGE_TOKEN=<seu_token>
```

**Boas Práticas**:
- `.env` no `.gitignore`
- `.env.example` vazio (template)
- Nunca hardcoded no código
- Rotação periódica (planejada)

### Comunicação

**Interna (Containers)**:
- HTTP puro (rede isolada bridge)
- Sem exposição externa do PostgreSQL

**Externa (Produção - M8)**:
- HTTPS obrigatório (TLS 1.3)
- Certificados Let's Encrypt
- HSTS headers

---

## Performance e Escalabilidade

### Cache Strategy

#### 1. Database Query Cache

**SQLAlchemy**:
- Lazy loading de relacionamentos
- Eager loading (`joinedload`) em queries complexas
- Query result expiration (15min para cotações)

#### 2. Application-Level Cache

**PostgreSQL como Cache**:
- TTL 15 minutos (campo `data_ultima_cotacao`)
- Update on-demand (sem polling)
- Hit rate 85-95%

#### 3. HTTP Response Cache (Futuro - M8)

**Redis**:
- Cache de endpoints GET pesados
- Invalidação por eventos (webhook)
- TTL configurável por rota

### Database Optimization

**Configurações PostgreSQL**:
```ini
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

**Índices Estratégicos**:
- Cobertura de 95% das queries frequentes
- Análise com `EXPLAIN ANALYZE`
- Reindexação periódica (planejada)

### Gunicorn Workers

**Configuração**:
```bash
gunicorn --workers 4 --threads 2 --bind 0.0.0.0:5000 app:app
```

**Cálculo**:
- **Workers**: `(2 * CPU_CORES) + 1` = 4 (para dual-core)
- **Threads**: 2 (IO-bound predominante)
- **Concurrent Requests**: ~8-16

### Métricas de Performance

| Métrica | Valor | Observação |
|---------|-------|------------|
| **Response Time (Cache)** | 0.03-0.3s | PostgreSQL query |
| **Response Time (API)** | 0.25-5s | brapi.dev (cold start) |
| **Cache Hit Rate** | 85-95% | Uso horário comercial |
| **Concurrent Users** | 20-40 | Teste de stress |
| **Database Connections** | Max 100 | Pool SQLAlchemy |

### Escalabilidade Futura

**Horizontal Scaling (M8+)**:
- Load Balancer (Nginx/HAProxy)
- Múltiplas instâncias do backend
- Database read replicas
- Redis cluster

**Vertical Scaling**:
- Aumentar Gunicorn workers
- PostgreSQL shared_buffers
- CPU/RAM do host

---

## Deployment Architecture (M8 - Planejado)

### Desenvolvimento (Atual)

```
Local Machine (Ubuntu)
├── Podman (rootless)
├── 3 Containers
└── Volumes persistentes
```

### Produção (Planejado)

**Opção 1 - 3 Serviços Separados**:
```
Cloud Provider (Railway/Render/Fly.io)
├── PostgreSQL Gerenciado (Tier Free: 1GB)
├── Backend Service (Container)
└── Frontend Service (Container)
```

**Opção 2 - 2 Serviços (Free Tier Otimizado)**:
```
Cloud Provider
├── PostgreSQL Gerenciado
└── Flask Consolidado (API + Frontend)
```

**Providers Sugeridos**:
- **Railway**: $5/mês após trial
- **Render**: Free tier com sleep após 15min inatividade
- **Fly.io**: Free tier com limites generosos

---

## Referências

- [MODULES.md](MODULES.md) - Detalhes de cada módulo M0-M7
- [API_REFERENCE.md](API_REFERENCE.md) - Endpoints completos
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Deploy e troubleshooting

---

**Documento gerado**: 06 de Janeiro de 2026  
**Versão**: v0.7.6  
**Baseado em**: PROMPT_MESTRE_EXITUS_V10_FINAL + Estado real do sistema
