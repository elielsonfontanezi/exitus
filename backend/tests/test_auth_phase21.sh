#!/bin/bash
echo "🧪 TESTES FASE 2.1 - AUTENTICAÇÃO JWT"

# 1. Health check
echo "1. Health check..."
curl -s http://localhost:5000/health | python3 -m json.tool

# 2. Login admin (deve funcionar)
echo "2. Login admin..."
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -m json.tool

# 3. Login inválido (deve falhar)
echo "3. Login inválido..."
curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"invalido","password":"123"}' | python3 -m json.tool

# 4. /me sem token (deve falhar 401)
echo "4. /me sem token..."
curl -s -X GET http://localhost:5000/api/auth/me | python3 -m json.tool

echo "✅ Testes Fase 2.1 concluídos!"
