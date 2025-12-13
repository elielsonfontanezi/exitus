# 🧹 PLANO DE LIMPEZA E CONSOLIDAÇÃO - DOCS/

**Sistema Exitus - Reorganização da Documentação**  
**Data:** 13/12/2025

---

## 📋 PROBLEMAS A RESOLVER

### 1. Duplicação
- `M3_CHECKLIST.md` vs `MODULO3_CHECKLIST.md`

### 2. Inconsistência de Nomenclatura
- Mistura de `moduloX_*.md` (lowercase) e `MODULOX_*.md` (uppercase)

### 3. Documentação Dupla (Narrativo + Checklist)
- `modulo0_ambiente.md` + `MODULO0_CHECKLIST.md`
- `modulo1_database.md` + `MODULO1_CHECKLIST.md`
- `modulo2_backend_auth.md` + `MODULO2_CHECKLIST.md`
- `modulo3_backend_financeiro.md` + `MODULO3_CHECKLIST.md`
- `modulo4_backend_buy_signals.md` + `modulo4_backend_integracoes.md` + `MODULO4_CHECKLIST.md`
- `modulo5_frontend_base.md` + `MODULO5_CHECKLIST.md`
- `modulo6_frontend_dashboards.md` + `MODULO6_CHECKLIST.md`

---

## ✅ PLANO DE AÇÃO

### Fase 1: Análise e Decisão (VOCÊ VALIDA)

#### Opção A: Manter APENAS CHECKLISTs ⭐ **RECOMENDADO**
**Vantagens:**
- Documentos objetivos e práticos
- Fácil de atualizar (lista de tarefas)
- Padronizado (todos os módulos têm)

**Ação:**
```bash
# Remover documentos narrativos desatualizados
rm docs/M3_CHECKLIST.md                      # Duplicata
rm docs/modulo0_ambiente.md                  # Info já em MODULO0_CHECKLIST.md
rm docs/modulo1_database.md                  # Info já em MODULO1_CHECKLIST.md
rm docs/modulo2_backend_auth.md              # Info já em MODULO2_CHECKLIST.md
rm docs/modulo3_backend_financeiro.md        # Info já em MODULO3_CHECKLIST.md
rm docs/modulo4_backend_buy_signals.md       # Info já em MODULO4_CHECKLIST.md
rm docs/modulo4_backend_integracoes.md       # Info já em MODULO4_CHECKLIST.md
rm docs/modulo5_frontend_base.md             # Info já em MODULO5_CHECKLIST.md
rm docs/modulo6_frontend_dashboards.md       # Info já em MODULO6_CHECKLIST.md
```

**Resultado Final:**
```
docs/
├── endpoints_m2_m3.txt
├── exitus_db_structure.txt
├── INSTALACAO_MODULO1.md
├── MODULO0_CHECKLIST.md          ✅ Único doc M0
├── MODULO1_CHECKLIST.md          ✅ Único doc M1
├── MODULO2_CHECKLIST.md          ✅ Único doc M2
├── MODULO3_CHECKLIST.md          ✅ Único doc M3
├── MODULO3_COMPLETO.md           ✅ Documentação detalhada M3
├── MODULO4_CHECKLIST.md          ✅ Único doc M4
├── MODULO5_CHECKLIST.md          ✅ Único doc M5
├── MODULO6_CHECKLIST.md          ✅ Único doc M6
├── MODULO7_ANALISE_ESTRATEGICA.md
├── MODULO7_EXEMPLOS_PRATICOS.md
├── MODULO7_PROMPT_DERIVADO.md
├── MODULO7.5_APIS.md
├── MODULO7.5_CHECKLIST.md
├── MODULO7.5_TOKENS.md
└── PLANO_APIS_EXTERNAS_E_CALCULOS.md
```

---

#### Opção B: Consolidar em Documentos Completos (Estilo M3)
**Vantagens:**
- Documentação rica e detalhada
- Útil para onboarding e consulta

**Desvantagens:**
- Mais trabalhoso para manter atualizado
- Requer consolidação manual

**Ação:**
```bash
# Consolidar cada módulo em um doc COMPLETO
# Exemplo: modulo0_ambiente.md + MODULO0_CHECKLIST.md → MODULO0_COMPLETO.md
```

---

### Fase 2: Padronização de Nomenclatura

#### Renomear para Uppercase (Padrão dos CHECKLISTs)
```bash
# Renomear para manter consistência
mv docs/endpoints_m2_m3.txt docs/ENDPOINTS_M2_M3.txt
mv docs/exitus_db_structure.txt docs/EXITUS_DB_STRUCTURE.txt
```

---

### Fase 3: Criar Estrutura de Pastas (Opcional, mas recomendado)

```bash
# Criar estrutura organizada
mkdir -p docs/00_CORE
mkdir -p docs/01_API_REFERENCE
mkdir -p docs/02_MODULES
mkdir -p docs/03_VALIDATION

# Mover arquivos
mv docs/EXITUS_DB_STRUCTURE.txt docs/00_CORE/
mv docs/ENDPOINTS_M2_M3.txt docs/01_API_REFERENCE/
mv docs/PLANO_APIS_EXTERNAS_E_CALCULOS.md docs/01_API_REFERENCE/

mv docs/MODULO*_CHECKLIST.md docs/02_MODULES/
mv docs/MODULO*_COMPLETO.md docs/02_MODULES/
mv docs/MODULO7_*.md docs/02_MODULES/
mv docs/MODULO7.5_*.md docs/02_MODULES/

mv docs/INSTALACAO_MODULO1.md docs/02_MODULES/
```

