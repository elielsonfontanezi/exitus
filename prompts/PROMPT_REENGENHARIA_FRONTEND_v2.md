# 🎯 PROMPT: REENGENHARIA FRONTEND EXITUS v2.0

**Persona:** Cascade (Persona 2 - docs/PERSONAS.md)  
**Modelo IA Recomendado:** Claude Sonnet (complexidade moderada-alta)  
**Créditos Estimados:** 60-80

---

## 📋 CONTEXTO ESTRATÉGICO

O Exitus tem um **backend robusto** com:
- ✅ 491 testes passando (100%)
- ✅ 67+ endpoints REST
- ✅ PostgreSQL com 22 tabelas
- ✅ Motor fiscal completo (IR, IOF, DARF)
- ✅ Multi-moeda (BRL/USD) e multi-mercado
- ✅ APIs de cotações em tempo real

**Frontend atual:** HTMX 1.9.10 + Alpine.js 3.x + TailwindCSS 3.4
- Protótipo funcional, mas limitado em UX
- Sem componentização sistemática
- Dashboard básico, sem diferenciação mercados

---

## 🎯 OBJETIVOS DA REENGENHARIA

### 1. **Avaliação Crítica de Stack**
- Analisar se HTMX + Alpine.js escala para complexidade desejada
- Comparar com alternativas (Next.js, Vue.js, React)
- Considerar curva de aprendizado vs produtividade
- **Decisão:** Justificar mantimento ou migração

### 2. **Dashboard Global Multi-Mercado**
- Diferenciar visualmente ativos 🇧🇷 BRL vs 🇺🇸 USD vs 🌍 INTL
- Métricas de performance por mercado/corretora
- Alocação geográfica com mapa visual
- Timeline unificada de eventos

### 3. **Sistema de Componentes**
- Criar biblioteca de componentes Jinja2 reutilizáveis
- Cards: ativo, portfolio, provento, alerta
- Badges: status, tipo_ativo, moeda
- Tabelas dinâmicas com sorting/filtering
- Forms modais com validação

### 4. **UX Especializada**
- **Dividendos:** Calendário visual, timeline, projeções
- **IR:** Dashboard fiscal, DARFs pendentes, relatórios
- **Buy Signals:** Cards interativos com detalhes
- **Planos de Compra:** Novo conceito (ver detalhes abaixo)
- **Rentabilidade:** Gráficos avançados (Chart.js)

### 5. **Planos de Compra (NOVO CONCEITO)**
- **Ideia:** Dashboard para visualizar melhores oportunidades de compra
- **Contexto:** Lista de ativos de interesse (já na carteira ou não)
- **Funcionalidade:** Análise comparativa de preço teto vs preço atual
- **Diferencial vs Buy Signals:** 
  - Buy Signals: Score individual (0-100) por ativo
  - Planos de Compra: Visão consolidada multi-ativos com priorização
- **Implementação:** Nova rota `/api/planos-compra` e dashboard dedicado

---

## 📚 FONTES DE VERDADE (LEITURA OBRIGATÓRIA)

Antes de qualquer proposta, ler e processar:

### **Documentação Essencial:**
1. **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Contratos completos
2. **[ENUMS.md](docs/ENUMS.md)** - 15 TipoAtivo, mapeamentos
3. **[ROADMAP.md](docs/ROADMAP.md)** - Status atual (83% GAPs)
4. **[VISION.md](docs/VISION.md)** - Proposta de valor
5. **[CODING_STANDARDS.md](docs/CODING_STANDARDS.md)** - snake_case

### **GAPs Relevantes:**
6. **[EXITUS-DIVCALENDAR-001.md](docs/EXITUS-DIVCALENDAR-001.md)** - Calendário dividendos
7. **[EXITUS-IR-001.md](docs/EXITUS-IR-001.md)** - Motor fiscal
8. **[EXITUS-EXPORT-001.md](docs/EXITUS-EXPORT-001.md)** - Exportação

### **Dados Estruturais:**
9. **[EXITUS_DB_STRUCTURE.txt](docs/EXITUS_DB_STRUCTURE.txt)** - Schema completo
10. **[EXITUS_ER_DIAGRAM.md](docs/EXITUS_ER_DIAGRAM.md)** - Visualização

---

## 🔍 ANÁLISE OBRIGATÓRIA (PRIMEIRO PASSO)

### **1. Diagnóstico do Frontend Atual**
- Listar todos os templates em `/frontend/app/templates/`
- Identificar componentes repetitivos
- Mapear dependências (HTMX, Alpine.js, Tailwind)
- Verificar integração com APIs do backend
- **DECISÃO CRÍTICA:** Manter estrutura atual vs iniciar do zero?

