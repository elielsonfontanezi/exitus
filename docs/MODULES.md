# Módulos do Sistema Exitus M0-M7

## Índice
- Visão Geral
- M0 — Preparação do Ambiente
- M1 — Database Schema
- M2 — Backend API Core
- M3 — Portfolio Analytics
- M4 — Buy Signals & Cálculos Fiscais
- M5 — Frontend Base
- M6 — Dashboards Frontend
- M7 — Relatórios e Análises
- Roadmap Futuro

---

## Visão Geral

O Sistema Exitus foi desenvolvido em 8 módulos incrementais (M0-M7), cada um
entregando funcionalidades completas e testadas.

### Status dos Módulos

| Módulo | Nome | Status | Data Conclusão | Endpoints |
|---|---|---|---|---|
| M0 | Infraestrutura | PROD | Nov 2025 | — |
| M1 | Database Schema | PROD | Nov 2025 | — |
| M2 | Backend API Core | PROD | Dez 2025 | 22 |
| M3 | Portfolio Analytics | PROD | Dez 2025 | 11 |
| M4 | Buy Signals & Fiscais | PROD | Dez 2025 | 12 |
| M5 | Frontend Base | PROD | 04 Dez 2025 | 15 |
| M6 | Dashboards Frontend | PROD | 06 Dez 2025 | 4 |
| M7.3 | Alertas | PROD | Dez 2025 | 4 |
| M7.4 | Relatórios | PROD | Jan 2026 | 5 |
| M7.5 | Cotações Live | PROD | 09 Dez 2025 | 3 |
| M7.6 | Histórico de Preços | PROD | 06 Jan 2026 | — |
| M8 | Analytics Avançados | PLAN | Q2 2026 | — |
| M9 | Deploy & Monitoramento | PLAN | Q1 2026 | — |

**Total de Endpoints: 69 rotas RESTful validadas.**

> v0.7.10: M2 atualizado — Posições passou de 2 para 4 endpoints após resolução
> dos GAPs EXITUS-POS-001 a EXITUS-POS-007. Ver `M2_POSICOES.md`.

---

## M0 — Preparação do Ambiente

**Objetivo:** Criar infraestrutura containerizada com Podman, configurar rede
isolada e estabelecer ambiente de desenvolvimento local reproduzível.

**Status:** PRODUCTION READY — Data de Conclusão: Novembro 2025

**Tecnologias:** Podman 4.x rootless, Podman Compose 1.0, Ubuntu 22.04 LTS

**Componentes Implementados:**

1. Instalação e configuração do Podman
2. Criação dos 3 containers:
   - `exitus-db` — PostgreSQL 16, porta 5432, volume persistente
   - `exitus-backend` — Flask API, porta 5000
   - `exitus-frontend` — Flask HTMX, porta 8080
3. Rede bridge customizada `exitus-net` com DNS interno (`exitus-db`, `exitus-backend`)
4. Volumes persistentes: `postgres` (dados do PostgreSQL), `data` (backups e arquivos)

**Scripts:** `install_podman.sh`, `start_exitus.sh`, `stop_exitus.sh`,
`restart_exitus.sh`, `logs_exitus.sh`

---

## M1 — Database Schema

**Objetivo:** Modelar e implementar schema PostgreSQL 16 otimizado para dados
financeiros multi-mercado, com migrations gerenciadas por Alembic.

**Status:** PRODUCTION READY — Data de Conclusão: Novembro 2025

### Entidades Principais — 21 Tabelas

**Core:**
1. `usuario` — Usuários do sistema
2. `corretora` — Brokers/corretoras
3. `ativo` — Ativos financeiros multi-mercado (14 tipos)

**Portfolio:**
4. `posicao` — Holdings dos usuários
5. `transacao` — Compras/vendas e outros tipos de transação
6. `provento` — Dividendos/JCP/rendimentos
7. `movimentacao_caixa` — Depósitos/saques/ajustes de caixa

**Operations:**
8. `evento_corporativo` — Splits, bonificações, fusões, etc.
9. `feriado_mercado` — Calendário de mercado por país/bolsa
10. `fonte_dados` — APIs externas de cotações
11. `regra_fiscal` — Impostos por país/tipo de ativo

**Analytics (M7):**
12. `portfolio` — Carteiras customizadas
13. `configuracao_alerta` — Sistema de alertas
14. `auditoria_relatorio` / `relatorios_performance` — Relatórios salvos e auditoria
15. `projecoes_renda` — Projeções de renda
16. `historico_preco` — Histórico de preços (M7.6)

