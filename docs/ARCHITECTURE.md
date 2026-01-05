
# 🏗️ Arquitetura Exitus v0.7.5 (M7 Complete)

**Data**: 05/Jan/2026 | **Branch**: `feature/docs-reestruturacao` | **Commit**: `d1bbfd9d`

## Stack Técnico

| Camada | Tecnologias Principais | Portas |
|--------|------------------------|--------|
| **Frontend** | Flask/Jinja2 + Tailwind CSS 3.4 + HTMX 1.9 + Alpine.js + Chart.js 4.4 | `:8080` |
| **Backend API** | Flask 3.x + SQLAlchemy 2.x + Marshmallow + JWT (PyJWT) + Alembic | `:5000` |
| **Banco** | PostgreSQL 15 + Índices (86) + FKs (15) + NUMERIC(15,2) moedas | `:5432` |
| **Infra** | Podman (3 containers) + Gunicorn 4 workers + Volumes persistentes | `exitus-net` |

**Containers ativos**:
```
exitus-db         postgres:15     Up 4+ days
exitus-backend    gunicorn        Up 2+ hours  0.0.0.0:5000->5000/tcp
exitus-frontend   gunicorn        Up 1+ hour   0.0.0.0:8080->8080/tcp
```

## Modelo de Dados (Entidades Centrais)

```mermaid
erDiagram
    usuario {
        string36 id PK
        string username
        string email
    }
    usuario ||--o{ portfolio : "gerencia"
    portfolio {
        string36 id PK
        string36 usuario_id FK
        string nome
    }
    portfolio ||--o{ posicao : "contém"
    posicao {
        string36 id PK
        string36 portfolio_id FK
        string36 ativo_id FK
        numeric quantidade
        numeric preco_medio
    }
    posicao }o--|| ativo : "refere"
    ativo {
        string36 id PK
        string ticker
        string mercado "B3/NASDAQ"
    }
    ativo ||--o{ transacao : "participa"
    transacao {
        string36 id PK
        string36 ativo_id FK
        string36 corretora_id FK
        enum tipo "COMPRA/VENDA"
        numeric valor_total
    }
    usuario ||--o{ alerta : "configura"
    alerta {
        string36 id PK
        string36 usuario_id FK
        enum tipo_alerta "alta_preco/queda_preco/..."
        boolean ativo
    }
    posicao ||--o{ provento : "recebe"
```

**Total**: 12+ entidades, 86 índices, 15 FKs, migrations Alembic completas.

## Camadas Backend (MVC Padrão Exitus)

```
REQUEST → Blueprint → Service → Model/DB → JSON Response
```

1. **Models** (`backend/app/models/`): SQLAlchemy declarativo, `tablename` explícito singular.
2. **Services** (`backend/app/services/`): Lógica de negócio (PortfolioService 8 métodos, AlertaService).
3. **Blueprints** (`backend/app/blueprints/`): 16+ registrados em `init.py` (portfolio, alertas, transacoes, relatorios).
4. **Schemas** (`backend/app/schemas/`): Marshmallow (snake_case enums, `joinedload` anti-N+1 queries).

## Fluxos Principais

### 1. Transação → Portfolio (M3/M4)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant FE as Frontend (:8080)
    participant BE as Backend API (:5000)
    participant S as Services
    participant DB as PostgreSQL

    U->>FE: POST /dashboard/transactions/new (PETR4 compra)
    FE->>BE: POST /api/transacoes {ativo_id, corretora_id, tipo='COMPRA'}
    BE->>S: PortfolioService.calcular_posicoes()
    S->>DB: INSERT transacao + UPDATE posicao (PM recalculado)
    Note over S,DB: NUMERIC(15,2) | joinedload(ativo, corretora)

    U->>FE: GET /dashboard/portfolios
    FE->>BE: GET /api/portfolios/dashboard?page=1
    BE->>S: PortfolioService.agregar_alocacao()
    S->>DB: SELECT portfolio, SUM(posicao.valor) GROUP BY classe
    DB->>S: {acoes:65%, fii:25%, renda_fixa:10%}
    S->>BE: JSON paginado
    BE->>FE: 200 OK
    FE->>U: Tabela + doughnut Chart.js
