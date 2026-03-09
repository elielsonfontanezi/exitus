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
- 21. Reconciliação
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

## 9. Movimentações de Caixa

**Base URL**: `/api/movimentacoes`  
**Auth**: Bearer JWT obrigatório em todas as rotas.

### GET /api/movimentacoes
Lista movimentações de caixa do usuário autenticado.

Query params: `page`, `per_page` (max 100), `corretora_id`, `data_inicio`, `data_fim`

Response 200:
```json
{
  "success": true,
  "data": {
    "movimentacoes": [...],
    "total": 2
  },
  "message": "2 movimentações encontradas"
}
```

### GET /api/movimentacoes/saldo/{corretora_id}
Retorna saldo calculado para uma corretora.

Response 200:
```json
{
  "success": true,
  "data": { "saldo": 5000.0, "corretora_id": "uuid" }
}
```

---

## 10. Buy Signals (M4)

**Base URL**: `/api/buy-signals`  
**Auth**: Não requer JWT (endpoints públicos de análise).  
**Nota**: Retorna 404 se ticker não encontrado no banco.

### GET /api/buy-signals/buy-score/{ticker}
Calcula score de compra (0-100) baseado em margem de segurança, Z-Score, DY e Beta.

Response 200:
```json
{
  "success": true,
  "data": {
    "ticker": "VALE3",
    "buy_score": 42
  }
}
```

Response 404 (ticker não existe):
```json
{ "success": false, "error": "Ativo XYZABC não encontrado" }
```

### GET /api/buy-signals/margem-seguranca/{ticker}
Calcula margem de segurança em relação ao preço teto.

Response 200:
```json
{
  "success": true,
  "data": {
    "ticker": "PETR4",
    "margem_seguranca": 12.5,
    "sinal": "🟢 COMPRA"
  },
  "message": "Margem de segurança: 12.50% vs Teto R$38.00"
}
```

Response 400 (preço teto não cadastrado):
```json
{ "success": false, "error": "Preço teto inválido." }
```

### GET /api/buy-signals/zscore/{ticker}
Calcula Z-Score baseado no histórico de preços (mínimo 30 dias).

Response 200:
```json
{
  "success": true,
  "data": { "ticker": "VALE3", "z_score": -0.85 }
}
```

Response 400 (histórico insuficiente):
```json
{ "success": false, "error": "Histórico insuficiente: 5 dias (mínimo 30)" }
```

### GET /api/buy-signals/watchlist-top
Retorna top 10 ativos por buy_score.

Response 200:
```json
{
  "success": true,
  "data": [
    { "ticker": "PETR4", "buy_score": 78, "preco_atual": 36.5, "preco_teto": 42.0 }
  ]
}
```

---

## 11. Alertas (M7.4)

**Base URL**: `/api/alertas`  
**Auth**: Bearer JWT obrigatório em todas as rotas.

### GET /api/alertas
Lista alertas do usuário autenticado.

Response 200:
```json
{
  "success": true,
  "data": [ { "id": "uuid", "nome": "PETR4 > 40", "ativo": true, ... } ],
  "message": "1 alerta(s) encontrado(s)"
}
```

Response 401 (sem token):
```json
{ "msg": "Missing Authorization Header" }
```

### POST /api/alertas
Cria novo alerta.

Body obrigatório: `nome`. Campos opcionais: `tipo_alerta`, `frequencia_notificacao`.  
Enums em minúsculo: `tipo_alerta` (ex.: `"preco_alvo"`), `frequencia_notificacao` (ex.: `"diaria"`).

Response 201:
```json
{
  "success": true,
  "message": "Alerta criado com sucesso",
  "data": { "id": "uuid", "nome": "PETR4 > 40", ... }
}
```

### PATCH /api/alertas/{alerta_id}/toggle
Alterna status ativo/inativo do alerta.

Response 200:
```json
{ "success": true, "message": "Status atualizado" }
```

Response 404:
```json
{ "success": false, "message": "Alerta não encontrado" }
```

### DELETE /api/alertas/{alerta_id}
Remove alerta.

Response 200:
```json
{ "success": true, "message": "Alerta removido" }
```

---

