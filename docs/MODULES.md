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

O Sistema Exitus foi desenvolvido em **8 módulos incrementais** (M0-M7), cada um entregando funcionalidades completas e testadas.[file:10]

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

**Total de Endpoints**: **67 rotas** RESTful validadas.[file:10]

---

## M0 - Preparação do Ambiente

### Objetivo

Criar infraestrutura containerizada com Podman, configurar rede isolada e estabelecer ambiente de desenvolvimento local reproduzível.[file:10]

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Novembro 2025.[file:10]

### Componentes Implementados

#### 1. Instalação e Configuração do Podman

**Tecnologias**:
- Podman 4.x (rootless)
- Podman Compose 1.0
- Ubuntu 22.04 LTS.[file:10]

**Arquivos**:
```
scripts/
├── install_podman.sh          # Instalação do Podman
├── start_exitus.sh            # Iniciar todos os containers
├── stop_exitus.sh             # Parar todos os containers
├── restart_exitus.sh          # Restart completo
└── logs_exitus.sh             # Ver logs agregados
```[file:10]

#### 2. Criação dos 3 Containers

- **exitus-db** (PostgreSQL 16, porta 5432, volume persistente)
- **exitus-backend** (Flask API, porta 5000)
- **exitus-frontend** (Flask + HTMX, porta 8080).[file:10]

#### 3. Rede Bridge Customizada

- Rede `exitus-net` (bridge), DNS interno por nome (`exitus-db`, `exitus-backend`).[file:10]

#### 4. Volumes Persistentes

```
volumes/
├── postgres/          # Dados do PostgreSQL
└── data/              # Backups e arquivos temporários
```[file:10]

### Funcionalidades

- Iniciar/parar/restart o sistema com 1 comando, logs por container, hot reload, persistência de dados e healthchecks automáticos.[file:10]

---

## M1 - Database Schema

### Objetivo

Modelar e implementar schema PostgreSQL 16 otimizado para dados financeiros multi-mercado, com migrations gerenciadas por Alembic.[file:10][file:5]

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Novembro 2025.[file:10]

### Componentes Implementados

#### 1. Entidades Principais (21 Tabelas)

**Core**:
1. `usuario` - Usuários do sistema.
2. `corretora` - Brokers/corretoras.
3. `ativo` - Ativos financeiros (multi-mercado, 14 tipos de ativos).[file:5][file:18]

**Portfolio**:
4. `posicao` - Holdings dos usuários.
5. `transacao` - Compras/vendas e outros tipos de transação.
6. `provento` - Dividendos/JCP/rendimentos.
7. `movimentacao_caixa` - Depósitos/saques/ajustes de caixa.[file:5]

**Operations**:
8. `evento_corporativo` - Splits, bonificações, fusões, etc.
9. `feriado_mercado` - Calendário de mercado por país/bolsa.
10. `fonte_dados` - APIs externas de cotações.
11. `regra_fiscal` - Impostos por país/tipo de ativo.[file:5]

**Analytics (M7)**:
12. `portfolio` - Carteiras customizadas.
13. `alerta` / `configuracoes_alertas` - Sistema de alertas.
14. `relatorios_performance` / `auditoria_relatorio` - Relatórios salvos e auditoria.
15. `projecoes_renda` - Projeções de renda.
16. `historico_preco` - Histórico de preços (M7.6).[file:5][file:18]

**System**:
17. `log_auditoria` - Rastreabilidade.
18. `parametros_macro` - Configurações macroeconômicas.
19–21. Outras tabelas auxiliares de relatórios e performance (detalhadas em `EXITUS_DB_STRUCTURE.txt`).[file:5]

#### 2. Enums Personalizados

O schema utiliza **Enums nativos do PostgreSQL** para garantir integridade e performance.[file:5][file:28]

Tabela crítica de enums:

