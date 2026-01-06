# 📋 Issues Template - Gaps da Revisão Módulos 1-4

**Gerado em**: 06/01/2026  
**Branch**: `feature/revisao`  
**Commit Base**: `7dedb7d`  
**Referência**: [docs/revisoes/](../docs/revisoes/)

---

## 🎯 Como Usar

1. Copie o conteúdo de cada issue abaixo
2. Crie uma nova issue no GitHub
3. Cole o conteúdo (título + descrição)
4. Adicione as labels sugeridas
5. Atribua o milestone correspondente

---

## 🔴 SPRINT 1 - PRIORIDADE P0 (Bloqueadores)

### Issue #1: [P0] Criar migration para tabela `historico_preco`

**Labels**: `priority: critical`, `database`, `migration`, `backend`  
**Milestone**: Sprint 1 - Módulo 1 Gap  
**Assignees**: [Backend Team]

#### Descrição

Criar migration Alembic para a tabela `historico_preco`, necessária para cálculos de Z-Score, volatilidade, Sharpe Ratio e Beta com dados reais.

#### Contexto

Atualmente, a API `/api/buy-signals/zscore/<ticker>` usa um array fixo de preços históricos (mock), o que impede cálculos precisos de métricas de risco.

#### Especificação da Tabela

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

COMMENT ON TABLE historico_preco IS 'Histórico diário de preços dos ativos';
COMMENT ON COLUMN historico_preco.data IS 'Data do pregão (dia útil)';
```

#### Critérios de Aceitação

- [ ] Migration criada em `backend/alembic/versions/`
- [ ] Tabela criada com 8 colunas + timestamps
- [ ] Índice composto `(ativoid, data)` criado
- [ ] Constraint UNIQUE `(ativoid, data)` funcionando
- [ ] FK para `ativo(id)` com ON DELETE CASCADE
- [ ] `alembic upgrade head` executa sem erros
- [ ] `alembic downgrade -1` reverte corretamente

#### Arquivos Afetados

- `backend/alembic/versions/XXXXX_create_historico_preco.py` (NOVO)
- `backend/app/models/historicopreco.py` (NOVO - SQLAlchemy model)

#### Referências

- [docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md](../docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md#gap-1-tabela-historico_preco-inexistente)
- [docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md](../docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md#gap-1-tabela-historico_preco-inexistente)

---

### Issue #2: [P0] Implementar job Celery para popular histórico de preços

**Labels**: `priority: critical`, `celery`, `backend`, `integration`  
**Milestone**: Sprint 1 - Módulo 1 Gap  
**Assignees**: [Backend Team]  
**Depends on**: Issue #1

#### Descrição

Criar job assíncrono Celery que popula a tabela `historico_preco` com dados históricos dos últimos 365 dias para todos os ativos ativos.

#### Especificação

**Arquivo**: `backend/app/tasks/popular_historico.py`

```python
from celery import Celery
from app.models import Ativo, HistoricoPreco
from app.services.cotacoesservice import fetch_historico
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def popular_historico_batch(self, dias=365):
    """
    Popula histórico de preços dos últimos N dias.

    Args:
        dias (int): Quantidade de dias para buscar (padrão: 365)

    Returns:
        dict: {'ativos_processados': int, 'registros_criados': int, 'erros': int}
    """
    ativos = Ativo.query.filter_by(ativo=True, deslistado=False).all()
    stats = {'ativos_processados': 0, 'registros_criados': 0, 'erros': 0}

    for ativo in ativos:
        try:
            # Buscar histórico da API externa
            historico = fetch_historico(ativo.ticker, ativo.mercado, dias)

            for registro in historico:
                hist = HistoricoPreco(
                    ativoid=ativo.id,
                    data=registro['data'],
                    preco_abertura=registro.get('abertura'),
                    preco_fechamento=registro['fechamento'],
                    preco_minimo=registro.get('minimo'),
                    preco_maximo=registro.get('maximo'),
                    volume=registro.get('volume')
                )
                db.session.add(hist)
                stats['registros_criados'] += 1

            db.session.commit()
            stats['ativos_processados'] += 1
            logger.info(f"✅ {ativo.ticker}: {len(historico)} dias")

        except Exception as e:
            logger.error(f"❌ {ativo.ticker}: {str(e)}")
            db.session.rollback()
            stats['erros'] += 1
            continue

    return stats
