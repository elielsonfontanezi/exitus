# Exitus - Sistema de Gestão de Investimentos

## Visão Geral

**Exitus** é uma plataforma multi-usuário de gestão e análise de investimentos, suportando múltiplos mercados (Brasil, EUA, Europa, Ásia), múltiplas classes de ativos (ações, FIIs, REITs, renda fixa) e múltiplas corretoras com controle unificado de caixa.

### Principais Funcionalidades

* **Consolidação Multi-Mercado**: Gestão unificada de ativos brasileiros e internacionais
* **Análise Fundamentalista**: Buy Score (0-100), Preço Teto (4 métodos), Z-Score com histórico real
* **Cotações em Tempo Real**: Multi-provider com cache inteligente (15min TTL)
* **Dashboards Interativos**: Performance, alocação, evolução patrimonial e métricas de risco
* **Sistema de Alertas**: Notificações configuráveis por preço, percentual e indicadores
* **Relatórios Avançados**: Geração automática de relatórios de performance com Sharpe Ratio
* **Cálculos Fiscais**: Regras configuráveis por país e tipo de ativo

### Tipos de Ativos Suportados (14 tipos)

O Exitus suporta **14 tipos de ativos** em 4 mercados diferentes:

#### **🇧🇷 Brasil (6 tipos)**

* **Ações** (ACAO): B3 - PETR4, VALE3, ITUB4
* **FIIs** (FII): Fundos Imobiliários - HGLG11, KNRI11
* **CDB** (CDB): Certificados de Depósito Bancário
* **LCI/LCA** (LCI_LCA): Letras de Crédito
* **Tesouro Direto** (TESOURO_DIRETO): Selic, IPCA+, Prefixado
* **Debêntures** (DEBENTURE): Títulos corporativos

#### **🇺🇸 Estados Unidos (4 tipos)**

* **Stocks** (STOCK): NYSE/NASDAQ - AAPL, MSFT, GOOGL
* **REITs** (REIT): Real Estate Investment Trusts - O, VNQ
* **Bonds** (BOND): Títulos corporativos e governamentais
* **ETFs** (ETF): Fundos negociados em bolsa - SPY, QQQ

#### **🌍 Internacional (2 tipos)**

* **Stocks Internacionais** (STOCK_INTL): Europa/Ásia - SAP.DE, 7203.T
* **ETFs Internacionais** (ETF_INTL): VWCE.DE

#### **🔷 Outros (2 tipos)**

* **Criptomoedas** (CRIPTO): BTC, ETH, SOL
* **Outros** (OUTRO): Commodities, derivatives

**Total de ativos cadastrados**: 62 (39 BR + 16 US + 3 EU + 4 outros)

**Documentação completa**: [ENUMS.md]()

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão |
| --- | --- | --- |
| **Backend** | Python + Flask | 3.11 / 3.0 |
| **ORM** | SQLAlchemy + Alembic | 2.0 / 1.13 |
| **Frontend** | HTMX + Alpine.js + TailwindCSS | 2.0 / 3.14 / 3.4 |
| **Database** | PostgreSQL | 16 |
| **Containers** | Podman (rootless) | 4.x |
| **APIs Externas** | brapi.dev, yfinance, Alpha Vantage, Finnhub | - |

### Arquitetura de 3 Containers

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (localhost:8080)            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Container 3: exitus-frontend      │
        │  Flask + HTMX + Alpine.js          │
        │  Port: 8080                        │
        └────────────┬───────────────────────┘
                     │ HTTP/JSON
                     ▼
        ┌────────────────────────────────────┐
        │  Container 2: exitus-backend       │
        │  Flask API + SQLAlchemy            │
        │  Port: 5000                        │
        └────────────┬───────────────────────┘
                     │ SQL
                     ▼
        ┌────────────────────────────────────┐
        │  Container 1: exitus-db            │
        │  PostgreSQL 16                     │
        │  Port: 5432                        │
        └────────────────────────────────────┘

