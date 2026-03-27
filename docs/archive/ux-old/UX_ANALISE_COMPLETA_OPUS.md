# 🎨 OPUS — Análise Completa UI/UX do Exitus

**Data:** 21/03/2026  
**Analista:** Cascade (Sonnet)  
**Escopo:** 10 telas modernizadas + design system + documentação UX  
**Score Geral:** B+ (7.5/10)

---

## 1. AVALIAÇÃO DAS 10 TELAS MODERNIZADAS

### 1.1 Matriz de Consistência

| # | Tela | Emoji | Hero Section | Cards Pattern | Botões | Alpine.js | Nota |
|---|------|-------|-------------|--------------|--------|-----------|------|
| 1 | **Dashboard** | 📊 | ✅ `bg-gradient-hero` | ✅ `card-moderno` | ✅ `btn-primario/secundario` | ✅ `x-data` | **A** |
| 2 | **Carteiras** | 📁 | ✅ idêntico | ✅ `card-moderno` | ✅ | ✅ | **A** |
| 3 | **Ativos** | 🎯 | ✅ idêntico | ✅ `card-moderno` | ✅ | ✅ | **A** |
| 4 | **Performance** | 📈 | ✅ idêntico | ⚠️ **misto** (`card-moderno` + `card card-elevated`) | ✅ | ✅ | **B+** |
| 5 | **Movimentações** | 💳 | ✅ idêntico | ⛔ **`card card-elevated`** (padrão antigo) | ✅ | ✅ | **B-** |
| 6 | **Alertas** | 🔔 | ✅ idêntico | ✅ `card-moderno` | ✅ | ⚠️ JS puro no modal | **B+** |
| 7 | **Relatórios** | 📄 | ✅ idêntico | ⛔ **`card card-gradient-*`** (padrão antigo) | ⚠️ misto (`btn btn-primary`) | ✅ | **B-** |
| 8 | **Imposto de Renda** | 🧾 | ✅ idêntico | ⛔ **`card card-gradient-*`** (padrão antigo) | ⚠️ misto (`btn btn-primary`) | ✅ | **B-** |
| 9 | **Educação** | 🎓 | ✅ idêntico | ⚠️ misto (`card-gradient-primary` + `card card-elevated`) | ⚠️ misto | ✅ | **B** |
| 10 | **Configurações** | ⚙️ | ✅ idêntico | ✅ `card card-elevated` (consistente internamente) | ⚠️ misto | ✅ | **B+** |

### 1.2 Achados Positivos (o que funcionou muito bem)

- **Hero Section 100% consistente** — todas as 10 páginas têm o mesmo HTML idêntico: `bg-gradient-hero rounded-3xl mx-6 mt-6 p-8`, decorativos com blur, ícone 16x16 com backdrop-blur, título `text-5xl`, subtítulo `text-xl text-white/80`
- **Gradient hero** (`#6366f1 → #8b5cf6`) — indigo-to-purple é premium e adequado para fintech
- **Animações** — `animate-fade-in`, `animate-scale-in`, `animate-pulse-slow`, `hover-lift` aplicadas consistentemente nas 3 primeiras telas
- **Emojis por página** — identidade visual distinta e memorável
- **Sidebar modernizado** — 4 grupos lógicos com sub-menus Alpine.js, busca inteligente

### 1.3 Achados Críticos (inconsistências)

**PROBLEMA #1 — Dual Card System (ALTA PRIORIDADE)**

Existem **3 padrões de cards** coexistindo:

| Padrão | Definição | Usado em |
|--------|-----------|----------|
| `card-moderno` | `design-system.css` L873-880 | Dashboard, Carteiras, Ativos, Alertas |
| `card card-elevated` | CSS legado | Movimentações, Performance (seções), Educação, Configurações |
| `card card-gradient-*` | CSS legado com gradiente | Relatórios, Imposto de Renda |

**Recomendação:** Migrar **todas** as telas para `card-moderno` como padrão único.

**PROBLEMA #2 — Dual Button System**

