#!/bin/bash
# Importação B3 Portal Investidor - Script Simplificado
# GAP: EXITUS-IMPORT-001

set -euo pipefail

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Função de ajuda
show_help() {
    cat << 'EOF'
🚀 Importação B3 Portal Investidor v1.0 - GAP EXITUS-IMPORT-001

📋 USO:
    ./scripts/import_b3.sh [arquivo_movimentacoes] [arquivo_negociacoes] [opções]

📁 ARQUIVOS:
    arquivo_movimentacoes    Caminho para movimentacao-*.xlsx (obrigatório)
                            Ex: tmp/movimentacao-2026-02-28-10-24-04.xlsx
                            
    arquivo_negociacoes       Caminho para negociacao-*.xlsx (opcional)
                            Ex: tmp/negociacao-2026-02-28-10-24-45.xlsx

⚙️  OPÇÕES:
    --dry-run                Apenas analisar arquivos sem importar
                            • Mostra estatísticas e amostra dos dados
                            • Identifica tipos não tratados
                            • Valida formato e estrutura
    
    --backup                 Criar backup completo antes de importar
                            • Usa recovery_manager.sh se disponível
                            • Recomendado para ambiente de produção
                            • Cria backup full do banco de dados
    
    --clean                  ⚠️  LIMPAR BASE DE DADOS antes de importar
                            • APAGA TODOS os dados de investimento:
                              - proventos (0 registros)
                              - transações (0 registros) 
                              - posições (0 registros)
                              - ativos (0 registros)
                              - corretoras (0 registros)
                            • Preserva apenas dados de sistema (usuários)
                            • ⚠️  USAR COM CUIDADO - SEM ROLLBACK!
                            • Ideal para testes e desenvolvimento
    
    --help, -h               Mostrar esta ajuda detalhada

🎯 EXEMPLOS DE USO:

    # Análise segura (sem alterações)
    ./scripts/import_b3.sh tmp/movimentacao-2026-02-28-10-24-04.xlsx --dry-run

    # Importação normal (preserva dados existentes)
    ./scripts/import_b3.sh tmp/movimentacao-2026-02-28-10-24-04.xlsx

    # Importação com backup (recomendado para produção)
    ./scripts/import_b3.sh tmp/movimentacao-2026-02-28-10-24-04.xlsx --backup

    # Importação com base limpa (ideal para testes)
    ./scripts/import_b3.sh tmp/movimentacao-2026-02-28-10-24-04.xlsx --clean

    # Importação completa (movimentações + negociações)
    ./scripts/import_b3.sh tmp/movimentacao-2026-02-28-10-24-04.xlsx tmp/negociacao-2026-02-28-10-24-45.xlsx --clean

📊 TIPOS DE MOVIMENTAÇÃO TRATADOS:

    ✅ Importados como Provento:
       - Rendimento, Dividendo, Juros Sobre Capital Próprio
       - Direito de Subscrição, Bonificação
    
    ⚠️  Identificados mas não implementados:
       - "Transferência - Liquidação" → Evento de custódia D+2 (futuro GAP)
    
    ❌ Ignorados (não aplicáveis):
       - "Cessão de Direitos - Solicitada"
       - Valores zerados (violam constraint)

💡 DICAS IMPORTANTES:

    1. Use --clean para testes limpos e consistentes
    2. Use --backup para ambiente de produção  
    3. Use --dry-run para validar arquivos antes
    4. Valores monetários usam formato European (R$ 0,80)
    5. Quantidades são tratadas como inteiros
    6. Erros são logados detalhadamente para debug

🔍 EXEMPLO DE SAÍDA:

    Movimentações: 9 importadas
    Ativos criados: 3  
    Corretoras criadas: 1
    Erros: 43 (duplicatas/tipos ignorados)

⚠️  AVISOS DE SEGURANÇA:

    • --clean apaga IRREVERSIVELMENTE dados de investimento
    • Sempre faça --backup antes de --clean em produção
    • Teste sempre com --dry-run primeiro
    • Verifique logs para erros e tipos ignorados

EOF
}

# Validar arquivo
validar_arquivo() {
    local arquivo="$1"
    
    if [[ ! -f "$arquivo" ]]; then
        error "Arquivo não encontrado: $arquivo"
        return 1
    fi
    
    if [[ ! "$arquivo" =~ \.(xlsx|xls)$ ]]; then
        error "Extensão inválida: $arquivo (use .xlsx ou .xls)"
        return 1
    fi
    
    if [[ ! -s "$arquivo" ]]; then
        error "Arquivo vazio: $arquivo"
        return 1
    fi
    
    log "Arquivo válido: $arquivo"
    return 0
}