```

#### Agendamento Celery Beat

```python
# backend/app/celeryconfig.py
beat_schedule = {
    'popular-historico-incremental': {
        'task': 'app.tasks.popular_historico.popular_historico_batch',
        'schedule': crontab(hour=1, minute=0),  # 01:00 UTC diariamente
        'kwargs': {'dias': 7}  # Incremental - últimos 7 dias
    }
}
```

#### Critérios de Aceitação

- [ ] Task Celery criada e registrada
- [ ] Função `fetch_historico()` implementada em `cotacoesservice.py`
- [ ] Integração com yfinance (BR/US) e brapi.dev (BR)
- [ ] Retry automático em caso de falha (3 tentativas)
- [ ] Logging detalhado (INFO + ERROR)
- [ ] Agendamento Celery Beat configurado
- [ ] Comando manual funciona: `celery -A app.celery call app.tasks.popular_historico_batch`
- [ ] Testes unitários cobrem cenários: sucesso, falha API, ativo inexistente

#### Arquivos Afetados

- `backend/app/tasks/popular_historico.py` (NOVO)
- `backend/app/services/cotacoesservice.py` (adicionar `fetch_historico()`)
- `backend/app/celeryconfig.py` (adicionar agendamento)
- `backend/tests/tasks/test_popular_historico.py` (NOVO)

#### Referências

- [docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md](../docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md#gap-1-tabela-historico_preco-inexistente)

---

### Issue #3: [P0] Atualizar serviço Z-Score para usar histórico real

**Labels**: `priority: critical`, `backend`, `calculation`, `refactor`  
**Milestone**: Sprint 1 - Módulo 1 Gap  
**Assignees**: [Backend Team]  
**Depends on**: Issue #1, Issue #2

#### Descrição

Refatorar função `calcular_zscore()` em `buysignalsservice.py` para usar dados reais da tabela `historico_preco` ao invés de array mockado.

#### Código Atual (Mock)

```python
def calcular_zscore(ticker):
    ativo = Ativo.query.filter_by(ticker=ticker).first()
    precoatual = float(ativo.precoatual)

    # ⚠️ MOCK - Array fixo
    historico_simulado = np.array([42.0, 41.5, 40.8, ...], dtype=float)
    media = np.mean(historico_simulado)
    std = np.std(historico_simulado)

    z = (precoatual - media) / std if std > 0 else 0.0
    return round(z, 2)
```

#### Código Proposto (Real)

```python
def calcular_zscore(ticker, dias=252):
    """
    Calcula Z-Score baseado em histórico real de preços.

    Args:
        ticker (str): Código do ativo
        dias (int): Janela de dias úteis (padrão: 252 = 1 ano)

    Returns:
        float: Z-Score (-3 a +3 tipicamente)

    Raises:
        ValueError: Se ativo não encontrado ou histórico insuficiente
    """
    ativo = Ativo.query.filter_by(ticker=ticker.upper()).first()
    if not ativo:
        raise ValueError(f"Ativo {ticker} não encontrado")

    precoatual = float(ativo.precoatual)

    # Buscar histórico real
    historico = (HistoricoPreco.query
                 .filter_by(ativoid=ativo.id)
                 .order_by(HistoricoPreco.data.desc())
                 .limit(dias)
                 .all())

    if len(historico) < 30:
        raise ValueError(f"Histórico insuficiente: {len(historico)} dias (mínimo: 30)")

    precos = np.array([float(h.preco_fechamento) for h in historico])
    media = np.mean(precos)
    std = np.std(precos)

    if std == 0:
        logger.warning(f"{ticker}: Desvio padrão zero (preço constante)")
        return 0.0

    z = (precoatual - media) / std
    return round(float(z), 2)