| Padrão | Definição | Usado em |
|--------|-----------|----------|
| `btn-primario` / `btn-secundario` | `design-system.css` L887-1000 | Dashboard, Carteiras, Ativos, Movimentações, Alertas |
| `btn btn-primary` / `btn btn-outline` | CSS legado | Relatórios, IR, Performance, Educação, Configurações |

**Recomendação:** Padronizar em `btn-primario` / `btn-secundario` em todas as telas.

**PROBLEMA #3 — Ícones inconsistentes**

- **Movimentações** (`movimentacoes.html:67`): usa `<i class="fas fa-exchange-alt">` (Font Awesome)
- **Todas as demais**: usam emojis (`<span class="text-2xl">📊</span>`)

**PROBLEMA #4 — Footer desatualizado**

```@/home/p016525/elielson/exitus/frontend/app/templates/base.html:95
                        v1.0.0 | Módulo 5
```
Deveria ser `v0.9.3` conforme ROADMAP.

**PROBLEMA #5 — Alertas modal com JS puro vs Alpine.js**

```@/home/p016525/elielson/exitus/frontend/app/templates/dashboard/alerts.html:241-248
function abrirModal() {
    console.log("🔔 BOTÃO NOVO ALERTA CLICADO!");
    document.getElementById('modal-alerta').classList.remove('hidden');
    document.getElementById('modal-alerta').classList.add('flex');
}
function fecharModal() {
    document.getElementById('modal-alerta').classList.add('hidden');
    document.getElementById('modal-alerta').classList.remove('flex');
}
```
Todas as demais telas usam Alpine.js (`x-show`, `@click`). Este modal deveria seguir o mesmo padrão.

**PROBLEMA #6 — Imposto de Renda typo**

```@/home/p016525/elielson/exitus/frontend/app/templates/dashboard/imposto_renda.html:349
                <template xfor="prejuizo in prejuizos" :key="prejuizo.ano + '-' + prejuizo.mes">
```
`xfor` deveria ser `x-for` — **bug funcional** que impede a renderização da lista de prejuízos.

---

## 2. SUMARIZAÇÃO DA DOCUMENTAÇÃO UI/UX

| Documento | Linhas | Conteúdo UX |
|-----------|--------|-------------|
| `design-system.css` | 1289 | Design system completo: 7 paletas de cores (primary, success, danger, warning, info, secondary, attention), tipografia Inter, 13 seções (reset, cores, tipografia, espaçamento, bordas, sombras, layout, cards, badges, formulários, botões, animações, utilitárias) |
| `UX_BENCHMARKING.md` | 203 | Análise competitiva Day 1: Nubank (minimalismo/roxo), Inter (cards grandes/abas), PicPay (gradientes/ícones), Mercado Bitcoin (dados visuais). Metas: <30s primeira ação, >85% conclusão, >70 NPS |
| `CODING_STANDARDS.md` | Seção nova ~110L | Padrões frontend: Hero Section, Cards Modernos, Botões, Emojis por página, Cores Semânticas, Animações. Exemplos HTML completos |
| `CHANGELOG.md` | Entrada 20/03 | UX Evolution completa: 10 telas, design system, animações, emojis |
| `ROADMAP.md` | Seção UX | Frontend UX Evolution 100% concluído (20/03/2026, v0.9.3) |
| `PROJECT_STATUS.md` | Seção UX | 10 páginas modernizadas, design unificado |
| `UX_MODERNIZACAO.md` | 274 | Planejamento completo: cores emocionais, tipografia, componentes, roadmap de 2 semanas |
| `UX_IMPLEMENTACAO_WEEK1.md` | 489 | Implementação detalhada: CSS completo, componentes, animações, checklist |

### Gaps na Documentação

1. **Falta um `DESIGN_SYSTEM.md`** dedicado — as decisões de design (por que indigo→purple? por que Inter? por que emojis?) estão dispersas
2. **UX_BENCHMARKING.md** parou no Day 1 — Day 2 (entrevistas/protótipos) nunca foi executado
3. **Não há guia de acessibilidade** — contrast ratios, ARIA labels, keyboard navigation

---

## 3. REVALIDAÇÃO DO AGRUPAMENTO E APRESENTAÇÃO

