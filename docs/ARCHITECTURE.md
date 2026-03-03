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
- **Multi-Classe**: Ações, FIIs, REITs, Renda Fixa nacional e internacional, cripto e outros
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
- 21 tabelas + 86+ índices otimizados

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
Volumes:
  - ./backend:/app:Z
  - exitus-backend-logs:/app/logs:Z
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
Volumes:
  - ./frontend:/app:Z
  - exitus-frontend-logs:/app/logs:Z
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
- Enums para tipos fixos (`ClasseAtivo`, `TipoTransacao`, `TipoAtivo`, etc.)[file:5][file:18]
- Triggers para auditoria (planejado)

**Bancos de dados:**

| Nome | Uso | Criação |
|------|-----|---------|
| `exitusdb` | Produção/desenvolvimento | `setup_containers.sh` |
| `exitusdb_test` | Testes automatizados (pytest) | `scripts/create_test_db.sh` |

> `exitusdb_test` é criado via `pg_dump --schema-only` do `exitusdb` — garante paridade total de schema, ENUMs e constraints. Nunca usar `db.create_all()` para isso (L-TEST-002).

### Testes Automatizados

| Componente | Localização | Função |
|---|---|---|
| `pytest.ini` | `backend/pytest.ini` | Configuração: `cache_dir=/tmp/pytest_cache`, `addopts=-v --tb=short` |
| `conftest.py` | `backend/tests/conftest.py` | Fixtures globais: `app` (session), `client`, `auth_client`, `usuario_seed`, `ativo_seed`, `corretora_seed` |
| `TestingConfig` | `backend/app/config.py` | Aponta para `exitusdb_test`, JWT sem expiração, CSRF desabilitado |
| Testes unitários | `tests/test_business_rules.py` | 37 testes com mocks — `business_rules.py` |
| Testes integração | `tests/test_*_integration.py` | 59 testes contra PostgreSQL real (`exitusdb_test`) |
| Testes IR (EXITUS-IR-001) | `tests/test_ir_integration.py` | 19 testes — apuração, DARF, histórico |

**Estratégia de isolamento:**
- `app` fixture com escopo `session` — contexto Flask ativo durante toda a suite
- Fixtures de entidade com escopo `function` — criação com UUID único + DELETE no teardown
- Sem `db.drop_all()`/`db.create_all()` entre testes — apenas DELETE explícito
- Banco de teste recriável a qualquer momento via `./scripts/create_test_db.sh`
- **Suite total: 96 passed, 0 failed**

**Executar testes:**
```bash
# Suite completa (dentro do container — obrigatório)
podman exec exitus-backend python -m pytest tests/ -q --no-cov

# Recriar banco de teste antes de rodar (após migrations)
./scripts/create_test_db.sh && podman exec exitus-backend python -m pytest tests/ -q --no-cov
```

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

Todo código segue snake_case (PEP 8 Python + PostgreSQL):[file:24]

- Tabelas/colunas: `movimentacao_caixa`, `data_ultima_cotacao`
- Variáveis/funções: `get_portfolio_metrics()`
- Endpoints: `api/buy-signals/buy-score`

### Exceções Tipadas — `app/utils/exceptions.py` (CRUD-002)

Todos os services devem usar exceções tipadas em vez de `ValueError`. O handler genérico em `app/__init__.py` converte automaticamente para o HTTP correto.

| Exceção | HTTP | Quando usar |
|---|---|---|
| `NotFoundError` | 404 | Entidade não encontrada por ID/ticker |
| `ConflictError` | 409 | Duplicidade (ticker, username, etc.) |
| `ForbiddenError` | 403 | Sem permissão para a operação |
| `BusinessRuleError` | 422 | Regra de negócio violada |

```python
# Service — exceção tipada
from app.utils.exceptions import NotFoundError, ConflictError
raise NotFoundError("Ativo não encontrado")   # → 404
raise ConflictError("Ticker já existe")       # → 409

# Route — capturar ExitusError ANTES de Exception
from app.utils.exceptions import ExitusError
try:
    result = AtivoService.delete(id)
except ExitusError as e:
    return e.to_response()   # HTTP correto automático
except Exception as e:
    return error(str(e), 500)
```

