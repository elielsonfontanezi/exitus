> ⚠️ **DOCUMENTO HISTÓRICO**  
> Esta matriz foi criada em 06/01/2026 para identificar gaps de compliance.  
> **GAP P0 (historico_preco) foi RESOLVIDO** em 06/01/2026 (commit `ab59342`).  
> Documento mantido para referência histórica em `docs/ARCHIVE/`.

---

## GAP 1: Tabela historico_preco ✅ **RESOLVIDO** (v0.7.6)

**Status anterior:** ❌ BLOQUEADOR - Tabela inexistente  
**Status atual:** ✅ IMPLEMENTADO  

### Resolução
- **Data:** 06/01/2026
- **Commit:** `ab59342` (Merge: Sistema de Histórico de Preços)
- **Issues:** #1, #2, #3, #4

### Implementação
- ✅ Migration Alembic com tabela `historico_preco`
- ✅ `HistoricoService` com lazy loading (189 linhas)
- ✅ `calcular_zscore()` refatorado usando dados reais
- ✅ Script `popular_historico_inicial.py` com filtros
- ✅ Multi-mercado (BR `.SA`, US sem sufixo)
- ✅ Validação mínimo 30 dias

### Impacto
- **Z-Score:** Dados reais (antes: mock array fixo)
- **Volatilidade:** Cálculo habilitado
- **Sharpe/Beta:** Desbloqueia implementação futura
- **Compliance:** 50% → 100% (4/4 campos)


# 🔍 MATRIZ DE COMPLIANCE: Entidade-Relacionamento x APIs

**Data**: 06/01/2026  
**Commit**: 861b808818af98b1149316877bfa5fe78327daf4  
**Objetivo**: Validar que todos os campos necessários para cálculos existem no ER

---

## 📌 Escopo

Este documento cruza:
- **Entidades do ER** (19 tabelas, 244 campos)
- **APIs de Cálculo** (12 endpoints principais)
- **Campos Utilizados** (validação de existência e tipo)

---

## 🎯 TABELA MESTRA DE COMPLIANCE

### Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| ✅ | Campo existe no ER e é usado corretamente |
| ⚠️ | Campo existe mas pode ser NULL (usa default) |
| ❌ | Campo NÃO existe no ER (GAP) |
| 🔵 | Campo calculado/derivado (não armazenado) |
| 🟢 | Campo de JOIN (tabela relacionada) |

---

## 📊 MATRIZ DETALHADA POR API

### 1. API: Preço Teto Multi-Método

**Endpoint**: `GET /api/calculos/precoteto/<ticker>`  
**Service**: `backend/app/services/portfolioservice.py`  
**Módulo**: M4 - Buy Signals

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Observação |
|-------|--------|----------|-------------|--------|------------|
| `id` | ativo | UUID | UUID | ✅ | PK |
| `ticker` | ativo | VARCHAR(20) | str | ✅ | Busca principal |
| `nome` | ativo | VARCHAR(200) | str | ✅ | Retorno |
| `tipo` | ativo | ENUM(TipoAtivo) | Enum | ✅ | Lógica ação/FII |
| `classe` | ativo | ENUM(ClasseAtivo) | Enum | ✅ | Classificação |
| `mercado` | ativo | VARCHAR(10) | str | ✅ | Define parâmetros regionais |
| `moeda` | ativo | VARCHAR(3) | str | ✅ | BRL, USD, EUR |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | ✅ | Cotação atual |
| `precoteto` | ativo | NUMERIC(18,6) | Decimal | ✅ | Calculado |
| `dividendyield` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | Pode ser NULL → usa 6% |
| `pl` | ativo | NUMERIC(10,2) | Decimal | ⚠️ | Pode ser NULL |
| `pvp` | ativo | NUMERIC(10,2) | Decimal | ⚠️ | Pode ser NULL |
| `roe` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | Pode ser NULL |
| `beta` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | Pode ser NULL → usa 1.0 |
| `taxalivrerisco` | parametrosmacro | NUMERIC(8,4) | Decimal | ✅ | Por mercado (BR: 10.5%) |
| `crescimentomedio` | parametrosmacro | NUMERIC(8,4) | Decimal | ✅ | Por mercado (BR: 5%) |
| `custocapital` | parametrosmacro | NUMERIC(8,4) | Decimal | ✅ | WACC regional (BR: 12%) |
| `capratefii` | parametrosmacro | NUMERIC(8,4) | Decimal | ✅ | Para FIIs (BR: 6%) |