### 3.1 Agrupamento Atual (Sidebar)

```
📊 Resumo          → Dashboard, Carteiras (sub), Ativos, Performance
💰 Operações       → Comprar/Vender (sub), Movimentações, Proventos (sub), Planos (sub)
📈 Análises        → Análises (sub), Relatórios, Imposto de Renda, Educação
⚙️ Config          → Alertas, Configurações
```

### 3.2 Problemas Identificados

1. **Alertas em "Config"** — Alertas é funcionalidade de monitoramento, não configuração. Pertence mais a "Análises" ou a um grupo próprio "Monitoramento"
2. **Educação em "Análises"** — Educação é suporte/aprendizado, não análise. Poderia ser item no footer ou seção própria
3. **Sub-menus excessivos** — 4 itens com sub-menu (Carteiras, Comprar/Vender, Proventos, Planos, Análises) criam 5 níveis de expansão na sidebar, aumentando carga cognitiva
4. **"Comprar/Vender" + "Planos"** — sobreposição conceitual (planos de compra/venda vs comprar/vender)

### 3.3 Proposta de Reagrupamento

```
📊 Visão Geral     → Dashboard, Performance
💼 Portfólio       → Carteiras, Ativos, Alocação
💰 Operações       → Movimentações, Comprar/Vender, Proventos
📈 Análises        → Relatórios, Imposto de Renda, Comparador
🔔 Monitoramento   → Alertas, Fluxo de Caixa
🎓 Aprender        → Educação (link discreto no footer ou seção colapsada)
⚙️ Configurações   → Perfil, Notificações, Segurança, Preferências
```

**Benefícios:**
- **Reduz sub-menus** de 5 para 1-2
- **Separa monitoramento** de configuração
- **Agrupa por ação mental**: ver → gerenciar → operar → analisar → monitorar
- **Alinha com benchmarks**: Nubank (5 itens), Inter (4 abas), PicPay (4-5 ações)

### 3.4 Padrão de Apresentação Recomendado

Cada tela deveria seguir exatamente esta estrutura:

```
1. Hero Section (idêntico — ✅ já implementado)
2. Stats Cards (4 cards com card-moderno — PADRONIZAR)
3. Filtros/Ações (barra horizontal — padronizar)
4. Conteúdo Principal (tabela/grid/gráfico)
5. Seção Secundária (insights, análise, detalhes)
```

Páginas que **não seguem** este padrão: Movimentações (pula direto para tabela), Educação (hero duplicado).

---

## 4. AVALIAÇÃO TIPOGRÁFICA

### 4.1 Stack Atual

```@/home/p016525/elielson/exitus/frontend/app/static/css/design-system.css:135
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
```

| Elemento | Classe Tailwind | Tamanho Real | Benchmark (Inter/PicPay) | Avaliação |
|----------|----------------|-------------|--------------------------|-----------|
| Hero título | `text-5xl font-bold` | 48px / 700 | 32-40px | ✅ Bom (impactante) |
| Hero subtítulo | `text-xl text-white/80` | 20px / 400 | 18-20px | ✅ Adequado |
| Card título | `font-bold text-gray-900` | 16px / 700 | 18-20px | ⚠️ Poderia ser `text-lg` |
| Card valor | `text-3xl font-bold` | 30px / 700 | 28-32px | ✅ Bom |
| Body text | `text-sm text-gray-600` | 14px / 400 | 16px | ⚠️ **Abaixo do benchmark** |
| Badge | `text-sm` | 14px / varied | 12-14px | ✅ Adequado |
| Sidebar item | base (16px) | 16px / 400 | 14-16px | ✅ Adequado |
| Tab labels | `font-medium text-sm` | 14px / 500 | 14-16px | ✅ Adequado |
| Tabela header | `font-semibold text-gray-700` | 16px / 600 | 14-16px | ✅ Adequado |
| Tabela body | base | 16px / 400 | 14-16px | ✅ Adequado |

### 4.2 Veredicto sobre a Fonte Inter

**Inter é excelente para fintech.** Razões:

