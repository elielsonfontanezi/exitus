# Seeds do Sistema Exitus - Guia Completo

**APENAS PARA AMBIENTE DE DESENVOLVIMENTO** ⚠️

> **v0.9.4** — Cenários de teste implementados (E2E, IR, Stress) + dados atualizados  
> **Atualização:** 22/03/2026 - Adicionado histórico patrimonial ao test_full

---

## 📋 Sumário Rápido

| Seção | O que encontrar |
|-------|------------------|
| **Credenciais** | Usuários/senhas para acesso |
| **Cenários JSON** | test_full, test_e2e, test_ir, test_stress |
| **Comandos** | Reset, seed, verificação |
| **Troubleshooting** | Problemas comuns e soluções |
| **Histórico Patrimonial** | 16 meses de evolução (R$ 0 → R$ 58.050) |

---

## 🔐 Credenciais de Acesso

### Usuários Padrão

| Username | Email | Senha | Perfil |
|----------|-------|-------|-------|
| `e2e_admin` | `admin@e2e.exitus` | `e2e_senha_123` | **Administrador** |
| `e2e_user` | `usuario@e2e.exitus` | `e2e_senha_123` | Usuário |
| `e2e_viewer` | `viewer@e2e.exitus` | `e2e_senha_123` | Visualizador |
| `teste.user` | `teste@exitus.com` | `senha123` | Teste |

### Teste de Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e_admin","password":"e2e_senha_123"}'
```

### Uso do Token

```bash
# Exportar token
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"e2e_admin","password":"e2e_senha_123"}' | jq -r '.data.access_token')

