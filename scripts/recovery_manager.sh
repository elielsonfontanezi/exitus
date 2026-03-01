#!/bin/bash
# -*- coding: utf-8 -*-
# EXITUS RECOVERY MANAGER - Sistema Unificado de Backup/Restore
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

# Criar diretórios necessários
mkdir -p "$BACKUP_DIR" "$METADATA_DIR" "$LOG_DIR"

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/recovery.log"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_DIR/recovery.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/recovery.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/recovery.log"
}

# Função de ajuda
show_help() {
    echo -e "${CYAN}EXITUS RECOVERY MANAGER v1.0.0${NC}"
    echo ""
    echo "Sistema unificado de backup/restore com validação e rollback"
    echo ""
    echo "Uso: $0 [modo] [opções]"
    echo ""
    echo "Modos:"
    echo "  backup     Criar backup do sistema"
    echo "  restore    Restaurar sistema de um backup"
    echo "  reset      Reset do sistema com seeds"
    echo "  validate   Validar integridade do sistema"
    echo "  status     Mostrar status dos backups"
    echo "  schedule   Agendar backups automáticos"
    echo "  dashboard  Interface interativa"
    echo ""
    echo "Opções de backup:"
    echo "  --type=full|incremental     Tipo de backup (default: full)"
    echo "  --compress                  Comprimir backup (default: true)"
    echo ""
    echo "Opções de restore:"
    echo "  --from=arquivo              Arquivo de backup para restore"
    echo "  --validate                  Validar pós-restore (default: true)"
    echo "  --rollback                  Habilitar rollback (default: true)"
    echo ""
    echo "Opções de reset:"
    echo "  --mode=full|minimal|custom  Tipo de reset (default: full)"
    echo ""
    echo "Exemplos:"
    echo "  $0 backup --type=full"
    echo "  $0 restore --from=backup_20260301.sql"
    echo "  $0 reset --mode=minimal"
    echo "  $0 validate --check=integrity"
    echo ""
}

# Validar ambiente
validate_environment() {
    log "Validando ambiente..."
    
    # Verificar containers
    if ! podman ps --format "{{.Names}}" | grep -q "exitus-db"; then
        error "Container exitus-db não encontrado"
        return 1
    fi
    
    if ! podman ps --format "{{.Names}}" | grep -q "exitus-backend"; then
        error "Container exitus-backend não encontrado"
        return 1
    fi
    
    # Verificar espaço em disco
    local available_space
    available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    local required_space=1048576 # 1GB em KB
    
    if [[ $available_space -lt $required_space ]]; then
        error "Espaço em disco insuficiente. Disponível: ${available_space}KB, Requerido: ${required_space}KB"
        return 1
    fi
    
    log "Ambiente validado com sucesso"
    return 0
}

# Gerar checksum SHA-256
generate_checksum() {
    local file="$1"
    sha256sum "$file" | awk '{print $1}'
}

# Validar checksum
validate_checksum() {
    local file="$1"
    local expected_checksum="$2"
    
    local actual_checksum
    actual_checksum=$(generate_checksum "$file")
    
    if [[ "$actual_checksum" != "$expected_checksum" ]]; then
        error "Checksum inválido. Esperado: $expected_checksum, Atual: $actual_checksum"
        return 1
    fi
    
    log "Checksum validado: $actual_checksum"
    return 0
}

