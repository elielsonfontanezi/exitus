#!/bin/bash
# -*- coding: utf-8 -*-
# EXITUS RECOVERY ROLLBACK - Rollback Automático de Operações
# Arquiteto: Perplexity AI (Persona 2)
# Versão: 1.0.0
# GAP: EXITUS-RECOVERY-001

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
METADATA_DIR="$PROJECT_ROOT/backups/metadata"
LOG_DIR="$PROJECT_ROOT/logs"

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/recovery_rollback.log"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_DIR/recovery_rollback.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/recovery_rollback.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/recovery_rollback.log"
}

# Função de ajuda
show_help() {
    echo -e "${CYAN}EXITUS RECOVERY ROLLBACK v1.0.0${NC}"
    echo ""
    echo "Sistema de rollback automático para operações de recovery"
    echo ""
    echo "Uso: $0 [operação] [opções]"
    echo ""
    echo "Operações:"
    echo "  list       Listar pontos de rollback disponíveis"
    echo "  rollback   Executar rollback para um ponto específico"
    echo "  auto       Rollback automático da última operação"
    echo "  cleanup    Limpar pontos de rollback antigos"
    echo ""
    echo "Opções de rollback:"
    echo "  --to=rollback_id          Ponto de rollback específico"
    echo "  --force                   Forçar rollback sem confirmação"
    echo "  --validate                Validar pós-rollback (default: true)"
    echo ""
    echo "Exemplos:"
    echo "  $0 list"
    echo "  $0 rollback --to=rollback_20260301_143000"
    echo "  $0 auto"
    echo ""
}

# Listar pontos de rollback disponíveis
list_rollback_points() {
    echo -e "${CYAN}=== PONTOS DE ROLLBACK DISPONÍVEIS ===${NC}"
    echo ""
    
    if [[ ! -d "$BACKUP_DIR" ]]; then
        error "Diretório de backups não encontrado"
        return 1
    fi
    
    # Buscar backups de rollback
    local rollback_backups
    rollback_backups=$(find "$BACKUP_DIR" -name "*rollback*.sql*" -o -name "*prereset*.sql*" -o -name "*prebackup*.sql*" | sort -r)
    
    if [[ -z "$rollback_backups" ]]; then
        warn "Nenhum ponto de rollback encontrado"
        return 0
    fi
    
    echo -e "${BLUE}ID${NC}\t\t${BLUE}Tipo${NC}\t${BLUE}Data${NC}\t\t${BLUE}Tamanho${NC}\t${BLUE}Status${NC}"
    echo "────────────────────────────────────────────────────────────────"
    
    while IFS= read -r backup_file; do
        local basename_file
        basename_file=$(basename "$backup_file")
        
        # Extrair informações
        local rollback_id
        rollback_id=$(basename "$backup_file" .sql | sed 's/\.(gz)$//')
        
        local rollback_type="unknown"
        if [[ "$basename_file" == *"rollback"* ]]; then
            rollback_type="rollback"
        elif [[ "$basename_file" == *"prereset"* ]]; then
            rollback_type="prereset"
        elif [[ "$basename_file" == *"prebackup"* ]]; then
            rollback_type="prebackup"
        fi
        
        local file_date
        file_date=$(stat -c %y "$backup_file" | cut -d' ' -f1 | cut -d'-' -f2,3)
        
        local file_size
        file_size=$(du -h "$backup_file" | cut -f1)
        
        local status="available"
        if [[ -f "$METADATA_DIR/${rollback_id}.json" ]]; then
            status="validated"
        fi
        
        echo -e "${GREEN}$rollback_id${NC}\t${YELLOW}$rollback_type${NC}\t$file_date\t$file_size\t${GREEN}$status${NC}"
    done <<< "$rollback_backups"
    
    echo ""
}

