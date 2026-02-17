#!/bin/bash
echo "🔄 Exitus Backend - Rebuild SEGURO (preserva banco)"

# 1. Libera a porta 5000 antes de começar (Evita o erro de 'bind')
sudo fuser -k 5000/tcp 2>/dev/null || true

# 2. Build com formato Docker e SEM cache para garantir as libs novas

# Para quando for preciso build sem cache
# cd backend && podman build --no-cache -t exitus-backend:latest . && cd ..

# Build normal
cd backend && podman build -t exitus-backend:latest . && cd ..

# 3. Para e remove o container antigo
podman stop exitus-backend 2>/dev/null
podman rm exitus-backend 2>/dev/null

# 4. Inicia o container 
podman run -d --name exitus-backend --network exitus-net -p 5000:5000 \
  -v $(pwd)/backend/app:/app/app \
  -v exitus-backend-logs:/app/logs \
  --env-file backend/.env \
	exitus-backend:latest

echo "⏳ Aguardando inicialização (15s)..."
sleep 15

# 5. Logs e Healthcheck
podman logs --tail 30 exitus-backend
curl -s http://localhost:5000/health || echo "❌ Healthcheck falhou"
