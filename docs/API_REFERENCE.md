# API Reference - Sistema Exitus v0.7.6

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

Endpoints usam snake_case (ex: api_portfolio_dashboard).

### Base URL

```
http://localhost:5000/api
```

**Produção** (quando deployado):
```
https://seu-dominio.com/api
```

### Autenticação

Todas as rotas (exceto `/auth/login` e `/auth/register`) requerem **JWT Bearer Token**.

**Header obrigatório**:
```
Authorization: Bearer <seu_token_jwt>
```

**Obter Token**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Expiry**: 1 hora (3600 segundos)

### Formato de Resposta

#### Sucesso
```json
{
  "success": true,
  "data": { ... },
  "message": "Operação realizada com sucesso"
}
```

#### Erro
```json
{
  "error": "Descrição do erro",
  "statuscode": 400
}
```

#### Lista Paginada
```json
{
  "success": true,
  "data": [...],
  "total": 127,
  "pages": 13,
  "current_page": 1,
  "per_page": 10
}
```

### Paginação

**Naming Convention**: Endpoints seguem snake_case (ex: `api/portfolio/dashboard`, `api/buy-signals/buy-scorePETR4`).

Parâmetros de query:
- `?page=1` - Número da página (default: 1)
- `?per_page=10` - Items por página (default: 10, max: 100)

**Exemplo**:
```bash
GET /api/transacoes?page=2&per_page=20
```

**Nota: snake_case em todos endpoints (ver CODING_STANDARDS.md).**

### Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| **200** | OK - Sucesso |
| **201** | Created - Recurso criado |
| **400** | Bad Request - Dados inválidos |
| **401** | Unauthorized - Token ausente/inválido |
| **403** | Forbidden - Sem permissão |
| **404** | Not Found - Recurso não encontrado |
| **500** | Internal Server Error - Erro no servidor |

---

## 1. Autenticação

### POST /api/auth/login

Autentica usuário e retorna token JWT.

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200):
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

**Exemplo cURL**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

### POST /api/auth/register

Registra novo usuário.

**Request**:
```json
{
  "username": "novouser",
  "email": "user@example.com",
  "password": "senha123",
  "password_confirm": "senha123"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "uuid-aqui",
    "username": "novouser",
    "email": "user@example.com"
  },
  "message": "Usuário criado com sucesso"
}
```

**Validações**:
- `username`: mínimo 3 caracteres, único
- `email`: formato válido, único
- `password`: mínimo 8 caracteres
- `password_confirm`: deve ser igual a `password`

---

## 2. Usuários

### GET /api/usuarios

Lista todos os usuários (paginado).

**Query Parameters**:
- `page` - Número da página (default: 1)
- `per_page` - Items por página (default: 10)

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "username": "admin",
      "email": "admin@exitus.com",
      "ativo": true,
      "created_at": "2025-11-12T10:00:00Z"
    }
  ],
  "total": 2,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

---

### GET /api/usuarios/{id}

Detalha um usuário específico.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "username": "admin",
    "email": "admin@exitus.com",
    "ativo": true,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-12-15T14:30:00Z"
  }
}
```

---

### PUT /api/usuarios/{id}

Atualiza usuário (completo).

**Request**:
```json
{
  "email": "novoemail@exitus.com",
  "ativo": true
}
```

---

### DELETE /api/usuarios/{id}

Deleta usuário (soft delete).

**Response** (200):
```json
{
  "success": true,
  "message": "Usuário deletado com sucesso"
}
```

---

## 3. Corretoras

### GET /api/corretoras

Lista corretoras do usuário autenticado.

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "nome": "Clear Corretora",
      "cnpj": "00.000.000/0001-00",
      "pais": "BR",
      "moeda_padrao": "BRL",
      "saldo_caixa": 5000.00
    }
  ],
  "total": 3
}
```

---

### POST /api/corretoras

Cria nova corretora.

**Request**:
```json
{
  "nome": "XP Investimentos",
  "cnpj": "11.111.111/0001-11",
  "pais": "BR",
  "moeda_padrao": "BRL"
}
```

---

### GET /api/corretoras/{id}
**Responses:**
- `200` - Corretora encontrada
- `401` - Token JWT inválido ou ausente
- `403` - ⚠️ **NOVO:** Corretora existe mas pertence a outro usuário
- `404` - Corretora não existe

---

