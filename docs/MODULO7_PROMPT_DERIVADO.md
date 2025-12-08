# 🎯 MÓDULO 7: Relatórios e Análises Avançadas - PROMPT DERIVADO

**Data Criação:** 07/12/2025 18:13
**Status:** DEVELOPMENT
**Versão:** 1.0

---

## 📋 CONTEXTO GERAL

Continuação do desenvolvimento do sistema **Exitus - Sistema de Controle e Análise de Investimentos Global**, a partir do **estado estável do Módulo 6**.

Este tópico implementará o **Módulo 7: Relatórios e Análises Avançadas**.

---

## 📊 ESTADO ATUAL DO PROJETO

### Containers Rodando
```
✅ exitus-db (PostgreSQL 15) - Operacional
✅ exitus-backend (Flask) - API REST com 30+ endpoints
✅ exitus-frontend (porta 8080) - Interface com dashboards
```

### Módulos Concluídos
```
✅ Módulo 0: Infraestrutura Podman (rede, volumes, containers)
✅ Módulo 1: Database Backend (14 models, 90+ índices, 15 FKs)
✅ Módulo 2: API REST CRUD (auth + 4 entidades)
✅ Módulo 3: Entidades Financeiras (posicoes/proventos/movimentacoes/eventos)
✅ Módulo 4: Backend API Integrações + Buy Signals 🌟
✅ Módulo 5: Frontend Base + Autenticação 🌟
✅ Módulo 6: Container 3 - Frontend (Dashboards e Visualizações) 🌟
```

### M6 ESTADO FINAL - Funcionalidades Implementadas

#### M6.1 - Buy Signals ✅
- Tabela com badges coloridos por score (verde ≥80, amarelo 60-79, vermelho <60)
- Bandeiras por mercado (Brasil, EUA, Europa)
- Botões "Comprar" funcionais com POST /portfolio/compra
- Gráfico Chart.js distribuição mercados (doughnut: BR=2, US=1)
- 3 cards stats (Total Sinais, Sinais Fortes, Margem Média)
- Mock data: PETR4, VALE3, AAPL

#### M6.2 - Portfolios/Carteiras ✅
- Modal "Nova Carteira" com 6 campos (Nome, Tipo, País, Moeda, Saldo, Observações)
- Botão submit POST /portfolios/create funcional
- 4 cards stats (Total: 3, Ativas: 3, Saldo BR, Saldo US)
- Badges status coloridos (ATIVA verde / INATIVA cinza)
- Mock data: XP Investimentos, Clear Corretora, Avenue Securities

#### M6.3 - Transações ✅
- Suporte a 7 tipos de ativos (ação, FII, REIT, bond, ETF, cripto, outro)
- Filtros avançados (6 campos: Tipo, Classe, Mercado, Corretora, Datas)
- Badges azuis tipos de ativo + bandeiras mercado
- 2 gráficos Chart.js com valores financeiros reais
- Modal "Nova Transação" completo
- Mock data: 5 transações

#### M6.4 - Proventos (Dividendos/JCP) ✅
- Tabela com dividendos, JCP e rendimentos
- Badges PAGO (verde) / PREVISTO (amarelo) coloridos
- Filtros (5 campos: Ativo, Tipo, Status, Datas)
- Gráfico linha "Evolução Mensal" funcional
- 4 cards stats (Total: 5, Recebido, A Receber, Total Geral)
- Mock data: PETR4, VALE3, MXRF11, AAPL, HGLG11

---

## 📁 ARQUIVOS DE REFERÊNCIA DISPONÍVEIS

Documentação e checklists para análise:

