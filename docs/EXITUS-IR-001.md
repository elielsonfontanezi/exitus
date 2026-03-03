# EXITUS-IR-001 — Engine de Cálculo de IR sobre Renda Variável

> **Status:** ✅ Concluído (03/03/2026)  
> **Versão:** 1.0  
> **Branch:** `feature/revisao-negocio-vision`  
> **Testes:** 19 testes de integração — 100% passou

---

## 1. Objetivo

Implementar engine completa de apuração mensal de Imposto de Renda (IR) sobre operações de renda variável, cobrindo as regras fiscais vigentes no Brasil para o ano-calendário 2024+. O sistema calcula IR devido por categoria de ativo, aplica isenções, e gera dados para preenchimento do DARF.

---

## 2. Escopo Implementado

### 2.1 Categorias de ativos e alíquotas

| Categoria | Tipos de Ativo | Alíquota | Isenção Mensal | Código DARF |
|-----------|---------------|----------|----------------|-------------|
| Swing trade ações BR | `ACAO` | 15% | R$ 20.000 em vendas | 6015 |
| Day-trade (qualquer tipo) | Todos | 20% | Sem isenção | 6015 |
| FIIs | `FII` | 20% | Sem isenção | 6015 |
| Renda variável exterior | `STOCK`, `REIT`, `ETF`, `BOND` | 15% | Sem isenção | 0561 |

### 2.2 Regras de isenção

- **Swing trade ações BR:** isento quando vendas totais do mês ≤ R$ 20.000. Aplica-se apenas ao tipo `ACAO` (ações brasileiras). FIIs, ETFs e ativos US **não** fazem parte deste limite.
- **DARF mínimo:** valor abaixo de R$ 10,00 não é recolhido — deve acumular para o mês seguinte.

### 2.3 Detecção de day-trade

Venda é classificada como day-trade quando existe uma compra do **mesmo ativo** (`ativo_id`) no **mesmo dia calendário** (`data_transacao.date()`). A classificação ocorre antes da separação por categoria.

### 2.4 Cálculo de lucro

O lucro por venda é calculado como:

```
lucro_bruto  = valor_total_venda − (preco_unitario_venda × quantidade)
lucro_liquido = lucro_bruto − custos_totais
```

