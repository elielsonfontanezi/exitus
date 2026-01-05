# 📊 PLANO COMPLETO - APIs EXTERNAS + CÁLCULOS FINANCEIROS

**Exitus** - Sistema de Controle e Análise de Investimentos Global  
**Data:** 08/12/2025  
**Status:** Planejamento M7.5 / M8

---

## 🌍 5 APIS EXTERNAS PLANEJADAS

### **1. yfinance (Yahoo Finance)** 🥇
```python
Tipo: Biblioteca Python gratuita
URL: https://query1.finance.yahoo.com
Autenticação: ❌ Não requer
Rate Limit: 2000/hora
Prioridade: 1 (ALTA - usar primeiro)
Status: ✅ ATIVA

📌 Cobertura:
- ✅ B3 (Brasil): PETR4.SA, VALE3.SA, ITUB4.SA
- ✅ NYSE/NASDAQ: AAPL, MSFT, GOOGL
- ✅ Criptos: BTC-USD, ETH-USD
- ✅ Histórico completo + dividendos
- ✅ Dados fundamentalistas (P/L, DY, ROE)

🎯 Usar para: Preços real-time, histórico, dividendos globais
```

### **2. brapi.dev (Brasil API)** 🇧🇷
```python
Tipo: API brasileira gratuita
URL: https://brapi.dev/api
Autenticação: ❌ Não requer
Rate Limit: 100/minuto
Prioridade: 1 (ALTA - especializada B3)
Status: ✅ ATIVA

📌 Cobertura:
- ✅ B3 especializada (tempo real)
- ✅ FIIs: HGLG11, MXRF11, KNRI11
- ✅ Ações: PETR4, VALE3, ITUB4
- ✅ Indicadores fundamentalistas
- ✅ Dividend Yield atualizado

🎯 Usar para: Dados B3 em tempo real, DY de FIIs
```

### **3. Alpha Vantage** 🔑
```python
Tipo: API gratuita com chave
URL: https://www.alphavantage.co/query
Autenticação: ✅ API Key obrigatória
Rate Limit: 5/minuto (plano free)
Prioridade: 2 (MÉDIA - fallback)
Status: ✅ ATIVA

📌 Cobertura:
- ✅ Mercados globais (US, EU, ASIA)
- ✅ Criptomoedas
- ✅ Forex (câmbio)
- ✅ Indicadores técnicos (RSI, MACD, Bollinger)
- ✅ Histórico 20+ anos

🎯 Usar para: Histórico longo, indicadores técnicos, forex
```

### **4. Finnhub** 🌐
```python
Tipo: API com plano gratuito
URL: https://finnhub.io/api/v1
Autenticação: ✅ API Key obrigatória
Rate Limit: 60/minuto (free tier)
Prioridade: 2 (MÉDIA - notícias)
Status: ✅ ATIVA

📌 Cobertura:
- ✅ Mercados globais (US, EU, ASIA)
- ✅ **Notícias financeiras** (diferencial!)
- ✅ Calendário econômico
- ✅ Earnings reports
- ✅ Análises de analistas

🎯 Usar para: Notícias financeiras, earnings, sentiment analysis
```

### **5. IEX Cloud** 🇺🇸
```python
Tipo: API focada em mercado americano
URL: https://cloud.iexapis.com/stable
Autenticação: ✅ API Key obrigatória
Rate Limit: 50.000/mês (free tier)
Prioridade: 3 (BAIXA - fallback US)
Status: ✅ ATIVA

📌 Cobertura:
- ✅ NYSE/NASDAQ completo
- ✅ Dados intraday (1min, 5min)
- ✅ Balanços financeiros
- ✅ Insider trading
- ✅ IPOs

🎯 Usar para: Mercado US, dados intraday, fundamentalistas US
```

---

## 📈 CÁLCULOS FINANCEIROS AVANÇADOS (M7)

### **1. IRR - Taxa Interna de Retorno** 💰
```python
Método: Newton-Raphson (iterativo)
Entrada: Series de fluxos de caixa datados [(data, valor), ...]
Saída: Taxa anual (%)

Exemplo:
[
  (2025-01-01, -10000),  # Investimento inicial
  (2025-06-01, +500),    # Dividendo
  (2025-12-31, +11000)   # Resgate
]
IRR = 12.5% ao ano

🎯 Usar para: Rentabilidade real de investimentos
```

### **2. Índice de Sharpe** 📊
```python
Fórmula: (Retorno Portfolio - Taxa Livre Risco) / Desvio Padrão Retornos
Entrada:
  - Série de retornos diários/mensais
  - Taxa livre de risco (Selic: 3% a.a. / 12 = 0.25% a.m.)
Saída: Número (quanto maior, melhor)
  - < 1.0 → Ruim
  - 1.0-2.0 → Bom
  - > 2.0 → Excelente

Exemplo:
Retorno portfolio: 18% a.a.
Taxa livre risco: 3% a.a.
Volatilidade: 10% a.a.
Sharpe = (18% - 3%) / 10% = 1.5 ✅ BOM

🎯 Usar para: Retorno ajustado ao risco
```

### **3. Índice de Sortino** 📉
```python
Similar ao Sharpe, mas penaliza APENAS desvio negativo (downside)
Fórmula: (Retorno Portfolio - Target Return) / Downside Deviation
Entrada:
  - Série de retornos
  - Target return (ex: 10% a.a.)
Saída: Número (comparável a Sharpe)

Diferença:
- Sharpe: penaliza volatilidade total (boa e ruim)
- Sortino: penaliza APENAS quedas (downside)

🎯 Usar para: Risco de perda (melhor que Sharpe)
```

