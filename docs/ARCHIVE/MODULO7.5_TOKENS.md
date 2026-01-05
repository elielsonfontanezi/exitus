# MÓDULO 7.5 - GUIA DE CONFIGURAÇÃO DE TOKENS API

**Versão:** 1.0  
**Data:** 09/12/2025  
**Nível:** Intermediário/Avançado

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [brapi.dev (B3)](#1-brapidev-b3)
3. [Alpha Vantage](#2-alpha-vantage)
4. [Finnhub](#3-finnhub)
5. [Polygon.io](#4-polygonio-opcional)
6. [yfinance](#5-yfinance-sem-token)
7. [Configuração .env](#configuração-env)
8. [Testes](#testes)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 VISÃO GERAL

O Exitus M7.5 suporta **5 provedores de cotações** com fallback automático:

| Provider | Mercado | Token Obrigatório | Rate Limit FREE | Custo Premium |
|----------|---------|-------------------|-----------------|---------------|
| **brapi.dev** | 🇧🇷 B3 | ❌ Não | 10 req/min | R$ 19/mês (60 req/min) |
| **yfinance** | 🌐 Global | ❌ Não | ~5-10 req/min | Grátis |
| **Alpha Vantage** | 🇺🇸 US/EU | ✅ Sim | 500 req/dia | $50/mês (ilimitado) |
| **Finnhub** | 🇺🇸 US/EU | ✅ Sim | 60 req/min | $40/mês (300 req/min) |
| **Polygon.io** | 🇺🇸 US | ✅ Sim | ❌ Pago | $99/mês |

**Recomendação mínima:** brapi.dev (FREE) + yfinance (backup)  
**Recomendação produção:** brapi.dev PREMIUM + Alpha Vantage FREE

---

## 1️⃣ brapi.dev (B3)

### **Descrição**
API brasileira especializada em **B3 (bolsa brasileira)**. Melhor provider para ativos brasileiros (PETR4, VALE3, etc).

### **Registro**
1. Acesse: https://brapi.dev/
2. Clique em **"Criar Conta"**
3. Preencha email + senha
4. Confirme email
5. Acesse **Dashboard → API Keys**
6. Copie seu token

### **Planos**
```
┌─────────────────────────────────────────────┐
│ FREE (Grátis)                               │
│ - 10 requisições/minuto                     │
│ - Cotações em tempo real (delay 15min)     │
│ - Histórico 1 ano                           │
│ - ✅ SUFICIENTE para uso pessoal            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PREMIUM (R$ 19/mês)                         │
│ - 60 requisições/minuto                     │
│ - Cotações em tempo real                    │
│ - Histórico 5 anos                          │
│ - Fundamentalista (DY, P/L, ROE)            │
│ - ✅ RECOMENDADO para produção              │
└─────────────────────────────────────────────┘
```

### **Configuração**
```bash
# .env
BRAPI_TOKEN=seu_token_aqui_ex_abc123xyz
```

### **Teste**
```bash
curl "https://brapi.dev/api/quote/PETR4?token=SEU_TOKEN" | jq .
```

**Response esperado:**
```json
{
  "results": [{
    "symbol": "PETR4",
    "regularMarketPrice": 31.46,
    "regularMarketChangePercent": -0.632,
    "regularMarketVolume": 3764900
  }]
}
```

---

## 2️⃣ Alpha Vantage

### **Descrição**
API global para cotações US, Europa, Ásia. **500 requisições/dia grátis** (suficiente para uso pessoal).

### **Registro**
1. Acesse: https://www.alphavantage.co/support/#api-key
2. Preencha email + nome
3. **Token enviado IMEDIATAMENTE no email** ✅
4. Copie token (ex: `DEMO` ou `ABC123XYZ`)

### **Planos**
```
┌─────────────────────────────────────────────┐
│ FREE (Grátis)                               │
│ - 500 requisições/dia (= 20 req/hora)      │
│ - 5 requisições/minuto                      │
│ - Cotações globais                          │
│ - ✅ ÓTIMO para backup                      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ PREMIUM ($50/mês)                           │
│ - Requisições ilimitadas                    │
│ - 120 req/minuto                            │
│ - Dados intraday (1min, 5min)              │
└─────────────────────────────────────────────┘
```

### **Configuração**
```bash
# .env
ALPHAVANTAGE_TOKEN=seu_token_aqui
```

### **Teste**
```bash
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=SEU_TOKEN" | jq .
```

**Response esperado:**
```json
{
  "Global Quote": {
    "01. symbol": "AAPL",
    "05. price": "195.50",
    "10. change percent": "-0.50%"
  }
}
```

---

## 3️⃣ Finnhub

### **Descrição**
API premium para stocks US/EU. **60 req/min grátis** (melhor rate limit FREE).

### **Registro**
1. Acesse: https://finnhub.io/register
2. Preencha email + senha
3. Confirme email
4. **Token disponível imediatamente no dashboard** ✅
5. Copie token

### **Planos**
```
┌─────────────────────────────────────────────┐
│ FREE (Grátis)                               │
│ - 60 requisições/minuto                     │
│ - Cotações US + EU                          │
│ - WebSocket real-time                       │
│ - ✅ EXCELENTE rate limit                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ STARTER ($40/mês)                           │
│ - 300 requisições/minuto                    │
│ - Dados históricos ilimitados               │
└─────────────────────────────────────────────┘
```

### **Configuração**
```bash
# .env
FINNHUB_TOKEN=seu_token_aqui
```

### **Teste**
```bash
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=SEU_TOKEN" | jq .
```

**Response esperado:**
```json
{
  "c": 195.50,    // current price
  "d": -0.98,     // change
  "dp": -0.50,    // percent change
  "h": 197.20,    // high
  "l": 194.50,    // low
  "o": 196.00,    // open
  "pc": 196.48    // previous close
}
```

---

## 4️⃣ Polygon.io (Opcional)

### **Descrição**
API premium US. **NÃO possui tier FREE** (mínimo $99/mês). **Não obrigatório** para Exitus.

### **Registro**
1. Acesse: https://polygon.io/pricing
2. Escolha plano **Starter ($99/mês)**
3. Preencha cartão de crédito
4. Token no dashboard

### **Planos**
```
┌─────────────────────────────────────────────┐
│ STARTER ($99/mês)                           │
│ - 100.000 requisições/mês                   │
│ - Cotações US + Crypto                      │
│ - Histórico 2 anos                          │
└─────────────────────────────────────────────┘
```

### **Configuração**
```bash
# .env (deixar vazio se não assinar)
POLYGON_TOKEN=
```

---

## 5️⃣ yfinance (Sem Token)

### **Descrição**
Wrapper Python não-oficial do Yahoo Finance. **SEM token**, mas rate limit agressivo (~5-10 req/min).

### **Configuração**
```bash
# Nenhuma configuração necessária (já instalado)
pip install yfinance
```

### **Limitações**
- ❌ Rate limit 429 frequente
- ❌ Sem SLA/suporte
- ❌ Pode quebrar sem aviso
- ✅ Grátis
- ✅ Suporta global (incluindo .SA para B3)

### **Uso no Exitus**
```python
# Fallback automático (não precisa configurar)
import yfinance as yf
stock = yf.Ticker('PETR4.SA')
info = stock.fast_info  # Mais rápido que .info
```

---

## 📝 CONFIGURAÇÃO .env

### **Arquivo Completo**
```bash
# ==============================================
# M7.5 COTAÇÕES - TOKENS API
# ==============================================

# 1️⃣ brapi.dev (B3 - Primário)
# FREE: 10 req/min | PREMIUM (R$19/mês): 60 req/min
# Deixar vazio = usar FREE tier
BRAPI_TOKEN=

# 2️⃣ Alpha Vantage (US/EU - Fallback)
# FREE: 500 req/dia (20 req/hora)
# Token DEMO para testes (trocar por real)
ALPHAVANTAGE_TOKEN=demo

# 3️⃣ Finnhub (US/EU - Fallback)
# FREE: 60 req/min
# Deixar vazio = desabilitar provider
FINNHUB_TOKEN=

# 4️⃣ Polygon.io (US - Opcional)
# PAGO obrigatório: $99/mês
# Deixar vazio = ignorar provider
POLYGON_TOKEN=

# 5️⃣ yfinance (Global - Fallback automático)
# Sem token necessário
# Rate limit: ~5-10 req/min
```

### **Copiar .env.example**
```bash
cd backend
cp .env.example .env
nano .env  # Editar tokens
```

---

## 🧪 TESTES

### **Teste 1: Verificar Tokens Carregados**
```bash
podman exec -it exitus-backend python3 << 'PYTHON'
import os
from dotenv import load_dotenv
load_dotenv()

print("BRAPI_TOKEN:", os.getenv('BRAPI_TOKEN', 'VAZIO'))
print("ALPHAVANTAGE_TOKEN:", os.getenv('ALPHAVANTAGE_TOKEN', 'VAZIO'))
print("FINNHUB_TOKEN:", os.getenv('FINNHUB_TOKEN', 'VAZIO'))
PYTHON
```

### **Teste 2: API Individual (brapi.dev)**
```bash
TOKEN_BRAPI="seu_token_aqui"
curl "https://brapi.dev/api/quote/PETR4?token=$TOKEN_BRAPI" | jq '.results[0].regularMarketPrice'
# Output esperado: 31.46
```

### **Teste 3: Exitus Endpoint (com fallback)**
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 | jq '{ticker, preco_atual, provider}'

# Output esperado:
# {
#   "ticker": "PETR4",
#   "preco_atual": 31.46,
#   "provider": "brapi.dev"
# }
```

---

## 🐛 TROUBLESHOOTING

### **Erro: "Invalid API key"**
**Causa:** Token incorreto ou expirado.

**Solução:**
1. Verificar token no dashboard do provider
2. Copiar token completo (sem espaços)
3. Atualizar `.env`
4. Reiniciar container: `podman restart exitus-backend`

---

### **Erro: Rate limit 429**
**Causa:** Excedeu limite de requisições.

**Solução:**
```bash
# Ver logs provider usado
podman logs exitus-backend --tail 50 | grep "provider"

# Se brapi.dev FREE (10 req/min):
# - Upgrade para PREMIUM (60 req/min)
# - Ou aguardar 1 minuto

# Se yfinance (5-10 req/min):
# - Configurar brapi.dev como primário
# - Cache PostgreSQL reduz chamadas em 85%
```

---

### **Erro: "APIs indisponíveis"**
**Causa:** Todas APIs falharam (raro).

**Solução:**
1. Verificar internet: `ping 8.8.8.8`
2. Verificar tokens configurados
3. Testar APIs direto (cURL)
4. Consultar status: https://status.brapi.dev/

---

## 📊 COMPARAÇÃO PROVIDERS

### **Melhor para B3 (Ações Brasileiras)**
🥇 **brapi.dev PREMIUM** (R$19/mês) - 60 req/min  
🥈 **brapi.dev FREE** - 10 req/min  
🥉 **yfinance** (.SA) - ~5 req/min

### **Melhor para US Stocks**
🥇 **Finnhub FREE** - 60 req/min  
🥈 **Alpha Vantage FREE** - 500 req/dia  
🥉 **yfinance** - ~5 req/min

### **Melhor Custo-Benefício**
🥇 **brapi.dev FREE** + **Alpha Vantage FREE** = R$ 0/mês  
🥈 **brapi.dev PREMIUM** + **Finnhub FREE** = R$ 19/mês  
🥉 **Polygon Starter** = $99/mês (desnecessário)

---

## 🎯 RECOMENDAÇÕES POR CENÁRIO

### **Cenário 1: Uso Pessoal (0-10 acessos/dia)**
```bash
BRAPI_TOKEN=            # FREE tier suficiente
ALPHAVANTAGE_TOKEN=demo # Backup
FINNHUB_TOKEN=          # Opcional
```
**Custo:** R$ 0/mês ✅

---

### **Cenário 2: Família/Amigos (10-50 acessos/dia)**
```bash
BRAPI_TOKEN=seu_token_premium      # R$ 19/mês
ALPHAVANTAGE_TOKEN=seu_token_free  # Backup
FINNHUB_TOKEN=seu_token_free       # Backup US
```
**Custo:** R$ 19/mês ✅

---

### **Cenário 3: Produção Empresa (100+ acessos/dia)**
```bash
BRAPI_TOKEN=seu_token_premium          # R$ 19/mês
ALPHAVANTAGE_TOKEN=seu_token_premium   # $50/mês
FINNHUB_TOKEN=seu_token_starter        # $40/mês
```
**Custo:** ~R$ 550/mês

---

## 📚 LINKS ÚTEIS

- brapi.dev: https://brapi.dev/docs
- Alpha Vantage: https://www.alphavantage.co/documentation/
- Finnhub: https://finnhub.io/docs/api
- Polygon: https://polygon.io/docs
- yfinance GitHub: https://github.com/ranaroussi/yfinance

---

**Última Atualização:** 09/12/2025  
**Suporte:** Sistema Exitus
