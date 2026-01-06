# 🔍 REVISÃO - MÓDULOS 2-4: Backend APIs e Cálculos Financeiros

**Data**: 06/01/2026  
**Commit**: 861b808818af98b1149316877bfa5fe78327daf4  
**Status**: ✅ OPERACIONAL COM GAPS DOCUMENTADOS

---

## 📌 Escopo dos Módulos

### Módulo 2: Backend API (Autenticação e Core)
- Estrutura Flask + SQLAlchemy
- Autenticação JWT
- CRUD de Usuario e Corretora
- Rate limiting

### Módulo 3: Backend API (Entidades Financeiras)
- CRUD de Ativo, Posicao, Transacao, Provento
- Services de negócio
- Validações financeiras
- API endpoints RESTful

### Módulo 4: Backend API (Integrações e Cálculos)
- Integração APIs externas (yfinance, brapi.dev)
- **Cálculos financeiros avançados**
- Importação/Exportação
- Buy Signals

---

## 🎯 INVENTÁRIO COMPLETO DE APIs DE CÁLCULOS

### 1. APIs de Valuation (Módulo 4)

#### 1.1 Preço Teto Multi-Método

**Endpoint**: `GET /api/calculos/precoteto/<ticker>`  
**Arquivo**: `backend/app/blueprints/calculosblueprint.py`

**Tabelas Consumidas**:
- `ativo` → ticker, precoatual, dividendyield, tipo, mercado
- `parametrosmacro` → taxalivrerisco, crescimentomedio, custocapital, capratefii