---

## 🎯 RECOMENDAÇÃO FINAL: OPÇÃO A (Manter CHECKLISTs)

### Execução Imediata

```bash
#!/bin/bash
# Script de limpeza - docs/cleanup_docs.sh

echo "🧹 Limpando documentação duplicada/desatualizada..."

# 1. Remover duplicatas
rm -f docs/M3_CHECKLIST.md
echo "✅ Removido: M3_CHECKLIST.md (duplicata)"

# 2. Remover documentos narrativos desatualizados
rm -f docs/modulo0_ambiente.md
rm -f docs/modulo1_database.md
rm -f docs/modulo2_backend_auth.md
rm -f docs/modulo3_backend_financeiro.md
rm -f docs/modulo4_backend_buy_signals.md
rm -f docs/modulo4_backend_integracoes.md
rm -f docs/modulo5_frontend_base.md
rm -f docs/modulo6_frontend_dashboards.md
echo "✅ Removidos: 8 documentos narrativos (info consolidada nos CHECKLISTs)"

# 3. Padronizar nomenclatura
if [ -f docs/endpoints_m2_m3.txt ]; then
    mv docs/endpoints_m2_m3.txt docs/ENDPOINTS_M2_M3.txt
    echo "✅ Renomeado: endpoints_m2_m3.txt → ENDPOINTS_M2_M3.txt"
fi

echo ""
echo "📊 Estrutura final:"
ls -1 docs/
echo ""
echo "✅ Limpeza concluída!"
```

### Validação Pós-Limpeza

```bash
#!/bin/bash
# Script de validação - docs/validate_docs.sh

echo "🔍 Validando estrutura de documentação..."

# Verificar se todos os módulos têm CHECKLIST
MODULES=(0 1 2 3 4 5 6)
for M in "${MODULES[@]}"; do
    FILE="docs/MODULO${M}_CHECKLIST.md"
    if [ -f "$FILE" ]; then
        echo "✅ $FILE"
    else
        echo "❌ FALTANDO: $FILE"
    fi
done

# Verificar documentação M7
M7_DOCS=(
    "docs/MODULO7_ANALISE_ESTRATEGICA.md"
    "docs/MODULO7_EXEMPLOS_PRATICOS.md"
    "docs/MODULO7_PROMPT_DERIVADO.md"
    "docs/MODULO7.5_APIS.md"
    "docs/MODULO7.5_CHECKLIST.md"
    "docs/MODULO7.5_TOKENS.md"
)

for DOC in "${M7_DOCS[@]}"; do
    if [ -f "$DOC" ]; then
        echo "✅ $DOC"
    else
        echo "❌ FALTANDO: $DOC"
    fi
done

echo ""
echo "🎯 Validação concluída!"
```

---

## 📝 RESULTADO ESPERADO

### Antes (27 arquivos, redundância)
```
docs/
├── M3_CHECKLIST.md                      ❌ DUPLICATA
├── MODULO3_CHECKLIST.md                 ✅
├── modulo3_backend_financeiro.md        ❌ DESATUALIZADO
├── MODULO3_COMPLETO.md                  ✅
├── [... 23 outros arquivos ...]
```

### Depois (17 arquivos, organizado)
```
docs/
├── ENDPOINTS_M2_M3.txt                  ✅ RENOMEADO
├── EXITUS_DB_STRUCTURE.txt              ✅ RENOMEADO
├── INSTALACAO_MODULO1.md                ✅
├── MODULO0_CHECKLIST.md                 ✅
├── MODULO1_CHECKLIST.md                 ✅
├── MODULO2_CHECKLIST.md                 ✅
├── MODULO3_CHECKLIST.md                 ✅
├── MODULO3_COMPLETO.md                  ✅
├── MODULO4_CHECKLIST.md                 ✅
├── MODULO5_CHECKLIST.md                 ✅
├── MODULO6_CHECKLIST.md                 ✅
├── MODULO7_ANALISE_ESTRATEGICA.md       ✅
├── MODULO7_EXEMPLOS_PRATICOS.md         ✅
├── MODULO7_PROMPT_DERIVADO.md           ✅
├── MODULO7.5_APIS.md                    ✅
├── MODULO7.5_CHECKLIST.md               ✅
├── MODULO7.5_TOKENS.md                  ✅
└── PLANO_APIS_EXTERNAS_E_CALCULOS.md    ✅
```

**Redução:** 27 → 18 arquivos (-33%)  
**Ganho:** Zero duplicação, nomenclatura consistente

---

## ⚠️ BACKUP ANTES DE EXECUTAR

```bash
# Criar backup da documentação atual
tar -czf docs_backup_$(date +%Y%m%d_%H%M%S).tar.gz docs/
echo "✅ Backup criado"
```

---

## 🚀 PRÓXIMOS PASSOS

Após executar a limpeza:

1. **Validar** estrutura com `validate_docs.sh`
2. **Criar** documentos críticos:
   - TROUBLESHOOTING_GUIDE.md
   - API_REFERENCE_COMPLETE.md
   - ARCHITECTURE_OVERVIEW.md
3. **Atualizar** README.md com índice da documentação

---

**Você aprova a execução do Plano de Limpeza (Opção A)?**
