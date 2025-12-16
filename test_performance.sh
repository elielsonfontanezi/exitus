#!/bin/bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

echo "=== Benchmark de Performance ==="
echo ""

# Dashboard
echo "📊 Portfolio Dashboard:"
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/dashboard > /dev/null

# Buy Signals
echo "🎯 Buy Score PETR4:"
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/buy-signals/buy-score/PETR4 > /dev/null

# Cotações (com cache)
echo "💹 Cotação PETR4 (cache):"
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 > /dev/null

# Cotações (sem cache - primeira chamada)
echo "💹 Cotação AAPL (sem cache):"
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/AAPL > /dev/null
