
# Credenciais de Teste - Sistema Exitus (Dev)

**APENAS PARA AMBIENTE DE DESENVOLVIMENTO** ⚠️

> **v0.7.9** — Corrigido: login usa `username` (não `email`). Adicionados 8 ativos Renda Fixa BR.

---

## 📋 Usuários Seedados

| Username       | Email                         | Senha      | Perfil            |
|----------------|-------------------------------|------------|-------------------|
| `admin`        | `admin@exitus.com`            | `senha123` | **Administrador** |
| `joao.silva`   | `joao.silva@example.com`      | `senha123` | Usuário           |
| `maria.santos` | `maria.santos@example.com`    | `senha123` | Usuário           |
| `viewer`       | `viewer@exitus.com`           | `senha123` | Visualizador      |
| `teste.user`   | `teste@exitus.com`            | `senha123` | Teste             |

---

## 🔐 Teste de Login (cURL)

> ⚠️ **GAP EXITUS-AUTH-001 (resolvido — Opção A):** O endpoint de login requer `username`, não `email`.

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'
```

**Response esperada:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "783c2bfd-9e36-4cbd-a4fb-901afae9fad3",
      "username": "admin",
      "email": "admin@exitus.com"
    }
  }
}
```

---

## 🎫 Uso do Token

```bash
# Exportar token para variável de ambiente
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r '.data.access_token')

# Usar token em requisições protegidas
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/ativos
```

> ⚠️ **GAP EXITUS-DOCS-API-001:** A resposta de `/api/ativos` usa `.data.ativos[]` (não `.data.items[]`).
> Use sempre `jq '.data.ativos[]'` ao processar a lista de ativos.

---

## 📊 Dados Seedados por Tabela (v0.7.9)

| Tabela                 | **Registros** | Descrição                                                  |
|------------------------|---------------|------------------------------------------------------------|
| **usuarios**           | **5**         | Perfis diversos: admin, usuário padrão, visualizador, teste |
| **ativo**              | **70**        | **47 BR** (ações+FIIs+Renda Fixa) + **16 US** + **3 EU** + **4 outros** |
| **corretora**          | **13**        | Nacionais e internacionais                                 |
| **portfolio**          | **4**         | Estratégias: conservador, moderado, agressivo              |
| **transacao**          | **17**        | COMPRA, VENDA, distribuídas entre ativos/corretoras        |
| **posicao**            | **17**        | Posições ativas vinculadas a portfolios                    |
| **provento**           | **29**        | DIVIDENDO, JCP, RENDIMENTO por ativo                       |
| **movimentacao_caixa** | **2**         | Transferências, depósitos, retiradas                       |
| **regra_fiscal**       | **6**         | Regras de IR brasileiras (Ações, FIIs, JCP)                |
| **feriado_mercado**    | **30**        | Feriados B3 2025-2026                                      |
| **fonte_dados**        | **7**         | APIs: yfinance, brapi.dev, Alpha Vantage, etc.             |

**Total ativos seedados:** **70** ✅

---

## 🆕 Detalhamento Ativos v0.7.9

### 🇧🇷 Brasil (47 ativos)

**Ações (20):** `PETR4`, `VALE3`, `ITUB4`, `BBDC4`, `BBAS3`, `MGLU3`, `WEGE3`, `RENT3`, `RAIL3`,
`SUZB3`, `KLBN11`, `ELET3`, `CMIG4`, `CPLE6`, `ABEV3` e demais.

**FIIs (15):** `HGLG11`, `KNRI11`, `BTLG11`, `MXRF11`, `KNCR11`, `LVBI11`, `GGRC11`, `XPML11`,
`VISC11`, `TRXF11` e demais.

**Renda Fixa (12)** ⭐ *v0.7.8 + v0.7.9*:
| Tipo             | Ticker              | Nome                        | Seed                           |
|------------------|---------------------|-----------------------------|--------------------------------|
| `CDB`            | `CDBNUBANK100CDI`   | Nubank CDB 100% CDI         | `seed_ativos_renda_fixa_br.py` |
| `CDB`            | `CDBINTER105CDI`    | Banco Inter CDB 105% CDI    | `seed_ativos_renda_fixa_br.py` |
| `CDB`            | `CDBC6107CDI`       | C6 Bank CDB 107% CDI        | `seed_ativos_renda_fixa_br.py` |
| `TESOURO_DIRETO` | `TESOUROSELIC2029`  | Tesouro Selic 2029          | `seed_ativos_renda_fixa_br.py` |
| `TESOURO_DIRETO` | `TESOUROIPCA2035`   | Tesouro IPCA+ 2035          | `seed_ativos_renda_fixa_br.py` |
| `TESOURO_DIRETO` | `TESOUROPREFIX2027` | Tesouro Prefixado 2027      | `seed_ativos_renda_fixa_br.py` |
| `DEBENTURE`      | `VALE23DBNT`        | Vale Debênture NT 2023      | `seed_ativos_renda_fixa_br.py` |
| `DEBENTURE`      | `PETR4DBNT`         | Petrobras Debênture NT      | `seed_ativos_renda_fixa_br.py` |