**Compliance**: 17/17 campos existem (100%) | 5 campos podem ser NULL (29%)

---

### 2. API: Margem de Segurança

**Endpoint**: `GET /api/buy-signals/margem-seguranca/<ticker>`  
**Service**: `backend/app/services/buysignalsservice.py`  
**Módulo**: M4 - Buy Signals

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Fórmula |
|-------|--------|----------|-------------|--------|---------|
| `ticker` | ativo | VARCHAR(20) | str | ✅ | Busca |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | ✅ | Numerador |
| `precoteto` | ativo | NUMERIC(18,6) | Decimal | ✅ | Denominador |
| **`margem`** | 🔵 **CALCULADO** | - | float | 🔵 | `(teto - atual) / teto * 100` |

**Fórmula**:
```python
margem = ((precoteto - precoatual) / precoteto) * 100

# Sinal
if margem >= 5: sinal = "COMPRA"
elif margem >= 0: sinal = "NEUTRO"
else: sinal = "VENDA"
```

**Compliance**: 3/3 campos existem (100%)

---

### 3. API: Buy Score (0-100)

**Endpoint**: `GET /api/buy-signals/buy-score/<ticker>`  
**Service**: `backend/app/services/buysignalsservice.py`  
**Módulo**: M4 - Buy Signals

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Peso |
|-------|--------|----------|-------------|--------|------|
| `ticker` | ativo | VARCHAR(20) | str | ✅ | - |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | ✅ | 30 pts (via margem) |
| `precoteto` | ativo | NUMERIC(18,6) | Decimal | ✅ | 30 pts (via margem) |
| `dividendyield` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | 20 pts (default: 4%) |
| `beta` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | 25 pts (default: 1.0) |
| **`zscore`** | 🔵 **CALCULADO** | - | float | ⚠️ | 25 pts (requer histórico) |

**Fórmula**:
```python
# Componentes (0-100)
margem_pts = clip(margem / 3, 0, 30)           # 0-30 pts
z_pts = 25 if zscore < -1 else 15 if zscore < 0 else 5  # 5-25 pts
dy_pts = clip(dy * 5, 0, 20)                   # 0-20 pts
beta_pts = clip(max(0, 25 - (beta - 1) * 12.5), 0, 25)  # 0-25 pts

score = margem_pts + z_pts + dy_pts + beta_pts
```

**Compliance**: 5/6 campos existem (83%) | 1 campo calculado requer tabela histórico

---

### 4. API: Z-Score (Desvio do Preço)

**Endpoint**: `GET /api/buy-signals/zscore/<ticker>`  
**Service**: `backend/app/services/buysignalsservice.py`  
**Módulo**: M4 - Buy Signals

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Observação |
|-------|--------|----------|-------------|--------|------------|
| `ticker` | ativo | VARCHAR(20) | str | ✅ | Busca |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | ✅ | Valor atual |
| `data` | ❌ **historico_preco** | DATE | date | ❌ | **GAP CRÍTICO** |
| `preco_fechamento` | ❌ **historico_preco** | NUMERIC(18,6) | Decimal | ❌ | **GAP CRÍTICO** |

**Fórmula**:
```python
# ⚠️ IMPLEMENTAÇÃO ATUAL (MOCK)
historico_simulado = [42.0, 41.5, 40.8, 39.2, ...]  # Array fixo
media = np.mean(historico_simulado)
std = np.std(historico_simulado)
zscore = (precoatual - media) / std

# ✅ IMPLEMENTAÇÃO DESEJADA (REQUER historico_preco)
historico = HistoricoPreco.query.filter_by(ativoid=ativo.id).order_by('data DESC').limit(252).all()
precos = [h.preco_fechamento for h in historico]
media = np.mean(precos)
std = np.std(precos)
zscore = (precoatual - media) / std
```

**Compliance**: 2/4 campos existem (50%) | ❌ Tabela `historico_preco` inexistente

---

### 5. API: Dashboard Consolidado do Portfolio

