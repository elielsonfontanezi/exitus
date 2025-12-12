#!/bin/bash
# TESTE ABRANGENTE EXITUS - M0 até M7.4

CONTAINER_NAME="exitus-backend"
echo "🔍 Verificando se o contêiner $CONTAINER_NAME está rodando..."

# O comando podman inspect retorna 0 se o contêiner existir e estiver em execução
# Usamos jq para extrair o estado de execução (Running: true)
if podman inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null | grep -q "true"; then
    echo "✅ Contêiner $CONTAINER_NAME está online e rodando."
else
    echo "❌ ERRO: O contêiner $CONTAINER_NAME NÃO está rodando."
    echo "Por favor, inicie-o antes de executar o teste."
    exit 1 # Sai do script com código de erro 1
fi

export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.data.access_token')

echo "🔹 M0 - INFRAESTRUTURA"
echo "✅ PostgreSQL:" && podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT COUNT(*) FROM usuarios;" | grep -E "^\s+[0-9]"
echo "✅ Backend UP:" && curl -s http://localhost:5000/health | jq -r '.status'
echo "✅ Frontend UP:" && curl -s http://localhost:8080/health | jq -r '.status' || echo "OK (se retornar erro, frontend pode estar sem /health)"

echo -e "\n🔹 M1 - DATABASE MODELS (12 tabelas)"
podman exec -it exitus-db psql -U exitus -d exitusdb -c "\dt" | grep -E "usuarios|corretoras|ativos|transacoes" | wc -l

echo -e "\n🔹 M2 - API REST CRUD"
echo "✅ Usuários:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/usuarios | jq '.data.total'
echo "✅ Corretoras:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/corretoras | jq '.data.total'
echo "✅ Ativos:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/ativos | jq '.data.total'
echo "✅ Transações:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/transacoes | jq '.data.total'

echo -e "\n🔹 M3 - ANALYTICS"
echo "✅ Posições:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/posicoes | jq '.data.total'
echo "✅ Proventos:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/proventos | jq '.data.total'
echo "✅ Portfolio Dashboard:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/portfolio/dashboard | jq '.data.patrimonio_total'

echo -e "\n🔹 M4 - BUY SIGNALS"
echo "✅ Signals PETR4:" && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5000/api/buy-signals/PETR4" | jq '.data.ticker'
echo "✅ Z-Score:" && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5000/api/buy-signals/PETR4/z-score" | jq '.data.z_score'

echo -e "\n🔹 M5 - FRONTEND BASE"
echo "✅ Templates HTMX:" && ls -1 frontend/app/templates/*.html 2>/dev/null | wc -l

echo -e "\n🔹 M6 - DASHBOARDS"
echo "✅ Sinais:" && ls frontend/app/templates/sinais*.html 2>/dev/null | wc -l
echo "✅ Portfolio:" && ls frontend/app/templates/portfolio*.html 2>/dev/null | wc -l

echo -e "\n🔹 M7.1-7.3 - RELATÓRIOS + ALERTAS"
echo "✅ Alertas:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/alertas | jq '.data | length'
echo "✅ Projeções:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/projecoes/renda | jq '.projecoes | length'
echo "✅ Performance:" && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5000/api/performance/performance?data_inicio=2025-01-01&data_fim=2025-12-31" | jq '.resultado_json.sharpe_ratio'
echo "✅ Relatórios (AuditoriaRelatorio):" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/relatorios/lista | jq '.total'

echo -e "\n🔹 M7.4 - NOVO ENDPOINT"
echo "✅ Portfolio Simple:" && curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/m7/portfolio | jq '.status'

echo -e "\n🔹 M7.5 - COTAÇÕES"
echo "✅ Cotação PETR4:" && curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:5000/api/cotacoes/PETR4" | jq '.data.ticker'

echo -e "\n🎉 RESUMO FINAL"
echo "Containers: $(podman ps --filter name=exitus --format '{{.Names}}' | wc -l)/3"
echo "Blueprints: $(podman logs exitus-backend 2>&1 | grep -c 'Blueprint.*registered')"
echo "DB Tabelas: $(podman exec -it exitus-db psql -U exitus -d exitusdb -tc '\dt' | grep -c 'public')"
echo "Relatórios: $(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/relatorios/lista | jq '.total')"