## 12. Cotações em Tempo Real (M7.5)

**Base URL**: `/api/cotacoes`  
**Auth**: Bearer JWT obrigatório.  
**Cache**: TTL 15 minutos por ativo. Se `data_ultima_cotacao < 15min`, retorna dados do banco sem chamar API externa. Após expirar, consulta provedores externos (brapi.dev → yfinance → fallback banco).

### GET /api/cotacoes/{ticker}
Retorna cotação atual do ativo.

Response 200 (cache válido):
```json
{
  "success": true,
  "data": {
    "ticker": "VALE3",
    "preco_atual": 68.5,
    "dy_12m": 0.12,
    "pl": 5.2,
    "provider": "database_cache",
    "cache_age_minutes": 3,
    "cache_valid_until": "2026-02-27T18:45:00"
  },
  "message": "Cotação VALE3 (cache)"
}
```

Response 200 (API externa):
```json
{
  "success": true,
  "data": {
    "ticker": "VALE3",
    "preco_atual": 68.5,
    "provider": "brapi.dev",
    "cache_ttl_minutes": 15
  },
  "message": "Cotação VALE3 atualizada"
}
```

Response 200 (fallback banco — APIs indisponíveis):
```json
{
  "success": true,
  "data": {
    "ticker": "VALE3",
    "preco_atual": 67.0,
    "provider": "database_fallback",
    "warning": "APIs indisponíveis - dados podem estar desatualizados"
  },
  "message": "Cotação VALE3 (fallback - dados podem estar desatualizados)"
}
```

Response 404:
```json
{ "error": "Ativo XYZABC não encontrado" }
```

### GET /api/cotacoes/batch?symbols=PETR4,VALE3
Cotações em lote (máx 10 tickers por requisição).

Response 200:
```json
{
  "PETR4": { "ticker": "PETR4", "preco_atual": 36.5, "provider": "brapi.dev", "success": true },
  "VALE3": { "ticker": "VALE3", "preco_atual": 68.5, "provider": "database_cache", "success": true }
}
```

### GET /api/cotacoes/health
Health check do módulo de cotações (não requer JWT).

Response 200:
```json
{
  "status": "ok",
  "module": "cotacoes_m7.5",
  "cache_ttl": "15 minutos",
  "providers": ["brapi.dev (FREE tier)", "yfinance", "alphavantage", "database_cache"]
}
```

---

## 10. Eventos Corporativos

CRUD completo + ação de aplicar evento. **POST/PUT/DELETE requerem role `admin`.**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/eventos-corporativos/` | Listar eventos (paginado, filtro `ativo_id`) |
| GET | `/api/eventos-corporativos/<id>` | Obter evento por ID |
| POST | `/api/eventos-corporativos/` | Criar evento corporativo |
| PUT | `/api/eventos-corporativos/<id>` | Atualizar evento |
| DELETE | `/api/eventos-corporativos/<id>` | Deletar evento |
| POST | `/api/eventos-corporativos/<id>/aplicar` | Aplicar evento às posições do usuário |

**Campos POST/PUT:**
- `ativo_id` (UUID, obrigatório no POST)
- `tipo_evento` (enum: split, grupamento, bonificacao, direito_sub, fusao, cisao, incorporacao, mudanca_ticker, deslistagem, relisting, cancelamento, outro)
- `data_evento` (date, obrigatório no POST)
- `descricao` (string min 3 chars, obrigatório no POST)
- `data_com`, `proporcao`, `ativo_novo_id`, `observacoes` (opcionais)

## 13. Regras Fiscais

CRUD completo. **POST/PUT/DELETE requerem role `admin`.**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/regras-fiscais/` | Listar regras (paginado, filtros: `pais`, `tipo_ativo`, `ativa`) |
| GET | `/api/regras-fiscais/<id>` | Obter regra por ID |
| POST | `/api/regras-fiscais/` | Criar regra fiscal |
| PUT | `/api/regras-fiscais/<id>` | Atualizar regra |
| DELETE | `/api/regras-fiscais/<id>` | Deletar regra |

