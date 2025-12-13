# 📡 API REFERENCE COMPLETA - SISTEMA EXITUS

**Sistema Exitus - Documentação de Endpoints**  
**Base URL:** `http://localhost:5000/api`  
**Autenticação:** JWT Bearer Token  
**Versão:** 1.0  
**Data:** 13/12/2025

---

## 🔐 AUTENTICAÇÃO

Todos os endpoints (exceto `/auth/login`) requerem token JWT no header:

```bash
Authorization: Bearer <token>
```

### Obter Token

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "uuid",
      "username": "admin",
      "role": "admin"
    }
  }
}
```

---

## 👤 M2.1 - USUÁRIOS

### Listar Usuários
```
GET /api/usuarios
GET /api/usuarios?page=1&per_page=50
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "usuarios": [...],
    "total": 10
  }
}
```

### Buscar Usuário por ID
```
GET /api/usuarios/{id}
```

### Criar Usuário
```
POST /api/usuarios
Content-Type: application/json

{
  "username": "novo_usuario",
  "email": "usuario@example.com",
  "password": "senha123",
  "role": "USER"
}
```

### Atualizar Usuário
```
PUT /api/usuarios/{id}
Content-Type: application/json

{
  "email": "novo_email@example.com"
}
```

### Deletar Usuário
```
DELETE /api/usuarios/{id}
```

---

## 🏦 M2.2 - CORRETORAS

### Listar Corretoras
```
GET /api/corretoras
GET /api/corretoras?page=1&per_page=50
```

### Buscar Corretora por ID
```
GET /api/corretoras/{id}
```

### Criar Corretora
```
POST /api/corretoras
Content-Type: application/json

{
  "nome": "Clear Corretora",
  "pais": "BR",
  "tipo": "CORRETORA",
  "moeda_padrao": "BRL"
}
```

### Atualizar Corretora
```
PUT /api/corretoras/{id}
```

### Deletar Corretora
```
DELETE /api/corretoras/{id}
```

---

## 📈 M2.3 - ATIVOS

### Listar Ativos
```
GET /api/ativos
GET /api/ativos?ticker=PETR4
GET /api/ativos?tipo=ACAO
GET /api/ativos?mercado=BR
```

**Parâmetros de Query:**
- `ticker` - Filtrar por ticker (case-insensitive, LIKE)
- `tipo` - Filtrar por tipo (ACAO, FII, STOCK, ETF, etc)
- `mercado` - Filtrar por mercado (BR, US, etc)
- `page` - Página (padrão: 1)
- `per_page` - Itens por página (padrão: 50, max: 100)

### Buscar Ativo por ID
```
GET /api/ativos/{id}
```

### Criar Ativo
```
POST /api/ativos
Content-Type: application/json

{
  "ticker": "PETR4",
  "nome": "Petrobras PN",
  "tipo": "ACAO",
  "mercado": "BR",
  "classe": "RENDA_VARIAVEL",
  "moeda": "BRL",
  "setor": "Energia"
}
```

### Atualizar Ativo
```
PUT /api/ativos/{id}
Content-Type: application/json

{
  "preco_atual": 38.50,
  "setor": "Petróleo e Gás"
}
```

### Deletar Ativo
```
DELETE /api/ativos/{id}
```

---

## 💰 M2.4 - TRANSAÇÕES

### Listar Transações
```
GET /api/transacoes
GET /api/transacoes?ativo_id={uuid}
GET /api/transacoes?corretora_id={uuid}
GET /api/transacoes?tipo=COMPRA
```

**Parâmetros de Query:**
- `ativo_id` - Filtrar por ativo
- `corretora_id` - Filtrar por corretora
- `tipo` - Filtrar por tipo (COMPRA, VENDA)
- `data_inicio` - Filtrar por data inicial (YYYY-MM-DD)
- `data_fim` - Filtrar por data final (YYYY-MM-DD)

### Buscar Transação por ID
```
GET /api/transacoes/{id}
```

### Criar Transação (Compra/Venda)
```
POST /api/transacoes
Content-Type: application/json

