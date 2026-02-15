#!/bin/bash
# Para todos os serviços do Exitus de forma ordenada

echo "===================="
echo "   STOPPING EXITUS  "
echo "===================="
echo ""

# Parar Frontend
echo "[1/3] Parando Frontend..."
podman stop exitus-frontend 2>/dev/null || echo "  ! Frontend já estava parado"

# Parar Backend
echo "[2/3] Parando Backend..."
podman stop exitus-backend 2>/dev/null || echo "  ! Backend já estava parado"

# Parar PostgreSQL
echo "[3/3] Parando PostgreSQL..."
podman stop exitus-db 2>/dev/null || echo "  ! PostgreSQL já estava parado"

echo ""
echo "===================="
echo "    STATUS FINAL    "
echo "===================="
podman ps --filter name=exitus --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Serviços encerrados com sucesso!"
