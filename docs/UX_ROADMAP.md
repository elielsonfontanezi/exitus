# 🎨 Roadmap de Evolução UX/UI - Exitus

## 📋 Visão Geral

**Objetivo:** Modernizar a interface do Exitus de um design tecnicista para um visual moderno e amigável para público geral, **inspirado no Investidor10**.

**Público-Alvo:** Qualquer pessoa (público geral) que deseja uma interface clara e intuitiva, sem necessidade de conhecimento especializado em negócios ou finanças.

**Referência Principal:** Investidor10.com.br - Design denso mas organizado, tipografia Nunito, cores sóbrias (dourado/marrom).

**Timeline:** 4 semanas (1 mês) - Abordagem Incremental

---

## 📚 **Documentos de Referência**

### **Controle e Execução:**
- **UX_ROADMAP.md** ← *Este documento* (controle geral, fases, entregas)
- **UX_ESTRUTURA_PROPOSTA.md** ← *Estrutura detalhada, layouts, componentes*

### **Design System:**
- **UX_DESIGN_SYSTEM.md** ← *Padrões visuais, cores, tipografia, CSS*

### **Análise Histórica:**
- **UX_ANALISE_COMPLETA_OPUS.md** ← *Análise completa, decisões, raciocínio*

---

## 🔄 **Fluxo de Trabalho**

```
UX_ROADMAP.md (Controle)
    ↓
UX_ESTRUTURA_PROPOSTA.md (Estrutura)
    ↓
UX_DESIGN_SYSTEM.md (Implementação)
    ↓
Código Frontend
```

> **📌 IMPORTANTE:** Verifique **UX_PLANO_EXECUCAO.md** para a metodologia interativa completa de implementação tela a tela!

---

## 🎯 Fases de Implementação - 4 Semanas Incrementais

### **📅 SEMANA 1: Design System Moderno**

