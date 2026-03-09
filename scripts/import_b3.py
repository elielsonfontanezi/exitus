#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Importação B3 Portal Investidor - Script Híbrido
# GAP: EXITUS-IMPORT-001
# Arquiteto: Perplexity AI (Persona 2)

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

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Função de ajuda
show_help() {
    echo -e "${CYAN}Importação B3 Portal Investidor v1.0.0${NC}"
    echo ""
    echo "Script híbrido para importação de arquivos CSV/Excel da B3"
    echo ""
    echo "Uso: $0 [arquivo_movimentacoes] [arquivo_negociacoes] [opções]"
    echo ""
    echo "Arquivos:"
    echo "  arquivo_movimentacoes    Caminho para movimentacao-*.xlsx ou movimentacao-*.csv"
    echo "  arquivo_negociacoes       Caminho para negociacao-*.xlsx ou negociacao-*.csv (opcional)"
    echo ""
    echo "Opções:"
    echo "  --sobrescrever           Sobrescrever registros duplicados (default: true)"
    echo "  --dry-run                Apenas analisar arquivos, não importar"
    echo "  --backup                 Criar backup antes de importar"
    echo "  --help, -h               Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 movimentacao-202601.xlsx negociacao-202601.xlsx"
    echo "  $0 movimentacao-202601.csv --dry-run"
    echo "  $0 movimentacao-202601.xlsx --backup --sobrescrever"
    echo ""
}

# Validar arquivo
validar_arquivo() {
    local arquivo="$1"
    
    if [[ ! -f "$arquivo" ]]; then
        error "Arquivo não encontrado: $arquivo"
        return 1
    fi
    
    # Verificar extensão
    if [[ ! "$arquivo" =~ \.(csv|xlsx|xls)$ ]]; then
        error "Extensão inválida: $arquivo (use .csv, .xlsx ou .xls)"
        return 1
    fi
    
    # Verificar tamanho
    if [[ ! -s "$arquivo" ]]; then
        error "Arquivo vazio: $arquivo"
        return 1
    fi
    
    log "Arquivo válido: $arquivo"
    return 0
}

# Analisar arquivo (dry-run)
analisar_arquivo() {
    local arquivo="$1"
    local tipo="$2"
    
    log "Analisando arquivo: $arquivo"
    
    # Usar Python para análise
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT/backend')

try:
    from app.services.import_b3_service import ImportB3Service
    
    service = ImportB3Service()
    
    if '$tipo' == 'movimentacoes':
        dados = service.parse_movimentacoes('$arquivo')
        print(f'{len(dados)} movimentações encontradas')
        
        if dados:
            print('Amostra de dados:')
            for i, item in enumerate(dados[:3]):
                print(f'  {i+1}. {item[\"data\"]} - {item[\"tipo_movimentacao\"]} - {item[\"produto\"]} - R$ {item[\"valor_operacao\"]}')
            
            print('Tipos de movimentação:')
            tipos = {}
            for item in dados:
                tipos[item['tipo_movimentacao']] = tipos.get(item['tipo_movimentacao'], 0) + 1
            for tipo, count in tipos.items():
                print(f'  {tipo}: {count}')
    
    elif '$tipo' == 'negociacoes':
        dados = service.parse_negociacoes('$arquivo')
        print(f'{len(dados)} negociações encontradas')
        
        if dados:
            print('Amostra de dados:')
            for i, item in enumerate(dados[:3]):
                print(f'  {i+1}. {item[\"data\"]} - {item[\"tipo_movimentacao\"]} - {item[\"codigo_negociacao\"]} - R$ {item[\"valor\"]}')
            
            print('Tipos de negociação:')
            tipos = {}
            for item in dados:
                tipos[item['tipo_movimentacao']] = tipos.get(item['tipo_movimentacao'], 0) + 1
            for tipo, count in tipos.items():
                print(f'  {tipo}: {count}')
    
except Exception as e:
    print(f'Erro na análise: {e}')
    sys.exit(1)
"
}

