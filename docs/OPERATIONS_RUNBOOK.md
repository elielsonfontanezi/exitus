
# ⚙️ Operations Runbook - Exitus v0.7.5

**Objetivo**: Guia rápido para subir/manter/resolver problemas no ambiente dev/prod.

## Comandos Essenciais (Podman)

### Subir Ambiente Completo
```bash
# Build + up todos (5min primeira vez)
./scripts/rebuild-restart-exitus-backend.sh
./scripts/rebuild-restart-exitus-frontend.sh
podman-compose up -d  # ou podman-compose.yml

# Verificar
podman ps | grep exitus
# exitus-db, backend:5000, frontend:8080 todos 'Up'
```

### Seeds + Dados Iniciais
```bash
podman exec -it exitus-backend bash -c "
  cd /app && 
  python -c 'from app.seeds import seed_all; seed_all()'
"
# Cria: admin user, 17 ativos, 2 depósitos XP R$5k, 4 alertas
```

### Health Checks
```bash
curl localhost:5000/health    # Backend: {"status":"ok","module":"M4+Alertas ✅"}
curl localhost:8080/health    # Frontend: {"status":"ok"}
curl -H "Authorization: Bearer $TOKEN" localhost:5000/api/relatorios/lista | jq '.total'  # 15+
```

## Reset Completo (5min)

```bash
# 1. Parar tudo
podman-compose down -v

# 2. Remover volumes (perde dados!)
podman volume rm exitus-db-data  # ATENÇÃO!

# 3. Rebuild + seeds
./scripts/rebuild-restart-exitus-backend.sh
./scripts/rebuild-restart-exitus-frontend.sh
# Auto-seeds rodam
```

## Playbooks de Incidentes (Top 8)

### 1. **API 400 "data_inicio obrigatória"** (Relatórios)
```
ERRO: POST /api/relatorios/gerar sem data_inicio/data_fim
FIX: Usar snake_case: {"data_inicio": "2026-01-01", "data_fim": "2026-01-31"}
```

### 2. **Backend Offline (Connection Refused :5000)**
```
VER: podman logs exitus-backend --tail 20
FIX: podman restart exitus-backend
Se persistir: ./scripts/rebuild-restart-exitus-backend.sh
```

### 3. **Frontend carrega mock (não dados reais)**
```
CAUSA: Backend offline ou token expirado
FIX: 
1. TOKEN=$(curl -s -X POST localhost:5000/api/auth/login -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')
2. Ver DevTools Network → 200 em /api/portfolios?
```

### 4. **Migration "relation does not exist"**
```
FIX:
podman exec exitus-backend alembic upgrade head
podman exec exitus-backend python -c 'from app.seeds import seed_all; seed_all()'
```

### 5. **Token Expirado (401 Unauthorized)**
```
NOVO TOKEN:
export TOKEN=$(curl -s -X POST localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')
```

### 6. **Porta 5000/8080 em uso**
```
VER: sudo lsof -i :5000
KILL: podman stop/rm exitus-backend
RESTART: ./scripts/rebuild-restart-exitus-backend.sh
```

### 7. **Logs em Tempo Real**
```bash
podman logs -f exitus-backend  # Backend
podman logs -f exitus-frontend # Frontend
```

### 8. **Teste End-to-End Rápido**
```bash
# Login + Portfolio + Relatório
TOKEN=...  # acima
curl -H "Authorization: Bearer $TOKEN" localhost:5000/api/portfolios/dashboard | jq '.total_patrimonio'
curl -H "Authorization: Bearer $TOKEN" localhost:5000/api/relatorios/gerar \\
  -H "Content-Type: application/json" \\
  -d '{"tipo":"PERFORMANCE","data_inicio":"2026-01-01","data_fim":"2026-01-31"}' | jq '.id'
```

## Checklist Diário de Saúde

- [ ] `podman ps` → 3 containers Up
- [ ] Backend health → "M4 - Buy Signals + Alertas ✅"
- [ ] Frontend health → "ok"
- [ ] Login → Dashboard carrega (sem mock)
- [ ] Relatórios lista → total 15+
- [ ] Alertas → Toggle PETR4 funciona

## Backup/Export

```bash
# DB dump
podman exec exitus-db pg_dump -U exitus exitusdb > backup_$(date +%Y%m%d).sql

# Relatórios (futuro M8)
# curl /api/relatorios/{id}/export?format=csv
```

---
**Geração**: Perplexity AI | **Base**: TROUBLESHOOTING_GUIDE + validações M4-M7 | **Próximo**: CHANGELOG_MODULOS.md