### PUT /api/corretoras/{id}
**Responses:**
- `200` - Atualizada com sucesso
- `400` - Dados inválidos
- `401` - Token JWT inválido ou ausente
- `403` - ⚠️ **NOVO:** Corretora existe mas pertence a outro usuário
- `404` - Corretora não existe

---

### DELETE /api/corretoras/{id}
**Responses:**
- `200` - Deletada com sucesso
- `401` - Token JWT inválido ou ausente
- `403` - ⚠️ **NOVO:** Corretora existe mas pertence a outro usuário
- `404` - Corretora não existe

---

## 4. Ativos

### GET /api/ativos

Lista ativos (paginado, filtros opcionais).

**Query Parameters**:
- `ticker` - Filtro por ticker (ex: `?ticker=PETR4`)
- `tipo` - Filtro por tipo (ACAO, FII, REIT, RENDA_FIXA)
- `mercado` - Filtro por mercado (BR, US, EU, ASIA)

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "ticker": "PETR4",
      "nome": "Petrobras PN",
      "tipo": "ACAO",
      "mercado": "BR",
      "setor": "Energia",
      "preco_atual": 31.46,
      "dividend_yield": 9.5,
      "pl": 4.8,
      "data_ultima_cotacao": "2026-01-06T18:00:00Z"
    }
  ],
  "total": 17
}
```

---

### GET /api/ativos/{id}

Detalha ativo.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "ticker": "PETR4",
    "nome": "Petrobras PN",
    "tipo": "ACAO",
    "mercado": "BR",
    "setor": "Energia",
    "moeda": "BRL",
    "preco_atual": 31.46,
    "dividend_yield": 9.5,
    "pl": 4.8,
    "pvp": 1.2,
    "roe": 18.5,
    "data_ultima_cotacao": "2026-01-06T18:00:00Z",
    "created_at": "2025-11-15T10:00:00Z"
  }
}
```

---

### POST /api/ativos

Cria novo ativo.

**Request**:
```json
{
  "ticker": "VALE3",
  "nome": "Vale ON",
  "tipo": "ACAO",
  "mercado": "BR",
  "setor": "Mineração",
  "moeda": "BRL"
}
```

---

## 5. Portfólios

### GET /api/portfolios/dashboard

Dashboard consolidado do portfolio do usuário.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "patrimonioativos": 125430.50,
    "custoaquisicao": 100000.00,
    "saldocaixa": 5000.00,
    "patrimoniototal": 130430.50,
    "lucrobruto": 25430.50,
    "rentabilidadeperc": 25.43
  },
  "message": "Dashboard gerado com sucesso"
}
```

**Exemplo cURL**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolios/dashboard | jq .
```

---

### GET /api/portfolio/alocacao

Alocação por classe de ativo.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "rendavariavel": {
      "valor": 80000.00,
      "percentual": 63.8
    },
    "rendafixa": {
      "valor": 30000.00,
      "percentual": 23.9
    },
    "fii": {
      "valor": 15430.50,
      "percentual": 12.3
    }
  },
  "message": "Alocação por classe calculada"
}
```

---

### GET /api/portfolio/performance

Performance individual de todos os ativos.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total": 17,
    "ativos": [
      {
        "ticker": "PETR4",
        "quantidade": 100,
        "precomedio": 28.50,
        "precoatual": 31.46,
        "custototal": 2850.00,
        "valoratual": 3146.00,
        "lucro": 296.00,
        "rentabilidadeperc": 10.39
      }
    ]
  }
}
```

---

### GET /api/portfolio/distribuicao-classes

Distribuição percentual por classe.

---

### GET /api/portfolio/distribuicao-setores

Distribuição percentual por setor.

---

### GET /api/portfolio/evolucao

Evolução patrimonial (até 24 meses).

**Query Parameters**:
- `meses` - Número de meses (default: 12, max: 24)

**Response** (200):
```json
{
  "success": true,
  "data": {
    "meses": 12,
    "historico": [
      {
        "mes": "2025-02",
        "patrimonio": 95000.00
      },
      {
        "mes": "2025-03",
        "patrimonio": 102000.00
      }
    ]
  }
}
```

---

### GET /api/portfolio/metricas-risco