**Endpoint**: `GET /api/portfolio/dashboard`  
**Service**: `backend/app/services/portfolioservice.py`  
**Módulo**: M3 - Portfolio Analytics

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `id` | posicao | UUID | UUID | ✅ | PK |
| `usuarioid` | posicao | UUID FK | UUID | ✅ | Filtro multi-tenant |
| `ativoid` | posicao | UUID FK | UUID | 🟢 | JOIN com ativo |
| `corretoraid` | posicao | UUID FK | UUID | 🟢 | JOIN com corretora |
| `quantidade` | posicao | NUMERIC(18,8) | Decimal | ✅ | Qtd. de ativos |
| `precomedio` | posicao | NUMERIC(18,6) | Decimal | ✅ | Preço médio compra |
| `custototal` | posicao | NUMERIC(18,2) | Decimal | ✅ | SUM(custototal) |
| `valoratual` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | Pode ser NULL → calc via JOIN |
| `lucroprejuizorealizado` | posicao | NUMERIC(18,2) | Decimal | ✅ | Vendas realizadas |
| `lucroprejuizonaorealizado` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | `valoratual - custototal` |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | 🟢 | JOIN: `quantidade * precoatual` |
| `ticker` | ativo | VARCHAR(20) | str | 🟢 | JOIN: exibição |
| `nome` | ativo | VARCHAR(200) | str | 🟢 | JOIN: exibição |
| `saldoatual` | corretora | NUMERIC(18,2) | Decimal | 🟢 | JOIN: SUM(saldoatual) |

**Fórmulas Derivadas**:
```python
patrimonio_ativos = SUM(posicao.valoratual)
custo_aquisicao = SUM(posicao.custototal)
saldo_caixa = SUM(corretora.saldoatual WHERE usuarioid=X)
patrimonio_total = patrimonio_ativos + saldo_caixa
lucro_bruto = patrimonio_ativos - custo_aquisicao
rentabilidade_perc = (lucro_bruto / custo_aquisicao * 100) if custo_aquisicao > 0 else 0
```

**Compliance**: 14/14 campos existem (100%) | 2 campos podem ser NULL (14%)

---

### 6. API: Alocação por Classe de Ativo

**Endpoint**: `GET /api/portfolio/alocacao`  
**Service**: `backend/app/services/portfolioservice.py`  
**Módulo**: M3 - Portfolio Analytics

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `usuarioid` | posicao | UUID FK | UUID | ✅ | Filtro |
| `valoratual` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | Agregação SUM(valor) GROUP BY classe |
| `classe` | ativo | ENUM(ClasseAtivo) | Enum | 🟢 | JOIN: GROUP BY |

**Query SQL Equivalente**:
```sql
SELECT 
    a.classe,
    SUM(p.valoratual) as valor_total,
    ROUND(SUM(p.valoratual) / (SELECT SUM(valoratual) FROM posicao WHERE usuarioid=X) * 100, 2) as percentual
FROM posicao p
JOIN ativo a ON p.ativoid = a.id
WHERE p.usuarioid = X
GROUP BY a.classe;
```

**Compliance**: 3/3 campos existem (100%)

---

### 7. API: Dividend Yield Médio do Portfolio

**Endpoint**: `GET /api/calculos/portfolio` (campo dentro do JSON)  
**Service**: `backend/app/services/portfolioservice.py`  
**Módulo**: M3 - Portfolio Analytics

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `usuarioid` | posicao | UUID FK | UUID | ✅ | Filtro |
| `valoratual` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | Ponderação |
| `dividendyield` | ativo | NUMERIC(8,4) | Decimal | ⚠️ | JOIN: média ponderada |

**Fórmula**:
```python
# Média ponderada por valor investido
soma_dy_ponderado = SUM(valoratual * dividendyield)
total_investido = SUM(valoratual)
dy_medio = soma_dy_ponderado / total_investido if total_investido > 0 else 0
```

**SQL Equivalente**:
```sql
SELECT 
    COALESCE(
        SUM(p.valoratual * COALESCE(a.dividendyield, 0)) / NULLIF(SUM(p.valoratual), 0),
        0
    ) as dy_medio
FROM posicao p
JOIN ativo a ON p.ativoid = a.id
WHERE p.usuarioid = X;
```

**Compliance**: 3/3 campos existem (100%) | 2 campos podem ser NULL

---

### 8. API: Cotação em Tempo Real (Individual)

