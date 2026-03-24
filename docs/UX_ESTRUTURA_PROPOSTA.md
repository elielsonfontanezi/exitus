# 🏗️ Proposta de Estrutura UX para Exitus

> **Data:** 24/03/2026  
> **Inspirado em:** Investidor10 (visual) + Contexto Exitus (negócio)  
> **Status:** ✅ Dashboard implementado com melhorias UX (24/03/2026)
> 
> **Dashboard Features:**
> - ✅ Loading Skeleton
> - ✅ Cards de Ação Rápida
> - ✅ Tooltips Educacionais
> - ✅ Meta de Patrimônio
> - ✅ Benchmark vs CDI
> - ✅ Próximos Proventos
> 
> **📌 IMPORTANTE:** Verifique **UX_PLANO_EXECUCAO.md** para a metodologia de implementação interativa!

---

## 📋 Análise Comparativa

### Investidor10 - Site de CONTEÚDO/ANÁLISE
- **Foco:** Informação, educação, análise de mercado
- **Menu:** Categorias de ativos (Ações, FIIs, Internacionais)
- **Fluxo:** Pesquisar → Analisar → Comparar → Aprender
- **Monetização:** Assinatura PRO (ferramentas + carteiras)

### Exitus - Sistema de GESTÃO
- **Foco:** Controlar, analisar, otimizar investimentos pessoais
- **Menu:** Fluxo de trabalho do investidor
- **Fluxo:** Ver portfolio → Operar → Analisar → Otimizar
- **Monetização:** Sistema próprio (não assinatura)

---

## 🎯 **Proposta de Estrutura para Exitus**

### **1. Header Principal (Topo)**
```
[Logo Exitus] [Busca Rápida] [Notificações] [Usuário] [Config]
```

### **2. Menu Horizontal com Dropdowns (Estilo Investidor10)**

#### Estrutura Principal (Header)
```
[Logo Exitus] [Visão Geral ▼] [Operações ▼] [Ativos ▼] [Análises ▼] [Relatórios ▼] [Ferramentas ▼] [Alertas ▼] [Busca] [Notificações] [Usuário]
```

#### Dropdowns Detalhados

```
**Visão Geral ▼**
├── Dashboard
├── Patrimônio Total
├── Performance do Mês
└── Histórico Completo

**Operações ▼**
├── Comprar Ativos
├── Vender Ativos
├── Transferências
├── Rebalanceamento
└── Histórico de Operações

**Ativos ▼**
├── Ações
│   ├── Minhas Ações
│   ├── Buscar Ações
│   └── Setores
├── FIIs
│   ├── Meus FIIs
│   ├── Buscar FIIs
│   └── Tipos de Imóveis
├── ETFs
├── Renda Fixa
└── Criptoativos

**Análises ▼**
├── Proventos
│   ├── Recebidos
│   ├── Projetados
│   └── Calendário
├── Rentabilidade
│   ├── Por Período
│   ├── Por Ativo
│   └── Comparativo
├── Imposto de Renda
│   ├── Cálculo Mensal
│   ├── DARFs Pendentes
│   └── Declaração Anual
├── Alocação de Ativos
└── Análise de Riscos

**Relatórios ▼**
├── Relatórios Mensais
├── Relatórios Anuais
├── IR Completo
├── Exportar Dados
│   ├── Excel
│   ├── PDF
│   └── CSV
└── Compartilhar

**Ferramentas ▼**
├── Comparador de Ativos
├── Calculadora IR
├── Simulador de Investimentos
├── Projetor de Metas
└── Screeners

**Alertas ▼**
├── Alertas de Preço
├── Alertas de Dividendos
├── Alertas de Notícias
└── Alertas Personalizados
```

### **3. Área Principal (Content)**
**Layout Dinâmico baseado na seleção do menu:**

#### Dashboard (Visão Geral)
```
┌─────────────────────────────────────────────────────┐
│  RESUMO DO PATRIMÔNIO                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ R$ 125K  │ │ +5.2%   │ │ 12 Ativos│ │ 3 Setores│   │
│  │Total    │ │Mês      │ │Carteira │ │Diversif │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────────────────┤
│  GRÁFICO EVOLUÇÃO + TOP 5 ATIVOS                     │
└─────────────────────────────────────────────────────┘
```

#### Operações (Comprar/Vender)
```
┌─────────────────┐ ┌───────────────────────────────┐
│  1. SELECIONE    │ │  2. DETALHES DA OPERAÇÃO       │
│  O ATIVO         │ │  ┌─────────────┐ ┌───────────┐ │
│  ┌───────────┐  │ │  │Quantidade   │ │Preço     │ │
│  │[BUSCA]    │  │ │  │100         │ │R$45,67   │ │
│  └───────────┘  │ │  └─────────────┘ └───────────┘ │
│  ┌───────────┐  │ │  ┌─────────────┐ ┌───────────┐ │
│  │PETR4      │  │ │  │Tipo         │ │Total     │ │
│  │VALE3      │  │ │  │Compra       │ │R$4.567   │ │
│  │ITUB4      │  │ │  └─────────────┘ └───────────┘ │
│  └───────────┘  │ │                                   │
│                 │ │  [CANCELAR]  [CONFIRMAR COMPRA]   │
└─────────────────┘ └───────────────────────────────┘
```