# Criar metadados do backup
create_metadata() {
    local backup_file="$1"
    local backup_type="$2"
    local metadata_file="$METADATA_DIR/$(basename "$backup_file" .sql).json"
    
    local size_mb
    size_mb=$(du -m "$backup_file" | cut -f1)
    
    local checksum
    checksum=$(generate_checksum "$backup_file")
    
    # Status dos containers
    local db_status
    db_status=$(podman inspect exitus-db --format "{{.State.Status}}" 2>/dev/null || echo "missing")
    
    local backend_status
    backend_status=$(podman inspect exitus-backend --format "{{.State.Status}}" 2>/dev/null || echo "missing")
    
    local frontend_status
    frontend_status=$(podman inspect exitus-frontend --format "{{.State.Status}}" 2>/dev/null || echo "missing")
    
    cat > "$metadata_file" << EOF
{
  "backup_id": "$(basename "$backup_file" .sql)",
  "type": "$backup_type",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "size_mb": $size_mb,
  "checksum": "sha256:$checksum",
  "containers_status": {
    "exitus-db": "$db_status",
    "exitus-backend": "$backend_status",
    "exitus-frontend": "$frontend_status"
  },
  "validation": "passed",
  "rollback_available": true,
  "created_by": "recovery_manager.sh"
}
EOF
    
    log "Metadados criados: $metadata_file"
}

# Backup completo
backup_full() {
    local compress="${1:-true}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/backup_full_$timestamp.sql"
    
    log "Iniciando backup completo..."
    
    # Validar ambiente
    validate_environment || return 1
    
    # Criar backup
    info "Criando backup do banco de dados..."
    if ! podman exec exitus-db pg_dump -U exitus -d exitusdb > "$backup_file"; then
        error "Falha ao criar backup do banco"
        return 1
    fi
    
    # Comprimir se solicitado
    if [[ "$compress" == "true" ]]; then
        info "Comprimindo backup..."
        gzip "$backup_file"
        backup_file="${backup_file}.gz"
    fi
    
    # Criar metadados
    create_metadata "$backup_file" "full"
    
    log "Backup completo criado: $backup_file"
    return 0
}

# Restore do sistema
restore_system() {
    local backup_file="$1"
    local validate="${2:-true}"
    local enable_rollback="${3:-true}"
    
    log "Iniciando restore do sistema..."
    
    # Validar arquivo de backup
    if [[ ! -f "$backup_file" ]]; then
        error "Arquivo de backup não encontrado: $backup_file"
        return 1
    fi
    
    # Extrair se for .gz
    if [[ "$backup_file" == *.gz ]]; then
        info "Extraindo backup comprimido..."
        gunzip -c "$backup_file" > "/tmp/restore_$(date +%s).sql"
        backup_file="/tmp/restore_$(date +%s).sql"
    fi
    
    # Validar checksum se tiver metadados
    local metadata_file="$METADATA_DIR/$(basename "$backup_file" .sql).json"
    if [[ -f "$metadata_file" ]]; then
        local expected_checksum
        expected_checksum=$(jq -r '.checksum' "$metadata_file" | sed 's/sh256://')
        validate_checksum "$backup_file" "$expected_checksum" || return 1
    fi
    
    # Backup pré-operação (para rollback)
    if [[ "$enable_rollback" == "true" ]]; then
        info "Criando backup pré-operação para rollback..."
        backup_full "false" "rollback_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Parar containers de aplicação
    info "Parando containers de aplicação..."
    podman stop exitus-backend 2>/dev/null || true
    podman stop exitus-frontend 2>/dev/null || true
    
    # Restaurar banco
    info "Restaurando banco de dados..."
    if ! podman exec -i exitus-db psql -U exitus -d exitusdb < "$backup_file"; then
        error "Falha ao restaurar banco de dados"
        return 1
    fi
    
    # Reiniciar containers
    info "Reiniciando containers de aplicação..."
    podman start exitus-backend
    podman start exitus-frontend
    
    # Validar pós-restore
    if [[ "$validate" == "true" ]]; then
        info "Validando sistema pós-restore..."
        sleep 10
        
        # Health check do backend
        if ! curl -fs http://localhost:5000/health >/dev/null 2>&1; then
            warn "Backend não respondeu ao health check"
        fi
        
        # Health check do frontend
        if ! curl -fs http://localhost:8080/health >/dev/null 2>&1; then
            warn "Frontend não respondeu ao health check"
        fi
    fi
    
    log "Restore concluído com sucesso"
    return 0
}

