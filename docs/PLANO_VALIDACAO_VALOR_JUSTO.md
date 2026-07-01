# Plano de Validação — Pipeline de Dados e Valor Justo

**Data:** 01/07/2026  
**GAP:** `VAL-PIPE-001`  
**Status:** 📋 Planejado (documentação aprovada; implementação pendente)  
**Relacionado:** [`valuation_service.py`](../backend/app/services/valuation_service.py), [`MANUAL_USUARIO_DRAFT.md`](MANUAL_USUARIO_DRAFT.md), [`PLANO_MASSA_TESTES_MENU.md`](PLANO_MASSA_TESTES_MENU.md)

---

## Objetivo

Validar em **4 camadas** a confiabilidade do **Valor Justo** (`valor_justo`):

1. **Cotações** — preços com atraso ≤ 15 minutos (TTL)
2. **Indicadores** — `parametros_macro` (k, g, WACC, cap_rate_fii, CDI/IPCA/SELIC)
3. **Histórico** — `historico_preco` populado para Z-Score, correlação, benchmarks
4. **Valuation** — fórmulas por perfil/tipo de ativo vs dados de mercado (golden datasets)

**Princípio:** dados primeiro, cálculo depois. Não certificar fórmulas enquanto B1–B3 não estiverem verdes.

---

## Arquitetura (4 camadas)

```
Camada 1 — Ingestão
  Providers (Brapi, Finnhub, Alpha, YF, Twelve) → Circuit Breaker → TTL 15min

Camada 2 — Persistência
  ativo (preco_atual, dy, eps, fcf, ffo) + parametros_macro + historico_preco

Camada 3 — Valuation
  valuation_service.calcular_valor_justo() — perfis dividendos/growth/bancos/fii/padrao

Camada 4 — Consumo
  /api/calculos/preco_teto, /api/buy-signals/*, /ferramentas/preco-teto, buy-signals, detalhe ativo
```

---

## Estado atual (diagnóstico 01/07/2026)

### O que já existe

| Componente | Arquivo | Testes |
|------------|---------|--------|
| Valuation | `valuation_service.py` | `test_valuation_service.py` (26) |
| API preço teto | `calculos_blueprint.py` | `test_calculos.py` |
| Buy signals | `buy_signals_service.py` | `test_buy_signals*.py` |
| TTL 15min | `cotacoes_blueprint.py` | `test_cotacoes_health.py` (health only) |
| Indicadores dashboard | `indicadores_service.py` | `test_indicadores_dashboard.py` |
| Histórico lazy | `historico_service.py` | **sem testes dedicados** |

### Lacunas conhecidas

| ID | Lacuna |
|----|--------|
| V-GAP-01 | EPS/FCF não atualizados por cotações (só seed) |
| V-GAP-02 | `ativo.cap_rate` ignorado — usa `cap_rate_fii` macro |
| V-GAP-03 | Fallbacks dy=0.06, preco=30 quando NULL |
| V-GAP-04 | 3 esquemas de sinal (valuation / margem / buy_score) |
| V-GAP-05 | `stock_intl` sem perfil growth |
| V-GAP-06 | `GET /api/cotacoes/batch` ignora TTL 15min |
| V-GAP-07 | Zero testes para `buscar_historico` e cascade de providers |

---

## Fase B — Validar leituras de dados

### B1. Cotações (atraso ≤ 15 min)

**Endpoint:** `GET /api/cotacoes/{ticker}` — TTL **900s**.

| Caso | Aceite |
|------|--------|
| Cache hit | 2ª chamada em &lt;15min → `provider: database_cache` |
| Cache miss | `data_ultima_cotacao` &gt;15min → cascade externo |
| Fallback | Provider falha → `database_fallback` |
| Health | `GET /api/cotacoes/health?ttl_minutos=15` — 0 desatualizados após refresh |

**Teste novo:** `backend/tests/test_cotacoes_ttl.py`

**Runbook manual:**
```bash
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e_user","password":"e2e_senha_123"}' | jq -r '.data.access_token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/cotacoes/PETR4
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/cotacoes/PETR4  # cache
curl http://localhost:5000/api/cotacoes/health?ttl_minutos=15
```

### B2. Indicadores macro

**Fontes:** `parametros_macro` (CDI, IPCA, SELIC, k, g, WACC, cap_rate_fii).

| Indicador | Validação |
|-----------|-----------|
| CDI, IPCA, SELIC | Faixas plausíveis; estender `test_indicadores_dashboard.py` |
| Ibovespa | Env `IBOVESPA_ANUAL` — **não** input de valuation |
| k, g, WACC, cap_rate_fii | Obrigatório não-NULL antes da Fase C |

