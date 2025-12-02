#!/bin/bash
echo "🧪 TESTES DECORATORS - Fase 2.1.2"
echo ""

# 1. Fazer login e pegar tokens
echo "1. Login admin..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

# Extrair tokens usando python
ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['refresh_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Erro ao obter access_token!"
    echo "Resposta do servidor:"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "✅ Access Token obtido: ${ACCESS_TOKEN:0:30}..."
echo "✅ Refresh Token obtido: ${REFRESH_TOKEN:0:30}..."
echo ""

# 2. Teste /me COM token (deve funcionar)
echo "2. GET /api/auth/me COM token (deve funcionar)..."
curl -s -X GET "http://localhost:5000/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# 3. Teste /me SEM token (deve falhar 401)
echo "3. GET /api/auth/me SEM token (deve falhar)..."
curl -s -X GET http://localhost:5000/api/auth/me | python3 -m json.tool
echo ""

# 4. Teste /me/admin COM token ADMIN (deve funcionar)
echo "4. GET /api/auth/me/admin COM token ADMIN (deve funcionar)..."
curl -s -X GET "http://localhost:5000/api/auth/me/admin" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# 5. Teste refresh token
echo "5. POST /api/auth/refresh (renovar access_token)..."
curl -s -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN" | python3 -m json.tool
echo ""

# 6. Login com usuário comum (não admin)
echo "6. Login usuário comum (joao.silva)..."
RESPONSE_USER=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao.silva","password":"user123"}')

USER_TOKEN=$(echo "$RESPONSE_USER" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    echo "⚠️  Usuário joao.silva não disponível ou senha incorreta"
else
    echo "✅ Token USER obtido: ${USER_TOKEN:0:30}..."
    
    # 7. Teste /me/admin com USER (deve falhar 403)
    echo "7. GET /api/auth/me/admin COM token USER (deve falhar 403)..."
    curl -s -X GET "http://localhost:5000/api/auth/me/admin" \
      -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
    echo ""
fi

echo "✅ Testes decorators concluídos!"
