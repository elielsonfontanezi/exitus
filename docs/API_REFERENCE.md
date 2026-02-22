# API Reference — Sistema Exitus v0.7.10

## Índice
- Informações Gerais
- 1. Autenticação
- 2. Usuários
- 3. Corretoras
- 4. Ativos
- 5. Portfólios
- 6. Posições
- 7. Transações
- 8. Proventos
- 9. Movimentações de Caixa
- 10. Eventos Corporativos
- 11. Buy Signals
- 12. Cálculos Financeiros
- 13. Regras Fiscais
- 14. Feriados
- 15. Fontes de Dados
- 16. Alertas
- 17. Relatórios
- 18. Cotações
- 19. Projeções
- 20. Performance
- Health Checks

---

## Informações Gerais

### Base URL
```
http://localhost:5000/api      # Desenvolvimento
https://seu-dominio.com/api    # Produção (quando deployado)
```

Endpoints usam snake_case (ex.: `api/portfolio/dashboard`).

### Autenticação
Todas as rotas exceto `/auth/login` e `/auth/register` requerem JWT Bearer Token.

Header obrigatório:
```
Authorization: Bearer <seu_token_jwt>
```

Obter Token:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}'
```

Expiry: 1 hora (3600 segundos).

### Formato de Resposta

Sucesso:
```json
{"success": true, "data": {}, "message": "Operação realizada com sucesso"}
```

Erro:
```json
{"error": "Descrição do erro", "status_code": 400}
```

Lista paginada:
```json
{
  "success": true,
  "data": {},
  "total": 127,
  "pages": 13,
  "page": 1,
  "per_page": 10
}
```

### Paginação
Parâmetros de query:
- `page` — Número da página (default: 1)
- `per_page` — Itens por página (default: 10, max: 100)

Exemplo:
```bash
GET /api/transacoes?page=2&per_page=20
```

### Códigos de Status HTTP

| Código | Significado |
|---|---|
| 200 | OK — Sucesso |
| 201 | Created — Recurso criado |
| 400 | Bad Request — Dados inválidos |
| 401 | Unauthorized — Token ausente/inválido |
| 403 | Forbidden — Sem permissão |
| 404 | Not Found — Recurso não encontrado |
| 500 | Internal Server Error — Erro no servidor |

---

## 1. Autenticação

### POST /api/auth/login
Autentica usuário e retorna token JWT.

Request:
```json
{"username": "admin", "password": "senha123"}
```

Response 200:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "<uuid>",
      "username": "admin",
      "email": "admin@exitus.com",
      "role": "admin"
    }
  },
  "message": "Login realizado com sucesso"
}
```

### POST /api/auth/register
Registra novo usuário.

---

## 2. Usuários
CRUD básico de usuários: lista, detalhe, update, soft delete, conforme estrutura atual.

---

## 3. Corretoras
CRUD de corretoras com validação de propriedade do usuário. Retorna `403` quando a
corretora pertence a outro usuário (não `404`).

---

## 4. Ativos

### GET /api/ativos
Lista ativos paginado, com filtros opcionais.

Query Parameters:
- `ticker` — Filtro por ticker (ex.: `?ticker=PETR4`)
- `tipo` — Filtro por tipo (Enum TipoAtivo)
- `mercado` — Filtro por mercado: `BR`, `US`, `EU`, `ASIA`, `GLOBAL`

**Enum TipoAtivo — 14 valores:**
- Brasil (BR): `acao`, `fii`, `cdb`, `lci_lca`, `tesouro_direto`, `debenture`
- Estados Unidos (US): `stock`, `reit`, `bond`, `etf`
- Internacional: `stock_intl`, `etf_intl`
- Outros: `cripto`, `outro`

Response 200:
```json
{
  "success": true,
  "data": {
    "ativos": [
      {
        "id": "<uuid>",
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
        "cap_rate": null
      }
    ]
  },
  "total": 70,
  "pages": 7,
  "page": 1,
  "per_page": 10
}
```

### GET /api/ativos/{id}
Detalha ativo.

### POST /api/ativos
Cria novo ativo (admin only).

Campos obrigatórios: `ticker`, `nome`, `tipo`, `classe`, `mercado`, `moeda`.

**Enum ClasseAtivo:** `renda_variavel`, `renda_fixa`, `cripto`, `commodity`, `hibrido`

Para referência completa dos enums, consulte `ENUMS.md`.

---

## 5. Portfólios
APIs de dashboard, alocação, performance e carteiras customizadas:
- `GET /api/portfolio/dashboard`
- `GET /api/portfolio/alocacao`
- `GET /api/portfolio/performance`
- `GET /api/portfolio/evolucao`
- CRUD de `/api/portfolios`

---

