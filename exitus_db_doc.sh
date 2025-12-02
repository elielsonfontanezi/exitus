#!/bin/bash

# Script para documentar estrutura completa do banco exitus-db
# Gera arquivo texto com todas as tabelas, colunas, PKs, FKs e constraints
# Autor: Sistema Exitus
# Data: 2025-12-02

# Configurações do ambiente
DB_CONTAINER="exitus-db"
DB_NAME="exitus"
DB_USER="exitus_user"
OUTPUT_FILE="exitus_db_structure_$(date +%Y%m%d_%H%M%S).txt"

# Cores para output (opcional, comentar se preferir sem cores)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  EXITUS - Documentação da Estrutura do Banco${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Verifica se o container está rodando
if ! podman ps | grep -q "$DB_CONTAINER"; then
    echo -e "${YELLOW}AVISO: Container $DB_CONTAINER não está rodando!${NC}"
    echo "Execute: podman start $DB_CONTAINER"
    exit 1
fi

echo -e "${GREEN}✓ Container $DB_CONTAINER está online${NC}"
echo -e "Gerando documentação em: ${YELLOW}$OUTPUT_FILE${NC}"
echo ""

# Cria o arquivo de saída com cabeçalho
cat > "$OUTPUT_FILE" << EOF
================================================================================
EXITUS - ESTRUTURA DO BANCO DE DADOS
================================================================================
Database: $DB_NAME
Gerado em: $(date '+%Y-%m-%d %H:%M:%S')
================================================================================

EOF

# SQL para listar todas as tabelas do schema public
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

# SQL para estrutura detalhada de cada tabela
echo "Coletando estrutura detalhada das tabelas..."
podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOSQL' >> "$OUTPUT_FILE"

\echo '================================================================================'
\echo 'ESTRUTURA DETALHADA DAS TABELAS'
\echo '================================================================================'
\echo ''

-- Para cada tabela, mostra estrutura completa
DO $$
DECLARE
    tbl_name text;
BEGIN
    FOR tbl_name IN 
        SELECT tablename 
        FROM pg_catalog.pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    LOOP
        RAISE NOTICE '';
        RAISE NOTICE '################################################################################';
        RAISE NOTICE 'TABELA: %', tbl_name;
        RAISE NOTICE '################################################################################';
        RAISE NOTICE '';
    END LOOP;
END $$;

EOSQL

# Para cada tabela, executa \d+ e informações adicionais
echo "Coletando detalhes de colunas, PKs e FKs..."
TABLES=$(podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY tablename;")

for table in $TABLES; do
    # Remove espaços em branco
    table=$(echo "$table" | xargs)
    
    echo "  - Processando tabela: $table"
    
    cat >> "$OUTPUT_FILE" << EOF

################################################################################
TABELA: $table
################################################################################

EOF

    # Usa \d+ para mostrar estrutura completa da tabela
    podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << EOSQL >> "$OUTPUT_FILE"
\d+ $table

EOSQL

    # Query customizada para mostrar colunas com detalhes
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

    # Query para mostrar Foreign Keys
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

    # Query para mostrar Primary Keys
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

    # Query para mostrar Unique Constraints
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

    # Query para mostrar Indexes
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

# Adiciona resumo ao final
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

# Finaliza o arquivo
cat >> "$OUTPUT_FILE" << EOF

================================================================================
FIM DA DOCUMENTAÇÃO
================================================================================
EOF

echo ""
echo -e "${GREEN}✓ Documentação gerada com sucesso!${NC}"
echo -e "${BLUE}Arquivo: ${YELLOW}$OUTPUT_FILE${NC}"
echo ""
echo -e "${BLUE}Para visualizar:${NC}"
echo -e "  cat $OUTPUT_FILE"
echo -e "  less $OUTPUT_FILE"
echo -e "  code $OUTPUT_FILE  ${BLUE}# (se estiver usando VSCode)${NC}"
echo ""
echo -e "${GREEN}Pronto para compartilhar o status do banco! 🎯${NC}"
