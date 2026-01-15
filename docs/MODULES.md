# Módulos do Sistema Exitus (M0-M7)

## 📋 Índice

- [Visão Geral](#visão-geral)
- [M0 - Preparação do Ambiente](#m0---preparação-do-ambiente)
- [M1 - Database Schema](#m1---database-schema)
- [M2 - Backend API Core](#m2---backend-api-core)
- [M3 - Portfolio Analytics](#m3---portfolio-analytics)
- [M4 - Buy Signals & Cálculos Fiscais](#m4---buy-signals--cálculos-fiscais)
- [M5 - Frontend Base](#m5---frontend-base)
- [M6 - Dashboards Frontend](#m6---dashboards-frontend)
- [M7 - Relatórios e Análises](#m7---relatórios-e-análises)
- [Roadmap Futuro](#roadmap-futuro)

---

## Visão Geral

O Sistema Exitus foi desenvolvido em **8 módulos incrementais** (M0-M7), cada um entregando funcionalidades completas e testadas. Este documento detalha objetivos, status, componentes e métricas de cada módulo.

### Status dos Módulos

| Módulo | Nome | Status | Data Conclusão | Endpoints |
|--------|------|--------|----------------|-----------|
| **M0** | Infraestrutura | ✅ PROD | Nov 2025 | - |
| **M1** | Database Schema | ✅ PROD | Nov 2025 | - |
| **M2** | Backend API Core | ✅ PROD | Dez 2025 | 20 |
| **M3** | Portfolio Analytics | ✅ PROD | Dez 2025 | 11 |
| **M4** | Buy Signals & Fiscais | ✅ PROD | Dez 2025 | 12 |
| **M5** | Frontend Base | ✅ PROD | 04 Dez 2025 | 15 |
| **M6** | Dashboards Frontend | ✅ PROD | 06 Dez 2025 | 4 |
| **M7.3** | Alertas | ✅ PROD | Dez 2025 | 4 |
| **M7.4** | Relatórios | ✅ PROD | Jan 2026 | 5 |
| **M7.5** | Cotações Live | ✅ PROD | 09 Dez 2025 | 3 |
| **M7.6** | Histórico de Preços | ✅ PROD | 06 Jan 2026 | - |
| **M8** | Analytics Avançados | 📅 PLAN | Q2 2026 | - |
| **M9** | Deploy & Monitoramento | 📅 PLAN | Q1 2026 | - |

**Total de Endpoints**: **67 rotas** RESTful validadas

---

## M0 - Preparação do Ambiente

### Objetivo

Criar infraestrutura containerizada com Podman, configurar rede isolada e estabelecer ambiente de desenvolvimento local reproduzível.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Novembro 2025

### Componentes Implementados

#### 1. Instalação e Configuração do Podman

**Tecnologias**:
- Podman 4.x (rootless)
- Podman Compose 1.0
- Ubuntu 22.04 LTS

**Arquivos**:
```
scripts/
├── install_podman.sh          # Instalação do Podman
├── start_exitus.sh            # Iniciar todos os containers
├── stop_exitus.sh             # Parar todos os containers
├── restart_exitus.sh          # Restart completo
└── logs_exitus.sh             # Ver logs agregados
```

#### 2. Criação dos 3 Containers

**Container 1: exitus-db**
- Imagem: `postgres:16`
- Porta: 5432
- Volume: `./volumes/postgres`

**Container 2: exitus-backend**
- Imagem: Custom (Python 3.11)
- Porta: 5000
- Deps: Flask, SQLAlchemy, Alembic

**Container 3: exitus-frontend**
- Imagem: Custom (Python 3.11)
- Porta: 8080
- Deps: Flask, Jinja2, HTMX

#### 3. Rede Bridge Customizada

**Rede**: `exitus-net`
- Tipo: Bridge
- Isolamento: Containers não acessam host diretamente
- DNS: Resolução por nome (`exitus-db`, `exitus-backend`)

#### 4. Volumes Persistentes

```
volumes/
├── postgres/          # Dados do PostgreSQL
└── data/              # Backups e arquivos temporários
```

### Funcionalidades

- ✅ Iniciar/parar/restart sistema com 1 comando
- ✅ Logs individuais por container
- ✅ Hot reload (backend e frontend)
- ✅ Persistência de dados entre restarts
- ✅ Rede isolada para segurança
- ✅ Healthchecks automáticos

### Scripts Principais

```bash
# Iniciar sistema completo
./scripts/start_exitus.sh

# Ver status
podman ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}"

# Acessar container
podman exec -it exitus-backend bash

# Ver logs em tempo real
podman logs -f exitus-backend
```

---

## M1 - Database Schema

### Objetivo

Modelar e implementar schema PostgreSQL 16 otimizado para dados financeiros multi-mercado, com migrations gerenciadas por Alembic.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Novembro 2025

### Componentes Implementados

#### 1. Entidades Principais (20 Tabelas)

**Core**:
1. `usuario` - Usuários do sistema
2. `corretora` - Brokers/corretoras
3. `ativo` - Ativos financeiros (ações, FIIs, REITs)

**Portfolio**:
4. `posicao` - Holdings dos usuários
5. `transacao` - Compras/vendas
6. `provento` - Dividendos/JCP
7. `movimentacao_caixa` - Depósitos/saques

**Operations**:
8. `evento_corporativo` - Splits, bonificações
9. `feriado` - Calendário de mercado
10. `fonte_dados` - APIs externas
11. `regra_fiscal` - Impostos por país

**Analytics (M7)**:
12. `portfolio` - Carteiras customizadas
13. `alerta` - Sistema de alertas
14. `relatorio` - Relatórios salvos
15. `projecao` - Projeções de renda
16. `historico_preco` - Histórico de preços (M7.6)

**System**:
17. `log_auditoria` - Rastreabilidade
18. `parametro` - Configurações globais

#### 2. Migrations Alembic

**Arquivos**:
```
backend/migrations/versions/
├── 001_initial_schema.py          # 12 tabelas iniciais
├── 007_add_reports_and_alerts.py  # M7.3/M7.4
├── 008_add_historico_preco.py     # M7.6 (06 Jan 2026)
└── ... (8 migrations totais)
```

**Comandos**:
```bash
# Aplicar migrations
flask db upgrade

# Criar nova migration
flask db migrate -m "Descrição"

# Rollback
flask db downgrade
```

#### 3. Seeds de Dados Iniciais

**Arquivos**:
```
backend/app/seeds/
├── seed_usuarios.py      # 2 usuários (admin + user)
├── seed_corretoras.py    # 3 corretoras (Clear, XP, Avenue)
├── seed_ativos.py        # 17 ativos (BR + US)
├── seed_feriados.py      # Calendário BR/US 2025-2026
├── seed_regras_fiscais.py # IR BR (15% ações, 20% FII)
└── seed_all.sh           # Script para popular tudo
```

**Executar**:
```bash
podman exec -it exitus-backend bash
cd app/seeds
./seed_all.sh
```

### Índices e Otimizações

**86+ índices criados**:
- `ativo.ticker` (UNIQUE, BTREE)
- `transacao(usuario_id, data_transacao DESC)`
- `posicao(usuario_id, ativo_id)` (UNIQUE)
- `provento(ativo_id, data_pagamento DESC)`
- `historico_preco(ativo_id, data DESC)`

**Performance**:
- Queries complexas: <100ms
- Joins multi-tabela: <300ms
- Inserções em lote: 1000 rows/s

### Funcionalidades

- ✅ Schema completo para multi-mercado
- ✅ Suporte a Brasil, EUA, Europa, Ásia
- ✅ Múltiplas classes (ações, FIIs, REITs, renda fixa)
- ✅ Eventos corporativos (splits, bonificações)
- ✅ Auditoria (log_auditoria)
- ✅ Migrations versionadas
- ✅ Seeds para desenvolvimento

---

## M2 - Backend API Core

### Objetivo

Implementar API RESTful com autenticação JWT, CRUD base para entidades principais e estrutura de blueprints escalável.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Dezembro 2025

### Componentes Implementados

#### 1. Autenticação JWT

**Endpoints**:
- `POST /api/auth/login` - Login (retorna token)
- `POST /api/auth/register` - Registro de novo usuário

**Token JWT**:
- Algoritmo: HS256
- Expiry: 1 hora
- Claims: `user_id`, `username`, `exp`, `iat`

**Exemplo**:
```bash
curl -X POST http://localhost:5000/api/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"admin123"}'

# Response:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

#### 2. Blueprints Registrados (16 total)

**Core**:
1. `auth_bp` - Autenticação
2. `usuarios_bp` - Gestão de usuários
3. `corretoras_bp` - Gestão de corretoras
4. `ativos_bp` - Gestão de ativos

**Portfolio**:
5. `posicoes_bp` - Posições (holdings)
6. `transacoes_bp` - Transações
7. `proventos_bp` - Proventos
8. `movimentacoes_bp` - Movimentações de caixa

**Buy Signals & Fiscais (M4)**:
9. `feriados_bp` - Feriados
10. `fontes_bp` - Fontes de dados
11. `regras_fiscais_bp` - Regras fiscais
12. `calculos_bp` - Cálculos financeiros
13. `buy_signals_bp` - Sinais de compra

**Analytics (M7)**:
14. `alertas_bp` - Alertas
15. `relatorios_bp` - Relatórios
16. `cotacoes_bp` - Cotações live

#### 3. CRUD Base

**Padrão de Endpoints**:
```
GET    /api/{recurso}           # Listar (paginado)
GET    /api/{recurso}/{id}      # Detalhar
POST   /api/{recurso}           # Criar
PUT    /api/{recurso}/{id}      # Atualizar completo
PATCH  /api/{recurso}/{id}      # Atualizar parcial
DELETE /api/{recurso}/{id}      # Deletar
```

**Paginação Automática**:
```bash
GET /api/transacoes?page=1&per_page=10

# Response:
{
  "success": true,
  "data": [...],
  "total": 127,
  "pages": 13,
  "current_page": 1,
  "per_page": 10
}
```

#### 4. Validação e Serialização

**Marshmallow Schemas**:
```python
# app/schemas/transacao_schema.py
class TransacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transacao
        include_fk = True

    # Validações
    tipo = fields.String(required=True, validate=validate.OneOf(['COMPRA', 'VENDA']))
    quantidade = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    preco_unitario = fields.Decimal(required=True, validate=validate.Range(min=0.01))
```

### Funcionalidades

- ✅ 20 endpoints CRUD base
- ✅ Autenticação JWT obrigatória
- ✅ Isolamento de dados por usuário
- ✅ Paginação automática
- ✅ Validação com Marshmallow
- ✅ Rate limiting configurável
- ✅ CORS habilitado
- ✅ Logs estruturados

### Métricas

| Métrica | Valor |
|---------|-------|
| **Endpoints** | 20 |
| **Blueprints** | 16 |
| **Response Time** | 50-200ms |
| **Taxa de Sucesso** | 100% |

---

## M3 - Portfolio Analytics

### Objetivo

Implementar cálculos financeiros avançados, métricas de portfolio e APIs de análise de performance.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Dezembro 2025

### Componentes Implementados

#### 1. PortfolioService (8 métodos)

**Classe**: `app/services/portfolio_service.py`

**Métodos**:
1. `get_dashboard(usuario_id)` - Dashboard consolidado
2. `get_alocacao(usuario_id)` - Alocação por classe
3. `get_portfolio_metrics(usuario_id)` - Métricas avançadas
4. `get_distribuicao_classes(usuario_id)` - Distribuição percentual
5. `get_distribuicao_setores(usuario_id)` - Distribuição setorial
6. `get_evolucao_patrimonial(usuario_id, meses=12)` - Evolução temporal
7. `get_metricas_risco(usuario_id)` - Volatilidade, Sharpe, Drawdown
8. `get_performance_ativos(usuario_id)` - Performance individual

#### 2. Endpoints de Portfolio (11 total)

**Dashboard Consolidado**:
```bash
GET /api/portfolio/dashboard

# Response:
{
  "success": true,
  "data": {
    "patrimonioativos": 125430.50,
    "custoaquisicao": 100000.00,
    "saldocaixa": 5000.00,
    "patrimoniototal": 130430.50,
    "lucrobruto": 25430.50,
    "rentabilidadeperc": 25.43
  }
}
```

**Alocação por Classe**:
```bash
GET /api/portfolio/alocacao

# Response:
{
  "success": true,
  "data": {
    "rendavariavel": {"valor": 80000.00, "percentual": 63.8},
    "rendafixa": {"valor": 30000.00, "percentual": 23.9},
    "fii": {"valor": 15430.50, "percentual": 12.3}
  }
}
```

**Performance Individual**:
```bash
GET /api/portfolio/performance

# Response:
{
  "success": true,
  "data": {
    "total": 17,
    "ativos": [
      {
        "ticker": "PETR4",
        "quantidade": 100,
        "precomedio": 28.50,
        "precoatual": 31.46,
        "custototal": 2850.00,
        "valoratual": 3146.00,
        "lucro": 296.00,
        "rentabilidadeperc": 10.39
      },
      ...
    ]
  }
}
```

#### 3. Cálculos Implementados

**Indicadores Básicos**:
- Patrimônio Total
- Custo de Aquisição
- Lucro/Prejuízo Bruto
- Rentabilidade Percentual
- Dividend Yield Médio

**Métricas de Risco**:
- Volatilidade Anualizada
- Sharpe Ratio
- Max Drawdown
- Beta vs IBOV (planejado)

**Alocação**:
- Por Classe de Ativo
- Por Setor
- Por Mercado (BR/US/EU)
- Por Corretora

### Funcionalidades

- ✅ 11 endpoints de analytics
- ✅ Dashboard consolidado em tempo real
- ✅ Alocação multi-dimensional
- ✅ Performance individual por ativo
- ✅ Métricas de risco
- ✅ Evolução patrimonial (até 24 meses)
- ✅ Cálculo automático de preço médio
- ✅ Suporte a múltiplas moedas

### Métricas

| Métrica | Valor |
|---------|-------|
| **Endpoints** | 11 |
| **Métodos de Cálculo** | 8 |
| **Response Time** | 100-500ms |
| **Precisão** | 4 casas decimais |

---

## M4 - Buy Signals & Cálculos Fiscais

### Objetivo

Implementar análise fundamentalista com Buy Score (0-100), Preço Teto (4 métodos), Z-Score com histórico real e regras fiscais configuráveis.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: 15 Dezembro 2025

### Componentes Implementados

#### 1. Buy Score (0-100)

**Endpoint**: `GET /api/buy-signals/buy-score/{ticker}`

**Metodologia**:
- P/L (0-20 pontos)
- P/VP (0-20 pontos)
- Dividend Yield (0-20 pontos)
- ROE (0-20 pontos)
- Margem de Segurança (0-20 pontos)

**Exemplo**:
```bash
GET /api/buy-signals/buy-score/PETR4

# Response:
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "buyscore": 80,
    "recomendacao": "COMPRA",
    "precoteto": 34.39,
    "precoatual": 31.46,
    "margem_seguranca": 9.1
  }
}
```

**Escala**:
- **80-100**: COMPRA FORTE
- **60-79**: COMPRA
- **40-59**: NEUTRO
- **20-39**: VENDA
- **0-19**: VENDA FORTE

#### 2. Preço Teto (4 Métodos)

**Endpoint**: `GET /api/calculos/preco-teto/{ticker}`

**Métodos**:
1. **Bazin**: `(DY * 100) / 6`
2. **Graham**: `√(22.5 * VPA * LPA)`
3. **Gordon**: `Dividendo / (Taxa Desconto - Crescimento)`
4. **Preço Médio**: Média dos 3 métodos

**Exemplo**:
```bash
GET /api/calculos/preco-teto/PETR4

# Response:
{
  "ativo": "PETR4",
  "precoatual": 31.26,
  "precoteto": {
    "bazin": 35.50,
    "graham": 36.20,
    "gordon": 31.50,
    "medio": 34.39
  },
  "margemseguranca": 9.1,
  "sinal": "NEUTRO",
  "cor": "yellow"
}
```

#### 3. Z-Score com Histórico Real

**Endpoint**: `GET /api/buy-signals/zscore/{ticker}`

**Metodologia**:
```
Z-Score = (Preço Atual - Média 252 dias) / Desvio Padrão
```

**Integração**: Usa `historico_preco` table (M7.6)

**Exemplo**:
```bash
GET /api/buy-signals/zscore/PETR4

# Response:
{
  "ticker": "PETR4",
  "zscore": -1.35,
  "interpretacao": "SUBVALORIZADO",
  "preco_atual": 31.46,
  "media_252d": 34.80,
  "desvio_padrao": 2.48,
  "dias_historico": 252
}
```

**Interpretação**:
- **Z < -2**: Muito subvalorizado (oportunidade de compra)
- **-2 < Z < -1**: Subvalorizado
- **-1 < Z < 1**: Neutro (preço justo)
- **1 < Z < 2**: Sobrevalorizado
- **Z > 2**: Muito sobrevalorizado (oportunidade de venda)

#### 4. Regras Fiscais

**Endpoint**: `GET /api/regras-fiscais`

**Cadastro**:
```bash
POST /api/regras-fiscais
{
  "pais": "BR",
  "tipo_ativo": "ACAO",
  "aliquota_ir": 15.0,
  "incide_sobre": "GANHO_CAPITAL",
  "isento_ate": 20000.00
}
```

**Regras Atuais**:
- **BR - Ações**: 15% sobre ganho capital (isento até R$ 20k/mês)
- **BR - FII**: 20% sobre ganho capital (sem isenção)
- **US - Stocks**: 15% sobre dividendos (acordo BR-US)

### Funcionalidades

- ✅ Buy Score 0-100 (5 critérios)
- ✅ Preço Teto (4 métodos)
- ✅ Z-Score com histórico real (252 dias)
- ✅ Margem de Segurança automática
- ✅ Regras fiscais por país + tipo ativo
- ✅ Watchlist Top (planejado)
- ✅ Sinais coloridos (verde/amarelo/vermelho)

### Métricas

| Métrica | Valor |
|---------|-------|
| **Endpoints** | 12 |
| **Métodos de Cálculo** | 4 (Preço Teto) |
| **Histórico Z-Score** | 252 dias (1 ano trading) |
| **Regras Fiscais** | 6 cadastradas |
| **Response Time** | 50-200ms |

---

## M5 - Frontend Base

### Objetivo

Implementar frontend server-side rendering com Flask, Jinja2, HTMX e Alpine.js para interatividade sem JavaScript complexo.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: 04 Dezembro 2025

### Componentes Implementados

#### 1. Estrutura de Templates

**Base Layout**:
```
frontend/app/templates/
├── base.html                  # Layout mestre
├── auth/
│   ├── login.html            # Login
│   └── register.html         # Registro
├── dashboard/
│   └── index.html            # Dashboard principal
├── partials/
│   ├── navbar.html           # Barra de navegação
│   ├── sidebar.html          # Menu lateral
│   └── flash_messages.html   # Mensagens flash
└── components/
    ├── modal.html            # Modal genérico
    └── table.html            # Tabela paginada
```

#### 2. Rotas Frontend (15 total)

**Públicas (sem autenticação)**:
- `GET /` - Redirect para login
- `GET /auth/login` - Página de login
- `GET /auth/register` - Página de registro
- `POST /auth/login` - Processar login
- `POST /auth/register` - Processar registro

**Protegidas (requer JWT)**:
- `GET /dashboard` - Dashboard principal
- `GET /logout` - Logout (limpar session)

#### 3. HTMX + Alpine.js

**HTMX (Partial Updates)**:
```html
<!-- Exemplo: Atualizar tabela sem reload -->
<button 
  hx-get="/api/transacoes?page=2" 
  hx-target="#transacoes-table"
  hx-swap="innerHTML">
  Próxima Página
</button>
```

**Alpine.js (Interatividade)**:
```html
<!-- Exemplo: Dropdown -->
<div x-data="{ open: false }">
  <button @click="open = !open">Menu</button>
  <ul x-show="open" @click.away="open = false">
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</div>
```

#### 4. Session Management

**JWT em Session**:
```python
@app.route('/auth/login', methods=['POST'])
def login():
    # ... validação ...
    token = response_backend['data']['access_token']
    session['jwt_token'] = token
    session['username'] = username
    return redirect('/dashboard')
```

**Middleware de Autenticação**:
```python
@app.before_request
def check_auth():
    if request.endpoint not in ['login', 'register']:
        if 'jwt_token' not in session:
            return redirect('/auth/login')
```

### Funcionalidades

- ✅ 15 rotas frontend
- ✅ 7+ templates Jinja2
- ✅ HTMX para updates parciais
- ✅ Alpine.js para interatividade
- ✅ TailwindCSS (via CDN)
- ✅ Session management com JWT
- ✅ Flash messages (sucesso/erro)
- ✅ Navbar + Sidebar responsivos
- ✅ Logout funcional

### Métricas

| Métrica | Valor |
|---------|-------|
| **Rotas** | 15 |
| **Templates** | 7+ |
| **Response Time** | 50-150ms (SSR) |
| **Assets CDN** | HTMX, Alpine.js, Tailwind |

---

## M6 - Dashboards Frontend

### Objetivo

Criar 4 dashboards interativos com Chart.js, tabelas dinâmicas e integração completa com backend M3/M4.

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: 06 Dezembro 2025

### Componentes Implementados

#### 1. Dashboard Buy Signals

**Rota**: `GET /buy-signals`

**Componentes**:
- Tabela de ativos com Buy Score
- Gráfico de barras (Chart.js) - Top 10 scores
- Filtros: Mercado (BR/US), Score mínimo
- Botão "Atualizar Cotações" (HTMX)

**Screenshot**: Desktop + Mobile responsivo

#### 2. Dashboard Portfolios

**Rota**: `GET /portfolios`

**Componentes**:
- Cards com métricas principais (Patrimônio, Lucro, Rentabilidade%)
- Gráfico Pizza - Alocação por classe
- Tabela de posições (17 ativos)
- Modal "Nova Carteira" (Alpine.js)

**Integrações**:
- `GET /api/portfolio/dashboard` - Métricas
- `GET /api/portfolio/alocacao` - Gráfico pizza
- `GET /api/posicoes` - Tabela

#### 3. Dashboard Transações

**Rota**: `GET /transacoes`

**Componentes**:
- Tabela paginada (10 por página)
- 2 Gráficos (Chart.js):
  - Evolução do patrimônio (linha)
  - Transações por tipo (barras)
- Filtros: Data, Ticker, Tipo (COMPRA/VENDA)

#### 4. Dashboard Proventos

**Rota**: `GET /proventos`

**Componentes**:
- Tabela de proventos recebidos
- Gráfico de linha - Proventos mensais (12 meses)
- Total YTD (Year-to-Date)

### Gráficos Chart.js (5 total)

1. **Buy Score - Barras Horizontais**
2. **Alocação - Pizza/Donut**
3. **Evolução Patrimonial - Linha**
4. **Transações por Tipo - Barras**
5. **Proventos Mensais - Linha**

**Configuração Padrão**:
```javascript
new Chart(ctx, {
  type: 'bar',
  data: {...},
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Título' }
    }
  }
});
```

### Fallback Mock Data

**Quando backend offline**:
```javascript
// app/static/js/mock_data.js
const MOCK_PORTFOLIO = {
  patrimoniototal: 125430.50,
  lucrobruto: 25430.50,
  rentabilidadeperc: 25.43
};
```

**Uso**:
```javascript
fetch('/api/portfolio/dashboard')
  .then(res => res.json())
  .catch(() => MOCK_PORTFOLIO); // Fallback
```

### Funcionalidades

- ✅ 4 dashboards completos
- ✅ 5 gráficos Chart.js
- ✅ Tabelas paginadas e filtráveis
- ✅ Modal para criação de carteira
- ✅ Fallback mock data
- ✅ Responsivo (desktop + mobile)
- ✅ HTMX para updates parciais
- ✅ Alpine.js para dropdowns/modals

### Métricas

| Métrica | Valor |
|---------|-------|
| **Dashboards** | 4 |
| **Gráficos** | 5 |
| **Response Time** | 200-800ms (inclui gráficos) |
| **Screenshots** | 10 capturados |

---

## M7 - Relatórios e Análises

### M7.3 - Alertas

**Status**: ✅ PRODUCTION READY (Dez 2025)

**Endpoints** (4):
- `GET /api/alertas` - Listar alertas
- `POST /api/alertas` - Criar alerta
- `PATCH /api/alertas/{id}/toggle` - Ativar/desativar
- `DELETE /api/alertas/{id}` - Deletar

**Tipos de Alerta** (6):
1. Alta de Preço
2. Baixa de Preço
3. DY Mínimo
4. P/L Máximo
5. Volume Anormal
6. Margem de Segurança

**Exemplo**:
```bash
POST /api/alertas
{
  "nome": "PETR4 acima de R$ 35",
  "tipo_alerta": "ALTA_PRECO",
  "ticker": "PETR4",
  "condicao_operador": ">",
  "condicao_valor": 35.0
}
```

### M7.4 - Relatórios

**Status**: ✅ PRODUCTION READY (Jan 2026)

**Endpoints** (5):
- `GET /api/relatorios/lista` - Listar relatórios (paginado)
- `POST /api/relatorios/gerar` - Gerar novo relatório
- `GET /api/relatorios/{id}` - Detalhar relatório
- `POST /api/relatorios/{id}/exportar` - Exportar PDF (stub)
- `DELETE /api/relatorios/{id}` - Deletar

**Tipos de Relatório**:
1. **PERFORMANCE** - Rentabilidade, Sharpe Ratio, Drawdown
2. **FISCAL** - IR devido, transações tributáveis
3. **ALOCACAO** - Distribuição por classe/setor

**Exemplo**:
```bash
POST /api/relatorios/gerar
{
  "tipo": "PERFORMANCE",
  "data_inicio": "2026-01-01",
  "data_fim": "2026-01-31"
}

# Response:
{
  "id": "247e...",
  "tipo": "PERFORMANCE",
  "sharpe_ratio": 1.45,
  "max_drawdown": -12.3,
  "rentabilidade_periodo": 8.5
}
```

### M7.5 - Cotações Live

**Status**: ✅ PRODUCTION READY (09 Dez 2025)

**Endpoints** (3):
- `GET /api/cotacoes/{ticker}` - Cotação individual
- `GET /api/cotacoes/batch?tickers=A,B,C` - Lote
- `GET /api/cotacoes/health` - Status do módulo

**Providers** (5):
1. brapi.dev (primário - B3)
2. yfinance (fallback 1 - global)
3. Alpha Vantage (fallback 2 - US)
4. Finnhub (fallback 3 - US/EU)
5. PostgreSQL Cache (fallback final)

**Cache**:
- TTL: 15 minutos
- Hit Rate: 85-95%
- Response Time: 0.03-0.3s (cache) | 0.25-5s (API)

**Exemplo**:
```bash
GET /api/cotacoes/PETR4

# Response (cache hit):
{
  "ticker": "PETR4",
  "precoatual": 31.46,
  "variacaopercentual": -0.632,
  "provider": "cache-postgresql",
  "cacheageminutes": 5,
  "success": true
}
```

### M7.6 - Histórico de Preços

**Status**: ✅ PRODUCTION READY (06 Jan 2026)

**Componentes**:
- Tabela `historico_preco`
- Service com lazy loading
- Script `popular_historico_inicial.py`
- Integração com Z-Score

**Script**:
```bash
podman exec -it exitus-backend   python3 app/scripts/popular_historico_inicial.py   --ticker PETR4 --dias 252
```

**Funcionalidades**:
- ✅ Lazy loading (busca banco → API se necessário)
- ✅ Multi-mercado (BR .SA, US sem sufixo)
- ✅ Z-Score com dados reais (substituiu mock)
- ✅ Validação mínima de 30 dias
- ✅ Script manual com filtros

---

## Roadmap Futuro

### M8 - Analytics Avançados (Q2 2026)

**Objetivos**:
- Simulação Monte Carlo
- Otimização de Portfolio (Markowitz)
- Backtesting de estratégias
- Alertas em tempo real (WebSocket)
- Export PDF/Excel completo
- Celery para tarefas assíncronas

**Escopo**:
- 20-30 horas de implementação
- Bibliotecas: PyPortfolioOpt, QuantLib

### M9 - Deploy e Monitoramento (Q1 2026)

**Objetivos**:
- CI/CD com GitHub Actions
- Deploy em Railway/Render/Fly.io
- Monitoramento com Prometheus + Grafana (planejado)
- Logs centralizados
- Backups automáticos
- Health checks avançados

**Escopo**:
- 10-15 horas de implementação
- Testes end-to-end
- Documentação de deploy

---

## Métricas Gerais do Sistema

| Categoria | Métrica | Valor |
|-----------|---------|-------|
| **Endpoints** | Total de rotas | 67 |
| **Tabelas** | Database | 20 |
| **Índices** | PostgreSQL | 86+ |
| **Blueprints** | Flask | 16 |
| **Templates** | Frontend | 7+ |
| **Gráficos** | Chart.js | 5 |
| **Providers** | Cotações | 5 (4 APIs + cache) |
| **Cache Hit Rate** | Cotações | 85-95% |
| **Response Time** | Médio | 50-500ms |
| **Usuários Teste** | Concurrent | 20-40 |

---

## Referências

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detalhes técnicos da arquitetura
- [API_REFERENCE.md](API_REFERENCE.md) - Documentação completa de endpoints
- [USER_GUIDE.md](USER_GUIDE.md) - Guia do usuário final
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Operações e troubleshooting

---

**Documento gerado**: 06 de Janeiro de 2026  
**Versão**: v0.7.6  
**Baseado em**: Checklists M0-M7, CHANGELOG_MODULOS.md, validações executadas