| Enum              | Valores principais                                                                                                                      | Usado em       |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------|----------------|
| `TipoAtivo`       | `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`, `STOCK`, `REIT`, `BOND`, `ETF`, `STOCK_INTL`, `ETF_INTL`, `CRIPTO`, `OUTRO` | `ativo`        |
| `ClasseAtivo`     | `RENDA_VARIAVEL`, `RENDA_FIXA`, `CRIPTO`, `COMMODITY`, `HIBRIDO`                                                                       | `ativo`        |
| `TipoTransacao`   | `COMPRA`, `VENDA`, `DIVIDENDO`, `JCP`, `ALUGUEL`, `BONIFICACAO`, `SPLIT`, `GRUPAMENTO`, `SUBSCRICAO`, `AMORTIZACAO`                    | `transacao`    |
| `TipoProvento`    | `DIVIDENDO`, `JCP`, `RENDIMENTO`, `CUPOM`, `BONIFICACAO`, `AMORTIZACAO_PROVENTO`, `OUTRO_PROVENTO`                                     | `provento`     |
| `TipoCorretora`   | `CORRETORA`, `EXCHANGE`                                                                                                                | `corretora`    |
| `UserRole`        | `ADMIN`, `USER`, `READONLY`                                                                                                            | `usuario`      |
| `TipoMovimentacao`| `DEPOSITO`, `SAQUE`, `TRANSFERENCIA`, `CREDITO_PROVENTO`, `TAXA_CORRETAGEM`, `TAXA_CUSTODIA`, `IMPOSTO`, `AJUSTE`, `OUTRO_MOV`        | `movimentacao_caixa` |
| `TipoEventoCorporativo` | `SPLIT`, `GRUPAMENTO`, `BONIFICACAO`, `FUSAO`, `CISAO`, `SPINOFF`, `INCORPORACAO`, `MUDANCA_TICKER`, `DESLISTAGEM`, `SUBSCRICAO`, `CONVERSAO`, `OUTRO_EVENTO` | `evento_corporativo` |
| `IncidenciaImposto` | `LUCRO`, `RECEITA`, `PROVENTO`, `OPERACAO`                                                                                           | `regra_fiscal` |

**Resumo**: 11 enums, 60+ valores distintos atualmente.[file:18][file:28]

#### 3. Expansão de TipoAtivo (v0.7.8)

O enum `TipoAtivo` foi expandido de 7 para **14 valores**, com suporte explícito a renda fixa brasileira e ativos internacionais.[file:18][file:28]

