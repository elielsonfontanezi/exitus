#!/bin/bash
# Script unificado de gerenciamento do Exitus
# Uso: ./scripts/exitus.sh [comando] [alvo]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de help
show_help() {
    echo -e "${BLUE}Exitus - Script Unificado de Gerenciamento${NC}"
    echo ""
    echo "Uso: $0 [comando] [alvo]"
    echo ""
    echo "Comandos:"
    echo "  start     Inicia serviços"
    echo "  stop      Para serviços"
    echo "  restart   Reinicia serviços"
    echo "  rebuild   Rebuild containers"
    echo "  status    Status dos serviços"
    echo "  logs      Mostra logs"
    echo "  health    Health check"
    echo "  help      Mostra esta ajuda"
    echo ""
    echo "Alvos:"
    echo "  all       Todos os serviços (default)"
    echo "  backend   Apenas backend"
    echo "  frontend  Apenas frontend"
    echo "  db        Apenas banco"
    echo ""
    echo "Exemplos:"
    echo "  $0 start all           # Inicia tudo"
    echo "  $0 rebuild backend     # Rebuild backend"
    echo "  $0 restart frontend    # Restart frontend"
    echo "  $0 logs backend        # Logs do backend"
}

# Função de validação
check_container() {
    local container=$1
    if podman ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
        return 0
    else
        return 1
    fi
}

# Função de status
show_status() {
    echo -e "${BLUE}==================== STATUS ====================${NC}"
    podman ps --filter name=exitus --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${BLUE}==================== URLs ====================${NC}"
    echo "Backend:  http://localhost:5000"
    echo "Frontend: http://localhost:8080"
    echo ""
}

# Função de health check
health_check() {
    echo -e "${BLUE}==================== HEALTH CHECK ====================${NC}"
    
    # Backend
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        echo -e "Backend:  ${GREEN}✅ OK${NC}"
    else
        echo -e "Backend:  ${RED}❌ Falhou${NC}"
    fi
    
    # Frontend
    if curl -s http://localhost:8080 >/dev/null 2>&1; then
        echo -e "Frontend: ${GREEN}✅ OK${NC}"
    else
        echo -e "Frontend: ${RED}❌ Falhou${NC}"
    fi
    
    # Database
    if podman exec exitus-db pg_isready -U exitus >/dev/null 2>&1; then
        echo -e "Database: ${GREEN}✅ OK${NC}"
    else
        echo -e "Database: ${RED}❌ Falhou${NC}"
    fi
    echo ""
}

# Comando START
cmd_start() {
    local target=${1:-all}
    
    echo -e "${GREEN}==================== STARTING EXITUS ====================${NC}"
    echo "Alvo: $target"
    echo ""
    
    case $target in
        "all")
            echo -e "${YELLOW}[1/3]${NC} Iniciando PostgreSQL..."
            podman start exitus-db 2>/dev/null || echo "  ✓ PostgreSQL já estava rodando"
            sleep 3
            
            echo -e "${YELLOW}[2/3]${NC} Iniciando Backend..."
            podman start exitus-backend 2>/dev/null || echo "  ✓ Backend já estava rodando"
            sleep 3
            
            echo -e "${YELLOW}[3/3]${NC} Iniciando Frontend..."
            podman start exitus-frontend 2>/dev/null || echo "  ✓ Frontend já estava rodando"
            sleep 2
            ;;
        "backend")
            echo -e "${YELLOW}[1/1]${NC} Iniciando Backend..."
            podman start exitus-backend 2>/dev/null || echo "  ✓ Backend já estava rodando"
            sleep 3
            ;;
        "frontend")
            echo -e "${YELLOW}[1/1]${NC} Iniciando Frontend..."
            podman start exitus-frontend 2>/dev/null || echo "  ✓ Frontend já estava rodando"
            sleep 2
            ;;
        "db")
            echo -e "${YELLOW}[1/1]${NC} Iniciando PostgreSQL..."
            podman start exitus-db 2>/dev/null || echo "  ✓ PostgreSQL já estava rodando"
            sleep 3
            ;;
        *)
            echo -e "${RED}❌ Alvo inválido: $target${NC}"
            exit 1
            ;;
    esac
    
    show_status
}