```

#### Critérios de Aceitação

- [ ] Função `calcular_zscore()` refatorada
- [ ] Query usa tabela `historico_preco`
- [ ] Parâmetro `dias` configurável (default: 252)
- [ ] Validação: mínimo 30 dias de histórico
- [ ] Tratamento de erro: histórico insuficiente
- [ ] Tratamento de erro: std = 0 (preço constante)
- [ ] Logging de warnings
- [ ] Testes unitários: 
  - Z-Score positivo, negativo, zero
  - Histórico < 30 dias (erro)
  - Std = 0 (retorna 0.0)
- [ ] Endpoint `/api/buy-signals/zscore/PETR4` funciona com dados reais

#### Arquivos Afetados

- `backend/app/services/buysignalsservice.py` (refatorar)
- `backend/tests/services/test_buysignalsservice.py` (adicionar testes)

#### Referências

- [docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md](../docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md#14-z-score-desvio-do-preço-histórico)
- [docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md](../docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md#exemplo-de-análise-detalhada-api-z-score)

---

### Issue #4: [P0] Adicionar constraints de validação em campos críticos

**Labels**: `priority: high`, `database`, `data-integrity`, `migration`  
**Milestone**: Sprint 1 - Módulo 1 Gap  
**Assignees**: [Backend Team]

#### Descrição

Adicionar constraints CHECK em campos financeiros do schema para prevenir dados inconsistentes.

#### Migration SQL

```sql
-- Ativo: Preços e percentuais positivos
ALTER TABLE ativo ADD CONSTRAINT ck_ativo_preco_positivo 
    CHECK (precoatual IS NULL OR precoatual >= 0);

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_precoteto_positivo 
    CHECK (precoteto IS NULL OR precoteto >= 0);

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_dy_range 
    CHECK (dividendyield IS NULL OR (dividendyield >= 0 AND dividendyield <= 100));

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_pl_positivo 
    CHECK (pl IS NULL OR pl >= 0);

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_pvp_positivo 
    CHECK (pvp IS NULL OR pvp >= 0);

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_roe_range 
    CHECK (roe IS NULL OR (roe >= -100 AND roe <= 100));

ALTER TABLE ativo ADD CONSTRAINT ck_ativo_beta_positivo 
    CHECK (beta IS NULL OR beta >= 0);

-- Posicao: Quantidade não negativa
ALTER TABLE posicao ADD CONSTRAINT ck_posicao_quantidade_positiva 
    CHECK (quantidade >= 0);

ALTER TABLE posicao ADD CONSTRAINT ck_posicao_precomedio_positivo 
    CHECK (precomedio >= 0);

-- Transacao: Valores positivos
ALTER TABLE transacao ADD CONSTRAINT ck_transacao_quantidade_positiva 
    CHECK (quantidade > 0);

ALTER TABLE transacao ADD CONSTRAINT ck_transacao_preco_positivo 
    CHECK (precounitario >= 0);

-- Provento: Valores consistentes
ALTER TABLE provento ADD CONSTRAINT ck_provento_valorporacao_positivo 
    CHECK (valorporacao >= 0);

ALTER TABLE provento ADD CONSTRAINT ck_provento_valorliquido_menor_bruto 
    CHECK (valorliquido <= valorbruto);

-- HistoricoPreco: Preços coerentes
ALTER TABLE historico_preco ADD CONSTRAINT ck_historico_fechamento_positivo 
    CHECK (preco_fechamento > 0);

ALTER TABLE historico_preco ADD CONSTRAINT ck_historico_minmax 
    CHECK (preco_minimo IS NULL OR preco_maximo IS NULL OR preco_minimo <= preco_maximo);
