# 📊 Dashboard v2 - Melhorias Planejadas

> **Data:** 21/03/2026  
> **Status:** Planejamento  
> **Prioridade:** Média  
> **Responsável:** A definir

---

## 🎯 **Contexto**

Dashboard v1 (Investidor10) foi aprovado com layout básico:
- ✅ Resumo de patrimônio (4 cards)
- ✅ Gráfico de evolução
- ✅ Top 5 ativos
- ✅ Próximos eventos
- ✅ Oportunidades

**Feedback do usuário (21/03/2026):**
> "Vale uma reavaliação do que ainda pode ser apresentado na tela principal. Por exemplo, no Dashboard atual há cards para Brasil, EUA e Internacional e Carteira, alocação Gráfica, alertas recentes e últimas transações. Poderia também mostrar saldo em caixa e o chaveamento entre moedas BRL/USD."

---

## 📋 **Componentes a Adicionar**

### **1. Visão Multi-Mercado** ⭐ ALTA PRIORIDADE

**Descrição:**
Cards separados para Brasil, EUA e Internacional mostrando:
- Patrimônio em cada mercado
- Percentual do total
- Rentabilidade individual

**Layout:**
```
┌─────────────┬─────────────┬─────────────┐
│ 🇧🇷 Brasil  │ 🇺🇸 EUA     │ 🌍 Internacional│
│ R$ 75.000   │ $8.500      │ €2.300      │
│ 60%         │ 30%         │ 10%         │
│ +5.2%       │ +8.1%       │ +3.5%       │
└─────────────┴─────────────┴─────────────┘
```

**Implementação:**
- CSS: `.card-mercado` (novo)
- Dados: API `/api/v1/dashboard/multi-mercado`
- Posição: Após resumo de patrimônio

---

### **2. Saldo em Caixa + Chaveamento BRL/USD** ⭐ ALTA PRIORIDADE

**Descrição:**
Card mostrando saldo disponível em caixa com toggle BRL/USD

**Layout:**
```
┌─────────────────────────────────┐
│ Saldo em Caixa                  │
│ R$ 12.450,00  [BRL] [USD]      │
│ (ou $2,280.50 se USD)          │
└─────────────────────────────────┘
```

**Implementação:**
- CSS: `.card-saldo-caixa` (novo)
- JS: Toggle BRL/USD (Alpine.js ou JS puro)
- API: `/api/v1/carteira/saldo-caixa`
- Conversão: Taxa do dia (API externa ou cache)
- Posição: No resumo de patrimônio (5º card)

---

### **3. Alocação Gráfica** 📊 MÉDIA PRIORIDADE

**Descrição:**
Gráfico pizza/donut mostrando distribuição de ativos

**Opções de visualização:**
- Por tipo (Ações, FIIs, Renda Fixa, Cripto)
- Por setor (Financeiro, Energia, Tecnologia, etc.)
- Por mercado (BR, US, INTL)

**Implementação:**
- Chart.js (tipo: doughnut)
- CSS: `.chart-alocacao` (já existe)
- Dropdown para alternar visualização
- Posição: Coluna lateral ou grid 2/3

---

### **4. Alertas Recentes** 🔔 MÉDIA PRIORIDADE

**Descrição:**
Lista de alertas disparados recentemente

**Tipos de alerta:**
- Preço atingido (alvo ou stop)
- Dividendos próximos
- Notícias relevantes
- Vencimentos

**Layout:**
```
┌──────────────────────────────────┐
│ Alertas Recentes                 │
│ • ⚠️ PETR4 atingiu R$ 40,00     │
│ • 💰 VALE3 dividendo em 2 dias  │
│ • 📰 ITUB4 notícia relevante    │
└──────────────────────────────────┘
```

**Implementação:**
- CSS: `.alertas-recentes` (novo)
- API: `/api/v1/alertas/recentes?limit=5`
- Ícones: Font Awesome
- Posição: Coluna lateral

---

### **5. Últimas Transações** 💸 MÉDIA PRIORIDADE

**Descrição:**
Lista das 5 últimas operações realizadas

**Layout:**
```
┌──────────────────────────────────┐
│ Últimas Transações               │
│ • PETR4 - Compra - R$ 4.567     │
│   100 ações @ R$ 45,67          │
│ • VALE3 - Venda - R$ 3.200      │
│   50 ações @ R$ 64,00           │
│ • ITUB4 - Compra - R$ 2.890     │
│   100 ações @ R$ 28,90          │
└──────────────────────────────────┘
```

