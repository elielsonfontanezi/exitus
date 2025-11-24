#!/bin/bash
echo "======================================"
echo "  EXITUS - TESTES DO MÓDULO 0"
echo "======================================"
echo ""

echo "1. Backend Health Check (host):"
curl -s http://localhost:5000/health | python3 -m json.tool
echo ""

echo "2. Frontend Health Check (host):"
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""

echo "3. Frontend → Backend (interno):"
podman exec exitus-frontend python -c "import requests; r = requests.get('http://exitus-backend:5000/health'); print(r.json())"
echo ""

echo "4. Backend → Database (conexão):"
podman exec exitus-backend python -c "import socket; socket.create_connection(('exitus-db', 5432), timeout=5); print('✓ Conexão OK')"
echo ""

echo "5. PostgreSQL Query:"
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT version();" | head -3
echo ""

echo "6. Containers rodando:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "======================================"
echo "  TODOS OS TESTES CONCLUÍDOS!"
echo "======================================"