# Usar em requisições
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/ativos
```

---

## 🎯 Cenários JSON Disponíveis

### Estrutura de Diretórios

```
backend/
├── seed_data/
│   ├── scenarios/           # Cenários JSON predefinidos
│   │   ├── test_e2e.json   # Dados realistas para E2E
│   │   ├── test_full.json  # Cenário COMPLETO com histórico
│   │   ├── test_ir.json    # Dados para testes de IR
│   │   └── test_stress.json # Dados para stress
│   ├── usuarios.json       # Seed básico de usuários
│   ├── ativos_br.json      # Ativos brasileiros
│   ├── ativos_us.json      # Ativos americanos
│   └── ativos_eu.json      # Ativos europeus
├── load_scenario.py        # Carregador de cenários JSON
└── reset_and_seed.py       # Script principal de reset+seed
```

---

### 1. test_full.json - **CENÁRIO COMPLETO** ✅

**Descrição:** Cenário COMPLETO para TODAS as telas - cobertura 100% do sistema (com histórico de evolução patrimonial)

**Conteúdo:**
- **Usuários:** 3 (e2e_admin, e2e_user, e2e_viewer)
- **Ativos:** 9 (BR, US, INTL)
- **Transações:** 8 (compras e vendas)
- **Proventos:** 2 (dividendos)
- **Movimentações:** 2 (depósito, saque)
- **Portfolios:** 3
- **Alertas:** 3
- **Planos:** 3 compra + 2 venda
- **Histórico Patrimonial:** 16 registros (Mar/2023 a Jun/2024)

**Uso:**
```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_full
```

---

### 2. test_e2e.json - **Testes E2E**

**Descrição:** Dados realistas para testes E2E

**Conteúdo:**
- **Usuários:** 3
- **Ativos:** 7
- **Transações:** 4
- **Proventos:** 2
- **Movimentações:** 2

**Uso:**
```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_e2e
```

---

### 3. test_ir.json - **Testes Fiscais**

**Descrição:** Dados específicos para testes de Imposto de Renda

**Conteúdo:**
- Operações com diferentes tipos de ativos
- Dados para cálculo de IR, DARF
- Proventos tributáveis e isentos

**Uso:**
```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_ir
```

---

### 4. test_stress.json - **Testes de Performance**

**Descrição:** Dados para testes de performance

**Conteúdo:**
- Grande volume de dados
- Múltiplos usuários e transações
- Dados estressantes para testes de carga

**Uso:**
```bash
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_stress
```

---

## 📊 Histórico Patrimonial

### Estrutura dos Dados

```json
{
  "version": "2.0",
  "description": "Cenário COMPLETO e2e_user — Carteira Aposentadoria com 30 ativos (10 BR + 10 US + 10 INTL), proventos, vendas com lucro/prejuízo, IR e compensação",
  "timestamp": "2026-03-25T00:00:00Z",
  "ativos": [...], // 30 ativos diversificados
  "transacoes": [...], // 48 transações (compras, vendas, day trades)
  "proventos": [...], // 32 proventos (DIVIDENDO, JCP, RENDIMENTO)
  "movimentacoes_caixa": [...], // 15 movimentações (aportes BRL/USD, saques, DARF)
  "portfolios": [...], // 4 portfolios (Aposentadoria, Dividendos BR, Growth US)
  "historico_patrimonio": [...] // 12 snapshots mensais (Jan-Dez/2024)
}
```

### Campos Principais

| Campo | Tipo | Descrição |
|-------|------|----------|
| `usuario` | string | Username do usuário |
| `data` | string | Data do snapshot (YYYY-MM-DD) |
| `patrimonio_total` | decimal | Patrimônio total |
| `patrimonio_renda_variavel` | decimal | Valor em renda variável |
| `patrimonio_renda_fixa` | decimal | Valor em renda fixa |
| `saldo_caixa` | decimal | Saldo disponível |
| `observacoes` | string | Observações do período |
| `moeda` | string | Moeda da movimentação (BRL, USD) |
| `quantidade_ativos` | integer | Quantidade de ativos para proventos |
| `imposto_retido` | decimal | IR retido na fonte (JCP) |

### Evolução do e2e_user - Carteira Aposentadoria

| Período | Patrimônio | Evento Principal |
|---------|------------|------------------|
| Jan/2024 | R$ 119.452 | Aportes iniciais BRL — PETR4, ITUB4, HGLG11, BBDC4 |
| Fev/2024 | R$ 172.815 | + VALE3, WEGE3, KNRI11, MXRF11 + aporte USD Avenue |
| Mar/2024 | R$ 188.920 | + AAPL, MSFT (US) + BBAS3, TAEE11 + proventos |
| Abr/2024 | R$ 227.350 | + TSLA34, AAPL34, MSFT34, GOOGL (INTL/US) |
| Mai/2024 | R$ 255.680 | + NVDA, AMZN (US) + AMZO34, GOGL34 (INTL) |
| Jun/2024 | R$ 278.900 | Venda PETR4 lucro + JPM, VTI, NVDC34 + saque |
| Jul/2024 | R$ 301.250 | Venda BBDC4 lucro + SCHD, O, DISB34 + aporte Nomad |
| Ago/2024 | R$ 335.100 | Venda VALE3 prejuízo + PLD, COCA34, IVVB11 |
| Set/2024 | R$ 348.750 | Venda WEGE3/MXRF11 prejuízo + EURP11, IVVB11 |
| Out/2024 | R$ 342.800 | Vendas PETR4/ITUB4/TSLA34/AAPL (IR gerado) |
| Nov/2024 | R$ 338.450 | Vendas MSFT/HGLG11/DISB34/GOOGL + DARF R$ 685,50 |
| Dez/2024 | R$ 330.200 | Vendas KNRI11/NVDA/BBAS3/GOGL34 + saque R$ 5K |

### Cenários de IR e Compensação

| Mês | Operações | Resultado | IR Pago |
|-----|-----------|-----------|---------|
| Outubro | Vendas PETR4/ITUB4 (>R$ 20K) + TSLA34/AAPL | Lucro líquido | R$ 685,50 |
| Novembro | Vendas MSFT/HGLG11/DISB34/GOOGL | Lucro/prejuízo misto | R$ 76,00 |
| Dezembro | Vendas KNRI11/NVDA/BBAS3/GOGL34 | Compensação prejuízos | — |

**Total investido**: R$ 173.000 (BRL) + US$ 23.000 (USD)  
**Proventos recebidos**: R$ 4.850 + US$ 45  
**IR total pago**: R$ 761,50

---

## 🛠️ Comandos Úteis

### Reset + Seed

```bash
# Cenário completo (com histórico patrimonial)
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_full