> **Nota:** Na resposta JSON da API, o campo `tipo` é retornado em lowercase snake_case:
> `CDB` → `"cdb"` | `TESOURO_DIRETO` → `"tesouro_direto"` | `DEBENTURE` → `"debenture"`
> Para filtros via query param, use UPPERCASE: `?tipo=CDB`, `?tipo=TESOURO_DIRETO`, `?tipo=DEBENTURE`

### 🇺🇸 US (16 ativos) — `app/seeds/seed_ativos_us.py`
- **Stocks (6):** `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `NVDA`
- **REITs (3):** `O`, `VNQ`, `PLD`
- **ETFs (5):** `SPY`, `QQQ`, `IWM`, `DIA`, `VTI`
- **Bonds (2):** `AGG`, `BND`

### 🇪🇺 EU (3 ativos) — `app/seeds/seed_ativos_eu.py`
- **Stocks INTL (2):** `ASML`, `SAP`
- **ETF INTL (1):** `VWCE.DE`

### 🛠️ Outros (4 ativos)
- **CRIPTO (2):** `BTC`, `ETH`
- **OUTRO (2):** `PETZ34`, `WEGE34`

---

## 🛠️ Scripts de Seeds

> ⚠️ v0.7.9 — Seeds US e EU corrigidos para usar `filter_by(ticker, mercado)`
> garantindo idempotência e alinhamento com UNIQUE (ticker, mercado).
> Seeds BR corrigidos: removido campo `bolsa_origem` (deprecated desde v0.7.8).

### 1. Executar Todos os Seeds
```bash
podman exec -it exitus-backend python -m app.seeds.run_all_seeds
```

### 2. Seeds Individuais
```bash
# Usuários (5)
podman exec -it exitus-backend python -m app.seeds.seed_usuarios

# Ativos BR — Ações e FIIs (25)
podman exec -it exitus-backend python -m app.seeds.seed_ativos_br

# Ativos Renda Fixa BR (8) ⭐ v0.7.9
podman exec -it exitus-backend python -m app.seeds.seed_ativos_renda_fixa_br

# Ativos US (16)
podman exec -it exitus-backend python -m app.seeds.seed_ativos_us

# Ativos EU (3)
podman exec -it exitus-backend python -m app.seeds.seed_ativos_eu

# Regras Fiscais BR (6)
podman exec -it exitus-backend python -m app.seeds.seed_regras_fiscais_br

# Feriados B3 2025-2026 (30)
podman exec -it exitus-backend python -m app.seeds.seed_feriados_b3

# Fontes de Dados (7)
podman exec -it exitus-backend python -m app.seeds.seed_fontes_dados
```

### 3. Limpar e Repopular (CUIDADO!)
```bash
# ATENÇÃO: Apaga TODOS os dados!
podman exec exitus-db psql -U exitus -d exitusdb -c "
TRUNCATE TABLE movimentacao_caixa, provento, transacao, posicao,
portfolio, corretora, ativo, usuario CASCADE;
"

# Repopular
podman exec -it exitus-backend python -m app.seeds.run_all_seeds
```

---

## 🔍 Verificar Seeds Instalados

```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 'usuario' AS tabela, COUNT(*) AS registros FROM usuario
UNION ALL SELECT 'ativo', COUNT(*) FROM ativo
UNION ALL SELECT 'corretora', COUNT(*) FROM corretora
UNION ALL SELECT 'regra_fiscal', COUNT(*) FROM regra_fiscal
UNION ALL SELECT 'feriado_mercado', COUNT(*) FROM feriado_mercado
UNION ALL SELECT 'fonte_dados', COUNT(*) FROM fonte_dados
ORDER BY tabela;
"
```

**Resultado esperado (v0.7.9):**
```
tabela            | registros
------------------+----------
ativo             | 70
corretora         | 13
feriado_mercado   | 30
fonte_dados       | 7
regra_fiscal      | 6
usuario           | 5
```

### Contagem por Tipo de Ativo (v0.7.9)
```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT tipo, COUNT(*) as total
FROM ativo
GROUP BY tipo
ORDER BY total DESC;
"
```

### Teste Filtros API Renda Fixa BR (validado 20/02/2026)
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r '.data.access_token')

# CDB — esperado: total=3
curl -s "http://localhost:5000/api/ativos?mercado=BR&tipo=CDB" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.total'

# TESOURO_DIRETO — esperado: total=3
curl -s "http://localhost:5000/api/ativos?mercado=BR&tipo=TESOURO_DIRETO" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.total'

# DEBENTURE — esperado: total=2
curl -s "http://localhost:5000/api/ativos?mercado=BR&tipo=DEBENTURE" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.total'
```

---

## ⚠️ Notas de Segurança
- **APENAS** para ambiente de **desenvolvimento**
- **NUNCA** use `senha123` em produção
- **Altere** todas as credenciais antes de deploy
- Mantenha este arquivo **fora do Git** em produção (`docs/SEEDS.md` → `.gitignore`)

---

## 📅 Validação
- **Data:** 20/Fev/2026
- **Versão:** **v0.7.9** (Seed Renda Fixa BR + Fix seeds US/EU/BR — M2-ATIVOS-005)
- **PostgreSQL:** 16.11
- **Total ativos seedados:** **70** (47 BR + 16 US + 3 EU + 4 outros)
- **Status:** ✅ **VALIDADO**

**Referência:** [ENUMS.md](../docs/ENUMS.md) (14 tipos) | [CHANGELOG.md](../docs/CHANGELOG.md)