**Campos POST/PUT:**
- `pais` (string 2 chars ISO, obrigatório no POST)
- `aliquota_ir` (float 0-100, obrigatório no POST)
- `incide_sobre` (enum: lucro, receita, provento, operacao)
- `descricao` (string min 3 chars, obrigatório no POST)
- `vigencia_inicio` (date, obrigatório no POST)
- `tipo_ativo`, `tipo_operacao`, `valor_isencao`, `vigencia_fim`, `ativa` (opcionais)

## 14. Feriados

CRUD completo. **POST/PUT/DELETE requerem role `admin`.**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/feriados/` | Listar feriados (paginado, filtros: `pais`, `mercado`, `ano`) |
| GET | `/api/feriados/<id>` | Obter feriado por ID |
| POST | `/api/feriados/` | Criar feriado |
| PUT | `/api/feriados/<id>` | Atualizar feriado |
| DELETE | `/api/feriados/<id>` | Deletar feriado |

**Campos POST/PUT:**
- `pais` (string 2 chars ISO, obrigatório no POST)
- `data_feriado` (date, obrigatório no POST)
- `tipo_feriado` (enum: nacional, bolsa, ponte, antecip, manutencao, outro)
- `nome` (string min 3 chars, obrigatório no POST)
- `mercado`, `horario_fechamento`, `recorrente`, `observacoes` (opcionais)

## 15–20. Demais Módulos

As APIs de Cálculos Financeiros, Fontes de Dados, Relatórios, Projeções e Performance
seguem o mesmo contrato padrão:
- **Auth**: Bearer JWT obrigatório.
- **Response sucesso**: `{"success": true, "data": {...}, "message": "..."}`.
- **Response erro**: `{"success": false, "message": "..."}`.
- **Enums**: consultar `docs/ENUMS.md`.

---

## 21. Exportação de Dados

> **GAP:** EXITUS-EXPORT-001 ✅ — Documentação detalhada: `docs/EXITUS-EXPORT-001.md`

Exportação de dados do portfólio em múltiplos formatos para análise externa.

**Auth:** Bearer JWT obrigatório em todos os endpoints.  
**Resposta:** arquivo para download direto (não usa envelope `success/data`).

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/export/transacoes` | Exporta transações (compras, vendas, etc.) |
| GET | `/api/export/proventos` | Exporta proventos (dividendos, JCP, aluguéis) |
| GET | `/api/export/posicoes` | Exporta posição consolidada atual |

**Parâmetros (query string):**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `formato` | string | `csv` \| `excel` \| `json` \| `pdf` (default: `json`) |
| `data_inicio` | YYYY-MM-DD | Filtro de data inicial |
| `data_fim` | YYYY-MM-DD | Filtro de data final |
| `ativo_id` | UUID | Filtrar por ativo |
| `corretora_id` | UUID | Filtrar por corretora (apenas transações) |
| `tipo` | string | Tipo da operação/provento (depende da entidade) |

**Headers da resposta:**
```
Content-Disposition: attachment; filename="exitus_transacoes_20250303_1800.csv"
Content-Type: text/csv; charset=utf-8          (CSV)
Content-Type: application/json                 (JSON)
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet  (Excel)
Content-Type: application/pdf                  (PDF)
X-Total-Records: <tamanho_em_bytes>
```

**Erros:**

| HTTP | Situação |
|------|----------|
| 401 | Token ausente ou inválido |
| 422 | Formato inválido, data mal formatada, tipo desconhecido |
| 500 | Erro interno (render, query) |

**Exemplos:**
```bash
# CSV de transações — período 2025
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/transacoes?formato=csv&data_inicio=2025-01-01&data_fim=2025-12-31" \
  -o transacoes_2025.csv

# Excel de proventos
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/proventos?formato=excel" -o proventos.xlsx

# PDF de posições
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/export/posicoes?formato=pdf" -o posicoes.pdf
```

---

## 22. IR — Apuração de Imposto de Renda

> **GAP:** EXITUS-IR-001 ✅ — Documentação detalhada: `docs/EXITUS-IR-001.md`

Engine de apuração mensal de IR sobre renda variável.

