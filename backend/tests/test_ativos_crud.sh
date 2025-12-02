#!/bin/bash
echo "🧪 TESTES FASE 2.2.3 - CRUD DE ATIVOS"
echo ""

# 1. Login ADMIN
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

# 2. Criar ação brasileira
echo "2. POST /api/ativos - Criar PETR4 (Ação BR)..."
PETR4=$(curl -s -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "PETR4",
    "nome": "Petrobras PN",
    "tipo": "acao",
    "classe": "renda_variavel",
    "mercado": "BR",
    "moeda": "BRL",
    "preco_atual": "38.50",
    "dividend_yield": "12.5",
    "pl": "4.2",
    "pvp": "0.85",
    "roe": "18.3"
  }')

echo "$PETR4" | python3 -m json.tool
PETR4_ID=$(echo "$PETR4" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
echo ""

# 3. Criar FII
echo "3. POST /api/ativos - Criar HGLG11 (FII)..."
curl -s -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "HGLG11",
    "nome": "CSHG Logística FII",
    "tipo": "fii",
    "classe": "renda_variavel",
    "mercado": "BR",
    "moeda": "BRL",
    "preco_atual": "165.00",
    "dividend_yield": "10.2",
    "pvp": "0.98"
  }' | python3 -m json.tool
echo ""

# 4. Criar ação US
echo "4. POST /api/ativos - Criar AAPL (Ação US)..."
curl -s -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "nome": "Apple Inc",
    "tipo": "acao",
    "classe": "renda_variavel",
    "mercado": "US",
    "moeda": "USD",
    "preco_atual": "195.50",
    "dividend_yield": "0.5",
    "pl": "32.5",
    "pvp": "45.2",
    "roe": "147.5"
  }' | python3 -m json.tool
echo ""

# 5. Criar criptomoeda
echo "5. POST /api/ativos - Criar BTC (Cripto)..."
curl -s -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC",
    "nome": "Bitcoin",
    "tipo": "cripto",
    "classe": "cripto",
    "mercado": "CRIPTO",
    "moeda": "USD",
    "preco_atual": "43500.00"
  }' | python3 -m json.tool
echo ""

# 6. Listar todos os ativos
echo "6. GET /api/ativos - Listar todos ativos..."
curl -s -X GET "http://localhost:5000/api/ativos?page=1&per_page=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 7. Filtrar por tipo
echo "7. GET /api/ativos?tipo=acao - Filtrar ações..."
curl -s -X GET "http://localhost:5000/api/ativos?tipo=acao" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 8. Filtrar por mercado
echo "8. GET /api/ativos?mercado=BR - Filtrar mercado BR..."
curl -s -X GET "http://localhost:5000/api/ativos?mercado=BR" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 9. Buscar por ticker
echo "9. GET /api/ativos/ticker/PETR4?mercado=BR - Buscar PETR4..."
curl -s -X GET "http://localhost:5000/api/ativos/ticker/PETR4?mercado=BR" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 10. Buscar por nome
echo "10. GET /api/ativos?search=Petrobras - Buscar 'Petrobras'..."
curl -s -X GET "http://localhost:5000/api/ativos?search=Petrobras" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 11. Atualizar preço
if [ ! -z "$PETR4_ID" ]; then
    echo "11. PUT /api/ativos/{id} - Atualizar preço PETR4..."
    curl -s -X PUT "http://localhost:5000/api/ativos/$PETR4_ID" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"preco_atual": "39.75", "pl": "4.3"}' | python3 -m json.tool
    echo ""
fi

# 12. Listar ativos por mercado
echo "12. GET /api/ativos/mercado/BR - Ativos mercado BR..."
curl -s -X GET "http://localhost:5000/api/ativos/mercado/BR" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

# 13. Login USER
echo "13. Login USER (joao.silva)..."
USER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao.silva","password":"novasenha123"}')

USER_TOKEN=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    # Tentar senha antiga
    USER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"joao.silva","password":"user123"}')
    USER_TOKEN=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
fi

echo "✅ Token USER obtido"
echo ""

# 14. USER pode listar ativos (leitura pública)
echo "14. GET /api/ativos - USER listando ativos (deve funcionar)..."
curl -s -X GET "http://localhost:5000/api/ativos" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 15. USER tentar criar ativo (deve falhar 403)
echo "15. POST /api/ativos - USER tentando criar (deve falhar 403)..."
curl -s -X POST http://localhost:5000/api/ativos \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "VALE3",
    "nome": "Vale",
    "tipo": "acao",
    "classe": "renda_variavel",
    "mercado": "BR",
    "moeda": "BRL"
  }' | python3 -m json.tool
echo ""

echo "✅ Testes CRUD Ativos concluídos!"
