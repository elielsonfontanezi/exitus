#!/bin/bash

# =====================================================
# EXITUS - POPULAR BANCO COM SEEDS INICIAIS
# =====================================================
# Arquivo: scripts/populate_seeds.sh
# =====================================================

set -e  # Para em caso de erro

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Iniciando população de seeds do Exitus..."
echo "📁 Projeto: $PROJECT_ROOT"
echo

# =====================================================
# 1. VERIFICAR CONTAINERS ONLINE (CORRIGIDO)
# =====================================================
echo "🔍 [1/3] Verificando containers..."

# Método mais robusto: usar podman inspect
if ! podman inspect exitus-backend >/dev/null 2>&1; then
    echo "❌ ERRO: Container 'exitus-backend' não existe"
    exit 1
fi

if ! podman inspect exitus-db >/dev/null 2>&1; then
    echo "❌ ERRO: Container 'exitus-db' não existe"
    exit 1
fi

BACKEND_STATUS=$(podman inspect exitus-backend --format "{{.State.Status}}" 2>/dev/null)
DB_STATUS=$(podman inspect exitus-db --format "{{.State.Status}}" 2>/dev/null)

if [[ "$BACKEND_STATUS" != "running" ]]; then
    echo "❌ ERRO: Container 'exitus-backend' não está rodando ($BACKEND_STATUS)"
    exit 1
fi

if [[ "$DB_STATUS" != "running" ]]; then
    echo "❌ ERRO: Container 'exitus-db' não está rodando ($DB_STATUS)"
    exit 1
fi

echo "✅ Containers OK: backend($BACKEND_STATUS) | db($DB_STATUS)"
echo

# =====================================================
# 2. EXECUTAR RUN_ALL_SEEDS (INTERATIVO)
# =====================================================
echo "🌱 [2/3] Executando seeds interativos..."
echo "   Digite 's' para continuar e 'n' quando solicitado para seeds já existentes."
echo

podman exec -it exitus-backend python -m app.seeds.run_all_seeds

echo
echo "✅ Seeds executados com sucesso!"
echo

# =====================================================
# 3. LISTAR RESUMO DAS TABELAS (2 FORMAS)
# =====================================================
echo "📊 [3/3] Resumo das tabelas populadas..."

echo "=== MÉTODO 1: Query Direta (Tabelas Principais) ==="
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 
  'usuario' as tabela, COUNT(*) as registros FROM usuario
UNION ALL
SELECT 'ativo', COUNT(*) FROM ativo
UNION ALL
SELECT 'regra_fiscal', COUNT(*) FROM regra_fiscal
UNION ALL
SELECT 'feriado_mercado', COUNT(*) FROM feriado_mercado
UNION ALL
SELECT 'fonte_dados', COUNT(*) FROM fonte_dados
ORDER BY tabela;"

echo
echo "=== MÉTODO 2: Todas as Tabelas (Automático) ==="
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT 
  t.table_name as tabela,
  COALESCE(c.reltuples::bigint, 0) as estimativa_registros
FROM information_schema.tables t
LEFT JOIN pg_class c ON c.relname = t.table_name
LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE t.table_schema = 'public' 
AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name;"

echo
echo "🎉 População de seeds concluída com sucesso!"
