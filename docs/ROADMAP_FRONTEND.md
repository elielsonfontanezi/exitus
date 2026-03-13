# 🎨 Exitus — Roadmap Frontend Reengenharia

> **Status:** 📋 Planejamento Concluído  
> **Versão:** 1.1  
> **Data:** 13/03/2026 (atualizado)  
> **Modelo IA Recomendado:** Claude Sonnet (complexidade moderada-alta)

---

## 📊 Visão Geral

### **Situação Atual**
- ✅ **Backend robusto:** 491 testes (100%), 67+ endpoints, motor fiscal completo
- ⚠️ **Frontend básico:** HTMX + Alpine.js + Tailwind, funcional mas limitado
- ❌ **UX incompleta:** Sem diferenciação multi-mercado, componentização fraca

### **Objetivo da Reengenharia**
Elevar o frontend ao nível de profissionalismo do backend, mantendo a stack atual (HTMX + Alpine.js) mas com:
- ✅ Componentização sistemática
- ✅ UX especializada multi-mercado
- ✅ Novo módulo "Planos de Compra"
- ✅ Gráficos avançados (Chart.js)
- ✅ Responsividade mobile-first

### **Progresso Atual (13/03/2026)**
- ✅ **Documentação técnica completa:** ROADMAP_FRONTEND.md criado
- ✅ **Wireframes ASCII:** 12 telas completas (3 prioritárias + 9 restantes)
- ✅ **Estratégia definida:** Componentização primeiro, telas depois
- ✅ **Protótipos validados:** Opção B (wireframes antes de implementar)

---

## 📐 Wireframes ASCII Criados

### **Arquivo de Referência:** `docs/PROTOTIPOS_FRONTEND_RESUMO.md`

**3 Telas Prioritárias (já validadas):**
1. **Dashboard Multi-Mercado** - Cards por mercado, gráficos, Top 5 ativos
2. **Buy Signals** - Análise individual com score visual e indicadores
3. **Planos de Compra** - Lista priorizada de oportunidades com carrinho

**9 Telas Restantes (wireframes criados):**
4. **Assets** - Ativos Cadastrados (tabela com filtros)
5. **Portfolios** - Gestão de Carteiras (cards de resumo)
6. **Transactions** - Histórico de Transações (tabela detalhada)
7. **Dividends** - Proventos e Calendário (gráfico + próximos)
8. **Analytics** - Analíticas (performance por ativo)
9. **Movimentações** - Movimentações de Caixa (fluxo financeiro)
10. **Alerts** - Sistema de Alertas (notificações)
11. **Reports** - Relatórios e Auditoria (lista de relatórios)
12. **Report Detail** - Detalhe de Relatório (relatório completo)

**Total:** 12 wireframes ASCII completos com layout, componentes e integrações

---

## 🎯 Decisões Estratégicas

### **1. Stack Tecnológico: MANTER HTMX + Alpine.js**

**Justificativa:**
- ✅ Curva de aprendizado baixa
- ✅ Sem build step (deploy direto)
- ✅ Leve (~50KB total)
- ✅ Server-side rendering (SEO friendly)
- ✅ Adequado para complexidade atual

**Alternativas Avaliadas e Descartadas:**
- ❌ **Next.js (React):** Overhead excessivo, curva de aprendizado alta
- ❌ **Vue.js + Nuxt:** Ainda requer build, menos adoção

**Critério de Reavaliação:**
> Se >60% dos templates precisarem refatoração completa, reconsiderar Vue.js

---

### **2. Estrutura de Navegação: 3 Telas Separadas**

```
/dashboard/assets        → Gestão de Ativos (cadastro, edição)
/dashboard/buy-signals   → Análise Individual (score detalhado)
/dashboard/planos-compra → Decisão de Investimento (NOVO)
```

**Diferenças Funcionais:**