### SQLAlchemy — `db.session.get()` obrigatório (SQLALCHEMY-002)

`Model.query.get()` foi depreciado no SQLAlchemy 2.0.

```python
# ❌ Depreciado
ativo = Ativo.query.get(id)

# ✅ Padrão atual
ativo = db.session.get(Ativo, id)
```

`filter_by().first()` continua correto para buscas por campos não-PK.

---

## Modelo de Dados

### Entidades Principais (21 Tabelas)

#### Core Tables

1. **usuario** - Usuários do sistema
   - `id` (UUID, PK)
   - `username`, `email` (unique)
   - `password_hash` (bcrypt)
   - `role` (Enum `UserRole`: `ADMIN`, `USER`, `READONLY`)
   - `ativo` (boolean)
   - `created_at`, `updated_at`

2. **corretora** - Corretoras/brokers
   - `id` (UUID, PK)
   - `usuario_id` (FK → usuario)
   - `nome`
   - `tipo` (Enum `TipoCorretora`: `CORRETORA`, `EXCHANGE`)
   - `pais` (ISO 3166-1 alpha-2, ex: BR, US)
   - `moeda_padrao` (ISO 4217, ex: BRL, USD, EUR)
   - `saldo_atual` (Decimal)
   - `ativa` (boolean)
   - `observacoes`