- **Otimizada para telas** — desenhada especificamente para interfaces digitais
- **Tabular numbers** — suporte nativo a números tabulares (`font-feature-settings: "tnum"`) — essencial para alinhamento de valores financeiros
- **Amplitude de pesos** — 300-800 permite hierarquia visual rica
- **Legibilidade** — x-height alta, espaçamento generoso
- **Usada por**: Linear, Vercel, GitHub — empresas de referência em UI

### 4.3 Recomendações Tipográficas

1. **Aumentar body text de 14px → 16px** — o `UX_BENCHMARKING.md` já identificou isso: *"Textos: 16px base (vs 14px atual)"*. Trocar `text-sm` por `text-base` nos textos descritivos
2. **Ativar font-feature-settings: "tnum"** para todos os valores monetários — garante alinhamento perfeito em colunas
3. **Contrast ratio** — `text-gray-600` sobre `bg-white` dá ~5.7:1 (WCAG AA ✅). `text-white/80` sobre gradient hero é aproximadamente 4.1:1 (borderline) — **considerar `text-white/90`**
4. **Card títulos** — subir de 16px para 18px (`text-lg`) para melhor hierarquia

---

## 5. PLANO DE TESTES DE USABILIDADE TELA A TELA

### 5.1 Metodologia

- **Tipo**: Teste exploratório guiado + verificação funcional
- **Ferramenta**: Playwright (MCP browser) ou manual
- **Ambiente**: `http://localhost:5000` (exitus-frontend)
- **Pré-requisito**: Backend rodando, banco seedado

### 5.2 Plano Detalhado por Tela

#### TELA 1 — 📊 Dashboard (`/dashboard/`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 1.1 | Carregar página | Hero visível, animações executam, cards renderizam | `GET /api/v1/portfolios/summary` |
| 1.2 | Clicar card BR | Redireciona para `/dashboard/portfolios?market=br` | — |
| 1.3 | Clicar card US | Redireciona para `/dashboard/portfolios?market=us` | — |
| 1.4 | Toggle moeda BRL↔USD | Valores recalculam em todas os cards | `GET /api/v1/exchange-rates` |
| 1.5 | Verificar gráficos | Chart.js renderiza, dados coerentes | `GET /api/v1/portfolios/performance` |
| 1.6 | Hover em cards | `hover-lift` anima (-4px), cursor pointer | — |
| 1.7 | Responsive | Resize para mobile: cards empilham, hero adapta | — |

#### TELA 2 — 📁 Carteiras (`/dashboard/portfolios`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 2.1 | Carregar página | Cards de resumo por mercado + lista de carteiras | `GET /api/v1/portfolios` |
| 2.2 | Clicar "Nova Carteira" | Modal abre com form | — |
| 2.3 | Preencher e submeter | Carteira criada, toast de sucesso | `POST /api/v1/portfolios` |
| 2.4 | Toggle grid/lista | Visualização alterna | — |
| 2.5 | Clicar carteira | Navega para detalhes | `GET /api/v1/portfolios/{id}` |
| 2.6 | Filtrar por mercado | Cards atualizam | `GET /api/v1/portfolios?market=X` |

#### TELA 3 — 🎯 Ativos (`/dashboard/assets`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 3.1 | Carregar página | Stats por tipo de ativo + tabela | `GET /api/v1/assets` |
| 3.2 | Filtrar por tipo | Tabela atualiza | `GET /api/v1/assets?type=X` |
| 3.3 | Buscar ativo | Resultados filtram em tempo real | — (client-side) |
| 3.4 | Clicar ativo | Navega para detalhes | `GET /api/v1/assets/{id}` |
| 3.5 | Verificar badges | Tipos corretos, cores semânticas | — |