```

#### Critérios de Aceitação

- [ ] Migration Alembic criada
- [ ] 15 constraints CHECK adicionados
- [ ] `alembic upgrade head` executa sem violar constraints existentes
- [ ] Testes de violação de constraint:
  - INSERT com `precoatual = -10` → ERRO
  - UPDATE com `dividendyield = 150` → ERRO
  - INSERT com `quantidade = -5` → ERRO
- [ ] Documentação SQL comentada no código
- [ ] Seeds de teste validam constraints

#### Arquivos Afetados

- `backend/alembic/versions/XXXXX_add_check_constraints.py` (NOVO)
- `backend/tests/test_constraints.py` (NOVO)

#### Referências

- [docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md](../docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md#melhoria-1-adicionar-constraints-de-validação)

---

### Issue #5: [P0] Testes de regressão de APIs após mudanças de schema

**Labels**: `priority: high`, `testing`, `backend`, `regression`  
**Milestone**: Sprint 1 - Módulo 1 Gap  
**Assignees**: [QA Team]  
**Depends on**: Issue #1, Issue #3, Issue #4

#### Descrição

Executar suite completa de testes de regressão para validar que as mudanças no schema não quebraram APIs existentes.

#### Escopo dos Testes

**12 APIs de Cálculo** (conforme [REVISAO_MODULOS_2-4_APIS_CALCULOS.md](../docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md)):

1. `/api/calculos/precoteto/<ticker>` → 4 métodos (Bazin, Graham, Gordon, DCF)
2. `/api/buy-signals/margem-seguranca/<ticker>`
3. `/api/buy-signals/buy-score/<ticker>`
4. `/api/buy-signals/zscore/<ticker>` ⭐ **MUDOU**
5. `/api/portfolio/dashboard`
6. `/api/portfolio/alocacao`
7. `/api/portfolio/performance`
8. `/api/calculos/portfolio` (DY médio)
9. `/api/cotacoes/<ticker>`
10. `/api/cotacoes/batch`
11. `/api/cotacoes/health`
12. `/api/proventos`

#### Critérios de Aceitação

- [ ] 12 endpoints testados com dados reais
- [ ] Casos de teste para PETR4, VALE3, ITUB4 (BR)
- [ ] Casos de teste para AAPL, MSFT (US)
- [ ] Response schemas validados (estrutura JSON)
- [ ] Performance: todas as queries < 500ms (cold cache)
- [ ] Performance: todas as queries < 100ms (warm cache)
- [ ] Cobertura de código > 80% em services
- [ ] Relatório de testes gerado (HTML + JSON)

#### Script de Teste

```bash
#!/bin/bash
# backend/tests/regression_suite.sh

export FLASK_ENV=testing
export DATABASE_URL=postgresql://test_user:test_pass@localhost/exitus_test

# Rodar suite completa
pytest backend/tests/     --cov=backend/app/services     --cov-report=html     --cov-report=term     --benchmark-only     --benchmark-min-rounds=5     -v

# Validar performance
pytest backend/tests/performance/ --benchmark-json=benchmark.json
python scripts/validate_benchmarks.py benchmark.json
```

#### Arquivos Afetados

- `backend/tests/regression_suite.sh` (NOVO)
- `backend/tests/test_apis_calculos.py` (ATUALIZAR)
- `backend/tests/performance/test_benchmarks.py` (NOVO)

---

## 🟡 SPRINT 2 - PRIORIDADE P1 (Alta)

### Issue #6: [P1] Implementar job Celery para atualizar indicadores fundamentalistas

**Labels**: `priority: high`, `celery`, `backend`, `integration`  
**Milestone**: Sprint 2 - Dados Fundamentalistas  
**Assignees**: [Backend Team]

#### Descrição

Criar job semanal que atualiza campos `dividendyield`, `pl`, `pvp`, `roe`, `beta` da tabela `ativo` via APIs externas (yfinance, brapi.dev).

#### Contexto

Atualmente ~40-80% desses campos são NULL, forçando cálculos a usar valores default (ex: DY = 4%, Beta = 1.0).

#### Especificação

**Arquivo**: `backend/app/tasks/atualizar_indicadores.py`

```python
@celery.task(bind=True, max_retries=2)
def atualizar_indicadores_batch(self):
    """Atualiza indicadores fundamentalistas via APIs externas."""
    ativos = Ativo.query.filter_by(ativo=True, deslistado=False).all()
    stats = {'atualizados': 0, 'erros': 0, 'nao_disponiveis': 0}

    for ativo in ativos:
        try:
            dados = fetch_fundamentals(ativo.ticker, ativo.mercado)

            ativo.dividendyield = dados.get('dy')
            ativo.pl = dados.get('pl')
            ativo.pvp = dados.get('pvp')
            ativo.roe = dados.get('roe')
            ativo.beta = dados.get('beta')

            db.session.commit()
            stats['atualizados'] += 1

        except DataNotAvailableError:
            stats['nao_disponiveis'] += 1
            continue
        except Exception as e:
            logger.error(f"Erro {ativo.ticker}: {e}")
            stats['erros'] += 1
            db.session.rollback()

    return stats