# Comando STOP
cmd_stop() {
    local target=${1:-all}
    
    echo -e "${YELLOW}==================== STOPPING EXITUS ====================${NC}"
    echo "Alvo: $target"
    echo ""
    
    case $target in
        "all")
            echo -e "${YELLOW}[1/3]${NC} Parando Frontend..."
            podman stop exitus-frontend 2>/dev/null || echo "  ✓ Frontend já estava parado"
            
            echo -e "${YELLOW}[2/3]${NC} Parando Backend..."
            podman stop exitus-backend 2>/dev/null || echo "  ✓ Backend já estava parado"
            
            echo -e "${YELLOW}[3/3]${NC} Parando PostgreSQL..."
            podman stop exitus-db 2>/dev/null || echo "  ✓ PostgreSQL já estava parado"
            ;;
        "backend")
            echo -e "${YELLOW}[1/1]${NC} Parando Backend..."
            podman stop exitus-backend 2>/dev/null || echo "  ✓ Backend já estava parado"
            ;;
        "frontend")
            echo -e "${YELLOW}[1/1]${NC} Parando Frontend..."
            podman stop exitus-frontend 2>/dev/null || echo "  ✓ Frontend já estava parado"
            ;;
        "db")
            echo -e "${YELLOW}[1/1]${NC} Parando PostgreSQL..."
            podman stop exitus-db 2>/dev/null || echo "  ✓ PostgreSQL já estava parado"
            ;;
        *)
            echo -e "${RED}❌ Alvo inválido: $target${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✅ Serviços parados${NC}"
}

# Comando RESTART
cmd_restart() {
    local target=${1:-all}
    
    echo -e "${BLUE}==================== RESTARTING EXITUS ====================${NC}"
    echo "Alvo: $target"
    echo ""
    
    cmd_stop $target
    sleep 2
    cmd_start $target
}

# Comando REBUILD
cmd_rebuild() {
    local target=${1:-all}
    
    echo -e "${BLUE}==================== REBUILDING EXITUS ====================${NC}"
    echo "Alvo: $target"
    echo ""
    
    case $target in
        "backend")
            echo -e "${YELLOW}[1/4]${NC} Liberando porta 5000..."
            sudo fuser -k 5000/tcp 2>/dev/null || true
            
            echo -e "${YELLOW}[2/4]${NC} Build backend..."
            cd backend && podman build -t exitus-backend:latest . && cd ..
            
            echo -e "${YELLOW}[3/4]${NC} Removendo container antigo..."
            podman stop exitus-backend 2>/dev/null || true
            podman rm exitus-backend 2>/dev/null || true
            
            echo -e "${YELLOW}[4/4]${NC} Iniciando novo container..."
            podman run -d --name exitus-backend --network exitus-net -p 5000:5000 \
              -v ./backend:/app:Z \
              -v exitus-backend-logs:/app/logs:Z \
              --env-file backend/.env \
              exitus-backend:latest
              
            sleep 15
            ;;
        "frontend")
            echo -e "${YELLOW}[1/3]${NC} Parando container antigo..."
            podman stop exitus-frontend 2>/dev/null || true
            podman rm exitus-frontend 2>/dev/null || true
            
            echo -e "${YELLOW}[2/3]${NC} Build frontend..."
            cd frontend && podman build -t exitus-frontend:latest . && cd ..
            
            echo -e "${YELLOW}[3/3]${NC} Iniciando novo container..."
            podman run -d \
              --name exitus-frontend \
              --network exitus-net \
              -p 8080:8080 \
              -v ./frontend/app:/app/app:Z \
              -v exitus-frontend-logs:/app/logs:Z \
              --env-file ./frontend/.env \
              exitus-frontend:latest
              
            sleep 5
            ;;
        "all")
            cmd_rebuild backend
            cmd_rebuild frontend
            ;;
        *)
            echo -e "${RED}❌ Alvo inválido: $target${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✅ Rebuild concluído${NC}"
    show_status
}

# Comando LOGS
cmd_logs() {
    local target=${1:-all}
    
    case $target in
        "backend")
            echo -e "${BLUE}==================== BACKEND LOGS ====================${NC}"
            podman logs --tail 50 -f exitus-backend
            ;;
        "frontend")
            echo -e "${BLUE}==================== FRONTEND LOGS ====================${NC}"
            podman logs --tail 50 -f exitus-frontend
            ;;
        "db")
            echo -e "${BLUE}==================== DATABASE LOGS ====================${NC}"
            podman logs --tail 50 -f exitus-db
            ;;
        "all")
            echo -e "${RED}❌ Para logs, especifique o alvo: backend|frontend|db${NC}"
            exit 1
            ;;
        *)
            echo -e "${RED}❌ Alvo inválido: $target${NC}"
            exit 1
            ;;
    esac
}

# Main
case ${1:-help} in
    "start")
        cmd_start $2
        ;;
    "stop")
        cmd_stop $2
        ;;
    "restart")
        cmd_restart $2
        ;;
    "rebuild")
        cmd_rebuild $2
        ;;
    "status")
        show_status
        ;;
    "logs")
        cmd_logs $2
        ;;
    "health")
        health_check
        ;;
    "help"|*)
        show_help
        ;;
esac