### B3. Histórico de preços

**Serviço:** `HistoricoService.obter_ou_criar_historico()` → `CotacoesService.buscar_historico()`.

| Caso | Aceite |
|------|--------|
| Lazy populate | count &lt; 80% de `dias` → popula |
| Cascade BR/US | brapi → twelve → alpha → yfinance (mock) |
| Consumidores | ≥30–252 dias para Z-Score, correlação, benchmarks |

**Testes novos:** `test_historico_service.py`, `test_buscar_historico_cascade.py`

---

## Fase C — Valor Justo por tipo de ativo

Inicia somente após B1+B2+B3 verdes para tickers golden.

### Matriz tipo × perfil × métodos

| Tipo / Perfil | Tickers golden | Métodos |
|---------------|----------------|---------|
| ACAO dividendos | PETR4, VALE3 | Bazin, Graham, Gordon, DCF |
| ACAO bancos | ITUB4 | idem (pesos bancos) |
| STOCK growth US | NVDA, AAPL | idem (pesos growth) |
| FII | HGLG11, KNRI11 | cap_rate, ffo, affo |
| REIT US | O, PLD | cap_rate variants |
| STOCK_INTL / BDR | TSLA34 | equity (perfil dividendos) — limitação V-GAP-05 |
| ETF / CRIPTO / RF | BOVA11, BTC | fallback `preco × 1.1` — **PARCIAL** |

### Golden dataset

Arquivo previsto: `backend/tests/fixtures/valuation_golden.json`  
Teste previsto: `backend/tests/test_valuation_golden.py`

Exemplo ITUB4:
```json
{
  "inputs": { "preco_atual": 32.45, "dividend_yield": 0.085, "eps": 3.12, "fcf": 8.5 },
  "macro": { "taxa_livre_risco": 0.1075, "crescimento_medio": 0.04, "custo_capital": 0.12 },
  "expected": { "perfil": "bancos", "valor_justo_min": 28.0, "valor_justo_max": 45.0 }
}
```

Fórmulas de referência: [`MANUAL_USUARIO_DRAFT.md`](MANUAL_USUARIO_DRAFT.md).

---

## Fase D — Ponta a ponta (API + UI)

| Tela | API | Verificação |
|------|-----|-------------|
| `/ferramentas/preco-teto` | `GET /api/calculos/preco_teto/{ticker}` | Métodos UI = JSON |
| `/analises/buy-signals` | `/api/buy-signals/watchlist-top` | `valor_justo` ≠ `preco_teto_usuario` |
| `/ativos/<TICKER>` | buy-score | Margem usa valor calculado |
| `/ferramentas/cotacoes` | `/api/cotacoes/health` | KPIs vs TTL 15min |

**E2E previsto:** `tests/e2e/21-valuation-pipeline.spec.ts`

---

## Critérios de certificação (definição de pronto)

1. Tickers golden com cotação `idade ≤ 15min` após refresh; testes TTL verdes
2. `parametros_macro` BR/US populado; dashboard sem fallback env
3. ≥252 dias de histórico para tickers de Z-Score e benchmarks
4. 12 golden tickers dentro de faixas documentadas; 26+ testes unitários mantidos
5. UI preço-teto, buy-signals e detalhe exibem mesmo `valor_justo` da API
6. `API_REFERENCE.md` documenta `GET /api/calculos/preco_teto/{ticker}`

---

## Ordem de implementação

| # | Tarefa | Esforço |
|---|--------|---------|
| 1 | Este documento + GAP ROADMAP | ✅ |
| 2 | `test_cotacoes_ttl.py` + decisão batch TTL | 1 sessão |
| 3 | `test_historico_service.py` + cascade mocks | 1 sessão |
| 4 | Estender `test_indicadores_dashboard.py` | 0,5 sessão |
| 5 | `valuation_golden.json` + `test_valuation_golden.py` | 1–2 sessões |
| 6 | Runbook manual 12 tickers | 0,5 sessão |
| 7 | E2E valuation smoke | 0,5 sessão |
| 8 | Resolver V-GAP-01..07 | variável |

**Estimativa:** 4–6 sessões + 1 validação manual.

---

## Relação com outros GAPs

| GAP | Relação |
|-----|---------|
| `SEED-MENU-001` | Massa `test_menu_full` deve ter eps/fcf/ffo para validação conjunta |
| `VALUATION-003` (futuro) | Sync fundamentals yfinance — fora do escopo v1 |
| `BUG-VAL-001..006` | Fórmulas já corrigidas; este plano valida pipeline de entrada |

---

## Histórico

| Data | Versão | Nota |
|------|--------|------|
| 01/07/2026 | 1.0 | Plano documentado; implementação pendente |