{
  "ativo_id": "uuid",
  "corretora_id": "uuid",
  "tipo": "COMPRA",
  "quantidade": 100,
  "preco_unitario": 35.50,
  "data_transacao": "2025-12-13T10:30:00",
  "taxas": 10.00,
  "imposto": 0.00
}
```

**Tipos Válidos:** `COMPRA`, `VENDA`

### Atualizar Transação
```
PUT /api/transacoes/{id}
```

### Deletar Transação
```
DELETE /api/transacoes/{id}
```

---

## 📊 M3.1 - POSIÇÕES

### Listar Posições
```
GET /api/posicoes
GET /api/posicoes?ativo_id={uuid}
GET /api/posicoes?corretora_id={uuid}
GET /api/posicoes?ticker=PETR4
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "posicoes": [
      {
        "id": "uuid",
        "ativo_id": "uuid",
        "corretora_id": "uuid",
        "quantidade": 100.0,
        "preco_medio": 35.07,
        "custototal": 3507.0,
        "taxas_acumuladas": 10.0,
        "lucro_prejuizo_realizado": 50.0
      }
    ],
    "total": 3
  }
}
```

### Recalcular Posições
```
POST /api/posicoes/calcular
```

**Ação:** Recalcula todas as posições do usuário baseado nas transações.

**Resposta:**
```json
{
  "success": true,
  "data": {
    "criadas": 2,
    "atualizadas": 3,
    "zeradas": 1
  }
}
```

---

## 💵 M3.2 - MOVIMENTAÇÕES DE CAIXA

### Listar Movimentações
```
GET /api/movimentacoes
GET /api/movimentacoes?corretora_id={uuid}
GET /api/movimentacoes?data_inicio=2025-01-01
GET /api/movimentacoes?data_fim=2025-12-31
```

### Criar Movimentação
```
POST /api/movimentacoes
Content-Type: application/json

{
  "corretora_id": "uuid",
  "tipo_movimentacao": "DEPOSITO",
  "valor": 5000.00,
  "moeda": "BRL",
  "data_movimentacao": "2025-12-13",
  "descricao": "Aporte mensal"
}
```

**Tipos Válidos:**
- `DEPOSITO` - Aporte de capital
- `SAQUE` - Resgate de valores
- `DIVIDENDO` - Recebimento de proventos
- `JCP` - Juros sobre Capital Próprio
- `TAXA` - Taxas de corretagem/custódia
- `BONIFICACAO` - Bonificações recebidas

### Consultar Saldo
```
GET /api/movimentacoes/saldo/{corretora_id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "saldo": 5000.0,
    "corretora_id": "uuid"
  }
}
```

---

## 🎁 M3.2B - PROVENTOS

### Listar Proventos (Admin)
```
GET /api/proventos
GET /api/proventos?ativo_id={uuid}
```

### Criar Provento (Admin)
```
POST /api/proventos
Content-Type: application/json

{
  "ativo_id": "uuid",
  "tipo": "DIVIDENDO",
  "valor_por_acao": 0.50,
  "data_com": "2025-12-15",
  "data_pagamento": "2025-12-30"
}
```

**Tipos:** `DIVIDENDO`, `JCP`, `RENDIMENTO`, `BONIFICACAO`

### Proventos Recebidos (Usuário)
```
GET /api/proventos/recebidos
GET /api/proventos/recebidos?data_inicio=2025-01-01
```

### Total Recebido
```
GET /api/proventos/total-recebido
GET /api/proventos/total-recebido?tipo=DIVIDENDO
```

---

## 🔄 M3.3 - EVENTOS CORPORATIVOS

### Listar Eventos
```
GET /api/eventos-corporativos
GET /api/eventos-corporativos?ativo_id={uuid}
GET /api/eventos-corporativos?tipo=DESDOBRAMENTO
```

### Criar Evento (Admin)
```
POST /api/eventos-corporativos
Content-Type: application/json