3. **ativo** - Ativos financeiros (cobertura global)[file:18][file:5]
   - `id` (UUID, PK)
   - `ticker` (VARCHAR(20), NOT NULL, INDEX)
   - `nome` (VARCHAR(200), NOT NULL, INDEX)
   - `tipo` (Enum `TipoAtivo`, 14 valores):
     - **Brasil (BR)**: `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
     - **Estados Unidos (US)**: `STOCK`, `REIT`, `BOND`, `ETF`
     - **Internacional (EU/ASIA)**: `STOCK_INTL`, `ETF_INTL`
     - **Outros**: `CRIPTO`, `OUTRO`
   - `classe` (Enum `ClasseAtivo`:
     - `RENDA_VARIAVEL`, `RENDA_FIXA`, `CRIPTO`, `COMMODITY`, `HIBRIDO`)
   - `mercado` (VARCHAR(10), NOT NULL, INDEX: `BR`, `US`, `EU`, `ASIA`, `GLOBAL`)
   - `moeda` (VARCHAR(3), NOT NULL, INDEX: `BRL`, `USD`, `EUR`, etc.)
   - `preco_atual` (NUMERIC, cotação atual)
   - `preco_teto` (NUMERIC, preço teto calculado)
   - `dividend_yield` (NUMERIC, 8,4)
   - `pl` (NUMERIC, 10,2)
   - `pvp` (NUMERIC, 10,2)
   - `roe` (NUMERIC, 8,4)
   - `beta` (NUMERIC, 8,4)
   - `cap_rate` (NUMERIC, 8,4, NULL) — **Cap Rate** para FIIs/REITs, usado em cálculos de valuation (migr. `202602162130`)
   - `data_ultima_cotacao` (TIMESTAMP WITH TIME ZONE)
   - `ativo` (boolean, default TRUE)
   - `deslistado` (boolean, default FALSE)
   - `data_deslistagem` (DATE, NULL)
   - `observacoes` (TEXT, NULL)
   - `created_at`, `updated_at`
   - **Constraints**:
     - `UNIQUE (ticker, mercado)` — ticker único por mercado
     - Check mínimo de tamanho de `ticker` e `nome`

#### Portfolio Tables

4. **posicao** - Holdings dos usuários
   - `id` (UUID, PK)
   - `usuario_id`, `ativo_id`, `corretora_id` (FKs)
   - `quantidade` (NUMERIC(18,8))
   - `preco_medio` (NUMERIC(18,6))
   - `custo_total` (NUMERIC(18,2))
   - `taxas_acumuladas` (NUMERIC(18,2))
   - `impostos_acumulados` (NUMERIC(18,2))
   - `valor_atual` (NUMERIC(18,2), join com `ativo.preco_atual`)
   - `lucro_prejuizo_realizado` (NUMERIC(18,2))
   - `lucro_prejuizo_nao_realizado` (NUMERIC(18,2))
   - `data_primeira_compra` (DATE)
   - `data_ultima_atualizacao` (TIMESTAMP)
   - `created_at`, `updated_at`

5. **transacao** - Compras/Vendas/Operações
   - `id` (UUID, PK)
   - `usuario_id`, `ativo_id`, `corretora_id` (FKs)
   - `tipo` (Enum `TipoTransacao`: `COMPRA`, `VENDA`, `DIVIDENDO`, `JCP`, `ALUGUEL`, etc.)
   - `quantidade`, `preco_unitario`
   - `valor_total`, `custos_totais`
   - `taxa_corretagem`, `emolumentos`, `taxa_liquidacao`, `imposto`
   - `data_transacao` (TIMESTAMP)

6. **provento** - Dividendos/JCP/Rendimentos
   - `id` (UUID, PK)
   - `ativo_id`, `usuario_id` (FKs)
   - `tipo_provento` (Enum `TipoProvento`: `DIVIDENDO`, `JCP`, `RENDIMENTO`, `CUPOM`, etc.)
   - `valor_por_acao`, `quantidade_ativos`
   - `valor_bruto`, `imposto_retido`, `valor_liquido`
   - `data_com`, `data_pagamento`
   - `created_at`, `updated_at`

#### Financial Operations

7. **movimentacao_caixa** - Depósitos/Saques
   - `id` (UUID, PK)
   - `corretora_id`, `usuario_id` (FKs)
   - `provento_id` (FK opcional)
   - `tipo_movimentacao` (Enum `TipoMovimentacao`: `DEPOSITO`, `SAQUE`, `TRANSFERENCIA`, `CREDITO_PROVENTO`, etc.)
   - `valor`, `moeda`
   - `data_movimentacao`
   - `descricao`, `comprovante`
   - `created_at`, `updated_at`

8. **evento_corporativo** - Splits, Bonificações
   - `id` (UUID, PK)
   - `ativo_id` (FK), `ativo_novo_id` (FK opcional)
   - `tipo_evento` (Enum `TipoEventoCorporativo`: `SPLIT`, `GRUPAMENTO`, `BONIFICACAO`, `FUSAO`, `SPINOFF`, etc.)
   - `data_evento`, `data_com`
   - `proporcao` (ex: 2:1, 10:1)
   - `descricao`
   - `impacto_posicoes` (boolean)
   - `observacoes`
   - `created_at`, `updated_at`

#### Reference Data

9. **feriado_mercado** - Calendário de mercado
   - `id` (UUID, PK)
   - `pais` (ISO 3166-1 alpha-2)
   - `mercado` (ex: `B3`, `NYSE`, `NASDAQ`, `EURONEXT`)
   - `data_feriado`
   - `tipo_feriado` (Enum `TipoFeriado`)
   - `nome`
   - `horario_fechamento` (opcional)
   - `recorrente` (boolean)
   - `observacoes`
   - `created_at`, `updated_at`

10. **fonte_dados** - APIs externas
    - `id` (UUID, PK)
    - `nome` (yfinance, brapi.dev, etc.)
    - `tipo_fonte` (Enum `TipoFonteDados`: `API`, `SCRAPER`, `MANUAL`, etc.)
    - `url_base`
    - `requer_autenticacao` (boolean)
    - `rate_limit`
    - `ativa` (boolean)
    - `prioridade` (int)
    - `ultima_consulta`, `total_consultas`, `total_erros`
    - `observacoes`
    - `created_at`, `updated_at`

11. **regra_fiscal** - Impostos por país
    - `id` (UUID, PK)
    - `pais` (ex: BR, US)
    - `tipo_ativo` (string, ex: `ACAO`, `FII`, `REIT`, etc.)
    - `tipo_operacao` (string, ex: `COMPRA`, `VENDA`, `DAYTRADE`)
    - `aliquota_ir` (NUMERIC(6,4))
    - `valor_isencao` (NUMERIC, opcional)
    - `incide_sobre` (Enum `IncidenciaImposto`: `LUCRO`, `RECEITA`, `PROVENTO`, `OPERACAO`)
    - `descricao`
    - `vigencia_inicio`, `vigencia_fim`
    - `ativa` (boolean)
    - `created_at`, `updated_at`

#### Analytics Tables (M7)

12. **portfolio** - Carteiras customizadas
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `nome`, `descricao`, `objetivo`
    - `ativo` (boolean)
    - `valor_inicial`, `percentual_alocacao_target`
    - `created_at`, `updated_at`

13. **alerta** / **configuracoes_alertas** - Sistema de alertas
    - `id` (UUID, PK)
    - `usuario_id`, `ativo_id`, `portfolio_id` (FKs)
    - `nome`
    - `tipo_alerta` (Enum `TipoAlerta`)
    - `condicao_operador` (Enum `OperadorCondicao`)
    - `condicao_valor`, `condicao_valor2`
    - `ativo` (boolean)
    - `frequencia_notificacao` (Enum `FrequenciaNotificacao`)
    - `canais_entrega` (ARRAY ou JSON)
    - `timestamp_criacao`, `timestamp_ultimo_acionamento`
    - `created_at`, `updated_at`

14. **relatorios_performance** / **auditoria_relatorio** - Relatórios salvos
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `tipo_relatorio` (Enum `TipoRelatorio`)
    - `data_inicio`, `data_fim`
    - `filtros` (JSON)
    - `resultado_json` (JSON)
    - `indice_sharpe`, `max_drawdown_percentual`
    - `formato_export` (Enum `FormatoExport`)
    - `timestamp_criacao`, `timestamp_download`
    - `created_at`, `updated_at`

15. **projecoes_renda** - Projeções de renda
    - `id` (UUID, PK)
    - `portfolio_id` (FK)
    - `periodo`
    - `renda_estimada`
    - `created_at`, `updated_at`

16. **historico_preco** - Histórico de preços (M7.6)[file:5]
    - `id` (UUID, PK)
    - `ativo_id` (FK → ativo)
    - `data`
    - `preco_abertura`, `preco_fechamento`, `preco_minimo`, `preco_maximo`
    - `volume`
    - `created_at`, `updated_at`
    - `UNIQUE (ativo_id, data)`

#### Audit & System

17. **log_auditoria** - Rastreabilidade
    - `id` (UUID, PK)
    - `usuario_id` (FK)
    - `acao`, `entidade`, `entidade_id`
    - `dados_antes`, `dados_depois` (JSON)
    - `ip_address`, `user_agent`
    - `timestamp`
    - `sucesso` (boolean)
    - `mensagem`

18. **parametros_macro** - Parâmetros macroeconômicos por país/mercado
    - `id` (UUID, PK)
    - `pais` (ex: BR, US, EU, JP)
    - `mercado` (ex: B3, NYSE, EURONEXT)
    - `taxa_livre_risco`
    - `crescimento_medio`
    - `custo_capital`
    - `inflacao_anual`
    - `cap_rate_fii` (cap rate médio por mercado)
    - `ytm_rf` (yield to maturity renda fixa)
    - `ativo` (boolean)
    - `created_at`, `updated_at`

19. **relatorios_performance** (já citado acima) — tabelas de métricas de performance agregadas.

20. **projecaorenda** / **relatoriosperformance** — tabelas auxiliares de analytics (detalhadas em `MODULES.md`).[file:10]

21. **outros metadados** (ex.: tabelas auxiliares futuras para monitoramento/parametrização).

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

### Expansão Multi-Mercado (v0.7.8)

A partir da versão **0.7.8**, o ENUM `TipoAtivo` foi expandido de 7 para **14 valores**, com suporte nativo a renda fixa BR e ativos internacionais.[file:18][file:28]

- **Brasil (6 tipos)**:
  - `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