```
├── PROMPT_MESTRE_EXITUS_V10_FINAL.md      ← Arquitetura completa
├── MODULO0_CHECKLIST.md                   ← Infraestrutura Podman ✅
├── MODULO1_CHECKLIST.md                   ← Database Backend ✅
├── MODULO2_CHECKLIST.md                   ← API REST CRUD ✅
├── MODULO3_CHECKLIST.md                   ← Entidades Financeiras ✅
├── MODULO4_CHECKLIST.md                   ← Buy Signals API ✅
├── MODULO5_CHECKLIST.md                   ← Frontend Base ✅
├── MODULO6_CHECKLIST.md                   ← Dashboards Frontend ✅
├── modulo6_frontend_dashboards.md         ← Docs M6
├── modulo6_fontest.txt                    ← Fontes M1-M6 completo
└── docs/                                  ← Documentação modular
```

---

## 🎯 OBJETIVO MÓDULO 7: Relatórios e Análises Avançadas

Implementar capacidade de gerar **relatórios consolidados** multi-dimensão com análises de performance, projeções de renda passiva, alertas inteligentes e exportação em múltiplos formatos.

### Escopo Principal

| Fase | Componente | Descrição | Status |
|------|-----------|-----------|--------|
| 7.1 | **Backend: Models** | AuditoriaRelatorio, ConfiguracaoAlerta, ProjecaoRenda | ⏳ |
| 7.2 | **Backend: Services** | relatório_service, alerta_service, projeção_service | ⏳ |
| 7.3 | **Backend: API Endpoints** | GET/POST endpoints relatórios (12+ endpoints) | ⏳ |
| 7.4 | **Backend: Cálculos** | Analytics avançados (IRR, taxa crescimento, volatilidade) | ⏳ |
| 7.5 | **Frontend: Relatórios** | Visualizações avançadas com Chart.js | ⏳ |
| 7.6 | **Frontend: Alertas** | Sistema notificações em tempo real (websocket) | ⏳ |
| 7.7 | **Exportação** | PDF/Excel com ReportLab ou openpyxl | ⏳ |
| 7.8 | **Testes & Docs** | Checklist, testes, documentação completa | ⏳ |

---

## 🏗️ ARQUITETURA MÓDULO 7

### 7.1 - Backend: Models Novos (SQLAlchemy)

**Arquivo:** `backend/models/auditoria_relatorio.py`

```python
# AuditoriaRelatorio
- id: UUID (PK)
- usuario_id: UUID (FK usuarios)
- tipo_relatorio: Enum [PORTFOLIO, PERFORMANCE, RENDA_PASSIVA, INVESTIMENTO, CUSTOMIZADO]
- data_inicio: Date
- data_fim: Date
- filtros: JSON (país, mercado, setor, classe_ativo)
- resultado_json: JSON (dados completos)
- timestamp_criacao: DateTime
- timestamp_download: DateTime (null até primeiro download)
- formato_export: Enum [VISUALIZACAO, PDF, EXCEL]
- chave_api_auditoria: String (para rastreamento)
```

**Arquivo:** `backend/models/configuracao_alerta.py`

```python
# ConfiguracaoAlerta
- id: UUID (PK)
- usuario_id: UUID (FK usuarios)
- nome: String (ex: "Alerta PETR4 > 30%")
- tipo_alerta: Enum [QUEDA_PRECO, ALTA_PRECO, DIVIDENDO_PREVISTO, META_RENTABILIDADE, VOLATILIDADE_ALTA, DESVIO_ALOCACAO, NOTICIAS_ATIVO]
- ativo_id: UUID (FK ativos, nullable)
- portfolio_id: UUID (FK portfolios, nullable)
- condicao_valor: Decimal (threshold)
- condicao_operador: Enum [>, <, ==, >=, <=, ENTRE]
- condicao_valor2: Decimal (nullable, para ENTRE)
- ativo: Boolean (default=True)
- frequencia_notificacao: Enum [IMEDIATA, DIARIA, SEMANAL, MENSAL]
- canais_entrega: Array [EMAIL, WEBAPP, SMS, TELEGRAM]
- timestamp_criacao: DateTime
- timestamp_ultimo_acionamento: DateTime (null se nunca acionado)
```

