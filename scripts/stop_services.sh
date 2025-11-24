#!/bin/bash
# Para todos os serviços do Exitus

echo "Parando serviços Exitus..."

podman stop exitus-frontend exitus-backend exitus-db

echo "=== Serviços parados! ==="
