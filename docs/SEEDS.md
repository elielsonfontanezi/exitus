# Credenciais de Teste - Sistema Exitus (Dev)

**APENAS PARA AMBIENTE DE DESENVOLVIMENTO** ⚠️[file:16]

## 📋 Usuários Seedados

| Username     | Email                | Senha    | Perfil        |
|--------------|----------------------|----------|---------------|
| `admin`      | `admin@exitus.com`   | `senha123` | **Administrador** |
| `joao.silva` | `joao.silva@example.com` | `senha123` | Usuário     |
| `maria.santos` | `maria.santos@example.com` | `senha123` | Usuário   |
| `viewer`     | `viewer@exitus.com`  | `senha123` | Visualizador |
| `teste.user` | `teste@exitus.com`   | `senha123` | Teste       |[file:16]

## 🔐 Teste de Login (cURL)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}'
```

**Response esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "783c2bfd-9e36-4cbd-a4fb-901afae9fad3",
    "username": "admin",
    "email": "admin@exitus.com"
  }
}
```[file:16]

## 🎫 Uso do Token

```bash
# Exportar token para variável de ambiente
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}' | jq -r .access_token)

# Usar token em requisições protegidas
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/usuarios
```[file:16]

## 📊 Dados Seedados por Tabela (v0.7.8)

| Tabela              | **Registros** | Descrição |
|---------------------|---------------|-----------|
| **usuarios**        | **5**         | Perfis diversos: admin, usuário padrão, visualizador, teste[file:16] |
| **ativo**           | **62**        | **39 BR (ações+FIIs)** + **16 US** + **3 EU** + **4 outros** |
| **corretora**       | **13**        | Nacionais e internacionais (NACIONAL, INTERNACIONAL)[file:16] |
| **portfolio**       | **4**         | Estratégias: conservador, moderado, agressivo[file:16] |
| **transacao**       | **17**        | COMPRA, VENDA, distribuídas entre ativos/corretoras[file:16] |
| **posicao**         | **17**        | Posições ativas vinculadas a portfolios[file:16] |
| **provento**        | **29**        | DIVIDENDO, JCP, RENDIMENTO por ativo[file:16] |
| **movimentacao_caixa** | **2**     | Transferências, depósitos, retiradas[file:16] |

**Total:** **131 registros** seedados ✅[file:16]

### 🆕 Detalhamento Ativos v0.7.8

**🇧🇷 Brasil (39 ativos):**
- **Ações** (20): `PETR4`, `VALE3`, `ITUB4`, `BBDC4`, etc.
- **FIIs** (15): `HGLG11`, `MXRF11`, `KNRI11`, etc.
- **Renda Fixa** (4): `CDB`, `LCI_LCA`, `TESOURO_SELIC`, `DEBENTURE`

**🇺🇸 US (16 ativos) - `app/seeds/seed_ativos_us.py`:**
- **Stocks** (10): `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `NVDA`, `META`, `JPM`, `V`, `WMT`
- **REITs** (3): `O`, `VNQ`, `SPG`
- **ETFs** (2): `SPY`, `QQQ`
- **Bond** (1): `US_TREASURY_10Y`

**🇪🇺 EU (3 ativos) - `app/seeds/seed_ativos_eu.py`:**
- **Stocks INTL** (2): `SAP.DE`, `ASML.AS`
- **ETF INTL** (1): `VWCE.DE`

**🛠️ Outros (4 ativos):**
- **CRIPTO** (2): `BTC`, `ETH`
- **OUTRO** (2): `PETZ34`, `WEGE34`[file:1]

## 🛠️ Scripts de Seeds

### 1. Executar Todos os Seeds
```bash
podman exec -it exitus-backend bash seeds/seed_all.sh
```[file:16]

### 2. Seeds Multi-Mercado (v0.7.8) ⭐
```bash
# Ativos US (16)
podman exec -it exitus-backend python -m app.seeds.seed_ativos_us

# Ativos EU (3)  
podman exec -it exitus-backend python -m app.seeds.seed_ativos_eu
```

### 3. Limpar e Repopular (CUIDADO!)
```bash
# ATENÇÃO: Apaga TODOS os dados!
podman exec exitus-db psql -U exitus -d exitusdb -c "
TRUNCATE TABLE movimentacao_caixa, provento, transacao, posicao, 
portfolio, corretora, ativo, usuario CASCADE;
"

# Repopular
podman exec -it exitus-backend bash seeds/seed_all.sh
```[file:16]

## 🔍 Verificar Seeds Instalados

```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 'usuario' AS tabela, COUNT(*) AS registros FROM usuario
UNION ALL SELECT 'ativo', COUNT(*) FROM ativo
UNION ALL SELECT 'corretora', COUNT(*) FROM corretora
UNION ALL SELECT 'portfolio', COUNT(*) FROM portfolio
UNION ALL SELECT 'transacao', COUNT(*) FROM transacao
UNION ALL SELECT 'posicao', COUNT(*) FROM posicao
UNION ALL SELECT 'provento', COUNT(*) FROM provento
UNION ALL SELECT 'movimentacao_caixa', COUNT(*) FROM movimentacao_caixa
ORDER BY tabela;
"
```

**Resultado esperado (v0.7.8):**
```
tabela              | registros
--------------------+----------
ativo               | 62
corretora           | 13
movimentacao_caixa  | 2
portfolio           | 4
posicao             | 17
provento            | 29
transacao           | 17
usuario             | 5
(8 rows)
**[TOTAL: 149 registros]** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/138901332/60d48d2a-e8ce-45f3-ae8c-6459a989d9c1/SEEDS.md)
```

### Contagem por Tipo de Ativo (v0.7.8)
```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT tipo, COUNT(*) as total 
FROM ativo 
GROUP BY tipo 
ORDER BY total DESC;
"
```
**Esperado:** 14 tipos com distribuição BR/US/EU/Outros.[file:1]

## ⚠️ Notas de Segurança
- **APENAS** para ambiente de **desenvolvimento**
- **NUNCA** use `senha123` em produção
- **Altere** todas as credenciais antes de deploy
- Mantenha este arquivo **fora do Git** em produção (`docs/SEEDS.md` → `.gitignore`)[file:16]

## 📅 Validação
- **Data:** 17/Fev/2026
- **Versão:** **v0.7.8** (Expansão ENUMs Multi-Mercado)
- **PostgreSQL:** 16.11
- **Total seedados:** **149 registros** (62 ativos + 87 outros)
- **Status:** ✅ **VALIDADO**

---

**Teste rápido:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@exitus.com","password":"senha123"}' | jq
```

**Agora você pode:**
1. **Git commit** (se versionar docs):
   ```bash
   git add docs/SEEDS.md
   git commit -m "docs: atualizar SEEDS.md com 62 ativos v0.7.8"
   ```
2. **.gitignore** (se dados sensíveis):
   ```bash
   echo "docs/SEEDS.md" >> .gitignore
   ```
3. **Testar login** conforme documentado[file:16]

**Referência:** [ENUMS.md](../ENUMS.md) (14 tipos)[file:1]
