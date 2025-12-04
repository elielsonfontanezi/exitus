#!/bin/bash
# Restart rápido do frontend (sem rebuild)

echo "Reiniciando exitus-frontend..."
podman restart exitus-frontend

sleep 3

echo ""
echo "Status:"
podman ps --filter name=exitus-frontend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Health check:"
curl -s http://localhost:8080/health | jq . || echo "Frontend ainda inicializando..."