## 6. Posições

> **Atualizado em v0.7.10** — 7 GAPs resolvidos. Schema completo com nested.
> Ver `M2_POSICOES.md` para histórico de validação.

### GET /api/posicoes
Lista posições do usuário autenticado com paginação e filtros.

Query Parameters:
- `page` — Página atual (default: 1)
- `per_page` — Itens por página (default: 50, max: 100)
- `ativo_id` — Filtrar por UUID do ativo
- `corretora_id` — Filtrar por UUID da corretora
- `ticker` — Filtrar por ticker do ativo (busca parcial, case-insensitive)
- `lucro_positivo` — `true` retorna apenas posições com lucro realizado > 0

Response 200:
```json
{
  "success": true,
  "data": {
    "posicoes": [
      {
        "id": "4990b451-0dbd-4235-93e9-2a950b0758cf",
        "usuario_id": "783c2bfd-9e36-4cbd-a4fb-901afae9fad3",
        "ativo_id": "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad",
        "corretora_id": "c5c2bc9d-2dde-4d16-ad9b-868628a746d1",
        "quantidade": 30,
        "preco_medio": 150.233333,
        "custo_total": 4507.0,
        "taxas_acumuladas": 7.0,
        "impostos_acumulados": 0.0,
        "valor_atual": null,
        "lucro_prejuizo_realizado": 0.0,
        "lucro_prejuizo_nao_realizado": null,
        "data_primeira_compra": "2025-06-09",
        "data_ultima_atualizacao": "2025-12-13T01:11:48",
        "ativo": {
          "id": "b8e4ccc8-3dfe-4a97-a8eb-e21a24c2e2ad",
          "ticker": "KNRI11",
          "nome": "Kinea Renda Imobiliária FII",
          "tipo": "fii",
          "classe": "renda_variavel",
          "mercado": "BR",
          "moeda": "BRL",
          "preco_atual": 149.51,
          "dividend_yield": 9.8
        },
        "corretora": {
          "id": "c5c2bc9d-2dde-4d16-ad9b-868628a746d1",
          "nome": "Clear Corretora",
          "tipo": "corretora",
          "pais": "BR",
          "moeda_padrao": "BRL"
        }
      }
    ]
  },
  "total": 17,
  "pages": 1,
  "page": 1,
  "per_page": 50,
  "message": "17 posições encontradas"
}
```

> **Nota:** `valor_atual` e `lucro_prejuizo_nao_realizado` são `null` até que o
> serviço de cotações (M7.5) execute `atualizar_valores_atuais()`.

### GET /api/posicoes/{id}
Retorna posição pelo ID com nested `ativo` e `corretora`.

- `403` se a posição pertence a outro usuário
- `404` se o ID não existe

### POST /api/posicoes/calcular
Recalcula todas as posições do usuário a partir do histórico de transações.

Quando usar:
- Após importação de transações em lote
- Quando posições aparecem inconsistentes
- Após correção manual de transações

Response 200:
```json
{
  "success": true,
  "data": {
    "posicoes_criadas": 0,
    "posicoes_atualizadas": 17,
    "posicoes_zeradas": 0
  },
  "message": "Recalculo concluido: 0 criadas, 17 atualizadas, 0 zeradas"
}
```

### GET /api/posicoes/resumo
Retorna resumo consolidado das posições do usuário.

Response 200:
```json
{
  "success": true,
  "data": {
    "quantidade_posicoes": 17,
    "total_investido": 45070.0,
    "total_valor_atual": 0.0,
    "total_lucro_realizado": 0.0,
    "total_lucro_nao_realizado": 0.0,
    "lucro_total": 0.0,
    "roi_percentual": 0.0
  }
}
```

---

## 7. Transações
Filtros e payload mantidos — `tipo` usa Enum TipoTransacao
(ex.: `COMPRA`, `VENDA`, `DIVIDENDO`, `JCP`, etc.).

---

## 8. Proventos
APIs de listagem, criação, update e delete de proventos.
`tipo` usa Enum TipoProvento: `DIVIDENDO`, `JCP`, `RENDIMENTO`, `CUPOM`, etc.

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

continuam com o mesmo contrato descrito na versão v0.7.6, consumindo os valores
de enums documentados em `ENUMS.md` e refletidos no schema atual.

---

*Documento atualizado: 22 de Fevereiro de 2026*
*Versão da API: v0.7.10*
*GAPs fechados nesta versão: EXITUS-POS-001 a EXITUS-POS-007 (M2-POSICOES)*
*GAP EXITUS-DOCS-API-001 fechado — GET /api/ativos responde `.data.ativos`, total: 70*
*Pendência menor: EXITUS-POS-008 — enum serialization em nested (não-bloqueante)*