# Validar ponto de rollback
validate_rollback_point() {
    local rollback_id="$1"
    local backup_file="$BACKUP_DIR/${rollback_id}.sql"
    
    # Verificar se arquivo existe
    if [[ ! -f "$backup_file" ]]; then
        # Tentar com .gz
        backup_file="$BACKUP_DIR/${rollback_id}.sql.gz"
        if [[ ! -f "$backup_file" ]]; then
            error "Arquivo de rollback não encontrado: $rollback_id"
            return 1
        fi
    fi
    
    # Verificar metadados
    local metadata_file="$METADATA_DIR/${rollback_id}.json"
    if [[ -f "$metadata_file" ]]; then
        local expected_checksum
        expected_checksum=$(jq -r '.checksum' "$metadata_file" 2>/dev/null | sed 's/sh256://' || echo "")
        
        if [[ -n "$expected_checksum" ]]; then
            # Extrair arquivo se for .gz
            local temp_file="/tmp/rollback_validate_$(date +%s).sql"
            if [[ "$backup_file" == *.gz ]]; then
                gunzip -c "$backup_file" > "$temp_file"
                backup_file="$temp_file"
            fi
            
            # Validar checksum
            local actual_checksum
            actual_checksum=$(sha256sum "$backup_file" | awk '{print $1}')
            
            if [[ "$actual_checksum" != "$expected_checksum" ]]; then
                error "Checksum inválido para rollback point: $rollback_id"
                [[ -f "$temp_file" ]] && rm -f "$temp_file"
                return 1
            fi
            
            [[ -f "$temp_file" ]] && rm -f "$temp_file"
            log "Rollback point validado: $rollback_id"
        fi
    else
        warn "Metadados não encontrados para: $rollback_id"
    fi
    
    return 0
}

# Executar rollback
execute_rollback() {
    local rollback_id="$1"
    local validate="${2:-true}"
    local force="${3:-false}"
    
    log "Iniciando rollback para: $rollback_id"
    
    # Validar ponto de rollback
    validate_rollback_point "$rollback_id" || return 1
    
    # Confirmação (a menos que seja forçado)
    if [[ "$force" != "true" ]]; then
        echo -e "${YELLOW}⚠️  ATENÇÃO: Esta operação irá reverter o sistema para o estado do ponto de rollback.${NC}"
        echo -e "${YELLOW}⚠️  Todos os dados alterados após este ponto serão PERDIDOS.${NC}"
        echo ""
        echo -n "Confirmar rollback para '$rollback_id'? (s/N): "
        read -r confirm
        
        if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
            log "Rollback cancelado pelo usuário"
            return 0
        fi
    fi
    
    # Preparar arquivo de backup
    local backup_file="$BACKUP_DIR/${rollback_id}.sql"
    local temp_file="/tmp/rollback_$(date +%s).sql"
    
    # Extrair se for .gz
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -c "$backup_file" > "$temp_file"
        backup_file="$temp_file"
    else
        cp "$backup_file" "$temp_file"
    fi
    
    # Criar backup pré-rollback
    log "Criando backup pré-rollback..."
    local prerollback_id="prerollback_$(date +%Y%m%d_%H%M%S)"
    "$SCRIPT_DIR/recovery_manager.sh" backup --no-compress
    mv "$BACKUP_DIR/backup_full_"*".sql" "$BACKUP_DIR/${prerollback_id}.sql"
    
    # Parar containers de aplicação
    log "Parando containers de aplicação..."
    podman stop exitus-backend 2>/dev/null || true
    podman stop exitus-frontend 2>/dev/null || true
    
    # Executar rollback do banco
    log "Restaurando banco de dados..."
    if ! podman exec -i exitus-db psql -U exitus -d exitusdb < "$backup_file"; then
        error "Falha ao restaurar banco de dados"
        
        # Tentar recuperar com backup pré-rollback
        warn "Tentando recuperar com backup pré-rollback..."
        if [[ -f "$BACKUP_DIR/${prerollback_id}.sql" ]]; then
            podman exec -i exitus-db psql -U exitus -d exitusdb < "$BACKUP_DIR/${prerollback_id}.sql"
            log "Sistema recuperado com backup pré-rollback"
        fi
        
        rm -f "$temp_file"
        return 1
    fi
    
    # Reiniciar containers
    log "Reiniciando containers de aplicação..."
    podman start exitus-backend
    podman start exitus-frontend
    
    # Aguardar inicialização
    sleep 10
    
    # Validar pós-rollback
    if [[ "$validate" == "true" ]]; then
        log "Validando sistema pós-rollback..."
        if "$SCRIPT_DIR/validate_recovery.sh" full; then
            log "✅ Rollback validado com sucesso"
        else
            warn "⚠️ Rollback executado mas validação falhou"
        fi
    fi
    
    # Limpar arquivo temporário
    rm -f "$temp_file"
    
    # Registrar rollback
    log "Rollback concluído: $rollback_id"
    
    # Gerar metadados do rollback
    local rollback_metadata="$METADATA_DIR/rollback_${rollback_id}_$(date +%Y%m%d_%H%M%S).json"
    cat > "$rollback_metadata" << EOF
{
  "rollback_id": "rollback_${rollback_id}_$(date +%Y%m%d_%H%M%S)",
  "source_rollback": "$rollback_id",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "prerollback_backup": "$prerollback_id",
  "status": "completed",
  "validated": $validate,
  "executed_by": "rollback_recovery.sh"
}
EOF
    
    return 0
}

