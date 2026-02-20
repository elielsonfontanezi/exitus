# Sistema Exitus - Documentação de ENUMs

**Versão:** 0.7.9
**Data:** 19/02/2026
**Status:** ✅ Produção

---

## ⚠️ Nota Importante — Comportamento dos ENUMs na API

> **GAP EXITUS-ENUMS-001 (documentado em v0.7.9)**
>
> Existe uma divergência entre a forma como os ENUMs são usados como **query param** vs como são **retornados** na resposta JSON:
>
> | Contexto | Formato | Exemplo |
> |----------|---------|---------|
> | **Query param** (filtro) | UPPERCASE | `?tipo=TESOURO_DIRETO` |
> | **Resposta JSON** (`tipo` field) | lowercase snake_case | `"tipo": "tesouro_direto"` |
> | **Banco de dados** (PostgreSQL) | lowercase sem underscore | `tesourodireto` |
> | **Python/SQLAlchemy** (Enum name) | UPPERCASE | `TipoAtivo.TESOURO_DIRETO` |
>
> **Tabela completa de mapeamento:**
>
> | Enum Python | Query Param | Resposta JSON | Banco (PostgreSQL) |
> |-------------|-------------|---------------|--------------------|
> | `ACAO` | `?tipo=ACAO` | `"acao"` | `acao` |
> | `FII` | `?tipo=FII` | `"fii"` | `fii` |
> | `CDB` | `?tipo=CDB` | `"cdb"` | `cdb` |
> | `LCI_LCA` | `?tipo=LCI_LCA` | `"lci_lca"` | `lcilca` |
> | `TESOURO_DIRETO` | `?tipo=TESOURO_DIRETO` | `"tesouro_direto"` | `tesourodireto` |
> | `DEBENTURE` | `?tipo=DEBENTURE` | `"debenture"` | `debenture` |
> | `STOCK` | `?tipo=STOCK` | `"stock"` | `stock` |
> | `REIT` | `?tipo=REIT` | `"reit"` | `reit` |
> | `BOND` | `?tipo=BOND` | `"bond"` | `bond` |
> | `ETF` | `?tipo=ETF` | `"etf"` | `etf` |
> | `STOCK_INTL` | `?tipo=STOCK_INTL` | `"stock_intl"` | `stockintl` |
> | `ETF_INTL` | `?tipo=ETF_INTL` | `"etf_intl"` | `etfintl` |
> | `CRIPTO` | `?tipo=CRIPTO` | `"cripto"` | `cripto` |
> | `OUTRO` | `?tipo=OUTRO` | `"outro"` | `outro` |
>
> **Origem da divergência:** O Python serializa `.value` do Enum (que é lowercase sem underscore para o banco), mas o blueprint normaliza para lowercase snake_case na resposta. O query param aceita case-insensitive via `upper()` no service.
>
> **Status:** Comportamento intencional (banco usa formato compacto sem `_`). Sem necessidade de migration.

---

## Visão Geral

Este documento descreve todos os ENUMs (enumerações) utilizados no Sistema Exitus, incluindo a **expansão para 14 tipos de ativos** implementada nas migrations `202602162111` e `202602162130`.

---

## 1. TipoAtivo (14 valores)

Enum principal para classificação de instrumentos financeiros com suporte multi-mercado.

### **1.1 Mercado BR (Brasil) - 6 tipos**

| Enum | Valor DB | Resposta JSON | Descrição | Classe Padrão | Moeda |
|------|----------|---------------|-----------|---------------|-------|
| `ACAO` | `acao` | `"acao"` | Ações negociadas na B3 | `RENDA_VARIAVEL` | BRL |
| `FII` | `fii` | `"fii"` | Fundos de Investimento Imobiliário | `RENDA_VARIAVEL` | BRL |
| `CDB` | `cdb` | `"cdb"` | Certificado de Depósito Bancário | `RENDA_FIXA` | BRL |
| `LCI_LCA` | `lcilca` | `"lci_lca"` | Letra de Crédito Imobiliário/Agrícola | `RENDA_FIXA` | BRL |
| `TESOURO_DIRETO` | `tesourodireto` | `"tesouro_direto"` | Títulos públicos federais | `RENDA_FIXA` | BRL |
| `DEBENTURE` | `debenture` | `"debenture"` | Debêntures corporativas | `RENDA_FIXA` | BRL |

**Exemplos de uso:**
- Filtro API: `GET /api/ativos?mercado=BR&tipo=TESOURO_DIRETO`
- Resposta JSON: `"tipo": "tesouro_direto"`
- psql: `WHERE tipo = 'tesourodireto'`

---

### **1.2 Mercado US (Estados Unidos) - 4 tipos**

| Enum | Valor DB | Resposta JSON | Descrição | Classe Padrão | Moeda |
|------|----------|---------------|-----------|---------------|-------|
| `STOCK` | `stock` | `"stock"` | Ações US (NYSE, NASDAQ) | `RENDA_VARIAVEL` | USD |
| `REIT` | `reit` | `"reit"` | Real Estate Investment Trust | `RENDA_VARIAVEL` | USD |
| `BOND` | `bond` | `"bond"` | Bonds corporativos/governamentais | `RENDA_FIXA` | USD |
| `ETF` | `etf` | `"etf"` | Exchange Traded Funds US | `RENDA_VARIAVEL` | USD |

