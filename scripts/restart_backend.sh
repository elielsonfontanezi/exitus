#!/bin/bash
# Restart rápido do backend (sem rebuild)

echo "Reiniciando exitus-backend..."
echo .

echo "Parando exitus-backend..."
podman stop exitus-backend
sleep 5

echo "Iniciando exitus-backend..."
podman start exitus-backend
echo "Aguarde..."
sleep 10

echo ""
echo "Status:"
podman ps --filter name=exitus-backend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Health check:"
curl -s http://localhost:5000/health | jq . || echo "Backend ainda inicializando..."