Métricas de risco do portfolio.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "volatilidade_anualizada": 18.5,
    "sharpe_ratio": 1.45,
    "max_drawdown": -12.3,
    "beta_ibov": 0.95
  }
}
```

---

### GET /api/portfolios

Lista carteiras customizadas.

---

### POST /api/portfolios

Cria nova carteira.

**Request**:
```json
{
  "nome": "Carteira Dividendos",
  "descricao": "Foco em ações high yield"
}
```

---

### GET /api/portfolios/{id}

Detalha carteira.

---

### PUT /api/portfolios/{id}

Atualiza carteira.

---

### DELETE /api/portfolios/{id}

Deleta carteira.

---

## 6. Posições

### GET /api/posicoes

Lista posições (holdings) do usuário.

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "ativo": {
        "ticker": "PETR4",
        "nome": "Petrobras PN"
      },
      "corretora": {
        "nome": "Clear Corretora"
      },
      "quantidade": 100,
      "preco_medio": 28.50,
      "custo_total": 2850.00,
      "valor_atual": 3146.00,
      "rentabilidade_perc": 10.39
    }
  ],
  "total": 17
}
```

---

### GET /api/posicoes/{id}

Detalha posição específica.

---

## 7. Transações

### GET /api/transacoes

Lista transações (paginado, filtros opcionais).

**Query Parameters**:
- `ticker` - Filtro por ticker
- `tipo` - Filtro por tipo (COMPRA, VENDA)
- `data_inicio` - Data inicial (YYYY-MM-DD)
- `data_fim` - Data final (YYYY-MM-DD)

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "ativo": {
        "ticker": "PETR4"
      },
      "tipo": "COMPRA",
      "quantidade": 100,
      "preco_unitario": 28.50,
      "valor_total": 2850.00,
      "taxas": 5.00,
      "impostos": 0.00,
      "data_transacao": "2025-11-20T10:30:00Z"
    }
  ],
  "total": 127,
  "pages": 13
}
```

---

### POST /api/transacoes

Registra nova transação.

**Request**:
```json
{
  "ativo_id": "uuid-do-ativo",
  "corretora_id": "uuid-da-corretora",
  "tipo": "COMPRA",
  "quantidade": 100,
  "preco_unitario": 28.50,
  "taxas": 5.00,
  "data_transacao": "2025-11-20"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "uuid-nova-transacao",
    "tipo": "COMPRA",
    "valor_total": 2855.00
  },
  "message": "Transação registrada com sucesso"
}
```

---

### GET /api/transacoes/{id}

Detalha transação.

---

### PUT /api/transacoes/{id}

Atualiza transação.

---

### DELETE /api/transacoes/{id}

Deleta transação.

---

## 8. Proventos

### GET /api/proventos

Lista proventos recebidos.

**Query Parameters**:
- `ticker` - Filtro por ticker
- `tipo` - Filtro por tipo (DIVIDENDO, JCP, RENDIMENTO)
- `ano` - Filtro por ano

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "ativo": {
        "ticker": "PETR4"
      },
      "tipo": "DIVIDENDO",
      "valor_bruto": 100.00,
      "valor_liquido": 85.00,
      "data_pagamento": "2025-12-15",
      "data_com": "2025-11-30"
    }
  ],
  "total": 45
}
```

---

### POST /api/proventos

Registra provento recebido.

**Request**:
```json
{
  "ativo_id": "uuid-do-ativo",
  "tipo": "DIVIDENDO",
  "valor_bruto": 100.00,
  "valor_liquido": 85.00,
  "data_pagamento": "2025-12-15",
  "data_com": "2025-11-30"
}
```

---

### GET /api/proventos/{id}

Detalha provento.

---

### PUT /api/proventos/{id}

Atualiza provento.

---

### DELETE /api/proventos/{id}

Deleta provento.

---

## 9. Movimentações de Caixa

### GET /api/movimentacao-caixa

Lista movimentações (depósitos/saques).

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "corretora": {
        "nome": "Clear Corretora"
      },
      "tipo": "DEPOSITO",
      "valor": 10000.00,
      "moeda": "BRL",
      "data_movimentacao": "2025-11-15"
    }
  ],
  "total": 23
}
```

---

### GET /api/movimentacao-caixa/extrato

Extrato consolidado de movimentações.

---

### GET /api/movimentacao-caixa/saldo/{corretora_id}

Saldo atual de uma corretora.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "corretora_id": "uuid-1",
    "saldo_atual": 5000.00,
    "moeda": "BRL",
    "ultima_atualizacao": "2026-01-06T22:00:00Z"
  }
}
```

---

### POST /api/movimentacao-caixa

Registra movimentação.

