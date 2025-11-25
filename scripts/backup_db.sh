#!/bin/bash
# Backup do banco de dados PostgreSQL

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Criando backup do banco de dados..."

podman exec exitus-db pg_dump -U exitus exitusdb > "$BACKUP_DIR/exitusdb_$TIMESTAMP.sql"

echo "Backup criado: $BACKUP_DIR/exitusdb_$TIMESTAMP.sql"