**Implementação:**
- CSS: `.ultimas-transacoes` (novo)
- API: `/api/v1/operacoes/recentes?limit=5`
- Cores: Verde (compra), Vermelho (venda)
- Posição: Coluna lateral ou grid principal

---

## 🎨 **Proposta de Layout Dashboard v2**

### **Opção A: Layout Denso (Investidor10 Style)**
```
┌─────────────────────────────────────────────────────────────┐
│ RESUMO PATRIMÔNIO (5 cards: Total, Rent, Ativos, Setores, Caixa) │
│ [BRL/USD Toggle no card Caixa]                             │
├──────────────────────┬──────────────────────────────────────┤
│ MULTI-MERCADO        │ ALOCAÇÃO GRÁFICA                     │
│ BR / US / INTL       │ (Pizza: Tipo/Setor/Mercado)          │
├──────────────────────┼──────────────────────────────────────┤
│ GRÁFICO EVOLUÇÃO     │ ALERTAS RECENTES                     │
│ (12 meses)           │ (5 itens)                            │
├──────────────────────┼──────────────────────────────────────┤
│ TOP 5 ATIVOS         │ ÚLTIMAS TRANSAÇÕES                   │
│ (Tabela)             │ (5 itens)                            │
└──────────────────────┴──────────────────────────────────────┘
```

### **Opção B: Layout Modular (Mais Espaçado)**
```
┌─────────────────────────────────────────────────────────────┐
│ RESUMO PATRIMÔNIO (5 cards em grid)                         │
├─────────────────────────────────────────────────────────────┤
│ MULTI-MERCADO (3 cards: BR / US / INTL)                    │
├──────────────────────┬──────────────────────────────────────┤
│ GRÁFICO EVOLUÇÃO     │ ALOCAÇÃO GRÁFICA                     │
│ (2/3)                │ (1/3)                                │
├──────────────────────┼──────────────────────────────────────┤
│ TOP 5 ATIVOS         │ ALERTAS RECENTES                     │
│ (2/3)                │ (1/3)                                │
├──────────────────────┼──────────────────────────────────────┤
│ PRÓXIMOS EVENTOS     │ ÚLTIMAS TRANSAÇÕES                   │
│ (1/2)                │ (1/2)                                │
└──────────────────────┴──────────────────────────────────────┘
```

---

## 🔄 **Plano de Implementação**

### **Fase 1: Componentes Essenciais** (Sprint 1)
- [ ] Saldo em Caixa + Toggle BRL/USD
- [ ] Visão Multi-Mercado (BR/US/INTL)
- [ ] Últimas Transações

### **Fase 2: Visualizações** (Sprint 2)
- [ ] Alocação Gráfica (Pizza/Donut)
- [ ] Alertas Recentes
- [ ] Ajustes de layout responsivo

### **Fase 3: Refinamento** (Sprint 3)
- [ ] Testes de performance
- [ ] Otimização de carregamento
- [ ] Validação com usuário
- [ ] Ajustes finais

---

## 📊 **APIs Necessárias**

### **Backend:**
- [ ] `GET /api/v1/dashboard/multi-mercado` - Dados BR/US/INTL
- [ ] `GET /api/v1/carteira/saldo-caixa` - Saldo disponível
- [ ] `GET /api/v1/alertas/recentes?limit=5` - Alertas disparados
- [ ] `GET /api/v1/operacoes/recentes?limit=5` - Últimas transações
- [ ] `GET /api/v1/dashboard/alocacao?tipo=ativo|setor|mercado` - Dados para gráfico

### **Frontend:**
- [ ] Componente Toggle BRL/USD (reutilizável)
- [ ] Componente Card Mercado (reutilizável)
- [ ] Componente Lista Alertas
- [ ] Componente Lista Transações

---

## 🎯 **Critérios de Sucesso**

- [ ] Todas as informações do dashboard antigo preservadas
- [ ] Toggle BRL/USD funcionando
- [ ] Visão multi-mercado clara e objetiva
- [ ] Layout responsivo (Desktop/Tablet/Mobile)
- [ ] Performance: Carregamento < 2s
- [ ] Aprovação do usuário

---

## 📝 **Notas**

- **Prioridade 1:** Saldo Caixa + Multi-Mercado (funcionalidades existentes)
- **Prioridade 2:** Alertas + Transações (novos dados)
- **Prioridade 3:** Alocação Gráfica (visualização adicional)

**Decisão de Layout:** A definir com usuário (Opção A vs Opção B)

---

**Próximo Passo:** Aguardar aprovação do plano e definir sprint para implementação.
