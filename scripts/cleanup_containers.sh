#!/bin/bash
# Remove todos os containers, volumes do Exitus E mata processos órfãos na porta 5000

echo "=== Cleanup Exitus ==="

# --- 1. Limpeza de Contêineres ---

echo "Parando containers..."
podman stop exitus-frontend 2>/dev/null || true
podman stop exitus-backend 2>/dev/null || true
podman stop exitus-db 2>/dev/null || true

echo "Removendo containers..."
podman rm exitus-frontend 2>/dev/null || true
podman rm exitus-backend 2>/dev/null || true
podman rm exitus-db 2>/dev/null || true

echo "Containers removidos!"
echo ""

echo "Para remover também volumes e network, execute manualmente (cuidado!):"
echo "  podman volume rm exitus-pgdata exitus-backend-logs exitus-frontend-logs"
echo "  podman network rm exitus-net"
echo ""