---

### **1.3 Mercado INTL (Internacional) - 2 tipos**

| Enum | Valor DB | Resposta JSON | Descrição | Classe Padrão | Moeda |
|------|----------|---------------|-----------|---------------|-------|
| `STOCK_INTL` | `stockintl` | `"stock_intl"` | Ações Internacionais (EU, ASIA) | `RENDA_VARIAVEL` | EUR/GBP/JPY |
| `ETF_INTL` | `etfintl` | `"etf_intl"` | ETFs Internacionais | `RENDA_VARIAVEL` | EUR/USD |

---

### **1.4 Outros (2 tipos)**

| Enum | Valor DB | Resposta JSON | Descrição | Classe Padrão | Moeda |
|------|----------|---------------|-----------|---------------|-------|
| `CRIPTO` | `cripto` | `"cripto"` | Criptomoedas | `CRIPTO` | USD/BRL |
| `OUTRO` | `outro` | `"outro"` | Outros ativos não classificados | `HIBRIDO` | Variável |

---

## 2. ClasseAtivo (5 valores)

| Enum | Valor DB | Descrição | Tipos de Ativos Associados |
|------|----------|-----------|----------------------------|
| `RENDA_VARIAVEL` | `rendavariavel` | Renda Variável | ACAO, FII, STOCK, REIT, ETF, STOCK_INTL, ETF_INTL |
| `RENDA_FIXA` | `rendafixa` | Renda Fixa | CDB, LCI_LCA, TESOURO_DIRETO, DEBENTURE, BOND |
| `CRIPTO` | `cripto` | Criptomoedas | CRIPTO |
| `COMMODITY` | `commodity` | Commodities | OUTRO (planejado) |
| `HIBRIDO` | `hibrido` | Ativos híbridos | OUTRO |

---

## 3. TipoTransacao (10 valores)

| Enum | Valor DB | Descrição | Afeta Posição? |
|------|----------|-----------|----------------|
| `COMPRA` | `compra` | Compra de ativo | ✅ Sim (+) |
| `VENDA` | `venda` | Venda de ativo | ✅ Sim (-) |
| `DIVIDENDO` | `dividendo` | Recebimento de dividendo | ❌ Não |
| `JCP` | `jcp` | Juros sobre Capital Próprio | ❌ Não |
| `ALUGUEL` | `aluguel` | Aluguel de ações | ❌ Não |
| `BONIFICACAO` | `bonificacao` | Bonificação em ações | ✅ Sim (+) |
| `SPLIT` | `split` | Desdobramento | ✅ Ajuste |
| `GRUPAMENTO` | `grupamento` | Agrupamento | ✅ Ajuste |
| `SUBSCRICAO` | `subscricao` | Direito de subscrição | ✅ Sim (+) |
| `AMORTIZACAO` | `amortizacao` | Amortização de título | ✅ Sim (-) |

---

## 4. TipoProvento (7 valores)

| Enum | Valor DB | Descrição | Imposto Padrão BR |
|------|----------|-----------|-------------------|
| `DIVIDENDO` | `dividendo` | Dividendo de ação | Isento |
| `JCP` | `jcp` | Juros sobre Capital Próprio | 15% retido |
| `RENDIMENTO` | `rendimento` | Rendimento de FII | Isento |
| `CUPOM` | `cupom` | Cupom de título de renda fixa | Variável |
| `BONIFICACAO` | `bonificacao` | Bonificação em dinheiro | Isento |
| `AMORTIZACAO_PROVENTO` | `amortizacaoprovento` | Amortização com provento | Variável |
| `OUTRO_PROVENTO` | `outroprovento` | Outros tipos de proventos | Variável |

---

## 5. TipoCorretora (2 valores)

| Enum | Valor DB | Descrição |
|------|----------|-----------|
| `CORRETORA` | `corretora` | Corretora tradicional (XP, Clear, Rico) |
| `EXCHANGE` | `exchange` | Exchange de criptomoedas (Binance, Coinbase) |

---

## 6. UserRole (3 valores)

| Enum | Valor DB | Permissões |
|------|----------|------------|
| `ADMIN` | `admin` | Acesso total, CRUD de ativos |
| `USER` | `user` | Acesso às próprias operações |
| `READONLY` | `readonly` | Apenas visualização |

---

## 7. TipoMovimentacao (9 valores)

| Enum | Valor DB | Descrição |
|------|----------|-----------|
| `DEPOSITO` | `deposito` | Depósito na corretora |
| `SAQUE` | `saque` | Saque da corretora |
| `TRANSFERENCIA` | `transferencia` | Transferência entre corretoras |
| `CREDITO_PROVENTO` | `creditoprovento` | Crédito de provento |
| `TAXA_CORRETAGEM` | `taxacorretagem` | Taxa de corretagem |
| `TAXA_CUSTODIA` | `taxacustodia` | Taxa de custódia |
| `IMPOSTO` | `imposto` | Débito de imposto |
| `AJUSTE` | `ajuste` | Ajuste manual |
| `OUTRO_MOV` | `outromov` | Outras movimentações |

