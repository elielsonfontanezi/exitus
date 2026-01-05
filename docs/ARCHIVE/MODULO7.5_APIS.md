# MÓDULO 7.5 - DOCUMENTAÇÃO API COTAÇÕES

**Versão:** 1.0  
**Base URL:** `http://localhost:5000/api/cotacoes`  
**Autenticação:** Bearer Token (JWT)  
**Content-Type:** `application/json`

---

## 📋 ÍNDICE

1. [Autenticação](#autenticação)
2. [Endpoints](#endpoints)
3. [Schemas Response](#schemas-response)
4. [Códigos de Status](#códigos-de-status)
5. [Rate Limiting](#rate-limiting)
6. [Exemplos cURL](#exemplos-curl)

---

## 🔐 AUTENTICAÇÃO

Todos os endpoints requerem JWT token no header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Obter Token:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token'
```

---

## 🚀 ENDPOINTS

### **1. GET /api/cotacoes/{ticker}**

Retorna cotação em tempo real (delay 15min) de um ativo específico.

**Parâmetros:**
- `ticker` (path, required) - Código do ativo (ex: PETR4, VALE3, AAPL)

**Response 200 OK (API externa):**
```json
{
  "ticker": "PETR4",
  "preco_atual": 31.46,
  "variacao_percentual": -0.632,
  "volume": 3764900,
  "dy_12m": 0.0,
  "pl": 0.0,
  "provider": "brapi.dev",
  "cache_ttl_minutes": 15,
  "success": true
}
```

**Response 200 OK (cache PostgreSQL):**
```json
{
  "ticker": "PETR4",
  "preco_atual": 31.46,
  "variacao_percentual": 0,
  "volume": 0,
  "dy_12m": 0.0,
  "pl": 0.0,
  "provider": "cache_postgresql",
  "cache_age_minutes": 3,
  "cache_valid_until": "2025-12-09T11:45:00",
  "success": true
}
```

**Response 200 OK (fallback banco):**
```json
{
  "ticker": "AAPL",
  "preco_atual": 195.50,
  "dy_12m": 0.5,
  "pl": 28.5,
  "provider": "database_fallback",
  "warning": "APIs indisponíveis - usando dados em cache",
  "last_update": "2025-12-09T10:30:00",
  "success": true
}
```

**Response 404 Not Found:**
```json
{
  "error": "Ativo XYZ123 não encontrado"
}
```

**Response 500 Internal Server Error:**
```json
{
  "error": "Database connection failed",
  "success": false
}
```

---

### **2. GET /api/cotacoes/batch**

Retorna cotações de múltiplos ativos em uma única requisição.

**Query Parameters:**
- `symbols` (query, optional) - Lista de tickers separados por vírgula (default: "PETR4,VALE3")
- **Limite:** Máximo 10 ativos por requisição

**Response 200 OK:**
```json
{
  "PETR4": {
    "ticker": "PETR4",
    "preco_atual": 31.46,
    "provider": "brapi.dev",
    "success": true
  },
  "VALE3": {
    "ticker": "VALE3",
    "preco_atual": 69.39,
    "provider": "cache_postgresql",
    "cache_age_minutes": 5,
    "success": true
  },
  "AAPL": {
    "ticker": "AAPL",
    "preco_atual": 195.50,
    "provider": "yfinance_fast",
    "success": true
  },
  "XYZ123": {
    "error": "Ativo não encontrado",
    "success": false
  }
}
```

**Comportamento:**
- Cada ticker é processado independentemente
- Falha em 1 ticker NÃO afeta os demais
- Response sempre 200 OK (verificar `success: false` por ativo)

---

### **3. GET /api/cotacoes/health**

Retorna status do módulo de cotações (sem autenticação).

**Response 200 OK:**
```json
{
  "status": "ok",
  "module": "cotacoes_m7.5",
  "cache_ttl": "15 minutos (Prompt Mestre)",
  "providers": [
    "brapi.dev (FREE tier)",
    "yfinance",
    "alphavantage",
    "database_cache"
  ],
  "update_trigger": "on_demand (somente quando usuário acessa tela)"
}
```

---

## 📐 SCHEMAS RESPONSE

### **CotacaoSchema**
```typescript
{
  ticker: string;                  // Código do ativo
  preco_atual: number;             // Preço atual (R$ ou USD)
  variacao_percentual: number;     // Variação % dia
  volume: number;                  // Volume negociado
  dy_12m: number;                  // Dividend Yield 12 meses (%)
  pl: number;                      // Preço/Lucro
  provider: string;                // API usada (brapi.dev, cache_postgresql, etc)
  cache_ttl_minutes?: number;      // TTL cache (se nova consulta)
  cache_age_minutes?: number;      // Idade cache (se cache hit)
  cache_valid_until?: string;      // ISO8601 timestamp validade cache
  warning?: string;                // Aviso (ex: APIs indisponíveis)
  success: boolean;                // true/false
}
```

### **BatchResponseSchema**
```typescript
{
  [ticker: string]: CotacaoSchema  // Key = ticker, Value = schema acima
}
```

### **HealthSchema**
```typescript
{
  status: "ok" | "degraded" | "error";
  module: string;
  cache_ttl: string;
  providers: string[];
  update_trigger: string;
}
```

---

## 📊 CÓDIGOS DE STATUS HTTP

| Código | Significado | Quando Ocorre |
|--------|-------------|---------------|
| **200** | OK | Sucesso (verificar `success: true/false` no body) |
| **401** | Unauthorized | Token JWT inválido/expirado |
| **404** | Not Found | Ativo não cadastrado no banco |
| **500** | Internal Server Error | Erro database/servidor |
| **503** | Service Unavailable | Todas APIs externas falharam |

---

## ⚡ RATE LIMITING

### **Por Usuário (JWT)**
- **Limite:** 100 requisições / minuto
- **Header Response:** `X-RateLimit-Remaining: 95`
- **429 Response:**
```json
{
  "error": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

### **Por IP (Global)**
- **Limite:** 300 requisições / minuto
- Proteção contra DDoS

---

## 🌐 PROVIDERS EXTERNOS

### **1️⃣ brapi.dev (B3 - Primário)**
- **Mercado:** Brasil (B3)
- **Rate Limit FREE:** 10 req/min
- **Rate Limit PREMIUM:** 60 req/min
- **Latência:** 0.2-5s
- **Confiabilidade:** 99.5%

### **2️⃣ yfinance (Fallback #1)**
- **Mercado:** Global
- **Rate Limit:** ~5-10 req/min (não oficial)
- **Latência:** 10-30s
- **Confiabilidade:** 85% (429 frequente)

### **3️⃣ Alpha Vantage (Fallback #2)**
- **Mercado:** US, Europa
- **Rate Limit FREE:** 500 req/dia
- **Latência:** 2-5s
- **Confiabilidade:** 98%

### **4️⃣ Finnhub (Fallback #3)**
- **Mercado:** US, Europa
- **Rate Limit FREE:** 60 req/min
- **Latência:** 2-5s
- **Confiabilidade:** 97%

### **5️⃣ PostgreSQL Cache (Fallback Final)**
- **TTL:** 15 minutos
- **Latência:** 0.03s ⚡
- **Confiabilidade:** 99.99%

---

## 💻 EXEMPLOS cURL

### **Exemplo 1: Cotação Individual**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 | jq .
```

### **Exemplo 2: Batch 5 Ativos**
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/cotacoes/batch?symbols=PETR4,VALE3,ITUB4,BBDC4,AAPL" | jq .
```

### **Exemplo 3: Health Check**
```bash
curl -s http://localhost:5000/api/cotacoes/health | jq .
```

### **Exemplo 4: Timing (cache vs API)**
```bash
# 1ª chamada (API externa)
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 > /dev/null
# Output: real 0m5.428s

# 2ª chamada (<15min = cache)
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 > /dev/null
# Output: real 0m0.031s ⚡
```

---

## 🐛 TROUBLESHOOTING

### **Erro: "Ativo não encontrado"**
**Causa:** Ticker não cadastrado na tabela `ativo`.

**Solução:**
```bash
podman exec -it exitus-db psql -U exitus -d exitusdb -c \
  "INSERT INTO ativo (ticker, mercado) VALUES ('XPTO4', 'BR');"
```

---

### **Erro: "APIs indisponíveis"**
**Causa:** Todas APIs externas falharam + cache expirado.

**Solução:**
- Verificar conectividade internet
- Verificar tokens no `.env`
- Consultar logs: `podman logs exitus-backend --tail 50`

---

### **Erro: 401 Unauthorized**
**Causa:** Token JWT expirado (TTL 1 hora).

**Solução:**
```bash
# Gerar novo token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')
```

---

## 📈 MÉTRICAS DE PERFORMANCE

### **Latência p95 (cache hit)**
```
Min:  0.025s
p50:  0.031s
p95:  0.087s
Max:  0.150s
```

### **Latência p95 (API externa)**
```
brapi.dev:     0.25-5.4s
yfinance:      10-30s
alphavantage:  2-5s
finnhub:       2-5s
```

---

## 🔒 SEGURANÇA

### **Headers Recomendados**
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
User-Agent: ExitusApp/1.0
```

### **Não Enviar**
- ❌ Tokens no query string
- ❌ Credenciais no body
- ❌ API keys hardcoded

---

## 📚 CHANGELOG

### **v1.0 (09/12/2025)**
- ✅ Implementação inicial
- ✅ Multi-provider fallback (4 APIs)
- ✅ Cache PostgreSQL 15min
- ✅ Rate limit 429 tratado
- ✅ Non-root container
- ✅ Documentação completa

---

**Suporte:** Sistema Exitus  
**Última Atualização:** 09/12/2025