# Cenário E2E
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_e2e

# Seed básico (sem cenários JSON)
podman exec exitus-backend python reset_and_seed.py --clean --seed-type=full

# Seed mínimo
podman exec exitus-backend python reset_and_seed.py --clean --seed-type=minimal

# Listar cenários disponíveis
podman exec exitus-backend python reset_and_seed.py --list-scenarios
```

### Verificação de Dados

```bash
# Verificar histórico patrimonial
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT u.username, COUNT(*) as registros, MIN(h.data) as primeira, MAX(h.data) as ultima 
FROM historico_patrimonio h 
JOIN usuario u ON h.usuario_id = u.id 
GROUP BY u.username;
"

# Verificar usuários
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT username, email FROM usuario;"

# Verificar ativos
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT ticker, mercado, tipo FROM ativo ORDER BY mercado, ticker;"

# Contagem geral
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 'usuario' AS tabela, COUNT(*) AS registros FROM usuario
UNION ALL SELECT 'ativo', COUNT(*) FROM ativo
UNION ALL SELECT 'corretora', COUNT(*) FROM corretora
UNION ALL SELECT 'historico_patrimonio', COUNT(*) FROM historico_patrimonio
ORDER BY tabela;
"
```

---

## 🔄 Como Funciona o Load Scenario

### Fluxo de Execução

1. **Reset do banco** - Limpa todas as tabelas
2. **Load JSON** - Carrega arquivo do cenário
3. **Seed em ordem** - Respeita dependências:
   - Assessoras
   - Usuários
   - Ativos
   - Corretoras
   - Transações
   - Proventos
   - Movimentações
   - Portfolios
   - Alertas
   - Planos de compra
   - Planos de venda
   - **Histórico patrimonial** ← (se existir)

### Resolução de Referências

O sistema automaticamente resolve:
- `username` → `usuario_id`
- `ticker` → `ativo_id`
- `nome` (corretora) → `corretora_id`

---

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Histórico Patrimonial Não É Seedado

**Sintomas:** Tabela vazia após rodar cenário

**Verificações:**
```bash
# Verificar se dados existem no JSON
grep -A5 "historico_patrimonio" backend/seed_data/scenarios/test_full.json

# Verificar se função existe
grep -A5 "_seed_historico_patrimonio" backend/load_scenario.py

# Verificar se está sendo chamada
grep "self._seed_historico_patrimonio" backend/load_scenario.py
```

**Solução:** Garantir que a função `_seed_historico_patrimonio()` está no `load_scenario.py` e é chamada em `seed_all()`.

#### 2. Erros de Import

**Sintomas:** `ImportError: cannot import name 'HistoricoPatrimonio'`

**Verificações:**
```bash
# Verificar import no __init__.py
grep "HistoricoPatrimonio" backend/app/models/__init__.py

