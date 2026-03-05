# EXITUS-IR-009 — Atualização de Regras Fiscais 2026 (Lei 15.270/2025)

> **⚠️ DOCUMENTO CONSOLIDADO em `EXITUS-IR-001.md` (Seção 9) — versão 2.0, 05/03/2026**  
> O conteúdo abaixo é mantido para referência histórica. A fonte de verdade é `EXITUS-IR-001.md`.

> **Status:** ✅ Concluído (04/03/2026)  
> **Prioridade:** Alta  
> **Impacto:** Alto  
> **Dependências:** EXITUS-IR-007 ✅, EXITUS-IR-004 ✅  
> **Base legal:** Lei 15.270/2025 (sancionada 26/11/2025), PLP 128/2025 (JCP), vigência 01/01/2026  
> **Testes:** 3 testes de integração (`TestRegrasFiscais2026`) — 100% passou  
> **Suite total:** 146 passed, 0 failed

---

## 1. Objetivo

Atualizar o engine de IR do Exitus para refletir as mudanças tributárias vigentes a partir de 01/01/2026, conforme a **Lei 15.270/2025** e legislação complementar. As regras atuais no sistema refletem a legislação pré-2026 e precisam ser atualizadas.

---

## 2. Mudanças Legislativas

### 2.1 JCP — Juros sobre Capital Próprio

| Item | Regra anterior | Regra 2026+ |
|------|---------------|-------------|
| **Alíquota IRRF** | 15% | **17,5%** |
| **Base de cálculo** | Lucros acumulados (sem restrição) | Apenas lucros acumulados de **anos anteriores** |
| **Código DARF** | 9453 | 9453 (mantido) |
| **Retenção** | Na fonte, pela empresa | Na fonte, pela empresa (mantido) |

**Fonte:** PLP 128/2025, sancionado em 26/12/2025.

**Regra de transição:** JCP deliberado e creditado até 31/12/2025 usa alíquota antiga (15%), mesmo que pago em 2026.

### 2.2 Dividendos Brasil

| Item | Regra anterior | Regra 2026+ |
|------|---------------|-------------|
| **Isenção** | Total (Lei 9.249/1995) | Limitada a **R$ 50.000/mês por fonte pagadora (CNPJ)** |
| **Alíquota acima da isenção** | — | **10% IRRF** sobre o **valor total** distribuído no mês |
| **Base de cálculo** | — | Se exceder R$50k no mês por CNPJ, todo o valor é tributado em 10% |
| **Crédito IRRF** | — | Valor retido entra como crédito na DIRPF anual |
| **Código DARF** | — | 9453 |

**Fonte:** Lei 15.270/2025, art. 6º-A.

**Regra de transição:** Lucros apurados até ano-calendário 2025, cuja distribuição foi aprovada até 31/12/2025, permanecem isentos mesmo se pagos em 2026+.

**Impacto no sistema:**
- O modelo atual não diferencia dividendos por fonte pagadora (CNPJ)
- Será necessário agrupar dividendos por `corretora_id` + `ativo_id` (proxy do CNPJ) para aplicar o limite de R$50k
- Nova lógica: se soma de dividendos de uma mesma empresa > R$50k/mês → 10% IRRF sobre **todo** o valor

### 2.3 Imposto Mínimo Anual (Renda Global)

| Item | Detalhe |
|------|---------|
| **Quem é atingido** | Contribuintes com renda anual > **R$ 600.000** |
| **Alíquota** | Progressiva: 0% a **10%** (máximo para renda > R$1,2M/ano) |
| **Base** | Soma de todos os rendimentos: salários, pró-labore, aluguéis, juros, dividendos (mesmo isentos), ganhos em bolsa |
| **Créditos** | IR já pago no ano (retenção na fonte, carnê-leão, IRRF sobre dividendos, etc.) é abatido |
| **Vigência** | Declaração a partir de abril/2027 (referente a 2026) |

**Impacto no sistema:** Este é escopo de **EXITUS-IR-006** (DIRPF anual). O engine mensal deve registrar todos os valores para consolidação anual.