**Arquivo:** `backend/models/projecao_renda.py`

```python
# ProjecaoRenda
- id: UUID (PK)
- usuario_id: UUID (FK usuarios)
- portfolio_id: UUID (FK portfolios)
- mes_ano: YearMonth (ex: 2025-12)
- renda_dividendos_projetada: Decimal
- renda_jcp_projetada: Decimal
- renda_rendimento_projetada: Decimal
- renda_total_mes: Decimal (soma das acima)
- renda_anual_projetada: Decimal
- crescimento_percentual_mes: Decimal
- crescimento_percentual_ano: Decimal
- ativos_contribuindo: Integer (quantidade)
- timestamp_calculo: DateTime
- metadados: JSON (detalhes por ativo)
```

**Arquivo:** `backend/models/relatorio_performance.py`

```python
# RelatorioPerformance
- id: UUID (PK)
- usuario_id: UUID (FK usuarios)
- portfolio_id: UUID (FK portfolios)
- periodo_inicio: Date
- periodo_fim: Date
- retorno_bruto_percentual: Decimal
- retorno_liquido_percentual: Decimal
- volatilidade_percentual: Decimal
- indice_sharpe: Decimal
- indice_sortino: Decimal
- max_drawdown_percentual: Decimal
- taxa_interna_retorno_irr: Decimal
- beta_mercado: Decimal
- alfa_de_jensen: Decimal
- valor_patrimonial_inicio: Decimal
- valor_patrimonial_fim: Decimal
- alocacao_por_classe: JSON
- alocacao_por_setor: JSON
- alocacao_por_pais: JSON
- rentabilidade_por_ativo: JSON
- timestamp_calculo: DateTime
```

---

### 7.2 - Backend: Service Layer

**Arquivo:** `backend/services/relatorio_service.py`

Responsabilidades:
- Buscar dados agregados do portfolio (múltiplas tabelas)
- Calcular métricas consolidadas por período
- Aplicar filtros dimensionais (país, mercado, setor, classe)
- Gerar estrutura de dados para relatório
- Persistir auditoria em AuditoriaRelatorio

**Arquivo:** `backend/services/alerta_service.py`

Responsabilidades:
- Validar condições de alerta contra dados atuais
- Disparar notificações (email, app, SMS via Twilio)
- Rastrear acionamentos em timestamp_ultimo_acionamento
- Suportar batch de alertas por usuário
- Integração com fila (Celery) para envios assíncronos

**Arquivo:** `backend/services/projecao_service.py`

Responsabilidades:
- Calcular projeção de renda passiva até 12 meses
- Usar histórico de proventos para extrapolação
- Considerar taxa de crescimento esperada
- Atualizar tabela ProjecaoRenda mensalmente
- Fornecer visualizações por portfólio/ativo/mês

**Arquivo:** `backend/services/analise_service.py`

Responsabilidades:
- Cálculos avançados: IRR, Sharpe Ratio, Sortino, Max Drawdown
- Comparação com benchmarks (IBOVESPA, S&P500)
- Análise de correlação entre ativos
- Identificação de desvios de alocação
- Cálculos de beta e alfa de Jensen

---

### 7.3 - Backend: API Endpoints (20+ novos)

```
# RELATÓRIOS
GET    /api/relatorios/lista
GET    /api/relatorios/{id}
POST   /api/relatorios/gerar
POST   /api/relatorios/{id}/exportar
DELETE /api/relatorios/{id}

# ALERTAS
GET    /api/alertas/lista
GET    /api/alertas/{id}
POST   /api/alertas/criar
PUT    /api/alertas/{id}
DELETE /api/alertas/{id}
POST   /api/alertas/{id}/test
GET    /api/alertas/historico

# PROJEÇÕES
GET    /api/projecoes/renda
GET    /api/projecoes/renda/{portfolio_id}
POST   /api/projecoes/recalcular
GET    /api/projecoes/cenarios

# ANÁLISES AVANÇADAS
GET    /api/analises/performance
GET    /api/analises/correlacao
GET    /api/analises/desvio-alocacao
GET    /api/analises/benchmark

Total: 20+ endpoints
```