#### **Dia 1-2: Fundação Visual**
- [ ] **Cores Investidor10**
  - Implementar palette dourado/marrom (#A38C65) como primária
  - Cores sóbrias e profissionais (sem gradientes excessivos)
  - Definir cores semânticas (sucesso verde, perigo vermelho)

- [ ] **Tipografia Nunito**
  - Implementar fonte Nunito (como Investidor10)
  - Escala: 16px base, 24px títulos
  - Pesos: 400 (normal), 600 (semibold), 700 (bold)

#### **Dia 3-4: Componentes Base**
- [ ] **Cards Compactos (Estilo Investidor10)**
  - Cards densos mas organizados (ticker + preço + variação)
  - Borda simples (1px) com hover sutil
  - Layout horizontal para máxima eficiência

- [ ] **Links e Botões**
  - Links dourado/marrom com hover underline
  - Botões sóbrios sem gradientes
  - Focus states claros e acessíveis

#### **Dia 5: Animações e Transições**
- [ ] **Microinterações**
  - Implementar animações suaves (fade-in, slide-up)
  - Adicionar hover states em todos elementos interativos
  - Criar loading skeletons

### **📅 SEMANA 2: Navegação Simplificada**

#### **Dia 1-2: Menu Horizontal com Dropdowns (Estilo Investidor10)**
- [ ] **Header Escuro com Dropdowns**
  - Background #212529 (preto suave)
  - Links brancos com hover rgba(255,255,255,0.1)
  - Logo à esquerda, menu centralizado
  - Dropdowns com setas ▼ animadas

- [ ] **Estrutura de Dropdowns**
  - Visão Geral | Operações | Ativos | Análises | Relatórios | Ferramentas
  - Subcategorias organizadas por seção
  - Ícones discretos para itens (Font Awesome)
  - Busca proeminente no header

- [ ] **Comportamento dos Dropdowns**
  - Aparecem com fade + slide suave
  - Background branco com borda #e9ecef
  - Sombra 0 4px 12px rgba(0,0,0,0.15)
  - Seções com títulos em dourado/marrom
  - Implementar navegação por contexto

- [ ] **Navegação por Abas**
  - Implementar abas horizontais principais
  - Adicionar indicador de seção ativa
  - Criar breadcrumbs para contexto

#### **Dia 3-4: Sub-menu Contextual**
- [ ] **Menu Dinâmico**
  - Implementar sub-menu que aparece suavemente
  - Adicionar busca inteligente
  - Criar filtros rápidos por categoria

#### **Dia 5: Mobile-First**
- [ ] **Layout Responsivo**
  - Adaptar navegação para mobile
  - Implementar menu hambúrguer
  - Otimizar toques e gestos

### **📅 SEMANA 3: Layout Denso e Gráficos**

#### **Dia 1-2: Tabelas de Dados (Estilo Investidor10)**
- [ ] **Tabelas Limpas**
  - Fundo branco, sem bordas externas
  - Linhas separadas por border-bottom #f1f3f4
  - Padding: 8px 15px nas células
  - Hover: background #f8f9fa

- [ ] **Gráficos e Charts**
  - Container branco com border 1px #e9ecef
  - Título 16px, weight 600
  - Sem animações excessivas
  - Cores sóbrias e profissionais

#### **Dia 3-4: Quadros de Conteúdo**
- [ ] **Section Boxes**
  - Background #f8f9fa
  - Border 1px #e9ecef, border-radius 8px
  - Título com border-bottom 2px primária
  - Padding 24px interno

#### **Dia 5: Cards de Notificação**
- [ ] **Alertas e Updates**
  - Border-left 4px cor primária
  - Box-shadow sutil 0 2px 4px rgba(0,0,0,0.1)
  - Título + timestamp (12px, muted)

### **📅 SEMANA 4: Mobile-First**

#### **Dia 1-2: Layout Adaptativo**
- [ ] **Mobile-First Approach**
  - Desenhar para mobile primeiro (320px+)
  - Adaptar para desktop (1024px+)
  - Testar em tablets intermediários section

#### **Dia 3-4: Cards de Ativos**
- [ ] **Tabela→Cards**
  - Converter tabela de ativos para cards visuais
  - Implementar grid responsivo
  - Adicionar informações contextuais

#### **Dia 5: Ações Rápidas**
- [ ] **Botões Flutuantes**
  - Implementar botões de ação rápida (Comprar, Vender, Depositar)
  - Adicionar oportunidades em destaque
  - Criar fluxo simplificado

### **📅 SEMANA 4: Polimento e Testes**

#### **Dia 1-2: Componentes Avançados**
- [ ] **Gráficos Modernos**
  - Atualizar gráficos com cores emocionais
  - Implementar tooltips e interações
  - Adicionar legendas claras

- [ ] **Alertas e Notificações**
  - Redesenhar sistema de alertas
  - Implementar notificações contextuais
  - Adicionar badges e indicadores

#### **Dia 3-4: Testes e Validação**
- [ ] **Testes A/B**
  - Testar cores (emocionais vs corporativas)
  - Testar layout (cards vs tabela)
  - Testar navegação (menu vs abas)

- [ ] **Performance e Acessibilidade**
  - Otimizar tempo de carregamento
  - Validar WCAG 2.1 AA
  - Testar navegação por teclado

#### **Dia 5: Documentação e Deploy**
- [ ] **Documentação Atualizada**
  - Atualizar ROADMAP.md com progresso
  - Documentar novos componentes
  - Criar guia de estilo

- [ ] **Deploy Gradual**
  - Implementar feature flags
  - Rollout para 10% usuários
  - Monitorar métricas

---

### **📅 SEMANA 5-6: Componentes Visuais**

#### **Sprint 5: Cards de Ativos**
- [ ] **Design de Cards**
  ```html
  <div class="card-ativo">
    <div class="header">
      <span class="ticker">PETR4</span>
      <span class="favorito">⭐</span>
    </div>
    <div class="info">
      <h4>Petrobras</h4>
      <div class="preco">
        <strong>R$ 45,67</strong>
        <span class="variacao positiva">+2.3%</span>
      </div>
    </div>
    <div class="acoes">
      <button class="btn-comprar">Comprar</button>
      <button class="btn-detalhes">Ver</button>
    </div>
  </div>
  ```

- [ ] **Estados Visuais**
  - Loading skeletons
  - Empty states amigáveis
  - Error states com soluções

- [ ] **Microinterações**
  - Hover suaves
  - Transições fluidas
  - Feedback visual imediato

#### **Sprint 6: Dashboard Simplificado**
- [ ] **Visão Principal**
  - 4 cards principais: Saldo, Lucro/Mes, Investimentos, Alertas
  - Gráficos simples (linha/área)
  - Ações rápidas proeminentes

- [ ] **Personalização**
  - Arrastar/soltar cards
  - Esconder/mostrar widgets
  - Salvar preferências

- [ ] **Contexto Inteligente**
  - "Bom dia, João! Seu portfólio subiu 2.3% hoje"
  - Sugestões baseadas em perfil
  - Tips educacionais

---

### **📅 SEMANA 7-8: Refinamento e Implementação**

#### **Sprint 7: Testes Visuais**
- [ ] **Testes A/B**
  - Layout dashboard (cards vs tabela)
  - Cores (emocionais vs corporativas)
  - Navegação (menu vs abas)

- [ ] **Validação Interna**
  - Testes de usabilidade com equipe
  - Revisão de acessibilidade
  - Validação de responsividade

- [ ] **Acessibilidade**
  - Leitor de tela (VoiceOver/TalkBack)
  - Navegação por teclado
  - Contraste e tamanho

#### **Sprint 8: Polimento Final**
- [ ] **Performance**
  - Tempo de carregamento < 2s
  - Core Web Vitals verdes
  - Otimização de imagens

- [ ] **Documentação**
  - Guia de estilo completo
  - Component library
  - Playbook de manutenção

- [ ] **Lançamento**
  - Feature flags para rollout gradual
  - Monitoramento de métricas
  - Feedback loop implementado

---

## 🎨 Componentes Chave

### **Card de Ativo Simplificado**
```html
<div class="investimento-card">
  <div class="header">
    <div class="simbolo">PETR4</div>
    <div class="categoria">Ação</div>
  </div>
  <div class="corpo">
    <h3>Petrobras</h3>
    <div class="valores">
      <span class="preco">R$ 45,67</span>
      <span class="variacao positiva">+2.3%</span>
    </div>
  </div>
  <div class="acoes">
    <button class="btn primario">Comprar</button>
    <button class="btn secundario">Ver</button>
  </div>
</div>
```

### **Dashboard Resumido**
```html
<div class="dashboard-simples">
  <div class="hero-section">
    <h1>Olá, João! 👋</h1>
    <p>Seu portfólio vale <strong>R$ 125.430,00</strong></p>
    <div class="resumo-rapido">
      <div class="card-metrica positivo">
        <span class="valor">+R$ 2.890,00</span>
        <span class="descricao">Este mês</span>
      </div>
      <div class="card-metrica">
        <span class="valor">12</span>
        <span class="descricao">Ativos</span>
      </div>
    </div>
  </div>
  
  <div class="acoes-rapidas">
    <button class="btn-grande comprar">💰 Comprar</button>
    <button class="btn-grande vender">💸 Vender</button>
    <button class="btn-grande depositar">🏦 Depositar</button>
  </div>
</div>
```

### **Navegação por Abas**
```html
<div class="nav-abas">
  <button class="aba ativa">📊 Resumo</button>
  <button class="aba">💰 Operações</button>
  <button class="aba">📈 Análises</button>
  <button class="aba">⚙️ Config</button>
</div>
```

---

## 📊 Métricas de Sucesso

### **KPIs de UX**
- **Tempo de primeira ação:** < 30 segundos
- **Taxa de conclusão de tarefas:** > 85%
- **Satisfação do usuário (NPS):** > 70
- **Taxa de erro:** < 5%

### **KPIs de Negócio**
- **Engajamento:** +40% tempo na plataforma
- **Conversão:** +25% operações realizadas
- **Retenção:** +30% usuários ativos/mês
- **Suporte:** -50% tickets de "não sei usar"

---

## 🛠️ Stack Tecnológico

### **Frontend**
- **Tailwind CSS** (já utilizado)
- **Alpine.js** (já utilizado)  
- **Framer Motion** (para animações)
- **Chart.js** (gráficos simplificados)

### **Ferramentas**
- **Figma** (design e protótipos)
- **Hotjar** (heatmaps e gravações)
- **Google Analytics** (métricas)
- **Vercel** (deploy e performance)

---

## 🎯 Deliverables por Sprint

| Sprint | Deliverable | Documento | Status |
|--------|-------------|-----------|--------|
| 1 | Pesquisa de usuários | UX_ROADMAP.md | 🔲 Planejado |
| 1 | Benchmarking UX (Investidor10) | UX_ANALISE_COMPLETA_OPUS.md | 🟡 **Concluído** |
| 2 | Design System v1 (Inspiração I10) | UX_DESIGN_SYSTEM.md | 🟡 **Atualizado** |
| 3 | Estrutura de navegação | UX_ESTRUTURA_PROPOSTA.md | � **Atualizado** |
| 4 | Menu horizontal dropdowns | UX_ESTRUTURA_PROPOSTA.md | � **Proposto** |
| 5 | Cards modulares (padrão) | UX_DESIGN_SYSTEM.md | � **Definido** |
| 6 | Layout responsivo | UX_ESTRUTURA_PROPOSTA.md | 🟡 **Proposto** |
| 7 | Implementação CSS | UX_DESIGN_SYSTEM.md | 🔲 Pendente |
| 8 | Testes e validação | UX_ROADMAP.md | 🔲 Pendente |

---

## 📊 **Painel de Controle**

### ✅ **Concluído:**
- [x] Análise completa Investidor10
- [x] Design system cores + tipografia
- [x] Estrutura de navegação proposta
- [x] Menu horizontal com dropdowns
- [x] Padrão de cards definidos

### 🔄 **Em Andamento:**
- [x] Implementação CSS no código - **Dashboard iniciado 21/03/2026**
- [ ] Aplicação nos templates
- [ ] Testes visuais

### ⏳ **Próximos Passos:**
1. Implementar CSS (UX_DESIGN_SYSTEM.md)
2. Aplicar estrutura (UX_ESTRUTURA_PROPOSTA.md)
3. Validar com usuários
4. Iterar conforme feedback

---

## 📱 **Implementação por Tela**

### **Dashboard** ✅ Validado
- **Data Início:** 21/03/2026
- **Data Conclusão:** 21/03/2026
- **Status:** Validado e em Produção
- **Responsável:** Sonnet
- **Prioridade:** Alta

#### **Planejamento:**
- **Dependências:** Nenhuma (primeira tela)
- **Componentes:** Cards modulares, gráficos, notificações, resumo patrimônio

#### **Implementação:**
- **CSS:** design-system.css
  - [x] .card-dashboard ✅
  - [x] .chart-container ✅
  - [x] .notification-panel ✅
  - [x] .resumo-patrimonio ✅
  - [x] .dropdown-menu (menu horizontal) ✅
  - [x] 347 linhas CSS adicionadas (21/03/2026)
  
- **HTML:** 
  - [x] templates/base.html (menu horizontal) ✅
  - [ ] templates/dashboard/index.html (estrutura)

- **JS:**
  - [x] Dropdowns JavaScript puro ✅
  - [ ] Cards expansíveis
  - [ ] Notificações

#### **Validação:**
- **Testes Funcionais:**
  - [x] Carregamento correto ✅
  - [x] Responsividade (Desktop/Tablet/Mobile) ✅
  - [x] Interações funcionando ✅
  - [x] Performance OK ✅

- **Validação Usuário:**
  - Data: 21/03/2026
  - Feedback: "Aprovado. Mas depois acho que vale uma reavaliação do que ainda pode ser apresentado na tela principal."
  - Status: [x] Aprovado

#### **Registro de Mudanças:**
- **21/03/2026:** Início da implementação (Sonnet)
- **21/03/2026:** Dashboard v1 validado e em produção

#### **Melhorias v2 - CONCLUÍDAS (21/03/2026):**

**Feedback do usuário:** "Vale uma reavaliação do que ainda pode ser apresentado na tela principal."

**Componentes implementados:**

1. ✅ **Visão Multi-Mercado** (ALTA PRIORIDADE)
   - Cards BR/US/INTL com patrimônio, percentual e rentabilidade
   - API: `/api/portfolios/dashboard`

2. ✅ **Saldo em Caixa + Toggle BRL/USD** (ALTA PRIORIDADE)
   - Card com saldo disponível
   - Toggle para alternar moeda (⇄)
   - API: `/api/carteira/saldo-caixa`

3. ✅ **Alocação Gráfica** (MÉDIA PRIORIDADE)
   - Gráfico doughnut (Chart.js)
   - Visualização por mercado (BR/US/INTL)
   - Dados: `alocacao_geografica`

4. ✅ **Alertas Recentes** (MÉDIA PRIORIDADE)
   - Lista de alertas disparados
   - API: `/api/alertas/recentes?limit=3`

5. ✅ **Últimas Transações** (MÉDIA PRIORIDADE)
   - 5 últimas operações
   - API: `/api/transacoes/recentes?limit=5`

**Status:** ✅ Implementado e em produção (21/03/2026)

---

## 🚀 Próximos Passos

1. **Aprovação do Roadmap** - Alinhamento com stakeholders
2. **Formação do Squad** - Designer + Frontend + UX Researcher
3. **Kickoff Week 1** - Início das pesquisas
4. **Review Bi-semanal** - Apresentação de progresso
5. **Launch Week 8** - Rollout para usuários

---

## 💬 Feedback e Iteração

**Canais de comunicação:**
- **Weekly sync** - Segundas 10h
- **Design review** - Quartas 15h  
- **User testing** - Sextas 14h
- **Stakeholder update** - Sextas 17h

**Ferramentas de feedback:**
- **Slack** #ux-roadmap
- **Figma** comentários em designs
- **Notion** documentação colaborativa
- **Miro** brainstorming e ideias

---

**Status:** 📋 **Planejamento Completo**  
**Próximo:** 🚀 **Aprovação e Kickoff Week 1**  
**Timeline:** 8 semanas | **Budget:** TBD | **Team:** 3 pessoas