> **Nota:** O `preco_unitario` da transação de venda é usado como proxy do custo de aquisição. Esta é uma simplificação — veja [Limitações](#6-limitações-e-gaps-derivados).

### 2.5 Breakdown por corretora

Cada resposta de apuração inclui `por_corretora`: lista com `corretora_id`, `corretora_nome`, `total_vendas` e `operacoes`. Útil para preencher a DIRPF anualmente.

---

## 3. Arquitetura

### 3.1 Arquivos

| Arquivo | Responsabilidade |
|---------|-----------------|
| `backend/app/services/ir_service.py` | Engine de cálculo — toda a lógica fiscal |
| `backend/app/blueprints/ir_blueprint.py` | 3 endpoints REST em `/api/ir/` |
| `backend/tests/test_ir_integration.py` | Suite de 19 testes de integração |

### 3.2 Diagrama de fluxo — `apurar_mes()`

```
apurar_mes(usuario_id, "YYYY-MM")
│
├── 1. Busca transações (COMPRA + VENDA) do período
│       JOIN Ativo + Corretora
│
├── 2. Classifica cada VENDA em categoria:
│       ├── is_day_trade? → day_trade[]
│       ├── tipo in TIPOS_FII? → fiis[]
│       ├── tipo in TIPOS_US? → exterior[]
│       └── default → swing_acoes[]
│
├── 3. Apura cada categoria:
│       ├── _apurar_swing_acoes()  → isenção R$20k
│       ├── _apurar_day_trade()    → 20%, sem isenção
│       ├── _apurar_fiis()         → 20%, sem isenção
│       └── _apurar_exterior()     → 15%, sem isenção
│
├── 4. Gera DARF:
│       ├── IR BR (swing + day-trade + FIIs) → código 6015
│       └── IR exterior                       → código 0561
│
└── 5. Retorna dict com categorias, por_corretora, ir_total, darf, alertas
```

### 3.3 Constantes fiscais (`ir_service.py`)

```python
ISENCAO_SWING_ACAO = Decimal('20000.00')   # Isenção mensal vendas ações swing
ALIQUOTA_SWING_ACAO = Decimal('0.15')      # 15%
ALIQUOTA_DAY_TRADE  = Decimal('0.20')      # 20%
ALIQUOTA_FII        = Decimal('0.20')      # 20%
ALIQUOTA_REIT       = Decimal('0.15')      # 15% (ETF/REIT US — simplificado)
ALIQUOTA_STOCK_US   = Decimal('0.15')      # 15% ganho capital US
DARF_MINIMO         = Decimal('10.00')     # Mínimo para recolhimento
```

---

## 4. API Reference

### 4.1 `GET /api/ir/apuracao?mes=YYYY-MM`

Apuração detalhada por categoria para o mês informado.

**Parâmetros:**

| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `mes` | string | ✅ | Mês no formato `YYYY-MM` (ex: `2025-03`) |

**Resposta 200:**

```json
{
  "success": true,
  "message": "Apuração de IR — 2025-03",
  "data": {
    "mes": "2025-03",
    "usuario_id": "uuid",
    "categorias": {
      "swing_acoes": {
        "total_vendas": 5000.00,
        "lucro_liquido": 2000.00,
        "aliquota": 15.0,
        "isento": true,
        "ir_devido": 0.0,
        "operacoes": 1
      },
      "day_trade": {
        "lucro_liquido": 0.0,
        "aliquota": 20.0,
        "isento": false,
        "ir_devido": 0.0,
        "operacoes": 0
      },
      "fiis": { "lucro_liquido": 0.0, "aliquota": 20.0, "isento": false, "ir_devido": 0.0, "operacoes": 0 },
      "exterior": { "lucro_liquido": 0.0, "aliquota": 15.0, "isento": false, "ir_devido": 0.0, "operacoes": 0 }
    },
    "por_corretora": [
      {
        "corretora_id": "uuid",
        "corretora_nome": "XP Investimentos",
        "total_vendas": 5000.00,
        "operacoes": 1
      }
    ],
    "ir_total": 0.0,
    "darf": [],
    "alertas": [
      "Vendas de ações em 2025-03 abaixo de R$20.000 — isento de IR (swing trade)."
    ]
  }
}
```

**Erros:**

| HTTP | Situação |
|------|----------|
| 400 | Parâmetro `mes` ausente |
| 401 | Token JWT ausente ou inválido |
| 422 | Formato inválido (ex: `03-2025`, `2025-13`) |

---

### 4.2 `GET /api/ir/darf?mes=YYYY-MM`

DARFs a pagar no mês informado.

**Parâmetros:** igual ao `/apuracao`

**Resposta 200:**

```json
{
  "success": true,
  "data": {
    "mes": "2025-03",
    "darfs": [
      {
        "codigo_receita": "6015",
        "descricao": "Ganho de capital — renda variável BR (ações, FIIs, day-trade)",
        "valor": 450.00,
        "pagar": true,
        "obs": null
      }
    ],
    "ir_total": 450.00,
    "alertas": []
  }
}
```

> Quando `pagar: false`, o campo `obs` explica o motivo (ex: abaixo do mínimo de R$10,00).

---

### 4.3 `GET /api/ir/historico?ano=YYYY`

Resumo de apuração mês a mês para o ano inteiro. Retorna sempre **12 entradas**.

**Parâmetros:**

| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `ano` | integer | ✅ | Ano calendário (ex: `2025`). Intervalo válido: 2000–2100. |

**Resposta 200:**

```json
{
  "success": true,
  "data": {
    "ano": 2025,
    "meses": [
      { "mes": "2025-01", "ir_total": 0.0, "alertas": [], "operacoes": 0 },
      { "mes": "2025-02", "ir_total": 320.50, "alertas": [], "operacoes": 3 },
      ...
      { "mes": "2025-12", "ir_total": 0.0, "alertas": [], "operacoes": 0 }
    ]
  }
}
```

**Erros:**

| HTTP | Situação |
|------|----------|
| 400 | Parâmetro `ano` ausente ou não numérico ou fora do intervalo |
| 401 | Token JWT ausente ou inválido |

---

## 5. Testes

Suite em `backend/tests/test_ir_integration.py` — 19 testes, 100% passou.

| Classe | Testes | O que cobre |
|--------|--------|-------------|
| `TestApuracao` | 9 | 401 sem token, 400 sem parâmetro, 422 formato inválido, mês vazio, 4 categorias na estrutura, isenção R$20k, campo `mes`, `por_corretora` |
| `TestDarf` | 5 | 401 sem token, 400 sem parâmetro, mês sem lucro → lista vazia, campo `mes`, envelope padrão |
| `TestHistorico` | 6 | 401 sem token, 400 sem parâmetro, ano não numérico, 12 meses, campos obrigatórios, formato `YYYY-MM` |

**Fixture `cenario_ir`:** cria corretora + compra 100×R$30 + venda 100×R$50 em 2025-03. Total vendas = R$5.000 → abaixo de R$20k → swing isento.

---

## 6. Limitações e GAPs Derivados

As limitações abaixo foram identificadas durante a implementação e **são escopo de GAPs futuros** registrados no ROADMAP.md.

### 6.1 EXITUS-IR-002 — Custo Médio Histórico (PM Acumulado)

**Limitação atual:** O lucro é calculado usando `preco_unitario` da transação de venda como proxy do custo de aquisição. Isso é **impreciso** — o custo real depende do preço médio ponderado acumulado de todas as compras anteriores ao mês de apuração.

**Correto seria:** buscar o PM acumulado da tabela `posicao` (campo `preco_medio`) para o ativo na data imediatamente anterior à venda.

**Impacto:** IR calculado pode divergir do real, subestimando ou superestimando lucro.

---

### 6.2 EXITUS-IR-003 — Compensação de Prejuízo Acumulado entre Meses

**Limitação atual:** Prejuízos de um mês não são persistidos e compensados automaticamente em meses seguintes. A lógica de aplicar compensação existe nos métodos de apuração, mas não há tabela `saldo_prejuizo` para persistir o acumulado.

**Regra fiscal (IN RFB 1.585/2015):** Prejuízos de swing trade compensam apenas lucros de swing trade futuros. Prejuízos de day-trade compensam apenas day-trade. A compensação não expira.

**Impacto:** IR calculado pode ser maior que o real quando há prejuízos acumulados de meses anteriores.

---

### 6.3 EXITUS-IR-004 — Proventos Tributáveis (JCP e Withholding Tax US)

**Limitação atual:** O engine não processa proventos. JCP (Juros sobre Capital Próprio) tem 15% retidos na fonte — o sistema não registra nem consolida esses valores no resumo fiscal mensal. Dividendos de ações US têm withholding tax de 30% (treaty BR-US pode reduzir para 15%/25%) que não é calculado.

**Escopo necessário:**
- JCP: buscar tabela `provento` onde `tipo = 'JCP'` e consolidar IR retido na fonte
- Dividendos US: withholding tax 30% sobre `valor_liquido` de proventos de ativos `TIPOS_US`
- Integrar resumo de IR sobre proventos na resposta de `/api/ir/apuracao`

---

### 6.4 EXITUS-IR-005 — Renda Fixa (Tabela Regressiva de IR)

**Limitação atual:** Ativos de renda fixa (`CDB`, `LCI_LCA`, `TESOURO_DIRETO`, `DEBENTURE`) não são calculados no engine de IR. A tabela regressiva vigente no Brasil é:

| Prazo da aplicação | Alíquota IR |
|--------------------|-------------|
| Até 180 dias | 22,5% |
| 181 a 360 dias | 20,0% |
| 361 a 720 dias | 17,5% |
| Acima de 720 dias | 15,0% |

LCI/LCA: isentas de IR para pessoa física.

**Escopo necessário:** calcular IR retido na fonte para resgates de RF, integrando com `data_vencimento` e `data_compra` dos ativos de renda fixa.

> **Nota:** Este item está parcialmente coberto pelo GAP `EXITUS-RFCALC-001` (Fase 4), que trata cálculos avançados de RF.

---

### 6.5 EXITUS-IR-006 — IRPF Anual: Declaração e Bens e Direitos

**Limitação atual:** O sistema produz dados para recolhimento mensal via DARF, mas não gera o relatório estruturado para preenchimento da Declaração de Ajuste Anual (DIRPF) — especificamente as fichas "Renda Variável" e "Bens e Direitos".

**Escopo necessário:**
- Relatório anual consolidado por ativo com custo de aquisição e situação final
- Exportação no formato adequado para preenchimento manual ou importação no programa IRPF da RFB
- Integrar com `EXITUS-EXPORT-001` para geração de PDF/Excel

---

### 6.7 EXITUS-IR-008 — Tratamento Fiscal de UNITs B3

**Limitação atual:** O enum `TipoAtivo` (14 tipos) não inclui `UNIT`. UNITs (ex: `TAEE11`, `KLBN11`, `SANB11`) são certificados de depósito compostos por ações ON + PN. Se uma UNIT entrar no sistema hoje, cai no branch `default` de `apurar_mes()` e é tratada como `swing_acoes` — o que **por acaso** é fiscalmente correto (UNITs são equiparadas a ações: 15% swing, 20% day-trade, isenção R$20k, DARF 6015), mas sem garantia estrutural.

**Problema real:** O desmembramento de UNIT em ações ON + PN exige rateio proporcional do preço médio. Sem esse rateio, o custo de aquisição das ações resultantes fica zerado, gerando IR inflado na venda.

**Recomendação:** Prioridade **baixa**. Funciona acidentalmente hoje. Depende fortemente de `EXITUS-UNITS-001` (Fase 4) — implementar junto, não antes.

---

## 7. Tabelas do banco utilizadas

| Tabela | Uso |
|--------|-----|
| `transacao` | Fonte das operações (COMPRA/VENDA) do período |
| `ativo` | Tipo do ativo (para classificação de categoria) |
| `corretora` | Nome da corretora para breakdown por corretora |
| `posicao` | **Não utilizada** (ver EXITUS-IR-002 — custo médio) |
| `regra_fiscal` | **Não utilizada** (constantes hardcoded no service) |
| `provento` | **Não utilizada** (ver EXITUS-IR-004) |

> A tabela `regra_fiscal` existe no banco mas as alíquotas estão hardcoded no `ir_service.py`. O GAP `EXITUS-IR-007` rastreia a integração dinâmica com essa tabela.

---

## 8. Decisões de design

### 8.1 Por que `Decimal` em vez de `float`?

Todos os valores monetários usam `decimal.Decimal` com `ROUND_HALF_UP`. Float tem erros de representação binária (ex: `0.1 + 0.2 ≠ 0.3`) que são inaceitáveis em cálculos fiscais.

### 8.2 Por que DARF exterior usa código `0561`?

O código `0561` é o DARF para "Ganhos de Capital — Alienação de Bens e Direitos no Exterior" (IN RFB 1.627/2016). O código `6015` é exclusivo para renda variável doméstica.

### 8.3 Por que `historico_anual` sempre retorna 12 meses?

Garante contrato fixo de API — o frontend pode mapear diretamente os 12 índices sem lógica condicional. Meses sem operações retornam `ir_total: 0.0`.

### 8.4 Detecção de day-trade por `ativo_id` vs `ticker`

A detecção usa `ativo_id` (UUID) e não `ticker` para evitar falsos positivos em casos de UNITS vs ações base que compartilham ticker similar. Isso também é mais performático (índice direto).

---

## 9. Exemplos de uso (cURL)

```bash
# Obter token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "joao.silva", "password": "senha123"}' \
  | jq -r '.data.access_token')

# Apuração de março/2025
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/ir/apuracao?mes=2025-03" | jq '.'

# DARFs de março/2025
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/ir/darf?mes=2025-03" | jq '.data.darfs'

# Histórico anual 2025
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/ir/historico?ano=2025" | jq '.data.meses[] | select(.ir_total > 0)'
```

---

## 10. Histórico de revisões

| Data | Versão | Alteração |
|------|--------|-----------|
| 03/03/2026 | 1.0 | Implementação inicial — engine, 3 endpoints, 19 testes |

---

*Próximos passos: EXITUS-IR-002 (custo médio histórico), EXITUS-IR-003 (compensação prejuízo), EXITUS-IR-004 (JCP/withholding), EXITUS-IR-005 (RF tabela regressiva), EXITUS-IR-006 (DIRPF anual), EXITUS-IR-007 (alíquotas dinâmicas via `regra_fiscal`).*