**Request**:
```json
{
  "corretora_id": "uuid-da-corretora",
  "tipo": "DEPOSITO",
  "valor": 10000.00,
  "data_movimentacao": "2025-11-15"
}
```

---

### PUT /api/movimentacao-caixa/{id}

Atualiza movimentação.

---

### DELETE /api/movimentacao-caixa/{id}

Deleta movimentação.

---

## 10. Eventos Corporativos

### GET /api/evento-corporativo

Lista eventos corporativos (splits, bonificações).

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "ativo": {
        "ticker": "PETR4"
      },
      "tipo": "SPLIT",
      "fator_ajuste": 2.0,
      "data_evento": "2025-10-01",
      "aplicado": true
    }
  ]
}
```

---

### POST /api/evento-corporativo

Registra evento corporativo.

**Request**:
```json
{
  "ativo_id": "uuid-do-ativo",
  "tipo": "SPLIT",
  "fator_ajuste": 2.0,
  "data_evento": "2025-10-01"
}
```

**Tipos de Evento**:
- `SPLIT` - Desdobramento
- `BONIFICACAO` - Bonificação
- `FUSAO` - Fusão
- `SPINOFF` - Cisão
- `OPA` - Oferta Pública de Aquisição

---

### POST /api/evento-corporativo/{id}/aplicar

Aplica evento corporativo (ajusta posições/transações).

**Response** (200):
```json
{
  "success": true,
  "message": "Evento aplicado com sucesso. 5 posições ajustadas."
}
```

---

## 11. Buy Signals

### GET /api/buy-signals/buy-score/{ticker}

Calcula Buy Score (0-100) de um ativo.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "buyscore": 80,
    "recomendacao": "COMPRA",
    "precoteto": 34.39,
    "precoatual": 31.46,
    "margem_seguranca": 9.1,
    "criterios": {
      "pl": 20,
      "pvp": 18,
      "dy": 19,
      "roe": 15,
      "margem_seguranca": 8
    }
  }
}
```

**Escala de Recomendação**:
- **80-100**: COMPRA FORTE
- **60-79**: COMPRA
- **40-59**: NEUTRO
- **20-39**: VENDA
- **0-19**: VENDA FORTE

**Exemplo cURL**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/buy-signals/buy-score/PETR4 | jq .
```

---

### GET /api/buy-signals/zscore/{ticker}

Calcula Z-Score com histórico real (252 dias).

**Response** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "zscore": -1.35,
    "interpretacao": "SUBVALORIZADO",
    "preco_atual": 31.46,
    "media_252d": 34.80,
    "desvio_padrao": 2.48,
    "dias_historico": 252
  }
}
```

**Interpretação Z-Score**:
- **Z < -2**: Muito subvalorizado (forte sinal de compra)
- **-2 < Z < -1**: Subvalorizado
- **-1 < Z < 1**: Neutro (preço justo)
- **1 < Z < 2**: Sobrevalorizado
- **Z > 2**: Muito sobrevalorizado (sinal de venda)

---

### GET /api/buy-signals/margem-seguranca/{ticker}

Calcula margem de segurança (%).

**Response** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "precoatual": 31.46,
    "precoteto": 34.39,
    "margem_seguranca": 9.1,
    "recomendacao": "NEUTRO"
  }
}
```

---

### GET /api/buy-signals/watchlist-top

Top ativos por Buy Score (planejado).

---

## 12. Cálculos Financeiros

### GET /api/calculos/portfolio

Cálculos consolidados do portfolio.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "portfolioinfo": {
      "patrimoniototal": 130430.50,
      "custototal": 100000.00,
      "numativos": 17,
      "saldocaixa": 5000.00
    },
    "rentabilidade": {
      "ytd": 25.43,
      "1a": 32.5,
      "3a": 78.3
    },
    "risco": {
      "volatilidade_anualizada": 18.5,
      "sharpe_ratio": 1.45,
      "max_drawdown": -12.3,
      "beta_ibov": 0.95
    },
    "alocacao": {
      "rendavariavel": {"valor": 80000.00, "percentual": 63.8}
    },
    "dividend_yield_medio": 9.5
  }
}
```

---

### GET /api/calculos/preco-teto/{ticker}

Calcula Preço Teto (4 métodos).