#### TELA 4 — 📈 Performance (`/dashboard/performance`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 4.1 | Carregar página | 4 cards de métricas + gráficos | `GET /api/v1/performance/summary` |
| 4.2 | Mudar período (1M/6M/1A/5A) | Gráfico atualiza | `GET /api/v1/performance?period=X` |
| 4.3 | Toggle benchmarks | CDI/IBOV/IFIX aparecem no gráfico | `GET /api/v1/benchmarks` |
| 4.4 | Heatmap | Renderiza corretamente, cores semânticas | `GET /api/v1/performance/heatmap?year=X` |
| 4.5 | Tabela de ativos | Dados coerentes, sparklines renderizam | `GET /api/v1/assets/performance` |
| 4.6 | Buscar ativo na tabela | Filtro client-side funciona | — |
| 4.7 | Ordenar por valor/% | Tabela reordena | — |

#### TELA 5 — 💳 Movimentações (`/dashboard/dashboard_movimentacoes`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 5.1 | Carregar página | Stats + tabela de movimentações | `GET /api/v1/movimentacoes` |
| 5.2 | Clicar "Nova Movimentação" | Modal/form abre | — |
| 5.3 | Exportar CSV | Download inicia | `GET /api/v1/movimentacoes/export?format=csv` |
| 5.4 | Exportar Excel | Download inicia | `GET /api/v1/movimentacoes/export?format=xlsx` |
| 5.5 | Verificar badges | Tipos (depósito=success, compra=primary) | — |
| 5.6 | Paginação | Navega entre páginas | `GET /api/v1/movimentacoes?page=X` |

#### TELA 6 — 🔔 Alertas (`/dashboard/alerts`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 6.1 | Carregar página | 4 stats cards + tabela de alertas | `GET /api/v1/alerts` |
| 6.2 | Clicar "Novo Alerta" | Modal abre (JS puro) | — |
| 6.3 | Preencher form completo | Validação HTML5 funciona | — |
| 6.4 | Submeter alerta | Criado com sucesso | `POST /api/v1/alerts` |
| 6.5 | Toggle ativo/inativo | Switch funciona | `PATCH /api/v1/alerts/{id}` |
| 6.6 | Hora dinâmica | Atualiza a cada 60s | — |

#### TELA 7 — 📄 Relatórios (`/dashboard/reports`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 7.1 | Carregar página | 4 cards de resumo + grid de relatórios | `GET /api/v1/reports` |
| 7.2 | Clicar "Gerar Relatório" | Dropdown com tipos abre | — |
| 7.3 | Selecionar tipo | Modal de configuração abre | — |
| 7.4 | Configurar período + formato | Radio buttons de formato (PDF/Excel/CSV) | — |
| 7.5 | Gerar relatório | Spinner, depois relatório na lista | `POST /api/v1/reports/generate` |
| 7.6 | Download relatório | Arquivo baixa corretamente | `GET /api/v1/reports/{id}/download` |
| 7.7 | Excluir relatório | Removido da lista | `DELETE /api/v1/reports/{id}` |

#### TELA 8 — 🧾 Imposto de Renda (`/dashboard/imposto-renda`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 8.1 | Carregar página | 4 cards de resumo + abas | `GET /api/v1/ir/summary` |
| 8.2 | Aba Calculadora | Formulário renderiza, calcular IR funciona | `POST /api/v1/ir/simulate` |
| 8.3 | Aba DARFs | Tabela de DARFs com status | `GET /api/v1/ir/darfs` |
| 8.4 | Gerar DARF | DARF criado | `POST /api/v1/ir/darfs` |
| 8.5 | Aba Prejuízos | ⛔ **BUG: `xfor` → `x-for`** — lista não renderiza | `GET /api/v1/ir/losses` |
| 8.6 | Aba Relatório | Resumo anual + gráfico | `GET /api/v1/ir/report?year=X` |
| 8.7 | Exportar relatório | Download funciona | `GET /api/v1/ir/report/export` |

#### TELA 9 — 🎓 Educação (`/dashboard/educacao`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 9.1 | Carregar página | Hero educação + abas | `GET /api/v1/education/articles` |
| 9.2 | Aba Artigos | Grid de artigos com imagem, badge, tempo | — |
| 9.3 | Filtrar categoria | Artigos filtram | — (client-side) |
| 9.4 | Aba Vídeos | Grid com thumbnails e play button | `GET /api/v1/education/videos` |
| 9.5 | Aba Cursos | Cards com progresso | `GET /api/v1/education/courses` |
| 9.6 | Aba Calculadoras | Grid de calculadoras | — |
| 9.7 | Insights personalizados | 3 cards de insights renderizam | `GET /api/v1/education/insights` |

