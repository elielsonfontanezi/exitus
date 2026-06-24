#!/bin/bash
# =============================================================================
# EXITUS-TESTDB-001 — Recriação automatizada do banco de teste
#
# Uso:
#   ./scripts/create_test_db.sh              # recria exitusdb_test + seed test_e2e (padrão)
#   ./scripts/create_test_db.sh --dry-run    # apenas valida, não executa
#   ./scripts/create_test_db.sh --skip-seed  # recria sem carregar seed
#
# O que faz:
#   1. Verifica que os containers exitus-db e exitus-backend estão rodando
#   2. Drop do banco exitusdb_test (se existir)
#   3. Criação do banco exitusdb_test
#   4. Aplicação do schema via pg_dump --schema-only do exitusdb (paridade total)
#   5. Seed automático test_e2e (salvo com --skip-seed)
#   6. Verificação de paridade via check_db_parity.sh
#
# Idempotente: seguro para executar múltiplas vezes.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
DB_CONTAINER="exitus-db"
BACKEND_CONTAINER="exitus-backend"
TEST_DB="exitusdb_test"
DB_USER="exitus"
DRY_RUN=false
SKIP_SEED=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Parse de argumentos
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case $arg in
        --dry-run)   DRY_RUN=true ;;
        --skip-seed) SKIP_SEED=true ;;
        *) echo "Uso: $0 [--dry-run] [--skip-seed]"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[$(date '+%H:%M:%S')] $*"; }
ok()   { echo "[$(date '+%H:%M:%S')] ✅ $*"; }
err()  { echo "[$(date '+%H:%M:%S')] ❌ $*" >&2; exit 1; }
warn() { echo "[$(date '+%H:%M:%S')] ⚠️  $*"; }

# ---------------------------------------------------------------------------
# 1. Verificar containers
# ---------------------------------------------------------------------------
log "Verificando containers..."

if ! podman inspect "$DB_CONTAINER" --format '{{.State.Status}}' 2>/dev/null | grep -q "running"; then
    err "Container '$DB_CONTAINER' não está rodando. Execute: ./scripts/start_exitus.sh"
fi
ok "Container '$DB_CONTAINER' está rodando"

if ! podman inspect "$BACKEND_CONTAINER" --format '{{.State.Status}}' 2>/dev/null | grep -q "running"; then
    err "Container '$BACKEND_CONTAINER' não está rodando. Execute: ./scripts/start_exitus.sh"
fi
ok "Container '$BACKEND_CONTAINER' está rodando"

if $DRY_RUN; then
    warn "Modo dry-run — nenhuma alteração será feita"
    ok "Validação concluída"
    exit 0
fi

# ---------------------------------------------------------------------------
# 2. Drop do banco de teste (forçar desconexão de sessões ativas)
# ---------------------------------------------------------------------------
log "Encerrando conexões ativas em '$TEST_DB'..."
podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$TEST_DB' AND pid <> pg_backend_pid();" \
    > /dev/null 2>&1 || true

log "Removendo banco '$TEST_DB' (se existir)..."
podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c \
    "DROP DATABASE IF EXISTS $TEST_DB;" \
    > /dev/null
ok "Banco '$TEST_DB' removido"

# ---------------------------------------------------------------------------
# 3. Criar banco de teste
# ---------------------------------------------------------------------------
log "Criando banco '$TEST_DB'..."
podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c \
    "CREATE DATABASE $TEST_DB OWNER $DB_USER ENCODING 'UTF8' LC_COLLATE 'en_US.utf8' LC_CTYPE 'en_US.utf8' TEMPLATE template0;" \
    > /dev/null
ok "Banco '$TEST_DB' criado"

# ---------------------------------------------------------------------------
# 4. Aplicar schema via pg_dump --schema-only do exitusdb (paridade total)
# ---------------------------------------------------------------------------
log "Exportando schema de 'exitusdb' via pg_dump..."
podman exec "$DB_CONTAINER" pg_dump \
    -U "$DB_USER" \
    --schema-only \
    --no-owner \
    --no-privileges \
    exitusdb | \
podman exec -i "$DB_CONTAINER" psql \
    -U "$DB_USER" \
    -d "$TEST_DB" \
    -v ON_ERROR_STOP=1 \
    > /dev/null
ok "Schema aplicado"

# Contar tabelas criadas
TABLE_COUNT=$(podman exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" \
    | tr -d ' ')
log "  $TABLE_COUNT tabelas criadas no banco de teste"

# ---------------------------------------------------------------------------
# 5. Resumo
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 5. Seed automático (test_e2e) — salvo se --skip-seed
# ---------------------------------------------------------------------------
if ! $SKIP_SEED; then
    log "Carregando seed 'test_e2e' no banco de teste..."
    if podman exec -e TESTING=true "$BACKEND_CONTAINER" \
        python load_scenario.py test_e2e > /dev/null 2>&1; then
        ok "Seed 'test_e2e' carregado (3 usuários, 7 ativos, 4 transações)"
    else
        warn "Seed falhou — banco de teste está vazio. Execute manualmente:"
        warn "  podman exec -e TESTING=true $BACKEND_CONTAINER python load_scenario.py test_e2e"
    fi
else
    warn "--skip-seed ativo — banco de teste criado sem dados"
fi

# ---------------------------------------------------------------------------
# 6. Verificação de paridade de schema
# ---------------------------------------------------------------------------
log "Verificando paridade entre exitusdb e $TEST_DB..."
bash "$SCRIPT_DIR/check_db_parity.sh" || true

# ---------------------------------------------------------------------------
# Resumo
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo "  Banco de teste recriado com sucesso!"
echo "  Banco:    $TEST_DB"
echo "  Usuário:  $DB_USER"
if ! $SKIP_SEED; then
echo "  Seed:     test_e2e carregado"
fi
echo "  Próximo:  podman exec $BACKEND_CONTAINER python -m pytest tests/ -q --no-cov"
echo "============================================================"