---

### 7.4 - Backend: Cálculos Avançados

#### IRR (Internal Rate of Return)
Método: Newton-Raphson iterativo
Entrada: Series de fluxos de caixa datados
Saída: Taxa anual (%)

#### Índice de Sharpe
Fórmula: (Retorno Portfolio - Taxa Livre Risco) / Desvio Padrão Retornos
Entrada: Série retornos diários, taxa livre risco (3% Selic atual)
Saída: Número > 1.0 = boa, > 2.0 = excelente

#### Índice de Sortino
Similar Sharpe, mas penaliza apenas desvio negativo (downside)
Entrada: Série retornos, target return
Saída: Número comparável a Sharpe

#### Volatilidade
Definição: Desvio padrão dos retornos
Entrada: Série preços
Saída: % ao ano (anualizado)

#### Max Drawdown
Definição: Maior queda acumulada do pico
Entrada: Série preços chronológica
Saída: % de queda máxima observada

---

## 🔄 FASES IMPLEMENTAÇÃO MÓDULO 7

### Fase 7.1: Backend - Models (SQLAlchemy)
**Duração:** 1h
**Checklist:**
- [ ] AuditoriaRelatorio model + migrate
- [ ] ConfiguracaoAlerta model + migrate
- [ ] ProjecaoRenda model + migrate
- [ ] RelatorioPerformance model + migrate
- [ ] Índices adicionados
- [ ] Relationships configurados
- [ ] Models registrados em __init__.py

### Fase 7.2: Backend - Service Layer
**Duração:** 2.5h
**Checklist:**
- [ ] RelatorioService
- [ ] AlertaService
- [ ] ProjecaoService
- [ ] AnaliseService
- [ ] Testes unitários
- [ ] Mock data

### Fase 7.3: Backend - API Endpoints
**Duração:** 2h
**Checklist:**
- [ ] RelatorioBlueprint
- [ ] AlertaBlueprint
- [ ] ProjecaoBlueprint
- [ ] AnaliseBlueprint
- [ ] Auth/permissões
- [ ] Validação com Marshmallow
- [ ] Documentação Swagger

### Fase 7.4: Backend - Cálculos
**Duração:** 2h
**Checklist:**
- [ ] IRR calculator
- [ ] Sharpe Ratio
- [ ] Volatilidade
- [ ] Max Drawdown
- [ ] Testes com dados reais
- [ ] Validação

### Fase 7.5: Backend - WebSocket
**Duração:** 1.5h
**Checklist:**
- [ ] flask-socketio
- [ ] Evento conectar_alertas
- [ ] Evento alerta_disparado
- [ ] Integração AlertaService
- [ ] Testes

### Fase 7.6: Frontend - Relatórios
**Duração:** 2h
**Checklist:**
- [ ] Página /dashboard/relatorios
- [ ] Modal "Novo Relatório"
- [ ] Página /dashboard/relatorios/{id}
- [ ] Chart.js integrado
- [ ] Botões export
- [ ] HTMX paginação
- [ ] Responsivo

### Fase 7.7: Frontend - Alertas
**Duração:** 2h
**Checklist:**
- [ ] Página /dashboard/alertas
- [ ] Modal "Novo Alerta"
- [ ] Página /dashboard/alertas/historico
- [ ] WebSocket integration
- [ ] Toast notification
- [ ] Status badges

### Fase 7.8: Frontend - Projeções
**Duração:** 1.5h
**Checklist:**
- [ ] Página /dashboard/projecoes/renda
- [ ] Seletor portfolio + cenário
- [ ] Gráfico bar chart
- [ ] Tabela detalhada
- [ ] Totalizações

