#!/bin/bash
echo "🔄 Exitus Backend - Rebuild SEGURO (preserva banco)"

# 1. Build SEM recriar banco
cd backend && podman build -t exitus-backend:latest . && cd ..

# 2. SÓ backend (preserva DB + Frontend)
podman stop exitus-backend
podman rm exitus-backend
podman run -d --name exitus-backend --network exitus-net -p 5000:5000 \
  -v $(pwd)/backend/app:/app/app \
  -v exitus-backend-logs:/app/logs \
  --env-file backend/.env exitus-backend:latest

sleep 15
podman logs --tail 30 exitus-backend
curl http://localhost:5000/health

sleep 10
