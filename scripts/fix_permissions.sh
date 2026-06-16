#!/bin/bash
# Script para corrigir permissões dos containers Exitus
# Resolve problema de UID/GID entre Windows WSL e containers

set -e

echo "🔧 Exitus - Corrigindo Permissões dos Containers"
echo "=============================================="

# Obter UID/GID atual
USER_UID=$(id -u)
USER_GID=$(id -g)
echo "📊 UID/GID do usuário atual: $USER_UID:$USER_GID"

# Parar containers existentes
echo ""
echo "🛑 Parando containers existentes..."
podman stop exitus-backend 2>/dev/null || echo "Container backend não estava rodando"
podman stop exitus-frontend 2>/dev/null || echo "Container frontend não estava rodando"
podman stop exitus-db 2>/dev/null || echo "Container DB não estava rodando"

# Remover containers para recriar com novas configurações
echo ""
echo "🗑️ Removendo containers para recriação..."
podman rm exitus-backend 2>/dev/null || true
podman rm exitus-frontend 2>/dev/null || true

# Reconstruir imagens com novo Dockerfile
echo ""
echo "🏗️ Reconstruindo imagem backend (com suporte a UID/GID dinâmico)..."
cd backend
podman build -t exitus-backend:latest .
cd ..

echo ""
echo "🏗️ Reconstruindo imagem frontend..."
cd frontend
podman build -t exitus-frontend:latest .
cd ..

# Iniciar o banco (se não estiver rodando)
if ! podman ps -q -f name=exitus-db | grep -q .; then
    echo ""
    echo "🚀 Iniciando container PostgreSQL..."
    podman run -d --name exitus-db \
      --network exitus-net \
      -v exitus-pgdata:/var/lib/postgresql/data \
      -e POSTGRES_USER=exitus \
      -e POSTGRES_PASSWORD=exitus123 \
      -e POSTGRES_DB=exitusdb \
      -e TZ=America/Sao_Paulo \
      docker.io/postgres:16
    
    echo "⏳ Aguardando PostgreSQL inicializar..."
    sleep 10
else
    echo "✅ Container PostgreSQL já está rodando"
fi

# Criar container backend com UID/GID corretos
echo ""
echo "🚀 Criando container backend com UID/GID: $USER_UID:$USER_GID..."
podman run -d --name exitus-backend \
  --network exitus-net \
  -p 5000:5000 \
  -v ./backend:/app:Z \
  -v exitus-backend-logs:/app/logs:Z \
  --env-file ./backend/.env \
  -e USER_UID=$USER_UID \
  -e USER_GID=$USER_GID \
  exitus-backend:latest

# Criar container frontend com UID/GID corretos
echo ""
echo "🚀 Criando container frontend com UID/GID: $USER_UID:$USER_GID..."
podman run -d --name exitus-frontend \
  --network exitus-net \
  -p 8080:8080 \
  -v ./frontend:/app:Z \
  -v exitus-frontend-logs:/app/logs:Z \
  --env-file ./frontend/.env \
  -e USER_UID=$USER_UID \
  -e USER_GID=$USER_GID \
  exitus-frontend:latest

echo ""
echo "⏳ Aguardando containers inicializarem..."
sleep 15

echo ""
echo "📊 Status dos containers:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Permissões corrigidas!"
echo "📍 Backend: http://localhost:5000"
echo "📍 Frontend: http://localhost:8080"
echo ""
echo "🎯 Agora você pode editar arquivos no Windsurf/Windows"
echo "   e as permissões serão mantidas corretamente!"
