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
- [Acessar Container Shell](#acessar-container-shell)
- [Validação Seeds](#validação-seeds)
- [Validação Usuários](#validação-usuários)
- [Validar ENUMs no Banco](#validar-enums-no-banco)

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
POSTGRES_DB=exitusdb
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
# Alpha Vantage API
# Obtenha em: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=seu_token_aqui


# Finnhub API
# Obtenha em: https://finnhub.io/register
FINNHUB_API_KEY=seu_token_aqui

# Financial Modeling Prep (opcional)
# Obtenha em: https://site.financialmodelingprep.com/developer/docs
FMP_API_KEY=seu_token_aqui

# Polygon.io (opcional)
# Obtenha em: https://polygon.io/
POLYGON_API_KEY=seu_token_aqui

# brapi.dev
BRAPI_API_KEY=seu_token_aqui

# https://twelvedata.com
TWELVE_DATA_API_KEY=seu_token_aqui

# https://marketstack.com
MARKETSTACK_API_KEY=seu_token_aqui

# https://console.hgbrasil.com
HGFINANCE_API_KEY=seu_token_aqui

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
  -e POSTGRES_DB=exitusdb \
  -e TZ=America/Sao_Paulo \
  -v ./volumes/postgres:/var/lib/postgresql/data:Z \
  -p 5432:5432 \
  postgres:16

# Aguardar 10 segundos para inicialização
sleep 10
```

#### 5. Iniciar Backend

```bash
# Obter UID/GID do usuário (importante para permissões)
USER_UID=$(id -u)
USER_GID=$(id -g)

podman run -d \
  --name exitus-backend \
  --network exitus-net \
  --env-file .env \
  -v ./backend:/app:Z \
  -v exitus-backend-logs:/app/logs:Z \
  -p 5000:5000 \
  -e USER_UID=$USER_UID \
  -e USER_GID=$USER_GID \
  exitus-backend:latest
```

#### 6. Iniciar Frontend

```bash
podman run -d \
  --name exitus-frontend \
  --network exitus-net \
  --env-file .env \
  -v ./frontend:/app:Z \
  -v exitus-frontend-logs:/app/logs:Z \
  -p 8080:8080 \
  -e USER_UID=$USER_UID \
  -e USER_GID=$USER_GID \
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

# Modo Seguro / Health Check
./scripts/repair_containers.sh

# Restart frontend
./scripts/restart_frontend.sh

# Restart backend
./scripts/restart_backend.sh

# Rebuild + Restart backend
./scripts/rebuild_restart_exitus-backend.sh

# Rebuild + Restart frontend
./scripts/rebuild_restart_exitus-frontend.sh
```

---

### Script de Inicialização

>Lembpre-se de que os scripts de automação estão localizados no diretório `scripts/` e servem para padronizar o ciclo de vida dos serviços (Banco de Dados, Backend e Frontend).

#### `start_exitus.sh`** (Modo Padrão)

**Objetivo:** Inicia os containers na ordem de dependência (DB -> API -> UI) de forma simples.

* **Quando usar:** No dia a dia, quando o ambiente já está configurado e você apenas precisa subir os serviços.
* **Comportamento:** Executa o `podman start`, aguarda um `sleep` fixo e exibe a tabela de status ao final.

#### `repair_containers.sh` (Modo Seguro / Health Check)

**Objetivo:** Garante que cada serviço esteja **realmente pronto** antes de prosseguir.

* **Quando usar:** Primeira execução do dia, após atualizações de código ou quando o ambiente apresentar instabilidade.
* **Diferenciais:**
* Verifica a saúde real (ex: testa conexão SQL no DB e endpoint `/health` no Backend).
* Reinicia containers travados automaticamente.
* Possui *timeout* de 40 segundos para evitar loops infinitos.


---

### Script de Interrupção

#### `stop_exitus.sh`

**Objetivo:** Encerra todos os processos de forma graciosa.

* **Ordem de Execução:** Para o Frontend primeiro, seguido pelo Backend e, por fim, o PostgreSQL.
* **Por que esta ordem?** Garante que as aplicações encerrem suas conexões antes que o banco de dados seja desligado, evitando corrupção de dados ou logs de erro desnecessários.

---

### Script de Reinicialização

#### `restart_exitus.sh`

**Objetivo:** Realiza o ciclo completo de desligamento e religamento.

* **Funcionamento:** Orquestra a execução do `stop_exitus.sh` seguido do `start_exitus.sh`.
* **Vantagem:** Reutiliza a lógica dos scripts base, garantindo consistência e limpeza de portas de rede (sockets) entre as sessões.

---

## Guia de Uso Rápido

### Permissões

Antes da primeira execução, garanta que todos os scripts sejam executáveis:

```bash
chmod +x scripts/*.sh

```

### Comandos Comuns

| Ação | Comando |
| --- | --- |
| **Subir ambiente rápido** | `./scripts/start_exitus.sh` |
| **Subir com validação (Safe)** | `./scripts/repair_containers.sh` |
| **Parar tudo** | `./scripts/stop_exitus.sh` |
| **Reiniciar tudo** | `./scripts/restart_exitus.sh` |

---

## Verificação de Saúde

Após rodar qualquer script de início, você pode verificar manualmente o status com:

```bash
podman ps --filter name=exitus

```

**URLs de Acesso:**

* **Frontend:** [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080)
* **Backend:** [http://localhost:5000](https://www.google.com/search?q=http://localhost:5000)

---

> **Nota:** Se algum serviço falhar persistentemente no `repair_containers.sh`, verifique os logs específicos usando `podman logs [nome-do-container]`.

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

### Carregamento de Cenários de Teste JSON

**Novo comando disponível (22/03/2026):**

```bash
# Carregar cenário de teste E2E
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_e2e

# Carregar cenário completo (test_full)
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_full

# Carregar cenário para testes de IR
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_ir

# Carregar cenário de stress (volume alto)
podman exec exitus-backend python reset_and_seed.py --clean --scenario test_stress
```

**Cenários disponíveis:**
- `test_e2e` - Dados realistas para testes E2E (3 usuários, 7 ativos, 4 transações, 2 proventos, 2 movimentações, 3 alertas)
- `test_full` - Cenário completo para todas as telas (cobertura 100% do sistema)
- `test_ir` - Dados específicos para cálculo de Imposto de Renda
- `test_stress` - Volume alto para testes de performance (6 usuários, 13 transações)

**O que é carregado:**
- Assessoras
- Usuários
- Ativos (BR, US, EU)
- Corretoras
- Transações (compra/venda)
- Proventos (dividendos, JCP, rendimentos)
- Movimentações de caixa (depósitos, saques)
- Alertas de preço
- Portfolios
- Planos de compra/venda

**Resultado esperado:**
- Dashboard com saldo de caixa != 0
- Alertas ativos e funcionais
- Portfolios criados
- Planos de compra/venda ativos
- Todas as telas com dados completos

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

### Fluxo Alembic — Ciclo Completo (EXITUS-MIGRATION-001)

> Referência rápida para o ciclo completo de migrations no ambiente Podman.
> Sempre execute dentro do container `exitus-backend`.

#### Pré-requisito — entrar no container

```bash
podman exec -it exitus-backend bash
cd app
```

#### Passo 1 — Inspecionar estado atual

```bash
# Versão aplicada atualmente no banco
flask db current
# Output esperado (exemplo):
# 008addhistoricopreco (head)

# Histórico completo de migrations
flask db history
# Output esperado:
# 008addhistoricopreco -> (head)
# 007addreports -> 008addhistoricopreco
# ...
# <base> -> 001initialschema

# Verificar se há migrations pendentes (não aplicadas)
flask db heads
# Se o output == flask db current → banco está atualizado
```

#### Passo 2 — Criar nova migration (após alterar models)

```bash
# Gera script de migration automaticamente por diff do model vs banco
flask db migrate -m "Descrição clara da mudança"
# Exemplo:
flask db migrate -m "Adicionar coluna email_verificado em usuario"

# IMPORTANTE: Sempre revisar o script gerado antes de aplicar
ls migrations/versions/
# Abrir o arquivo mais recente e validar upgrade() e downgrade()
```

#### Passo 3 — Revisar o script gerado (obrigatório)

```bash
# Verificar se o autogenerate capturou corretamente as mudanças
# Pontos de atenção:
# - ENUMs: create_type=False obrigatório para tipos já existentes no PG
# - Colunas nullable: confirmar se há dados existentes que impedem NOT NULL
# - Índices: conferir se foram gerados corretamente
cat migrations/versions/<revision_id>_descricao.py
```

#### Passo 4 — Aplicar migration

```bash
# Aplicar todas as migrations pendentes
flask db upgrade

# Aplicar até uma revisão específica
flask db upgrade 007addreports

# Confirmar que foi aplicada
flask db current
# Output deve mostrar o novo head
```

#### Passo 5 — Rollback (se necessário)

```bash
# Voltar 1 migration
flask db downgrade

# Voltar para revisão específica
flask db downgrade 007addreports

# Voltar tudo ao estado inicial — CUIDADO: apaga todos os dados!
flask db downgrade base
```

#### Passo 6 — Verificação pós-migration

```bash
# Confirmar versão atual
flask db current

# Validar tabelas no banco
podman exec exitus-db psql -U exitus -d exitusdb -c \
  "\dt" | grep -E "transacao|posicao|ativo"

# Reiniciar backend para recarregar models
exit  # sair do container
podman restart exitus-backend
podman logs --tail 20 exitus-backend
# Verificar ausência de erros de schema/ENUM na inicialização
```

#### Referência rápida — comandos Alembic

| Comando | Descrição |
|---|---|
| `flask db current` | Revisão atual aplicada no banco |
| `flask db history` | Histórico completo de migrations |
| `flask db heads` | Última revisão disponível |
| `flask db migrate -m "..."` | Gera nova migration por autogenerate |
| `flask db upgrade` | Aplica todas as migrations pendentes |
| `flask db upgrade <rev>` | Aplica até revisão específica |
| `flask db downgrade` | Reverte 1 migration |
| `flask db downgrade <rev>` | Reverte até revisão específica |
| `flask db downgrade base` | Reverte tudo ⚠️ |

#### Histórico de migrations do projeto (v0.7.11)

| Revisão | Descrição | Versão |
|---|---|---|
| `001initialschema` | Schema inicial — 13 tabelas, 11 ENUMs | v0.7.1 |
| `007addreports` | Tabela `auditoria_relatorio` | v0.7.1 |
| `008addhistoricopreco` | Tabela `historico_preco` | v0.7.1 |
| `20260216_2111` | Expansão `tipoativo`: 7 → 14 valores | v0.7.8 |
| `20260216_2130` | Campo `caprate` em `ativo`, remove `bolsa_origem` | v0.7.8 |


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
podman exec exitus-db pg_dump -U exitus exitusdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Exemplo de output:
# backup_20260107_101500.sql (12.5 MB)

# Verificar conteúdo
head -20 backup_20260107_101500.sql
```

#### Backup Apenas Dados (sem schema)

```bash
podman exec exitus-db pg_dump -U exitus --data-only exitusdb > data_only_backup.sql
```

#### Backup de Tabela Específica

```bash
podman exec exitus-db pg_dump -U exitus -t transacao exitusdb > transacao_backup.sql
```

---

### Restore de Backup

```bash
# Parar backend (evitar conflitos)
podman stop exitus-backend

# Restore
podman exec -i exitus-db psql -U exitus exitusdb < backup_20260107_101500.sql

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

## Acessar Container Shell

### Executar Scripts Python no Backend

Para executar scripts administrativos que interagem com models Flask/SQLAlchemy:

#### Método Correto (com contexto Flask)

```bash
# Template padrão para scripts administrativos
podman exec -it exitus-backend bash -c "cd /app && python3 << 'EOF'
from app import create_app
from app.database import db
from app.models import Usuario, Corretora, Ativo, Transacao  # Imports necessários

app = create_app()

with app.app_context():
    # SEU CÓDIGO AQUI
    # Exemplo: Listar todos os usuários
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f'{u.username} - {u.email}')
    
    # Exemplo: Atualizar senha
    admin = Usuario.query.filter_by(username='admin').first()
    admin.set_password('novasenha123')
    db.session.commit()
    print('✅ Senha atualizada!')
EOF
"
```

#### Por que precisa de `app_context()`?

- **SQLAlchemy** precisa do contexto Flask para acessar `db.session`
- **Models** dependem de configurações carregadas em `create_app()`
- **Queries** falham sem o contexto ativo (erro: `RuntimeError: Working outside of application context`)

#### Métodos INCORRETOS (NÃO usar)

```bash
# ❌ ERRO 1: Sem contexto Flask
podman exec exitus-backend python3 << 'EOF'
from app.models import Usuario  # ModuleNotFoundError
EOF

# ❌ ERRO 2: Script externo sem app_context
podman exec exitus-backend python3 /tmp/script.py  # RuntimeError

# ❌ ERRO 3: Tentar usar python3 -m sem contexto
podman exec exitus-backend python3 -m app.script  # Falha nas queries
```

#### Exemplos Práticos

**1. Resetar senhas de usuários:**

```bash
podman exec -it exitus-backend bash -c "cd /app && python3 << 'EOF'
from app import create_app
from app.database import db
from app.models import Usuario

app = create_app()

with app.app_context():
    usuarios = Usuario.query.filter(Usuario.username.in_(['admin', 'joao.silva'])).all()
    for u in usuarios:
        u.set_password('senha123')
        print(f'✅ {u.username} atualizado')
    db.session.commit()
EOF
"
```

**2. Listar corretoras com saldo > 1000:**

```bash
podman exec -it exitus-backend bash -c "cd /app && python3 << 'EOF'
from app import create_app
from app.models import Corretora

app = create_app()

with app.app_context():
    corretoras = Corretora.query.filter(Corretora.saldo_atual > 1000).all()
    for c in corretoras:
        print(f'{c.nome} ({c.pais}): {c.moeda_padrao} {c.saldo_atual}')
EOF
"
```

**3. Verificar integridade de dados:**

```bash
podman exec -it exitus-backend bash -c "cd /app && python3 << 'EOF'
from app import create_app
from app.models import Usuario, Corretora, Ativo

app = create_app()

with app.app_context():
    print(f'Usuários: {Usuario.query.count()}')
    print(f'Corretoras: {Corretora.query.count()}')
    print(f'Ativos: {Ativo.query.count()}')
EOF
"
```

---

**Nota importante:** Se o script for muito complexo, considere criar um arquivo `.py` dentro de `backend/app/scripts/` e executá-lo com:

```bash
podman exec -it exitus-backend bash -c "cd /app && python3 -c 'from app import create_app; from app.scripts.seu_script import main; app=create_app(); app.app_context().push(); main()'"
```

---

## Testes e Validação

### ⚠️ Pré-requisito: testes rodam DENTRO do container

O ambiente de testes **não existe no host**. As dependências Python (`marshmallow-sqlalchemy`, `flask-testing`, etc.) estão instaladas apenas dentro do container `exitus-backend`. Tentar rodar `pytest` diretamente no host resulta em `ModuleNotFoundError`.

**Regra:** sempre use `podman exec exitus-backend python -m pytest ...`

---

### Rodar Testes Automatizados (pytest)

```bash
# ✅ CORRETO — rodar suite completa dentro do container
podman exec exitus-backend python -m pytest tests/ -q --no-cov

# Com verbose (detalhes por teste)
podman exec exitus-backend python -m pytest tests/ -v --no-cov

# Módulo específico
podman exec exitus-backend python -m pytest tests/test_ativos_integration.py -v --no-cov

# Teste específico
podman exec exitus-backend python -m pytest tests/test_ativos_integration.py::TestCriarAtivo -v --no-cov

# Parar no primeiro falho
podman exec exitus-backend python -m pytest tests/ -x --no-cov
```

> **Por que `--no-cov`?** O coverage tenta gravar `.coverage` em `/app/`, que pode ter permissão negada no volume Podman (GAP EXITUS-INFRA-001). Use `--no-cov` para evitar `INTERNALERROR`.

### Recriar o banco de teste do zero

**Obrigatório após qualquer `alembic upgrade`** — e também após schema corrompido ou primeiro setup em nova máquina:

```bash
# Recria exitusdb_test com schema idêntico ao exitusdb de produção
./scripts/create_test_db.sh

# Apenas valida containers sem alterar nada
./scripts/create_test_db.sh --dry-run
```

**O que o script faz:**
1. Verifica que `exitus-db` e `exitus-backend` estão rodando
2. Encerra conexões ativas no banco de teste
3. Drop + create de `exitusdb_test`
4. Aplica schema via `pg_dump --schema-only` do `exitusdb` (garante paridade total, inclusive ENUMs)

> **⚠️ Importante:** Usar sempre `create_test_db.sh` para recriar o banco de teste — nunca `db.create_all()` diretamente, pois não respeita a ordem de criação de ENUMs PostgreSQL (L-TEST-002).

### ❌ Métodos INCORRETOS (não usar)

```bash
# ❌ No host — ModuleNotFoundError
python -m pytest tests/

# ❌ cd dentro do container — não tem shell interativo no CI
cd /home/.../exitus/backend && pytest tests/
```

---

### Testes de Integração

#### Teste Manual de Endpoints

**1. Obter Token JWT**:
```bash
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r '.data.access_token')

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
```bash
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
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 1;"
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
podman exec exitus-db psql -U exitus -d exitusdb -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname='exitusdb';"

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
podman exec -it exitus-db psql -U exitus -d exitusdb

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
  "status_code": 401
}
```

**Solução Rápida**:
```bash
# Gerar novo token
export TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r '.data.access_token')
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
podman exec exitus-db psql -U exitus -d exitusdb -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 3. Ver conexões DB
podman exec exitus-db psql -U exitus -d exitusdb -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

**Soluções**:
- Aumentar Gunicorn workers (editar Dockerfile)
- Adicionar índices em queries lentas
- Implementar Redis cache (M8)
- Escalar horizontalmente (múltiplas instâncias backend)

---

### GAP EXITUS-INFRA-001 — Volume `app/` read-only no container

> ⚠️ **GAP EXITUS-INFRA-001 (v0.7.10 — documentado):** O volume `./backend:/app:Z` é montado como **read-only** pelo Podman em alguns ambientes SELinux/rootless. Comandos como `podman exec sed -i` falham com `Permission denied`.

**Sintoma**:
```bash
podman exec exitus-backend sed -i 's/foo/bar/' /app/arquivo.py
# sed: cannot open /app/arquivo.py: Permission denied
```

**Causa**: O flag `:Z` aplica relabeling SELinux mas não garante permissão de escrita ao usuário `exitus` (UID 1000) dentro do container quando o volume é montado pelo host com permissões restritas.

**Workaround atual (v0.7.10)**:
- **Sempre edite arquivos no host** (fora do container) — o volume é bidirecional; mudanças no host refletem imediatamente no container via hot reload:
```bash
# ✅ CORRETO — editar no host
nano backend/app/seeds/seed_ativos_br.py

# ✅ Verificar que o container enxerga a mudança
podman exec exitus-backend cat /app/seeds/seed_ativos_br.py | head -5
```

- **Para scripts temporários**, copie via `podman cp`:
```bash
# Copiar script do host para o container
podman cp ./meu_script.py exitus-backend:/tmp/meu_script.py

# Executar (de /tmp, que é read-write)
podman exec -it exitus-backend python3 /tmp/meu_script.py
```

**Resolução planejada (v0.8.0)**:
- Avaliar remoção do flag `:Z` em ambientes sem SELinux obrigatório
- Verificar se `podman unshare chown` resolve o problema de permissão sem comprometer segurança

---

## Scripts Úteis

### Listar Todos os Scripts

```bash
ls -lh scripts/

# Output (24 scripts):
# backup_db.sh                       — backup do banco de dados
# cleanup_containers.sh              — limpeza de containers parados
# create_test_db.sh                  — recriação do banco de teste exitusdb_test
# exitus.sh                          — CLI unificado do sistema
# update_db_structure.sh             — sobrescreve docs/EXITUS_DB_STRUCTURE.txt com o schema atual
# generate_api_docs.sh               — geração de docs da API (legado)
# get_backend_token.sh               — obtém token JWT para testes manuais
# import_b3.sh                       — importação de arquivos B3 (Excel/CSV)
# populate_seeds.sh                  — popula dados de seed no banco
# rebuild_restart_exitus-backend.sh  — rebuild + restart do backend
# rebuild_restart_exitus-frontend.sh — rebuild + restart do frontend
# recovery_dashboard.sh              — dashboard TUI de recovery
# recovery_manager.sh                — orquestrador de backup/restore
# repair_containers.sh               — reparo e health check dos containers
# reset_and_seed.sh                  — reset completo + seed controlado
# restart_backend.sh                 — restart apenas do backend
# restart_exitus.sh                  — restart de todos os containers
# restart_frontend.sh                — restart apenas do frontend
# restore_db.sh                      — restaura backup do banco
# rollback_recovery.sh               — rollback automático de recovery
# setup_containers.sh                — configuração inicial dos containers
# setup_env.sh                       — configuração de variáveis de ambiente
# start_exitus.sh                    — inicia todos os containers
# stop_exitus.sh                     — para todos os containers
# validate_recovery.sh               — validações pós-recovery
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
podman exec exitus-db pg_dump -U exitus exitusdb | \
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
  podman exec -i exitus-db psql -U exitus exitusdb
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

## Validação Seeds
>  Módulo 2 Core

**Versão:** `v0.7.6` | **Data:** `14/02/2026`

---

### 1. Executar Seeds M2

Use o comando abaixo para garantir que o path do Python seja reconhecido corretamente.

* **Pré-requisito:** Container `exitus-backend` em execução.
* **Tempo esperado:** < 2 segundos.

```bash
podman exec -it exitus-backend bash -c "cd /app && PYTHONPATH=. python3 app/seeds/seed_modulo2.py"
```

**Output esperado:**

> ✅ Usuários criados!  
> ✅ Corretoras criadas!  
> ✅ Ativos criados!  
> ✅ SEED MÓDULO 2 CONCLUÍDO!

---

### 2. Auditoria de Dados (Contagens)

Verifique se as volumetrias batem com os requisitos da `v0.7.6`.

```bash
podman exec -it exitus-db psql exitusdb -U exitus -c "
SELECT 'usuario' as tabela, COUNT(*) as quantidade FROM usuario
UNION ALL SELECT 'corretora', COUNT(*) FROM corretora
UNION ALL SELECT 'ativo', COUNT(*) FROM ativo
UNION ALL SELECT 'transacao', COUNT(*) FROM transacao
UNION ALL SELECT 'portfolio', COUNT(*) FROM portfolio
UNION ALL SELECT 'posicao', COUNT(*) FROM posicao
UNION ALL SELECT 'provento', COUNT(*) FROM provento;"
```

| Tabela | Qtd Esperada |
| --- | --- |
| **usuario** | 5 |
| **corretora** | 14 |
| **ativo** | 44+ |
| **transacao** | 17+ |
| **portfolio** | 4+ |
| **posicao** | 17+ |
| **provento** | 29+ |

---

### 3. Validação de Acesso Admin

Verifique se o usuário mestre foi criado com as flags corretas.

```bash
podman exec -it exitus-db psql exitusdb -U exitus -c "
SELECT id, username, email, role, ativo, created_at
FROM usuario
WHERE email='admin@exitus.com';"
```

---

### 4. Credenciais de Teste (Ambiente DEV)

| Username | Email | Senha | Role |
| --- | --- | --- | --- |
| `admin` | admin@exitus.com | senha123 | **ADMIN** |
| `joao.silva` | joao.silva@example.com | senha123 | USER |
| `maria.santos` | maria.santos@example.com | senha123 | USER |
| `viewer` | viewer@exitus.com | senha123 | READONLY |
| `teste.user` | teste@exitus.com | senha123 | USER |

> ⚠️ **IMPORTANTE:** Estas credenciais são exclusivas para desenvolvimento. **Nunca** utilize estas senhas em produção.

---

### 5. Troubleshooting (Resolução de Problemas)

#### **Erro:** `ModuleNotFoundError: No module named 'app'`

* **Causa:** Execução fora do diretório raiz ou sem PYTHONPATH.
* **Solução:** Utilize `PYTHONPATH=.` dentro do container.

#### **Erro:** `ImportError: cannot import name 'IncidenciaImposto'`

* **Causa:** Script `run_all_seeds.py` está legado/depreciado.
* **Solução:** Execute especificamente o `seed_modulo2.py`.

---

###  6. Performance

Para medir a latência do banco de dados:

```bash
time podman exec exitus-db psql exitusdb -U exitus -c "SELECT COUNT(*) FROM usuario; SELECT COUNT(*) FROM ativo;"
```

* **Critério de Sucesso:** `real < 0.5s`

---

## Validação Usuários 
> M2 Core: 5 Endpoints

**Versão:** `v0.7.6` | **Data:** `15/02/2026`

---

### Comandos de Teste

#### 1. Login e Obtenção de Tokens

```bash
# Token ADMIN
export TOKEN_ADMIN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}' | jq -r '.data.access_token')

# Token USER
export TOKEN_USER=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"maria.santos","password":"senha123"}' | jq -r '.data.access_token')

# Verificar tokens
echo "Token ADMIN: ${TOKEN_ADMIN:0:50}..."
echo "Token USER: ${TOKEN_USER:0:50}..."
```

#### 2. GET /api/usuarios (Listagem - ADMIN only)

```bash
# Happy path (paginação)
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios?page=1&per_page=10" | jq '{total: .data.total, usuarios: .data.usuarios | length}'

# Filtros combinados
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios?ativo=true&role=ADMIN&search=admin" | jq .

# Sem JWT (deve retornar 401)
curl -s "http://localhost:5000/api/usuarios" | jq .

# USER comum (deve retornar 403)
curl -s -H "Authorization: Bearer $TOKEN_USER" \
  "http://localhost:5000/api/usuarios" | jq .
```

#### 3. GET /api/usuarios/{id} (Detalhes)

```bash
# Obter ID de maria.santos
MARIA_ID=$(curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios?search=maria.santos" | jq -r '.data.usuarios.id')

# ADMIN vê qualquer usuário
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios/$MARIA_ID" | jq '{username: .data.username, email: .data.email}'

# USER vê próprio usuário
curl -s -H "Authorization: Bearer $TOKEN_USER" \
  "http://localhost:5000/api/usuarios/$MARIA_ID" | jq '{success, message: .message}'

# USER tenta ver ADMIN (deve retornar 403)
ADMIN_ID=$(curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios?role=ADMIN" | jq -r '.data.usuarios.id')

curl -s -H "Authorization: Bearer $TOKEN_USER" \
  "http://localhost:5000/api/usuarios/$ADMIN_ID" | jq .
```

#### 4. POST /api/usuarios (Criar)

```bash
# Criar usuário (registro público - sem JWT)
curl -s -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste_novo",
    "email": "teste@example.com",
    "password": "senha1234",
    "nome_completo": "Usuário Teste",
    "role": "USER"
  }' | jq '{success, username: .data.username}'

# Validação: senha curta (deve retornar 400)
curl -s -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{"username":"curto","email":"curto@test.com","password":"123"}' | jq .

# Validação: email duplicado (deve retornar 400)
curl -s -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{"username":"outro","email":"teste@example.com","password":"senha1234"}' | jq .
```

#### 5. PUT /api/usuarios/{id} (Atualizar)

```bash
# USER atualiza próprio usuário (campos permitidos)
curl -s -X PUT -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"nome_completo": "Maria Santos - Atualizado"}' \
  "http://localhost:5000/api/usuarios/$MARIA_ID" | jq '{success, nome_completo: .data.nome_completo}'

# USER tenta alterar role (deve retornar 400 - GAP-005 resolvido)
curl -s -X PUT -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"role": "ADMIN"}' \
  "http://localhost:5000/api/usuarios/$MARIA_ID" | jq .

# ADMIN altera role e ativo
curl -s -X PUT -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"role": "READONLY", "ativo": false}' \
  "http://localhost:5000/api/usuarios/$MARIA_ID" | jq '{success, role: .data.role, ativo: .data.ativo}'
```

#### 6. DELETE /api/usuarios/{id} (Deletar - ADMIN only)

```bash
# Obter ID do usuário teste
TESTE_ID=$(curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios?search=teste_novo" | jq -r '.data.usuarios.id')

# ADMIN deleta usuário
curl -s -X DELETE -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios/$TESTE_ID" | jq .

# Verificar deleção (deve retornar 404)
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  "http://localhost:5000/api/usuarios/$TESTE_ID" | jq .

# USER tenta deletar (deve retornar 403)
curl -s -X DELETE -H "Authorization: Bearer $TOKEN_USER" \
  "http://localhost:5000/api/usuarios/$ADMIN_ID" | jq .
```

---

### Resultados Esperados

| Endpoint | Método | Performance | Status |
| --- | --- | --- | --- |
| `/api/usuarios` | GET | < 100ms | 200 / 401 / 403 |
| `/api/usuarios/{id}` | GET | < 100ms | 200 / 403 / 404 |
| `/api/usuarios` | POST | < 200ms | 201 / 400 |
| `/api/usuarios/{id}` | PUT | < 150ms | 200 / 400 / 403 |
| `/api/usuarios/{id}` | DELETE | < 100ms | 200 / 403 / 404 |

---

### Validar ENUMs no Banco

```bash
# Verificar tipos de ativos cadastrados
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = 'tipoativo'::regtype 
ORDER BY enumsortorder;
"

# Deve retornar 14 valores:
# acao, fii, cdb, lcilca, tesourodireto, debenture,
# stock, reit, bond, etf, stockintl, etfintl, cripto, outro

# Contar ativos por tipo
podman exec exitus-db psql -U exitus -d exitusdb -c "
SELECT tipo, COUNT(*) as total 
FROM ativo 
GROUP BY tipo 
ORDER BY total DESC;
"
```

---

## 🔧 Correção de Permissões (Windows WSL)

### Problema Comum

Ao editar arquivos no Windsurf (Windows) através do WSL, os arquivos são criados com UID/GID diferentes do usuário dentro dos containers Podman.

### Sintomas
- Erros: "Permission denied", "Operation not permitted"
- Containers não conseguem ler/escrever arquivos montados
- Arquivos com owner `100999` (Windows) vs `exitus` (container)

### Solução Automática

#### Método 1: Script Fix (Recomendado)
```bash
# Corrige instalação existente
./scripts/fix_permissions.sh
```

#### Método 2: Setup com UID/GID
```bash
# Para nova instalação
./scripts/setup_containers.sh
```

### Verificação
```bash
# Verificar UID/GID no host
id -u && id -g

# Verificar UID/GID no container
podman exec exitus-backend id -u exitus
podman exec exitus-backend id -g exitus

# Deve ser igual!
```

### Manual (se necessário)
```bash
# Parar containers
podman stop exitus-backend exitus-frontend

# Reconstruir imagem com UID/GID
cd backend
podman build -t exitus-backend:latest .
cd ../frontend
podman build -t exitus-frontend:latest .
cd ..

# Criar com UID/GID correto
USER_UID=$(id -u)
USER_GID=$(id -g)

podman run -d --name exitus-backend \
  --network exitus-net \
  -p 5000:5000 \
  -v ./backend:/app:Z \
  --env-file ./backend/.env \
  -e USER_UID=$USER_UID \
  -e USER_GID=$USER_GID \
  exitus-backend:latest
```

**Documentação completa**: [PERMISSIONS_FIX.md](PERMISSIONS_FIX.md)

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
