# Manual do Usuário — Sistema Exitus v0.9.25 (RASCUNHO)

> **Versão:** v0.9.25  
> **Data:** 25/06/2026 (atualizado com status atual do sistema)  
> **Status:** 🟡 RASCUNHO EM DESENVOLVIMENTO — Sistema ainda em fase de desenvolvimento (48/54 GAPs concluídos)  
> **Objetivo:** Guia completo de navegação e uso do sistema  
> **Público:** Investidores e assessoras de investimento

---

## 📋 Índice

1. [Introdução](#introdução)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Módulos do Sistema](#módulos-do-sistema)
5. [Fluxos Principais](#fluxos-principais)
6. [APIs e Integrações](#apis-e-integrações)
7. [Perguntas Frequentes](#perguntas-frequentes)

---

## 🎯 Introdução

### O que é o Exitus?

**Exitus** é uma plataforma completa de gestão e análise de investimentos que permite:
- Consolidar investimentos de múltiplos mercados (Brasil, EUA, Internacional)
- Calcular automaticamente impostos (IR, IOF, DARF)
- Analisar performance e rentabilidade do portfólio
- Receber alertas de preços e eventos corporativos
- Criar planos disciplinados de compra e venda

### Diferenciais

- ✅ **Multi-mercado:** BR, US, INTL em uma única plataforma
- ✅ **Multi-moeda:** BRL, USD, EUR com conversão automática
- ✅ **Motor fiscal completo:** IR, IOF, DARF, compensação de prejuízos
- ✅ **15 tipos de ativos:** Ações, FIIs, ETFs, Bonds, Cripto, etc.
- ✅ **Buy Signals com IA:** Análise fundamentalista automatizada
- ✅ **Multi-tenancy:** Suporte para assessoras com múltiplos clientes

---

## Acesso ao Sistema

### 1. Login

**URL:** `http://localhost:8080/auth/login`

**Para ambiente de desenvolvimento, use:**
- **Usuário:** `e2e_user`
- **Senha:** `e2e_senha_123`

**Funcionalidades:**
- Login com usuário/senha
- Opção "Lembrar-me" (mantém sessão)
- Recuperação de senha
- Registro de nova conta

**API relacionada:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Resposta:
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "admin",
    "role": "ADMIN",
    "assessora_id": "23c54cb4-cb0a-438f-b985-def21d70904e"
  }
}
```

---

## 📊 Dashboard Principal

### URL: `/dashboard/`

**Visão geral do patrimônio consolidado em tempo real.**

### Funcionalidades

1. **Resumo por Mercado**
   - Brasil (Ações & FIIs)
   - Estados Unidos (Stocks & ETFs)
   - Internacional (Global Markets)

2. **Métricas Principais**
   - Patrimônio total (multi-moeda)
   - Rentabilidade geral (%)
   - Total de portfolios
   - Total de posições

3. **Gráficos**
   - Alocação geográfica (pizza)
   - Evolução patrimonial (linha)
   - Top ativos por mercado

4. **Ações Rápidas**
   - Botão "Buy Signals" → Oportunidades de compra
   - Botão "Carteiras" → Gestão de portfolios
   - Toggle de moeda (BRL/USD/EUR)

### APIs Relacionadas

```bash
# Dashboard consolidado
GET /api/portfolios/dashboard
Authorization: Bearer <token>

# Evolução patrimonial
GET /api/portfolios/evolucao?meses=12
Authorization: Bearer <token>

# Resposta:
{
  "success": true,
  "data": {
    "resumo": {
      "patrimonio_total": 250000.00,
      "rentabilidade_geral": 12.5,
      "total_portfolios": 3,
      "total_posicoes": 45
    },
    "por_mercado": {
      "BR": {
        "patrimonio": 150000.00,
        "percentual": 60.0,
        "rentabilidade": 15.2,
        "top_ativos": [...]
      },
      "US": {...},
      "INTL": {...}
    },
    "alocacao_geografica": {...},
    "evolucao": [...]
  }
}
```

---

## 🧩 Módulos do Sistema

### 1. Buy Signals — Oportunidades de Compra

**URL:** `/analises/buy-signals`

**Descrição:** Identifica as melhores oportunidades de compra usando análise quantitativa — combina margem de segurança, Z-Score estatístico, dividend yield e beta em um score de 0 a 100.

**Funcionalidades:**
- Watchlist Top 10 — ativos com melhores Buy Scores
- Consulta individual por ticker (autocomplete)
- Painel de detalhe com score, margem, Z-Score e sinal
- KPIs: Top Score, Ativos Analisados, Score ≥ 60, Score < 40

**Como usar:**
1. Acesse "Análises → Buy Signals" no menu
2. Visualize a watchlist Top 10 ranqueada por Buy Score
3. Digite um ticker no campo "Consultar Score por Ticker" e clique "Analisar"
4. O painel de detalhe exibe: Score (0-100), Margem de Segurança, Z-Score e sinal (NEUTRO/COMPRAR/VENDER)

#### Técnicas de Cálculo

**1. Margem de Segurança** (`calcular_margem_seguranca`)

Mede a distância entre o preço atual e o preço teto (valor justo) cadastrado no ativo.

```
Margem = (Preço Teto - Preço Atual) / Preço Teto × 100
```

- **Margem > 5%:** 🟢 COMPRA — ativo abaixo do valor justo
- **Margem 0-5%:** 🟡 NEUTRO — próximo do valor justo
- **Margem < 0%:** 🔴 VENDA — acima do valor justo

**Exemplo ITUB4:** Preço atual R$ 32,45, Preço teto R$ 38,00 → Margem = 14,61% → 🟢 COMPRA

**2. Z-Score** (`calcular_zscore`)

Mede quantos desvios-padrão o preço atual está da média histórica (252 dias úteis = 1 ano). Indica se o ativo está "caro" ou "barato" estatisticamente.

```
Z-Score = (Preço Atual - Média_252d) / Desvio_Padrão_252d
```

- **Z < -1:** Ativo significativamente abaixo da média (oportunidade estatística)
- **Z -1 a 0:** Abaixo da média (neutro)
- **Z > 0:** Acima da média (relativamente caro)

**Requer:** mínimo de 30 registros de histórico de preços no banco (`historico_preco`). Se indisponível, a tela exibe "Z-Score indisponível".

**3. Buy Score** (`calcular_buy_score`)

Score composto de 0 a 100, soma de 4 fatores ponderados:

| Fator | Peso Máximo | Cálculo | Descrição |
|-------|-------------|---------|-----------|
| **Margem de Segurança** | 30 pts | `margem × 3` (clipado em 30) | Quanto maior a margem, mais pontos |
| **Z-Score** | 25 pts | `25 se Z < -1, 15 se Z < 0, 5 caso contrário` | Ativos abaixo da média histórica pontuam mais |
| **Dividend Yield** | 20 pts | `DY × 5` (clipado em 20) | DY de 4% = 20 pts (máximo) |
| **Beta** | 25 pts | `max(0, 25 - (beta-1) × 12.5)` (clipado em 25) | Beta 1.0 = 25 pts; beta alto reduz pontos (risco) |

**Sinais:**
- **Score ≥ 80:** COMPRAR (forte oportunidade)
- **Score 60-79:** AGUARDAR (oportunidade moderada)
- **Score < 60:** VENDER/NEUTRO (não é momento)

**Limitação conhecida:** Se margem ou Z-Score não podem ser calculados (ex: sem histórico de preços), o `try/except` zera esses fatores e o score cai para ~50 (fallback artificial). Nesse caso, o score não reflete análise real — apenas DY e beta contribuem. Para identificar: se todos os ativos da watchlist têm score 50, é provável que histórico esteja indisponível.

**4. Watchlist Top 10**

Lista os 10 ativos com maiores Buy Scores. Ordenada por score decrescente. Exibe: Ticker, Preço Atual, Preço Teto, Margem %, Buy Score, Sinal.

**API:**
```bash
GET /api/buy-signals/watchlist-top
GET /api/buy-signals/buy-score/{ticker}
GET /api/buy-signals/margem-seguranca/{ticker}
GET /api/buy-signals/zscore/{ticker}
GET /api/buy-signals/analisar/{ticker}
Authorization: Bearer <token>
```

**Nota técnica:** O Z-Score requer histórico de preços populado no banco. Em ambiente de desenvolvimento sem provider de histórico configurado, o Z-Score pode estar indisponível. Ver `ROADMAP.md` → HIST-002 para plano de fallback multi-provider.

#### Como o histórico é populado e atualizado

1. Ao consultar um ticker, o sistema verifica quantos registros existem em `historico_preco`. Se houver pelo menos 80% dos dias solicitados (ex.: 200 de 252), os dados do banco são usados diretamente.
2. Se faltar histórico, o `HistoricoService` aciona os providers externos (`CotacoesService.buscar_historico`) apenas uma vez para preencher o intervalo solicitado. Os dados retornados são persistidos com timestamp (`updatedat`).
3. Nas consultas seguintes, o frontend reutiliza o histórico salvo até que uma regra de negócio peça atualização (ex.: solicitado mais dias ou identificado gap superior a 1 dia útil). Assim evitamos chamadas repetidas às APIs externas e mantemos o Z-Score confiável mesmo offline.

> Resumo: histórico é "dado frio" — fica no banco por padrão e só é baixado novamente quando há lacunas suficientes para comprometer o cálculo.

---

### 2. Portfolios — Gestão de Carteiras

**URL:** `/dashboard/portfolios`

**Descrição:** Gerencie múltiplas carteiras de investimento com visão consolidada.

**Funcionalidades:**
- Criar/editar/excluir portfolios
- Visão consolidada de todas as carteiras
- Métricas por portfolio (patrimônio, rentabilidade, alocação)
- Filtros por mercado e moeda

**Como usar:**
1. Clique em "Nova Carteira" para criar
2. Preencha: nome, descrição, mercado, moeda base
3. Visualize métricas de cada carteira
4. Clique em uma carteira para ver detalhes

**Regras de Negócio:**
- Cada portfolio tem uma moeda base (BRL, USD, EUR)
- Portfolios podem conter ativos de múltiplos mercados
- Rentabilidade calculada em relação ao custo médio
- Alocação por classe de ativo e mercado

**APIs:**
```bash
# Listar portfolios
GET /api/portfolios
Authorization: Bearer <token>

# Criar portfolio
POST /api/portfolios
Content-Type: application/json

{
  "nome": "Carteira Dividendos",
  "descricao": "Foco em dividendos",
  "mercado": "BR",
  "moeda_base": "BRL"
}

# Obter detalhes
GET /api/portfolios/{id}
```

---

### 3. Transações — Histórico de Operações

**URL:** `/dashboard/transactions`

**Descrição:** Registre e acompanhe todas as compras e vendas de ativos.

**Funcionalidades:**
- Registrar compra/venda de ativos
- Histórico completo de transações
- Filtros por data, ativo, tipo, mercado
- Cálculo automático de preço médio e lucro/prejuízo

**Como usar:**
1. Clique em "Nova Transação"
2. Selecione: tipo (compra/venda), ativo, quantidade, preço
3. Informe: data, corretora, taxas
4. Sistema calcula automaticamente IR e IOF

**Regras de Negócio:**
- Compra: aumenta posição e atualiza preço médio
- Venda: reduz posição e calcula lucro/prejuízo
- IR calculado automaticamente (15% ou 20% conforme prazo)
- IOF aplicado em operações < 30 dias (renda fixa)
- Compensação de prejuízos automática

**APIs:**
```bash
# Listar transações
GET /api/transacoes?page=1&per_page=20
Authorization: Bearer <token>

# Criar transação
POST /api/transacoes
Content-Type: application/json

{
  "tipo": "COMPRA",
  "ativo_id": "uuid",
  "quantidade": 100,
  "preco_unitario": 28.50,
  "data_operacao": "2026-03-19",
  "corretora_id": "uuid",
  "taxas": 10.00
}
```

---

### 4. Ativos — Catálogo de Ativos

**URLs:**
- `/ativos/acoes` — Minhas Ações
- `/ativos/fiis` — Meus FIIs
- `/ativos/etfs` — ETFs
- `/ativos/renda-fixa` — Renda Fixa
- `/ativos/cripto` — Criptoativos
- `/ativos/<ticker>` — Detalhe do Ativo

**Funcionalidades:**
- Lista de ativos com cotações atualizadas por categoria
- Busca por ticker dentro de cada categoria
- Stats: total, com preço, DY médio
- Detalhe do ativo: fundamentos (P/L, P/VP, ROE, DY) e ações rápidas

**Como usar:**
1. Clique em "Ativos" no menu
2. Escolha a categoria (Ações, FIIs, ETFs, etc.)
3. Use a busca para filtrar por ticker
4. Clique em qualquer linha para ver o detalhe completo

**Sprint 3** — Implementado em 09/06/2026

---

### 5. Proventos — Dividendos e JCP

**URLs:**
- `/proventos/recebidos` — Proventos Recebidos
- `/proventos/projetados` — Proventos Projetados
- `/proventos/calendario` — Calendário de Dividendos

**Funcionalidades:**
- Histórico de proventos recebidos (100+ reais)
- Proventos projetados (PREVISTO)
- Calendário agrupado por mês
- Stats: total recebido, valor unitário médio, quantidade

**Como usar:**
1. Acesse "Análises" → "Proventos" no menu
2. Escolha: Recebidos, Projetados ou Calendário
3. Confira calendário de próximos pagamentos
4. Filtre por ativo ou período

**Sprint 2** — Implementado em 09/06/2026

**Tipos de provento:**
- Dividendos (isentos de IR)
- JCP (15% IR na fonte)
- Bonificações
- Direitos de subscrição

**APIs:**
```bash
# Listar proventos
GET /api/proventos?ativo_id={uuid}&ano=2026
Authorization: Bearer <token>

# Calendário de dividendos
GET /api/calendario-dividendos
```

---

### 6. Planos de Compra — Acumulação Disciplinada

**URLs:**
- `/planos-compra/` — Dashboard de Planos
- `/planos-compra/<id>` — Detalhe do Plano
- `/planos-venda/` — Planos de Venda (em desenvolvimento)

**Funcionalidades:**
- Lista de planos de acumulação por ativo
- Barra de progresso: qtd acumulada vs. meta
- Progresso médio, ativos em andamento, concluídos
- Detalhe: meta, aporte mensal, prazo, ativo alvo
- Ações rápidas: registrar aporte, ver ativo

**Como usar:**
1. Acesse "Planos" no menu
2. Visualize todos os planos de acumulação ativos
3. Clique em "Detalhes" para ver progresso individual
4. Use "Registrar Aporte" para avançar no plano

**Sprint 4** — Implementado em 09/06/2026

---

### 7. Alertas — Monitoramento de Preços

**URL:** `/alertas/`

**Funcionalidades:**
- Lista de todos os alertas configurados
- Distribuição por tipo: Preço Alvo, Dividendo, Stop Loss
- Status ativo/inativo e total de acionamentos
- Condição: operador e valor de referência

**Como usar:**
1. Acesse "Alertas" no menu
2. Visualize alertas ativos e seu status
3. Identifique alertas já acionados

**Sprint 4** — Implementado em 09/06/2026

---

### 8. Imposto de Renda — IR e DARF

**URLs:**
- `/imposto-renda/mensal` — Apuração Mensal IR
- `/imposto-renda/darfs` — DARFs do Mês
- `/imposto-renda/historico` — Histórico Anual
- `/imposto-renda/declaracao` — Declaração DIRPF

**Funcionalidades:**
- Apuração mensal por categoria: Day Trade (20%), Swing Trade (15%), FIIs (20%), Exterior (15%), Renda Fixa
- Proventos: Dividendos BR/EUA, JCP, Aluguel de Ações com IR retido na fonte
- DARFs geradas no mês com total de IR devido
- Histórico de 12 meses com operações e alertas
- DIRPF: bens e direitos por ativo (custo de aquisição real para declaração)

**Como usar:**
1. Acesse "Análises" → "Imposto de Renda" no menu
2. Veja a apuração do mês atual com todas as categorias
3. Verifique DARFs pendentes para pagamento
4. Consulte o histórico anual para acompanhar evolução
5. Use a Declaração DIRPF para dados de bens e direitos

**Regras de Negócio:**
- Day Trade: 20% sobre lucro
- Swing Trade: 15% sobre lucro (ações/FIIs)
- Renda Fixa: 15-22.5% conforme prazo
- Isenção: vendas < R$ 20.000/mês (ações)
- Acúmulo: IR < R$ 10,00 acumula para próximo mês
- Compensação: prejuízos compensam lucros da mesma categoria

**APIs:**
```bash
# Apuração do mês
GET /api/ir/apuracao?ano=2026&mes=2026-06
Authorization: Bearer <token>

# DARFs do mês
GET /api/ir/darf?ano=2026&mes=2026-06
Authorization: Bearer <token>

{
  "ano": 2026,
  "mes": 3,
  "codigo_receita": "6015"
}

# Consultar saldo de prejuízos
GET /api/ir/saldo-prejuizo
```

**Sprint 5** — Implementado em 09/06/2026

---

### 9. Rentabilidade e Análises — Sprint 6

**URLs:**
- `/analises/rentabilidade/periodo` — Rentabilidade TWR/MWR por Período
- `/analises/alocacao` — Alocação de Ativos por Classe
- `/analises/evolucao` — Evolução Patrimonial (série histórica)
- `/analises/performance` — Performance: Sharpe, Drawdown, Top Ativos
- `/analises/buy-signals` — Buy Score por Ticker

**Funcionalidades:**
- TWR (Time-Weighted Return) e MWR (Money-Weighted Return) com benchmark CDI e alpha
- Alocação RF/RV/Cripto com barras de progresso e tabela de desvio vs. target
- Evolução patrimonial mês a mês de 2024 a 2026 (R$119k → R$795k)
- Sharpe Ratio, Max Drawdown, rentabilidade bruta e líquida
- Buy Score 0–100 por ticker com gauge visual e tabela de posições

**Como usar:**
1. Acesse "Análises" → "Rentabilidade" no menu
2. Use os filtros de período (3m, 6m, 12m, ytd) para ajustar o intervalo
3. Confira a Alocação para ver distribuição da carteira
4. Veja a Evolução para série histórica completa
5. Em Buy Signals, digite qualquer ticker para ver o score

**Dados reais exibidos:**
- TWR: 81.14% | MWR: -65.4% (12 meses)
- Patrimônio total: R$ 795.720,82 | RF: 61.6% | RV: 38.4%
- Sharpe: 1.45 | Drawdown: -8.3% | Rent. Líquida: 10.2%

**APIs:**
```bash
# Rentabilidade
GET /api/portfolios/rentabilidade?periodo=12m
Authorization: Bearer <token>

# Alocação
GET /api/portfolios/alocacao

# Evolução
GET /api/portfolios/evolucao

# Performance
GET /api/performance/performance

# Buy Score
GET /api/buy-signals/buy-score/PETR4
```

**Sprint 6** — Implementado em 09/06/2026

---

### 10. Relatórios e Exportação

**Sprint 7** — Implementado em 09/06/2026

#### 10.1 Relatório Mensal
**URL:** `/relatorios/mensal`

**Descrição:** Resumo consolidado do mês com operações, proventos recebidos e resumo de IR.

**Funcionalidades:**
- Filtro por mês e ano
- Tabela de operações (compra/venda) com preço, quantidade e total
- Tabela de proventos recebidos
- Cards de resumo: IR devido, proventos isentos, total de operações

**Como usar:**
1. Acesse "Relatórios > Relatório Mensal"
2. Selecione mês e ano desejados
3. Clique em "Filtrar"
4. Use "⬇ Exportar CSV" para download

#### 10.2 Relatório Anual
**URL:** `/relatorios/anual`

**Descrição:** Visão consolidada do ano com histórico de IR mensal e totais.

**Funcionalidades:**
- Filtro por ano-calendário
- Histórico IR por mês (Day Trade, Swing, FII)
- Total anual de IR com indicação de DARF obrigatório (≥ R$10)
- Totais de operações e proventos do ano

#### 10.3 Extrato Completo
**URL:** `/relatorios/extrato`

**Descrição:** Histórico completo de operações com filtros avançados.

**Funcionalidades:**
- Filtro por tipo (Compra, Venda, Dividendo, Bonificação)
- Filtro por período (data início / data fim)
- Resumo: total de operações, compras e vendas
- Link direto para exportação CSV

#### 10.4 IR Completo
**URL:** `/relatorios/ir`

**Descrição:** Visão consolidada de Imposto de Renda: apuração corrente, histórico mensal e DIRPF.

**Funcionalidades:**
- Apuração do mês atual (Day Trade, Swing, FII, Total)
- Histórico mensal de IR para o ano selecionado
- Bens e Direitos para preenchimento do DIRPF
- Link direto para o módulo de IR (`/imposto-renda/mensal`)

#### 10.5 Exportar CSV
**URL:** `/relatorios/exportar/csv`

**Descrição:** Export de dados brutos em formato CSV, gerado diretamente no navegador.

**Tipos de export:**
- **Transações** — data, tipo, ticker, quantidade, preço unitário, total (com filtros de data)
- **Proventos** — data pagamento, ticker, tipo, valor/cota, total
- **Posições** — ticker, nome, tipo, quantidade, preço médio, custo total

**Como usar:**
1. Acesse "Relatórios > Exportar Dados > [tipo] CSV"
2. Selecione o tipo de dado clicando no cartão
3. Para transações, aplique filtros de data opcionais
4. Clique em "⬇ Baixar CSV"

> O arquivo é gerado 100% no navegador — nenhum dado é enviado para servidor externo.

---

### 11. Ferramentas

**Sprint 8** — Implementado em 09/06/2026

#### 11.1 Screener de Ativos
**URL:** `/ferramentas/screener`

**Descrição:** Filtre ativos por fundamentos — Dividend Yield, P/VP, P/L e tipo.

**Funcionalidades:**
- Filtro por tipo: Ações, FIIs, ETFs, Internacionais, Renda Fixa
- Filtro DY mínimo (%), P/VP máximo, P/L máximo
- Coloração semântica: verde (atrativo), vermelho (caro), amarelo (atenção)
- Link direto para o Comparador
- Ordenado por Dividend Yield (maior primeiro)

#### 11.2 Comparador de Ativos
**URL:** `/ferramentas/comparador`

**Descrição:** Compare até 3 ativos lado a lado com dados fundamentalistas e cotação em tempo real.

**Indicadores comparados:** Preço Atual, Variação Dia, Dividend Yield, P/VP, P/L, ROE, Beta, Market Cap.

**Como usar:**
1. Selecione 1 a 3 ativos nos dropdowns
2. Clique em "Comparar"
3. O melhor valor em cada indicador é marcado com ★

#### 11.3 Calculadora de IR
**URL:** `/ferramentas/calculadora-ir`

**Descrição:** Simule o ganho/perda e imposto de renda antes de vender, usando suas posições reais.

**Funcionalidades:**
- Preencher automaticamente a partir de uma posição real (dropdown)
- Tipos: Swing Trade (15%), Day Trade (20%), FII (20%)
- Isenção automática para Swing Trade com venda ≤ R$20.000
- Calcula: custo, receita, lucro, rentabilidade, IR, lucro líquido

#### 11.4 Simulador de Aportes
**URL:** `/ferramentas/simulador`

**Descrição:** Projete o crescimento do patrimônio com juros compostos e aportes mensais.

**Funcionalidades:**
- Capital inicial + aporte mensal configurável
- Atalhos de rentabilidade: SELIC 10,5%, CDI 10,4%, IBOV 12%
- Período de 1 a 40 anos (slider)
- Correção pela inflação (valor real)
- Tabela de marcos: 1, 2, 3, 5, 10, 15, 20, 25, 30, 40 anos
- Renda passiva mensal estimada (regra dos 4% a.a.)

---

### 7. Alertas — Monitoramento de Preços

**URL:** `/dashboard/alerts`

**Descrição:** Configure alertas de preço, notícias e eventos corporativos.

**Funcionalidades:**
- Criar alertas de preço (acima/abaixo)
- Alertas de variação percentual
- Notificações de eventos corporativos
- Ativar/desativar alertas

**Como usar:**
1. Acesse "Alertas"
2. Clique em "Novo Alerta"
3. Configure: ativo, tipo, valor de referência
4. Escolha canal de notificação (email, push)
5. Ative/desative conforme necessário

**Tipos de alerta:**
- Preço acima de X
- Preço abaixo de X
- Variação > X% no dia
- Evento corporativo (dividendo, desdobramento)

**APIs:**
```bash
# Listar alertas
GET /api/alertas
Authorization: Bearer <token>

# Criar alerta
POST /api/alertas
Content-Type: application/json

{
  "ativo_id": "uuid",
  "tipo": "PRECO_ACIMA",
  "valor_referencia": 30.00,
  "ativo": true
}

# Ativar/desativar
PATCH /api/alertas/{id}/toggle
```

---

### 8. Planos de Compra — Compra Disciplinada

**URL:** `/dashboard/planos-compra`

**Descrição:** Automatize compras com inteligência artificial e disciplina.

**Funcionalidades:**
- Criar planos de compra recorrente
- Definir gatilhos de preço
- Acompanhar execução do plano
- Histórico de compras realizadas

**Como usar:**
1. Acesse "Planos de Compra"
2. Clique em "Novo Plano"
3. Configure: ativo, valor mensal, gatilhos
4. Sistema executa automaticamente quando condições são atendidas

**Estratégias:**
- Preço Alvo: compra quando preço <= X
- Média Móvel: compra quando preço cruza MM
- Buy Score: compra quando score >= X
- Recorrente: compra todo dia X do mês

**APIs:**
```bash
# Listar planos
GET /api/planos-compra
Authorization: Bearer <token>

# Criar plano
POST /api/planos-compra
Content-Type: application/json

{
  "ativo_id": "uuid",
  "valor_mensal": 1000.00,
  "estrategia": "PRECO_ALVO",
  "preco_alvo": 28.00,
  "ativo": true
}
```

---

### 9. Planos de Venda — Proteção de Lucros

**URL:** `/dashboard/planos-venda`

**Descrição:** Proteja lucros com stop gain e stop loss inteligentes.

**Funcionalidades:**
- Stop Gain: venda automática ao atingir lucro
- Stop Loss: venda automática para limitar prejuízo
- Trailing Stop: stop loss dinâmico
- Venda parcial ou total

**Como usar:**
1. Acesse "Planos de Venda"
2. Clique em "Novo Plano"
3. Configure: ativo, tipo, percentual
4. Sistema monitora e executa automaticamente

**Tipos de plano:**
- Stop Gain: vende quando lucro >= X%
- Stop Loss: vende quando prejuízo >= X%
- Trailing Stop: ajusta stop conforme preço sobe
- Preço Alvo: vende quando preço >= X

**APIs:**
```bash
# Listar planos
GET /api/planos-venda
Authorization: Bearer <token>

# Criar plano
POST /api/planos-venda
Content-Type: application/json

{
  "posicao_id": "uuid",
  "tipo": "STOP_GAIN",
  "percentual": 20.0,
  "quantidade": 100,
  "ativo": true
}
```

---

### 10. Performance — Análise de Rentabilidade

**URL:** `/dashboard/performance`

**Descrição:** Análise completa do desempenho do portfólio.

**Funcionalidades:**
- Rentabilidade por período (dia, mês, ano, total)
- Comparação com benchmarks (Ibovespa, S&P500)
- Gráfico de evolução patrimonial
- Análise de risco (volatilidade, Sharpe Ratio)

**Métricas disponíveis:**
- Rentabilidade absoluta e percentual
- CAGR (taxa anualizada)
- Volatilidade
- Sharpe Ratio
- Máximo drawdown
- Comparação com índices

**APIs:**
```bash
# Calcular performance
GET /api/performance/portfolio?periodo=12M
Authorization: Bearer <token>

# Resposta:
{
  "success": true,
  "data": {
    "rentabilidade_percentual": 15.2,
    "rentabilidade_absoluta": 38000.00,
    "cagr": 14.8,
    "volatilidade": 18.5,
    "sharpe_ratio": 0.82,
    "max_drawdown": -12.3,
    "benchmark_ibov": 12.5,
    "benchmark_sp500": 18.2
  }
}
```

---

### 11. Alocação — Distribuição de Patrimônio

**URL:** `/dashboard/alocacao`

**Descrição:** Visualize e otimize a distribuição do patrimônio.

**Funcionalidades:**
- Alocação por classe de ativo
- Alocação por mercado geográfico
- Alocação por setor econômico
- Sugestões de rebalanceamento

**Gráficos:**
- Pizza: alocação atual
- Barras: comparação com meta
- Treemap: hierarquia de alocação

**APIs:**
```bash
# Obter alocação
GET /api/portfolios/alocacao
Authorization: Bearer <token>

# Resposta:
{
  "success": true,
  "data": {
    "por_classe": {
      "ACAO": 60.0,
      "FII": 20.0,
      "RENDA_FIXA": 15.0,
      "CRIPTO": 5.0
    },
    "por_mercado": {
      "BR": 70.0,
      "US": 25.0,
      "INTL": 5.0
    },
    "por_setor": {...}
  }
}
```

---

### 12. Fluxo de Caixa — Entradas e Saídas

**URL:** `/dashboard/fluxo-caixa`

**Descrição:** Acompanhe entradas, saídas e saldo da conta.

**Funcionalidades:**
- Histórico de movimentações
- Saldo disponível por corretora
- Projeção de fluxo futuro
- Categorização de movimentações

**Tipos de movimentação:**
- Aporte (entrada de dinheiro)
- Resgate (saída de dinheiro)
- Dividendo recebido
- Taxa de corretagem
- Imposto pago

**APIs:**
```bash
# Listar movimentações
GET /api/movimentacoes-caixa?data_inicio=2026-01-01
Authorization: Bearer <token>

# Criar movimentação
POST /api/movimentacoes-caixa
Content-Type: application/json

{
  "tipo": "APORTE",
  "valor": 5000.00,
  "data": "2026-03-19",
  "corretora_id": "uuid",
  "descricao": "Aporte mensal"
}
```

---

### 13. Relatórios — Auditoria e Exportação

**URL:** `/dashboard/reports`

**Descrição:** Gere relatórios detalhados e exporte dados.

**Funcionalidades:**
- Relatório de posições
- Relatório de transações
- Relatório de IR anual
- Exportação em CSV, Excel, PDF

**Tipos de relatório:**
- Posições consolidadas
- Histórico de transações
- Proventos recebidos
- IR devido por mês
- Performance anual

**Como usar:**
1. Acesse "Relatórios"
2. Selecione tipo de relatório
3. Configure período e filtros
4. Clique em "Gerar"
5. Baixe em formato desejado

**APIs:**
```bash
# Listar relatórios
GET /api/relatorios
Authorization: Bearer <token>

# Gerar relatório
POST /api/relatorios/gerar
Content-Type: application/json

{
  "tipo": "POSICOES",
  "formato": "PDF",
  "data_inicio": "2026-01-01",
  "data_fim": "2026-12-31"
}

# Download
GET /api/relatorios/{id}/download
```

---

### 14. Comparador — Análise Comparativa

**URL:** `/dashboard/comparador`

**Descrição:** Compare múltiplos ativos lado a lado.

**Funcionalidades:**
- Comparar até 4 ativos simultaneamente
- Indicadores fundamentalistas
- Gráficos de cotação
- Ranking de Buy Score

**Indicadores comparados:**
- Preço atual
- P/L, P/VP, ROE, Dividend Yield
- Margem líquida, ROIC
- Crescimento de receita
- Buy Score

**Como usar:**
1. Acesse "Comparador"
2. Adicione ativos (até 4)
3. Visualize comparação lado a lado
4. Analise gráficos e indicadores

---

### 15. Educação — Insights e Aprendizado

**URL:** `/dashboard/educacao`

**Descrição:** Aprenda sobre investimentos e tome decisões mais inteligentes.

**Conteúdo:**
- Artigos sobre estratégias de investimento
- Glossário de termos financeiros
- Tutoriais em vídeo
- Análises de mercado
- Dicas de especialistas

**Categorias:**
- Iniciante: conceitos básicos
- Intermediário: estratégias avançadas
- Avançado: análise técnica e fundamentalista
- Fiscal: IR, IOF, tributação

---

### 16. Configurações — Personalização

**URL:** `/dashboard/configuracoes`

**Descrição:** Personalize sua experiência e gerencie sua conta.

**Funcionalidades:**
- Dados pessoais
- Preferências de moeda
- Notificações (email, push)
- Segurança (senha, 2FA)
- Integrações (corretoras, bancos)

**Seções:**
1. **Perfil:** nome, email, foto
2. **Preferências:** moeda padrão, idioma, tema
3. **Notificações:** alertas, relatórios, newsletters
4. **Segurança:** alterar senha, 2FA, sessões ativas
5. **Integrações:** conectar corretoras, importar dados

---

## 🔄 Fluxos Principais

### Fluxo 1: Primeiro Acesso

1. **Login** → `/auth/login`
2. **Dashboard** → Visualizar resumo vazio
3. **Criar Portfolio** → `/dashboard/portfolios` → "Nova Carteira"
4. **Registrar Transação** → `/dashboard/transactions` → "Nova Transação"
5. **Visualizar Posições** → Dashboard atualizado com dados

### Fluxo 2: Compra de Ativo

1. **Buy Signals** → Identificar oportunidade
2. **Analisar Ativo** → Ver detalhes e indicadores
3. **Criar Plano de Compra** → Automatizar compra
4. **Registrar Transação** → Após execução
5. **Acompanhar Performance** → Dashboard e Performance

### Fluxo 3: Declaração de IR

1. **Imposto de Renda** → Selecionar ano
2. **Revisar Cálculos** → Verificar IR devido por mês
3. **Gerar DARFs** → Para meses com IR >= R$ 10,00
4. **Exportar Relatório** → Para declaração anual
5. **Acompanhar Prejuízos** → Saldo para compensação futura

### Fluxo 4: Rebalanceamento

1. **Alocação** → Visualizar distribuição atual
2. **Comparar com Meta** → Identificar desvios
3. **Planos de Venda** → Vender ativos sobreposicionados
4. **Planos de Compra** → Comprar ativos subposicionados
5. **Monitorar** → Acompanhar execução

---

## 🔌 APIs e Integrações

### Base URL

```
Desenvolvimento: http://localhost:5000/api
Produção: https://seu-dominio.com/api
```

### Autenticação

Todas as APIs (exceto login/register) requerem JWT Bearer Token:

```bash
Authorization: Bearer <seu_token_jwt>
```

### Endpoints Principais

| Módulo | Endpoint | Método | Descrição |
|--------|----------|--------|-----------|
| **Auth** | `/auth/login` | POST | Login |
| **Portfolios** | `/portfolios` | GET | Listar |
| **Portfolios** | `/portfolios/dashboard` | GET | Dashboard |
| **Transações** | `/transacoes` | GET/POST | CRUD |
| **Ativos** | `/ativos` | GET | Listar |
| **Cotações** | `/cotacoes/ativo/{ticker}` | GET | Cotação |
| **Proventos** | `/proventos` | GET | Listar |
| **IR** | `/ir/calcular` | GET | Calcular |
| **Alertas** | `/alertas` | GET/POST | CRUD |
| **Buy Signals** | `/buy-signals/watchlist-top` | GET | Top oportunidades |
| **Performance** | `/performance/portfolio` | GET | Métricas |
| **Relatórios** | `/relatorios/gerar` | POST | Gerar |

### Documentação Completa

Consulte `docs/API_REFERENCE.md` para documentação completa de todas as APIs.

---

## ❓ Perguntas Frequentes

### Como importar transações da B3?

1. Baixe o arquivo Excel da B3 (Extrato de Negociação)
2. Acesse "Configurações" → "Integrações"
3. Clique em "Importar B3"
4. Selecione o arquivo
5. Sistema processa e cria transações automaticamente

### Como funciona o cálculo de IR?

O sistema calcula IR automaticamente considerando:
- Tipo de operação (day trade vs swing trade)
- Prazo de aplicação (renda fixa)
- Isenção de R$ 20.000/mês (ações)
- Compensação de prejuízos
- Acúmulo de valores < R$ 10,00

### Posso usar em múltiplas moedas?

Sim! O sistema suporta BRL, USD e EUR:
- Cada portfolio tem uma moeda base
- Conversão automática para consolidação
- Toggle de moeda no dashboard
- Cotações atualizadas diariamente

### Como funciona o multi-tenancy?

Para assessoras:
- Cada assessora tem um ID único
- Usuários vinculados à assessora
- Dados isolados por assessora
- Dashboard consolidado por cliente

### Quais tipos de ativos são suportados?

**15 tipos de ativos:**
- Ações (BR, US, INTL)
- FIIs (Fundos Imobiliários)
- ETFs (BR, US)
- Stocks (US, INTL)
- REITs (US)
- Bonds (US)
- Tesouro Direto
- CDB, LCI, LCA
- Debêntures
- Fundos de Investimento
- Criptomoedas
- Commodities

---

## 📞 Suporte

**Documentação:**
- `docs/INDEX.md` — Índice geral
- `docs/API_REFERENCE.md` — APIs completas
- `docs/ARCHITECTURE.md` — Arquitetura do sistema

**Logs:**
- Backend: `podman logs -f exitus-backend`
- Frontend: `podman logs -f exitus-frontend`

**Troubleshooting:**
- Consulte `docs/OPERATIONS_RUNBOOK.md`
- Verifique `docs/LESSONS_LEARNED.md` para erros comuns

---

*Última atualização: 19/03/2026 — v0.9.2*  
*Responsável: Elielson Fontanezi + Cascade AI*
