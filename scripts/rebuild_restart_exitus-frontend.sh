#!/bin/bash
# -*- coding: utf-8 -*-
# Exitus - Rebuild e Restart do Container Frontend
# Módulo 5: Frontend Base + Autenticação

set -e

echo "========================================"
echo "  EXITUS - REBUILD FRONTEND CONTAINER  "
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Parar container se estiver rodando
echo -e "${YELLOW}[1/5]${NC} Parando container exitus-frontend..."
podman stop exitus-frontend 2>/dev/null || echo "Container já estava parado"

# 2. Remover container existente
echo -e "${YELLOW}[2/5]${NC} Removendo container antigo..."
podman rm exitus-frontend 2>/dev/null || echo "Container já foi removido"

# 3. Rebuild da imagem
echo -e "${YELLOW}[3/5]${NC} Rebuilding imagem exitus-frontend:latest..."
cd frontend
podman build -t exitus-frontend:latest .
cd ..

# 4. Recriar container com mount do código (hot reload)
echo -e "${YELLOW}[4/5]${NC} Criando novo container exitus-frontend..."
podman run -d \
  --name exitus-frontend \
  --network exitus-net \
  -p 8080:8080 \
  -v ./frontend/app:/app/app:Z \
  -v exitus-frontend-logs:/app/logs:Z \
  --env-file ./frontend/.env \
  exitus-frontend:latest

# 5. Aguardar container inicializar
echo -e "${YELLOW}[5/5]${NC} Aguardando container inicializar..."
sleep 5

# Verificar status
echo ""
echo "========================================"
echo "          STATUS DO CONTAINER           "
echo "========================================"
podman ps --filter name=exitus-frontend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health check
echo ""
echo "========================================"
echo "            HEALTH CHECK                "
echo "========================================"
sleep 2
if curl -f http://localhost:8080/health 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend está respondendo!${NC}"
else
    echo -e "${RED}✗ Frontend não está respondendo. Verificar logs:${NC}"
    echo "  podman logs exitus-frontend"
fi

echo ""
echo "========================================"
echo "              FINALIZADO                "
echo "========================================"
echo -e "${GREEN}Frontend URL:${NC} http://localhost:8080"
echo -e "${GREEN}Health Check:${NC} http://localhost:8080/health"
echo -e "${GREEN}Login Page:${NC} http://localhost:8080/auth/login"
echo ""
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  podman logs -f exitus-frontend        # Ver logs em tempo real"
echo "  podman exec -it exitus-frontend bash  # Acessar container"
echo "  podman restart exitus-frontend        # Restart rápido"
echo ""

sleep 10

podman logs --tail 30 exitus-frontend
