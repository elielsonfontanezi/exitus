# API Reference - Sistema Exitus v0.7.10

## 📋 Índice

- [Informações Gerais](#informações-gerais)
- [1. Autenticação](#1-autenticação)
- [2. Usuários](#2-usuários)
- [3. Corretoras](#3-corretoras)
- [4. Ativos](#4-ativos)
- [5. Portfólios](#5-portfólios)
- [6. Posições](#6-posições)
- [7. Transações](#7-transações)
- [8. Proventos](#8-proventos)
- [9. Movimentações de Caixa](#9-movimentações-de-caixa)
- [10. Eventos Corporativos](#10-eventos-corporativos)
- [11. Buy Signals](#11-buy-signals)
- [12. Cálculos Financeiros](#12-cálculos-financeiros)
- [13. Regras Fiscais](#13-regras-fiscais)
- [14. Feriados](#14-feriados)
- [15. Fontes de Dados](#15-fontes-de-dados)
- [16. Alertas](#16-alertas)
- [17. Relatórios](#17-relatórios)
- [18. Cotações](#18-cotações)
- [19. Projeções](#19-projeções)
- [20. Performance](#20-performance)
- [Health Checks](#health-checks)

---

## Informações Gerais

### Endpoints

Endpoints usam snake_case (ex: `api/portfolio/dashboard`).[file:31]

### Base URL

```text
http://localhost:5000/api
```

**Produção** (quando deployado):

```text
https://seu-dominio.com/api
```

### Autenticação

Todas as rotas (exceto `/auth/login` e `/auth/register`) requerem **JWT Bearer Token**.[file:31]

**Header obrigatório**:

```text
Authorization: Bearer <seu_token_jwt>
```

**Obter Token**:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'
```

**Expiry**: 1 hora (3600 segundos).[file:31]

### Formato de Resposta

Sucesso:

```json
{
  "success": true,
  "data": { },
  "message": "Operação realizada com sucesso"
}
```

Erro:

```json
{
  "error": "Descrição do erro",
  "statuscode": 400
}
```

Lista paginada:

```json
{
  "success": true,
  "data": [],
  "total": 127,
  "pages": 13,
  "current_page": 1,
  "per_page": 10
}
```

### Paginação

Parâmetros de query:

- `page` – Número da página (default: 1)
- `per_page` – Itens por página (default: 10, max: 100)[file:31]

Exemplo:

```bash
GET /api/transacoes?page=2&per_page=20
```

### Códigos de Status HTTP

| Código | Significado                              |
|--------|------------------------------------------|
| 200    | OK - Sucesso                            |
| 201    | Created - Recurso criado                |
| 400    | Bad Request - Dados inválidos           |
| 401    | Unauthorized - Token ausente/inválido   |
| 403    | Forbidden - Sem permissão               |
| 404    | Not Found - Recurso não encontrado      |
| 500    | Internal Server Error - Erro no servidor|

---

## 1. Autenticação

### POST /api/auth/login

Autentica usuário e retorna token JWT.[file:31]

**Request:**

```json
{
  "username": "admin",
  "password": "senha123"
}
```

**Response (200):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "uuid-aqui",
      "username": "admin",
      "email": "admin@exitus.com"
    }
  },
  "message": "Login realizado com sucesso"
}
```

---

### POST /api/auth/register

Registra novo usuário.[file:31]

---

## 2. Usuários

CRUD básico de usuários (lista, detalhe, update, soft delete), conforme estrutura atual.[file:31]

---

## 3. Corretoras

CRUD de corretoras com validação de propriedade do usuário (403 quando a corretora pertence a outro usuário).[file:31]

---

## 4. Ativos

### GET /api/ativos

Lista ativos (paginado, filtros opcionais).[file:31]

**Query Parameters:**

- `ticker` – Filtro por ticker (ex: `?ticker=PETR4`)
- `tipo` – Filtro por tipo (Enum `TipoAtivo`)
- `mercado` – Filtro por mercado (`BR`, `US`, `EU`, `ASIA`, `GLOBAL`)

**Enum TipoAtivo (14 valores):**[file:28]

- **Brasil (BR)**: `ACAO`, `FII`, `CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`
- **Estados Unidos (US)**: `STOCK`, `REIT`, `BOND`, `ETF`
- **Internacional (INTL)**: `STOCK_INTL`, `ETF_INTL`
- **Outros**: `CRIPTO`, `OUTRO`

**Response (200):**

```json
{
  "success": true,
  "data": {
    "ativos": [
      {
        "id": "uuid-1",
        "ticker": "PETR4",
        "nome": "Petrobras PN",
        "tipo": "acao",
        "mercado": "BR",
        "moeda": "BRL",
        "preco_atual": 31.46,
        "dividend_yield": 9.5,
        "pl": 4.8,
        "pvp": 1.2,
        "roe": 18.5,
        "cap_rate": null,
        "data_ultima_cotacao": "2026-01-06T18:00:00Z"
      }
    ],
    "total": 70,
    "pages": 7,
    "current_page": 1,
    "per_page": 10
  }
}
```

---

### GET /api/ativos/{id}

Detalha ativo.[file:31]

---

### POST /api/ativos

Cria novo ativo.[file:31]

**Campos obrigatórios:**

- `ticker` (string, único por mercado)
- `nome` (string)
- `tipo` (Enum `TipoAtivo`, ver lista acima)
- `classe` (Enum `ClasseAtivo`: `RENDA_VARIAVEL`, `RENDA_FIXA`, `CRIPTO`, `COMMODITY`, `HIBRIDO`)
- `mercado` (`BR`, `US`, `EU`, `ASIA`, `GLOBAL`)
- `moeda` (`BRL`, `USD`, `EUR`, etc.)[file:28]

**Request – Exemplo Brasil (ACAO):**

```json
{
  "ticker": "VALE3",
  "nome": "Vale ON",
  "tipo": "ACAO",
  "classe": "RENDA_VARIAVEL",
  "mercado": "BR",
  "moeda": "BRL",
  "setor": "Mineração"
}
```

**Request – Exemplo Renda Fixa BR (CDB):**

```json
{
  "ticker": "CDB_NUBANK_CDI",
  "nome": "Nubank CDB 100% CDI",
  "tipo": "CDB",
  "classe": "RENDA_FIXA",
  "mercado": "BR",
  "moeda": "BRL"
}
```

**Request – Exemplo US STOCK:**

```json
{
  "ticker": "AAPL",
  "nome": "Apple Inc.",
  "tipo": "STOCK",
  "classe": "RENDA_VARIAVEL",
  "mercado": "US",
  "moeda": "USD"
}
```

**Request – Exemplo ETF_INTL:**

```json
{
  "ticker": "VWCE.DE",
  "nome": "Vanguard FTSE All-World UCITS ETF",
  "tipo": "ETF_INTL",
  "classe": "RENDA_VARIAVEL",
  "mercado": "EU",
  "moeda": "EUR"
}
```

**Valores aceitos em `tipo`:**

```text
acao, fii, cdb, lcilca, tesourodireto, debenture,
stock, reit, bond, etf, stockintl, etfintl, cripto, outro
```

Para referência completa dos enums, consulte `ENUMS.md`.[file:28]

---

## 5. Portfólios

APIs de dashboard, alocação, performance e carteiras customizadas, conforme já descrito (sem mudança de contrato).[file:31]

- `GET /api/portfolios/dashboard`
- `GET /api/portfolio/alocacao`
- `GET /api/portfolio/performance`
- `GET /api/portfolio/evolucao`
- CRUD de `/api/portfolios`.[file:31]

---

## 6. Posições

- `GET /api/posicoes`
- `GET /api/posicoes/{id}`

Retornam holdings com join de `ativo` e `corretora`.[file:31]

---

## 7. Transações

Filtros e payload mantidos; `tipo` é Enum `TipoTransacao` (ex.: `COMPRA`, `VENDA`, `DIVIDENDO`, `JCP`, etc.).[file:18][file:31]

---

## 8. Proventos

APIs de listagem, criação, update e delete de proventos, com `tipo` como Enum `TipoProvento` (`DIVIDENDO`, `JCP`, `RENDIMENTO`, `CUPOM`, etc.).[file:18][file:31]

---

## 9–20. Demais Seções

As seções de:

- Movimentações de Caixa
- Eventos Corporativos
- Buy Signals
- Cálculos Financeiros
- Regras Fiscais
- Feriados
- Fontes de Dados
- Alertas
- Relatórios
- Cotações
- Projeções
- Performance
- Health Checks

continuam com o mesmo contrato já descrito na versão v0.7.6, apenas consumindo agora os novos valores de enums documentados em `ENUMS.md` e refletidos no schema atualizado (`TipoAtivo`, `ClasseAtivo`, `IncidenciaImposto`, etc.).[file:22][file:18][file:28]

---

**Documento atualizado**: 20 de Fevereiro de 2026  
**Versão da API**: v0.7.10 — GAP EXITUS-DOCS-API-001 ✅ fechado: `GET /api/ativos` responde `.data.ativos[]`; total=70; senha padrão dev padronizada (`senha123`).