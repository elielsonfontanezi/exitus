# 🧪 Plano de Testes E2E - Frontend V2.0

> **Data:** 17/03/2026  
> **Versão:** 1.0  
> **Status:** 📋 Planejamento  
> **Escopo:** 17 telas premium do ROADMAP_FRONTEND_V2.0

---

## 🎯 Objetivo

Validar todas as funcionalidades, UX e integrações das 17 telas premium do frontend V2.0, garantindo qualidade de produção e experiência de usuário comparável às melhores plataformas de investimento.

---

## 📊 Matriz de Cobertura

| Tela | Prioridade | Tipo Teste | Complexidade | Tempo Estimado |
|------|------------|------------|--------------|----------------|
| Dashboard | Alta | Regressão + Funcional | Média | 2h |
| Análise Ativos | Alta | Funcional + UX | Média | 1.5h |
| Performance | Alta | Funcional + Visual | Alta | 2h |
| Proventos | Média | Funcional | Média | 1h |
| Alocação | Alta | Funcional + Visual | Alta | 2h |
| Fluxo Caixa | Média | Funcional | Média | 1.5h |
| Imposto Renda | Alta | Funcional + Cálculo | Alta | 2.5h |
| Alertas | Média | Funcional + CRUD | Média | 1.5h |
| Comparador | Alta | Funcional + UX | Alta | 2h |
| Planos Compra | Alta | Funcional + CRUD | Alta | 2h |
| Planos Venda | Alta | Funcional + CRUD | Alta | 2h |
| Educação | Média | Navegação | Baixa | 1h |
| Configurações | Média | CRUD + UX | Média | 1.5h |
| Buy Signals | Alta | Funcional + IA | Alta | 2h |
| Portfolios | Alta | CRUD + Multi-moeda | Alta | 2h |
| Transações | Alta | CRUD + Exportação | Alta | 2h |
| Relatórios | Alta | Geração + Download | Alta | 2h |

**Total Estimado:** 30 horas de testes

---

## 🛠️ Ferramentas e Framework

### **Stack de Testes**
- **Playwright** - Automação E2E (Chrome, Firefox, Safari)
- **Jest** - Testes unitários JavaScript
- **Cypress** - Testes de integração (alternativa)
- **Lighthouse** - Performance e acessibilidade
- ** axe-core** - Testes de acessibilidade

### **Infraestrutura**
- **Docker** - Ambiente isolado
- **GitHub Actions** - CI/CD
- **Allure** - Relatórios de testes
- **BrowserStack** - Cross-browser testing

---

## 📋 Cenários de Teste por Tela

### **1. Dashboard (Alta Prioridade)**

#### **Funcionalidade**
- [ ] Carregamento inicial < 3s
- [ ] Cards exibem dados corretos
- [ ] Gráficos renderizam sem erro
- [ ] Currency toggle funciona
- [ ] Responsividade (mobile/tablet/desktop)

#### **Integração**
- [ ] API `/api/dashboard/summary` responde < 500ms
- [ ] Mock data fallback ativa quando API offline
- [ ] Tokens JWT autenticam corretamente

#### **UX/Visual**
- [ ] Animações suaves e performáticas
- [ ] Hover effects funcionam
- [ ] Loading states visíveis
- [ ] Cores consistentes com design system

### **2. Imposto de Renda (Alta Prioridade)**

#### **Funcionalidade**
- [ ] Cálculo automático de IR
- [ ] Simulação de compensação de prejuízos
- [ ] Geração de DARFs
- [ ] Exportação de relatórios

#### **Validação**
- [ ] Cálculos matematicamente corretos
- [ ] Regras fiscais aplicadas (15%, 20%)
- [ ] Prejuízos acumulados persistem
- [ ] Alíquotas por período corretas

#### **Edge Cases**
- [ ] Lucro zero (sem IR)
- [ ] Prejuízo maior que lucro
- [ ] Múltimos meses sem movimento
- [ ] Day trade vs swing trade

### **3. Planos de Compra/Venda (Alta Prioridade)**

#### **CRUD**
- [ ] Criar plano com configurações
- [ ] Editar plano existente
- [ ] Pausar/retomar execuções
- [ ] Excluir plano com confirmação

#### **Simulação**
- [ ] Simular DCA com diferentes períodos
- [ ] Calcular custo médio
- [ ] Projetar quantidade de ativos
- [ ] Comparar cenários

#### **Integração**
- [ ] API `/api/planos-compra` persiste dados
- [ ] Webhook de execuções simuladas
- [ ] Notificações de execução

---

## 🎮 Fluxos de Teste E2E

### **Fluxo 1: Investidor Novo**
1. Acessar dashboard → Ver resumo
2. Explorar buy signals → Analisar PETR4
3. Criar plano de compra → DCA mensal
4. Configurar alertas → Preço alvo
5. Visualizar portfolio → Novo plano

### **Fluxo 2: Investidor Avançado**
1. Análise de alocação → Rebalanceamento
2. Simular venda → Calcular IR
3. Gerar relatório → Download PDF
4. Exportar transações → CSV
5. Configurar moeda USD → Conversão

### **Fluxo 3: Teste de Stress**
1. Múltiplas abas (10+ telas)
2. Alternar moeda BRL/USD
3. Filtros complexos + paginação
4. Download simultâneo de relatórios
5. Reload sem perda de dados

