# Guia de Comandos cURL – Sistema Exitus

## 1. Autenticação

### 1.1 Fazer login (obter token)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq

TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.data.access_token')  # ✅ Snake case

echo "Token: $TOKEN"
```

### 1.2 Login com cookies

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c /tmp/cookies.txt \
  | jq

curl -X GET http://localhost:5000/api/ativos \
  -b /tmp/cookies.txt \
  | jq
```

### 1.3 Validar token

```bash
curl -X GET http://localhost:5000/api/auth/validate \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 2. Ativos

### 2.1 Listar ativos

```bash
curl -X GET "http://localhost:5000/api/ativos?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/ativos?tipo=ACAO" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/ativos?mercado=BR" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 2.2 Buscar ativo por ID

```bash
ATIVO_ID="seu-uuid-aqui"

curl -X GET "http://localhost:5000/api/ativos/$ATIVO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 2.3 Buscar ativo por ticker

```bash
curl -X GET "http://localhost:5000/api/ativos/ticker/PETR4" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/ativos/ticker/AAPL?mercado=US" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 2.4 Cadastrar ativo

```bash
curl -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BBDC4",
    "nome": "Bradesco PN",
    "tipo": "ACAO",
    "classe": "RENDAVARIAVEL",
    "mercado": "BR",
    "moeda": "BRL"
  }' | jq

curl -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "HGLG11",
    "nome": "CSHG Logística FII",
    "tipo": "FII",
    "classe": "RENDAVARIAVEL",
    "mercado": "BR",
    "moeda": "BRL"
  }' | jq

curl -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
    "nome": "Microsoft Corporation",
    "tipo": "ACAO",
    "classe": "RENDAVARIAVEL",
    "mercado": "US",
    "moeda": "USD"
  }' | jq
```

### 2.5 Atualizar ativo

```bash
ATIVO_ID="seu-uuid-aqui"

curl -X PUT "http://localhost:5000/api/ativos/$ATIVO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preco_atual": 42.50,
    "preco_teto": 55.00,
    "dividend_yield": 8.5,
    "p_l": 12.3
  }' | jq
```

### 2.6 Remover ativo

```bash
ATIVO_ID="seu-uuid-aqui"

curl -X DELETE "http://localhost:5000/api/ativos/$ATIVO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X DELETE "http://localhost:5000/api/ativos/$ATIVO_ID?force=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 3. Proventos

### 3.1 Listar proventos

```bash
curl -X GET http://localhost:5000/api/proventos \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/proventos?ticker=PETR4" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/proventos?data_inicio=2025-01-01&data_fim=2025-12-31" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/proventos?tipo=DIVIDENDO" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 3.2 Cadastrar provento

```bash
ATIVO_ID="uuid-do-ativo"

curl -X POST http://localhost:5000/api/proventos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo_id": "'$ATIVO_ID'",
    "tipo_provento": "DIVIDENDO",
    "valor_por_acao": 1.50,
    "quantidade_ativos": 100,
    "data_com": "2025-12-01",
    "data_pagamento": "2025-12-20"
  }' | jq
```

### 3.3 Buscar provento por ID

```bash
PROVENTO_ID="uuid-do-provento"

curl -X GET "http://localhost:5000/api/proventos/$PROVENTO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 3.4 Remover provento

```bash
PROVENTO_ID="uuid-do-provento"

curl -X DELETE "http://localhost:5000/api/proventos/$PROVENTO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 4. Corretoras

### 4.1 Listar corretoras

```bash
curl -X GET http://localhost:5000/api/corretoras \
  -H "Authorization: BearER $TOKEN" \
  | jq
```

### 4.2 Cadastrar corretora

```bash
curl -X POST http://localhost:5000/api/corretoras \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "XP Investimentos",
    "tipo": "CORRETORA",
    "pais": "BR",
    "moeda_padrao": "BRL",
    "saldo_atual": 10000.00
  }' | jq
```

### 4.3 Atualizar saldo

```bash
CORRETORA_ID="uuid-da-corretora"

curl -X PUT "http://localhost:5000/api/corretoras/$CORRETORA_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "saldo_atual": 25000.00
  }' | jq
```

## 5. Transações

### 5.1 Listar transações

```bash
curl -X GET http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/transacoes?tipo_operacao=COMPRA" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 5.2 Cadastrar compra

```bash
ATIVO_ID="uuid-do-ativo"
CORRETORA_ID="uuid-da-corretora"

curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo_id": "'$ATIVO_ID'",
    "corretora_id": "'$CORRETORA_ID'",
    "tipo_operacao": "COMPRA",
    "data": "2025-12-16",
    "quantidade": 100,
    "preco_unitario": 42.50,
    "taxas": 10.00
  }' | jq
```

### 5.3 Cadastrar venda

```bash
curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo_id": "'$ATIVO_ID'",
    "corretora_id": "'$CORRETORA_ID'",
    "tipo_operacao": "VENDA",
    "data": "2025-12-16",
    "quantidade": 50,
    "preco_unitario": 45.00,
    "taxas": 8.00
  }' | jq
```

## 6. Cotações (M7.5)

### 6.1 Cotação individual

```bash
curl -X GET "http://localhost:5000/api/cotacoes/PETR4" \
  -H "Authorization: Bearer $TOKEN" \
  | jq

curl -X GET "http://localhost:5000/api/cotacoes/AAPL?mercado=US" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 6.2 Cotação em batch

```bash
curl -X POST http://localhost:5000/api/cotacoes/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": [
      {"ticker": "PETR4", "mercado": "BR"},
      {"ticker": "VALE3", "mercado": "BR"},
      {"ticker": "AAPL", "mercado": "US"}
    ]
  }' | jq
```

### 6.3 Health das cotações

```bash
curl -X GET http://localhost:5000/api/cotacoes/health \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 7. Buy Signals

### 7.1 Buy signal por ticker

```bash
curl -X GET "http://localhost:5000/api/buy-signals/PETR4" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 7.2 Watchlist TOP

```bash
curl -X GET http://localhost:5000/api/buy-signals/watchlist-top \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 8. Portfolio

### 8.1 Resumo do portfolio

```bash
curl -X GET http://localhost:5000/api/portfolio/resumo \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 8.2 Posições consolidadas

```bash
curl -X GET http://localhost:5000/api/portfolio/posicoes \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 8.3 Performance

```bash
curl -X GET http://localhost:5000/api/portfolio/performance \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## 9. Utilitários

### 9.1 Health geral

```bash
curl -X GET http://localhost:5000/health | jq
```

### 9.2 Versão da API

```bash
curl -X GET http://localhost:5000/api/version | jq
```

### 9.3 Listar usuários (admin)

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```
