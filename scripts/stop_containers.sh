#!/bin/bash
# Para todos os serviços do Exitus

echo "Parando serviços Exitus..."

podman stop exitus-frontend exitus-backend exitus-db 2>/dev/null || true

echo "=== Serviços parados! ==="