---

## 📱 Dispositivos e Browsers

### **Desktop**
- Chrome 120+ (principal)
- Firefox 119+
- Safari 17+
- Edge 120+

### **Mobile**
- iOS Safari 17+
- Chrome Mobile 120+
- Samsung Internet 23+

### **Resoluções**
- Mobile: 375x667 (iPhone SE)
- Tablet: 768x1024 (iPad)
- Desktop: 1920x1080 (Full HD)
- 4K: 3840x2160

---

## 🚀 Estratégia de Execução

### **Fase 1: Testes de Fumaça (2 dias)**
- Validação básica de todas as telas
- Verificação de carregamento e navegação
- Testes de responsividade

### **Fase 2: Testes Funcionais (5 dias)**
- CRUD operations
- Cálculos e validações
- Integrações com APIs

### **Fase 3: Testes de UX (2 dias)**
- Fluxos completos do usuário
- Performance e acessibilidade
- Cross-browser testing

### **Fase 4: Testes de Stress (1 dia)**
- Múltiplos usuários simultâneos
- Grandes volumes de dados
- Condições de rede adversas

---

## 📊 Métricas e KPIs

### **Cobertura**
- **Cobertura de código:** > 80%
- **Cobertura de telas:** 100%
- **Cobertura de fluxos:** > 90%

### **Performance**
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1

### **Acessibilidade**
- **WCAG 2.1 AA:** 100%
- **Contraste ratio:** > 4.5:1
- **Navegação por teclado:** 100%

### **Bugs**
- **Críticos:** 0 bloqueantes
- **Altos:** < 5 por tela
- **Médios:** < 10 por tela
- **Baixos:** < 20 por tela

---

## 🐛 Bug Tracking e Relatórios

### **Classificação de Bugs**
- **P0 - Crítico:** Quebra de funcionalidade principal
- **P1 - Alto:** Funcionalidade importante com work-around
- **P2 - Médio:** Funcionalidade secundária afetada
- **P3 - Baixo:** Issues cosméticos ou melhorias

### **Relatórios Diários**
- **Testes executados:** X/Y
- **Pass rate:** XX%
- **Bugs encontrados:** X (P0: 0, P1: X, P2: X, P3: X)
- **Bloqueios:** Nenhum

### **Relatório Final**
- **Resumo executivo**
- **Matriz de cobertura**
- **Métricas de performance**
- **Recomendações de produção**
- **Débito técnico identificado**

---

## 🔄 Ambiente de Teste

### **Docker Compose**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
      - API_URL=http://backend:5000
  
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://test:test@db:5432/test
  
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=test
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
  
  playwright:
    image: mcr.microsoft.com/playwright:v1.40
    volumes:
      - ./tests:/tests
    depends_on:
      - frontend
      - backend
```

### **Dados de Teste**
- **Usuários:** 3 perfis (novato, intermediário, avançado)
- **Ativos:** 20 ativos variados (Ações, FIIs, ETFs, BDRs)
- **Transações:** 100+ transações históricas
- **Planos:** 10 planos ativos diversos

---

## ✅ Checklist de Pré-Produção

### **Funcional**
- [ ] Todos os testes passando
- [ ] Sem bugs P0/P1
- [ ] APIs respondendo < 500ms
- [ ] Mock data funcionando

### **Performance**
- [ ] Lighthouse score > 90
- [ ] Bundle size < 500KB
- [ ] Imagens otimizadas
- [ ] Cache configurado

### **Segurança**
- [ ] XSS prevenido
- [ ] CSRF tokens ativos
- [ ] Headers de segurança
- [ ] Sensitive data não exposto

### **UX**
- [ ] Loading states visíveis
- [ ] Error handling amigável
- [ ] Feedback de ações
- [ ] Navegação intuitiva

---

## 📈 Timeline

| Semana | Atividades | Entregáveis |
|--------|------------|-------------|
| 1 | Setup ambiente + Fase 1 | Configuração + Testes de fumaça |
| 2 | Fase 2 + início Fase 3 | Testes funcionais + UX parcial |
| 3 | Fase 3 + Fase 4 | Testes completos + Relatório final |
| 4 | Validação + correções | Homologação + Go/No-Go |

**Total:** 3 semanas para testes completos

---

## 🎯 Critérios de Aceite

### **Go para Produção**
- ✅ 95%+ testes passando
- ✅ 0 bugs P0/P1
- ✅ Performance Lighthouse > 90
- ✅ Acessibilidade WCAG 2.1 AA
- ✅ Documentação completa

### **No-Go para Produção**
- ❌ Bugs P0 bloqueantes
- ❌ Performance < 80 Lighthouse
- ❌ Cobertura < 70%
- ❌ Issues de segurança
- ❌ UX não validada

---

## 📞 Contato e Suporte

**Equipe de Testes:**
- QA Lead: [nome]
- Test Engineers: [nomes]
- Frontend Devs: [nomes]

**Comunicação:**
- Daily: 9h30 (15 min)
- Weekly: Sexta 16h (1h)
- Emergency: Slack #frontend-tests

---

**Status:** 📋 **AGUARDANDO APROVAÇÃO PARA INÍCIO**  
**Próximo Passo:** Setup do ambiente de testes  
**Previsão Início:** 24/03/2026