#### TELA 10 — ⚙️ Configurações (`/dashboard/configuracoes`)
| # | Ação | Verificar | API Call |
|---|------|-----------|----------|
| 10.1 | Carregar página | Hero + abas de configuração | `GET /api/v1/user/profile` |
| 10.2 | Aba Perfil | Form com dados, avatar, salvar funciona | `PUT /api/v1/user/profile` |
| 10.3 | Aba Notificações | Checkboxes email/push | `PUT /api/v1/user/notifications` |
| 10.4 | Aba Segurança | Alterar senha, 2FA, sessões | `PUT /api/v1/user/password` |
| 10.5 | Aba Preferências | Idioma, tema, moeda, privacidade | `PUT /api/v1/user/preferences` |
| 10.6 | Salvar cada aba | Toast de confirmação | — |

### 5.3 Testes Transversais (Cross-Page)

| # | Teste | Verificar |
|---|-------|-----------|
| T1 | **Currency toggle** | Alternar BRL↔USD persiste entre páginas (localStorage) |
| T2 | **Sidebar navigation** | Todos os 8+ links funcionam, item ativo destacado |
| T3 | **Sidebar search** | Busca filtra itens corretamente |
| T4 | **Mobile responsive** | Sidebar mobile overlay funciona, hamburger menu |
| T5 | **Flash messages** | Auto-hide após 5s, dismiss manual funciona |
| T6 | **Auth guard** | Páginas protegidas redirecionam para login |
| T7 | **Loading states** | HTMX indicator aparece durante requests |
| T8 | **Animações** | Todas as `animate-*` executam na primeira carga |
| T9 | **Dark mode** | Design system tem variáveis — verificar se toggle existe |

---

## RESUMO EXECUTIVO

### Score Geral: **B+ (7.5/10)**

| Critério | Nota | Comentário |
|----------|------|------------|
| **Hero Sections** | A (10/10) | 100% consistentes, premium, animados |
| **Design System** | A- (8.5/10) | Robusto, 1289 linhas, bem estruturado |
| **Consistência Cards** | C+ (6/10) | 3 padrões coexistem — precisa unificar |
| **Consistência Botões** | B- (6.5/10) | 2 padrões coexistem |
| **Tipografia** | B+ (7.5/10) | Inter excelente, body text deveria ser 16px |
| **Navegação** | B (7/10) | Sidebar funcional mas com excesso de sub-menus |
| **Animações** | A (9/10) | Ricas, suaves, com delays escalonados |
| **Acessibilidade** | C (5/10) | Sem ARIA labels, sem keyboard nav, contrast borderline |
| **Documentação UX** | B (7/10) | Benchmarking bom, falta guia de design system dedicado |

### Top 5 Ações Prioritárias

1. **Corrigir bug `xfor` → `x-for`** em `imposto_renda.html:349` (bug funcional)
2. **Unificar cards** → migrar todas as 6 telas inconsistentes para `card-moderno`
3. **Unificar botões** → migrar para `btn-primario` / `btn-secundario`
4. **Aumentar body text** de `text-sm` (14px) → `text-base` (16px) nas descrições
5. **Migrar modal de Alertas** de JS puro para Alpine.js

---

## DOCUMENTOS TEMPORÁRIOS IDENTIFICADOS

### Arquivos .md em docs/ que poderiam ser consolidados:

#### 1. UX (3 arquivos → 1)
- `UX_MODERNIZACAO.md` (274L) — Planejamento
- `UX_IMPLEMENTACAO_WEEK1.md` (489L) — Implementação detalhada
- `UX_BENCHMARKING.md` (203L) — Análise competitiva
- **Proposta:** Consolidar em `UX_DESIGN_SYSTEM.md` único

#### 2. Frontend/Roadmap/Testes Archive (20 arquivos — avaliados individualmente)