**Response** (200):
```json
{
  "success": true,
  "data": {
    "ativo": "PETR4",
    "precoatual": 31.26,
    "precoteto": {
      "bazin": 35.50,
      "graham": 36.20,
      "gordon": 31.50,
      "medio": 34.39
    },
    "margemseguranca": 9.1,
    "sinal": "NEUTRO",
    "cor": "yellow",
    "parametrosregiao": {
      "taxalivrerisco": 10.5,
      "wacc": 12.5,
      "crescimento": 4.5
    }
  }
}
```

**Métodos**:
1. **Bazin**: `(DY * 100) / 6`
2. **Graham**: `√(22.5 * VPA * LPA)`
3. **Gordon**: `Dividendo / (Taxa Desconto - g)`
4. **Médio**: Média aritmética dos 3

---

## 13. Regras Fiscais

### GET /api/regras-fiscais

Lista regras fiscais cadastradas.

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "pais": "BR",
      "tipo_ativo": "ACAO",
      "aliquota_ir": 15.0,
      "incide_sobre": "GANHO_CAPITAL",
      "isento_ate": 20000.00
    },
    {
      "id": "uuid-2",
      "pais": "BR",
      "tipo_ativo": "FII",
      "aliquota_ir": 20.0,
      "incide_sobre": "GANHO_CAPITAL",
      "isento_ate": null
    }
  ]
}
```

---

### POST /api/regras-fiscais

Cria nova regra fiscal.

**Request**:
```json
{
  "pais": "US",
  "tipo_ativo": "REIT",
  "aliquota_ir": 30.0,
  "incide_sobre": "DIVIDENDO"
}
```

---

### GET /api/regras-fiscais/{id}

Detalha regra fiscal.

---

### DELETE /api/regras-fiscais/{id}

Deleta regra fiscal.

---

## 14. Feriados

### GET /api/feriados

Lista feriados de mercado.

**Query Parameters**:
- `mercado` - Filtro por mercado (BR, US, EU)
- `ano` - Filtro por ano

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "data": "2026-01-01",
      "mercado": "BR",
      "descricao": "Ano Novo"
    },
    {
      "id": "uuid-2",
      "data": "2026-04-21",
      "mercado": "BR",
      "descricao": "Tiradentes"
    }
  ]
}
```

---

### POST /api/feriados

Cadastra feriado.

---

### GET /api/feriados/{id}

Detalha feriado.

---

### DELETE /api/feriados/{id}

Deleta feriado.

---

## 15. Fontes de Dados

### GET /api/fontes

Lista fontes de dados (APIs externas).

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "nome": "brapi.dev",
      "tipo": "COTACOES",
      "prioridade": 1,
      "ativo": true,
      "rate_limit_dia": null,
      "rate_limit_minuto": 60
    },
    {
      "id": "uuid-2",
      "nome": "yfinance",
      "tipo": "COTACOES",
      "prioridade": 2,
      "ativo": true
    }
  ]
}
```

---

### POST /api/fontes

Cadastra fonte de dados.

---

### GET /api/fontes/{id}

Detalha fonte.

---

### DELETE /api/fontes/{id}

Deleta fonte.

---

## 16. Alertas

### GET /api/alertas

Lista alertas do usuário.

**Query Parameters**:
- `ativo` - Filtro por status (true/false)
- `tipo` - Filtro por tipo

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "nome": "PETR4 acima de R$ 35",
      "tipo_alerta": "ALTA_PRECO",
      "ativo": {
        "ticker": "PETR4"
      },
      "condicao_operador": ">",
      "condicao_valor": 35.0,
      "ativo_flag": true,
      "ultima_verificacao": "2026-01-06T20:00:00Z"
    }
  ],
  "total": 6
}
```

**Tipos de Alerta**:
- `ALTA_PRECO` - Preço acima de X
- `BAIXA_PRECO` - Preço abaixo de X
- `DY_MINIMO` - Dividend Yield abaixo de X%
- `PL_MAXIMO` - P/L acima de X
- `VOLUME_ANORMAL` - Volume > 2x média
- `MARGEM_SEGURANCA` - Margem >= X%

---

### POST /api/alertas

Cria novo alerta.

**Request**:
```json
{
  "nome": "VALE3 oportunidade",
  "tipo_alerta": "BAIXA_PRECO",
  "ativo_id": "uuid-do-ativo",
  "condicao_operador": "<",
  "condicao_valor": 65.0
}
```

---

### PATCH /api/alertas/{id}/toggle