### **4. Volatilidade (Desvio Padrão)** 📈
```python
Fórmula: Desvio padrão dos retornos × √252 (dias úteis/ano)
Entrada: Série de preços diários
Saída: % ao ano (anualizado)

Exemplo:
Retornos diários: [0.5%, -0.3%, 0.8%, -0.2%, ...]
Desvio padrão diário: 1.2%
Volatilidade anual: 1.2% × √252 = 19.05% a.a.

🎯 Usar para: Medir risco do ativo
```

### **5. Max Drawdown (Perda Máxima)** 📉
```python
Fórmula: Maior queda acumulada do pico histórico
Entrada: Série de preços cronológica
Saída: % de queda máxima observada

Exemplo:
Preços: [100, 110, 105, 90, 95, 120]
Pico: 110
Vale: 90
Max Drawdown = (90 - 110) / 110 = -18.18%

🎯 Usar para: Pior cenário histórico, risco de perda
```

### **6. Beta (Risco Sistemático)** 🌐
```python
Fórmula: Covariância(Ativo, Mercado) / Variância(Mercado)
Entrada:
  - Retornos do ativo
  - Retornos do benchmark (IBOV, S&P500)
Saída: Número
  - Beta = 1.0 → Move igual ao mercado
  - Beta > 1.0 → Mais volátil que mercado
  - Beta < 1.0 → Menos volátil que mercado

Exemplo:
PETR4 Beta = 1.3 → 30% mais volátil que IBOV

🎯 Usar para: Correlação com mercado
```

### **7. Alfa de Jensen** 🎯
```python
Fórmula: Retorno Ativo - [Taxa Livre Risco + Beta × (Retorno Mercado - Taxa Livre Risco)]
Entrada:
  - Retorno do ativo
  - Beta calculado
  - Retorno do benchmark
Saída: % (alfa positivo = gestor bateu mercado)

Exemplo:
Retorno ativo: 18% a.a.
Beta: 1.2
Retorno IBOV: 12% a.a.
Taxa livre risco: 3% a.a.
Alfa = 18% - [3% + 1.2 × (12% - 3%)] = 4.2% ✅ BATEU MERCADO

🎯 Usar para: Avaliar gestor/estratégia
```

### **8. Dividend Yield (DY)** 💵
```python
Fórmula: (Soma Dividendos 12 meses / Preço Atual) × 100
Entrada:
  - Histórico de dividendos (12 meses)
  - Preço atual da ação/FII
Saída: % ao ano

Exemplo:
PETR4:
Dividendos 12m: R$ 3.50
Preço atual: R$ 38.50
DY = (3.50 / 38.50) × 100 = 9.09% a.a.

🎯 Usar para: Renda passiva, comparar FIIs/ações
```

---

## 🏗️ ARQUITETURA INTEGRAÇÃO M7.5/M8

```
┌─────────────────────────────────────────────────┐
│         FRONTEND (HTMX + TailwindCSS)           │
│  Dashboard Real-time | Gráficos Chart.js       │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│      BACKEND FLASK (M7 Services)                │
│  - RelatorioService (IRR, Sharpe, Sortino)      │
│  - AlertaService (preço, DY, volatilidade)      │
│  - ProjecaoService (renda passiva 12m)          │
│  - AnaliseService (benchmarks, correlação)      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│     COTACAO SERVICE (M7.5 - NOVO!)              │
│  - Prioridade: yfinance > brapi > Alpha Vantage │
│  - Cache Redis (30s TTL)                        │
│  - Fallback automático                          │
│  - Rate limit respeitado                        │
└──────────────────┬──────────────────────────────┘
                   │
       ┌───────────┼───────────┬──────────┐
       │           │           │          │
┌──────▼─────┐ ┌──▼──────┐ ┌──▼─────┐ ┌──▼──────┐
│ yfinance   │ │brapi.dev│ │Alpha   │ │Finnhub  │
│ (prioridade│ │(B3 real)│ │Vantage │ │(notícias│
│    1)      │ │         │ │        │ │   )     │
└────────────┘ └─────────┘ └────────┘ └─────────┘
```

---

## 🎯 PRÓXIMOS PASSOS

### **M7.5 - APIs Cotações Live (30min)**
```
1. Criar CotacaoService (backend/app/services/)
2. Implementar 5 endpoints:
   - GET /api/cotacoes/{ticker}
   - GET /api/historico/{ticker}?periodo=1y
   - GET /api/batch?symbols=PETR4,VALE3,AAPL
   - GET /api/dividendos/{ticker}
   - GET /api/fundamentalista/{ticker}
3. Frontend: Dashboard preços live + gráficos
4. Testes com PETR4, AAPL, BTC-USD
```

### **M8 - IA Portfolio Optimizer (futuro)**
```
- Usa dados reais das APIs
- Reinforcement Learning (Q-Learning)
- Otimização Markowitz (fronteira eficiente)
- Rebalanceamento automático
- Backtesting
```

---

## 🏆 DIFERENCIAIS EXITUS

```
✅ 5 APIs integradas (redundância + cobertura global)
✅ 8 cálculos financeiros avançados (IRR, Sharpe, Sortino, Beta, Alfa)
✅ Dados B3 + US + Cripto (cobertura completa)
✅ Real-time + Histórico 20+ anos
✅ Notícias financeiras (Finnhub)
✅ Fallback automático (prioridade inteligente)
✅ Cache Redis (performance)
✅ Rate limit respeitado (compliance)
```

**Exitus = Bloomberg + TradingView + Portfolio Visualizer OPEN SOURCE!** 🚀

---

**Criado:** 08/12/2025  
**Próximo:** M7.5 APIs Live OU M8 IA Optimizer  