| Aspecto | Ativos | Buy Signals | Planos de Compra |
|---------|--------|-------------|------------------|
| **Objetivo** | Cadastro | Análise individual | Decisão de investimento |
| **Escopo** | Todos (70+) | 1 ativo por vez | Top 10 oportunidades |
| **Score** | ❌ Não | ✅ Detalhado | ✅ Comparativo |
| **Comparação** | ❌ Não | ❌ Não | ✅ Lado a lado |
| **Sugestão** | ❌ Não | ❌ Não | ✅ Quantidade + valor |
| **Integração Carteira** | ❌ Não | ❌ Não | ✅ Mostra posições |

---

### **3. Requisitos do Usuário (Confirmados)**

| Requisito | Resposta | Implicação |
|-----------|----------|------------|
| Prioridade #1 | Dashboard Multi-Mercado | ✅ Fase 1 |
| Mercado principal | Apenas Brasil 🇧🇷 | ⚠️ Foco BR, preparar expansão |
| Dispositivos | 50/50 Desktop/Mobile | ✅ Responsividade obrigatória |
| Primeira visualização | Patrimônio consolidado | ✅ Hero section |
| Moeda | Toggle BRL/USD | ✅ Switch de moeda |
| Priorização | Score + Margem + Teto + Customizável | ✅ Filtros avançados |
| Layout | Cards grandes | ✅ Design limpo e espaçoso |
| Gráficos | Pizza + Linha + outras opções | ✅ Chart.js múltiplos tipos |

---

## 🏗️ Arquitetura de Componentes

### **Biblioteca Proposta: `frontend/app/templates/components/`**

```
components/
├── cards/
│   ├── stat_card.html              # KPI genérico (patrimônio, rentabilidade)
│   ├── market_stat_card.html       # KPI por mercado (🇧🇷 🇺🇸 🌍)
│   ├── asset_card.html             # Card de ativo individual
│   ├── opportunity_card.html       # Card de oportunidade (Planos de Compra)
│   └── portfolio_summary_card.html # Resumo de carteira
│
├── badges/
│   ├── market_badge.html           # 🇧🇷 BR | 🇺🇸 US | 🌍 INTL
│   ├── currency_badge.html         # BRL | USD | EUR
│   ├── asset_type_badge.html       # ACAO | FII | STOCK | REIT
│   ├── score_badge.html            # 🟢 85 | 🟡 65 | 🔴 40
│   └── signal_badge.html           # COMPRAR | AGUARDAR | VENDER
│
├── tables/
│   ├── data_table.html             # Tabela genérica com sorting
│   ├── asset_table.html            # Tabela de ativos
│   ├── transaction_table.html      # Tabela de transações
│   ├── dividend_table.html         # Tabela de proventos
│   └── opportunity_table.html      # Tabela de oportunidades
│
├── charts/
│   ├── allocation_pie_chart.html   # Pizza (alocação geográfica)
│   ├── evolution_line_chart.html   # Linha (evolução patrimonial)
│   ├── performance_bar_chart.html  # Barra (performance por ativo)
│   └── chart_wrapper.html          # Wrapper genérico Chart.js
│
├── forms/
│   ├── filter_form.html            # Formulário de filtros
│   ├── search_bar.html             # Barra de busca
│   ├── currency_toggle.html        # Toggle BRL/USD
│   └── modal_form.html             # Modal genérico
│
├── layout/
│   ├── page_header.html            # Cabeçalho de página
│   ├── section_divider.html        # Divisor de seção
│   └── empty_state.html            # Estado vazio (sem dados)
│
└── utils/
    ├── loading_spinner.html        # Spinner de carregamento
    ├── toast_notification.html     # Notificação toast
    └── pagination.html             # Paginação
```

**Total:** 28 componentes reutilizáveis

---

## 📋 Roadmap de Implementação

### **FASE 1: Fundação e Componentização (2 semanas)**

#### **Sprint 1.1: Biblioteca de Componentes Base (Semana 1)**