Ativa/desativa alerta.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid-1",
    "ativo": false
  },
  "message": "Alerta desativado"
}
```

---

### DELETE /api/alertas/{id}

Deleta alerta.

---

## 17. Relatórios

### GET /api/relatorios/lista

Lista relatórios salvos (paginado).

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "247e-uuid",
      "tipo": "PERFORMANCE",
      "data_inicio": "2026-01-01",
      "data_fim": "2026-01-31",
      "sharpe_ratio": 1.45,
      "max_drawdown": -12.3,
      "rentabilidade_periodo": 8.5,
      "created_at": "2026-01-31T23:00:00Z"
    }
  ],
  "total": 15,
  "pages": 2
}
```

---

### POST /api/relatorios/gerar

Gera novo relatório.

**Request**:
```json
{
  "tipo": "PERFORMANCE",
  "data_inicio": "2026-01-01",
  "data_fim": "2026-01-31"
}
```

**Tipos de Relatório**:
- `PERFORMANCE` - Rentabilidade, Sharpe, Drawdown
- `FISCAL` - IR devido, transações tributáveis
- `ALOCACAO` - Distribuição por classe/setor

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "247e-uuid",
    "tipo": "PERFORMANCE",
    "sharpe_ratio": 1.45,
    "max_drawdown": -12.3,
    "rentabilidade_periodo": 8.5,
    "volatilidade": 18.2
  },
  "message": "Relatório gerado com sucesso"
}
```

---

### GET /api/relatorios/{id}

Detalha relatório.

---

### POST /api/relatorios/{id}/exportar

Exporta relatório (PDF - stub).

**Request**:
```json
{
  "formato": "PDF"
}
```

---

### DELETE /api/relatorios/{id}

Deleta relatório.

---

## 18. Cotações

### GET /api/cotacoes/{ticker}

Obtém cotação de um ativo (cache 15min).

**Response** (200 - Cache Hit):
```json
{
  "ticker": "PETR4",
  "precoatual": 31.46,
  "variacaopercentual": -0.632,
  "volume": 3764900,
  "dy12m": 9.5,
  "pl": 4.8,
  "provider": "cache-postgresql",
  "cacheageminutes": 5,
  "cachevaliduntil": "2026-01-06T23:15:00Z",
  "success": true
}
```

**Response** (200 - Cache Miss):
```json
{
  "ticker": "PETR4",
  "precoatual": 31.46,
  "variacaopercentual": -0.632,
  "volume": 3764900,
  "provider": "brapi.dev",
  "cachettlminutes": 15,
  "success": true
}
```

**Providers (ordem de fallback)**:
1. Cache PostgreSQL (15min TTL)
2. brapi.dev (primário - B3)
3. yfinance (fallback 1 - global)
4. Alpha Vantage (fallback 2 - US)
5. Finnhub (fallback 3 - US/EU)

**Exemplo cURL**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 | jq .
```

---

### GET /api/cotacoes/batch

Obtém cotações de múltiplos ativos.

**Query Parameters**:
- `symbols` - Lista de tickers separados por vírgula

**Exemplo**:
```bash
GET /api/cotacoes/batch?symbols=PETR4,VALE3,AAPL
```

**Response** (200):
```json
{
  "PETR4": {
    "precoatual": 31.46,
    "provider": "cache-postgresql",
    "success": true
  },
  "VALE3": {
    "precoatual": 69.39,
    "provider": "brapi.dev",
    "success": true
  },
  "AAPL": {
    "precoatual": 195.50,
    "provider": "yfinance-fast",
    "success": true
  }
}
```

---

### GET /api/cotacoes/health

Status do módulo de cotações.

**Response** (200):
```json
{
  "status": "ok",
  "module": "cotacoes-m7.5",
  "cachettl": "15 minutos (Prompt Mestre)",
  "providers": [
    "brapi.dev (FREE tier)",
    "yfinance",
    "alphavantage",
    "database-cache"
  ],
  "updatetrigger": "on-demand (somente quando usuário acessa tela)"
}
```

---

## 19. Projeções

### GET /api/projecoes/renda

Projeções de renda passiva (todos portfolios).

---

### GET /api/projecoes/renda/{portfolio_id}

Projeções de renda de um portfolio específico.

**Response** (200):
```json
{
  "success": true,
  "data": {
    "portfolio_id": "uuid-1",
    "projecao_mensal": 1200.00,
    "projecao_anual": 14400.00,
    "dividend_yield_medio": 9.5
  }
}
```

