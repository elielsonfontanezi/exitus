# Plano de Massa de Dados — Menu Principal (test_menu_full)

**Data:** 01/07/2026  
**GAP:** `SEED-MENU-001`  
**Status:** 🟡 Implementado — walkthrough API 36/36 OK; aguarda OK manual do usuário  
**Relacionado:** [`AUDITORIA_FUNCIONAL.md`](AUDITORIA_FUNCIONAL.md) § Go-Live, [`SEEDS.md`](SEEDS.md), [`ROADMAP.md`](ROADMAP.md), [`PLANO_VALIDACAO_VALOR_JUSTO.md`](PLANO_VALIDACAO_VALOR_JUSTO.md)

---

## Objetivo

Criar cenário **`test_menu_full`** que garanta dados realistas e não-vazios para **todas as 43 telas** do menu principal, cobrindo:

- Ativos **BR / US / INTL** (15 tipos de `TipoAtivo`)
- Fluxo **aporte → compra → provento → venda → DARF → resgate**
- IR, reconciliação, análises (risco, correlação, alocação) e configurações admin

**Gate Go-Live (Trilha A):** bloqueado até validação manual do usuário com `test_menu_full` carregado. Ver critério em [`AUDITORIA_FUNCIONAL.md`](AUDITORIA_FUNCIONAL.md).

---

## Diagnóstico — estado atual (01/07/2026)

### Cenários existentes

| Cenário | Uso | Limitação para menu 100% |
|---------|-----|--------------------------|
| `test_full` | Pytest, IR, RV/RF | Sem CRIPTO, LCI_LCA, BOND, ETF BR; sem `calendario_dividendo`, `projecoes_renda`, `regras_fiscais` |
| `test_e2e` | E2E leve | Poucos ativos/transações; tem blocos auxiliares que `test_full` não tem |
| `test_ir` | IR especializado | Escopo fiscal apenas |
| `test_stress` | Volume | Não orientado a telas |

### `load_scenario.py` — entidades suportadas vs gaps

**Suportadas (16):** assessoras, usuarios, ativos, corretoras, transacoes, proventos, movimentacoes_caixa, portfolios, alertas, planos_compra, planos_venda, historico_patrimonio, calendario_dividendo, projecoes_renda, regras_fiscais, eventos_corporativos.

**Não suportadas (5) — exigem extensão do loader:**

| Entidade JSON | Tela impactada |
|---------------|----------------|
| `fontes_dados` | `/configuracoes/fontes-dados` |
| `meta_alocacao` | `/analises/alocacao` (metas explícitas no seed) |
| `taxas_cambio` | `/carteira/cambio` |
| `historico_preco` | `/analises/correlacao`, `/analises/risco`, `/analises/evolucao` |
| `saldo_prejuizo` | `/ferramentas/calculadora-ir`, compensação IR |

### Cobertura `TipoAtivo` (15 valores)

| Tipo | `test_full` | COMPRA/VENDA |
|------|-------------|--------------|
| ACAO, FII, UNIT | ✅ | ✅ |
| CDB, TESOURO_DIRETO, DEBENTURE | ✅ | ✅ (RF) |
| STOCK, REIT, ETF (US) | ✅ | ✅ |
| STOCK_INTL, ETF_INTL | ✅ | ✅ |
| **LCI_LCA** | ❌ | — |
| **BOND** | ❌ | — |
| **CRIPTO** | ❌ | — |
| **ETF BR** (BOVA11) | ❌ | — (só `test_e2e`) |
| OUTRO | ❌ | — |

---

## Critérios de aceite do cenário `test_menu_full`

1. **15/15 `TipoAtivo`** com ≥1 ativo catalogado e ≥1 compra
2. **≥80%** dos tipos RV com venda (lucro e prejuízo onde aplicável)
3. Timeline **Jan/2024 – Mar/2026**: aportes alinhados a compras; DARF em meses críticos
4. **43/43 telas** com status seed `COBERTO` na matriz da auditoria
5. Script `verify_menu_seed.py` passa após `reset_and_seed.py --scenario test_menu_full`
6. Pytest baseline: **663 passed**, 0 failed (sem regressão)
7. **OK explícito do usuário** após walkthrough manual → libera Trilha A

---

## Catálogo de ativos proposto (~48–52)

| Mercado | Tipos | Exemplos |
|---------|-------|----------|
| BR RV | ACAO (6), FII (3), UNIT (1), ETF (2) | PETR4, HGLG11, TAEE11, BOVA11, SMAL11 |
| BR RF | CDB (3), LCI_LCA (2), TESOURO (3), DEB (2) | CDBNUBANK… + LCI XP, LCA Itaú |
| US RV | STOCK (5), REIT (2), ETF (2) | AAPL, O, VTI |
| US RF | BOND (2) | TLT, AGG |
| INTL | STOCK_INTL (6), ETF_INTL (2) | TSLA34, IVVB11 |
| Outros | CRIPTO (3) | BTC, ETH, SOL |

