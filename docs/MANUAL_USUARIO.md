# Manual do Usuário — Sistema Exitus v0.9.2

> **Versão:** v0.9.2  
> **Data:** 19/03/2026  
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

## 🔐 Acesso ao Sistema

### 1. Login

**URL:** `http://localhost:8080/auth/login`

**Credenciais padrão:**
- **Usuário:** `admin`
- **Senha:** `admin123`

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

**URL:** `/dashboard/buy-signals`

**Descrição:** Identifica as melhores oportunidades de compra usando análise fundamentalista com IA.

**Funcionalidades:**
- Lista de ativos com Buy Score (0-100)
- Margem de segurança calculada
- Filtros por mercado e classe de ativo
- Análise detalhada por ativo

**Como usar:**
1. Acesse "Buy Signals" no menu ou dashboard
2. Visualize a lista de ativos ranqueados por Buy Score
3. Clique em "Analisar" para ver detalhes do ativo
4. Use os filtros para refinar a busca

**Regras de Negócio:**
- Buy Score > 70: Forte compra
- Buy Score 50-70: Compra moderada
- Buy Score < 50: Aguardar
- Margem de segurança: diferença entre preço atual e preço teto

**API:**
```bash
GET /api/buy-signals/watchlist-top
Authorization: Bearer <token>

# Resposta:
{
  "success": true,
  "data": [
    {
      "ticker": "PETR4",
      "nome": "Petrobras PN",
      "mercado": "BR",
      "buy_score": 85,
      "margem_seguranca": 25.5,
      "preco_atual": 28.50,
      "preco_teto": 38.20
    }
  ]
}
```

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

### 4. Ativos — Análise e Cotações

**URL:** `/dashboard/assets`

**Descrição:** Visualize e analise todos os ativos disponíveis no sistema.

**Funcionalidades:**
- Lista de ativos com cotações atualizadas
- Busca por ticker ou nome
- Filtros por mercado, classe, setor
- Análise fundamentalista detalhada

**Como usar:**
1. Acesse "Ativos" no menu
2. Use a busca para encontrar um ativo
3. Clique no ativo para ver análise completa
4. Visualize: cotação, indicadores, histórico

**Dados disponíveis:**
- Cotação atual e histórico
- Indicadores fundamentalistas (P/L, P/VP, ROE, etc.)
- Dividendos históricos
- Eventos corporativos
- Buy Score e análise de valuation

**APIs:**
```bash
# Listar ativos
GET /api/ativos?mercado=BR&classe=ACAO
Authorization: Bearer <token>

# Obter ativo específico
GET /api/ativos/{id}

# Cotação atual
GET /api/cotacoes/ativo/{ticker}
```

---

### 5. Proventos — Dividendos e JCP

**URL:** `/dashboard/dividends`

**Descrição:** Acompanhe dividendos, JCP e eventos corporativos.

**Funcionalidades:**
- Histórico de proventos recebidos
- Calendário de pagamentos futuros
- Filtros por ativo, tipo, data
- Projeção de renda passiva

**Como usar:**
1. Acesse "Proventos" no menu
2. Visualize histórico de recebimentos
3. Confira calendário de próximos pagamentos
4. Filtre por ativo ou período

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

### 6. Imposto de Renda — Calculadora e DARFs

**URL:** `/dashboard/imposto-renda`

**Descrição:** Calcule IR devido, gere DARFs e acompanhe compensação de prejuízos.

**Funcionalidades:**
- Calculadora de IR por mês
- Geração de DARFs automática
- Compensação de prejuízos
- Relatório anual para declaração
- Acúmulo de DARF < R$ 10,00

**Como usar:**
1. Acesse "Imposto de Renda"
2. Selecione mês/ano para cálculo
3. Visualize IR devido por categoria
4. Gere DARF se valor >= R$ 10,00
5. Acompanhe saldo de prejuízos

**Regras de Negócio:**
- Day Trade: 20% sobre lucro
- Swing Trade: 15% sobre lucro (ações/FIIs)
- Renda Fixa: 15-22.5% conforme prazo
- Isenção: vendas < R$ 20.000/mês (ações)
- Acúmulo: IR < R$ 10,00 acumula para próximo mês
- Compensação: prejuízos compensam lucros da mesma categoria

**APIs:**
```bash
# Calcular IR do mês
GET /api/ir/calcular?ano=2026&mes=3
Authorization: Bearer <token>

# Gerar DARF
POST /api/ir/gerar-darf
Content-Type: application/json

{
  "ano": 2026,
  "mes": 3,
  "codigo_receita": "6015"
}

# Consultar saldo de prejuízos
GET /api/ir/saldo-prejuizo
```

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
- `docs/README.md` — Índice geral
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