**Auth:** Bearer JWT obrigatório.  
**Resposta:** envelope padrão `{"success": true, "data": {...}}`.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/ir/apuracao?mes=YYYY-MM` | Apuração detalhada por categoria (swing, day-trade, FIIs, exterior) |
| GET | `/api/ir/darf?mes=YYYY-MM` | DARFs a pagar no mês (código de receita, valor, status) |
| GET | `/api/ir/historico?ano=YYYY` | Resumo anual mês a mês (sempre 12 entradas) |

**Categorias e alíquotas:** ações BR 15% (isenção R$20k/mês), day-trade 20%, FIIs 20%, exterior 15%.  
**Códigos DARF:** 6015 (BR) / 0561 (exterior). Mínimo para recolhimento: R$10,00.

---

## 21. Rentabilidade (EXITUS-RENTABILIDADE-001)

**Auth:** Bearer JWT obrigatório.  
**Resposta:** envelope padrão `{"success": true, "data": {...}}`.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/portfolios/rentabilidade` | Calcula TWR, MWR/XIRR e comparação com benchmark |

**Query params:**

| Parâmetro | Valores aceitos | Default |
|-----------|----------------|---------|
| `periodo` | `1m`, `3m`, `6m`, `12m`, `24m`, `ytd`, `max` | `12m` |
| `benchmark` | `CDI`, `IBOV`, `IFIX`, `IPCA6`, `SP500` | `CDI` |

**Exemplo:**
```bash
GET /api/portfolios/rentabilidade?periodo=6m&benchmark=CDI
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "periodo": "6m",
    "data_inicio": "2025-09-08",
    "data_fim": "2026-03-08",
    "dias": 181,
    "twr": 0.1234,
    "twr_percentual": 12.34,
    "mwr": 0.1189,
    "mwr_percentual": 11.89,
    "benchmark": {
      "nome": "CDI",
      "retorno": 0.0672,
      "retorno_percentual": 6.72
    },
    "alpha": 0.0562,
    "alpha_percentual": 5.62,
    "total_fluxos": 3
  }
}
```

**Observações:**
- **TWR** (Time-Weighted Return): remove efeito de aportes/resgates. Padrão GIPS.
- **MWR** (Money-Weighted Return / XIRR): TIR considerando fluxo de caixa real do investidor.
- **CDI**: calculado via `parametros_macro.taxa_livre_risco` (dias úteis/252).
- **IBOV/IFIX/SP500**: retorno via `historico_preco` dos ativos BOVA11/IFIX11/IVVB11.
- **IPCA6**: IPCA (`parametros_macro.inflacao_anual`) + 6% a.a.

---

## 21. Reconciliação (EXITUS-RECONCILIACAO-001)

**Auth:** Bearer JWT obrigatório.  
**Resposta:** envelope padrão.

Endpoints para verificação de consistência entre dados calculados e importados.

### GET /api/reconciliacao/verificar

Executa verificação completa de reconciliação (posições, saldos, integridade).

**Resposta:**
```json
{
  "status": "OK",
  "divergencias": [],
  "resumo": {
    "total_divergencias": 0,
    "erros": 0,
    "avisos": 0
  }
}
```

**Status possíveis:**
- `OK`: Nenhuma divergência encontrada
- `WARNING`: Divergências menores (custos, saldos com tolerância)
- `ERROR`: Divergências críticas (quantidade de posições)

**Exemplo com divergências:**
```json
{
  "status": "ERROR",
  "divergencias": [
    {
      "tipo": "POSICAO_QUANTIDADE",
      "severidade": "ERROR",
      "ativo_ticker": "PETR4",
      "corretora_nome": "Clear",
      "quantidade_posicao": 100.0,
      "quantidade_calculada": 150.0,
      "diferenca": 50.0,
      "mensagem": "Divergência de quantidade: PETR4 na Clear"
    }
  ],
  "resumo": {
    "total_divergencias": 1,
    "erros": 1,
    "avisos": 0
  }
}
```

### GET /api/reconciliacao/posicoes

Verifica apenas reconciliação de posições (quantidade e custo).

**Resposta:**
```json
{
  "divergencias": [
    {
      "tipo": "POSICAO_CUSTO",
      "severidade": "WARNING",
      "ativo_ticker": "VALE3",
      "corretora_nome": "XP",
      "custo_posicao": 5000.0,
      "custo_calculado": 5050.0,
      "diferenca": 50.0,
      "mensagem": "Divergência de custo: VALE3"
    }
  ],
  "total": 1
}
```

