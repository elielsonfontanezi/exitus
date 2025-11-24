#!/bin/bash
# Configuração inicial dos containers do Exitus

set -e

# Remover containers existentes se houver
echo "Removendo containers antigos (se existirem)..."
podman stop exitus-db exitus-backend exitus-frontend 2>/dev/null || true
podman rm exitus-db exitus-backend exitus-frontend 2>/dev/null || true


echo "=== Setup Exitus - Módulo 0 ==="

# Criar network
echo "Criando network..."
podman network create exitus-net 2>/dev/null || echo "Network já existe"

# Criar volumes
echo "Criando volumes..."
podman volume create exitus-pgdata 2>/dev/null || echo "Volume pgdata já existe"
podman volume create exitus-backend-logs 2>/dev/null || echo "Volume backend-logs já existe"
podman volume create exitus-frontend-logs 2>/dev/null || echo "Volume frontend-logs já existe"

# Build das imagens
echo "Building backend image..."
cd backend
podman build -t exitus-backend:latest .
cd ..

echo "Building frontend image..."
cd frontend
podman build -t exitus-frontend:latest .
cd ..

# Criar container PostgreSQL
echo "Criando container PostgreSQL..."
podman run -d --name exitus-db   --network exitus-net   -v exitus-pgdata:/var/lib/postgresql/data   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   docker.io/postgres:15

echo "Aguardando PostgreSQL inicializar..."
sleep 10

# Criar container Backend
echo "Criando container Backend..."
podman run -d --name exitus-backend   --network exitus-net   -p 5000:5000   -v ./backend:/app:Z   -v exitus-backend-logs:/app/logs:Z   -e POSTGRES_HOST=exitus-db   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   exitus-backend:latest

# Criar container Frontend
echo "Criando container Frontend..."
podman run -d --name exitus-frontend   --network exitus-net   -p 8080:8080   -v ./frontend:/app:Z   -v exitus-frontend-logs:/app/logs:Z   -e BACKEND_API_URL=http://exitus-backend:5000   -e TZ=America/Sao_Paulo   exitus-frontend:latest

echo ""
echo "=== Setup concluído! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