# Importar arquivo
importar_arquivo() {
    local arquivo="$1"
    local tipo="$2"
    local sobrescrever="${3:-true}"
    
    log "Importando arquivo: $arquivo"
    
    # Usar Python para importação
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT/backend')

try:
    from app import create_app, db
    from app.services.import_b3_service import ImportB3Service
    
    app = create_app()
    
    with app.app_context():
        service = ImportB3Service()
        
        if '$tipo' == 'movimentacoes':
            dados = service.parse_movimentacoes('$arquivo')
            if dados:
                resultado = service.importar_movimentacoes(dados, sobrescrever=$sobrescrever)
                print(f'Movimentações: {resultado[\"sucesso\"]} importadas com sucesso')
                if resultado['erros'] > 0:
                    print(f'Erros: {resultado[\"erros\"]}')
                    for erro in resultado['erros_lista'][:5]:
                        print(f'   {erro}')
                print(f'Ativos criados: {resultado[\"ativos_criados\"]}')
                print(f'Corretoras criadas: {resultado[\"corretoras_criadas\"]}')
            else:
                print('Nenhuma movimentação válida encontrada')
        
        elif '$tipo' == 'negociacoes':
            dados = service.parse_negociacoes('$arquivo')
            if dados:
                resultado = service.importar_negociacoes(dados, sobrescrever=$sobrescrever)
                print(f'Negociações: {resultado[\"sucesso\"]} importadas com sucesso')
                if resultado['erros'] > 0:
                    print(f'Erros: {resultado[\"erros\"]}')
                    for erro in resultado['erros_lista'][:5]:
                        print(f'   {erro}')
                print(f'Ativos criados: {resultado[\"ativos_criados\"]}')
                print(f'Corretoras criadas: {resultado[\"corretoras_criadas\"]}')
            else:
                print('Nenhuma negociação válida encontrada')
        
except Exception as e:
    print(f'Erro na importação: {e}')
    sys.exit(1)
"
}

# Criar backup
criar_backup() {
    log "Criando backup pré-importação..."
    
    if [[ -x "$SCRIPT_DIR/recovery_manager.sh" ]]; then
        "$SCRIPT_DIR/recovery_manager.sh" backup --type=full --compress
        log "Backup criado com sucesso"
    else
        warn "Script de recovery não encontrado, pulando backup"
    fi
}

# Verificar dependências
verificar_dependencias() {
    log "Verificando dependências..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 não encontrado"
        return 1
    fi
    
    # Verificar se estamos no diretório correto
    if [[ ! -d "$PROJECT_ROOT/backend" ]]; then
        error "Diretório backend não encontrado: $PROJECT_ROOT/backend"
        return 1
    fi
    
    # Verificar se o container backend está rodando
    if ! podman ps --format "{{.Names}}" | grep -q "exitus-backend"; then
        error "Container exitus-backend não está rodando"
        return 1
    fi
    
    log "Dependências OK"
    return 0
}

# Função principal
main() {
    local arquivo_movimentacoes=""
    local arquivo_negociacoes=""
    local sobrescrever="true"
    local dry_run="false"
    local criar_backup_flag="false"
    
    # Parse argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --sobrescrever)
                sobrescrever="true"
                ;;
            --no-sobrescrever)
                sobrescrever="false"
                ;;
            --dry-run)
                dry_run="true"
                ;;
            --backup)
                criar_backup_flag="true"
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            -*)
                error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$arquivo_movimentacoes" ]]; then
                    arquivo_movimentacoes="$1"
                elif [[ -z "$arquivo_negociacoes" ]]; then
                    arquivo_negociacoes="$1"
                else
                    error "Número excessivo de argumentos"
                    show_help
                    exit 1
                fi
                ;;
        esac
        shift
    done
    
    # Validar argumentos obrigatórios
    if [[ -z "$arquivo_movimentacoes" ]]; then
        error "Arquivo de movimentações é obrigatório"
        show_help
        exit 1
    fi
    
    # Verificar dependências
    verificar_dependencias || exit 1
    
    # Validar arquivos
    validar_arquivo "$arquivo_movimentacoes" || exit 1
    if [[ -n "$arquivo_negociacoes" ]]; then
        validar_arquivo "$arquivo_negociacoes" || exit 1
    fi
    
    # Criar backup se solicitado
    if [[ "$criar_backup_flag" == "true" ]]; then
        criar_backup
    fi
    
    echo ""
    echo -e "${CYAN}=== IMPORTAÇÃO B3 PORTAL INVESTIDOR ===${NC}"
    echo ""
    
    # Processar movimentações
    echo -e "${BLUE}Processando Movimentacoes:${NC}"
    if [[ "$dry_run" == "true" ]]; then
        analisar_arquivo "$arquivo_movimentacoes" "movimentacoes"
    else
        importar_arquivo "$arquivo_movimentacoes" "movimentacoes" "$sobrescrever"
    fi
    
    echo ""
    
    # Processar negociações (se fornecido)
    if [[ -n "$arquivo_negociacoes" ]]; then
        echo -e "${BLUE}Processando Negociacoes:${NC}"
        if [[ "$dry_run" == "true" ]]; then
            analisar_arquivo "$arquivo_negociacoes" "negociacoes"
        else
            importar_arquivo "$arquivo_negociacoes" "negociacoes" "$sobrescrever"
        fi
    fi
    
    echo ""
    if [[ "$dry_run" == "true" ]]; then
        log "Análise concluída (modo dry-run)"
    else
        log "Importação concluída com sucesso"
    fi
}

# Executar função principal
main "$@"