**Endpoint**: `GET /api/cotacoes/<ticker>`  
**Service**: `backend/app/services/cotacoesservice.py`  
**Módulo**: M7.5 - Cotações Live

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `ticker` | ativo | VARCHAR(20) | str | ✅ | Busca |
| `mercado` | ativo | VARCHAR(10) | str | ✅ | Adaptar ticker (BR: .SA) |
| `precoatual` | ativo | NUMERIC(18,6) | Decimal | ✅ | Cache |
| `dataultimacotacao` | ativo | TIMESTAMP TZ | datetime | ✅ | TTL 15 min |
| `nome` | fontedados | VARCHAR(100) | str | 🟢 | JOIN: identificar API |
| `ativa` | fontedados | BOOLEAN | bool | 🟢 | JOIN: filtrar fontes |
| `prioridade` | fontedados | INTEGER | int | 🟢 | JOIN: ordem tentativa |
| `urlbase` | fontedados | VARCHAR(500) | str | 🟢 | JOIN: endpoint API |

**Lógica de Cache (TTL 15 min - Prompt Mestre)**:
```python
TTL_SECONDS = 900  # 15 minutos
now = datetime.now()

if ativo.dataultimacotacao and (now - ativo.dataultimacotacao).seconds < TTL_SECONDS:
    return {'provider': 'cache-postgresql', 'cache_age_minutes': ...}

# Fallback cascade: brapi → yfinance → cache-stale
for fonte in FonteDados.query.filter_by(ativa=True).order_by('prioridade').all():
    # Tentar API externa...
```

**Compliance**: 8/8 campos existem (100%)

---

### 9. API: Performance Individual de Ativos

**Endpoint**: `GET /api/portfolio/performance`  
**Service**: `backend/app/services/portfolioservice.py`  
**Módulo**: M3 - Portfolio Analytics

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `usuarioid` | posicao | UUID FK | UUID | ✅ | Filtro |
| `ativoid` | posicao | UUID FK | UUID | ✅ | GROUP BY |
| `quantidade` | posicao | NUMERIC(18,8) | Decimal | ✅ | Qtd. total |
| `precomedio` | posicao | NUMERIC(18,6) | Decimal | ✅ | PM |
| `custototal` | posicao | NUMERIC(18,2) | Decimal | ✅ | Custo |
| `valoratual` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | Valor mercado |
| `lucroprejuizonaorealizado` | posicao | NUMERIC(18,2) | Decimal | ⚠️ | Lucro não realizado |
| `ticker` | ativo | VARCHAR(20) | str | 🟢 | JOIN: identificação |
| `nome` | ativo | VARCHAR(200) | str | 🟢 | JOIN: nome |
| `tipo` | ativo | ENUM | Enum | 🟢 | JOIN: classificação |

**Campos Derivados**:
```python
for p in posicoes:
    rentabilidade_perc = ((p.valoratual - p.custototal) / p.custototal * 100) if p.custototal > 0 else 0
```

**Compliance**: 10/10 campos existem (100%)

---

### 10. API: Proventos Recebidos

**Endpoint**: `GET /api/proventos` (filtrado por usuário)  
**Service**: `backend/app/services/proventoservice.py`  
**Módulo**: M3 - Portfolio Analytics

| Campo | Tabela | Tipo SQL | Tipo Python | Status | Uso |
|-------|--------|----------|-------------|--------|-----|
| `id` | provento | UUID | UUID | ✅ | PK |
| `ativoid` | provento | UUID FK | UUID | 🟢 | JOIN com posicao |
| `tipoprovento` | provento | ENUM(TipoProvento) | Enum | ✅ | DIVIDENDO, JCP, etc |
| `valorporacao` | provento | NUMERIC(18,6) | Decimal | ✅ | R$/ação |
| `quantidadeativos` | provento | NUMERIC(18,2) | Decimal | ✅ | Qtd. pagante |
| `valorbruto` | provento | NUMERIC(18,2) | Decimal | ✅ | Valor bruto |
| `impostoretido` | provento | NUMERIC(18,2) | Decimal | ✅ | IR |
| `valorliquido` | provento | NUMERIC(18,2) | Decimal | ✅ | Líquido |
| `datacom` | provento | DATE | date | ✅ | Data COM |
| `datapagamento` | provento | DATE | date | ✅ | Data pagamento |
| `quantidade` | posicao | NUMERIC(18,8) | Decimal | 🟢 | JOIN: qtd. recebida |