**Artefatos a criar:**
```
components/badges/
├── market_badge.html (🇧🇷 🇺🇸 🌍)
├── currency_badge.html (BRL USD EUR)
├── score_badge.html (🟢 🟡 🔴)
└── signal_badge.html (COMPRAR AGUARDAR VENDER)

components/cards/
├── stat_card.html (genérico)
├── market_stat_card.html (por mercado)
├── asset_card.html (ativos individuais)
├── opportunity_card.html (oportunidades Planos de Compra)
└── portfolio_summary_card.html (resumo carteiras)

components/tables/
├── data_table.html (genérico com sorting)
├── asset_table.html (ativos cadastrados)
├── transaction_table.html (histórico transações)
├── dividend_table.html (proventos)
└── opportunity_table.html (Planos de Compra)

components/charts/
├── allocation_pie_chart.html (alocação geográfica)
├── evolution_line_chart.html (evolução patrimonial)
├── performance_bar_chart.html (performance por ativo)
└── chart_wrapper.html (wrapper genérico Chart.js)

components/forms/
├── filter_form.html (filtros genéricos)
├── search_bar.html (busca)
├── currency_toggle.html (BRL ⇄ USD)
└── modal_form.html (modal genérico)

components/layout/
├── page_header.html (cabeçalho de página)
├── section_divider.html (divisor de seção)
└── empty_state.html (estado vazio)

components/utils/
├── loading_spinner.html (spinner de carregamento)
├── toast_notification.html (notificações toast)
└── pagination.html (paginação)
```

**Testes:**
- [ ] Renderização de badges em diferentes contextos
- [ ] Toggle de moeda funcional
- [ ] Cards responsivos (mobile/desktop)
- [ ] Tables com sorting/filtering
- [ ] Gráficos Chart.js funcionais
- [ ] Forms com validação

**Entregável:** 28 componentes base funcionais

---

#### **Sprint 1.2: Dashboard Multi-Mercado MVP (Semana 2)**

**Modificar:** `/dashboard/` (index.html)

**Implementar:**
1. Seção "Patrimônio Consolidado" (3 cards por mercado)
2. Toggle BRL/USD funcional (Alpine.js)
3. Integração com endpoint `/api/portfolios/dashboard`
4. Cards responsivos (grid adaptativo)

**Backend necessário:**
```python
# Modificar endpoint existente
GET /api/portfolios/dashboard

Response:
{
  "patrimonio_por_mercado": {
    "BR": {
      "total_brl": 50000,
      "percentual": 60,
      "rentabilidade_mes": 8.5
    },
    "US": {
      "total_usd": 10000,
      "percentual": 30,
      "rentabilidade_mes": 12.3
    },
    "INTL": {
      "total_eur": 2000,
      "percentual": 10,
      "rentabilidade_mes": 5.2
    }
  },
  "total_consolidado_brl": 68450,
  "total_consolidado_usd": 13690,
  "rentabilidade_geral_mes": 9.2,
  "rentabilidade_geral_ano": 24.5
}
```

**Testes:**
- [ ] Toggle BRL/USD alterna valores
- [ ] Cards exibem dados corretos
- [ ] Responsivo em mobile (320px)

**Entregável:** Dashboard Multi-Mercado funcional

---

### **FASE 2: Gráficos e Visualizações (2 semanas)**

#### **Sprint 2.1: Integração Chart.js (Semana 3)**

**Adicionar dependência:**
```html
<!-- Chart.js 4.x via CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Criar componentes:**
```
components/charts/
├── allocation_pie_chart.html (alocação geográfica)
├── evolution_line_chart.html (evolução patrimonial)
└── chart_wrapper.html (wrapper genérico)
```

**Implementar no Dashboard:**
1. Gráfico Pizza: Alocação 🇧🇷 60% | 🇺🇸 30% | 🌍 10%
2. Gráfico Linha: Evolução últimos 12 meses

**Backend necessário:**
```python
# Novo endpoint
GET /api/analytics/alocacao-geografica

Response:
{
  "data": [
    {"mercado": "BR", "percentual": 60, "valor_brl": 50000},
    {"mercado": "US", "percentual": 30, "valor_brl": 20450},
    {"mercado": "INTL", "percentual": 10, "valor_brl": 6800}
  ]
}

# Novo endpoint
GET /api/analytics/evolucao-patrimonial?meses=12

