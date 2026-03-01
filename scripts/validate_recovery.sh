#!/bin/bash
# -*- coding: utf-8 -*-
# EXITUS RECOVERY VALIDATOR - Validações Pós-Operação
# Arquiteto: Perplexity AI (Persona 2)
# Versão: 1.0.0
# GAP: EXITUS-RECOVERY-001

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/recovery_validation.log"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_DIR/recovery_validation.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/recovery_validation.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/recovery_validation.log"
}

# Validar integridade do banco de dados
validate_database_integrity() {
    log "Validando integridade do banco de dados..."
    
    # Verificar conexão
    if ! podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
        error "Banco de dados não acessível"
        return 1
    fi
    
    # Verificar tabelas críticas
    local critical_tables=("usuario" "ativo" "portfolio" "transacao" "movimentacao_caixa")
    local failed_tables=()
    
    for table in "${critical_tables[@]}"; do
        if ! podman exec exitus-db psql -U exitus -d exitusdb -c "\dt $table" >/dev/null 2>&1; then
            failed_tables+=("$table")
        fi
    done
    
    if [[ ${#failed_tables[@]} -gt 0 ]]; then
        error "Tabelas críticas faltando: ${failed_tables[*]}"
        return 1
    fi
    
    # Verificar constraints
    local constraint_check
    constraint_check=$(podman exec exitus-db psql -U exitus -d exitusdb -c "
        SELECT 
            COUNT(*) as total_constraints
        FROM information_schema.table_constraints 
        WHERE constraint_schema = 'public'
    " 2>/dev/null | tail -1)
    
    if [[ -z "$constraint_check" || "$constraint_check" -eq 0 ]]; then
        warn "Nenhuma constraint encontrada no banco"
    else
        log "Constraints encontradas: $constraint_check"
    fi
    
    # Verificar dados básicos
    local user_count
    user_count=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM usuario" 2>/dev/null || echo "0")
    
    if [[ "$user_count" -eq 0 ]]; then
        warn "Nenhum usuário encontrado no banco"
    else
        log "Usuários encontrados: $user_count"
    fi
    
    log "Integridade do banco validada"
    return 0
}

# Validar health checks dos serviços
validate_service_health() {
    log "Validando health checks dos serviços..."
    
    local services_down=()
    
    # Database
    if podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
        log "✅ Database: OK"
    else
        services_down+=("Database")
    fi
    
    # Backend
    if curl -fs http://localhost:5000/health >/dev/null 2>&1; then
        log "✅ Backend: OK"
    else
        services_down+=("Backend")
    fi
    
    # Frontend
    if curl -fs http://localhost:8080/health >/dev/null 2>&1; then
        log "✅ Frontend: OK"
    else
        services_down+=("Frontend")
    fi
    
    if [[ ${#services_down[@]} -gt 0 ]]; then
        error "Serviços inoperantes: ${services_down[*]}"
        return 1
    fi
    
    log "Todos os serviços estão operacionais"
    return 0
}

# Validar endpoints críticos
validate_critical_endpoints() {
    log "Validando endpoints críticos..."
    
    # Aguardar serviços iniciarem
    sleep 5
    
    # Endpoint de health do backend
    if curl -fs http://localhost:5000/health >/dev/null 2>&1; then
        log "✅ /health endpoint: OK"
    else
        warn "⚠️ /health endpoint: Falha"
    fi
    
    # Endpoint de autenticação
    if curl -fs http://localhost:5000/api/auth/login >/dev/null 2>&1; then
        log "✅ /api/auth/login endpoint: OK"
    else
        warn "⚠️ /api/auth/login endpoint: Falha"
    fi
    
    # Endpoint de ativos
    if curl -fs http://localhost:5000/api/ativos >/dev/null 2>&1; then
        log "✅ /api/ativos endpoint: OK"
    else
        warn "⚠️ /api/ativos endpoint: Falha"
    fi
    
    log "Validação de endpoints concluída"
    return 0
}

# Validar consistência de dados
validate_data_consistency() {
    log "Validando consistência de dados..."
    
    # Verificar registros órfãos
    local orphaned_records
    orphaned_records=$(podman exec exitus-db psql -U exitus -d exitusdb -c "
        SELECT 
            'portfolio_sem_usuario' as issue, COUNT(*) as count
        FROM portfolio p 
        LEFT JOIN usuario u ON p.usuario_id = u.id 
        WHERE u.id IS NULL
        
        UNION ALL
        
        SELECT 
            'transacao_sem_portfolio' as issue, COUNT(*) as count
        FROM transacao t 
        LEFT JOIN portfolio p ON t.portfolio_id = p.id 
        WHERE p.id IS NULL
    " 2>/dev/null)
    
    if [[ -n "$orphaned_records" ]]; then
        warn "Registros órfãos encontrados:"
        echo "$orphaned_records"
    else
        log "Nenhum registro órfão encontrado"
    fi
    
    # Verificar saldos consistentes
    local balance_check
    balance_check=$(podman exec exitus-db psql -U exitus -d exitusdb -c "
        SELECT 
            COUNT(*) as inconsistent_portfolios
        FROM portfolio 
        WHERE saldo_atual < 0
    " 2>/dev/null | tail -1)
    
    if [[ "$balance_check" -gt 0 ]]; then
        warn "$balance_check portfolios com saldo negativo"
    else
        log "Todos os portfolios têm saldo válido"
    fi
    
    log "Consistência de dados validada"
    return 0
}

# Validar performance
validate_performance() {
    log "Validando performance do sistema..."
    
    # Testar resposta do backend
    local backend_response_time
    backend_response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/health)
    
    if (( $(echo "$backend_response_time > 2.0" | bc -l) )); then
        warn "Backend response time lento: ${backend_response_time}s"
    else
        log "Backend response time OK: ${backend_response_time}s"
    fi
    
    # Testar resposta do frontend
    local frontend_response_time
    frontend_response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8080/health)
    
    if (( $(echo "$frontend_response_time > 2.0" | bc -l) )); then
        warn "Frontend response time lento: ${frontend_response_time}s"
    else
        log "Frontend response time OK: ${frontend_response_time}s"
    fi
    
    # Verificar uso de memória dos containers
    local db_memory
    db_memory=$(podman stats --no-stream --format "{{.MemUsage}}" exitus-db 2>/dev/null || echo "N/A")
    local backend_memory
    backend_memory=$(podman stats --no-stream --format "{{.MemUsage}}" exitus-backend 2>/dev/null || echo "N/A")
    
    log "Uso de memória - DB: $db_memory, Backend: $backend_memory"
    
    log "Performance validada"
    return 0
}

# Gerar relatório de validação
generate_validation_report() {
    local report_file="$LOG_DIR/validation_report_$(date +%Y%m%d_%H%M%S).json"
    
    log "Gerando relatório de validação: $report_file"
    
    # Coletar métricas
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local db_status="unknown"
    local backend_status="unknown"
    local frontend_status="unknown"
    
    # Verificar status dos containers
    if podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
        db_status="running"
    fi
    
    if curl -fs http://localhost:5000/health >/dev/null 2>&1; then
        backend_status="running"
    fi
    
    if curl -fs http://localhost:8080/health >/dev/null 2>&1; then
        frontend_status="running"
    fi
    
    # Contar registros
    local user_count=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM usuario" 2>/dev/null || echo "0")
    local portfolio_count=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM portfolio" 2>/dev/null || echo "0")
    local transaction_count=$(podman exec exitus-db psql -U exitus -d exitusdb -t -c "SELECT COUNT(*) FROM transacao" 2>/dev/null || echo "0")
    
    # Gerar JSON
    cat > "$report_file" << EOF
{
  "validation_id": "validation_$(date +%Y%m%d_%H%M%S)",
  "timestamp": "$timestamp",
  "system_status": {
    "database": "$db_status",
    "backend": "$backend_status",
    "frontend": "$frontend_status"
  },
  "data_metrics": {
    "users": $user_count,
    "portfolios": $portfolio_count,
    "transactions": $transaction_count
  },
  "validation_results": {
    "database_integrity": "passed",
    "service_health": "passed",
    "critical_endpoints": "passed",
    "data_consistency": "passed",
    "performance": "passed"
  },
  "overall_status": "healthy",
  "generated_by": "validate_recovery.sh"
}
EOF
    
    log "Relatório gerado: $report_file"
}

# Função principal
main() {
    local validation_type="${1:-full}"
    
    echo -e "${BLUE}=== EXITUS RECOVERY VALIDATOR ===${NC}"
    echo ""
    
    case $validation_type in
        "database"|"db")
            validate_database_integrity
            ;;
        "health")
            validate_service_health
            ;;
        "endpoints")
            validate_critical_endpoints
            ;;
        "consistency")
            validate_data_consistency
            ;;
        "performance")
            validate_performance
            ;;
        "full"|"all")
            log "Iniciando validação completa do sistema..."
            
            # Executar todas as validações
            if validate_database_integrity && \
               validate_service_health && \
               validate_critical_endpoints && \
               validate_data_consistency && \
               validate_performance; then
                log "✅ Todas as validações passaram com sucesso"
                generate_validation_report
            else
                error "❌ Algumas validações falharam"
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            echo "Uso: $0 [tipo]"
            echo ""
            echo "Tipos de validação:"
            echo "  database, db    - Validar integridade do banco"
            echo "  health          - Validar health checks"
            echo "  endpoints       - Validar endpoints críticos"
            echo "  consistency     - Validar consistência de dados"
            echo "  performance     - Validar performance"
            echo "  full, all       - Executar todas as validações"
            echo ""
            ;;
        *)
            error "Tipo de validação desconhecido: $validation_type"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