```

---

## 🗄️ Database Schema

### Tabelas Principais (21 tabelas)

| Tabela | Descrição | Campos Críticos |
| --- | --- | --- |
| `ativo` | Instrumentos financeiros (62 ativos) | ticker, tipo (**14 ENUMs**), classe, mercado, cap_rate |
| `usuario` | Usuários do sistema | username, email, role (3 ENUMs) |
| `corretora` | Corretoras/Exchanges | nome, tipo (2 ENUMs), pais, saldo_atual |
| `posicao` | Holdings atuais | quantidade, preco_medio, lucro_prejuizo |
| `transacao` | Operações executadas | tipo (10 ENUMs), quantidade, preco_unitario |
| `provento` | Dividendos/JCP/Rendimentos | tipo (7 ENUMs), valor_por_acao, data_com |
| `movimentacao_caixa` | Depósitos/Saques | tipo (9 ENUMs), valor, moeda |
| `evento_corporativo` | Splits/Bonificações | tipo (12 ENUMs), proporcao, data_evento |
| `historico_preco` | Histórico OHLCV | data, preco_fechamento, volume |
| `parametros_macro` | Taxa Selic, CDI, WACC | por país/mercado, cap_rate_fii |
| `regra_fiscal` | Impostos por país | aliquota_ir, valor_isencao, incidencia (4 ENUMs) |

* **Total de ENUMs**: 11 tipos, 62 valores únicos
* **Índices**: 86+ otimizados para queries de cálculo
* **Foreign Keys**: 15 com integridade referencial
* **Migrations**: Gerenciadas com Alembic (versão atual: `202602162130`)

---

## Coding Standard

* **Naming Convention**: snakecase para variáveis, funções, tabelas, colunas e arquivos (ex: `created_at`, `buy_score`, `historico_preco`).
* **Classes**: PascalCase (ex: `PortfolioService`).
* **Constantes**: UPPER_SNAKE_CASE (ex: `JWT_SECRET_KEY`).
* **Guia Completo**: [CODING_STANDARDS.md]()

---

## 🚀 Quick Start (5 minutos)

### Pré-requisitos

* **Ubuntu 22.04 LTS** (ou similar)
* **Podman 4.x** instalado
* **Git**
* **8GB RAM** mínimo
* **10GB** de espaço em disco

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/elielsonfontanezi/exitus.git
cd exitus

# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Edite o .env com suas credenciais (opcional para desenvolvimento)
nano .env

```

### 2. Configurar Tokens de APIs (Opcional)

Para cotações em tempo real, configure no `.env`:

```bash
# APIs de Cotações (M7.5)
BRAPI_TOKEN=seu_token_premium_aqui          # Premium: 60 req/min (FREE tier: 10 req/min)
ALPHAVANTAGE_TOKEN=seu_token_aqui           # Free: 500 req/dia
FINNHUB_TOKEN=seu_token_aqui                # Free: 60 req/min

```

**Nota**: O sistema funciona **SEM tokens** usando cache local e yfinance como fallback.

### 3. Executar o Sistema

```bash
# Subir os 3 containers
./scripts/start_exitus.sh

# Aguarde ~30 segundos para inicialização completa
# Logs em tempo real (opcional):
podman logs -f exitus-backend

```

### 4. Acessar

* **Frontend**: http://localhost:8080
* **Backend API**: http://localhost:5000/api
* **Health Check Backend**: http://localhost:5000/health
* **Health Check Frontend**: http://localhost:8080/health

**Credenciais padrão**:

* **Usuário**: `admin`
* **Senha**: `admin123`

---

## 📦 Módulos Implementados (M0-M7)