### **2. Avaliação de Reinício (Opção Zero)**
- **Prós:** Arquitetura limpa, padrão moderno, sem débito técnico
- **Contras:** Reimplementar tudo, tempo extra, risco de regressão
- **Critérios:** 
  - Se >50% dos templates precisam refatoração → Considerar reinício
  - Se performance <80% do esperado → Considerar reinício
  - Se UX atual inadequada para multi-mercado → Considerar reinício

### **3. Análise de Performance**
- Tempo de carregamento do dashboard
- Uso de memória no browser
- Requisições paralelas vs sequenciais
- Cache implementado

### **4. Avaliação de UX**
- Fluxo de navegação atual
- Responsividade mobile
- Acessibilidade (WCAG)
- Feedback visual ao usuário

### **5. Análise de Buy Signals vs Planos de Compra**
- **Buy Signals existentes:** `/api/buy-signals/watchlist-top`
- **Funcionalidade atual:** Score individual (0-100), margem de segurança
- **Gap identificado:** Não há visão consolidada multi-ativos
- **Oportunidade:** Planos de Compra como evolução natural
  - Dashboard comparativo (Ações BR, FIIs BR, etc.)
  - Priorização baseada em múltiplos critérios
  - Integração com carteira existente

---

## 📋 PLANO DE REMODELAGEM (ENTREGA ESPERADA)

### **Fase 1: Decisão de Stack**
```
Análise comparativa:
✅ HTMX + Alpine.js: Manter? Justificar
❌ Next.js: Migrar? Custo/benefício
❌ Vue.js: Alternativa viável?
```

### **Fase 2: Arquitetura de Componentes**
```
Estrutura proposta:
├── components/
│   ├── cards/
│   ├── badges/
│   ├── tables/
│   └── forms/
├── layouts/
├── pages/
└── utils/
```

### **Fase 3: Dashboard Global**
```
Layout proposto:
┌─────────────────────────────────┐
│ Header: User + Moedas + Mercado │
├─────────────────────────────────┤
│ KPIs: Patrimônio, Rentabilidade │
├─────────────────────────────────┤
│ Gráfico: Alocação Geográfica    │
├─────────────────────────────────┤
│ Cards: Top 5 Ativos por Mercado │
└─────────────────────────────────┘
```

### **Fase 4: Implementação**
- Componentização progressiva
- Testes de UI (Cypress?)
- Documentação de componentes
- Migração sem quebra

---

## 🚨 REGRAS CRÍTICAS DE EXECUÇÃO

### **Fluxo Obrigatório:**
1. **ANÁLISE** → Ler fontes de verdade
2. **DIAGNÓSTICO** → Apresentar findings
3. **PLANO** → Propor arquitetura
4. **APROVAÇÃO** → Aguardar "APROVADO"
5. **IMPLEMENTAÇÃO** → Executar fase a fase

### **Proibições:**
- ❌ Não implementar sem aprovação
- ❌ Não mudar stack sem justificativa detalhada
- ❌ Não quebrar funcionalidades existentes
- ❌ Não ignorar contratos da API

### **Obrigações:**
- ✅ Manter 100% funcionalidade atual
- ✅ Preservar todos os endpoints
- ✅ Usar snake_case em IDs/classes
- ✅ Documentar cada componente

### **Colaboração com Mantenedor (CRÍTICO)**
- **Discussão Obrigatória:** Antes de implementar qualquer interface
- **Validação de UX:** Apresentar mockups/wireframes para aprovação
- **Priorização:** Alinhar features com necessidades reais do usuário
- **Feedback Iterativo:** Refinar com base no conhecimento do mantenedor
- **Foco no Valor:** Garantir que cada tela resolva um problema real

**Por quê?**
- Mantenedor tem conhecimento profundo do domínio e fluxos reais
- IA pode propor soluções tecnicamente corretas mas inadequadas
- Colaboração garante interfaces que realmente agregam valor
- Evita retrabalho e features desnecessárias

---

## 🎯 AÇÃO IMEDIATA

1. **Confirme leitura** dos 10 documentos listados
2. **Apresente diagnóstico** do frontend atual
3. **Proponha decisão** sobre stack (manter vs migrar vs reinício)
4. **Esboçe layout** do Dashboard Global
5. **Analise Planos de Compra** vs Buy Signals existentes
6. **Recomende implementação** do novo conceito
7. **Sugira pontos de discussão** com o mantenedor para cada interface

**IMPORTANTE:** Prepare uma lista de perguntas para o mantenedor sobre:
- Fluxos reais de uso
- Prioridades de negócio
- Critérios de decisão (ex: Planos de Compra)
- Necessidades não atendidas

**Aguardando sua análise completa antes de prosseguir...**
