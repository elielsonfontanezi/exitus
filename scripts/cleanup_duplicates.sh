#!/bin/bash

# ============================================================
# 🧹 EXITUS - SCRIPT DE LIMPEZA DE DUPLICAÇÕES
# ============================================================
# Autor: Sistema Exitus
# Data: Janeiro 2026
# Versão: 1.0
# ============================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretórios
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "PROJECT_ROOT=$PROJECT_ROOT"
exit
BACKUP_DIR="$HOME/exitus_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
AUDIT_LOG="$PROJECT_ROOT/logs/audit_$TIMESTAMP.log"

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$AUDIT_LOG"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$AUDIT_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$AUDIT_LOG"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$AUDIT_LOG"
}

# ============================================================
# FASE 0: PRÉ-VALIDAÇÃO
# ============================================================

fase0_validacao() {
    log "============================================================"
    log "FASE 0: PRÉ-VALIDAÇÃO"
    log "============================================================"
    
    # Verificar se estamos no diretório correto
    if [[ ! -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
        error "Diretório inválido! Execute o script da raiz do projeto Exitus."
        exit 1
    fi
    
    # Criar diretório de logs
    mkdir -p "$PROJECT_ROOT/logs"
    
    # Verificar git
    if ! command -v git &> /dev/null; then
        error "Git não encontrado! Instale git para continuar."
        exit 1
    fi
    
    # Verificar status git
    if [[ -n $(git status --porcelain) ]]; then
        warn "Existem mudanças não commitadas!"
        read -p "Deseja continuar mesmo assim? (s/N): " response
        if [[ ! "$response" =~ ^[Ss]$ ]]; then
            info "Operação cancelada pelo usuário."
            exit 0
        fi
    fi
    
    log "✅ Pré-validação concluída"
    echo ""
}

# ============================================================
# FASE 1: BACKUP COMPLETO
# ============================================================

fase1_backup() {
    log "============================================================"
    log "FASE 1: BACKUP COMPLETO"
    log "============================================================"
    
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/exitus_backup_$TIMESTAMP.tar.gz"
    
    info "Criando backup em: $BACKUP_FILE"
    tar -czf "$BACKUP_FILE" \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='*.pyc' \
        --exclude='.git' \
        -C "$PROJECT_ROOT/.." \
        exitus
    
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ Backup criado: $BACKUP_SIZE"
    
    # Criar backup do git
    git branch "backup/pre-cleanup-$TIMESTAMP" 2>/dev/null || true
    log "✅ Branch de backup: backup/pre-cleanup-$TIMESTAMP"
    
    echo ""
}

# ============================================================
# FASE 2: AUDITORIA - ARQUIVOS DUPLICADOS
# ============================================================

fase2_auditoria_arquivos() {
    log "============================================================"
    log "FASE 2: AUDITORIA - ARQUIVOS DUPLICADOS"
    log "============================================================"
    
    cd "$PROJECT_ROOT"
    
    # 2.1 Buscar .bak
    info "🔍 Buscando arquivos .bak..."
    BAK_FILES=$(find . -type f -name "*.bak" ! -path "./.git/*" ! -path "*/node_modules/*" | wc -l)
    
    if [[ $BAK_FILES -gt 0 ]]; then
        warn "Encontrados $BAK_FILES arquivos .bak:"
        find . -type f -name "*.bak" ! -path "./.git/*" ! -path "*/node_modules/*" | tee -a "$AUDIT_LOG"
    else
        log "✅ Nenhum arquivo .bak encontrado"
    fi
    
    # 2.2 Buscar .OLD
    info "🔍 Buscando arquivos .OLD..."
    OLD_FILES=$(find . -type f -name "*.OLD" ! -path "./.git/*" ! -path "*/node_modules/*" | wc -l)
    
    if [[ $OLD_FILES -gt 0 ]]; then
        warn "Encontrados $OLD_FILES arquivos .OLD:"
        find . -type f -name "*.OLD" ! -path "./.git/*" ! -path "*/node_modules/*" | tee -a "$AUDIT_LOG"
    else
        log "✅ Nenhum arquivo .OLD encontrado"
    fi
    
    # 2.3 Buscar *_backup*
    info "🔍 Buscando arquivos *_backup*..."
    BACKUP_FILES=$(find . -type f -name "*_backup*" ! -path "./.git/*" ! -path "*/node_modules/*" ! -path "*/exitus_backups/*" | wc -l)
    
    if [[ $BACKUP_FILES -gt 0 ]]; then
        warn "Encontrados $BACKUP_FILES arquivos *_backup*:"
        find . -type f -name "*_backup*" ! -path "./.git/*" ! -path "*/node_modules/*" ! -path "*/exitus_backups/*" | tee -a "$AUDIT_LOG"
    else
        log "✅ Nenhum arquivo *_backup* encontrado"
    fi
    
    # 2.4 Buscar arquivos temporários
    info "🔍 Buscando arquivos temporários (~, .swp)..."
    TEMP_FILES=$(find . -type f \( -name "*~" -o -name "*.swp" \) ! -path "./.git/*" ! -path "*/node_modules/*" | wc -l)
    
    if [[ $TEMP_FILES -gt 0 ]]; then
        warn "Encontrados $TEMP_FILES arquivos temporários:"
        find . -type f \( -name "*~" -o -name "*.swp" \) ! -path "./.git/*" ! -path "*/node_modules/*" | tee -a "$AUDIT_LOG"
    else
        log "✅ Nenhum arquivo temporário encontrado"
    fi
    
    echo ""
    TOTAL_DUPLICATES=$((BAK_FILES + OLD_FILES + BACKUP_FILES + TEMP_FILES))
    
    if [[ $TOTAL_DUPLICATES -gt 0 ]]; then
        warn "📊 Total de arquivos duplicados: $TOTAL_DUPLICATES"
    else
        log "✅ Nenhum arquivo duplicado encontrado!"
    fi
    
    echo ""
}

# ============================================================
# FASE 3: AUDITORIA - BLUEPRINTS
# ============================================================

fase3_auditoria_blueprints() {
    log "============================================================"
    log "FASE 3: AUDITORIA - BLUEPRINTS"
    log "============================================================"
    
    cd "$PROJECT_ROOT"
    
    # 3.1 Listar todos os blueprints
    info "📋 Blueprints encontrados:"
    ls -1 backend/app/blueprints/*.py 2>/dev/null | grep -v __pycache__ | tee -a "$AUDIT_LOG" || warn "Nenhum blueprint encontrado"
    
    echo ""
    
    # 3.2 Verificar padrão de nomenclatura
    info "🔍 Verificando padrão de nomenclatura (_bp)..."
    
    INCONSISTENT=0
    
    for file in backend/app/blueprints/*.py; do
        if [[ -f "$file" ]] && [[ ! "$file" =~ __init__ ]] && [[ ! "$file" =~ routes ]]; then
            BLUEPRINT_VAR=$(grep -E "^[a-z_]+ = Blueprint\(" "$file" 2>/dev/null | head -1 | cut -d= -f1 | xargs)
            
            if [[ -n "$BLUEPRINT_VAR" ]]; then
                BASENAME=$(basename "$file" .py)
                
                # Verificar se termina com _bp ou _blueprint
                if [[ "$BLUEPRINT_VAR" != *"_bp" ]] && [[ "$BASENAME" != *"routes" ]]; then
                    warn "  ⚠️  $file → Variável: $BLUEPRINT_VAR (deveria ser *_bp)"
                    ((INCONSISTENT++))
                fi
            fi
        fi
    done
    
    if [[ $INCONSISTENT -eq 0 ]]; then
        log "✅ Todos os blueprints seguem o padrão _bp"
    else
        warn "⚠️  $INCONSISTENT blueprints com nomenclatura inconsistente"
    fi
    
    echo ""
}

# ============================================================
# FASE 4: AUDITORIA - IMPORTS
# ============================================================

fase4_auditoria_imports() {
    log "============================================================"
    log "FASE 4: AUDITORIA - IMPORTS"
    log "============================================================"
    
    cd "$PROJECT_ROOT"
    
    # 4.1 Verificar imports duplicados
    info "🔍 Buscando imports duplicados no __init__.py..."
    
    if [[ -f backend/app/__init__.py ]]; then
        DUPLICATE_IMPORTS=$(grep "from .blueprints" backend/app/__init__.py | sort | uniq -d | wc -l)
        
        if [[ $DUPLICATE_IMPORTS -gt 0 ]]; then
            warn "Encontrados $DUPLICATE_IMPORTS imports duplicados:"
            grep "from .blueprints" backend/app/__init__.py | sort | uniq -d | tee -a "$AUDIT_LOG"
        else
            log "✅ Nenhum import duplicado encontrado"
        fi
    fi
    
    echo ""
    
    # 4.2 Verificar código comentado
    info "🔍 Buscando código comentado nos blueprints..."
    
    COMMENTED_LINES=$(find backend/app/blueprints -name "*.py" -exec grep -l "^#.*import\|^#.*def\|^#.*class" {} \; | wc -l)
    
    if [[ $COMMENTED_LINES -gt 0 ]]; then
        warn "Encontrados $COMMENTED_LINES arquivos com código comentado"
    else
        log "✅ Nenhum código comentado excessivo"
    fi
    
    echo ""
}

# ============================================================
# FASE 5: LIMPEZA AUTOMÁTICA
# ============================================================

fase5_limpeza() {
    log "============================================================"
    log "FASE 5: LIMPEZA AUTOMÁTICA"
    log "============================================================"
    
    cd "$PROJECT_ROOT"
    
    warn "Esta fase irá DELETAR arquivos!"
    read -p "Deseja continuar com a limpeza? (s/N): " response
    
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        info "Limpeza cancelada pelo usuário."
        return
    fi
    
    # 5.1 Remover .bak
    info "🗑️  Removendo arquivos .bak..."
    REMOVED_BAK=$(find . -type f -name "*.bak" ! -path "./.git/*" ! -path "*/node_modules/*" -delete -print | wc -l)
    log "✅ Removidos $REMOVED_BAK arquivos .bak"
    
    # 5.2 Remover .OLD
    info "🗑️  Removendo arquivos .OLD..."
    REMOVED_OLD=$(find . -type f -name "*.OLD" ! -path "./.git/*" ! -path "*/node_modules/*" -delete -print | wc -l)
    log "✅ Removidos $REMOVED_OLD arquivos .OLD"
    
    # 5.3 Remover temporários
    info "🗑️  Removendo arquivos temporários..."
    REMOVED_TEMP=$(find . -type f \( -name "*~" -o -name "*.swp" \) ! -path "./.git/*" ! -path "*/node_modules/*" -delete -print | wc -l)
    log "✅ Removidos $REMOVED_TEMP arquivos temporários"
    
    echo ""
    TOTAL_REMOVED=$((REMOVED_BAK + REMOVED_OLD + REMOVED_TEMP))
    log "📊 Total de arquivos removidos: $TOTAL_REMOVED"
    
    echo ""
}

# ============================================================
# FASE 6: CORREÇÕES DE CÓDIGO
# ============================================================

fase6_correcoes() {
    log "============================================================"
    log "FASE 6: CORREÇÕES DE CÓDIGO (MANUAL)"
    log "============================================================"
    
    warn "Esta fase requer revisão manual!"
    warn "Por favor, revise o arquivo de auditoria:"
    warn "  $AUDIT_LOG"
    
    echo ""
    info "Correções sugeridas:"
    echo ""
    echo "1. Padronizar alertas.py:"
    echo "   sed -i 's/^bp = Blueprint/alertas_bp = Blueprint/' backend/app/blueprints/alertas.py"
    echo ""
    echo "2. Atualizar import no __init__.py:"
    echo "   sed -i 's/from .blueprints.alertas import bp as alertas_bp/from .blueprints.alertas import alertas_bp/' backend/app/__init__.py"
    echo ""
    echo "3. Remover código comentado:"
    echo "   # Revisar manualmente cada arquivo"
    echo ""
}

# ============================================================
# FASE 7: VALIDAÇÃO PÓS-LIMPEZA
# ============================================================

fase7_validacao() {
    log "============================================================"
    log "FASE 7: VALIDAÇÃO PÓS-LIMPEZA"
    log "============================================================"
    
    cd "$PROJECT_ROOT"
    
    # 7.1 Verificar sintaxe Python
    info "🔍 Verificando sintaxe Python..."
    
    SYNTAX_ERRORS=0
    for file in $(find backend -name "*.py" ! -path "*/migrations/*"); do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            error "Erro de sintaxe em: $file"
            ((SYNTAX_ERRORS++))
        fi
    done
    
    if [[ $SYNTAX_ERRORS -eq 0 ]]; then
        log "✅ Nenhum erro de sintaxe encontrado"
    else
        error "❌ Encontrados $SYNTAX_ERRORS erros de sintaxe"
    fi
    
    # 7.2 Sugerir testes
    echo ""
    info "📋 Próximos passos:"
    echo "  1. Reiniciar backend: podman restart exitus-backend"
    echo "  2. Verificar logs: podman logs --tail 50 exitus-backend"
    echo "  3. Testar endpoints: scripts/test_all_endpoints.sh"
    echo ""
}

# ============================================================
# FASE 8: RELATÓRIO FINAL
# ============================================================

fase8_relatorio() {
    log "============================================================"
    log "RELATÓRIO FINAL"
    log "============================================================"
    
    echo ""
    log "📁 Backup criado em: $BACKUP_DIR/exitus_backup_$TIMESTAMP.tar.gz"
    log "📄 Auditoria salva em: $AUDIT_LOG"
    log "🌳 Branch de backup: backup/pre-cleanup-$TIMESTAMP"
    echo ""
    
    info "Para restaurar em caso de problemas:"
    echo "  tar -xzf $BACKUP_DIR/exitus_backup_$TIMESTAMP.tar.gz -C ~"
    echo "  git checkout backup/pre-cleanup-$TIMESTAMP"
    echo ""
}

# ============================================================
# MAIN
# ============================================================

main() {
    clear
    
    echo -e "${BLUE}"
    echo "============================================================"
    echo "🧹 EXITUS - LIMPEZA DE DUPLICAÇÕES E PADRONIZAÇÃO"
    echo "============================================================"
    echo -e "${NC}"
    echo "Este script irá:"
    echo "  1. Criar backup completo"
    echo "  2. Auditar arquivos duplicados"
    echo "  3. Auditar nomenclatura de blueprints"
    echo "  4. Auditar imports"
    echo "  5. Limpar arquivos (com confirmação)"
    echo "  6. Sugerir correções de código"
    echo "  7. Validar mudanças"
    echo "  8. Gerar relatório"
    echo ""
    
    read -p "Deseja continuar? (s/N): " START
    
    if [[ ! "$START" =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
    
    echo ""
    
    # Executar fases
    fase0_validacao
    fase1_backup
    fase2_auditoria_arquivos
    fase3_auditoria_blueprints
    fase4_auditoria_imports
    fase5_limpeza
    fase6_correcoes
    fase7_validacao
    fase8_relatorio
    
    log "✅ Script concluído com sucesso!"
}

# Executar
main "$@"
