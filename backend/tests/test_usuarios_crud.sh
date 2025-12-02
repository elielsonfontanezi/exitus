#!/bin/bash
echo "🧪 TESTES FASE 2.2.1 - CRUD DE USUÁRIOS"
echo ""

# 1. Login ADMIN para obter token
echo "1. Login ADMIN..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

ADMIN_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Erro ao obter token ADMIN!"
    exit 1
fi
echo "✅ Token ADMIN obtido"
echo ""

# 2. Criar novo usuário
echo "2. POST /api/usuarios - Criar usuário 'teste.user'..."
curl -s -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste.user",
    "email": "teste@exitus.com",
    "password": "senha12345",
    "nome_completo": "Usuário de Teste",
    "role": "user"
  }' | python3 -m json.tool
echo ""

# 3. Listar usuários (admin only)
echo "3. GET /api/usuarios - Listar usuários (ADMIN)..."
curl -s -X GET "http://localhost:5000/api/usuarios?page=1&per_page=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 4. Buscar usuário específico
echo "4. GET /api/usuarios/{id} - Buscar admin (com token ADMIN)..."
ADMIN_ID="783c2bfd-9e36-4cbd-a4fb-901afae9fad3"
curl -s -X GET "http://localhost:5000/api/usuarios/$ADMIN_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 5. Login usuário comum
echo "5. Login usuário comum (joao.silva)..."
RESPONSE_USER=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao.silva","password":"user123"}')

USER_TOKEN=$(echo "$RESPONSE_USER" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
USER_ID=$(echo "$RESPONSE_USER" | python3 -c "import sys, json; import jwt; token=json.load(sys.stdin)['data']['access_token']; print(jwt.decode(token, options={'verify_signature': False})['sub'])" 2>/dev/null)

echo "✅ Token USER obtido (ID: $USER_ID)"
echo ""

# 6. Tentar listar usuários com USER (deve falhar 403)
echo "6. GET /api/usuarios - Tentar listar com USER (deve falhar 403)..."
curl -s -X GET http://localhost:5000/api/usuarios \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 7. Ver próprio perfil com USER (deve funcionar)
echo "7. GET /api/usuarios/{id} - USER vendo próprio perfil..."
curl -s -X GET "http://localhost:5000/api/usuarios/$USER_ID" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 8. Atualizar próprio perfil
echo "8. PUT /api/usuarios/{id} - USER atualizando próprio nome..."
curl -s -X PUT "http://localhost:5000/api/usuarios/$USER_ID" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome_completo": "João Silva Atualizado"}' | python3 -m json.tool
echo ""

# 9. Trocar senha
echo "9. PATCH /api/usuarios/{id}/password - Trocar senha..."
curl -s -X PATCH "http://localhost:5000/api/usuarios/$USER_ID/password" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password": "user123", "new_password": "novasenha123"}' | python3 -m json.tool
echo ""

# 10. Filtros e busca
echo "10. GET /api/usuarios?search=admin - Buscar por nome..."
curl -s -X GET "http://localhost:5000/api/usuarios?search=admin" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

echo "✅ Testes CRUD Usuários concluídos!"
