#!/bin/bash
#
# Exitus - Reset e Seed Controlado
# Script wrapper para executar dentro do container
#

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de ajuda
show_help() {
    echo -e "${BLUE}🚀 EXITUS - Sistema de Seed Controlado${NC}"
    echo ""
    echo -e "${YELLOW}📋 FORMAS DE EXECUÇÃO:${NC}"
    echo ""
    echo -e "1️⃣ RESET + SEED BÁSICO:"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=minimal"
    echo -e "   → 3 usuários, 3 ativos, 2 corretoras"
    echo ""
    echo -e "2️⃣ RESET + SEED COMPLETO:"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=full"
    echo -e "   → 5 usuários, 35+ ativos, 5 corretoras"
    echo ""
    echo -e "3️⃣ APENAS USUÁRIOS:"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=usuarios"
    echo -e "   → 5 usuários completos"
    echo ""
    echo -e "4️⃣ APENAS ATIVOS:"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=ativos"
    echo -e "   → Ativos BR, US, EU"
    echo ""
    echo -e "5️⃣ LEGACY COMPLETO:"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=legacy"
    echo -e "   → Equivalente ao run_all_seeds.py antigo"
    echo ""
    echo -e "${YELLOW}🔄 BACKUP/RESTORE:${NC}"
    echo ""
    echo -e "6️⃣ BACKUP DO CENÁRIO ATUAL:"
    echo -e "   ./scripts/reset_and_seed.sh --backup meu_teste"
    echo ""
    echo -e "7️⃣ RESTAURAR CENÁRIO:"
    echo -e "   ./scripts/reset_and_seed.sh --restore meu_teste"
    echo ""
    echo -e "8️⃣ LISTAR CENÁRIOS:"
    echo -e "   ./scripts/reset_and_seed.sh --list-scenarios"
    echo ""
    echo -e "${YELLOW}🎯 COMPARAÇÃO COM LEGACY:${NC}"
    echo ""
    echo -e "❌ ANTIGO (múltiplos scripts):"
    echo -e "   python backend/app/seeds/run_all_seeds.py"
    echo -e "   python backend/app/seeds/seed_usuarios.py"
    echo -e "   python backend/app/seeds/seed_ativos_br.py"
    echo ""
    echo -e "✅ NOVO (único script):"
    echo -e "   ./scripts/reset_and_seed.sh --clean --seed-type=full"
    echo ""
    echo -e "${YELLOW}📊 TIPOS DE SEED:${NC}"
    echo -e "   minimal → Dados básicos para testes rápidos"
    echo -e "   full    → Todos os dados para desenvolvimento"
    echo -e "   usuarios→ Apenas usuários do sistema"
    echo -e "   ativos  → Apenas ativos (BR, US, EU)"
    echo -e "   legacy  → Equivalente ao sistema antigo"
    echo ""
    echo -e "${YELLOW}🔧 OPÇÕES:${NC}"
    echo -e "   --clean         → Reset completo do banco"
    echo -e "   --seed-type     → Tipo de seed (default: minimal)"
    echo -e "   --backup        → Nome do cenário para backup"
    echo -e "   --restore       → Nome do cenário para restaurar"
    echo -e "   --list-scenarios→ Listar cenários disponíveis"
    echo ""
    echo -e "${YELLOW}⚠️ IMPORTANTE:${NC}"
    echo -e "   - Execute na raiz do projeto"
    echo -e "   - --clean apaga TODOS os dados"
    echo -e "   - Backup salva estado atual para restore"
    echo -e "   - Legacy mantém compatibilidade total"
}

# Verificar se container está rodando
check_container() {
    if ! podman ps | grep -q "exitus-backend"; then
        echo -e "${RED}❌ Container exitus-backend não está rodando!${NC}"
        echo -e "${YELLOW}Execute primeiro:${NC} ./scripts/start_exitus.sh"
        exit 1
    fi
}

# Verificar se estamos na raiz do projeto
check_project_root() {
    if [[ ! -f "backend/app/__init__.py" ]] || [[ ! -d "scripts" ]]; then
        echo -e "${RED}❌ Execute este script na raiz do projeto Exitus!${NC}"
        exit 1
    fi
}

# Copiar script para container e executar
execute_in_container() {
    echo -e "${BLUE}🔄 Preparando execução no container...${NC}"
    
    # Copiar script para container
    podman cp scripts/reset_and_seed.py exitus-backend:/app/
    
    # Copiar seed_data para container
    if [[ -d "scripts/seed_data" ]]; then
        podman cp scripts/seed_data/ exitus-backend:/app/
    fi
    
    echo -e "${GREEN}✅ Arquivos copiados para o container${NC}"
    echo -e "${BLUE}🚀 Executando no container...${NC}"
    
    # Executar script no container
    podman exec -it exitus-backend python reset_and_seed.py "$@"
}

# Main
main() {
    check_project_root
    
    # Se não tiver argumentos ou pedir ajuda
    if [[ $# -eq 0 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Se pedir ajuda detalhada
    if [[ "$1" == "--help-examples" ]]; then
        check_container
        execute_in_container --help-examples
        exit 0
    fi
    
    # Verificar container
    check_container
    
    # Executar no container
    execute_in_container "$@"
}

# Executar main com todos os argumentos
main "$@"
