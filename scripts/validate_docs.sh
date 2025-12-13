#!/bin/bash
# Script de validação da documentação
# Criado: 13/12/2025

echo "🔍 Validando estrutura de documentação..."
echo ""

ERRORS=0

# Verificar se todos os módulos têm CHECKLIST
MODULES=(0 1 2 3 4 5 6)
for M in "${MODULES[@]}"; do
    FILE="docs/MODULO${M}_CHECKLIST.md"
    if [ -f "$FILE" ]; then
        echo "✅ MODULO${M}_CHECKLIST.md"
    else
        echo "❌ FALTANDO: MODULO${M}_CHECKLIST.md"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""

# Verificar documentação M7
M7_DOCS=(
    "MODULO7_ANALISE_ESTRATEGICA.md"
    "MODULO7_EXEMPLOS_PRATICOS.md"
    "MODULO7_PROMPT_DERIVADO.md"
    "MODULO7.5_APIS.md"
    "MODULO7.5_CHECKLIST.md"
    "MODULO7.5_TOKENS.md"
)

for DOC in "${M7_DOCS[@]}"; do
    FILE="docs/$DOC"
    if [ -f "$FILE" ]; then
        echo "✅ $DOC"
    else
        echo "❌ FALTANDO: $DOC"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""
echo "📊 Total de arquivos em docs/: $(ls -1 docs/ | wc -l)"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Validação concluída com sucesso!"
    exit 0
else
    echo "⚠️ Validação concluída com $ERRORS erro(s)"
    exit 1
fi