### Fase 7.9: Exportação PDF/Excel
**Duração:** 1.5h
**Checklist:**
- [ ] ReportLab integration
- [ ] openpyxl integration
- [ ] Template PDF
- [ ] Múltiplas sheets Excel
- [ ] Formatação
- [ ] Download automático
- [ ] Testes

### Fase 7.10: Testes & Documentação
**Duração:** 2h
**Checklist:**
- [ ] test_relatorios_api.sh
- [ ] test_alertas_api.sh
- [ ] test_projecoes_api.sh
- [ ] test_exports.sh
- [ ] Performance tests
- [ ] Swagger docs
- [ ] README com exemplos

---

## 🚀 INSTRUÇÕES PARA IMPLEMENTAÇÃO

### 1. Sempre Considere Referências
- PROMPT_MESTRE_EXITUS_V10_FINAL.md (arquitetura)
- MODULO6_CHECKLIST.md (padrões implementados)
- modulo6_fontes.txt (código-fonte M1-M6)

### 2. Geração de Arquivos

#### Para arquivos .md (Markdown)
Criar para download com Python:
```bash
"Crie arquivo markdown para download: NOME.md"
```

#### Para arquivos de código
Exibir como bloco de código com caminho completo

### 3. Fluxo de Desenvolvimento
1. Criar arquivo(s) com código completo
2. Fornecer exemplos de uso/testes
3. Atualizar documentação
4. Confirmação do usuário antes de próxima fase

### 4. Atualização de Arquivos Existentes
Sempre fornecer versão COMPLETA:
- requirements.txt (com novas dependências)
- app.py / dashboard.py (com novas blueprints)
- models/__init__.py (com novos models)
- services/__init__.py (com novos services)

### 5. Git Workflow
```bash
git add .
git commit -m "✨ M7 Fase X: [Descrição]"
git log --oneline -1
```

---

## 📊 ESTADO FINAL ESPERADO (M7)

### Backend
✅ 4 models novos (SQLAlchemy)
✅ 4 services novos (lógica de negócio)
✅ 4 blueprints (20+ endpoints REST)
✅ 4 schemas (validação Marshmallow)
✅ 4 utilidades (cálculos estatísticos)
✅ WebSocket alertas (Flask-SocketIO)
✅ Exportação PDF/Excel (ReportLab + openpyxl)

Total: 45+ novos endpoints

### Frontend
✅ 3 novas páginas principais
✅ 3+ modais novos
✅ 5+ gráficos Chart.js
✅ WebSocket connection
✅ HTMX paginação/filtros
✅ Exportação automática
✅ Responsivo mobile 100%

### Documentação
✅ MODULO7_CHECKLIST.md
✅ modulo7_relatorios_analises.md
✅ modulo7_fontes.txt
✅ Swagger docs

---

## 🎯 SUCCESS CRITERIA

- ✅ Todos 20+ endpoints M7 retornam 200/201
- ✅ WebSocket alertas em tempo real funcionando
- ✅ Relatórios gerados em < 3 segundos
- ✅ PDF/Excel exportáveis sem erros
- ✅ Frontend responsivo (desktop + mobile)
- ✅ 90%+ testes passando
- ✅ Documentação 100% completa
- ✅ Pronto para M8

---

## 📞 SUPORTE

Dúvidas durante a implementação?
- Consulte PROMPT_MESTRE_EXITUS_V10_FINAL.md
- Analise modulo6_fontes.txt para padrões
- Valide com testes unitários a cada fase

---

**Próximo Passo:** Aguardando confirmação para iniciar Fase 7.1 (Backend Models).

Comando: `Iniciar M7 Fase 7.1`

---

*Versão 1.0 | 07/12/2025 18:13 | Status: PRONTO PARA IMPLEMENTAÇÃO*