```

### 2. Alertas (M7.3)

```mermaid
sequenceDiagram
    U->>FE: POST /dashboard/alerts/new {ticker='PETR4', tipo='alta_preco', valor=35}
    FE->>BE: POST /api/alertas
    BE->>DB: INSERT alerta (ativo=true)
    Note over BE,DB: Frequência: imediata/diaria | Canais: webapp/email

    Note over BE: Futuro: Celery task verifica/preço >35 → WebSocket
```

### 3. Relatórios (M7.4)

```mermaid
sequenceDiagram
    U->>FE: POST /dashboard/reports/gerar {tipo='PERFORMANCE', data_inicio='2026-01-01'}
    FE->>BE: POST /api/relatorios/gerar
    BE->>S: RelatorioService.gerar_performance()
    S->>DB: PortfolioService + cálculos (Sharpe=1.45, drawdown=-8.3%)
    S->>BE: {resultado_json: {rentabilidade_bruta:'12.5%'} }
    BE->>DB: INSERT relatorio (id='247e5178...')
    BE->>FE: 201 Created
    FE->>U: Tabela atualizada (15+ itens)
```

## Módulos e Status (M0–M7.5)

| Módulo | Escopo Principal | Status | Endpoints Chave | Arquivos Principais |
|--------|------------------|--------|-----------------|---------------------|
| **M0** | Infra Podman/DB | ✅ | Health checks | `podman-compose.yml` |
| **M1** | Auth + CRUD base | ✅ | `/api/auth/login` | `auth_blueprint.py` |
| **M2** | API REST Core | ✅ | `/api/usuarios`, `/api/corretoras` | `usuario_model.py` |
| **M3** | Portfolio Analytics | ✅ | `/api/portfolios/dashboard` | `portfolio_service.py` |
| **M4** | Buy Signals + Fiscais | ✅ | `/api/buy-signals/buy-score/PETR4` | `buy_signals_blueprint.py` |
| **M5** | Frontend Base | ✅ | `/dashboard`, `/auth/*` | `base.html`, `dashboard.py` |
| **M6** | Dashboards (4 telas) | ✅ | `/dashboard/transactions` | `transactions.html` |
| **M7.3** | Alertas CRUD | ✅ | `/api/alertas`, `/dashboard/alerts` | `alerta_model.py` |
| **M7.4** | Relatórios | ✅ | `/api/relatorios/gerar` | `relatorios_blueprint.py` |
| **M7.5** | Cotações Live | ✅ | `/api/cotacoes/PETR4` | `cotacoes_service.py` |

## Decisões de Design Críticas

- **Moeda/DB**: `NUMERIC(15,2)` em vez de float (precisão fiscal BR/US).
- **Enums**: `snake_case` consistente após correções M4 (ex: `alta_preco`).
- **Performance**: `joinedload` em queries com relacionamentos (anti-N+1).
- **Fallback**: Frontend mock data se backend offline (não quebra UI).
- **Deploy**: Gunicorn `--workers 4 --preload`, healthchecks 30s, volumes `exitus-db-data`.
- **Serialização**: Marshmallow schemas explícitos, `unknown=EXCLUDE`.

## Pendências Arquiteturais (M8+)

- **Célery + Redis**: Verificação periódica alertas, background relatórios.
- **WebSocket**: Notificações real-time (Socket.IO).
- **Export PDF/Excel**: ReportLab/Pandas para `/api/relatorios/{id}/export`.
- **Cache**: Redis para cotações (TTL 15min, fallback DB).

---
**Geração**: Perplexity AI | **Base**: commit `d1bbfd9d` + histórico M0-M7 | **Próximo**: USER_GUIDE.md