---

## 8. TipoEventoCorporativo (12 valores)

| Enum | Valor DB | Impacto Posições |
|------|----------|-----------------|
| `SPLIT` | `split` | Sim |
| `GRUPAMENTO` | `grupamento` | Sim |
| `BONIFICACAO` | `bonificacao` | Sim |
| `FUSAO` | `fusao` | Sim |
| `CISAO` | `cisao` | Sim |
| `SPINOFF` | `spinoff` | Sim |
| `INCORPORACAO` | `incorporacao` | Sim |
| `MUDANCA_TICKER` | `mudancaticker` | Não |
| `DESLISTAGEM` | `deslistagem` | Não |
| `SUBSCRICAO` | `subscricao` | Sim |
| `CONVERSAO` | `conversao` | Sim |
| `OUTRO_EVENTO` | `outroevento` | Variável |

---

## 9. IncidenciaImposto (4 valores)

| Enum | Valor DB | Descrição |
|------|----------|-----------|
| `LUCRO` | `lucro` | Incide sobre ganho de capital |
| `RECEITA` | `receita` | Incide sobre receita bruta |
| `PROVENTO` | `provento` | Incide sobre proventos |
| `OPERACAO` | `operacao` | Incide sobre cada operação |

> **Nota v0.7.9:** `IncidenciaImposto` agora está corretamente exportado em `app/models/__init__.py`.
> Fix: GAP EXITUS-SEEDS-RUN-001 resolvido.

---

## 10. TipoFeriado (6 valores)

| Enum | Valor DB | Descrição |
|------|----------|-----------|
| `NACIONAL` | `nacional` | Feriado nacional |
| `BOLSA` | `bolsa` | Fechamento da bolsa |
| `PONTE` | `ponte` | Ponte/emenda |
| `FECHAMENTO_ANTECIPADO` | `fechamentoantecipado` | Pregão encerrado mais cedo |
| `RELIGIOSO` | `religioso` | Feriado religioso |
| `OUTRO_FERIADO` | `outroferiado` | Outros |

---

## 11. TipoFonteDados (5 valores)

| Enum | Valor DB | Exemplos |
|------|----------|----------|
| `API` | `api` | yfinance, brapi.dev |
| `SCRAPER` | `scraper` | Web scraping |
| `MANUAL` | `manual` | Entrada manual |
| `ARQUIVO` | `arquivo` | Import CSV/Excel |
| `OUTRO_FONTE` | `outrofonte` | Outros |

---

## Histórico de Alterações

| Data | Versão | Mudança | Migration |
|------|--------|---------|-----------|
| 19/02/2026 | 0.7.9 | Documentada divergência ENUMs query param vs JSON vs DB | — |
| 19/02/2026 | 0.7.9 | `IncidenciaImposto` adicionado ao `app/models/__init__.py` | — |
| 16/02/2026 | 0.7.8 | Expansão de 7 para 14 tipos em TipoAtivo | `202602162111`, `202602162130` |
| 16/02/2026 | 0.7.8 | Adição do campo `cap_rate` em Ativo | `202602162130` |
| 16/02/2026 | 0.7.8 | Remoção do campo `bolsa_origem` | `202602162130` |

---

## Mapeamento Mercado → Sufixo (APIs externas)

| Mercado | Sufixo | Exemplo |
|---------|--------|---------|
| BR | `.SA` | PETR4.SA |
| US | *(vazio)* | AAPL |
| EU | *(depende da bolsa)* | SAP.DE |
| ASIA | *(depende da bolsa)* | 7203.T |
| GLOBAL | *(vazio)* | BTC-USD |

---

## Validações e Constraints

### No Banco de Dados (PostgreSQL)
```sql
-- Enum TipoAtivo com 14 valores (sem underscore)
CREATE TYPE tipoativo AS ENUM (
    'acao', 'fii', 'cdb', 'lcilca', 'tesourodireto', 'debenture',
    'stock', 'reit', 'bond', 'etf',
    'stockintl', 'etfintl',
    'cripto', 'outro'
);
```

### No Python (SQLAlchemy)
```python
class TipoAtivo(enum.Enum):
    # Brasil
    ACAO = "acao"
    FII = "fii"
    CDB = "cdb"
    LCI_LCA = "lcilca"
    TESOURO_DIRETO = "tesourodireto"
    DEBENTURE = "debenture"
    # US
    STOCK = "stock"
    REIT = "reit"
    BOND = "bond"
    ETF = "etf"
    # Internacional
    STOCK_INTL = "stockintl"
    ETF_INTL = "etfintl"
    # Outros
    CRIPTO = "cripto"
    OUTRO = "outro"
```

### Estatísticas Atuais do Sistema

- **Total de ENUMs:** 11 tipos diferentes
- **Total de valores:** 62 valores únicos
- **Ativos cadastrados:** 70 (47 BR + 16 US + 3 EU + 4 outros)
- **Migrations aplicadas:** 2 (`202602162111`, `202602162130`)
- **Última atualização:** 19/02/2026