Response:
{
  "data": [
    {"mes": "2025-01", "br": 45000, "us": 8000, "intl": 1500, "total": 54500},
    {"mes": "2025-02", "br": 47000, "us": 8500, "intl": 1800, "total": 57300},
    ...
  ]
}
```

**Testes:**
- [ ] Gráfico Pizza renderiza corretamente
- [ ] Gráfico Linha mostra evolução temporal
- [ ] Responsivo (adapta em mobile)

**Entregável:** 2 gráficos funcionais no Dashboard

---

#### **Sprint 2.2: Top 5 Ativos por Mercado (Semana 4)**

**Criar componente:**
```
components/cards/asset_card.html
```

**Implementar seção no Dashboard:**
- Top 5 Brasil (cards horizontais)
- Top 5 EUA (cards horizontais)
- Responsivo (stack vertical em mobile)

**Backend necessário:**
```python
# Novo endpoint
GET /api/portfolios/top-ativos?mercado=BR&limit=5

Response:
{
  "data": [
    {
      "ticker": "VALE3",
      "nome": "Vale ON",
      "preco_atual": 72.00,
      "variacao_dia": 2.5,
      "quantidade": 150,
      "valor_posicao": 10800
    },
    ...
  ]
}
```

**Testes:**
- [ ] Cards exibem top 5 por mercado
- [ ] Variação positiva/negativa com cores
- [ ] Responsivo (2 colunas → 1 coluna)

**Entregável:** Seção "Top 5 Ativos" funcional

---

### **FASE 3: Planos de Compra (2 semanas)**

#### **Sprint 3.1: Backend Planos de Compra (Semana 5)**

**Criar novo blueprint:**
```
backend/app/blueprints/planos_compra_blueprint.py
```

**Endpoints:**
```python
# 1. Listar oportunidades priorizadas
GET /api/planos-compra/oportunidades
Params: saldo_disponivel, moeda, score_min, margem_min, mercado
Response: Lista priorizada de oportunidades

# 2. Salvar plano de compra
POST /api/planos-compra/salvar
Body: {ativos: [{ticker, quantidade, valor}], total}
Response: plano_id