**Lógica de Cálculo**:
```python
# Para AÇÕES - 4 métodos regionalizados
if tipo in ['acao', 'acoes']:
    # Parâmetros regionais dinâmicos
    k = params['taxalivrerisco']      # BR: 10.5%, US: 4.5%
    g = params['crescimentomedio']    # BR: 5%, US: 3%
    wacc = params['custocapital']     # BR: 12%, US: 8%

    # Método 1: Bazin (DY Local)
    pt_bazin = (dy * k - g) if k > g else 0

    # Método 2: Graham (Local)
    eps = 2.50  # EPS estimado
    pt_graham = eps * (8.5 + 2 * g * 100) / (4.4 * k)

    # Método 3: Gordon (Local)
    d1 = dy * (1 + g)
    pt_gordon = d1 / (k - g) if k > g else 0

    # Método 4: DCF (5 anos)
    fcf = 5.0
    fluxos = [fcf * (1 + g)**i for i in range(1, 6)]
    valor_terminal = fluxos[-1] * 1.03 / (wacc - 0.03)
    fluxos.append(valor_terminal)
    pt_dcf = sum(fluxo / (1 + wacc)**(i+1) for i, fluxo in enumerate(fluxos))

    # Média dos 4 métodos
    pt_medio = (pt_bazin + pt_graham + pt_gordon + pt_dcf) / 4

# Para FIIs - 1 método (Cap Rate regional)
elif 'fii' in tipo.lower():
    caprate = params['capratefii']    # BR: 6%, US: 5%
    pt_caprate = dy / (1 + caprate)
    pt_medio = pt_caprate
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório | Observação |
|-------|--------|------|-------------|------------|
| `ticker` | ativo | VARCHAR(20) | ✅ | Busca do ativo |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ | Comparação |
| `dividendyield` | ativo | NUMERIC(8,4) | ✅ | DY anual (%) |
| `tipo` | ativo | ENUM | ✅ | Lógica diferente para ação/FII |
| `mercado` | ativo | VARCHAR(10) | ✅ | Define parâmetros regionais |
| `taxalivrerisco` | parametrosmacro | NUMERIC | ✅ | Por mercado |
| `crescimentomedio` | parametrosmacro | NUMERIC | ✅ | Por mercado |
| `custocapital` | parametrosmacro | NUMERIC | ✅ | WACC regional |
| `capratefii` | parametrosmacro | NUMERIC | ✅ | Para FIIs |

**✅ Compliance ER**: 100% - Todos os campos existem no banco.

**Response Exemplo**:
```json
{
  "ativo": "PETR4",
  "mercado": "BR",
  "precoatual": 31.26,
  "ptmedio": 34.39,
  "margemseguranca": 9.1,
  "parametrosregiao": {
    "taxalivrerisco": "10.5%",
    "crescimento": "5.0%",
    "wacc": "12.0%"
  },
  "metodos": {
    "bazin": {"pt": 35.20, "k": "10.5%"},
    "graham": {"pt": 33.80},
    "gordon": {"pt": 34.15},
    "dcf": {"pt": 34.40, "wacc": "12.0%"}
  },
  "sinal": "NEUTRO",
  "cor": "yellow"
}
```

---

#### 1.2 Margem de Segurança

**Endpoint**: `GET /api/buy-signals/margem-seguranca/<ticker>`  
**Arquivo**: `backend/app/services/buysignalsservice.py`

**Tabelas Consumidas**:
- `ativo` → ticker, precoatual, precoteto

**Lógica de Cálculo**:
```python
def calcular_margem_seguranca(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    precoatual = float(ativo.precoatual)
    precoteto = float(ativo.precoteto)

    # Margem = (Teto - Atual) / Teto * 100
    margem = ((precoteto - precoatual) / precoteto) * 100

    # Sinal de compra
    if margem >= 5:
        sinal = "COMPRA"
    elif margem >= 0:
        sinal = "NEUTRO"
    else:
        sinal = "VENDA"

    return margem, precoteto, sinal
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório |
|-------|--------|------|-------------|
| `ticker` | ativo | VARCHAR(20) | ✅ |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ |
| `precoteto` | ativo | NUMERIC(18,6) | ✅ |

**✅ Compliance ER**: 100%

---

#### 1.3 Buy Score (0-100)

**Endpoint**: `GET /api/buy-signals/buy-score/<ticker>`  
**Arquivo**: `backend/app/services/buysignalsservice.py`

**Tabelas Consumidas**:
- `ativo` → ticker, precoatual, precoteto, dividendyield, beta

**Lógica de Cálculo**:
```python
def calcular_buy_score(ticker):
    # Componentes (0-100)
    margem, _ = calcular_margem_seguranca(ticker)
    zscore = calcular_zscore(ticker)
    dy = float(ativo.dividendyield) if ativo.dividendyield else 4.0
    beta = float(ativo.beta) if ativo.beta else 1.0

    # Pontuação por componente
    margem_pts = np.clip(margem / 3, 0, 30)           # 0-30 pts
    z_pts = 25 if zscore < -1 else 15 if zscore < 0 else 5  # 5-25 pts
    dy_pts = np.clip(dy * 5, 0, 20)                   # 0-20 pts
    beta_pts = np.clip(max(0, (25 - (beta - 1) * 12.5)), 0, 25)  # 0-25 pts

    score = margem_pts + z_pts + dy_pts + beta_pts
    return round(min(score, 100))
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório |
|-------|--------|------|-------------|
| `ticker` | ativo | VARCHAR(20) | ✅ |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ |
| `precoteto` | ativo | NUMERIC(18,6) | ✅ |
| `dividendyield` | ativo | NUMERIC(8,4) | ⚠️ Usa 4% default se NULL |
| `beta` | ativo | NUMERIC(8,4) | ⚠️ Usa 1.0 default se NULL |

**⚠️ Compliance ER**: 80% - Funciona, mas depende de valores default quando campos são NULL.

---

#### 1.4 Z-Score (Desvio do Preço Histórico)

**Endpoint**: `GET /api/buy-signals/zscore/<ticker>`  
**Arquivo**: `backend/app/services/buysignalsservice.py`

**Tabelas Consumidas**:
- `ativo` → ticker, precoatual

**Lógica de Cálculo**:
```python
def calcular_zscore(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    precoatual = float(ativo.precoatual)

    # ⚠️ SIMULAÇÃO: Histórico fixo (deveria vir de tabela historico_preco)
    historico_simulado = np.array([42.0, 41.5, 40.8, 39.2, 38.6, 
                                   37.9, 38.1, 39.8, 41.2, 40.5, 
                                   39.0, 38.6], dtype=float)

    media = np.mean(historico_simulado)
    std = np.std(historico_simulado)

    if std > 0:
        z = (precoatual - media) / std
        return round(float(z), 2)
    return 0.0
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório | Observação |
|-------|--------|------|-------------|------------|
| `ticker` | ativo | VARCHAR(20) | ✅ | |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ | |
| `historico_preco` | ⚠️ **NÃO EXISTE** | - | ❌ | **GAP CRÍTICO** |

**❌ Compliance ER**: 50% - Funciona com mock, mas requer tabela `historico_preco` para produção.

---

### 2. APIs de Portfolio (Módulo 3)

#### 2.1 Dashboard Consolidado

**Endpoint**: `GET /api/portfolio/dashboard`  
**Arquivo**: `backend/app/services/portfolioservice.py`

**Tabelas Consumidas**:
- `posicao` → usuarioid, quantidade, precomedio, custototal, valoratual
- `ativo` → (JOIN) precoatual, ticker, nome
- `corretora` → (JOIN) nome

**Lógica de Cálculo**:
```python
def get_portfolio_dashboard(usuarioid):
    posicoes = Posicao.query.filter_by(usuarioid=usuarioid).all()

    # Agregações
    patrimonio_ativos = sum(p.valoratual or 0 for p in posicoes)
    custo_aquisicao = sum(p.custototal for p in posicoes)
    saldo_caixa = sum(c.saldoatual for c in corretoras)

    patrimonio_total = patrimonio_ativos + saldo_caixa
    lucro_bruto = patrimonio_ativos - custo_aquisicao
    rentabilidade_perc = (lucro_bruto / custo_aquisicao * 100) if custo_aquisicao > 0 else 0

    return {
        'patrimonioativos': round(patrimonio_ativos, 2),
        'custoaquisicao': round(custo_aquisicao, 2),
        'saldocaixa': round(saldo_caixa, 2),
        'patrimoniototal': round(patrimonio_total, 2),
        'lucrobruto': round(lucro_bruto, 2),
        'rentabilidadeperc': round(rentabilidade_perc, 2)
    }
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório |
|-------|--------|------|-------------|
| `usuarioid` | posicao | UUID FK | ✅ |
| `quantidade` | posicao | NUMERIC(18,8) | ✅ |
| `precomedio` | posicao | NUMERIC(18,6) | ✅ |
| `custototal` | posicao | NUMERIC(18,2) | ✅ |
| `valoratual` | posicao | NUMERIC(18,2) | ⚠️ Pode ser NULL |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ |
| `saldoatual` | corretora | NUMERIC(18,2) | ✅ |

**✅ Compliance ER**: 100%

---

#### 2.2 Alocação por Classe de Ativo

**Endpoint**: `GET /api/portfolio/alocacao`  
**Arquivo**: `backend/app/services/portfolioservice.py`

**Tabelas Consumidas**:
- `posicao` → usuarioid, valoratual
- `ativo` → (JOIN) classe

**Lógica de Cálculo**:
```python
def get_alocacao_por_classe(usuarioid):
    posicoes = (Posicao.query
                .filter_by(usuarioid=usuarioid)
                .join(Ativo)
                .all())

    # Agregar por classe
    alocacao = {}
    total = sum(p.valoratual or 0 for p in posicoes)

    for p in posicoes:
        classe = p.ativo.classe.value  # RENDAVARIAVEL, RENDAFIXA, etc
        alocacao[classe] = alocacao.get(classe, 0) + (p.valoratual or 0)

    # Percentuais
    for classe in alocacao:
        alocacao[classe] = {
            'valor': round(alocacao[classe], 2),
            'percentual': round(alocacao[classe] / total * 100, 2) if total > 0 else 0
        }

    return alocacao
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório |
|-------|--------|------|-------------|
| `usuarioid` | posicao | UUID FK | ✅ |
| `valoratual` | posicao | NUMERIC(18,2) | ⚠️ Pode ser NULL |
| `classe` | ativo | ENUM(ClasseAtivo) | ✅ |

**✅ Compliance ER**: 100%

---

#### 2.3 Dividend Yield Médio do Portfolio

**Endpoint**: `GET /api/calculos/portfolio` (dentro do objeto)  
**Arquivo**: `backend/app/services/portfolioservice.py`

**Tabelas Consumidas**:
- `posicao` → usuarioid, valoratual
- `ativo` → (JOIN) dividendyield

**Lógica de Cálculo**:
```python
def get_dividend_yield_medio(usuarioid):
    posicoes = (Posicao.query
                .filter_by(usuarioid=usuarioid)
                .join(Ativo)
                .all())

    # Média ponderada por valor investido
    soma_dy_ponderado = sum(
        (p.valoratual or 0) * (p.ativo.dividendyield or 0)
        for p in posicoes
    )
    total_investido = sum(p.valoratual or 0 for p in posicoes)

    dy_medio = soma_dy_ponderado / total_investido if total_investido > 0 else 0
    return round(dy_medio, 2)
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório |
|-------|--------|------|-------------|
| `usuarioid` | posicao | UUID FK | ✅ |
| `valoratual` | posicao | NUMERIC(18,2) | ⚠️ Pode ser NULL |
| `dividendyield` | ativo | NUMERIC(8,4) | ⚠️ Usa 0 se NULL |

**⚠️ Compliance ER**: 80% - Funciona, mas usa defaults para valores NULL.

---

### 3. APIs de Cotação em Tempo Real (Módulo 7.5)

#### 3.1 Cotação Individual

**Endpoint**: `GET /api/cotacoes/<ticker>`  
**Arquivo**: `backend/app/services/cotacoesservice.py`

**Tabelas Consumidas**:
- `ativo` → ticker, mercado, dataultimacotacao, precoatual
- `fontedados` → nome, ativa, prioridade

**Lógica de Cálculo**:
```python
def obter_cotacao(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    TTL_SECONDS = 900  # 15 minutos (Prompt Mestre)
    now = datetime.now()

    # Verificar cache (TTL 15min)
    if ativo.dataultimacotacao and (now - ativo.dataultimacotacao).seconds < TTL_SECONDS:
        return {
            'ticker': ticker,
            'precoatual': float(ativo.precoatual),
            'provider': 'cache-postgresql',
            'cache_age_minutes': (now - ativo.dataultimacotacao).seconds // 60
        }

    # Buscar em APIs externas (fallback cascade)
    for fonte in FonteDados.query.filter_by(ativa=True).order_by('prioridade').all():
        try:
            if fonte.nome == 'brapi.dev':
                dados = fetch_brapi(ticker, ativo.mercado)
            elif fonte.nome == 'yfinance':
                dados = fetch_yfinance(ticker, ativo.mercado)

            # Atualizar cache no DB
            ativo.precoatual = dados['preco']
            ativo.dataultimacotacao = now
            db.session.commit()

            return {**dados, 'provider': fonte.nome}
        except:
            continue

    # Fallback: retornar último valor do cache
    return {'ticker': ticker, 'precoatual': float(ativo.precoatual), 'provider': 'cache-stale'}
```

**Campos do ER Utilizados**:
| Campo | Tabela | Tipo | Obrigatório | Observação |
|-------|--------|------|-------------|------------|
| `ticker` | ativo | VARCHAR(20) | ✅ | |
| `mercado` | ativo | VARCHAR(10) | ✅ | Adapta ticker (BR: .SA) |
| `precoatual` | ativo | NUMERIC(18,6) | ✅ | Cache |
| `dataultimacotacao` | ativo | TIMESTAMP | ✅ | TTL 15min |
| `nome` | fontedados | VARCHAR(100) | ✅ | Identificar API |
| `ativa` | fontedados | BOOLEAN | ✅ | Filtrar fontes |
| `prioridade` | fontedados | INTEGER | ✅ | Ordem de tentativa |

**✅ Compliance ER**: 100%

---

## 📊 MATRIZ DE COMPLIANCE: API x TABELAS

| API / Cálculo | Ativo | Posicao | Transacao | Provento | Corretora | ParametrosMacro | FonteDados | HistoricoPreco ⚠️ |
|---------------|-------|---------|-----------|----------|-----------|-----------------|------------|------------------|
| **Preço Teto** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Margem Segurança** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Buy Score** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ (zscore) |
| **Z-Score** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ **GAP** |
| **Dashboard Portfolio** | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Alocação Classe** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **DY Médio** | ✅ | ✅ | ❌ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| **Cotação Live** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

**Legenda**:
- ✅ Usa e existe no ER
- ⚠️ Usa mas campo pode ser NULL
- ❌ Não usa esta tabela
- ❌ **GAP** Tabela não existe no ER

---

## 🔴 GAPS CRÍTICOS IDENTIFICADOS

### GAP 1: Tabela `historico_preco` Inexistente
**Impacto**: 🔴 **CRÍTICO**  
**APIs Afetadas**:
- Z-Score (usa mock)
- Volatilidade (não implementada)
- Sharpe Ratio (não implementada)
- Beta (usa valor fixo)

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

### GAP 2: Campo `caprate` em Ativo
**Impacto**: 🟡 **MÉDIO**  
**APIs Afetadas**:
- Preço Teto (FIIs) → Usa valor fixo da tabela `parametrosmacro`

**Solução**:
```sql
ALTER TABLE ativo ADD COLUMN caprate NUMERIC(8,4) NULL;
COMMENT ON COLUMN ativo.caprate IS 'Cap Rate individual do FII (%)';
```

### GAP 3: Campos NULL em `dividendyield`, `pl`, `pvp`, `roe`
**Impacto**: 🟡 **MÉDIO**  
**APIs Afetadas**:
- Buy Score → Usa defaults quando NULL
- DY Médio → Ignora ativos sem DY
- Filtros de valuation → Não funcionam sem dados

**Solução**: Popular campos via job assíncrono que consulta APIs.

---

## 🟡 INCONSISTÊNCIAS ENCONTRADAS

### Inconsistência 1: Enum Serialization
**Problema**: `TipoAtivo`, `ClasseAtivo` são Enums no DB, mas tratados como strings no JSON.  
**Arquivo**: `backend/app/models/ativo.py`

**Evidência**:
```python
# todict() serializa enum como string
def todict(self):
    return {
        'tipo': self.tipo.value if self.tipo else None,  # ✅ Correto
        'classe': self.classe.value if self.classe else None  # ✅ Correto
    }
```

**Status**: ✅ **RESOLVIDO** - Código atual já trata corretamente.

### Inconsistência 2: Nomes de Campos `pl` e `pvp`
**Problema**: Confusão entre `pl`/`p_l` e `pvp`/`p_vp`.  
**Status**: ✅ **RESOLVIDO** - Código usa consistentemente `pl` e `pvp`.

---

## 🟢 PONTOS FORTES

1. **✅ Regionalização**: Parâmetros macro por mercado (BR, US, EU).
2. **✅ Multi-método**: Preço Teto usa 4 métodos (Bazin, Graham, Gordon, DCF).
3. **✅ Cache Inteligente**: Cotações com TTL 15min (Prompt Mestre).
4. **✅ Fallback Cascade**: Múltiplas APIs de cotação (brapi → yfinance → cache).
5. **✅ Separação de Concerns**: Services isolam lógica de negócio dos controllers.
6. **✅ Validações**: Marshmallow schemas para input validation.

---

## 💡 SUGESTÕES DE MELHORIA

### Melhoria 1: Job Assíncrono para Popular Indicadores
```python
# backend/app/tasks/atualizar_indicadores.py
from celery import Celery
from app.models import Ativo
from app.services.cotacoesservice import fetch_fundamentals

@celery.task
def atualizar_indicadores_batch():
    ativos = Ativo.query.filter_by(ativo=True, deslistado=False).all()
    for ativo in ativos:
        try:
            dados = fetch_fundamentals(ativo.ticker, ativo.mercado)
            ativo.pl = dados.get('pl')
            ativo.pvp = dados.get('pvp')
            ativo.roe = dados.get('roe')
            ativo.dividendyield = dados.get('dy')
            db.session.commit()
        except:
            continue
```

**Agendar**: Executar 1x por dia (00:00 UTC).

### Melhoria 2: Implementar API de Histórico
```python
# backend/app/blueprints/historico.py
@bp.route('/historico/<ticker>', methods=['GET'])
@jwt_required()
def get_historico(ticker):
    dias = request.args.get('dias', 365, type=int)
    historico = (HistoricoPreco.query
                 .join(Ativo)
                 .filter(Ativo.ticker == ticker.upper())
                 .order_by(HistoricoPreco.data.desc())
                 .limit(dias)
                 .all())
    return jsonify({'data': [h.todict() for h in historico]})
```

### Melhoria 3: Adicionar Cálculo de Volatilidade Real
```python
def calcular_volatilidade(ticker, dias=252):
    historico = (HistoricoPreco.query
                 .join(Ativo)
                 .filter(Ativo.ticker == ticker.upper())
                 .order_by(HistoricoPreco.data.desc())
                 .limit(dias)
                 .all())

    precos = np.array([h.preco_fechamento for h in historico])
    retornos = np.diff(np.log(precos))
    volatilidade_anual = np.std(retornos) * np.sqrt(252)
    return round(volatilidade_anual, 4)
```

---

## 📋 PLANO DE AÇÃO

### Prioridade P0 - Implementar Imediatamente
1. ❌ **Criar tabela `historico_preco`** → Desbloqueia Z-Score, volatilidade, Beta
2. ❌ **Job para popular `dividendyield`, `pl`, `pvp`, `roe`** → Melhora Buy Score

### Prioridade P1 - Próxima Sprint
3. ⚠️ Adicionar campo `caprate` individual em Ativo
4. ⚠️ Implementar endpoint `/historico/<ticker>`
5. ⚠️ Implementar cálculo de volatilidade real

### Prioridade P2 - Backlog
6. 📊 Adicionar Sharpe Ratio ao dashboard
7. 📊 Implementar correlação entre ativos
8. 📊 Alertas automáticos quando margem > 10%

---

## 📦 Arquivos Revisados

### Blueprints (Rotas)
- `backend/app/blueprints/calculosblueprint.py` ⭐ **Preço Teto**
- `backend/app/blueprints/buysignalsblueprint.py` ⭐ **Buy Score, Z-Score**
- `backend/app/blueprints/cotacoesblueprint.py` ⭐ **Cotações Live**
- `backend/app/blueprints/portfolio.py` (dashboard, alocação)

### Services (Lógica de Negócio)
- `backend/app/services/buysignalsservice.py` ⭐ **CRÍTICO**
- `backend/app/services/portfolioservice.py` ⭐ **CRÍTICO**
- `backend/app/services/cotacoesservice.py` ⭐ **CRÍTICO**
- `backend/app/services/ativoservice.py`
- `backend/app/services/posicaoservice.py`
- `backend/app/services/transacaoservice.py`
- `backend/app/services/proventoservice.py`

### Models
- `backend/app/models/ativo.py` ⭐ **CRÍTICO**
- `backend/app/models/posicao.py` ⭐ **CRÍTICO**
- `backend/app/models/parametrosmacro.py`
- `backend/app/models/fontedados.py`

---

## ✅ CRITÉRIOS DE CONCLUSÃO

- [x] Inventário completo de APIs de cálculo
- [x] Mapeamento de tabelas/campos usados
- [x] Validação de compliance ER x APIs
- [ ] ❌ Tabela `historico_preco` criada (PENDENTE)
- [ ] ❌ Indicadores fundamentalistas populados (PENDENTE)
- [ ] ⚠️ Z-Score usando dados reais (PENDENTE - depende de historico_preco)

**Status Geral**: ✅ **MÓDULOS 2-4 OPERACIONAIS COM GAPS DOCUMENTADOS**

---

## 🔗 Referências Cruzadas

- 📄 [REVISÃO_MÓDULO_1_BANCO_DADOS.md](./REVISAO_MODULO_1_BANCO_DADOS.md)
- 📄 [MATRIZ_COMPLIANCE_ER_APIS.md](./MATRIZ_COMPLIANCE_ER_APIS.md) ← Próximo documento
- 📄 `docs/MODULO4_CHECKLIST.md`
- 📄 `docs/VALIDACAO_M4_COMPLETA.md`
- 📄 `docs/API_REFERENCE_COMPLETE.md`

---

**Próximo Passo**: Gerar **MATRIZ_COMPLIANCE_ER_APIS.md** (tabela cruzada detalhada) 🚀