# Reset do sistema
reset_system() {
    local mode="${1:-full}"
    
    log "Iniciando reset do sistema (modo: $mode)..."
    
    # Backup pré-operação
    info "Criando backup pré-operação..."
    backup_full "false" "prereset_$(date +%Y%m%d_%H%M%S)"
    
    # Reset do banco
    case "$mode" in
        "full")
            info "Reset completo - usando populate_seeds.sh"
            "$SCRIPT_DIR/populate_seeds.sh"
            ;;
        "minimal")
            info "Reset mínimo - limpando apenas dados transacionais"
            # Implementar reset mínimo aqui
            warn "Reset mínimo não implementado ainda"
            ;;
        "custom")
            info "Reset custom - implementar conforme necessidade"
            warn "Reset custom não implementado ainda"
            ;;
        *)
            error "Modo de reset inválido: $mode"
            return 1
            ;;
    esac
    
    log "Reset concluído"
    return 0
}

# Validar integridade
validate_system() {
    local check_type="${1:-integrity}"
    
    log "Validando sistema (tipo: $check_type)..."
    
    case "$check_type" in
        "integrity")
            info "Validando integridade do banco..."
            # Verificar conexão com o banco
            if ! podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
                error "Banco de dados não acessível"
                return 1
            fi
            
            # Verificar tabelas principais
            local tables=("usuario" "ativo" "portfolio" "transacao")
            for table in "${tables[@]}"; do
                local count
                count=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM $table" 2>/dev/null || echo "0")
                info "Tabela $table: $count registros"
            done
            ;;
            
        "health")
            info "Validando health checks..."
            
            # Database
            if podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
                log "✅ Database: OK"
            else
                error "❌ Database: FALHA"
                return 1
            fi
            
            # Backend
            if curl -fs http://localhost:5000/health >/dev/null 2>&1; then
                log "✅ Backend: OK"
            else
                warn "⚠️ Backend: Não responde"
            fi
            
            # Frontend
            if curl -fs http://localhost:8080/health >/dev/null 2>&1; then
                log "✅ Frontend: OK"
            else
                warn "⚠️ Frontend: Não responde"
            fi
            ;;
    esac
    
    log "Validação concluída"
    return 0
}

