# 📋 Plano de Reorganização da Documentação

> **Data:** 17/03/2026  
> **Status:** 📋 **PLANEJAMENTO**  
> **Objetivo:** Centralizar e otimizar documentação

---

## 🎯 Problema Identificado

Múltiplos roadmaps e documentos de status criando confusão e duplicação de informações.

---

## 📊 Análise dos Documentos Atuais

### **Documentos de Status (Consolidar em PROJECT_STATUS.md)**
- `ROADMAPS_STATUS_GERAL.md` - Status geral dos roadmaps ✅
- `PROXIMA_FASE_ESTRATEGIA.md` - Próximos passos ✅
- `FRONTEND_V2_STATUS.md` - Status do frontend V2 ✅

### **Roadmaps (Manter individuais)**
- `ROADMAP_BACKEND.md` - Específico do backend ✅
- `ROADMAP_FRONTEND_V2.md` - Específico do frontend V2 ✅
- `ROADMAP_TESTES_FRONTEND.md` - Específico de testes ✅

### **Documentos Históricos (Arquivar)**
- `ROADMAP_FRONTEND.md` - Obsoleto, mas tem valor histórico 📁
- `ROADMAP_FASE4.md` - Integrado ao backend 📁

### **Análises e GAPs (Reorganizar)**
- `FRONTEND_ANALISE_COMPLETA.md` - Análise técnica importante 📋
- `FRONTEND_GAPS_RESOLVIDOS.md` - GAPs resolvidos importantes 📋
- `FRONTEND_REFACTOR_PROPOSAL.md` - Proposta técnica 📋
- `TESTES_E2E_PLAN.md` - Plano original de testes 📋

---

## 🗂️ Estrutura Proposta

### **1. Documentos Centrais (Nível 1)**
```
docs/
├── README.md                    # Visão geral do projeto
├── PROJECT_STATUS.md           # Status centralizado (NOVO)
├── CHANGELOG.md                # Histórico de mudanças
└── ROADMAPS_SUMMARY.md         # Sumário de todos os roadmaps (NOVO)
```

### **2. Roadmaps Específicos (Nível 2)**
```
docs/
├── ROADMAP_BACKEND.md          # Backend específico
├── ROADMAP_FRONTEND_V2.md      # Frontend V2 específico
└── ROADMAP_TESTES_FRONTEND.md  # Testes específicos
```

### **3. Documentação Técnica (Nível 3)**
```
docs/
├── ARCHITECTURE.md             # Arquitetura
├── API_REFERENCE.md            # APIs
├── CODING_STANDARDS.md         # Padrões
├── MODULES.md                  # Módulos
└── ENUMS.md                    # Enumerações
```

### **4. GAPs e Especificações (Nível 4)**
```
docs/
├── GAPs/                       # NOVO DIRETÓRIO
│   ├── FRONTEND_ANALISE.md     # Movido e renomeado
│   ├── FRONTEND_GAPS.md        # Movido e renomeado
│   └── [outros GAPs]
└── EXITUS-*.md                 # GAPs existentes
```

### **5. Documentos Históricos (Arquivar)**
```
docs/
└── archive/                    # NOVO DIRETÓRIO
    ├── ROADMAP_FRONTEND.md     # Movido
    ├── ROADMAP_FASE4.md        # Movido
    └── [outros obsoletos]
```

---

## 📋 Ações Propostas

### **Criar Novos Documentos**
1. `PROJECT_STATUS.md` - Status centralizado (já criado)
2. `ROADMAPS_SUMMARY.md` - Sumário executivo
3. `docs/GAPs/` - Diretório para GAPs frontend
4. `docs/archive/` - Arquivo histórico

### **Reorganizar Conteúdo**
1. Mover análises frontend para `docs/GAPs/`
2. Mover documentos obsoletos para `docs/archive/`
3. Criar sumário interligando todos os roadmaps
4. Atualizar referências cruzadas

### **Manter Inalterados**
- Roadmaps específicos (BACKEND, FRONTEND_V2, TESTES)
- Documentação técnica (ARCHITECTURE, API, etc.)
- GAPs existentes (EXITUS-*.md)
- Documentos operacionais

---

## 🎯 Benefícios Esperados

### **Clareza**
- Único ponto de status (`PROJECT_STATUS.md`)
- Separação clara entre histórico e atual
- Navegação intuitiva

### **Manutenibilidade**
- Menos duplicação
- Atualizações centralizadas
- Arquivamento organizado

### **Acessibilidade**
- Documentos fáceis de encontrar
- Hierarquia lógica
- Referências claras

---

## 📝 Próximos Passos

1. **Criar estrutura de diretórios**
2. **Mover documentos conforme plano**
3. **Criar ROADMAPS_SUMMARY.md**
4. **Atualizar referências cruzadas**
5. **Fazer commit organizado**

---

## ⚠️ Cuidados a Tomar

- Preservar histórico importante
- Manter todos os GAPs existentes
- Não perder documentação técnica
- Testar todas as referências

---

## 🔄 Fluxo de Trabalho

```
HOJE: Múltiplos status dispersos
↓
REORGANIZAR: Estrutura clara
↓
RESULTADO: Documentação centralizada e acessível
```

---

*Status: 📋 Planejamento concluído, aguardando aprovação*