{
  "ativo_id": "uuid",
  "tipo": "DESDOBRAMENTO",
  "proporcao": "1:10",
  "data_evento": "2025-12-20",
  "data_vigencia": "2025-12-21",
  "descricao": "Split 1:10"
}
```

**Tipos:** `DESDOBRAMENTO` (Split), `GRUPAMENTO` (Inplit), `BONIFICACAO`

### Aplicar Evento
```
POST /api/eventos-corporativos/{id}/aplicar
```

**Ação:** Aplica ajustes nas posições conforme a proporção do evento.

---

## 🎯 M3.4 - PORTFOLIO CONSOLIDADO

### Dashboard 360°
```
GET /api/portfolio/dashboard
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "patrimonio_ativos": 11117.30,
    "custo_aquisicao": 11021.00,
    "saldo_caixa": 0.0,
    "patrimonio_total": 11117.30,
    "lucro_bruto": 96.30,
    "rentabilidade_perc": 0.87
  }
}
```

### Alocação por Classe
```
GET /api/portfolio/alocacao
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "acao": {
      "valor": 6514.0,
      "percentual": 59.1
    },
    "fii": {
      "valor": 4507.0,
      "percentual": 40.9
    }
  }
}
```

---

## 🎯 M4 - BUY SIGNALS (ANÁLISE FUNDAMENTALISTA)

### Buy Signals Completo
```
GET /api/buy-signals/{ticker}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "preco_atual": 38.50,
    "preco_justo_graham": 42.30,
    "preco_justo_gordon": 40.15,
    "margem_seguranca": 9.8,
    "buy_score": 7.5,
    "recomendacao": "COMPRA MODERADA"
  }
}
```

### Margem de Segurança
```
GET /api/buy-signals/{ticker}/margem-seguranca
```

### Buy Score
```
GET /api/buy-signals/{ticker}/buy-score
```

### Indicadores Fundamentalistas
```
GET /api/buy-signals/{ticker}/indicadores
```

**Resposta:**
```json
{
  "pl": 8.5,
  "pvp": 1.2,
  "roe": 15.3,
  "dividend_yield": 6.2
}
```

---

## 💹 M7.5 - COTAÇÕES EM TEMPO REAL

### Cotação Individual
```
GET /api/cotacoes/{ticker}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "preco": 38.50,
    "variacao_dia": 2.1,
    "volume": 125000000,
    "ultima_atualizacao": "2025-12-13T15:30:00",
    "fonte": "brapi.dev"
  }
}
```

### Cotação em Lote (Batch)
```
POST /api/cotacoes/batch
Content-Type: application/json

{
  "tickers": ["PETR4", "VALE3", "ITUB4"]
}
```

### Health Check
```
GET /api/cotacoes/health
```

---

## 📊 M7 - RELATÓRIOS E ANÁLISES

### Relatório de Performance
```
GET /api/relatorios/performance
GET /api/relatorios/performance?periodo=12M
```

**Resposta:**
```json
{
  "sharpe_ratio": 1.25,
  "sortino_ratio": 1.45,
  "volatilidade": 18.5,
  "max_drawdown": -12.3,
  "retorno_acumulado": 22.5
}
```

### Projeção de Renda Passiva
```
GET /api/projecoes/renda-passiva
GET /api/projecoes/renda-passiva?meses=12
```

### Alertas Configurados
```
GET /api/alertas
POST /api/alertas
DELETE /api/alertas/{id}
```

---

## 🔍 CÓDIGOS DE STATUS HTTP

| Código | Significado | Quando Ocorre |
|--------|-------------|---------------|
| 200 | OK | Sucesso (GET, PUT, DELETE) |
| 201 | Created | Recurso criado com sucesso (POST) |
| 204 | No Content | Sucesso sem retorno de dados |
| 400 | Bad Request | Dados inválidos enviados |
| 401 | Unauthorized | Token ausente ou inválido |
| 403 | Forbidden | Sem permissão (ex: user acessando endpoint admin) |
| 404 | Not Found | Recurso não encontrado |
| 500 | Internal Server Error | Erro no servidor (ver logs) |

---

## 🧪 EXEMPLOS DE USO

### Fluxo Completo: Criar Transação → Ver Posições

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  jq -r '.data.access_token')

# 2. Criar transação de compra
curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo_id": "uuid-do-ativo",
    "corretora_id": "uuid-da-corretora",
    "tipo": "COMPRA",
    "quantidade": 100,
    "preco_unitario": 35.50,
    "data_transacao": "2025-12-13T10:00:00"
  }'

# 3. Recalcular posições
curl -X POST http://localhost:5000/api/posicoes/calcular \
  -H "Authorization: Bearer $TOKEN"

# 4. Ver posições atualizadas
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/posicoes | jq .

# 5. Ver dashboard consolidado
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/dashboard | jq .
```

---

## 📚 PADRÕES DE RESPOSTA

### Resposta de Sucesso
```json
{
  "success": true,
  "data": { ... },
  "message": "Operação realizada com sucesso"
}
```

### Resposta de Erro
```json
{
  "success": false,
  "error": "Descrição do erro",
  "details": { ... }
}
```

### Resposta Paginada
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

---

## 🔗 RECURSOS ADICIONAIS

- **Troubleshooting:** Ver `docs/TROUBLESHOOTING_GUIDE.md`
- **Estrutura do Banco:** Ver `docs/EXITUS_DB_STRUCTURE.txt`
- **Guia de Validação:** Ver `docs/VALIDACAO_M3_MANUAL.md`

---

**Última Atualização:** 13/12/2025  
**Versão:** 1.0  
**Gerado por:** Sistema Exitus - API Reference Generator
