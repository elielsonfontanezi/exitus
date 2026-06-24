#!/bin/bash
# =============================================================================
# check_db_parity.sh — Valida paridade de schema entre exitusdb e exitusdb_test
#
# Uso:
#   ./scripts/check_db_parity.sh           # compara e reporta divergências
#   ./scripts/check_db_parity.sh --strict  # sai com erro se houver divergência
#
# O que verifica:
#   1. Contagem de tabelas
#   2. Valores de todos os ENUMs
#   3. Contagem de colunas por tabela
#
# Chamado automaticamente pelo create_test_db.sh após recriar o banco.
# =============================================================================

set -uo pipefail

DB_CONTAINER="exitus-db"
DB_USER="exitus"
PROD_DB="exitusdb"
TEST_DB="exitusdb_test"
STRICT=false
ERRORS=0

for arg in "$@"; do
    case $arg in
        --strict) STRICT=true ;;
        *) echo "Uso: $0 [--strict]"; exit 1 ;;
    esac
done

ok()   { echo "  ✅ $*"; }
fail() { echo "  ❌ $*"; ERRORS=$((ERRORS + 1)); }
info() { echo "  ℹ️  $*"; }

echo ""
echo "============================================================"
echo "  EXITUS — Verificação de Paridade de Schema"
echo "  Produção: $PROD_DB  |  Testes: $TEST_DB"
echo "============================================================"
echo ""

# ---------------------------------------------------------------------------
# 1. Tabelas
# ---------------------------------------------------------------------------
echo "▶ Tabelas..."

PROD_TABLES=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$PROD_DB" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" \
    | tr -d ' \n')

TEST_TABLES=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" \
    | tr -d ' \n')

if [ "$PROD_TABLES" = "$TEST_TABLES" ]; then
    ok "Tabelas: $PROD_TABLES / $TEST_TABLES (idêntico)"
else
    fail "Tabelas divergem: $PROD_DB=$PROD_TABLES  $TEST_DB=$TEST_TABLES"
fi

# ---------------------------------------------------------------------------
# 2. ENUMs — comparar valores de cada enum
# ---------------------------------------------------------------------------
echo ""
echo "▶ ENUMs..."

ENUMS=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$PROD_DB" -t -c \
    "SELECT typname FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='public' AND t.typtype='e' ORDER BY typname;" \
    | tr -d ' ' | grep -v '^$')

ENUM_ERRORS=0
for enum in $ENUMS; do
    PROD_VALS=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$PROD_DB" -t -c \
        "SELECT string_agg(enumlabel, ',' ORDER BY enumsortorder) FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid WHERE t.typname='$enum';" \
        | tr -d ' \n')

    TEST_VALS=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB" -t -c \
        "SELECT string_agg(enumlabel, ',' ORDER BY enumsortorder) FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid WHERE t.typname='$enum';" \
        | tr -d ' \n')

    if [ "$PROD_VALS" = "$TEST_VALS" ]; then
        ok "ENUM $enum: $(echo "$PROD_VALS" | tr ',' ' ' | wc -w | tr -d ' ') valores (idêntico)"
    else
        fail "ENUM $enum diverge:"
        info "  $PROD_DB: $PROD_VALS"
        info "  $TEST_DB: $TEST_VALS"
        ENUM_ERRORS=$((ENUM_ERRORS + 1))
    fi
done

# ---------------------------------------------------------------------------
# 3. Colunas por tabela
# ---------------------------------------------------------------------------
echo ""
echo "▶ Colunas por tabela..."

PROD_COLS=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$PROD_DB" -t -c \
    "SELECT table_name || '=' || COUNT(*) FROM information_schema.columns WHERE table_schema='public' GROUP BY table_name ORDER BY table_name;" \
    | tr -d ' ' | grep -v '^$' | sort)

TEST_COLS=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB" -t -c \
    "SELECT table_name || '=' || COUNT(*) FROM information_schema.columns WHERE table_schema='public' GROUP BY table_name ORDER BY table_name;" \
    | tr -d ' ' | grep -v '^$' | sort)

COL_DIFF=$(diff <(echo "$PROD_COLS") <(echo "$TEST_COLS") || true)

if [ -z "$COL_DIFF" ]; then
    ok "Colunas: todas as tabelas idênticas"
else
    fail "Colunas divergem entre os bancos:"
    echo "$COL_DIFF" | grep '^[<>]' | while read -r line; do
        info "  $line"
    done
fi

# ---------------------------------------------------------------------------
# Resultado final
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
if [ "$ERRORS" -eq 0 ]; then
    echo "  ✅ PARIDADE OK — schema idêntico entre $PROD_DB e $TEST_DB"
    echo "============================================================"
    echo ""
    exit 0
else
    echo "  ❌ $ERRORS DIVERGÊNCIA(S) encontrada(s)"
    echo "  Execute: ./scripts/create_test_db.sh para sincronizar"
    echo "============================================================"
    echo ""
    if $STRICT; then
        exit 1
    else
        exit 0
    fi
fi
