#!/bin/bash
echo "🧪 TESTES FASE 2.2.2 - CRUD DE CORRETORAS"
echo ""

# 1. Login usuário comum (joao.silva) - senha foi alterada para novasenha123
echo "1. Login USER (joao.silva)..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao.silva","password":"novasenha123"}')

USER_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    echo "❌ Erro ao obter token USER! Tentando senha antiga..."
    RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"joao.silva","password":"user123"}')
    USER_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
fi

echo "✅ Token USER obtido"
echo ""

# 2. Criar corretora BR
echo "2. POST /api/corretoras - Criar corretora XP (BR)..."
CORRETORA_XP=$(curl -s -X POST http://localhost:5000/api/corretoras \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "XP Investimentos",
    "tipo": "corretora",
    "pais": "BR",
    "moeda_padrao": "BRL",
    "saldo_atual": "10000.50",
    "observacoes": "Conta principal"
  }')

echo "$CORRETORA_XP" | python3 -m json.tool
XP_ID=$(echo "$CORRETORA_XP" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
echo ""

# 3. Criar exchange cripto
echo "3. POST /api/corretoras - Criar exchange Binance..."
curl -s -X POST http://localhost:5000/api/corretoras \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Binance",
    "tipo": "exchange",
    "pais": "US",
    "moeda_padrao": "USD",
    "saldo_atual": "5000.00",
    "observacoes": "Exchange de criptomoedas"
  }' | python3 -m json.tool
echo ""

# 4. Criar corretora US
echo "4. POST /api/corretoras - Criar Avenue (US)..."
curl -s -X POST http://localhost:5000/api/corretoras \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Avenue Securities",
    "tipo": "corretora",
    "pais": "US",
    "moeda_padrao": "USD",
    "saldo_atual": "2500.75"
  }' | python3 -m json.tool
echo ""

# 5. Listar todas as corretoras
echo "5. GET /api/corretoras - Listar todas corretoras do usuário..."
curl -s -X GET "http://localhost:5000/api/corretoras?page=1&per_page=10" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 6. Filtrar por tipo
echo "6. GET /api/corretoras?tipo=exchange - Filtrar exchanges..."
curl -s -X GET "http://localhost:5000/api/corretoras?tipo=exchange" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 7. Filtrar por país
echo "7. GET /api/corretoras?pais=BR - Filtrar por país BR..."
curl -s -X GET "http://localhost:5000/api/corretoras?pais=BR" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 8. Buscar por nome
echo "8. GET /api/corretoras?search=XP - Buscar 'XP'..."
curl -s -X GET "http://localhost:5000/api/corretoras?search=XP" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 9. Buscar corretora específica
if [ ! -z "$XP_ID" ]; then
    echo "9. GET /api/corretoras/{id} - Buscar XP por ID..."
    curl -s -X GET "http://localhost:5000/api/corretoras/$XP_ID" \
      -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
    echo ""
fi

# 10. Atualizar corretora
if [ ! -z "$XP_ID" ]; then
    echo "10. PUT /api/corretoras/{id} - Atualizar saldo XP..."
    curl -s -X PUT "http://localhost:5000/api/corretoras/$XP_ID" \
      -H "Authorization: Bearer $USER_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"saldo_atual": "15000.00", "observacoes": "Saldo atualizado"}' | python3 -m json.tool
    echo ""
fi

# 11. Saldo total em BRL
echo "11. GET /api/corretoras/saldo-total?moeda=BRL - Saldo total BRL..."
curl -s -X GET "http://localhost:5000/api/corretoras/saldo-total?moeda=BRL" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 12. Saldo total em USD
echo "12. GET /api/corretoras/saldo-total?moeda=USD - Saldo total USD..."
curl -s -X GET "http://localhost:5000/api/corretoras/saldo-total?moeda=USD" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 13. Tentar acessar corretora de outro usuário (admin)
echo "13. Login ADMIN..."
ADMIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ ! -z "$XP_ID" ] && [ ! -z "$ADMIN_TOKEN" ]; then
    echo "14. GET - ADMIN tentando acessar corretora do USER (deve falhar)..."
    curl -s -X GET "http://localhost:5000/api/corretoras/$XP_ID" \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
    echo ""
fi

echo "✅ Testes CRUD Corretoras concluídos!"
