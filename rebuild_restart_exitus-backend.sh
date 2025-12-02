# 1. Substituir backend/app/models/usuario.py com o código acima

# 2. Rebuild
cd backend && podman build -t exitus-backend:latest . && cd ..

# 3. Restart
./scripts/setup_containers.sh 

# 4. Verificar status
podman ps

# 5. Verificar logs
podman logs --tail 50 exitus-backend