**System:**
17. `log_auditoria` — Rastreabilidade
18. `parametros_macro` — Configurações macroeconômicas
19-21. Tabelas auxiliares de relatórios e performance (detalhadas em `EXITUS_DB_STRUCTURE.txt`)

### Enums Personalizados

| Enum | Valores principais | Usado em |
|---|---|---|
| TipoAtivo | ACAO, FII, CDB, LCI_LCA, TESOURO_DIRETO, DEBENTURE, STOCK, REIT, BOND, ETF, STOCK_INTL, ETF_INTL, CRIPTO, OUTRO | ativo |
| ClasseAtivo | RENDA_VARIAVEL, RENDA_FIXA, CRIPTO, COMMODITY, HIBRIDO | ativo |
| TipoTransacao | COMPRA, VENDA, DIVIDENDO, JCP, ALUGUEL, BONIFICACAO, SPLIT, GRUPAMENTO, SUBSCRICAO, AMORTIZACAO | transacao |
| TipoProvento | DIVIDENDO, JCP, RENDIMENTO, CUPOM, BONIFICACAO, AMORTIZACAO_PROVENTO, OUTRO_PROVENTO | provento |
| TipoCorretora | CORRETORA, EXCHANGE | corretora |
| UserRole | ADMIN, USER, READONLY | usuario |
| TipoMovimentacao | DEPOSITO, SAQUE, TRANSFERENCIA, CREDITO_PROVENTO, TAXA_CORRETAGEM, TAXA_CUSTODIA, IMPOSTO, AJUSTE, OUTRO_MOV | movimentacao_caixa |
| TipoEventoCorporativo | SPLIT, GRUPAMENTO, BONIFICACAO, FUSAO, CISAO, SPINOFF, INCORPORACAO, MUDANCA_TICKER, DESLISTAGEM, SUBSCRICAO, CONVERSAO, OUTRO_EVENTO | evento_corporativo |
| IncidenciaImposto | LUCRO, RECEITA, PROVENTO, OPERACAO | regra_fiscal |

Resumo: 11 enums, 60 valores distintos. Para referência completa, ver `ENUMS.md`.

### Migrations Alembic — 10 migrations totais
- `001_initial_schema.py` — 12 tabelas iniciais
- `007_add_reports_and_alerts.py` — M7.3/M7.4
- `008_add_historico_preco.py` — M7.6 (06 Jan 2026)
- `202602162111_expand_tipoativo_14_valores.py`
- `202602162130_add_caprate_ativo.py`

### Seeds de Dados
**Total dev: 70 ativos** (47 BR, 16 US, 3 EU, 4 outros)

`seed_usuarios.py`, `seed_corretoras.py`, `seed_ativos_br.py`,
`seed_ativos_renda_fixa_br.py`, `seed_ativos_us.py`, `seed_ativos_eu.py`,
`seed_feriados.py`, `seed_regras_fiscais.py`

### Índices e Otimizações
Mais de 86 índices criados para suportar queries de cálculo, relatórios e dashboards.

---

## M2 — Backend API Core

**Objetivo:** Implementar API RESTful com autenticação JWT, CRUD base para
entidades principais e estrutura de blueprints escalável.

**Status:** PRODUCTION READY — Data de Conclusão: Dezembro 2025

**Componentes:**
- Autenticação JWT: `/api/auth/login`, `/api/auth/register`
- 16 blueprints para usuários, corretoras, ativos, posições, transações,
  proventos, movimentações, buy signals, cálculos, regras fiscais, alertas,
  relatórios e cotações
- Padrão CRUD completo com paginação, validação via Marshmallow e isolamento por usuário

**Endpoints do módulo (22 total):**

| Grupo | Endpoints | Validado em |
|---|---|---|
| auth | 2 | M2-AUTH |
| usuarios | 4 | M2-USUARIOS |
| corretoras | 6 | M2-CORRETORAS (29/29 ✅) |
| ativos | 6 | M2-ATIVOS |
| posicoes | **4** | **M2-POSICOES (12/12 ✅)** |

> **v0.7.10:** Posições expandido de 2 para 4 endpoints.
> GAPs EXITUS-POS-001 a EXITUS-POS-007 resolvidos.
> Pendência menor: EXITUS-POS-008 (enum serialization — não-bloqueante).

Exemplo de uso:
```bash
GET /api/ativos?tipo=acao&mercado=BR
Authorization: Bearer <token>
```

---

## M3 — Portfolio Analytics

**Objetivo:** Implementar cálculos financeiros avançados, métricas de portfolio
e APIs de análise de performance.