---

### GET /api/projecoes/cenarios

Cenários de projeção (otimista/realista/pessimista).

---

### POST /api/projecoes/recalcular

Recalcula projeções.

---

## 20. Performance

### GET /api/performance/performance

Performance detalhada do portfolio.

---

### GET /api/performance/benchmark

Comparação com benchmarks (IBOV, S&P500).

---

### GET /api/performance/correlacao

Matriz de correlação entre ativos.

---

### GET /api/performance/desvio-alocacao

Desvio da alocação alvo.

---

## Health Checks

### GET /health (Backend)

**URL**: `http://localhost:5000/health`

**Response** (200):
```json
{
  "status": "ok",
  "env": "development",
  "module": "M4 - Buy Signals & Fiscais | Portfolio",
  "service": "exitus-backend"
}
```

---

### GET /health (Frontend)

**URL**: `http://localhost:8080/health`

**Response** (200):
```json
{
  "status": "ok",
  "service": "exitus-frontend",
  "env": "development"
}
```

---

## Resumo de Endpoints

| Domínio | Endpoints | Autenticação |
|---------|-----------|--------------|
| **Autenticação** | 2 | Não |
| **Usuários** | 5 | Sim |
| **Corretoras** | 5 | Sim |
| **Ativos** | 5 | Sim |
| **Portfólios** | 11 | Sim |
| **Posições** | 2 | Sim |
| **Transações** | 5 | Sim |
| **Proventos** | 5 | Sim |
| **Movimentações** | 5 | Sim |
| **Eventos Corp.** | 3 | Sim |
| **Buy Signals** | 4 | Sim |
| **Cálculos** | 2 | Sim |
| **Regras Fiscais** | 4 | Sim |
| **Feriados** | 4 | Sim |
| **Fontes** | 4 | Sim |
| **Alertas** | 4 | Sim |
| **Relatórios** | 5 | Sim |
| **Cotações** | 3 | Sim |
| **Projeções** | 4 | Sim |
| **Performance** | 4 | Sim |
| **Health** | 2 | Não |

**Total**: **67 endpoints**

---

## Exemplos de Uso Completos

### Fluxo 1: Autenticação e Consulta de Portfolio

```bash
# 1. Login
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

# 2. Consultar Dashboard
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolios/dashboard | jq .

# 3. Consultar Performance Individual
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/performance | jq '.data.ativos[0]'
```

---

### Fluxo 2: Registrar Transação

```bash
# 1. Listar ativos disponíveis
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/ativos?ticker=PETR4 | jq '.data[0].id'

# 2. Listar corretoras
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/corretoras | jq '.data[0].id'

# 3. Registrar compra
curl -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ativo_id": "uuid-petr4",
    "corretora_id": "uuid-corretora",
    "tipo": "COMPRA",
    "quantidade": 100,
    "preco_unitario": 31.50,
    "taxas": 5.00,
    "data_transacao": "2026-01-06"
  }'
```

---

### Fluxo 3: Criar Alerta

```bash
# 1. Criar alerta de preço
curl -X POST http://localhost:5000/api/alertas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "PETR4 oportunidade",
    "tipo_alerta": "BAIXA_PRECO",
    "ativo_id": "uuid-petr4",
    "condicao_operador": "<",
    "condicao_valor": 30.0
  }'

# 2. Listar alertas ativos
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/alertas?ativo=true | jq .
```

---

### Fluxo 4: Análise de Buy Signal

```bash
# 1. Buy Score
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/buy-signals/buy-score/PETR4 | jq .

# 2. Preço Teto
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/calculos/preco-teto/PETR4 | jq .

# 3. Z-Score
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/buy-signals/zscore/PETR4 | jq .
```

---

## Versionamento da API

**Versão Atual**: `v0.7.6`

**Changelog**: Ver [CHANGELOG.md](CHANGELOG.md)

**Breaking Changes**: Nenhuma mudança quebra de compatibilidade desde v0.7.0

---

## Referências

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura e tecnologias
- [MODULES.md](MODULES.md) - Detalhes de cada módulo
- [USER_GUIDE.md](USER_GUIDE.md) - Guia do usuário
- [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) - Operações

---

**Documento gerado**: 06 de Janeiro de 2026  
**Versão**: v0.7.6  
**Baseado em**: API_REFERENCE_COMPLETE.md (67 rotas), validações M4/M7.5
