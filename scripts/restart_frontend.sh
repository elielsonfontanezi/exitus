#!/bin/bash
# Restart rápido do frontend (sem rebuild)

echo "Reiniciando exitus-frontend..."
echo .

echo "Parando exitus-frontend..."
podman stop exitus-frontend
sleep 5

echo "Iniciando exitus-frontend..."
podman start exitus-frontend
echo "Aguarde..."
sleep 10

echo ""
echo "Status:"
podman ps --filter name=exitus-frontend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Health check:"
curl -s http://localhost:8080/health | jq . || echo "Frontend ainda inicializando..."