# Analisar arquivo
analisar_arquivo() {
    local arquivo="$1"
    local tipo="$2"
    local arquivo_container="/tmp/$(basename "$arquivo")"
    
    log "Analisando arquivo: $arquivo"
    
    # Copiar arquivo para o container
    podman cp "$arquivo" exitus-backend:"$arquivo_container"
    
    podman exec -i exitus-backend python3 -c "
import sys
sys.path.append('/app')

try:
    from app.services.import_b3_service import ImportB3Service
    
    service = ImportB3Service()
    
    if '$tipo' == 'movimentacoes':
        dados = service.parse_movimentacoes('$arquivo_container')
        print(f'{len(dados)} movimentações encontradas')
        
        if dados:
            print('Amostra:')
            for i, item in enumerate(dados[:3]):
                print(f'  {i+1}. {item[\"data\"]} - {item[\"tipo_movimentacao\"]} - {item[\"produto\"]}')
    
    elif '$tipo' == 'negociacoes':
        dados = service.parse_negociacoes('$arquivo_container')
        print(f'{len(dados)} negociações encontradas')
        
        if dados:
            print('Amostra:')
            for i, item in enumerate(dados[:3]):
                print(f'  {i+1}. {item[\"data\"]} - {item[\"tipo_movimentacao\"]} - {item[\"codigo_negociacao\"]}')
    
except Exception as e:
    print(f'Erro: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
}

# Importar arquivo
importar_arquivo() {
    local arquivo="$1"
    local tipo="$2"
    local arquivo_container="/tmp/$(basename "$arquivo")"
    
    log "Importando arquivo: $arquivo"
    
    # Copiar arquivo para o container
    podman cp "$arquivo" exitus-backend:"$arquivo_container"
    
    podman exec -i exitus-backend python3 -c "
import sys
sys.path.append('/app')

try:
    from app import create_app
    from app.database import db
    from app.services.import_b3_service import ImportB3Service
    
    app = create_app()
    
    with app.app_context():
        service = ImportB3Service()
        
        if '$tipo' == 'movimentacoes':
            dados = service.parse_movimentacoes('$arquivo_container')
            if dados:
                resultado = service.importar_movimentacoes(dados)
                print(f'Movimentações: {resultado[\"sucesso\"]} importadas')
                print(f'Ativos criados: {resultado[\"ativos_criados\"]}')
                print(f'Corretoras criadas: {resultado[\"corretoras_criadas\"]}')
                if resultado['erros'] > 0:
                    print(f'Erros: {resultado[\"erros\"]}')
        
        elif '$tipo' == 'negociacoes':
            dados = service.parse_negociacoes('$arquivo_container')
            if dados:
                resultado = service.importar_negociacoes(dados)
                print(f'Negociações: {resultado[\"sucesso\"]} importadas')
                print(f'Ativos criados: {resultado[\"ativos_criados\"]}')
                print(f'Corretoras criadas: {resultado[\"corretoras_criadas\"]}')
                if resultado['erros'] > 0:
                    print(f'Erros: {resultado[\"erros\"]}')
        
except Exception as e:
    print(f'Erro na importação: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
}

# Limpar base de dados
clean_database() {
    log "Limpando base de dados..."
    
    podman exec -i exitus-backend python3 -c "
import sys
sys.path.append('/app')

try:
    from app import create_app
    from app.database import db
    from app.models.provento import Provento
    from app.models.transacao import Transacao
    from app.models.ativo import Ativo
    from app.models.corretora import Corretora
    from app.models.posicao import Posicao
    
    app = create_app()
    
    with app.app_context():
        # Limpar na ordem correta (respeitando FKs)
        Provento.query.delete()
        Transacao.query.delete()
        Posicao.query.delete()
        Ativo.query.delete()
        Corretora.query.delete()
        
        db.session.commit()
        print('Base de dados limpa com sucesso')
    
except Exception as e:
    print(f'Erro ao limpar base: {e}')
    sys.exit(1)
"
}

# Verificar dependências
verificar_dependencias() {
    log "Verificando dependências..."
    
    if ! command -v podman &> /dev/null; then
        error "Podman não encontrado"
        return 1
    fi
    
    if ! podman ps --format "table {{.Names}}" | grep -q "exitus-backend"; then
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
    local dry_run="false"
    local criar_backup="false"
    local clean_db="false"
    
    # Parse argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run="true"
                ;;
            --backup)
                criar_backup="true"
                ;;
            --clean)
                clean_db="true"
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
                    exit 1
                fi
                ;;
        esac
        shift
    done
    
    if [[ -z "$arquivo_movimentacoes" ]]; then
        error "Arquivo de movimentações é obrigatório"
        show_help
        exit 1
    fi
    
    verificar_dependencias || exit 1
    validar_arquivo "$arquivo_movimentacoes" || exit 1
    
    if [[ -n "$arquivo_negociacoes" ]]; then
        validar_arquivo "$arquivo_negociacoes" || exit 1
    fi
    
    if [[ "$clean_db" == "true" ]]; then
        clean_database || exit 1
    fi
    
    if [[ "$criar_backup" == "true" ]]; then
        log "Criando backup..."
        if [[ -x "$SCRIPT_DIR/recovery_manager.sh" ]]; then
            "$SCRIPT_DIR/recovery_manager.sh" backup --type=full
        else
            warn "Script de recovery não encontrado"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}=== IMPORTAÇÃO B3 PORTAL INVESTIDOR ===${NC}"
    echo ""
    
    # Processar movimentações
    echo -e "${BLUE}Processando Movimentacoes:${NC}"
    if [[ "$dry_run" == "true" ]]; then
        analisar_arquivo "$arquivo_movimentacoes" "movimentacoes"
    else
        importar_arquivo "$arquivo_movimentacoes" "movimentacoes"
    fi
    
    echo ""
    
    # Processar negociações
    if [[ -n "$arquivo_negociacoes" ]]; then
        echo -e "${BLUE}Processando Negociacoes:${NC}"
        if [[ "$dry_run" == "true" ]]; then
            analisar_arquivo "$arquivo_negociacoes" "negociacoes"
        else
            importar_arquivo "$arquivo_negociacoes" "negociacoes"
        fi
    fi
    
    echo ""
    if [[ "$dry_run" == "true" ]]; then
        log "Análise concluída (modo dry-run)"
    else
        log "Importação concluída"
    fi
}

main "$@"