### 2.4 Investimentos no Exterior (EUA)

| Item | Regra 2026+ |
|------|-------------|
| **Retenção IRS (EUA)** | 30% na fonte (inalterado) |
| **Alíquota BR** | **15%** fixa sobre rendimentos no exterior |
| **Crédito tributário** | 30% retido nos EUA > 15% devido no BR → sem DARF adicional |
| **Obrigação** | Declaração detalhada obrigatória para evitar bitributação |

**Impacto no sistema:** A lógica de ganho de capital US (15%) permanece inalterada. O que muda é o tratamento de **dividendos US** — o withholding de 30% gera crédito, não DARF.

### 2.5 Aluguel de Ações

| Item | Regra 2026+ |
|------|-------------|
| **Alíquota** | Tabela regressiva de Renda Fixa: **22,5% a 15%** conforme prazo |
| **Retenção** | Automática pela corretora |
| **Código DARF** | 0561 |

| Prazo de aplicação | Alíquota |
|---|---|
| Até 180 dias | 22,5% |
| 181 a 360 dias | 20,0% |
| 361 a 720 dias | 17,5% |
| Acima de 720 dias | 15,0% |

---

## 3. Impacto no Sistema Exitus

### 3.1 Tabela `regra_fiscal` — Novas regras a inserir

| `pais` | `tipo_ativo` | `tipo_operacao` | `aliquota_ir` | `valor_isencao` | Vigência início | Descrição |
|--------|-------------|----------------|--------------|----------------|----------------|-----------|
| BR | NULL | JCP | 17.5000 | NULL | 2026-01-01 | JCP 17,5% IRRF (PLP 128/2025) |
| BR | NULL | DIVIDENDO | 0.0000 | 50000.00 | 2026-01-01 | Dividendos BR: isenção R$50k/mês por CNPJ |
| BR | NULL | DIVIDENDO_TRIBUTADO | 10.0000 | NULL | 2026-01-01 | Dividendos BR acima de R$50k: 10% IRRF |

### 3.2 Regras anteriores a expirar

As seguintes regras pré-2026 devem ter `vigencia_fim = '2025-12-31'`:

| Regra atual | Ação |
|---|---|
| JCP 15% (se for inserida por IR-004) | Setar `vigencia_fim = 2025-12-31` |

### 3.3 Mudanças estruturais necessárias

| Componente | Mudança |
|---|---|
| `ir_service.py` | Novo método `_apurar_proventos()` — agrupa por fonte pagadora, aplica limite R$50k (depende IR-004) |
| `regra_fiscal` seed | Inserir regras 2026 + expirar regras pré-2026 |
| `_carregar_regras_fiscais()` | Já suporta vigência por data (IR-007) — sem mudança |
| Resposta da API | Seção `proventos` com breakdown: JCP, dividendos isentos, dividendos tributados, aluguel |

### 3.4 Campos necessários (análise)

Para aplicar o limite de R$50k por CNPJ, o sistema precisa:
- Agrupar transações `DIVIDENDO` por `ativo_id` (cada ativo = uma empresa/CNPJ)
- Somar dividendos do mês por ativo
- Se soma > R$50k → tributar **todo** o valor em 10%
- Se soma ≤ R$50k → isento

**Nota:** O campo `ativo_id` já existe na `transacao` e serve como proxy do CNPJ da fonte pagadora.

---

## 4. Pré-requisitos

| GAP | Motivo |
|-----|--------|
| **EXITUS-IR-004** | Implementa proventos no engine (JCP, dividendos, aluguel) — base para aplicar regras 2026 |
| **EXITUS-IR-007** | ✅ Já concluído — alíquotas dinâmicas via `regra_fiscal` com vigência |

---

## 5. Plano de Implementação