Base: expandir [`test_full.json`](../backend/seed_data/scenarios/test_full.json); incorporar blocos de [`test_e2e.json`](../backend/seed_data/scenarios/test_e2e.json) (calendário, projeções, regras).

---

## Narrativa financeira (`e2e_user`)

Três portfolios (já existentes em `test_full`, expandir):

1. **Aposentadoria** — mix BR + US + RF  
2. **Dividendos BR** — FIIs + ações pagadoras + proventos mensais  
3. **Growth US + Cripto** — stocks US + posição cripto pequena  

Por portfolio:

- 4–6 aportes BRL/USD (24 meses)
- 2–3 resgates (incl. `tipo: imposto` para DARF)
- 1 transferência XP → Inter (reconciliação)

---

## Blocos JSON do cenário

Além dos blocos atuais de `test_full`:

```json
{
  "calendario_dividendo": [],
  "projecoes_renda": [],
  "regras_fiscais": [],
  "meta_alocacao": [],
  "fontes_dados": [],
  "taxas_cambio": [],
  "historico_preco": [],
  "saldo_prejuizo": []
}
```

---

## Extensões `load_scenario.py`

Ordem de implementação:

1. `_seed_taxas_cambio` (antes de transações USD)
2. `_seed_meta_alocacao` (após portfolios)
3. `_seed_fontes_dados`
4. `_seed_historico_preco` (≥12 meses por ativo principal)
5. `_seed_saldo_prejuizo` (após transações)

Referência: [`EXITUS_DB_STRUCTURE.txt`](EXITUS_DB_STRUCTURE.txt), MCP Postgres.

---

## Validação em 3 camadas

| Camada | Artefato | Meta |
|--------|----------|------|
| Integridade seed | `backend/tests/test_scenario_loader.py` | FKs, 15 tipos, blocos obrigatórios |
| Regressão API | pytest (`663 passed` baseline) | 0 novas falhas |
| E2E menu | `tests/e2e/` v4 | 43 telas com dados não-vazios |

```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_menu_full
podman exec exitus-backend python scripts/verify_menu_seed.py
```

---

## Ordem de implementação

| Fase | Entrega | Esforço |
|------|---------|---------|
| 1 | Este documento + matriz na auditoria | ✅ |
| 2 | Extensão `load_scenario.py` (5 `_seed_*`) | 1 sessão |
| 3 | `test_menu_full.json` incremental | 2–3 sessões |
| 4 | `verify_menu_seed.py` + testes loader | 0,5 sessão |
| 5 | E2E v4 alinhado | 2 sessões |
| 6 | Validação manual usuário | contínuo — **pendente** |

---

## Walkthrough API (02/07/2026)

Após `reset_and_seed.py --clean --scenario test_menu_full` e `scripts/walkthrough_menu_api.py`:

| Resultado | Valor |
|-----------|-------|
| Checks API | 36 |
| Erros | 0 |
| Vazios | 0 |

**Nota:** smoke cobre endpoints principais das 43 telas; validação visual no browser permanece como gate Go-Live.

```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_menu_full
podman exec exitus-backend python scripts/verify_menu_seed.py
podman exec exitus-backend python scripts/walkthrough_menu_api.py
```

---

## Walkthrough browser + checklist usuário (02/07/2026)

Script: `backend/scripts/walkthrough_menu_browser.py` (sessão Flask + validação API por tela).

**Checklist:** [`WALKTHROUGH_CHECKLIST_USUARIO.md`](WALKTHROUGH_CHECKLIST_USUARIO.md)

| Tier | Qtd | Ação sua |
|------|-----|----------|
| OBRIGATÓRIO | 16 | Abrir todas (CRUD, forms, export, admin) |
| RECOMENDADO | 7 | Gráficos/KPIs — confirmar visual |
| AMOSTRA | 19 | Escolher 5–8 listas read-only |
| PODE PULAR | 3 | Login + redirects (já OK) |

```bash
cd backend && python3 scripts/walkthrough_menu_browser.py
```

---

## Matriz resumida — telas com gap em `test_full`

| # | Tela | Seed `test_full` | Ação em `test_menu_full` |
|---|------|------------------|--------------------------|
| — | `/proventos/calendario` | PARCIAL | `calendario_dividendo` |
| — | `/analises/projecoes/renda` | FALTANDO | `projecoes_renda` |
| — | `/configuracoes/regras-fiscais` | FALTANDO | `regras_fiscais` |
| — | `/configuracoes/fontes-dados` | FALTANDO | `fontes_dados` + loader |
| — | `/carteira/cambio` | PARCIAL | `taxas_cambio` |
| — | Catálogo cripto | FALTANDO | ativos CRIPTO + transações |
| — | ETFs Brasil | FALTANDO | BOVA11, SMAL11 + compras |

Demais telas: **COBERTO** ou **PARCIAL** com `test_full` (detalhe na auditoria).

---

## Histórico

| Data | Versão | Nota |
|------|--------|------|
| 02/07/2026 | 1.1 | Cenário `test_menu_full` implementado; walkthrough API 36/36 |
| 01/07/2026 | 1.0 | Plano documentado; implementação pendente |