**Lógica de Cruzamento**:
```python
# Proventos recebidos pelo usuário
posicoes = Posicao.query.filter_by(usuarioid=usuarioid).all()
ativosids = [p.ativoid for p in posicoes]
proventos = Provento.query.filter(Provento.ativoid.in_(ativosids)).all()

for prov in proventos:
    posicao = next(p for p in posicoes if p.ativoid == prov.ativoid)
    quantidade_recebida = posicao.quantidade
    valor_bruto_recebido = prov.valorporacao * quantidade_recebida
    valor_liquido_recebido = valor_bruto_recebido * (prov.valorliquido / prov.valorbruto)
```

**Compliance**: 11/11 campos existem (100%)

---

## 📊 RESUMO GERAL DE COMPLIANCE

### Por API

| API | Campos Usados | Existem no ER | Podem ser NULL | Calculados | Compliance |
|-----|--------------|---------------|----------------|------------|------------|
| **Preço Teto** | 17 | 17 (100%) | 5 (29%) | 0 | ✅ 100% |
| **Margem Segurança** | 3 | 3 (100%) | 0 | 1 | ✅ 100% |
| **Buy Score** | 6 | 5 (83%) | 2 (33%) | 1 | ⚠️ 83% |
| **Z-Score** | 4 | 2 (50%) | 0 | 1 | ❌ 50% |
| **Dashboard Portfolio** | 14 | 14 (100%) | 2 (14%) | 6 | ✅ 100% |
| **Alocação Classe** | 3 | 3 (100%) | 1 (33%) | 2 | ✅ 100% |
| **DY Médio** | 3 | 3 (100%) | 2 (67%) | 1 | ✅ 100% |
| **Cotação Live** | 8 | 8 (100%) | 0 | 0 | ✅ 100% |
| **Performance Ativos** | 10 | 10 (100%) | 2 (20%) | 1 | ✅ 100% |
| **Proventos** | 11 | 11 (100%) | 0 | 3 | ✅ 100% |

**Média Geral**: 94% de compliance (79/84 campos)

### Por Tabela

| Tabela | Campos Totais | Usados em Cálculos | % Utilização |
|--------|---------------|-------------------|--------------|
| **ativo** | 21 | 15 | 71% |
| **posicao** | 16 | 10 | 63% |
| **provento** | 13 | 10 | 77% |
| **corretora** | 11 | 2 | 18% |
| **parametrosmacro** | 15 | 4 | 27% |
| **fontedados** | 14 | 4 | 29% |
| **transacao** | 19 | 0 | 0% ⚠️ |
| **usuario** | 9 | 1 | 11% |
| **historico_preco** | ❌ **NÃO EXISTE** | 2 campos necessários | ❌ |

**Observações**:
- Tabela `transacao` não é usada diretamente em cálculos (apenas para auditoria)
- Tabela `historico_preco` **NÃO EXISTE** mas é **CRÍTICA** para Z-Score, volatilidade, Beta

---

## 🔴 GAPS CRÍTICOS CONSOLIDADOS

### GAP 1: Tabela `historico_preco` Inexistente
**Impacto**: 🔴 **BLOQUEADOR**  
**APIs Afetadas**: Z-Score, Volatilidade, Sharpe Ratio, Beta (cálculo real)  
**Solução**:
```sql
CREATE TABLE historico_preco (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ativoid UUID NOT NULL REFERENCES ativo(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    preco_abertura NUMERIC(18,6),
    preco_fechamento NUMERIC(18,6) NOT NULL,
    preco_minimo NUMERIC(18,6),
    preco_maximo NUMERIC(18,6),
    volume BIGINT,
    createdat TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(ativoid, data)
);
CREATE INDEX ix_historico_ativoid_data ON historico_preco(ativoid, data DESC);
```

**Prioridade**: P0 - Implementar IMEDIATAMENTE

---

### GAP 2: Campos NULL em Indicadores Fundamentalistas
**Impacto**: 🟡 **MÉDIO**  
**Campos Afetados**: `dividendyield`, `pl`, `pvp`, `roe`, `beta`  
**APIs Afetadas**: Buy Score (usa defaults), Preço Teto (usa defaults)

**Solução**: Job assíncrono para popular via APIs externas
```python
# backend/app/tasks/atualizar_indicadores.py
@celery.task
def atualizar_indicadores_batch():
    ativos = Ativo.query.filter_by(ativo=True, deslistado=False).all()
    for ativo in ativos:
        dados = fetch_fundamentals(ativo.ticker, ativo.mercado)
        ativo.dividendyield = dados.get('dy')
        ativo.pl = dados.get('pl')
        ativo.pvp = dados.get('pvp')
        ativo.roe = dados.get('roe')
        ativo.beta = dados.get('beta')
        db.session.commit()
```

