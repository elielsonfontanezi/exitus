#!/bin/bash
# -*- coding: utf-8 -*-
# EXITUS RECOVERY DASHBOARD - Interface Interativa TUI
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
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
METADATA_DIR="$PROJECT_ROOT/backups/metadata"
LOG_DIR="$PROJECT_ROOT/logs"

# Funções de UI
clear_screen() {
    clear
}

draw_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    EXITUS RECOVERY MANAGER                    ║${NC}"
    echo -e "${CYAN}║                       v1.0.0 - TUI                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

draw_footer() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║ [ESC] Voltar | [Q] Sair | [R] Atualizar | [H] Ajuda           ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
}

get_system_status() {
    local db_status="❌ Down"
    local backend_status="❌ Down"
    local frontend_status="❌ Down"
    
    # Database
    if podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1" >/dev/null 2>&1; then
        db_status="✅ Running"
    fi
    
    # Backend
    if curl -fs http://localhost:5000/health >/dev/null 2>&1; then
        backend_status="✅ Running"
    fi
    
    # Frontend
    if curl -fs http://localhost:8080/health >/dev/null 2>&1; then
        frontend_status="✅ Running"
    fi
    
    echo "$db_status|$backend_status|$frontend_status"
}

get_backup_info() {
    local last_backup="Nenhum"
    local backup_count=0
    local total_size="0MB"
    
    if [[ -d "$BACKUP_DIR" ]]; then
        last_backup=$(ls -t "$BACKUP_DIR"/*.sql* 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "Nenhum")
        backup_count=$(ls -1 "$BACKUP_DIR"/*.sql* 2>/dev/null | wc -l)
        
        if [[ "$backup_count" -gt 0 ]]; then
            total_size=$(du -sh "$BACKUP_DIR"/*.sql* 2>/dev/null | cut -f1 | tail -1)
        fi
    fi
    
    echo "$last_backup|$backup_count|$total_size"
}

get_disk_space() {
    local available="N/A"
    local used="N/A"
    
    if [[ -d "$BACKUP_DIR" ]]; then
        available=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $4}')
        used=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $3}')
    fi
    
    echo "$available|$used"
}

# Tela principal
show_main_screen() {
    while true; do
        clear_screen
        draw_header
        
        # Status do sistema
        local status_info
        status_info=$(get_system_status)
        IFS='|' read -r db_status backend_status frontend_status <<< "$status_info"
        
        echo -e "${WHITE}📊 STATUS DO SISTEMA${NC}"
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ Database:   $db_status"
        echo "│ Backend:    $backend_status"
        echo "│ Frontend:   $frontend_status"
        echo "└─────────────────────────────────────────────────────────┘"
        echo ""
        
        # Informações de backup
        local backup_info
        backup_info=$(get_backup_info)
        IFS='|' read -r last_backup backup_count total_size <<< "$backup_info"
        
        echo -e "${WHITE}💾 INFORMAÇÕES DE BACKUP${NC}"
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ Último Backup: ${YELLOW}$last_backup${NC}"
        echo "│ Total Backups:  ${YELLOW}$backup_count${NC}"
        echo "│ Espaço Usado:   ${YELLOW}$total_size${NC}"
        echo "└─────────────────────────────────────────────────────────┘"
        echo ""
        
        # Espaço em disco
        local disk_info
        disk_info=$(get_disk_space)
        IFS='|' read -r available used <<< "$disk_info"
        
        echo -e "${WHITE}💽 ESPAÇO EM DISCO${NC}"
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ Disponível: ${GREEN}$available${NC}"
        echo "│ Usado:      ${YELLOW}$used${NC}"
        echo "└─────────────────────────────────────────────────────────┘"
        echo ""
        
        # Menu principal
        echo -e "${WHITE}🚀 MENU PRINCIPAL${NC}"
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Criar Backup Agora                            │"
        echo "│ ${GREEN}[2]${NC} Restaurar Sistema                             │"
        echo "│ ${GREEN}[3]${NC} Resetar Sistema                               │"
        echo "│ ${GREEN}[4]${NC} Validar Sistema                              │"
        echo "│ ${GREEN}[5]${NC} Gerenciar Backups                             │"
        echo "│ ${GREEN}[6]${NC} Rollback                                     │"
        echo "│ ${GREEN}[7]${NC} Ver Logs                                      │"
        echo "│ ${GREEN}[8]${NC} Configurações                                │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        # Ler input
        read -rsn1 key
        
        case $key in
            1)
                show_backup_screen
                ;;
            2)
                show_restore_screen
                ;;
            3)
                show_reset_screen
                ;;
            4)
                show_validate_screen
                ;;
            5)
                show_backup_management_screen
                ;;
            6)
                show_rollback_screen
                ;;
            7)
                show_logs_screen
                ;;
            8)
                show_config_screen
                ;;
            'q'|'Q')
                echo "Saindo..."
                exit 0
                ;;
            'h'|'H')
                show_help_screen
                ;;
            'r'|'R')
                continue
                ;;
        esac
    done
}

# Tela de backup
show_backup_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}💾 CRIAR BACKUP${NC}"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Backup Completo (Full)                       │"
        echo "│ ${GREEN}[2]${NC} Backup Incremental                           │"
        echo "│ ${GREEN}[3]${NC} Backup Agendado                             │"
        echo "│ ${GREEN}[4]${NC} Backup Personalizado                         │"
        echo "└─────────────────────────────────────────────────────────┘"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${YELLOW}Opções:${NC}                                            │"
        echo "│ • Compressão: ${GREEN}Ativada${NC}                           │"
        echo "│ • Validação: ${GREEN}Ativada${NC}                           │"
        echo "│ • Metadados:  ${GREEN}Ativados${NC}                          │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            1)
                execute_backup "full"
                ;;
            2)
                execute_backup "incremental"
                ;;
            3)
                show_scheduled_backup_screen
                ;;
            4)
                show_custom_backup_screen
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Executar backup
execute_backup() {
    local backup_type="$1"
    
    clear_screen
    draw_header
    
    echo -e "${WHITE}💾 EXECUTANDO BACKUP${NC}"
    echo ""
    echo "Tipo: ${YELLOW}$backup_type${NC}"
    echo ""
    
    # Executar backup
    if "$SCRIPT_DIR/recovery_manager.sh" backup --type="$backup_type"; then
        echo ""
        echo -e "${GREEN}✅ Backup concluído com sucesso!${NC}"
        echo ""
        read -p "Pressione Enter para continuar..."
    else
        echo ""
        echo -e "${RED}❌ Falha ao executar backup${NC}"
        echo ""
        read -p "Pressione Enter para continuar..."
    fi
}

# Tela de restore
show_restore_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}🔄 RESTAURAR SISTEMA${NC}"
        echo ""
        
        # Listar backups disponíveis
        if [[ -d "$BACKUP_DIR" ]]; then
            echo "┌─────────────────────────────────────────────────────────┐"
            echo "│ ${YELLOW}Backups Disponíveis:${NC}                              │"
            echo "├─────────────────────────────────────────────────────────┤"
            
            local count=0
            while IFS= read -r backup_file; do
                ((count++))
                if [[ $count -le 10 ]]; then
                    local basename_file
                    basename_file=$(basename "$backup_file")
                    local file_size
                    file_size=$(du -h "$backup_file" | cut -f1)
                    local file_date
                    file_date=$(stat -c %y "$backup_file" | cut -d' ' -f1 | cut -d'-' -f2,3)
                    
                    printf "│ ${GREEN}[%2d]${NC} %-45s ${YELLOW}%8s${NC} ${CYAN}%10s${NC} │\n" \
                        "$count" "$basename_file" "$file_size" "$file_date"
                fi
            done <<< "$(ls -t "$BACKUP_DIR"/*.sql* 2>/dev/null)"
            
            if [[ $count -eq 0 ]]; then
                echo "│ ${RED}Nenhum backup encontrado${NC}                              │"
            fi
            
            echo "└─────────────────────────────────────────────────────────┘"
            echo ""
        fi
        
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1-9]${NC} Selecionar Backup                            │"
        echo "│ ${GREEN}[B]${NC} Buscar Backup Específico                      │"
        echo "│ ${GREEN}[V]${NC} Validar Backup Antes de Restaurar           │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            [1-9])
                select_backup_by_number "$key"
                ;;
            'b'|'B')
                show_search_backup_screen
                ;;
            'v'|'V')
                show_validate_backup_screen
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Tela de reset
show_reset_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}🔄 RESETAR SISTEMA${NC}"
        echo ""
        echo -e "${RED}⚠️  ATENÇÃO: Esta operação irá resetar o sistema!${NC}"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Reset Completo (Full)                        │"
        echo "│ ${GREEN}[2]${NC} Reset Mínimo (Minimal)                       │"
        echo "│ ${GREEN}[3]${NC} Reset Personalizado (Custom)                   │"
        echo "└─────────────────────────────────────────────────────────┘"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${YELLOW}O que será feito:${NC}                                 │"
        echo "│ • Backup automático do estado atual                   │"
        echo "│ • Limpeza do banco de dados                          │"
        echo "│ • População com seeds                                │"
        echo "│ • Validação do sistema                               │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            1)
                execute_reset "full"
                ;;
            2)
                execute_reset "minimal"
                ;;
            3)
                show_custom_reset_screen
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Executar reset
execute_reset() {
    local reset_mode="$1"
    
    clear_screen
    draw_header
    
    echo -e "${WHITE}🔄 EXECUTANDO RESET${NC}"
    echo ""
    echo "Modo: ${YELLOW}$reset_mode${NC}"
    echo ""
    
    # Confirmação
    echo -e "${RED}⚠️  CONFIRMAÇÃO NECESSÁRIA${NC}"
    echo "Esta operação irá:"
    echo "• Criar backup do estado atual"
    echo "• Resetar o sistema para modo $reset_mode"
    echo "• Todos os dados atuais serão perdidos"
    echo ""
    echo -n "Confirmar reset? (s/N): "
    read -r confirm
    
    if [[ "$confirm" =~ ^[Ss]$ ]]; then
        echo ""
        echo "Executando reset..."
        
        if "$SCRIPT_DIR/recovery_manager.sh" reset --mode="$reset_mode"; then
            echo ""
            echo -e "${GREEN}✅ Reset concluído com sucesso!${NC}"
            echo ""
            read -p "Pressione Enter para continuar..."
        else
            echo ""
            echo -e "${RED}❌ Falha ao executar reset${NC}"
            echo ""
            read -p "Pressione Enter para continuar..."
        fi
    else
        echo ""
        echo "Reset cancelado."
        sleep 1
    fi
}

# Tela de validação
show_validate_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}✅ VALIDAR SISTEMA${NC}"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Validação Completa                           │"
        echo "│ ${GREEN}[2]${NC} Integridade do Banco                          │"
        echo "│ ${GREEN}[3]${NC} Health Checks                                 │"
        echo "│ ${GREEN}[4]${NC} Endpoints Críticos                            │"
        echo "│ ${GREEN}[5]${NC} Consistência de Dados                         │"
        echo "│ ${GREEN}[6]${NC} Performance                                    │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            1)
                execute_validation "full"
                ;;
            2)
                execute_validation "database"
                ;;
            3)
                execute_validation "health"
                ;;
            4)
                execute_validation "endpoints"
                ;;
            5)
                execute_validation "consistency"
                ;;
            6)
                execute_validation "performance"
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Executar validação
execute_validation() {
    local validation_type="$1"
    
    clear_screen
    draw_header
    
    echo -e "${WHITE}✅ EXECUTANDO VALIDAÇÃO${NC}"
    echo ""
    echo "Tipo: ${YELLOW}$validation_type${NC}"
    echo ""
    
    # Executar validação
    if "$SCRIPT_DIR/validate_recovery.sh" "$validation_type"; then
        echo ""
        echo -e "${GREEN}✅ Validação concluída com sucesso!${NC}"
        echo ""
        read -p "Pressione Enter para continuar..."
    else
        echo ""
        echo -e "${RED}❌ Falha na validação${NC}"
        echo ""
        read -p "Pressione Enter para continuar..."
    fi
}

# Tela de ajuda
show_help_screen() {
    clear_screen
    draw_header
    
    echo -e "${WHITE}❓ AJUDA - EXITUS RECOVERY MANAGER${NC}"
    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│ ${YELLOW}Comandos do Dashboard:${NC}                              │"
    echo "│ • ${GREEN}[1-8]${NC} Navegar pelas opções do menu                  │"
    echo "│ • ${GREEN}[ESC]${NC} Voltar para tela anterior                   │"
    echo "│ • ${GREEN}[Q]${NC} Sair do sistema                                │"
    echo "│ • ${GREEN}[R]${NC} Atualizar tela atual                          │"
    echo "│ • ${GREEN}[H]${NC} Mostrar esta ajuda                            │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ ${YELLOW}Tipos de Backup:${NC}                                   │"
    echo "│ • ${GREEN}Full${NC}: Backup completo do sistema                 │"
    echo "│ • ${GREEN}Incremental${NC}: Backup apenas das mudanças          │"
    echo "│ • ${GREEN}Custom${NC}: Backup personalizado                     │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ ${YELLOW}Tipos de Reset:${NC}                                    │"
    echo "│ • ${GREEN}Full${NC}: Reset completo com seeds                   │"
    echo "│ • ${GREEN}Minimal${NC}: Reset mínimo (dados básicos)           │"
    echo "│ • ${GREEN}Custom${NC}: Reset personalizado                     │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ ${YELLOW}Validações:${NC}                                       │"
    echo "│ • ${GREEN}Full${NC}: Validação completa do sistema            │"
    echo "│ • ${GREEN}Database${NC}: Integridade do banco                  │"
    echo "│ • ${GREEN}Health${NC}: Health checks dos serviços             │"
    echo "└─────────────────────────────────────────────────────────┘"
    
    echo ""
    read -p "Pressione Enter para voltar..."
}

# Tela de logs
show_logs_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}📋 VISUALIZAR LOGS${NC}"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Logs de Recovery                              │"
        echo "│ ${GREEN}[2]${NC} Logs de Validação                            │"
        echo "│ ${GREEN}[3]${NC} Logs de Rollback                              │"
        echo "│ ${GREEN}[4]${NC} Logs Completos                               │"
        echo "│ ${GREEN}[5]${NC} Logs em Tempo Real                            │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            1)
                view_log "recovery.log"
                ;;
            2)
                view_log "recovery_validation.log"
                ;;
            3)
                view_log "recovery_rollback.log"
                ;;
            4)
                view_all_logs
                ;;
            5)
                view_realtime_logs
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Visualizar log
view_log() {
    local log_file="$1"
    local log_path="$LOG_DIR/$log_file"
    
    if [[ -f "$log_path" ]]; then
        clear_screen
        draw_header
        echo -e "${WHITE}📋 VISUALIZAR LOG: $log_file${NC}"
        echo ""
        
        # Mostrar últimas 50 linhas
        tail -50 "$log_path"
        
        echo ""
        echo -e "${CYAN}Pressione 'q' para sair, setas para navegar${NC}"
        
        # Usar less para visualização
        less "$log_path"
    else
        clear_screen
        draw_header
        echo -e "${RED}Arquivo de log não encontrado: $log_file${NC}"
        echo ""
        read -p "Pressione Enter para voltar..."
    fi
}

# Tela de configurações
show_config_screen() {
    while true; do
        clear_screen
        draw_header
        
        echo -e "${WHITE}⚙️ CONFIGURAÇÕES${NC}"
        echo ""
        echo "┌─────────────────────────────────────────────────────────┐"
        echo "│ ${GREEN}[1]${NC} Configurações de Backup                        │"
        echo "│ ${GREEN}[2]${NC} Configurações de Validação                     │"
        echo "│ ${GREEN}[3]${NC] Configurações de Retenção                      │"
        echo "│ ${GREEN}[4]${NC} Configurações de Notificações                  │"
        echo "│ ${GREEN}[5]${NC} Restaurar Configurações Padrão                 │"
        echo "└─────────────────────────────────────────────────────────┘"
        
        draw_footer
        
        read -rsn1 key
        
        case $key in
            1)
                show_backup_config_screen
                ;;
            2)
                show_validation_config_screen
                ;;
            3)
                show_retention_config_screen
                ;;
            4)
                show_notification_config_screen
                ;;
            5)
                restore_default_config
                ;;
            27) # ESC
                return
                ;;
        esac
    done
}

# Função principal
main() {
    # Verificar dependências
    if ! command -v podman &> /dev/null; then
        echo -e "${RED}Erro: Podman não encontrado${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}Erro: curl não encontrado${NC}"
        exit 1
    fi
    
    # Criar diretórios necessários
    mkdir -p "$BACKUP_DIR" "$METADATA_DIR" "$LOG_DIR"
    
    # Iniciar dashboard
    show_main_screen
}

# Executar função principal
main "$@"