# Agendamento: Domingos 02:00 UTC
beat_schedule['atualizar-indicadores'] = {
    'task': 'app.tasks.atualizar_indicadores.atualizar_indicadores_batch',
    'schedule': crontab(day_of_week=0, hour=2, minute=0)
}
```

#### Critérios de Aceitação

- [ ] Task Celery criada
- [ ] Função `fetch_fundamentals()` implementada
- [ ] Integração com yfinance (US) e brapi.dev (BR)
- [ ] Tratamento de erro: dados não disponíveis (FIIs sem P/L, etc)
- [ ] Logging detalhado
- [ ] Agendamento semanal (domingos 02:00 UTC)
- [ ] Testes: mock de APIs externas
- [ ] Comando manual: `celery call atualizar_indicadores_batch`

#### Arquivos Afetados

- `backend/app/tasks/atualizar_indicadores.py` (NOVO)
- `backend/app/services/cotacoesservice.py` (adicionar `fetch_fundamentals()`)
- `backend/tests/tasks/test_atualizar_indicadores.py` (NOVO)

---

### Issue #7: [P1] Configurar Celery Beat para agendamentos automáticos

**Labels**: `priority: high`, `celery`, `backend`, `devops`  
**Milestone**: Sprint 2 - Infraestrutura  
**Assignees**: [DevOps Team]  
**Depends on**: Issue #2, Issue #6

#### Descrição

Configurar container Celery Beat para executar jobs agendados automaticamente.

#### Especificação

**Arquivo**: `backend/docker-compose.yml` (adicionar serviço)

```yaml
services:
  celery-worker:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
      - exitus-db
    networks:
      - exitus-network

  celery-beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - exitus-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - exitus-network
```

**Arquivo**: `backend/app/celeryconfig.py`

```python
from celery.schedules import crontab

# Agendamentos
beat_schedule = {
    'popular-historico-incremental': {
        'task': 'app.tasks.popular_historico_batch',
        'schedule': crontab(hour=1, minute=0),  # Diário 01:00 UTC
        'kwargs': {'dias': 7}
    },
    'atualizar-indicadores': {
        'task': 'app.tasks.atualizar_indicadores_batch',
        'schedule': crontab(day_of_week=0, hour=2, minute=0)  # Semanal
    }
}
```

#### Critérios de Aceitação

- [ ] Container `celery-worker` rodando
- [ ] Container `celery-beat` rodando
- [ ] Container `redis` rodando
- [ ] 2 tasks agendados registrados
- [ ] Logs confirmam execuções: `celery beat: Scheduler: Sending due task ...`
- [ ] Monitoring: Flower instalado (`http://localhost:5555`)
- [ ] Health check: `celery inspect active` retorna tasks

#### Arquivos Afetados

- `backend/docker-compose.yml` (adicionar 3 services)
- `backend/app/celeryconfig.py` (configurar beat_schedule)
- `backend/requirements.txt` (adicionar `celery[redis]`, `flower`)

---

### Issue #8: [P1] Adicionar endpoint `/api/indicadores/status` (health check de jobs)

**Labels**: `priority: medium`, `backend`, `monitoring`  
**Milestone**: Sprint 2 - Observabilidade  
**Assignees**: [Backend Team]  
**Depends on**: Issue #7

#### Descrição

Criar endpoint de monitoramento que retorna status dos jobs Celery (última execução, próxima execução, erros).

#### Especificação

**Endpoint**: `GET /api/indicadores/status`  
**Autenticação**: JWT (admin only)

**Response**:
```json
{
  "celery_status": "online",
  "jobs": {
    "popular_historico_batch": {
      "ultima_execucao": "2026-01-06T01:00:23Z",
      "proxima_execucao": "2026-01-07T01:00:00Z",
      "status": "success",
      "resultado": {
        "ativos_processados": 25,
        "registros_criados": 175,
        "erros": 0
      }
    },
    "atualizar_indicadores_batch": {
      "ultima_execucao": "2026-01-05T02:00:15Z",
      "proxima_execucao": "2026-01-12T02:00:00Z",
      "status": "success",
      "resultado": {
        "atualizados": 20,
        "erros": 2,
        "nao_disponiveis": 3
      }
    }
  },
  "redis_status": "connected",
  "queue_size": 0
}
```

#### Critérios de Aceitação