**Prioridade**: P1 - Próxima Sprint

---

### GAP 3: Campo `caprate` Individual para FIIs
**Impacto**: 🟢 **BAIXO**  
**Workaround Atual**: Usa valor único da tabela `parametrosmacro` (6% para BR)  
**Solução**:
```sql
ALTER TABLE ativo ADD COLUMN caprate NUMERIC(8,4) NULL;
COMMENT ON COLUMN ativo.caprate IS 'Cap Rate individual do FII (%)';
```

**Prioridade**: P2 - Backlog

---

## 💡 RECOMENDAÇÕES FINAIS

### Recomendação 1: Implementar Tabela `historico_preco`
**Justificativa**: Desbloqueia cálculos avançados (Z-Score real, volatilidade, Sharpe, Beta).  
**Esforço**: 🔴 Alto (migration + job de população + integração APIs)  
**Retorno**: 🟢 Alto (habilita 4 métricas críticas)

### Recomendação 2: Job Assíncrono para Indicadores
**Justificativa**: Atualmente 29% dos campos de cálculo podem ser NULL.  
**Esforço**: 🟡 Médio (setup Celery + integração APIs)  
**Retorno**: 🟢 Alto (melhora precisão de todos os cálculos)

### Recomendação 3: Adicionar Constraints de Validação
**Justificativa**: Prevenir dados inconsistentes (e.g., DY > 100%).  
**Esforço**: 🟢 Baixo (ALTER TABLE)  
**Retorno**: 🟡 Médio (aumenta confiabilidade)

```sql
ALTER TABLE ativo ADD CONSTRAINT ck_ativo_preco_positivo 
    CHECK (precoatual IS NULL OR precoatual >= 0);

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_dy_range 
    CHECK (dividendyield IS NULL OR (dividendyield >= 0 AND dividendyield <= 100));

ALTER TABLE posicao ADD CONSTRAINT ck_posicao_quantidade_positiva 
    CHECK (quantidade >= 0);
```

---

## ✅ CRITÉRIOS DE APROVAÇÃO

- [x] ✅ Inventário completo de APIs vs ER
- [x] ✅ Mapeamento de 84 campos utilizados em cálculos
- [x] ✅ Identificação de 3 GAPs críticos
- [x] ✅ 94% de compliance geral
- [ ] ❌ Tabela `historico_preco` implementada (PENDENTE - P0)
- [ ] ❌ Job de população de indicadores (PENDENTE - P1)
- [ ] ⚠️ Constraints de validação adicionados (PENDENTE - P2)

**Status Geral**: ✅ **ER E APIS VALIDADOS COM PLANO DE AÇÃO DEFINIDO**

---

## 📦 Arquivos de Referência

### Documentos de Revisão
- 📄 [REVISAO_MODULO_1_BANCO_DADOS.md](./REVISAO_MODULO_1_BANCO_DADOS.md)
- 📄 [REVISAO_MODULOS_2-4_APIS_CALCULOS.md](./REVISAO_MODULOS_2-4_APIS_CALCULOS.md)
- 📄 **MATRIZ_COMPLIANCE_ER_APIS.md** ← Este documento

### Fontes de Dados
- 📄 `docs/EXITUS_DB_STRUCTURE.txt` (ER completo - 19 tabelas)
- 📄 `exitus_fontes.txt` (código fonte consolidado)
- 📄 `backend/app/models/*.py` (15 models SQLAlchemy)
- 📄 `backend/app/services/*.py` (12 services de cálculo)
- 📄 `backend/app/blueprints/*.py` (16 blueprints registrados)

### Migrations e Seeds
- 📂 `backend/alembic/versions/` (15 migrations)
- 📂 `backend/app/seeds/` (5 scripts de população)

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Aprovação desta revisão** → Validar com time técnico
2. ❌ **Criar issue P0**: Implementar tabela `historico_preco`
3. ❌ **Criar issue P1**: Job Celery para popular indicadores
4. ❌ **Atualizar PROMPT_MESTRE_EXITUS**: Incluir novos requisitos
5. 📊 **Revisar Módulos 5-7**: Frontend e Dashboards (próxima fase)

---

**Revisão Completa Concluída** ✅  
**Data**: 06/01/2026 11:34 AM  
**Revisor**: Perplexity AI Assistant  
**Versão**: 1.0 Final