### **4. Painel Direito (Contextual)**
**Aparece conforme a página:**

#### Na página de ativo:
```
┌─────────────────┐
│  PETR4           │
│  R$ 45,67       │
│  ▲ 2.3%         │
├─────────────────┤
│  [COMPRAR]      │
│  [VENDER]       │
├─────────────────┤
│  Últimos 30 dias │
│  [GRÁFICO]      │
├─────────────────┤
│  Proventos       │
│  R$ 120/ano     │
└─────────────────┘
```

#### No dashboard:
```
┌─────────────────┐
│  PRÓXIMOS       │
│  EVENTOS         │
├─────────────────┤
│ • Dividendo     │
│   PETR4         │
│   3 dias        │
│ • Vencimento    │
│   Tesouro       │
│   15 dias       │
├─────────────────┤
│  OPORTUNIDADES  │
│  • BBAS3 -10%   │
│  • WEGE3 +5%    │
└─────────────────┘
```

---

## 🎨 **Padrões Visuais (Inspiração Investidor10)**

### Cores
- **Primária:** Dourado/marrom (#a38c65)
- **Fundo:** Branco (#ffffff)
- **Cards:** #f8f9fa
- **Texto:** #212529 (principal), #6c757d (secundário)

### Tipografia
- **Fonte:** Nunito
- **Títulos:** 600 weight
- **Corpo:** 400 weight
- **Tamanhos:** 14px base, 16px cards, 20px seções

### Componentes
- **Cards:** Borda 1px #e9ecef, border-radius 8px
- **Tabelas:** Linhas separadas por border-bottom
- **Botões:** Sóbrios, sem gradientes
- **Gráficos:** Container branco com borda sutil

---

## 🔄 **Fluxos de Navegação**

### 1. Fluxo Principal (Investidor)
```
Login → Dashboard → 
[Ver Patrimônio] → [Ver Detalhes Ativo] → 
[Decidir Operar] → [Executar Compra/Venda] → 
[Volver Dashboard]
```

### 2. Fluxo de Análise
```
Dashboard → Análises → 
[Selecionar Tipo] → [Ver Gráficos] → 
[Exportar Relatório] → 
[Compartilhar]
```

### 3. Fluxo de Configuração
```
Dashboard → Alertas → 
[Novo Alerta] → [Configurar] → 
[Ativar] → 
[Monitorar]
```

---

## 📱 **Responsividade**

### Desktop (>1024px)
- Menu horizontal fixo (header)
- Conteúdo full-width
- Painel direito opcional (300px)
- Dropdowns com hover

### Tablet (768-1024px)
- Menu horizontal com click para dropdowns
- Painel direito recolhível
- Conteúdo adaptativo

### Mobile (<768px)
- Menu hambúrguer (☰) que abre dropdowns verticais
- Dropdowns em tela cheia
- Swipe para fechar menu
- Cards empilhados

---

## 🎨 **Cards - Duas Opções Disponíveis**

### Opção A: Cards Originais Investidor10
```css
/* Para quem prefere o visual ultra-denso original */
.card-ativo-original {
  height: 66px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* ticker + preço + variação + 15+ campos em linha */
}
```

### Opção B: Cards Modulares (Proposta)
```css
/* Para quem prefiere melhor escaneabilidade */
.card-ativo-modular {
  padding: 16px;
  border-radius: 8px;
  /* Informação hierárquica e organizada */
}
```

---

## 💡 **Insights do Investidor10 Adaptados**

### ✅ Manter
- **Densidade informativa:** Muita dados visível
- **Organização por categorias:** Lógica e intuitiva
- **Busca proeminente:** Acesso rápido
- **Notificações:** Contextuais e relevantes

### ✅ Manter (com adaptações)
- **Menu horizontal com dropdowns:** Mantido conforme solicitação
- **Densidade informativa:** Preservada como opção A
- **Organização por categorias:** Adaptada para contexto Exitus

### 🔄 Adaptar
- **Conteúdo educativo → Ferramentas operacionais**
- **Análise de mercado → Gestão pessoal**
- **Assinatura → Sistema próprio**

---

## 🚀 **Próximos Passos**

1. **Validar estrutura** com stakeholders
2. **Criar wireframes** das principais telas
3. **Implementar CSS** com padrões visuais
4. **Testar usabilidade** com usuários
5. **Iterar conforme feedback**

---

*Esta proposta combina o melhor do visual Investidor10 com as necessidades específicas do negócio Exitus.*