1. **Concluir IR-004** — proventos tributáveis com regras pré-2026 (baseline)
2. **Seed regras 2026** — INSERT na `regra_fiscal` com vigência 2026-01-01
3. **Expirar regras pré-2026** — SET `vigencia_fim = 2025-12-31` onde aplicável
4. **Lógica de dividendos por CNPJ** — agrupamento por `ativo_id`, limite R$50k
5. **Testes** — cenários com valores acima/abaixo do limite, JCP 17.5%
6. **Docs** — EXITUS-IR-001.md, ROADMAP, CHANGELOG, ARCHITECTURE

---

## 6. Referências Legais

| Lei/PLP | Assunto | Link |
|---------|---------|------|
| Lei 15.270/2025 | Tributação de dividendos + imposto mínimo | [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15270.htm) |
| PLP 128/2025 | JCP 17,5% | [investidor10.com.br](https://investidor10.com.br/noticias/lula-sanciona-lei-que-eleva-para-17-5-a-taxacao-de-jcp-117645/) |
| Lei 9.249/1995 | Isenção de dividendos (revogada parcialmente) | — |
| IN RFB 1.585/2015 | Day-trade e operações em bolsa | — |

---

## 7. Tabela Resumo — Regras Fiscais Vigentes 2026

| Tipo | País | Alíquota | Isenção | DARF | Retenção |
|------|------|----------|---------|------|----------|
| Swing trade ações | BR | 15% | R$20k/mês em vendas | 6015 | Contribuinte recolhe |
| Day-trade | BR | 20% | — | 6015 | Contribuinte recolhe |
| FIIs (venda cotas) | BR | 20% | — | 6015 | Contribuinte recolhe |
| **JCP** | BR | **17,5%** | — | 9453 | **Na fonte (empresa)** |
| **Dividendo BR** | BR | **0% ou 10%** | **R$50k/mês por CNPJ** | 9453 | **Na fonte (empresa)** |
| Dividendo US | US | 15% (BR) | — | — | 30% retido IRS (crédito) |
| Aluguel ações | BR | 15% a 22,5% | — | 0561 | Na fonte (corretora) |
| Ganho capital US | US | 15% | — | — | Contribuinte declara |

---

---

## 8. Implementação

### 8.1 Seed realizado

As seguintes regras foram inseridas em `exitusdb` e `exitusdb_test` com `vigencia_inicio = 2026-01-01`:

| `tipo_operacao` | `aliquota_ir` | `valor_isencao` | Descrição |
|---|---|---|---|
| JCP | 17,5% | NULL | PLP 128/2025 |
| DIVIDENDO | 0% | R\$50.000 | Lei 15.270/2025 — isenção até R\$50k por fonte |
| DIVIDENDO_TRIBUTADO | 10% | NULL | Lei 15.270/2025 — acima de R\$50k |

As regras pré-2026 (JCP 15%, DIVIDENDO BR 0% irrestrito) já tinham `vigencia_fim = 2025-12-31` e são ignoradas automaticamente pelo `_carregar_regras_fiscais(data_ref)` para meses de 2026+.

### 8.2 Lógica implementada em `_apurar_proventos()`

- **JCP:** aliquota resolvida dinamicamente pela data do mês — 15% até dez/2025, 17,5% a partir de jan/2026
- **Dividendos BR (2026+):** agrupa por `ativo_id` (proxy CNPJ); se valor do ativo > R\$50k no mês → aplica 10% sobre **todo** o valor; caso contrário, isento
- Resposta inclui campos `limite_isencao_por_cnpj` e `regime` (`'2026+'` ou `'pré-2026'`)

### 8.3 Testes (`TestRegrasFiscais2026`)

| Teste | Cenário | Verificação |
|---|---|---|
| `test_jcp_aliquota_17_5_em_2026` | JCP R\$1k em 2026-03 | alíquota=17.5, ir_retido=175 |
| `test_dividendo_br_tributado_acima_50k_em_2026` | Dividendo R\$60k em 2026-03 | isento=False, ir_esperado=6000, regime='2026+' |
| `test_dividendo_br_isento_abaixo_50k_em_2026` | Dividendo R\$30k em 2026-03 | isento=True, ir_esperado=0 |

*Concluído em 04/03/2026.*