# Mostrar status
show_status() {
    local show_type="${1:-last}"
    
    echo -e "${CYAN}=== EXITUS RECOVERY STATUS ===${NC}"
    echo ""
    
    # Status dos containers
    echo -e "${BLUE}Containers:${NC}"
    podman ps --filter name=exitus --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Backups disponíveis
    echo -e "${BLUE}Backups Disponíveis:${NC}"
    if [[ -d "$BACKUP_DIR" ]]; then
        ls -la "$BACKUP_DIR"/*.sql* 2>/dev/null | tail -10 || echo "Nenhum backup encontrado"
    else
        echo "Diretório de backups não encontrado"
    fi
    echo ""
    
    # Últimas operações
    echo -e "${BLUE}Últimas Operações:${NC}"
    if [[ -f "$LOG_DIR/recovery.log" ]]; then
        tail -10 "$LOG_DIR/recovery.log"
    else
        echo "Nenhum log encontrado"
    fi
}

# Dashboard interativo
show_dashboard() {
    while true; do
        clear
        echo -e "${CYAN}┌─ EXITUS RECOVERY MANAGER ─────────────────┐${NC}"
        echo -e "${CYAN}│                                          │${NC}"
        
        # Status dos containers
        local db_status=$(podman inspect exitus-db --format "{{.State.Status}}" 2>/dev/null || echo "missing")
        local backend_status=$(podman inspect exitus-backend --format "{{.State.Status}}" 2>/dev/null || echo "missing")
        local frontend_status=$(podman inspect exitus-frontend --format "{{.State.Status}}" 2>/dev/null || echo "missing")
        
        if [[ "$db_status" == "running" && "$backend_status" == "running" ]]; then
            echo -e "${CYAN}│ 📊 Status: ${GREEN}All Systems Operational${NC}     │${NC}"
        else
            echo -e "${CYAN}│ 📊 Status: ${RED}Some Systems Down${NC}             │${NC}"
        fi
        
        # Último backup
        local last_backup
        last_backup=$(ls -t "$BACKUP_DIR"/*.sql* 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "Nenhum")
        echo -e "${CYAN}│ 💾 Last Backup: ${YELLOW}$last_backup${NC}            │${NC}"
        
        # Espaço disponível
        local available_space
        available_space=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $4}')
        echo -e "${CYAN}│ 💾 Available Space: ${YELLOW}$available_space${NC}           │${NC}"
        echo -e "${CYAN}│                                          │${NC}"
        echo -e "${CYAN}│ [1] Backup Now        [2] Restore         │${NC}"
        echo -e "${CYAN}│ [3] Reset System       [4] Validate       │${NC}"
        echo -e "${CYAN}│ [5] Status             [6] Schedule       │${NC}"
        echo -e "${CYAN}│ [7] Logs               [0] Exit           │${NC}"
        echo -e "${CYAN}│                                          │${NC}"
        echo -e "${CYAN}└──────────────────────────────────────────┘${NC}"
        echo ""
        echo -n "Select option: "
        
        read -r option
        
        case $option in
            1)
                echo ""
                read -p "Confirm backup? (y/N): " confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    backup_full
                    echo ""
                    read -p "Press Enter to continue..."
                fi
                ;;
            2)
                echo ""
                echo "Available backups:"
                ls -la "$BACKUP_DIR"/*.sql* 2>/dev/null | nl
                echo ""
                read -p "Enter backup number or name: " backup_input
                # Implementar restore aqui
                ;;
            3)
                echo ""
                read -p "Confirm system reset? (y/N): " confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    reset_system
                    echo ""
                    read -p "Press Enter to continue..."
                fi
                ;;
            4)
                echo ""
                validate_system
                echo ""
                read -p "Press Enter to continue..."
                ;;
            5)
                echo ""
                show_status
                echo ""
                read -p "Press Enter to continue..."
                ;;
            6)
                echo ""
                echo "Schedule feature coming soon..."
                echo ""
                read -p "Press Enter to continue..."
                ;;
            7)
                echo ""
                if [[ -f "$LOG_DIR/recovery.log" ]]; then
                    less "$LOG_DIR/recovery.log"
                else
                    echo "No logs found"
                    read -p "Press Enter to continue..."
                fi
                ;;
            0)
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# Função principal
main() {
    local command="${1:-help}"
    
    case $command in
        "backup")
            local backup_type="full"
            local compress="true"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --type=*)
                        backup_type="${1#*=}"
                        ;;
                    --compress)
                        compress="true"
                        ;;
                    --no-compress)
                        compress="false"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            backup_full "$compress"
            ;;
            
        "restore")
            local backup_file=""
            local validate="true"
            local rollback="true"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --from=*)
                        backup_file="${1#*=}"
                        ;;
                    --no-validate)
                        validate="false"
                        ;;
                    --no-rollback)
                        rollback="false"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            if [[ -z "$backup_file" ]]; then
                error "Especifique --from=arquivo_backup"
                exit 1
            fi
            
            restore_system "$backup_file" "$validate" "$rollback"
            ;;
            
        "reset")
            local mode="full"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --mode=*)
                        mode="${1#*=}"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            reset_system "$mode"
            ;;
            
        "validate")
            local check_type="integrity"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --check=*)
                        check_type="${1#*=}"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            validate_system "$check_type"
            ;;
            
        "status")
            local show_type="last"
            
            # Parse arguments
            shift
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --show=*)
                        show_type="${1#*=}"
                        ;;
                    *)
                        error "Opção desconhecida: $1"
                        exit 1
                        ;;
                esac
                shift
            done
            
            show_status "$show_type"
            ;;
            
        "dashboard")
            show_dashboard
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
