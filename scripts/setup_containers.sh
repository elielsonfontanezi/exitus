#!/bin/bash
# Configuração inicial dos containers do Exitus

set -e

# Remover containers existentes
echo "Removendo containers antigos (se existirem)..."
podman stop exitus-db  2>/dev/null || true
podman stop exitus-backend 2>/dev/null || true
podman stop exitus-frontend 2>/dev/null || true

podman rm exitus-db 2>/dev/null || true
podman rm exitus-backend 2>/dev/null || true
podman rm exitus-frontend 2>/dev/null || true

pkill -9 containers-rootlessport || true

echo "=== Setup Exitus - Módulo 0 ==="

# Criar network
echo "Criando network..."
podman network create exitus-net 2>/dev/null || echo "Network já existe"

# Criar volumes
echo "Criando volumes..."
podman volume create exitus-pgdata 2>/dev/null || echo "Volume pgdata já existe"
podman volume create exitus-backend-logs 2>/dev/null || echo "Volume backend-logs já existe"
podman volume create exitus-frontend-logs 2>/dev/null || echo "Volume frontend-logs já existe"

# Criar arquivos .env a partir dos exemplos (se não existirem)
echo "Criando arquivos .env..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ backend/.env criado a partir do .env.example"
else
    echo "✓ backend/.env já existe"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✓ frontend/.env criado a partir do .env.example"
else
    echo "✓ frontend/.env já existe"
fi

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
podman run -d --name exitus-db \
  --network exitus-net \
  -v exitus-pgdata:/var/lib/postgresql/data \
  -e POSTGRES_USER=exitus \
  -e POSTGRES_PASSWORD=exitus123 \
  -e POSTGRES_DB=exitusdb \
  -e TZ=America/Sao_Paulo \
  docker.io/postgres:15

echo "Aguardando PostgreSQL inicializar..."
sleep 10

# Criar container Backend (usando .env)
echo "Criando container Backend..."
podman run -d --name exitus-backend \
  --network exitus-net \
  -p 5000:5000 \
  -v ./backend:/app:Z \
  -v exitus-backend-logs:/app/logs:Z \
  --env-file ./backend/.env \
  exitus-backend:latest

# Criar container Frontend (usando .env)
echo "Criando container Frontend..."
podman run -d --name exitus-frontend \
  --network exitus-net \
  -p 8080:8080 \
  -v ./frontend:/app:Z \
  -v exitus-frontend-logs:/app/logs:Z \
  --env-file ./frontend/.env \
  exitus-frontend:latest

echo ""
echo "=== Setup concluído! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
sleep 20
podman ps
