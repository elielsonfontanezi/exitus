#!/bin/bash
# Inicia todos os serviços do Exitus

echo "===================="
echo "  STARTING EXITUS   "
echo "===================="
echo ""

# Iniciar PostgreSQL
echo "[1/3] Iniciando PostgreSQL..."
podman start exitus-db 2>/dev/null || echo "  ✓ PostgreSQL já estava rodando"
sleep 3

# Iniciar Backend
echo "[2/3] Iniciando Backend..."
podman start exitus-backend 2>/dev/null || echo "  ✓ Backend já estava rodando"
sleep 3

# Iniciar Frontend
echo "[3/3] Iniciando Frontend..."
podman start exitus-frontend 2>/dev/null || echo "  ✓ Frontend já estava rodando"
sleep 2

echo ""
echo "===================="
echo "  STATUS SERVICES   "
echo "===================="
podman ps --filter name=exitus --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "===================="
echo "    ACCESS URLs     "
echo "===================="
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