- **Estados Unidos (4 tipos)**:
  - `STOCK`, `REIT`, `BOND`, `ETF`
- **Internacional (2 tipos)**:
  - `STOCK_INTL`, `ETF_INTL`
- **Outros (2 tipos)**:
  - `CRIPTO`, `OUTRO`

O campo **`cap_rate`** foi adicionado à tabela `ativo` para FIIs/REITs e outros ativos de renda imobiliária, permitindo cálculos mais precisos de Preço Teto e métricas de fluxo de caixa descontado.[file:18]

> Referência detalhada em: `ENUMS.md`.

### Índices e Performance

**Índices Críticos** (86+ total):[file:5]

- `ativo.(ticker, mercado)` (UNIQUE, BTREE) — ticker único por mercado
- `ativo.mercado`, `ativo.classe`, `ativo.tipo`
- `transacao(usuario_id, data_transacao DESC)`
- `posicao(usuario_id, ativo_id)` (UNIQUE)
- `provento(ativo_id, data_pagamento DESC)`
- `historico_preco(ativo_id, data DESC)`
- `configuracoes_alertas(usuario_id, tipo_alerta)`
- `feriado_mercado(pais, mercado, data_feriado)`

**Otimizações Aplicadas**:
- Índices compostos em joins frequentes
- `ON DELETE CASCADE` em FKs (cleanup automático)
- Enums nativos do PostgreSQL para todos os tipos fixos (`TipoAtivo`, `ClasseAtivo`, `TipoTransacao`, etc.)
- Constraints de integridade (checks de faixa, unicidade, datas válidas)

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
- **TTL**: 15 minutos (campo `data_ultima_cotacao`)
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

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -m ${APP_USER}

