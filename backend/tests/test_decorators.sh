#!/bin/bash
echo "🧪 TESTES DECORATORS - Fase 2.1.2"

# 1. Fazer login e pegar token
echo "1. Login admin..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

ACCESS_TOKEN=$(echo $RESPONSE | python3 -m json.tool | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Token obtido: ${ACCESS_TOKEN:0:30}..."

# 2. Teste /me COM token (deve funcionar)
echo "2. /me COM token..."
curl -s -X GET "http://localhost:5000/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 3. Teste /me SEM token (deve falhar 401)
echo "3. /me SEM token..."
curl -s -X GET http://localhost:5000/api/auth/me | python3 -m json.tool

# 4. Teste refresh token
echo "4. Refresh token..."
REFRESH_TOKEN=$(echo $RESPONSE | python3 -m json.tool | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)
curl -s -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN" | python3 -m json.tool

echo "✅ Testes decorators concluídos!"
