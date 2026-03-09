#!/bin/bash
# Backup do banco de dados PostgreSQL
# Uso: ./scripts/backup_db.sh [--compress] [--keep=N]

set -e

# Configurações
BACKUP_DIR="./backups"
COMPRESS=false
KEEP_COUNT=7  # Manter últimos 7 backups por padrão

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --compress)
            COMPRESS=true
            shift
            ;;
        --keep=*)
            KEEP_COUNT="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Uso: $0 [--compress] [--keep=N]"
            echo "  --compress  Comprime backup com gzip"
            echo "  --keep=N    Mantém últimos N backups (padrão: 7)"
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            exit 1
            ;;
    esac
done

# Criar diretório de backups
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/exitusdb_$TIMESTAMP.sql"

# Verificar se container está rodando
if ! podman ps --format 'table {{.Names}}' | grep -q "^exitus-db$"; then
    echo "❌ Container exitus-db não está rodando"
    exit 1
fi

echo "🔄 Criando backup do banco de dados..."

# Criar backup
if podman exec exitus-db pg_dump -U exitus exitusdb > "$BACKUP_FILE"; then
    echo "✅ Backup criado: $BACKUP_FILE"
    
    # Comprimir se solicitado
    if [[ "$COMPRESS" == "true" ]]; then
        echo "🗜️  Comprimindo backup..."
        gzip "$BACKUP_FILE"
        BACKUP_FILE="${BACKUP_FILE}.gz"
        echo "✅ Backup comprimido: $BACKUP_FILE"
    fi
    
    # Verificar tamanho do arquivo
    BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
    if [[ $BACKUP_SIZE -gt 0 ]]; then
        echo "📊 Tamanho: $((BACKUP_SIZE / 1024)) KB"
    else
        echo "⚠️  Aviso: Backup parece estar vazio"
    fi
    
    # Limpar backups antigos
    echo "🧹 Limpando backups antigos (mantendo últimos $KEEP_COUNT)..."
    cd "$BACKUP_DIR"
    ls -t exitusdb_*.sql* 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | xargs -r rm
    echo "✅ Cleanup concluído"
    
else
    echo "❌ Falha ao criar backup"
    rm -f "$BACKUP_FILE" 2>/dev/null
    exit 1
fi