# Verificar se está no __all__
grep "HistoricoPatrimonio" backend/app/models/__init__.py -A2
```

**Solução:** Adicionar import e export em `backend/app/models/__init__.py`.

#### 3. Constraint Violation

**Sintomas:** `UniqueViolation: duplicate key value violates unique constraint`

**Causa:** Tentativa de inserir duplicado em `(usuario_id, data)`

**Solução:** O sistema já verifica duplicatas. Se ocorrer, limpar com `--clean`.

---

## 📝 Criando Novos Cenários

### Estrutura Básica

```json
{
  "version": "1.0",
  "description": "Descrição do cenário",
  "timestamp": "2026-03-22T00:00:00",
  "usuarios": [...],
  "assessoras": [...],
  "ativos": [...],
  "corretoras": [...],
  "transacoes": [...],
  "proventos": [...],
  "movimentacoes_caixa": [...],
  "alertas": [...],
  "portfolios": [...],
  "planos_compra": [...],
  "planos_venda": [...],
  "historico_patrimonio": [...]
}
```

### Dicas

1. **Use usernames únicos** para evitar conflitos
2. **Respeite os enums** (TipoAtivo, ClasseAtivo, etc.)
3. **Inclua histórico patrimonial** se precisar testar evolução
4. **Teste com --clean** sempre

---

## 🎯 Boas Práticas

### 1. Nomenclatura
- Prefixo `test_` para cenários de teste
- Nomes descritivos: `test_full`, `test_e2e`, `test_ir`

### 2. Dados Realistas
- Use valores de mercado reais
- Datas consistentes
- Evolução patrimonial lógica

### 3. Documentação
- Sempre atualizar este documento
- Descrever propósito do cenário
- Listar dados incluídos

### 4. Versionamento
- Incrementar versão em mudanças significativas
- Manter compatibilidade com versões anteriores quando possível

---

## 📚 Dados Seedados por Tabela

| Tabela | **Registros** | Descrição |
|--------|---------------|-----------|
| **usuarios** | **5** | Perfis diversos: admin, usuário padrão, visualizador, teste |
| **ativo** | **70** | **47 BR** (ações+FIIs+Renda Fixa) + **16 US** + **3 EU** + **4 outros** |
| **corretora** | **13** | Nacionais e internacionais |
| **portfolio** | **4** | Estratégias: conservador, moderado, agressivo |
| **transacao** | **17** | COMPRA, VENDA, distribuídas entre ativos/corretoras |
| **posicao** | **17** | Posições ativas vinculadas a portfolios |
| **provento** | **29** | DIVIDENDO, JCP, RENDIMENTO por ativo |
| **movimentacao_caixa** | **2** | Transferências, depósitos, retiradas |
| **regra_fiscal** | **12** | Regras de IR: venções (swing/DT/FII/US), proventos |
| **feriado_mercado** | **30** | Feriados B3 2025-2026 |
| **fonte_dados** | **7** | APIs: yfinance, brapi.dev, Alpha Vantage, etc. |
| **historico_patrimonio** | **16** | Snapshots mensais (Mar/2023 a Jun/2024) |

---

## 🚀 Para Próxima Sessão Cascade

Quando voltar a trabalhar com seeds, use este prompt:

```
Quero trabalhar com seeds do Exitus. Por favor:

1. Verifique o status atual dos cenários de seed
2. Execute o test_full para validar que o histórico patrimonial está funcionando
3. Se houver problemas, identifique e corrija
4. Mostre os dados inseridos no banco
5. Verifique se o endpoint /api/portfolios/evolucao retorna os dados corretamente

Contexto: Já implementamos HistoricoPatrimonio com 16 registros no test_full.json.
```

---

## ⚠️ Notas de Segurança

- **APENAS** para ambiente de **desenvolvimento**
- **NUNCA** use `senha123` em produção
- **Altere** todas as credenciais antes de deploy
- Mantenha este arquivo **fora do Git** em produção (`docs/SEEDS.md` → `.gitignore`)

---

## 📊 Validação

- **Data:** 22/03/2026
- **Versão:** **v0.9.4** (Cenários de teste + dados atualizados)
- **PostgreSQL:** 16.11
- **Total ativos seedados:** **47** (Ações BR, FIIs, Stocks US, Ações EU)
- **Total regras fiscais:** **6** (IR básico para operações)
- **Total usuários:** **5** (admin, users, viewer, teste)
- **Status:** **VALIDADO**

---

**Documentação relacionada:**
- [API_REFERENCE.md](API_REFERENCE.md) - Endpoints disponíveis
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Status atual do projeto
- [ROADMAP.md](ROADMAP.md) - Roadmap de implementação
- [CHANGELOG.md](CHANGELOG.md) - Histórico de mudanças

---

**Última atualização:** 22/03/2026  
**Versão:** v1.0 (Consolidado)  
**Status:** ✅ Funcional