### GET /api/reconciliacao/saldos

Verifica saldos de corretoras vs soma de movimentações de caixa.

**Resposta:**
```json
{
  "divergencias": [
    {
      "tipo": "SALDO_CORRETORA",
      "severidade": "WARNING",
      "corretora_nome": "Clear",
      "saldo_registrado": 10000.0,
      "saldo_calculado": 9950.0,
      "diferenca": 50.0,
      "mensagem": "Divergência de saldo na corretora Clear"
    }
  ],
  "total": 1
}
```

### GET /api/reconciliacao/integridade

Verifica integridade geral de transações (sem ativo, duplicadas, quantidade zero).

**Resposta:**
```json
{
  "divergencias": [
    {
      "tipo": "TRANSACAO_DUPLICADA",
      "severidade": "WARNING",
      "hash_importacao": "a1b2c3d4e5f6...",
      "quantidade": 2,
      "mensagem": "2 transações com mesmo hash de importação"
    }
  ],
  "total": 1
}
```

### GET /api/reconciliacao/ativo/{ativo_id}

Verifica reconciliação de um ativo específico.

**Query params:**
- `corretora_id` (opcional): Filtrar por corretora específica

**Resposta:**
```json
{
  "ativo_id": "uuid-do-ativo",
  "corretoras": [
    {
      "corretora_id": "uuid-corretora",
      "corretora_nome": "Clear",
      "quantidade_posicao": 100.0,
      "quantidade_calculada": 100.0,
      "diferenca": 0.0,
      "status": "OK"
    }
  ],
  "divergencias": []
}
```

**Tolerâncias:**
- Quantidade: 0.01 (arredondamento)
- Custos/Saldos: R$ 1,00

---

## 22. Importação B3 (EXITUS-VALIDATION-001)

**Auth:** Bearer JWT obrigatório.  
**Resposta:** envelope padrão.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/import/movimentacoes` | Importa movimentações B3 (proventos, eventos de custódia) |
| POST | `/api/import/negociacoes` | Importa negociações B3 (compras e vendas) |

**Body (multipart/form-data):**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `file` | File | Arquivo `.xlsx` ou `.csv` exportado do Portal B3 |
| `dry_run` | bool | `true` = preview sem persistir (default: `false`) |

**Resposta importação movimentações:**
```json
{
  "success": true,
  "data": {
    "proventos": {
      "sucesso": 12,
      "erros": 0,
      "duplicatas_ignoradas": 3,
      "duplicatas_lista": ["Duplicata ignorada: PETR4 em 2025-03-15 (hash=a1b2c3d4...)"]
    },
    "ativos_criados": 2,
    "corretoras_criadas": 0,
    "dry_run": false
  }
}
```

**Comportamento de idempotência:**
- Hash MD5 calculado por linha (`arquivo_origem + conteúdo`) — reimportar o mesmo arquivo é bloqueado.
- Arquivos distintos com mesmo conteúdo geram hashes diferentes (arquivo faz parte da chave).
- Campos de texto sanitizados: tags HTML removidas, caracteres de controle Unicode removidos.

---

*Documento atualizado: 09 de Março de 2026*
*Versão da API: v0.8.0-dev*
*GAPs fechados: EXITUS-POS-001→007, EXITUS-ATIVOS-ENUM-001, EXITUS-POS-PAGIN-001,*
*EXITUS-PROV-SLASH-001, EXITUS-BUYSIG-SCORE-001, EXITUS-ALERTAS-RESP-001, EXITUS-COTACOES-RESP-001,*
*EXITUS-SQLALCHEMY-001, EXITUS-CRUD-001, EXITUS-IR-001, EXITUS-EXPORT-001,*
*EXITUS-VALIDATION-001, EXITUS-RENTABILIDADE-001, EXITUS-SERVICE-REVIEW-001, EXITUS-COVERAGE-001,*
*EXITUS-DOCS-SYNC-001, EXITUS-AUDITLOG-001, EXITUS-RECONCILIACAO-001*
