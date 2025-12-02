#!/bin/bash
# Inicia todos os serviços do Exitus

echo "Iniciando serviços Exitus..."

podman start exitus-db || true
echo "PostgreSQL iniciado"
sleep 5

podman start exitus-backend || true
echo "Backend iniciado"

podman start exitus-frontend || true
echo "Frontend iniciado"

echo ""
echo "=== Serviços iniciados! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