| Módulo | Status | Descrição | Endpoints |
| --- | --- | --- | --- |
| **M0** | ✅ PROD | Infraestrutura (Podman, PostgreSQL, Rede) | - |
| **M1** | ✅ PROD | Database Schema (21 tabelas, 86+ índices) | - |
| **M2** | ✅ PROD | Backend API Core (Auth JWT, CRUD, 16 blueprints) | 67 |
| **M3** | ✅ PROD | Portfolio Analytics (Dashboard, Performance, Alocação) | 11 |
| **M4** | ✅ PROD | Buy Signals & Cálculos Fiscais (Z-Score, Preço Teto) | 12 |
| **M5** | ✅ PROD | Frontend Base (15 rotas, HTMX, Alpine.js) | 15 |
| **M6** | ✅ PROD | Dashboards Frontend (4 telas, Chart.js) | 4 |
| **M7.3** | ✅ PROD | Alertas (6 tipos, CRUD completo) | 4 |
| **M7.4** | ✅ PROD | Relatórios (Performance, Export PDF stub) | 5 |
| **M7.5** | ✅ PROD | Cotações Live (Multi-provider, Cache 15min) | 3 |
| **M8** | 📅 PLAN | Analytics Avançados (Monte Carlo, Otimização) | - |
| **M9** | 📅 PLAN | Deploy & Monitoramento (CI/CD, Prometheus) | - |

**Total de Endpoints**: **67 rotas** validadas e documentadas

---

## 📚 Documentação Completa

| Documento | Descrição |
| --- | --- |
| **[ARCHITECTURE.md]()** | Visão arquitetural, containers, modelo de dados, integrações |
| **[MODULES.md]()** | Detalhamento de cada módulo M0-M7 (objetivos, features, status) |
| **[API_REFERENCE.md]()** | Referência completa de todas as 67 APIs com exemplos cURL |
| **[USER_GUIDE.md]()** | Guia do usuário: dashboards, operações, análises |
| **[OPERATIONS_RUNBOOK.md]()** | Deploy, testes, troubleshooting, scripts úteis |
| **[CHANGELOG.md]()** | Histórico de versões e roadmap futuro |

---

## 🔧 Operações Comuns

### Gerenciar Containers

```bash
# Ver status dos containers
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Parar o sistema
./scripts/stop_exitus.sh

# Restart completo
./scripts/restart_exitus.sh

# Ver logs
podman logs exitus-backend
podman logs exitus-frontend
podman logs exitus-db

```

### Executar Migrations

```bash
# Acessar container backend
podman exec -it exitus-backend bash

# Rodar migrations
flask db upgrade

# Criar nova migration
flask db migrate -m "Descrição da mudança"

```

### Popular Histórico de Preços

```bash
# Popular histórico de um ticker específico (últimos 252 dias)
podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --ticker PETR4 --dias 252

# Popular todos os ativos em posições
podman exec -it exitus-backend python3 app/scripts/popular_historico_inicial.py --dias 252

```

### Testes

```bash
# Testes unitários
podman exec -it exitus-backend pytest tests/

# Teste de endpoints (requer token JWT)
./scripts/test_performance.sh

```

---

## 🎯 Exemplos de Uso

### 1. Obter Token JWT

```bash
curl -X POST http://localhost:5000/api/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token'

```

### 2. Consultar Dashboard do Portfolio

```bash
TOKEN="seu_token_aqui"

curl -H "Authorization: Bearer $TOKEN"   http://localhost:5000/api/portfolio/dashboard | jq .

```

**Response:**

```json
{
  "success": true,
  "data": {
    "patrimonioativos": 0.0,
    "custoaquisicao": 25021.0,
    "saldocaixa": 0.0,
    "patrimoniototal": 0.0,
    "lucrobruto": -25021.0,
    "rentabilidadeperc": -100.0
  }
}

```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE]() para mais detalhes.

---

## 📞 Contato e Suporte

* **Repositório**: [https://github.com/elielsonfontanezi/exitus]()
* **Issues**: [https://github.com/elielsonfontanezi/exitus/issues]()

---

**Versão atual**: v0.7.7 (Database Optimization & Schema Update)

**Última atualização**: 16 de Fevereiro de 2026