- [ ] Endpoint criado em `backend/app/blueprints/indicadores.py`
- [ ] Decorator `@admin_required`
- [ ] Query Celery para obter status de tasks
- [ ] Query Redis para obter tamanho da fila
- [ ] Response inclui próxima execução (calculado via crontab)
- [ ] Testes: admin acessa OK, user normal recebe 403

#### Arquivos Afetados

- `backend/app/blueprints/indicadores.py` (NOVO)
- `backend/tests/blueprints/test_indicadores.py` (NOVO)

---

### Issue #9: [P1] Documentar processo de setup de APIs externas (tokens)

**Labels**: `priority: medium`, `documentation`, `devops`  
**Milestone**: Sprint 2 - Docs  
**Assignees**: [Tech Writer]

#### Descrição

Criar guia passo-a-passo para configurar tokens de APIs externas (yfinance, brapi.dev, Alpha Vantage, etc).

#### Conteúdo Sugerido

**Arquivo**: `docs/SETUP_APIS_EXTERNAS.md`

```markdown
# 🔑 Configuração de APIs Externas

## 1. yfinance (Free - Sem Token)

Instalado automaticamente via `requirements.txt`. Sem necessidade de configuração.

## 2. brapi.dev (Free Tier)

1. Acesse https://brapi.dev/
2. Clique em "Planos" → "Free" → "Começar Grátis"
3. Faça login com GitHub
4. Copie o token em "Minha Conta"
5. Adicione ao `.env`:

```
BRAPI_API_KEY=your-token-here
```

**Limites Free Tier**: 20 requisições/minuto

## 3. Alpha Vantage (Free)

1. Acesse https://www.alphavantage.co/support/#api-key
2. Preencha formulário (nome + email)
3. Receba token por email
4. Adicione ao `.env`:

```
ALPHA_VANTAGE_API_KEY=your-token-here
```

**Limites Free**: 25 requisições/dia

[... etc para outras APIs ...]
```

#### Critérios de Aceitação

- [ ] Documento criado em `docs/SETUP_APIS_EXTERNAS.md`
- [ ] Seções para: yfinance, brapi.dev, Alpha Vantage, Finnhub
- [ ] Passo-a-passo com screenshots (se aplicável)
- [ ] Informação de limites de rate (free tiers)
- [ ] Exemplo de `.env` completo
- [ ] Troubleshooting: erros comuns

#### Arquivos Afetados

- `docs/SETUP_APIS_EXTERNAS.md` (NOVO)
- `README.md` (adicionar link na seção "Setup")

---

## 🟢 BACKLOG - PRIORIDADE P2 (Melhorias)

### Issue #10: [P2] Adicionar campo `caprate` individual em tabela Ativo

**Labels**: `priority: low`, `database`, `enhancement`, `fii`  
**Milestone**: Backlog  
**Assignees**: [Backend Team]

#### Descrição

Adicionar campo `caprate` (Cap Rate) individual para FIIs na tabela `ativo`, permitindo cálculo de Preço Teto personalizado por ativo.

#### Especificação

```sql
ALTER TABLE ativo ADD COLUMN caprate NUMERIC(8,4) NULL;
COMMENT ON COLUMN ativo.caprate IS 'Cap Rate individual do FII (%). Se NULL, usa valor regional de parametrosmacro.';
```

**Lógica Atualizada** (em `calculosblueprint.py`):

```python
# Prioriza Cap Rate individual
if 'fii' in tipo.lower():
    caprate = ativo.caprate if ativo.caprate else params['capratefii']
    pt_caprate = dy / (1 + caprate)
```

#### Critérios de Aceitação

- [ ] Migration criada
- [ ] Campo aceita NULL (default: usa `parametrosmacro`)
- [ ] Constraint: `caprate >= 0` e `caprate <= 100`
- [ ] Lógica de Preço Teto atualizada
- [ ] Testes: FII com caprate próprio, FII sem caprate (usa regional)

---

### Issue #11: [P2] Adicionar campo `setor` em tabela Ativo

**Labels**: `priority: low`, `database`, `enhancement`, `reports`  
**Milestone**: Backlog  
**Assignees**: [Backend Team]

#### Descrição