# Rollback automático (última operação)
auto_rollback() {
    log "Iniciando rollback automático da última operação..."
    
    # Buscar último ponto de rollback
    local last_rollback
    last_rollback=$(find "$BACKUP_DIR" -name "*rollback*.sql*" -o -name "*prereset*.sql*" -o -name "*prebackup*.sql*" | sort -r | head -1)
    
    if [[ -z "$last_rollback" ]]; then
        error "Nenhum ponto de rollback encontrado para rollback automático"
        return 1
    fi
    
    local rollback_id
    rollback_id=$(basename "$last_rollback" .sql | sed 's/\.(gz)$//')
    
    info "Rollback automático para: $rollback_id"
    execute_rollback "$rollback_id" "true" "true"
}

# Limpar pontos de rollback antigos
cleanup_rollback_points() {
    local days_to_keep="${1:-7}"
    
    log "Limpando pontos de rollback com mais de $days_to_keep dias..."
    
    local cutoff_date
    cutoff_date=$(date -d "$days_to_keep days ago" +%Y-%m-%d)
    
    local removed_count=0
    
    while IFS= read -r backup_file; do
        local file_date
        file_date=$(stat -c %y "$backup_file" | cut -d' ' -f1)
        
        if [[ "$file_date" < "$cutoff_date" ]]; then
            local basename_file
            basename_file=$(basename "$backup_file")
            local rollback_id
            rollback_id=$(basename "$backup_file" .sql | sed 's/\.(gz)$//')
            
            log "Removendo ponto de rollback antigo: $rollback_id"
            rm -f "$backup_file"
            rm -f "$METADATA_DIR/${rollback_id}.json"
            ((removed_count++))
        fi
    done <<< "$(find "$BACKUP_DIR" -name "*rollback*.sql*" -o -name "*prereset*.sql*" -o -name "*prebackup*.sql*")"
    
    log "Limpeza concluída. $removed_count pontos de rollback removidos"
}

# Função principal
main() {
    local command="${1:-help}"
    
    case $command in
        "list")
            list_rollback_points
            ;;
            
        "rollback")
            local rollback_id=""
            local validate="true"
            local force="false"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --to=*)
                        rollback_id="${1#*=}"
                        ;;
                    --no-validate)
                        validate="false"
                        ;;
                    --force)
                        force="true"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            if [[ -z "$rollback_id" ]]; then
                error "Especifique --to=rollback_id ou use 'list' para ver disponíveis"
                exit 1
            fi
            
            execute_rollback "$rollback_id" "$validate" "$force"
            ;;
            
        "auto")
            auto_rollback
            ;;
            
        "cleanup")
            local days_to_keep="7"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --days=*)
                        days_to_keep="${1#*=}"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            cleanup_rollback_points "$days_to_keep"
            ;;
            
        "help"|"-h"|"--help")
            show_help
            ;;
            
        *)
            error "Comando desconhecido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
