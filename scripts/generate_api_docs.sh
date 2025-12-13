#!/bin/bash
# Script de geração automática de documentação de API
# Sistema Exitus - 13/12/2025

set -e

OUTPUT="docs/API_REFERENCE_COMPLETE.md"
TEMP_FILE="/tmp/api_routes.tmp"

echo "🔍 Extraindo rotas dos blueprints..."

# Verificar se diretório existe
if [ ! -d "backend/app/blueprints" ]; then
    echo "❌ Erro: Diretório backend/app/blueprints não encontrado"
    exit 1
fi

# Extrair rotas
> $TEMP_FILE  # Limpar arquivo temp

for blueprint in backend/app/blueprints/*.py; do
    if [ -f "$blueprint" ]; then
        module=$(basename $blueprint .py | sed 's/_blueprint//')
        echo "  Processando: $module"

        # Extrair rotas (formato: @bp.route('/path', methods=['GET']))
        grep -E "@.*\.route\(" "$blueprint" | \
            sed "s/@.*\.route('\([^']*\)'.*methods=\[\([^]]*\)\].*/[$module] \2 \1/" >> $TEMP_FILE || true
    fi
done

# Contar rotas encontradas
TOTAL_ROUTES=$(wc -l < $TEMP_FILE)
echo "✅ Total de rotas encontradas: $TOTAL_ROUTES"

# Gerar documentação
cat > "$OUTPUT" << 'HEADER'
# 📡 API REFERENCE COMPLETA - SISTEMA EXITUS

**ATENÇÃO:** Este arquivo é gerado automaticamente pelo script \`generate_api_docs.sh\`.  
**Não editar manualmente.** Rode o script para atualizar.

**Base URL:** \`http://localhost:5000/api\`  
**Gerado em:** $(date)

---

## 📋 ROTAS DISPONÍVEIS

HEADER

# Adicionar rotas extraídas
sort $TEMP_FILE >> "$OUTPUT"

# Cleanup
rm $TEMP_FILE

echo ""
echo "✅ Documentação gerada em: $OUTPUT"
echo "📊 Total de rotas documentadas: $TOTAL_ROUTES"
echo ""
echo "Para visualizar:"
echo "  cat $OUTPUT"
echo ""
echo "Para mover para docs/:"
echo "  mv API_REFERENCE_COMPLETE.md docs/"