**Status:** PRODUCTION READY

- Dashboard consolidado, alocação por classe/mercado, performance por ativo
- Métricas de risco: Sharpe, volatilidade, drawdown

```bash
GET /api/portfolio/dashboard
```

---

## M4 — Buy Signals & Cálculos Fiscais

**Objetivo:** Implementar análise fundamentalista com Buy Score (0-100),
Preço Teto (4 métodos), Z-Score com histórico real e regras fiscais configuráveis.

**Status:** PRODUCTION READY

- `GET /api/buy-signals/buy-score/{ticker}` — Buy Score e recomendação
- `GET /api/calculos/preco-teto/{ticker}` — 4 métodos de preço teto
- `GET /api/buy-signals/zscore/{ticker}` — Z-Score usando `historico_preco`
- `GET /api/regras-fiscais` — regras por país/tipo de ativo

Regras fiscais incluem IR para ACAO, FII, REIT, etc., usando `regra_fiscal`
e `IncidenciaImposto`.

---

## M5 — Frontend Base

**Objetivo:** Implementar frontend SSR com Flask, Jinja2, HTMX e Alpine.js.

**Status:** PRODUCTION READY — Data: 04 Dez 2025

- 15 rotas frontend
- Templates base `base.html` e telas de login/registro/dashboard
- Integração com JWT mantido em sessão

---

## M6 — Dashboards Frontend

**Objetivo:** Criar dashboards interativos com Chart.js, tabelas dinâmicas e
integração com M3/M4.

**Status:** PRODUCTION READY — Data: 06 Dez 2025

- Dashboard Buy Signals, Portfólios, Transações e Proventos
- 5 gráficos principais (alocação, evolução patrimonial, proventos, etc.)

---

## M7 — Relatórios e Análises

### M7.3 — Alertas
CRUD de alertas `/api/alertas`, 6 tipos de alerta (alta/baixa preço, DY mínimo, etc.).

### M7.4 — Relatórios
Geração de relatórios de performance/fiscal/alocação via `/api/relatorios/gerar`
com armazenamento em `relatorios_performance` e auditoria em `auditoria_relatorio`.

### M7.5 — Cotações Live
3 endpoints de cotações com multi-provider (brapi.dev, yfinance, Alpha Vantage, Finnhub)
e cache PostgreSQL TTL 15 min.

> **Dependência de Posições:** `valor_atual` e `lucro_prejuizo_nao_realizado`
> nas posições são populados pelo serviço de cotações M7.5 via
> `atualizar_valores_atuais()`.

### M7.6 — Histórico de Preços
Tabela `historico_preco`, script `popular_historico_inicial.py` e integração com Z-Score.

---

## Roadmap Futuro

### M8 — Analytics Avançados (Q2 2026)
Simulação Monte Carlo, otimização Markowitz, backtesting, WebSocket alertas real-time,
export PDF/Excel profissional.

### M9 — Deploy e Monitoramento (Q1 2026)
CI/CD GitHub Actions, deploy Railway/Render, monitoramento com Prometheus/Grafana.

---

## Métricas Gerais do Sistema

| Categoria | Métrica | Valor |
|---|---|---|
| Endpoints | Rotas totais | **69** |
| Tabelas | Database | 21 |
| Índices | PostgreSQL | 86+ |
| Blueprints | Flask | 16 |
| Templates | Frontend | 7 |
| Gráficos | Chart.js | 5 |
| Providers | Cotações | 5 |
| Cache Hit Rate | Cotações | 85-95% |
| Response Time | Médio | 50-500ms |
| Usuários Teste | Concorrentes | 20-40 |
| Ativos Seedados | — | 70 (47 BR, 16 US, 3 EU, 4 outros) |
| Cobertura ENUMs | — | 14/14 tipos implementados e testados |

---

## Referências
- `ARCHITECTURE.md` — Detalhes técnicos da arquitetura
- `API_REFERENCE.md` — Documentação completa de endpoints
- `USER_GUIDE.md` — Guia do usuário final
- `OPERATIONS_RUNBOOK.md` — Operações e troubleshooting
- `ENUMS.md` — Detalhamento completo dos enums (14 tipos de TipoAtivo)
- `M2_CORRETORAS.md` — Validação M2-CORRETORAS (29/29 ✅)
- `M2_POSICOES.md` — Validação M2-POSICOES (12/12 ✅)

---

*Documento atualizado: 22 de Fevereiro de 2026*
*Versão: v0.7.10*
*70 ativos seedados — M2-POSICOES validado (7 GAPs fechados)*
