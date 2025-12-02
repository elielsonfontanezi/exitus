#!/bin/bash
echo "🧪 TESTES FASE 2.2.4 - CRUD DE TRANSAÇÕES"
echo ""

# 1. Login USER
echo "1. Login USER (joao.silva)..."
RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao.silva","password":"user123"}')

USER_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('access_token', ''))" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    echo "❌ Falha ao obter token USER"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "✅ Token USER obtido: ${USER_TOKEN:0:20}..."
echo ""

# 2. Buscar corretora do USER
echo "2. GET /api/corretoras - Buscar corretora do USER..."
CORRETORAS=$(curl -s -X GET "http://localhost:5000/api/corretoras" \
  -H "Authorization: Bearer $USER_TOKEN")

CORRETORA_ID=$(echo "$CORRETORAS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('corretoras', [{}])[0].get('id', ''))" 2>/dev/null)

if [ -z "$CORRETORA_ID" ]; then
    echo "❌ Nenhuma corretora encontrada"
    echo "$CORRETORAS" | python3 -m json.tool
    exit 1
fi

echo "✅ Corretora ID: $CORRETORA_ID"
echo ""

# 3. Buscar ativo PETR4
echo "3. GET /api/ativos/ticker/PETR4?mercado=BR - Buscar PETR4..."
PETR4=$(curl -s -X GET "http://localhost:5000/api/ativos/ticker/PETR4?mercado=BR" \
  -H "Authorization: Bearer $USER_TOKEN")

PETR4_ID=$(echo "$PETR4" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)

if [ -z "$PETR4_ID" ]; then
    echo "❌ PETR4 não encontrado"
    echo "$PETR4" | python3 -m json.tool
    exit 1
fi

echo "✅ PETR4 ID: $PETR4_ID"
echo ""

# 4. Criar transação de COMPRA
echo "4. POST /api/transacoes - Criar COMPRA 100 PETR4 @ R\$ 38.50..."
COMPRA=$(curl -s -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"tipo\": \"compra\",
    \"ativo_id\": \"$PETR4_ID\",
    \"corretora_id\": \"$CORRETORA_ID\",
    \"data_transacao\": \"2025-12-01T10:30:00\",
    \"quantidade\": \"100\",
    \"preco_unitario\": \"38.50\",
    \"taxa_corretagem\": \"10.00\",
    \"emolumentos\": \"2.50\",
    \"imposto\": \"0.50\"
  }")

echo "$COMPRA" | python3 -m json.tool
COMPRA_ID=$(echo "$COMPRA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)
echo ""

# 5. Buscar ativo VALE3
echo "5. GET /api/ativos/ticker/VALE3?mercado=BR - Buscar VALE3..."
VALE3=$(curl -s -X GET "http://localhost:5000/api/ativos/ticker/VALE3?mercado=BR" \
  -H "Authorization: Bearer $USER_TOKEN")

VALE3_ID=$(echo "$VALE3" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('id', ''))" 2>/dev/null)
echo "✅ VALE3 ID: $VALE3_ID"
echo ""

# 6. Criar transação de COMPRA VALE3
echo "6. POST /api/transacoes - Criar COMPRA 50 VALE3 @ R\$ 62.80..."
curl -s -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"tipo\": \"compra\",
    \"ativo_id\": \"$VALE3_ID\",
    \"corretora_id\": \"$CORRETORA_ID\",
    \"data_transacao\": \"2025-12-02T14:00:00\",
    \"quantidade\": \"50\",
    \"preco_unitario\": \"62.80\",
    \"taxa_corretagem\": \"8.00\",
    \"emolumentos\": \"2.00\"
  }" | python3 -m json.tool
echo ""

# 7. Criar transação de VENDA
echo "7. POST /api/transacoes - Criar VENDA 30 PETR4 @ R\$ 39.20..."
curl -s -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"tipo\": \"venda\",
    \"ativo_id\": \"$PETR4_ID\",
    \"corretora_id\": \"$CORRETORA_ID\",
    \"data_transacao\": \"2025-12-02T15:30:00\",
    \"quantidade\": \"30\",
    \"preco_unitario\": \"39.20\",
    \"taxa_corretagem\": \"6.00\",
    \"emolumentos\": \"1.50\",
    \"imposto\": \"0.30\"
  }" | python3 -m json.tool
echo ""

# 8. Criar transação de DIVIDENDO
echo "8. POST /api/transacoes - Criar DIVIDENDO PETR4..."
curl -s -X POST http://localhost:5000/api/transacoes \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"tipo\": \"dividendo\",
    \"ativo_id\": \"$PETR4_ID\",
    \"corretora_id\": \"$CORRETORA_ID\",
    \"data_transacao\": \"2025-11-15T00:00:00\",
    \"quantidade\": \"100\",
    \"preco_unitario\": \"0.85\",
    \"observacoes\": \"Dividendos referentes a novembro/2025\"
  }" | python3 -m json.tool
echo ""

# 9. Listar todas as transações
echo "9. GET /api/transacoes - Listar todas transações..."
curl -s -X GET "http://localhost:5000/api/transacoes?page=1&per_page=10" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 10. Filtrar por tipo
echo "10. GET /api/transacoes?tipo=compra - Filtrar compras..."
curl -s -X GET "http://localhost:5000/api/transacoes?tipo=compra" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 11. Filtrar por ativo
if [ ! -z "$PETR4_ID" ]; then
    echo "11. GET /api/transacoes?ativo_id=PETR4_ID - Filtrar PETR4..."
    curl -s -X GET "http://localhost:5000/api/transacoes?ativo_id=$PETR4_ID" \
      -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
    echo ""
fi

# 12. Filtrar por período
echo "12. GET /api/transacoes?data_inicio=2025-12-01 - Filtrar dezembro..."
curl -s -X GET "http://localhost:5000/api/transacoes?data_inicio=2025-12-01T00:00:00" \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
echo ""

# 13. Buscar transação por ID
if [ ! -z "$COMPRA_ID" ]; then
    echo "13. GET /api/transacoes/{id} - Buscar compra PETR4..."
    curl -s -X GET "http://localhost:5000/api/transacoes/$COMPRA_ID" \
      -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
    echo ""
fi

# 14. Atualizar transação
if [ ! -z "$COMPRA_ID" ]; then
    echo "14. PUT /api/transacoes/{id} - Atualizar taxa corretagem..."
    curl -s -X PUT "http://localhost:5000/api/transacoes/$COMPRA_ID" \
      -H "Authorization: Bearer $USER_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"taxa_corretagem": "12.00"}' | python3 -m json.tool
    echo ""
fi

# 15. Resumo por ativo
if [ ! -z "$PETR4_ID" ]; then
    echo "15. GET /api/transacoes/resumo/{ativo_id} - Resumo PETR4..."
    curl -s -X GET "http://localhost:5000/api/transacoes/resumo/$PETR4_ID" \
      -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool
    echo ""
fi

echo "✅ Testes CRUD Transações concluídos!"
