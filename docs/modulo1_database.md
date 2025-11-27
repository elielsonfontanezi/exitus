# Exitus - Módulo 1: Database
## Documentação Técnica do Banco de Dados

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Banco](#arquitetura-do-banco)
3. [Models e Tabelas](#models-e-tabelas)
4. [Relacionamentos](#relacionamentos)
5. [Enums e Tipos](#enums-e-tipos)
6. [Índices e Performance](#índices-e-performance)
7. [Queries Úteis](#queries-úteis)
8. [Diagrama ER](#diagrama-er)
9. [Boas Práticas](#boas-práticas)

---

## 🎯 Visão Geral

O banco de dados do Exitus foi projetado para gerenciar investimentos de forma completa e eficiente.

### Estatísticas

| Métrica | Valor |
|---------|-------|
| **Tabelas** | 13 (12 models + alembic_version) |
| **Enums** | 11 tipos personalizados |
| **Foreign Keys** | 15 relacionamentos |
| **Índices** | 86 (automáticos + customizados) |
| **SGBD** | PostgreSQL 15+ |

### Tecnologias

- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic 1.13+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+ Alpine

---

## 🏗️ Arquitetura do Banco

### Camadas de Dados

```
┌─────────────────────────────────────┐
│   CAMADA DE APLICAÇÃO (Flask)      │
├─────────────────────────────────────┤
│   CAMADA ORM (SQLAlchemy)          │
├─────────────────────────────────────┤
│   CAMADA DE DADOS (PostgreSQL)     │
└─────────────────────────────────────┘
```

### Grupos de Tabelas

**1. Core (Essenciais):**
- `usuario` - Usuários do sistema
- `corretora` - Corretoras/brokers
- `ativo` - Ativos financeiros (ações, FIIs, etc.)
- `posicao` - Posições consolidadas
- `transacao` - Operações de compra/venda

**2. Financeiras:**
- `provento` - Dividendos, JCP, rendimentos
- `movimentacao_caixa` - Depósitos, saques, transferências

**3. Eventos e Referência:**
- `evento_corporativo` - Splits, grupamentos, bonificações
- `feriado_mercado` - Feriados de bolsa

**4. Sistema:**
- `fonte_dados` - APIs de cotações
- `regra_fiscal` - Regras de IR
- `log_auditoria` - Auditoria de ações

---

## 📊 Models e Tabelas

### 1. Usuario

**Descrição:** Gerencia usuários e autenticação

**Tabela:** `usuario`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `username` | VARCHAR(80) | Username único |
| `email` | VARCHAR(120) | Email único |
| `password_hash` | VARCHAR(256) | Senha criptografada |
| `nome_completo` | VARCHAR(200) | Nome completo (opcional) |
| `ativo` | BOOLEAN | Se usuário está ativo |
| `role` | ENUM(UserRole) | Papel: ADMIN, USER, READONLY |
| `ultimo_login` | TIMESTAMP | Data do último login |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- UNIQUE: `username`, `email`
- CHECK: `username` deve ter pelo menos 3 caracteres
- CHECK: `email` deve ter formato válido

**Índices:**
- `ix_usuario_username`
- `ix_usuario_email`

**Relacionamentos:**
- 1:N com `corretora`
- 1:N com `posicao`
- 1:N com `transacao`
- 1:N com `movimentacao_caixa`
- 1:N com `log_auditoria`

---

### 2. Corretora

**Descrição:** Corretoras/brokers onde o usuário opera

**Tabela:** `corretora`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `usuario_id` | UUID | FK - Usuário dono |
| `nome` | VARCHAR(100) | Nome da corretora |
| `tipo` | ENUM(TipoCorretora) | NACIONAL, INTERNACIONAL |
| `pais` | VARCHAR(2) | Código ISO do país |
| `moeda_padrao` | VARCHAR(3) | Moeda padrão (BRL, USD) |
| `ativa` | BOOLEAN | Se corretora está ativa |
| `numero_conta` | VARCHAR(50) | Número da conta (opcional) |
| `observacoes` | TEXT | Observações gerais |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `usuario_id` → `usuario.id` (ON DELETE CASCADE)
- CHECK: `pais` formato ISO (2 letras maiúsculas)
- CHECK: `moeda_padrao` formato ISO (3 letras maiúsculas)
- CHECK: `nome` pelo menos 2 caracteres

**Índices:**
- `ix_corretora_usuario_id`
- `ix_corretora_nome`
- `ix_corretora_tipo`
- `ix_corretora_pais`
- `ix_corretora_moeda_padrao`
- `ix_corretora_ativa`

---

### 3. Ativo

**Descrição:** Ativos financeiros (ações, FIIs, ETFs, etc.)

**Tabela:** `ativo`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `ticker` | VARCHAR(20) | Código do ativo (PETR4, AAPL) |
| `nome` | VARCHAR(200) | Nome completo |
| `tipo` | ENUM(TipoAtivo) | ACAO, FII, ETF, BDR, etc. |
| `classe` | ENUM(ClasseAtivo) | RENDA_VARIAVEL, RENDA_FIXA |
| `mercado` | VARCHAR(10) | Mercado (BR, US, etc.) |
| `moeda` | VARCHAR(3) | Moeda de negociação |
| `preco_atual` | NUMERIC(18,8) | Último preço |
| `data_ultima_cotacao` | TIMESTAMP | Data da última cotação |
| `ativo` | BOOLEAN | Se está disponível |
| `deslistado` | BOOLEAN | Se foi deslistado |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- UNIQUE: `ticker`, `mercado`
- CHECK: `ticker` pelo menos 1 caractere
- CHECK: `preco_atual` >= 0 (se informado)

**Índices:**
- `ix_ativo_ticker`
- `ix_ativo_nome`
- `ix_ativo_tipo`
- `ix_ativo_classe`
- `ix_ativo_mercado`
- `ix_ativo_moeda`
- `ix_ativo_ativo`
- `ix_ativo_deslistado`
- `ix_ativo_data_ultima_cotacao`

---

### 4. Posicao

**Descrição:** Posição consolidada de um ativo na carteira

**Tabela:** `posicao`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `usuario_id` | UUID | FK - Usuário dono |
| `corretora_id` | UUID | FK - Corretora |
| `ativo_id` | UUID | FK - Ativo |
| `quantidade` | NUMERIC(18,8) | Quantidade de ativos |
| `preco_medio` | NUMERIC(18,8) | Preço médio de compra |
| `valor_investido` | NUMERIC(18,2) | Custo total |
| `data_primeira_compra` | DATE | Data da primeira compra |
| `data_ultima_atualizacao` | TIMESTAMP | Última atualização |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `usuario_id` → `usuario.id` (CASCADE)
- FOREIGN KEY: `corretora_id` → `corretora.id` (CASCADE)
- FOREIGN KEY: `ativo_id` → `ativo.id` (RESTRICT)
- UNIQUE: `usuario_id`, `corretora_id`, `ativo_id`
- CHECK: `quantidade` >= 0
- CHECK: `preco_medio` > 0
- CHECK: `valor_investido` >= 0

**Índices:**
- `ix_posicao_usuario_id`
- `ix_posicao_corretora_id`
- `ix_posicao_ativo_id`
- `ix_posicao_data_primeira_compra`
- `ix_posicao_data_ultima_atualizacao`

---

### 5. Transacao

**Descrição:** Operações de compra/venda de ativos

**Tabela:** `transacao`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `usuario_id` | UUID | FK - Usuário |
| `corretora_id` | UUID | FK - Corretora |
| `ativo_id` | UUID | FK - Ativo |
| `tipo_operacao` | ENUM | COMPRA, VENDA, BONIFICACAO, etc. |
| `quantidade` | NUMERIC(18,8) | Quantidade negociada |
| `preco_unitario` | NUMERIC(18,8) | Preço por ativo |
| `custos_operacao` | NUMERIC(18,2) | Taxas e emolumentos |
| `data_operacao` | DATE | Data da operação |
| `data_liquidacao` | DATE | Data de liquidação |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `usuario_id`, `corretora_id`, `ativo_id`
- CHECK: `quantidade` > 0
- CHECK: `preco_unitario` >= 0
- CHECK: `custos_operacao` >= 0
- CHECK: `data_liquidacao` >= `data_operacao`

**Índices:**
- `ix_transacao_usuario_id`
- `ix_transacao_corretora_id`
- `ix_transacao_ativo_id`
- `ix_transacao_tipo_operacao`
- `ix_transacao_data_operacao`
- `ix_transacao_data_liquidacao`

---

### 6. Provento

**Descrição:** Dividendos, JCP e outros proventos

**Tabela:** `provento`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `ativo_id` | UUID | FK - Ativo que pagou |
| `tipo_provento` | ENUM | DIVIDENDO, JCP, RENDIMENTO, etc. |
| `valor_por_acao` | NUMERIC(18,8) | Valor por ação/cota |
| `quantidade_ativos` | NUMERIC(18,8) | Qtd de ativos que o usuário tinha |
| `valor_total` | NUMERIC(18,2) | Valor total recebido |
| `imposto_retido` | NUMERIC(18,2) | IR retido na fonte |
| `data_com` | DATE | Data COM |
| `data_pagamento` | DATE | Data de pagamento |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `ativo_id` → `ativo.id` (RESTRICT)
- CHECK: `valor_por_acao` >= 0
- CHECK: `quantidade_ativos` > 0
- CHECK: `valor_total` >= 0
- CHECK: `imposto_retido` >= 0
- CHECK: `data_pagamento` >= `data_com`

**Índices:**
- `ix_provento_ativo_id`
- `ix_provento_tipo_provento`
- `ix_provento_data_com`
- `ix_provento_data_pagamento`

---

### 7. MovimentacaoCaixa

**Descrição:** Depósitos, saques e transferências entre corretoras

**Tabela:** `movimentacao_caixa`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `usuario_id` | UUID | FK - Usuário |
| `corretora_id` | UUID | FK - Corretora origem |
| `corretora_destino_id` | UUID | FK - Corretora destino (transferências) |
| `provento_id` | UUID | FK - Provento relacionado (se houver) |
| `tipo_movimentacao` | ENUM | DEPOSITO, SAQUE, TRANSFERENCIA, etc. |
| `valor` | NUMERIC(18,2) | Valor da movimentação |
| `moeda` | VARCHAR(3) | Moeda |
| `data_movimentacao` | DATE | Data da movimentação |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `usuario_id`, `corretora_id`, `corretora_destino_id`, `provento_id`
- CHECK: `valor` > 0

**Índices:**
- `ix_movimentacao_caixa_usuario_id`
- `ix_movimentacao_caixa_corretora_id`
- `ix_movimentacao_caixa_corretora_destino_id`
- `ix_movimentacao_caixa_provento_id`
- `ix_movimentacao_caixa_tipo_movimentacao`
- `ix_movimentacao_caixa_data_movimentacao`
- `ix_movimentacao_caixa_moeda`

---

### 8. EventoCorporativo

**Descrição:** Eventos corporativos (splits, grupamentos, etc.)

**Tabela:** `evento_corporativo`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `ativo_id` | UUID | FK - Ativo afetado |
| `ativo_novo_id` | UUID | FK - Novo ativo (fusões/cisões) |
| `tipo_evento` | ENUM | SPLIT, GRUPAMENTO, BONIFICACAO, etc. |
| `data_evento` | DATE | Data do evento |
| `data_com` | DATE | Data COM |
| `proporcao` | VARCHAR(20) | Proporção (ex: 2:1) |
| `descricao` | TEXT | Descrição do evento |
| `impacto_posicoes` | BOOLEAN | Se afeta posições |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- FOREIGN KEY: `ativo_id`, `ativo_novo_id` → `ativo.id`
- CHECK: `data_com` <= `data_evento` (se informado)

**Índices:**
- `ix_evento_corporativo_ativo_id`
- `ix_evento_corporativo_ativo_novo_id`
- `ix_evento_corporativo_tipo_evento`
- `ix_evento_corporativo_data_evento`
- `ix_evento_corporativo_data_com`
- `ix_evento_corporativo_impacto_posicoes`

---

### 9. FonteDados

**Descrição:** Fontes de dados para cotações (APIs)

**Tabela:** `fonte_dados`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `nome` | VARCHAR(100) | Nome da fonte (yfinance, brapi) |
| `tipo_fonte` | ENUM | API, SCRAPING, MANUAL, ARQUIVO |
| `url_base` | VARCHAR(500) | URL base da API |
| `requer_autenticacao` | BOOLEAN | Se requer API key |
| `rate_limit` | VARCHAR(50) | Limite de requisições |
| `ativa` | BOOLEAN | Se está ativa |
| `prioridade` | INTEGER | Ordem de prioridade |
| `ultima_consulta` | TIMESTAMP | Última consulta realizada |
| `total_consultas` | INTEGER | Total de consultas |
| `total_erros` | INTEGER | Total de erros |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- UNIQUE: `nome`
- CHECK: `nome` pelo menos 2 caracteres
- CHECK: `prioridade` >= 1

**Índices:**
- `ix_fonte_dados_nome`
- `ix_fonte_dados_tipo_fonte`
- `ix_fonte_dados_ativa`
- `ix_fonte_dados_prioridade`
- `ix_fonte_dados_ultima_consulta`

---

### 10. RegraFiscal

**Descrição:** Regras de tributação (IR)

**Tabela:** `regra_fiscal`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `pais` | VARCHAR(2) | País (código ISO) |
| `tipo_ativo` | VARCHAR(50) | Tipo de ativo (ACAO, FII) |
| `tipo_operacao` | VARCHAR(50) | Tipo operação (SWING_TRADE, DAY_TRADE) |
| `aliquota_ir` | NUMERIC(5,4) | Alíquota de IR (%) |
| `valor_isencao` | NUMERIC(18,2) | Valor de isenção mensal |
| `incide_sobre` | ENUM | LUCRO, PROVENTO, OPERACAO |
| `descricao` | TEXT | Descrição da regra |
| `vigencia_inicio` | DATE | Início da vigência |
| `vigencia_fim` | DATE | Fim da vigência |
| `ativa` | BOOLEAN | Se regra está ativa |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- CHECK: `pais` formato ISO (2 letras)
- CHECK: `aliquota_ir` >= 0 AND <= 100
- CHECK: `valor_isencao` >= 0 (se informado)
- CHECK: `vigencia_fim` >= `vigencia_inicio` (se informado)

**Índices:**
- `ix_regra_fiscal_pais`
- `ix_regra_fiscal_tipo_ativo`
- `ix_regra_fiscal_tipo_operacao`
- `ix_regra_fiscal_incide_sobre`
- `ix_regra_fiscal_vigencia_inicio`
- `ix_regra_fiscal_vigencia_fim`
- `ix_regra_fiscal_ativa`

---

### 11. FeriadoMercado

**Descrição:** Feriados e dias sem pregão

**Tabela:** `feriado_mercado`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `pais` | VARCHAR(2) | País (código ISO) |
| `mercado` | VARCHAR(20) | Mercado/bolsa (B3, NYSE) |
| `data_feriado` | DATE | Data do feriado |
| `tipo_feriado` | ENUM | NACIONAL, BOLSA, ANTECIPADO, etc. |
| `nome` | VARCHAR(200) | Nome do feriado |
| `horario_fechamento` | TIME | Horário de fechamento (se antecipado) |
| `recorrente` | BOOLEAN | Se é feriado anual fixo |
| `observacoes` | TEXT | Observações |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**Constraints:**
- UNIQUE: `pais`, `mercado`, `data_feriado`
- CHECK: `pais` formato ISO
- CHECK: `nome` pelo menos 3 caracteres

**Índices:**
- `ix_feriado_mercado_pais`
- `ix_feriado_mercado_mercado`
- `ix_feriado_mercado_data_feriado`
- `ix_feriado_mercado_tipo_feriado`
- `ix_feriado_mercado_recorrente`

---

### 12. LogAuditoria

**Descrição:** Logs de auditoria para compliance

**Tabela:** `log_auditoria`

**Campos:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK - Identificador único |
| `usuario_id` | UUID | FK - Usuário que realizou ação |
| `acao` | VARCHAR(50) | Tipo de ação (LOGIN, CREATE, UPDATE, DELETE) |
| `entidade` | VARCHAR(100) | Entidade afetada (Usuario, Transacao) |
| `entidade_id` | UUID | ID do registro afetado |
| `dados_antes` | JSON | Estado anterior (UPDATE) |
| `dados_depois` | JSON | Estado posterior (UPDATE/CREATE) |
| `ip_address` | VARCHAR(45) | IP de origem |
| `user_agent` | VARCHAR(500) | Navegador/cliente |
| `timestamp` | TIMESTAMP | Data/hora da ação |
| `sucesso` | BOOLEAN | Se ação foi bem-sucedida |
| `mensagem` | TEXT | Mensagem de erro ou detalhes |

**Constraints:**
- FOREIGN KEY: `usuario_id` → `usuario.id` (SET NULL)
- CHECK: `acao` pelo menos 3 caracteres

**Índices:**
- `ix_log_auditoria_usuario_id`
- `ix_log_auditoria_acao`
- `ix_log_auditoria_entidade`
- `ix_log_auditoria_entidade_id`
- `ix_log_auditoria_timestamp`
- `ix_log_auditoria_sucesso`
- `ix_log_auditoria_ip_address`

---

## 🔗 Relacionamentos

### Diagrama de Relacionamentos

```
USUARIO (1) ─────┬───── (N) CORRETORA
                 │
                 ├───── (N) POSICAO
                 │
                 ├───── (N) TRANSACAO
                 │
                 ├───── (N) MOVIMENTACAO_CAIXA
                 │
                 └───── (N) LOG_AUDITORIA

CORRETORA (1) ───┬───── (N) POSICAO
                 │
                 ├───── (N) TRANSACAO
                 │
                 └───── (N) MOVIMENTACAO_CAIXA

ATIVO (1) ───────┬───── (N) POSICAO
                 │
                 ├───── (N) TRANSACAO
                 │
                 ├───── (N) PROVENTO
                 │
                 └───── (N) EVENTO_CORPORATIVO

PROVENTO (1) ──── (N) MOVIMENTACAO_CAIXA

EVENTO_CORPORATIVO ─── (1) ATIVO (ativo_novo_id, opcional)
```

### Políticas de DELETE

| Tabela Pai | Tabela Filha | Política |
|------------|--------------|----------|
| `usuario` | `corretora` | CASCADE |
| `usuario` | `posicao` | CASCADE |
| `usuario` | `transacao` | CASCADE |
| `usuario` | `movimentacao_caixa` | CASCADE |
| `usuario` | `log_auditoria` | SET NULL |
| `corretora` | `posicao` | CASCADE |
| `corretora` | `transacao` | CASCADE |
| `ativo` | `posicao` | RESTRICT |
| `ativo` | `transacao` | RESTRICT |
| `ativo` | `provento` | RESTRICT |
| `provento` | `movimentacao_caixa` | SET NULL |

---

## 🔢 Enums e Tipos

### 1. UserRole
```python
ADMIN = "admin"      # Administrador completo
USER = "user"        # Usuário normal
READONLY = "readonly" # Apenas leitura
```

### 2. TipoCorretora
```python
NACIONAL = "nacional"           # Corretora brasileira
INTERNACIONAL = "internacional" # Corretora estrangeira
```

### 3. TipoAtivo
```python
ACAO = "acao"               # Ação
FII = "fii"                 # Fundo Imobiliário
ETF = "etf"                 # Exchange Traded Fund
BDR = "bdr"                 # Brazilian Depositary Receipt
REIT = "reit"               # Real Estate Investment Trust
STOCK = "stock"             # Ação estrangeira
CRYPTO = "crypto"           # Criptomoeda
RENDA_FIXA = "renda_fixa"   # Título de renda fixa
OUTRO = "outro"             # Outros
```

### 4. ClasseAtivo
```python
RENDA_VARIAVEL = "renda_variavel"
RENDA_FIXA = "renda_fixa"
```

### 5. TipoOperacao
```python
COMPRA = "compra"
VENDA = "venda"
BONIFICACAO = "bonificacao"
SUBSCRICAO = "subscricao"
DESDOBRAMENTO = "desdobramento"
GRUPAMENTO = "grupamento"
```

### 6. TipoProvento
```python
DIVIDENDO = "dividendo"
JCP = "jcp"                    # Juros sobre Capital Próprio
RENDIMENTO = "rendimento"      # Rendimento de FII
BONUS = "bonus"
```

### 7. TipoMovimentacao
```python
DEPOSITO = "deposito"
SAQUE = "saque"
TRANSFERENCIA = "transferencia"
CREDITO_PROVENTO = "credito_provento"
DEBITO_TAXA = "debito_taxa"
```

### 8. TipoEventoCorporativo
```python
SPLIT = "split"               # Desdobramento
GRUPAMENTO = "grupamento"
BONIFICACAO = "bonificacao"
FUSAO = "fusao"
CISAO = "cisao"
INCORPORACAO = "incorporacao"
MUDANCA_TICKER = "mudanca_ticker"
```

### 9. TipoFonteDados
```python
API = "api"
SCRAPING = "scraping"
MANUAL = "manual"
ARQUIVO = "arquivo"
```

### 10. IncidenciaImposto
```python
LUCRO = "lucro"           # IR sobre ganho de capital
PROVENTO = "provento"     # IR sobre dividendos/JCP
OPERACAO = "operacao"     # IR sobre operação (day trade)
```

### 11. TipoFeriado
```python
NACIONAL = "nacional"
BOLSA = "bolsa"
PONTE = "ponte"
FECHAMENTO_ANTECIPADO = "antecip"
MANUTENCAO = "manutencao"
OUTRO = "outro"
```

---

## 📈 Índices e Performance

### Índices Principais por Tabela

**Total de índices:** 86

**Distribuição:**
- Índices em foreign keys: 15
- Índices em campos de busca: 35
- Índices em campos de data: 20
- Índices UNIQUE: 8
- Outros índices: 8

### Estratégias de Indexação

1. **Foreign Keys:** Todas possuem índice automático
2. **Campos de Busca Frequente:** `ticker`, `username`, `email`, `nome`
3. **Campos de Filtro:** `ativo`, `tipo`, `mercado`, `pais`
4. **Campos de Ordenação:** `data_operacao`, `timestamp`, `prioridade`
5. **Campos UNIQUE:** `username`, `email`, `ticker+mercado`

### Queries Otimizadas

Todos os relacionamentos e buscas frequentes estão cobertos por índices.

---

## 💡 Queries Úteis

### 1. Listar todas as tabelas
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema='public' 
AND table_type='BASE TABLE'
ORDER BY table_name;
```

### 2. Ver estrutura de uma tabela
```sql
\d+ usuario
```

### 3. Ver todos os enums
```sql
SELECT typname, enumlabel
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typtype = 'e'
ORDER BY typname, enumsortorder;
```

### 4. Ver todas as foreign keys
```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

### 5. Ver todos os índices
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### 6. Estatísticas de tabelas
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 7. Buscar ativos por ticker
```sql
SELECT ticker, nome, tipo, mercado, preco_atual
FROM ativo
WHERE ticker ILIKE '%PETR%'
AND ativo = true
ORDER BY ticker;
```

### 8. Carteira consolidada de um usuário
```sql
SELECT
    a.ticker,
    a.nome,
    p.quantidade,
    p.preco_medio,
    p.valor_investido,
    a.preco_atual,
    (a.preco_atual * p.quantidade) AS valor_atual,
    ((a.preco_atual * p.quantidade) - p.valor_investido) AS lucro_prejuizo
FROM posicao p
JOIN ativo a ON p.ativo_id = a.id
WHERE p.usuario_id = 'uuid-do-usuario'
AND p.quantidade > 0
ORDER BY p.valor_investido DESC;
```

### 9. Histórico de transações
```sql
SELECT
    t.data_operacao,
    a.ticker,
    t.tipo_operacao,
    t.quantidade,
    t.preco_unitario,
    t.custos_operacao,
    (t.quantidade * t.preco_unitario + t.custos_operacao) AS valor_total
FROM transacao t
JOIN ativo a ON t.ativo_id = a.id
WHERE t.usuario_id = 'uuid-do-usuario'
ORDER BY t.data_operacao DESC
LIMIT 50;
```

### 10. Proventos recebidos no mês
```sql
SELECT
    a.ticker,
    p.tipo_provento,
    p.data_pagamento,
    p.valor_total,
    p.imposto_retido,
    (p.valor_total - p.imposto_retido) AS valor_liquido
FROM provento p
JOIN ativo a ON p.ativo_id = a.id
WHERE DATE_TRUNC('month', p.data_pagamento) = DATE_TRUNC('month', CURRENT_DATE)
ORDER BY p.data_pagamento DESC;
```

---

## 📐 Diagrama ER

### Diagrama Textual Completo

```
┌─────────────────────┐
│      USUARIO        │
├─────────────────────┤
│ id (PK)            │
│ username (UQ)      │
│ email (UQ)         │
│ password_hash      │
│ role               │
└──────────┬──────────┘
           │
           │ 1:N
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│     CORRETORA       │  │      POSICAO        │
├─────────────────────┤  ├─────────────────────┤
│ id (PK)            │  │ id (PK)            │
│ usuario_id (FK)    │  │ usuario_id (FK)    │
│ nome               │  │ corretora_id (FK)  │
│ tipo               │  │ ativo_id (FK)      │
│ pais               │  │ quantidade         │
└──────────┬──────────┘  └──────────┬──────────┘
           │                        │
           │                        │
           ├────────────────────────┤
           │                        │
           ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐
│     TRANSACAO       │  │       ATIVO         │
├─────────────────────┤  ├─────────────────────┤
│ id (PK)            │  │ id (PK)            │
│ usuario_id (FK)    │  │ ticker (UQ)        │
│ corretora_id (FK)  │  │ nome               │
│ ativo_id (FK)      │  │ tipo               │
│ tipo_operacao      │  │ mercado            │
│ quantidade         │  │ preco_atual        │
│ preco_unitario     │  └──────────┬──────────┘
└─────────────────────┘             │
                                    │ 1:N
                        ┌───────────┼───────────┐
                        │           │           │
                        ▼           ▼           ▼
              ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
              │   PROVENTO   │ │ MOVIMENTACAO │ │ EVENTO_          │
              │              │ │    _CAIXA    │ │ CORPORATIVO      │
              ├──────────────┤ ├──────────────┤ ├──────────────────┤
              │ id (PK)     │ │ id (PK)     │ │ id (PK)         │
              │ ativo_id(FK)│ │ usuario_id  │ │ ativo_id (FK)   │
              │ tipo        │ │ corretora   │ │ tipo_evento     │
              │ valor       │ │ provento_id │ │ proporcao       │
              └──────────────┘ └──────────────┘ └──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    TABELAS DE REFERÊNCIA                     │
├─────────────────────────────────────────────────────────────┤
│  FONTE_DADOS   │  REGRA_FISCAL  │  FERIADO_MERCADO          │
│  LOG_AUDITORIA │                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Boas Práticas

### 1. Uso de UUIDs

Todas as PKs são UUIDs para:
- Evitar exposição de IDs sequenciais
- Facilitar merge de bancos
- Segurança adicional

### 2. Timestamps

Todas as tabelas têm `created_at` e `updated_at` para auditoria.

### 3. Soft Delete

Tabelas principais usam flag `ativo` ao invés de DELETE físico.

### 4. Constraints

Uso extensivo de:
- CHECK constraints para validação
- UNIQUE constraints para integridade
- Foreign keys com políticas apropriadas

### 5. Índices

Índices em:
- Todas as foreign keys
- Campos de busca frequente
- Campos de ordenação
- Campos de filtro

### 6. Normalização

Banco normalizado (3FN) com desnormalizações estratégicas:
- `preco_atual` em `ativo` (cache)
- `valor_total` em `provento` (calculado)

### 7. Tipos de Dados

- `NUMERIC` para valores monetários (evita erros de arredondamento)
- `DATE` para datas puras
- `TIMESTAMP` para data+hora
- `VARCHAR` com limites apropriados
- `TEXT` para campos sem limite
- `BOOLEAN` para flags
- `JSON` para dados semi-estruturados

### 8. Nomenclatura

- Tabelas: singular, snake_case
- Colunas: snake_case
- Enums: UPPERCASE
- Foreign keys: `<tabela>_id`

---

## 🔒 Segurança

### 1. Senhas

- Armazenadas com hash bcrypt
- Nunca expor `password_hash` em APIs

### 2. SQL Injection

- Uso exclusivo de ORM (SQLAlchemy)
- Queries parametrizadas

### 3. Auditoria

- Tabela `log_auditoria` registra todas as ações
- IP e user-agent salvos

### 4. Roles

- Sistema de permissões baseado em roles
- ADMIN, USER, READONLY

---

## 📊 Performance

### Otimizações Implementadas

1. ✅ Índices em foreign keys
2. ✅ Índices em campos de busca
3. ✅ Índices compostos quando necessário
4. ✅ Connection pooling (SQLAlchemy)
5. ✅ Lazy loading de relacionamentos
6. ✅ Eager loading quando apropriado (joined)

### Monitoramento

```sql
-- Ver queries lentas
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Ver tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🎯 Conclusão

O banco de dados do Exitus foi projetado para:

✅ **Escalabilidade:** Suporta milhões de registros  
✅ **Performance:** Índices e queries otimizadas  
✅ **Integridade:** Constraints e foreign keys  
✅ **Auditoria:** Log completo de ações  
✅ **Segurança:** Hashing, roles, validações  
✅ **Manutenibilidade:** Código limpo e documentado  

---

**Versão:** 1.0  
**Data:** Novembro 2025  
**Autor:** Equipe Exitus