# 3. Listar planos salvos
GET /api/planos-compra/meus-planos
Response: Lista de planos salvos
```

**Service:**
```
backend/app/services/planos_compra_service.py
├── calcular_oportunidades(usuario_id, filtros)
├── priorizar_ativos(ativos, criterios)
└── sugerir_quantidade(ativo, saldo_disponivel)
```

**Testes:**
- [ ] Endpoint oportunidades retorna top 10
- [ ] Priorização por score + margem funciona
- [ ] Salvar plano persiste no banco

**Entregável:** Backend Planos de Compra funcional

---

#### **Sprint 3.2: Frontend Planos de Compra (Semana 6)**

**Criar página:**
```
frontend/app/templates/dashboard/planos_compra.html
```

**Componentes:**
```
components/cards/opportunity_card.html
components/tables/opportunity_table.html
```

**Funcionalidades:**
1. Filtros customizáveis (score, margem, mercado)
2. Lista priorizada de oportunidades
3. Adicionar/remover do plano
4. Cálculo automático de total
5. Validação de saldo disponível
6. Salvar/exportar plano

**Testes:**
- [ ] Filtros funcionam corretamente
- [ ] Adicionar ao plano atualiza total
- [ ] Validação de saldo exibe alerta
- [ ] Salvar plano chama API corretamente

**Entregável:** Tela Planos de Compra completa

---

### **FASE 4: Melhorias UX e Polimento (2 semanas)**

#### **Sprint 4.1: Refatoração Buy Signals (Semana 7)**

**Melhorar:** `/dashboard/buy-signals`

**Implementações:**
1. Layout mais visual (cards grandes)
2. Gráficos de indicadores (Chart.js radial)
3. Histórico de análises
4. Integração com alertas

**Testes:**
- [ ] Layout visual melhora UX
- [ ] Gráfico radial exibe indicadores
- [ ] Histórico persiste entre sessões

**Entregável:** Buy Signals redesenhado

---

#### **Sprint 4.2: Refatoração Assets (Semana 8)**

**Melhorar:** `/dashboard/assets`

**Implementações:**
1. Tabela com sorting/filtering (Alpine.js)
2. Modal de edição inline
3. Badges visuais (mercado, tipo, moeda)
4. Paginação funcional
5. Busca em tempo real

**Testes:**
- [ ] Sorting funciona em todas as colunas
- [ ] Filtros combinam corretamente
- [ ] Modal edita sem reload
- [ ] Busca filtra em tempo real

**Entregável:** Assets redesenhado

---

## 📊 Métricas de Sucesso

| Métrica | Antes | Meta | Como Medir |
|---------|-------|------|------------|
| **Componentes reutilizáveis** | 4 | 28 | Contar arquivos em `components/` |
| **Páginas com UX profissional** | 0 | 3 | Dashboard, Buy Signals, Planos de Compra |
| **Gráficos interativos** | 0 | 4 | Pizza, Linha, Barra, Radial |
| **Responsividade mobile** | 60% | 100% | Teste em 320px, 768px, 1024px |
| **Tempo de carregamento** | ~2s | <1s | Chrome DevTools Network |
| **Satisfação do usuário** | N/A | 8/10 | Feedback direto |

---

## 🚧 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| HTMX não escala para complexidade | Baixa | Alto | Critério de reavaliação definido (60%) |
| Chart.js performance em mobile | Média | Médio | Lazy loading, limitar pontos de dados |
| Backend não retorna dados esperados | Baixa | Alto | Validar endpoints antes de implementar |
| Usuário rejeita novo design | Baixa | Alto | Protótipos HTML para aprovação prévia |

---

## 📦 Entregáveis por Fase

### **Fase 1 (Semanas 1-2):**
- [ ] 8 componentes base (badges, cards, utils)
- [ ] Dashboard Multi-Mercado MVP
- [ ] Toggle BRL/USD funcional
- [ ] Documentação de componentes

### **Fase 2 (Semanas 3-4):**
- [ ] 3 componentes de gráficos
- [ ] 2 novos endpoints backend (analytics)
- [ ] Gráfico Pizza (alocação)
- [ ] Gráfico Linha (evolução)
- [ ] Seção Top 5 Ativos

### **Fase 3 (Semanas 5-6):**
- [ ] Backend Planos de Compra (3 endpoints)
- [ ] Service planos_compra_service.py
- [ ] Frontend Planos de Compra completo
- [ ] 2 novos componentes (opportunity_card, opportunity_table)

### **Fase 4 (Semanas 7-8):**
- [ ] Buy Signals redesenhado
- [ ] Assets redesenhado
- [ ] Testes E2E (Cypress/Playwright)
- [ ] Documentação final

---

## 🔄 Processo de Aprovação

### **Antes de Implementar:**
1. ✅ Protótipos HTML estáticos criados
2. ✅ Validação visual com mantenedor
3. ✅ Discussão de UX e ajustes
4. ✅ Aprovação explícita ("APROVADO")

### **Durante Implementação:**
- Commits atômicos por componente
- Testes unitários para cada componente
- Validação incremental com mantenedor

### **Após Implementação:**
- Suite de testes passando (491 + novos)
- Documentação atualizada (CHANGELOG, README)
- Deploy em ambiente de staging
- Aprovação final do mantenedor

---

## 📚 Documentação Relacionada

### **Leitura Obrigatória:**
- `ROADMAP_BACKEND.md` - Status backend, GAPs concluídos
- `API_REFERENCE.md` - Contratos dos endpoints
- `VISION.md` - Proposta de valor do sistema
- `CODING_STANDARDS.md` - Padrões de código

### **Referência:**
- `ARCHITECTURE.md` - Stack e containers
- `ENUMS.md` - Tipos de ativos e mapeamentos
- `PERSONAS.md` - Manual de operação da IA

---

## 🎯 Próximos Passos Imediatos

1. **Criar protótipos HTML estáticos** (3 telas principais)
2. **Validar visualmente** com mantenedor
3. **Ajustar conforme feedback**
4. **Obter aprovação** para iniciar implementação
5. **Executar Fase 1** (componentização)

---

## 📝 Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 12/03/2026 | Cascade (Claude Sonnet) | Versão inicial - planejamento completo |

---

**Status:** 📋 Aguardando aprovação de protótipos HTML  
**Próxima Ação:** Criar protótipos estáticos para validação visual