USER ${APP_USER}
```

**Verificação**:
```bash
podman exec -it exitus-backend whoami
# Output: exitus
```

#### Healthcheck Robusto

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
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
- Expiração de resultados conforme TTL de negócios (15 min para cotações)

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

---

## Sistema de Recovery (EXITUS-RECOVERY-001)

### Arquitetura Enterprise de Backup/Restore

**Componentes Principais**:
```yaml
Orquestrador: recovery_manager.sh (600+ linhas)
Validações: validate_recovery.sh (300+ linhas)
Rollback: rollback_recovery.sh (400+ linhas)
Interface: recovery_dashboard.sh (500+ linhas)
```

**Enterprise Features**:
- **Compressão gzip** automática de backups
- **Checksum SHA-256** para integridade
- **Metadados JSON** para rastreabilidade
- **Backup pré-operação** para rollback
- **Health checks** abrangentes
- **Interface TUI** amigável
- **Logs estruturados** em JSON

**Modos de Operação**:
```bash
# Backup
recovery_manager.sh backup --type=full|incremental|scheduled

# Restore
recovery_manager.sh restore --from=backup_20260301.sql --validate

# Reset
recovery_manager.sh reset --mode=full|minimal|custom

# Validate
validate_recovery.sh full|database|health|endpoints|consistency|performance

# Rollback
rollback_recovery.sh rollback --to=rollback_id
rollback_recovery.sh auto

# Dashboard
recovery_dashboard.sh  # Interface TUI completa
```

**Segurança e Robustez**:
- **Zero data loss** com backup pré-operação
- **Rollback automático** em caso de falha
- **Validação de checksums**
- **Recuperação automática**
- **Auditoria completa**

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
- [ENUMS.md](ENUMS.md) - Documentação completa de ENUMs

---

**Documento atualizado**: 03 de Março de 2026  
**Versão arquitetural**: v0.8.0-dev (Fase 2 concluída — 9 GAPs implementados, 56 ativos com dados fundamentalistas)