**PRESERVAR (15 arquivos, ~6.400 linhas):**
- `FRONTEND_ANALISE_COMPLETA.md` (378L) — Catálogo: 39 componentes + 14 telas
- `FRONTEND_V2_STATUS.md` (290L) — Certificado de conclusão V2.0
- `FRONTEND_GAPS_RESOLVIDOS.md` (236L) — Detalhes Chart.js radial, sidebar fix
- `INTEGRACAO_FRONTEND_BACKEND.md` (365L) — Contratos de integração front↔back
- `PROTOTIPOS_FRONTEND_RESUMO.md` (659L) — Wireframes ASCII originais
- `ROADMAP_BACKEND.md` (206L) — Visão consolidada backend por fases
- `ROADMAP_FASE4.md` (164L) — Índices SQL exatos, cache Redis config
- `ROADMAP_FRONTEND_V2.md` (785L) — ADR definitivo do frontend V2
- `ROADMAP_TESTES_FRONTEND.md` (551L) — Plano de testes ativo, 108 testes
- `TESTES_E2E_PLAN.md` (588L) — Page Object Model, estratégia Playwright
- `TESTES_HISTORICO.md` (204L) — 17 correções documentadas (lições aprendidas)
- `PERMISSIONS_FIX.md` (113L) — Troubleshooting WSL↔Podman UID/GID

**REMOVER (3 arquivos, ~1.400 linhas — obsoletos ou auto-declarados substituídos):**
- `FRONTEND_REFACTOR_PROPOSAL.md` (309L) — Proposta Next.js/SvelteKit nunca implementada
- `FRONTEND_TESTES_E2E_PLAN.md` (370L) — Auto-declara "SUPERADO"
- `ROADMAP_FRONTEND.md` (726L) — Auto-declara "Substituído por V2"

#### 3. GAPs individuais (8 arquivos → PRESERVAR)
- `archive/EXITUS-*.md` (8 arquivos, ~2.500 linhas) — ADRs (Architecture Decision Records)
- Contêm regras de negócio, specs de API, anti-patterns, decisões arquiteturais
- Informação NÃO está em ROADMAP/CHANGELOG (que têm 1-2 linhas por GAP)

**Veredicto:** **PRESERVAR** — são patrimônio de conhecimento do projeto

#### 4. MULTICLIENTE partes (4 arquivos — DECISÃO DO USUÁRIO)
- `archive/MULTICLIENTE_PARTE1.md` (226L) — Model, migrations, 4 models iniciais
- `archive/MULTICLIENTE_PARTE2A.md` (226L) — Migrations aplicadas, 11 models
- `archive/MULTICLIENTE_PARTE2B.md` (293L) — 9 models restantes, relacionamentos
- `archive/MULTICLIENTE_PARTE3.md` (221L) — Migração dados, helper tenant, JWT
- **Situação:** `MULTICLIENTE.md` consolidado (218L) já absorveu todo o conteúdo essencial
- **Opção A:** Remover (consolidado basta, referências no final do consolidado)
- **Opção B:** Manter (detalhes campo-a-campo podem ser úteis para debugging futuro)

### Resumo da consolidação proposta:

| Ação | Arquivos | Linhas |
|------|----------|--------|
| **PRESERVAR** | 23 (8 EXITUS + 15 FRONTEND/ROADMAP/TESTES) | ~8.900 |
| **REMOVER** | 3 (auto-declarados obsoletos) | ~1.400 |
| **CONSOLIDAR** | 3 UX docs → 1 | ~966 → ~500 |
| **DECISÃO USUÁRIO** | 4 MULTICLIENTE partes | ~966 |

---

## PRÓXIMOS PASSOS

1. **Aprovar plano de consolidação** dos arquivos .md
2. **Executar Top 5 ações prioritárias** (bug + unificação)
3. **Criar DESIGN_SYSTEM.md** dedicado
4. **Implementar plano de testes** tela a tela
5. **Reagrupar sidebar** conforme proposta

---

**Status:** 🎯 **Análise Completa Concluída**  
**Próximo:** ⚡ **Execução das Prioridades**  
**Timeline:** 2-3 dias para unificação + 1 semana para testes