Adicionar campo `setor` para classificação setorial de ativos (ex: "Tecnologia", "Energia", "Financeiro").

#### Especificação

```sql
ALTER TABLE ativo ADD COLUMN setor VARCHAR(50) NULL;
CREATE INDEX ix_ativo_setor ON ativo(setor);
COMMENT ON COLUMN ativo.setor IS 'Setor econômico (ex: Tecnologia, Petróleo, Bancos)';
```

**Casos de Uso**:
- Relatório de diversificação setorial
- Dashboard: alocação por setor
- Filtros avançados de busca

#### Critérios de Aceitação

- [ ] Migration criada
- [ ] Índice `ix_ativo_setor` criado
- [ ] Seed atualizado com setores dos 25 ativos
- [ ] Endpoint `/api/portfolio/alocacao-setor` (NOVO)

---

### Issue #12: [P2] Implementar view materializada para dashboards

**Labels**: `priority: low`, `database`, `performance`, `optimization`  
**Milestone**: Backlog  
**Assignees**: [Backend Team]

#### Descrição

Criar view materializada `vw_portfolio_consolidado` para otimizar queries do dashboard (atualização a cada 15min via job Celery).

#### Especificação

```sql
CREATE MATERIALIZED VIEW vw_portfolio_consolidado AS
SELECT 
    u.id AS usuarioid,
    COUNT(DISTINCT p.ativoid) AS numativos,
    SUM(p.custototal) AS custototal,
    SUM(p.valoratual) AS valoratual,
    SUM(p.lucroprejuizonaorealizado) AS lucrototal
FROM usuario u
LEFT JOIN posicao p ON p.usuarioid = u.id
GROUP BY u.id;

CREATE UNIQUE INDEX idx_vw_portfolio_usuario ON vw_portfolio_consolidado(usuarioid);
```

**Job Celery**:
```python
@celery.task
def refresh_portfolio_view():
    db.session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY vw_portfolio_consolidado')
    db.session.commit()

# Agendar: a cada 15 minutos
beat_schedule['refresh-portfolio-view'] = {
    'task': 'refresh_portfolio_view',
    'schedule': crontab(minute='*/15')
}
```

#### Critérios de Aceitação

- [ ] View materializada criada
- [ ] Job Celery de refresh (15 min)
- [ ] Query do dashboard usa view (performance +80%)

---

### Issue #13: [P2] Avaliar particionamento de tabela `transacao`

**Labels**: `priority: low`, `database`, `performance`, `research`  
**Milestone**: Backlog  
**Assignees**: [Database Team]

#### Descrição

Estudar viabilidade de particionar tabela `transacao` por ano (`datatransacao`) para melhorar performance em bases com milhões de registros.

#### Especificação

```sql
-- Particionamento por ano
CREATE TABLE transacao_2025 PARTITION OF transacao 
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE transacao_2026 PARTITION OF transacao 
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

#### Critérios de Decisão

- **Implementar se**: Volume de transações > 1 milhão/ano
- **Não implementar se**: Volume < 100k transações

#### Entregável

- [ ] Documento de análise: `docs/PARTICIONAMENTO_TRANSACAO_ANALYSIS.md`
- [ ] Benchmark: queries COM vs SEM particionamento
- [ ] Recomendação: SIM/NÃO + justificativa

---

## 📊 Resumo das Issues

| Prioridade | Quantidade | Labels Principais | Milestone |
|------------|------------|-------------------|-----------|
| **P0** | 5 issues | `critical`, `database`, `backend` | Sprint 1 |
| **P1** | 4 issues | `high`, `celery`, `integration` | Sprint 2 |
| **P2** | 4 issues | `low`, `enhancement`, `performance` | Backlog |
| **TOTAL** | **13 issues** | - | - |

---

## 🔗 Referências

- [docs/revisoes/README.md](../docs/revisoes/README.md)
- [docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md](../docs/revisoes/REVISAO_MODULO_1_BANCO_DADOS.md)
- [docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md](../docs/revisoes/REVISAO_MODULOS_2-4_APIS_CALCULOS.md)
- [docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md](../docs/revisoes/MATRIZ_COMPLIANCE_ER_APIS.md)

---

**Gerado automaticamente em**: 06/01/2026 13:26 -03  
**Versão**: 1.0