- **Brasil (6 tipos)**: `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
- **Estados Unidos (4 tipos)**: `STOCK`, `REIT`, `BOND`, `ETF`
- **Internacional (2 tipos)**: `STOCK_INTL`, `ETF_INTL`
- **Outros (2 tipos)**: `CRIPTO`, `OUTRO`

Migrations envolvidas:
- `202602162111` – expansão do enum `tipoativo`.
- `202602162130` – adição do campo `cap_rate` em `ativo` e ajustes relacionados.[file:18]

#### 4. Migrations Alembic

**Arquivos** (exemplo):[file:18]

```
backend/migrations/versions/
├── 001_initial_schema.py          # 12 tabelas iniciais
├── 007_add_reports_and_alerts.py  # M7.3/M7.4
├── 008_add_historico_preco.py     # M7.6 (06 Jan 2026)
├── 202602162111_expand_tipoativo_14_valores.py
├── 202602162130_add_caprate_ativo.py
└── ... (10+ migrations totais)
```

#### 5. Seeds de Dados Iniciais

**Arquivos principais**:[file:21][file:18]

- Usuários: `seed_usuarios.py`
- Corretoras: `seed_corretoras.py`
- Ativos BR/US/EU: `seed_ativos.py`, `seed_ativos_us.py`, `seed_ativos_eu.py`
- Feriados: `seed_feriados.py`
- Regras fiscais: `seed_regras_fiscais.py`

Total atual (dev): **62 ativos** (39 BR, 16 US, 3 EU, 4 outros).[file:21][file:18]

#### 6. Índices e Otimizações

Mais de **86 índices** criados para suportar queries de cálculo, relatórios e dashboards.[file:5][file:18]

- `ativo.ticker`, `ativo.mercado`, `ativo.classe`, `ativo.tipo`
- `historico_preco(ativo_id, data DESC)`
- `transacao(usuario_id, data_transacao DESC)`
- `posicao(usuario_id, ativo_id)` UNIQUE.[file:5]

### Funcionalidades

- Schema completo para multi-mercado e multi-moeda, com 14 tipos de ativos suportados e cap_rate em `ativo` para valuation de FIIs/REITs.[file:18][file:28]

---

## M2 - Backend API Core

### Objetivo

Implementar API RESTful com autenticação JWT, CRUD base para entidades principais e estrutura de blueprints escalável.[file:10]

### Status: ✅ PRODUCTION READY

**Data de Conclusão**: Dezembro 2025.[file:10]

### Componentes Implementados

- Autenticação JWT (`/api/auth/login`, `/api/auth/register`).
- 16 blueprints para usuários, corretoras, ativos, posições, transações, proventos, movimentações, buy signals, cálculos, regras fiscais, alertas, relatórios e cotações.[file:10][file:22]
- Padrão CRUD completo com paginação, validação via Marshmallow e isolamento por usuário.[file:22]

Exemplo de uso:
```bash
GET /api/ativos?tipo=acao&mercado=BR
Authorization: Bearer <token>
```[file:22]

---

## M3 - Portfolio Analytics

### Objetivo

Implementar cálculos financeiros avançados, métricas de portfolio e APIs de análise de performance.[file:10]

### Status: ✅ PRODUCTION READY

- Dashboard consolidado, alocação por classe/mercado, performance por ativo, métricas de risco (Sharpe, volatilidade, drawdown).[file:10][file:18]

Exemplo:
```bash
GET /api/portfolio/dashboard
```[file:22]

---

## M4 - Buy Signals & Cálculos Fiscais

### Objetivo

Implementar análise fundamentalista com Buy Score (0-100), Preço Teto (4 métodos), Z-Score com histórico real e regras fiscais configuráveis.[file:10]

### Status: ✅ PRODUCTION READY

- `GET /api/buy-signals/buy-score/{ticker}` – Buy Score e recomendação.
- `GET /api/calculos/preco-teto/{ticker}` – 4 métodos de preço teto.
- `GET /api/buy-signals/zscore/{ticker}` – Z-Score usando `historico_preco`.
- `GET /api/regras-fiscais` – regras por país/tipo_ativo.[file:22][file:18]

Regras fiscais incluem IR para `ACAO`, `FII`, `REIT`, etc., usando `regra_fiscal` e `IncidenciaImposto`.[file:18][file:5]

---

## M5 - Frontend Base

### Objetivo

Implementar frontend SSR com Flask, Jinja2, HTMX e Alpine.js.[file:10]

### Status: ✅ PRODUCTION READY

- 15 rotas frontend.
- Templates base (`base.html`) e telas de login/registro/dashboard.
- Integração com JWT mantido em sessão.[file:10]

---

## M6 - Dashboards Frontend

### Objetivo

Criar dashboards interativos com Chart.js, tabelas dinâmicas e integração com M3/M4.[file:10]

### Status: ✅ PRODUCTION READY

- Dashboard Buy Signals, Portfolios, Transações e Proventos.
- 5 gráficos principais (alocação, evolução patrimonial, proventos, etc.).[file:10]

---

## M7 - Relatórios e Análises

### M7.3 - Alertas

- CRUD de alertas (`/api/alertas`), 6 tipos de alerta (alta/baixa preço, DY mínimo, etc.).[file:10][file:22]

### M7.4 - Relatórios

- Geração de relatórios de performance/fiscal/alocação via `/api/relatorios/gerar` com armazenamento em `relatorios_performance` e auditoria em `auditoria_relatorio`.[file:18][file:22]

### M7.5 - Cotações Live

- 3 endpoints de cotações com multi-provider (brapi.dev, yfinance, Alpha Vantage, Finnhub) e cache PostgreSQL (TTL 15 min).[file:10][file:22]

### M7.6 - Histórico de Preços

- Tabela `historico_preco`, script `popular_historico_inicial.py` e integração com Z-Score.[file:18][file:5]

---

## Roadmap Futuro

### M8 - Analytics Avançados (Q2 2026)

- Monte Carlo, otimização de portfólio, backtesting e alertas em tempo real.[file:10]

### M9 - Deploy e Monitoramento (Q1 2026)

- CI/CD, deploy em cloud, monitoramento com Prometheus/Grafana e backups automatizados.[file:10]

---

## Métricas Gerais do Sistema

| Categoria      | Métrica         | Valor |
|----------------|-----------------|-------|
| Endpoints      | Rotas totais    | 67    |
| Tabelas        | Database        | 21    |
| Índices        | PostgreSQL      | 86+   |
| Blueprints     | Flask           | 16    |
| Templates      | Frontend        | 7+    |
| Gráficos       | Chart.js        | 5     |
| Providers      | Cotações        | 5     |
| Cache Hit Rate | Cotações        | 85-95%|
| Response Time  | Médio           | 50-500ms |
| Usuários Teste | Concorrentes    | 20-40 |

---

## Referências

- `ARCHITECTURE.md` – Detalhes técnicos da arquitetura.
- `API_REFERENCE.md` – Documentação completa de endpoints.
- `USER_GUIDE.md` – Guia do usuário final.
- `OPERATIONS_RUNBOOK.md` – Operações e troubleshooting.
- `ENUMS.md` – Detalhamento completo dos enums (inclui os 14 tipos de `TipoAtivo`).[file:28][file:8]

---

**Documento atualizado**: 17 de Fevereiro de 2026  
**Versão**: v0.7.8 (Expansão de TipoAtivo para 14 valores + cap_rate em ativo).[file:18][file:25]