#!/bin/bash

# Atualiza docs/EXITUS_DB_STRUCTURE.txt com a estrutura atual do banco
# Sempre sobrescreve o arquivo destino — nunca gera cópia com timestamp
# Uso: ./scripts/update_db_structure.sh
# Autor: Sistema Exitus

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_FILE="$PROJECT_ROOT/docs/EXITUS_DB_STRUCTURE.txt"

DB_CONTAINER="exitus-db"
DB_NAME="exitusdb"
DB_USER="exitus"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  EXITUS - Atualização de EXITUS_DB_STRUCTURE  ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if ! podman ps | grep -q "$DB_CONTAINER"; then
    echo -e "${YELLOW}AVISO: Container $DB_CONTAINER não está rodando!${NC}"
    echo "Execute: podman start $DB_CONTAINER"
    exit 1
fi

echo -e "${GREEN}✓ Container $DB_CONTAINER está online${NC}"
echo -e "Destino: ${YELLOW}$OUTPUT_FILE${NC}"
echo ""

# Sobrescreve o arquivo destino
cat > "$OUTPUT_FILE" << EOF
================================================================================
EXITUS - ESTRUTURA DO BANCO DE DADOS
================================================================================
Database: $DB_NAME
Gerado em: $(date '+%Y-%m-%d %H:%M:%S')
================================================================================

EOF

echo "Coletando lista de tabelas..."
podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOSQL' >> "$OUTPUT_FILE"
\echo '================================================================================'
\echo 'TABELAS DO BANCO EXITUS'
\echo '================================================================================'
\echo ''

SELECT 
    schemaname as "Schema",
    tablename as "Tabela",
    tableowner as "Owner"
FROM pg_catalog.pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''
EOSQL

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}ERRO ao conectar ao banco de dados!${NC}"
    exit 1
fi

echo "Coletando estrutura detalhada das tabelas..."
podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOSQL' >> "$OUTPUT_FILE"

\echo '================================================================================'
\echo 'ESTRUTURA DETALHADA DAS TABELAS'
\echo '================================================================================'
\echo ''
EOSQL

echo "Coletando detalhes de colunas, PKs e FKs..."
TABLES=$(podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY tablename;")

for table in $TABLES; do
    table=$(echo "$table" | xargs)
    echo "  - Processando tabela: $table"

    cat >> "$OUTPUT_FILE" << EOF

################################################################################
TABELA: $table
################################################################################

EOF

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"
\d+ $table

EOSQL

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"

-- Detalhes das Colunas
SELECT 
    ordinal_position as "Pos",
    column_name as "Coluna",
    data_type as "Tipo",
    CASE 
        WHEN character_maximum_length IS NOT NULL 
        THEN '(' || character_maximum_length || ')'
        ELSE ''
    END as "Tamanho",
    is_nullable as "Null?",
    column_default as "Default"
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = '$table'
ORDER BY ordinal_position;

EOSQL

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"

-- Foreign Keys (FKs)
\echo ''
\echo 'Foreign Keys:'
SELECT
    tc.constraint_name as "Nome FK",
    kcu.column_name as "Coluna",
    ccu.table_name AS "Tabela Referenciada",
    ccu.column_name AS "Coluna Referenciada"
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
    AND tc.table_name = '$table';

EOSQL

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"

-- Primary Keys (PKs)
\echo ''
\echo 'Primary Keys:'
SELECT
    tc.constraint_name as "Nome PK",
    kcu.column_name as "Coluna"
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY' 
    AND tc.table_schema = 'public'
    AND tc.table_name = '$table';

EOSQL

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"

-- Unique Constraints
\echo ''
\echo 'Unique Constraints:'
SELECT
    tc.constraint_name as "Nome Constraint",
    kcu.column_name as "Coluna"
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE' 
    AND tc.table_schema = 'public'
    AND tc.table_name = '$table';

EOSQL

    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"

-- Índices
\echo ''
\echo 'Índices:'
SELECT
    indexname as "Nome do Índice",
    indexdef as "Definição"
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename = '$table';

\echo ''
\echo '________________________________________________________________________________'
\echo ''

EOSQL

done

cat >> "$OUTPUT_FILE" << EOF

================================================================================
RESUMO GERAL
================================================================================

EOF

podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOSQL' >> "$OUTPUT_FILE"

-- Contagem de tabelas
\echo 'Total de Tabelas:'
SELECT COUNT(*) as "Total" 
FROM pg_catalog.pg_tables 
WHERE schemaname = 'public';

\echo ''
\echo 'Total de Colunas por Tabela:'
SELECT 
    table_name as "Tabela",
    COUNT(*) as "Num Colunas"
FROM information_schema.columns
WHERE table_schema = 'public'
GROUP BY table_name
ORDER BY table_name;

\echo ''
\echo 'Total de Foreign Keys por Tabela:'
SELECT
    tc.table_name as "Tabela",
    COUNT(*) as "Num FKs"
FROM information_schema.table_constraints AS tc 
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
GROUP BY tc.table_name
ORDER BY tc.table_name;

EOSQL

cat >> "$OUTPUT_FILE" << EOF

================================================================================
ENUMS DO BANCO
================================================================================

EOF

echo "Coletando valores dos ENUMs..."
podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOSQL' >> "$OUTPUT_FILE"

SELECT
    t.typname AS "Enum",
    string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) AS "Valores"
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE n.nspname = 'public'
GROUP BY t.typname
ORDER BY t.typname;

EOSQL

cat >> "$OUTPUT_FILE" << EOF

================================================================================
FIM DA DOCUMENTAÇÃO
================================================================================
EOF

echo ""
echo -e "${GREEN}✓ docs/EXITUS_DB_STRUCTURE.txt atualizado com sucesso!${NC}"
echo ""
