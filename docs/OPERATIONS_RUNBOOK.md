# Operations Runbook - Sistema Exitus

## 📋 Índice

- [Instalação e Setup](#instalação-e-setup)
- [Operações do Dia a Dia](#operações-do-dia-a-dia)
- [Manutenção do Database](#manutenção-do-database)
- [Testes e Validação](#testes-e-validação)
- [Monitoramento](#monitoramento)
- [Troubleshooting](#troubleshooting)
- [Scripts Úteis](#scripts-úteis)
- [Backup e Recovery](#backup-e-recovery)

---

## Instalação e Setup

### Requisitos de Sistema

**Hardware Mínimo**:
- CPU: 2 cores
- RAM: 8GB
- Disco: 10GB disponíveis
- Rede: Conexão internet estável

**Software**:
- Ubuntu 22.04 LTS (ou compatível)
- Podman 4.x
- Git 2.x
- curl, jq (ferramentas CLI)

---

### Instalação do Podman

#### Ubuntu/Debian

```bash
# Atualizar repositórios
sudo apt update

# Instalar Podman
sudo apt install -y podman

# Verificar instalação
podman --version
# Output: podman version 4.3.1

# Habilitar rootless (se necessário)
sudo usermod -aG podman $USER
newgrp podman
```

#### Configuração Rootless

```bash
# Verificar subuid/subgid
grep $USER /etc/subuid
grep $USER /etc/subgid

# Se não existir, adicionar:
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid

# Reiniciar user session
podman system migrate
```

---

### Clone do Repositório

```bash
# Clone via HTTPS
git clone https://github.com/elielsonfontanezi/exitus.git
cd exitus

# Ou via SSH (requer chave configurada)
git clone git@github.com:elielsonfontanezi/exitus.git
cd exitus

# Verificar branch
git branch
# * main

# Listar arquivos principais
ls -la
# .env.example
# README.md
# backend/
# frontend/
# scripts/
# docs/
```

---

### Configuração de Variáveis (.env)

#### 1. Copiar Arquivo de Exemplo

```bash
cp .env.example .env
```

#### 2. Editar Variáveis

```bash
nano .env
```

**Conteúdo Mínimo**:

```bash
# Database Configuration
POSTGRES_USER=exitus
POSTGRES_PASSWORD=sua_senha_segura_aqui
POSTGRES_DB=exitus_db
POSTGRES_HOST=exitus-db
POSTGRES_PORT=5432

# Flask Backend
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=chave_secreta_256_bits_aqui
JWT_SECRET_KEY=chave_jwt_256_bits_aqui

# Flask Frontend
FLASK_FRONTEND_PORT=8080
BACKEND_API_URL=http://exitus-backend:5000

# APIs de Cotações (Opcional - M7.5)
BRAPI_TOKEN=seu_token_premium_aqui
ALPHAVANTAGE_TOKEN=seu_token_aqui
FINNHUB_TOKEN=seu_token_aqui
POLYGON_TOKEN=seu_token_aqui  # Opcional

# Timezone
TZ=America/Sao_Paulo
```

**⚠️ IMPORTANTE**:
- Nunca commite `.env` no Git (já está no `.gitignore`)
- Use senhas fortes (mínimo 16 caracteres)
- Gere chaves secretas aleatórias:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```

---

### Build dos Containers

#### 1. Build das Imagens

```bash
# Build backend
cd backend
podman build -t exitus-backend:latest .

# Build frontend
cd ../frontend
podman build -t exitus-frontend:latest .

# Voltar para raiz
cd ..
```

#### 2. Criar Rede Bridge

```bash
podman network create exitus-net
```

#### 3. Criar Volumes Persistentes

```bash
mkdir -p volumes/postgres
mkdir -p volumes/data
```

#### 4. Iniciar PostgreSQL

```bash
podman run -d \
  --name exitus-db \
  --network exitus-net \
  -e POSTGRES_USER=exitus \
  -e POSTGRES_PASSWORD=sua_senha \
  -e POSTGRES_DB=exitus_db \
  -e TZ=America/Sao_Paulo \
  -v ./volumes/postgres:/var/lib/postgresql/data:Z \
  -p 5432:5432 \
  postgres:16

# Aguardar 10 segundos para inicialização
sleep 10
```

#### 5. Iniciar Backend

```bash
podman run -d \
  --name exitus-backend \
  --network exitus-net \
  --env-file .env \
  -v ./backend:/app:Z \
  -p 5000:5000 \
  exitus-backend:latest
```

#### 6. Iniciar Frontend

```bash
podman run -d \
  --name exitus-frontend \
  --network exitus-net \
  --env-file .env \
  -v ./frontend:/app:Z \
  -p 8080:8080 \
  exitus-frontend:latest
```

#### 7. Verificar Status

```bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Output esperado:
# NAMES              STATUS          PORTS
# exitus-db          Up 2 minutes    0.0.0.0:5432->5432/tcp
# exitus-backend     Up 1 minute     0.0.0.0:5000->5000/tcp
# exitus-frontend    Up 30 seconds   0.0.0.0:8080->8080/tcp
```

---

### Scripts de Automação

#### Usar Scripts Prontos

```bash
# Iniciar todos os containers
./scripts/start_exitus.sh

# Parar todos
./scripts/stop_exitus.sh

# Restart completo
./scripts/restart_exitus.sh

# Rebuild + Restart backend
./scripts/rebuild_restart_exitus-backend.sh

# Rebuild + Restart frontend
./scripts/rebuild_restart_exitus-frontend.sh
```

---

## Operações do Dia a Dia

### Iniciar o Sistema

```bash
# Opção 1: Via script
./scripts/start_exitus.sh

# Opção 2: Manual (ordem importa)
podman start exitus-db
sleep 5
podman start exitus-backend
podman start exitus-frontend

# Verificar logs
podman logs -f exitus-backend
```

**Health Checks**:
```bash
# Backend
curl http://localhost:5000/health
# {"status":"ok","env":"development","module":"M4 - Buy Signals & Fiscais"}

# Frontend
curl http://localhost:8080/health
# {"status":"ok","service":"exitus-frontend"}
```

---

### Parar o Sistema

```bash
# Opção 1: Via script
./scripts/stop_exitus.sh

# Opção 2: Manual
podman stop exitus-frontend
podman stop exitus-backend
podman stop exitus-db

# Força parada (se travado)
podman kill exitus-backend
```

---

### Restart

```bash
# Restart individual
podman restart exitus-backend

# Restart todos
./scripts/restart_exitus.sh

# Restart com rebuild (após mudanças no código)
./scripts/rebuild_restart_exitus-backend.sh
```

---

### Ver Logs

#### Logs em Tempo Real

```bash
# Backend
podman logs -f exitus-backend

# Frontend
podman logs -f exitus-frontend

# Database
podman logs -f exitus-db

# Últimas 100 linhas
podman logs --tail 100 exitus-backend
```

#### Filtrar Logs

```bash
# Apenas erros (ERROR)
podman logs exitus-backend 2>&1 | grep ERROR

# Últimas 24 horas
podman logs --since 24h exitus-backend

# Entre timestamps
podman logs --since 2026-01-06T10:00:00 --until 2026-01-06T12:00:00 exitus-backend
```

---

### Acessar Container (Shell)

```bash
# Backend
podman exec -it exitus-backend bash

# Uma vez dentro:
whoami  # exitus (non-root)
ls -la /app
python3 --version  # Python 3.11.x
flask --version    # Flask 3.0.x

# Sair
exit

# Executar comando único (sem entrar)
podman exec exitus-backend python3 -c "print('Hello')"
```

---

## Manutenção do Database

### Executar Migrations

#### Aplicar Migrations Pendentes

```bash
# Acessar backend container
podman exec -it exitus-backend bash

# Dentro do container
cd /app
flask db upgrade

# Output esperado:
# INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 001 -> 007_add_reports
# INFO  [alembic.runtime.migration] Running upgrade 007 -> 008_add_historico_preco
```

#### Criar Nova Migration

```bash
# Após modificar models em app/models/
flask db migrate -m "Descrição da mudança"

# Exemplo
flask db migrate -m "Adicionar coluna email_verificado em usuario"

# Verificar migration criada
ls migrations/versions/
```

#### Rollback de Migration

```bash
# Voltar 1 migration
flask db downgrade

# Voltar para versão específica
flask db downgrade 007_add_reports

# Voltar tudo (CUIDADO!)
flask db downgrade base
```

---

### Backup Manual

#### Backup Completo do Database

```bash
# Dump via pg_dump
podman exec exitus-db pg_dump -U exitus exitus_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Exemplo de output:
# backup_20260107_101500.sql (12.5 MB)

# Verificar conteúdo
head -20 backup_20260107_101500.sql
```

#### Backup Apenas Dados (sem schema)

```bash
podman exec exitus-db pg_dump -U exitus --data-only exitus_db > data_only_backup.sql
```

#### Backup de Tabela Específica

```bash
podman exec exitus-db pg_dump -U exitus -t transacao exitus_db > transacao_backup.sql
```

---

### Restore de Backup

```bash
# Parar backend (evitar conflitos)
podman stop exitus-backend

# Restore
podman exec -i exitus-db psql -U exitus exitus_db < backup_20260107_101500.sql

# Reiniciar backend
podman start exitus-backend

# Verificar logs
podman logs -f exitus-backend
```

---

### Popular Histórico de Preços

#### Script Automático (M7.6)

```bash
# Popular ticker específico (últimos 252 dias = 1 ano trading)
podman exec -it exitus-backend \
  python3 app/scripts/popular_historico_inicial.py \
  --ticker PETR4 --dias 252

# Popular todos os ativos em posições
podman exec -it exitus-backend \
  python3 app/scripts/popular_historico_inicial.py \
  --dias 252

# Incluir ativos deslistados
podman exec -it exitus-backend \
  python3 app/scripts/popular_historico_inicial.py \
  --incluir-deslistados --dias 365

# Output esperado:
# [INFO] Iniciando população de histórico de preços...
# [INFO] Processando PETR4 (1/17)...
# [OK] PETR4: 252 registros inseridos
# [INFO] Processando VALE3 (2/17)...
# [OK] VALE3: 252 registros inseridos
# ...
# [INFO] Resumo: 17 ativos processados, 15 sucesso, 2 falhas
```

---

## Testes e Validação

### Rodar Testes Unitários

```bash
# Acessar backend
podman exec -it exitus-backend bash

# Rodar todos os testes
pytest tests/ -v

# Rodar testes de um módulo específico
pytest tests/test_portfolio_service.py -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Ver relatório de cobertura
# Abrir htmlcov/index.html no navegador
```

---

### Testes de Integração

#### Teste Manual de Endpoints

**1. Obter Token JWT**:
```bash
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

echo "Token: $TOKEN"
```

**2. Testar Endpoint de Portfolio**:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/dashboard | jq .
```

**3. Testar Buy Score**:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/buy-signals/buy-score/PETR4 | jq .
```

**4. Testar Cotação**:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/cotacoes/PETR4 | jq .
```

---

### Teste de Performance

#### Benchmark de Endpoints

**Script**:
```bash
#!/bin/bash
# test_performance.sh

TOKEN="seu_token_aqui"
ENDPOINT="http://localhost:5000/api/portfolio/dashboard"

echo "Benchmark: $ENDPOINT"
echo "Requests: 100"
echo "Concorrência: 10"
echo ""

time for i in {1..100}; do
  curl -s -H "Authorization: Bearer $TOKEN" "$ENDPOINT" > /dev/null &
  if [ $(($i % 10)) -eq 0 ]; then
    wait
  fi
done
wait

echo "Concluído!"
```

**Executar**:
```bash
chmod +x test_performance.sh
./test_performance.sh
```

**Output esperado**:
```
Benchmark: http://localhost:5000/api/portfolio/dashboard
Requests: 100
Concorrência: 10

real    0m8.234s
user    0m1.023s
sys     0m0.456s
Concluído!
```

**Análise**:
- 100 requests em 8.2s = **12 req/s**
- Response time médio: **~820ms**

---

### Teste de Stress

```bash
# Instalar Apache Bench (se não tiver)
sudo apt install apache2-utils

# Teste de stress (1000 requests, 50 concurrent)
ab -n 1000 -c 50 -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/dashboard

# Output:
# Requests per second:    15.23 [#/sec] (mean)
# Time per request:       65.789 [ms] (mean)
# Transfer rate:          125.45 [Kbytes/sec] received
```

---

## Monitoramento

### Health Checks

#### Verificação Automática (a cada 30s)

Os containers têm healthchecks configurados:

```bash
# Ver status de saúde
podman ps --format "table {{.Names}}\t{{.Status}}"

# Output:
# exitus-backend    Up 2 hours (healthy)
# exitus-frontend   Up 2 hours (healthy)
# exitus-db         Up 2 hours (healthy)
```

#### Verificação Manual

```bash
# Backend
curl -f http://localhost:5000/health || echo "BACKEND DOWN"

# Frontend
curl -f http://localhost:8080/health || echo "FRONTEND DOWN"

# Database (via psql)
podman exec exitus-db psql -U exitus -d exitus_db -c "SELECT 1;"
```

---

### Métricas de Performance

#### Response Time

```bash
# Medir response time de endpoint
time curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/portfolio/dashboard > /dev/null

# Output:
# real    0m0.234s  ← Response time total
```

#### Cache Hit Rate (Cotações)

```bash
# Verificar logs de cotações
podman logs exitus-backend | grep "cotacoes" | tail -50

# Procurar por:
# [INFO] cotacoes: cache HIT - PETR4 (age: 5min)
# [INFO] cotacoes: cache MISS - VALE3, chamando brapi.dev

# Calcular hit rate:
# HIT / (HIT + MISS) * 100
```

#### Database Connections

```bash
# Ver conexões ativas
podman exec exitus-db psql -U exitus -d exitus_db -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname='exitus_db';"

# Output:
#  count
# -------
#      5
```

---

### Logs de Erro

#### Coletar Erros Recentes

```bash
# Últimos erros do backend (últimas 24h)
podman logs --since 24h exitus-backend 2>&1 | grep -i error > erros_backend.log

# Ver resumo
cat erros_backend.log | cut -d' ' -f4- | sort | uniq -c | sort -rn
```

---

## Troubleshooting

### Container não sobe

#### Problema 1: Porta já em uso

**Sintoma**:
```
Error: cannot listen on the TCP port: listen tcp 0.0.0.0:5000: bind: address already in use
```

**Solução**:
```bash
# Descobrir processo usando a porta
sudo lsof -i :5000

# Matar processo
sudo kill -9 <PID>

# Ou usar porta alternativa
podman run -p 5001:5000 ...
```

#### Problema 2: Imagem não encontrada

**Sintoma**:
```
Error: exitus-backend:latest: image not found
```

**Solução**:
```bash
# Rebuild da imagem
cd backend
podman build -t exitus-backend:latest .
```

#### Problema 3: Network não existe

**Sintoma**:
```
Error: network exitus-net not found
```

**Solução**:
```bash
podman network create exitus-net
```

---

### Erro de conexão PostgreSQL

#### Problema: Backend não conecta ao DB

**Sintoma nos logs**:
```
FATAL: password authentication failed for user "exitus"
```

**Diagnóstico**:
```bash
# 1. Verificar se DB está rodando
podman ps | grep exitus-db

# 2. Testar conexão manual
podman exec -it exitus-db psql -U exitus -d exitus_db

# 3. Verificar variáveis de ambiente
podman exec exitus-backend env | grep POSTGRES
```

**Solução**:
```bash
# Recriar DB com senha correta
podman stop exitus-db
podman rm exitus-db
rm -rf volumes/postgres/*

# Iniciar novamente com .env correto
./scripts/start_exitus.sh
```

---

### Token JWT expirado

**Sintoma**:
```json
{
  "error": "Token has expired",
  "statuscode": 401
}
```

**Solução Rápida**:
```bash
# Gerar novo token
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')
```

**Solução Permanente (M8)**:
- Implementar refresh tokens
- Aumentar expiry para 24h (desenvolvimento)

---

### API de cotação falhando

#### Problema: Todas APIs retornando erro

**Sintoma**:
```json
{
  "ticker": "PETR4",
  "success": false,
  "error": "Todas as fontes de dados falharam"
}
```

**Diagnóstico**:
```bash
# 1. Testar conexão internet
curl -I https://brapi.dev

# 2. Verificar tokens no .env
podman exec exitus-backend env | grep TOKEN

# 3. Testar API diretamente
curl "https://brapi.dev/api/quote/PETR4?token=SEU_TOKEN"
```

**Solução**:
- Verificar saldo de requests do dia (Alpha Vantage: 500/dia)
- Aguardar reset (00:00 UTC)
- Usar cache local (último preço conhecido)

---

### Performance degradada

**Sintoma**: Response times > 5s

**Diagnóstico**:
```bash
# 1. Verificar CPU/RAM
podman stats exitus-backend

# Output:
# CONTAINER      CPU %   MEM USAGE / LIMIT   NET I/O
# exitus-backend 45.2%   512MB / 2GB         1.2MB/3.4MB

# 2. Verificar queries lentas no PostgreSQL
podman exec exitus-db psql -U exitus -d exitus_db -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 3. Ver conexões DB
podman exec exitus-db psql -U exitus -d exitus_db -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

**Soluções**:
- Aumentar Gunicorn workers (editar Dockerfile)
- Adicionar índices em queries lentas
- Implementar Redis cache (M8)
- Escalar horizontalmente (múltiplas instâncias backend)

---

## Scripts Úteis

### Listar Todos os Scripts

```bash
ls -lh scripts/

# Output:
# start_exitus.sh
# stop_exitus.sh
# restart_exitus.sh
# rebuild_restart_exitus-backend.sh
# rebuild_restart_exitus-frontend.sh
# generate_api_docs.sh
# validate_docs.sh
# test_performance.sh
```

---

### generate_api_docs.sh

**Função**: Script legado que gerava `docs/API_REFERENCE_COMPLETE.md` (descontinuado em v0.7.6).

**Status**: 
- ⚠️ Descontinuado - substituído por documentação manual
- Nova referência: `docs/API_REFERENCE.md` (67 endpoints organizados por domínio)
- Arquivo antigo preservado em: `docs/ARCHIVE/API_REFERENCE_COMPLETE.md`

**Refatoração planejada**: M8 - Atualizar script para gerar novo formato

---

### validate_docs.sh

**Função**: Valida que todos os documentos estão presentes e atualizados.

```bash
./scripts/validate_docs.sh

# Output:
# ✅ README.md encontrado
# ✅ docs/ARCHITECTURE.md encontrado
# ✅ docs/MODULES.md encontrado
# ✅ docs/API_REFERENCE.md encontrado
# ✅ docs/USER_GUIDE.md encontrado
# ✅ docs/OPERATIONS_RUNBOOK.md encontrado
# ✅ docs/CHANGELOG.md encontrado
# 
# Total: 7/7 documentos OK
```

---

## Backup e Recovery

### Estratégia de Backup

#### Backup Diário Automático (Cron)

**Criar script** `backup_daily.sh`:
```bash
#!/bin/bash
# backup_daily.sh

BACKUP_DIR="/backup/exitus"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup database
podman exec exitus-db pg_dump -U exitus exitus_db | \
  gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup volumes
tar -czf $BACKUP_DIR/volumes_backup_$DATE.tar.gz volumes/

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

**Agendar no cron**:
```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 03:00)
0 3 * * * /caminho/para/backup_daily.sh >> /var/log/exitus_backup.log 2>&1
```

---

### Recovery Completo

**Cenário**: Sistema corrompido, recuperar de backup.

**Passos**:

1. **Parar todos os containers**:
```bash
./scripts/stop_exitus.sh
```

2. **Remover volumes corrompidos**:
```bash
podman volume rm exitus_postgres_data
rm -rf volumes/postgres/*
```

3. **Restaurar volumes**:
```bash
tar -xzf /backup/exitus/volumes_backup_20260106.tar.gz
```

4. **Iniciar DB**:
```bash
podman start exitus-db
sleep 10
```

5. **Restaurar dump SQL**:
```bash
gunzip < /backup/exitus/db_backup_20260106.sql.gz | \
  podman exec -i exitus-db psql -U exitus exitus_db
```

6. **Iniciar backend e frontend**:
```bash
podman start exitus-backend
podman start exitus-frontend
```

7. **Verificar integridade**:
```bash
curl http://localhost:5000/health
curl http://localhost:8080/health

# Testar login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## Referências

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detalhes da arquitetura
- [MODULES.md](MODULES.md) - Módulos implementados
- [API_REFERENCE.md](API_REFERENCE.md) - Documentação de APIs
- [USER_GUIDE.md](USER_GUIDE.md) - Guia do usuário

---

## Suporte

**GitHub Issues**: https://github.com/elielsonfontanezi/exitus/issues  
**Documentação**: https://github.com/elielsonfontanezi/exitus/tree/main/docs

---

**Documento gerado**: 07 de Janeiro de 2026  
**Versão**: v0.7.6  
**Baseado em**: Validações M4/M5/M6/M7.5, experiência operacional real
