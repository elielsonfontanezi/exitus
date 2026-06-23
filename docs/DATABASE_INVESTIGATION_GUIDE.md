# Database Investigation Guide - Sistema Exitus

## 🎯 Objetivo

Este documento serve como guia completo para investigação, manutenção e operações do banco de dados PostgreSQL do Exitus. Foi criado para evitar perda de tempo em investigações repetitivas e documentar padrões operacionais.

## 📋 Índice

- [Fontes de Verdade](#fontes-de-verdade)
- [Arquitetura do Database](#arquitetura-do-database)
- [Conexão e Acesso](#conexão-e-acesso)
- [Operações Comuns](#operações-comuns)
- [Migrations e Schema Changes](#migrations-e-schema-changes)
- [Troubleshooting](#troubleshooting)
- [Investigation Checklist](#investigation-checklist)
- [Documentação Relacionada](#documentação-relacionada)

---

## Fontes de Verdade

### Documentação Obrigatória (SEMPRE consultar primeiro)

1. **`docs/EXITUS_DB_STRUCTURE.txt`** - Estrutura completa do banco
   - Gerado automaticamente por `scripts/update_db_structure.sh`
   - Contém schema completo: tabelas, colunas, tipos, constraints, índices
   - **ATUALIZAR SEMPRE** após alterações no schema

2. **`docs/OPERATIONS_RUNBOOK.md`** - Procedimentos operacionais
   - Scripts úteis em `scripts/`
   - Comandos para manutenção do banco
   - Procedimentos de backup/recovery

3. **`backend/app/config.py`** - Configurações de conexão
   - Porta padrão: 5433 (host) → 5432 (container)
   - Credenciais: exitus/exitus123
   - Database: exitusdb

4. **`backend/migrations/`** - Histórico de migrations (Alembic)
   - `alembic.ini` - Configuração do Alembic
   - `versions/` - Migration files
   - `env.py` - Environment setup

---

## Arquitetura do Database

### Container PostgreSQL

```bash
# Container: exitus-db
# Image: docker.io/library/postgres:16
# Port mapping: 5433:5432 (host:container)
# Database: exitusdb
# User: exitus
# Password: exitus123
```

### Configuração de Conexão

```python
# backend/app/config.py
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5433'  # IMPORTANTE: não é 5432!
POSTGRES_USER = 'exitus'
POSTGRES_PASSWORD = 'exitus123'
POSTGRES_DB = 'exitusdb'

# Connection string:
# postgresql://exitus:exitus123@127.0.0.1:5433/exitusdb
```

### Estrutura Principal

- **31 tabelas** (ver `EXITUS_DB_STRUCTURE.txt`)
- **ENUMs customizados**: tipomovimentacao, userrole, etc.
- **Constraints complexas** com CHECKs e FKs
- **Índices otimizados** para performance

---

## Conexão e Acesso

### Via Podman (Recomendado)

```bash
# Acessar shell do container
podman exec -it exitus-db bash

# Conectar ao PostgreSQL diretamente
podman exec -it exitus-db psql -U exitus -d exitusdb

# Verificar status do container
podman ps | grep exitus-db
```

### Via Python/Flask

```python
from app import create_app
from app.database import db

app = create_app()
with app.app_context():
    # Operações no banco
    result = db.session.execute(db.text("SELECT COUNT(*) FROM usuario"))
    print(result.scalar())
```

### Via psql (se instalado localmente)

```bash
# Exportar variáveis (opcional)
export PGPASSWORD=exitus123
psql -h 127.0.0.1 -p 5433 -U exitus -d exitusdb
```

---

## Operações Comuns

### Verificar Estrutura do Banco

```bash
# Atualizar documentação do schema
./scripts/update_db_structure.sh

# Listar tabelas
podman exec -it exitus-db psql -U exitus -d exitusdb -c "\dt"

# Verificar estrutura específica
podman exec -it exitus-db psql -U exitus -d exitusdb -c "\d usuario"

# Listar ENUMs
podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipomovimentacao');"
```

### Criar/Recriar Database

```bash
# Parar e remover container existente
podman stop exitus-db
podman rm exitus-db

# Criar novo container
podman run -d --name exitus-db \
  -e POSTGRES_USER=exitus \
  -e POSTGRES_PASSWORD=exitus123 \
  -e POSTGRES_DB=exitusdb \
  -p 5433:5432 \
  docker.io/library/postgres:16

# Criar ENUMs manualmente (se necessário)
podman exec -it exitus-db psql -U exitus -d exitusdb -c "CREATE TYPE tipomovimentacao AS ENUM ('aporte', 'resgate', 'transferencia_enviada', 'transferencia_recebida', 'credito_provento');"

# Criar tabelas via Flask
cd backend && python -c "
from app import create_app
from app.database import db

app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas')
"
```

### Backup e Restore

```bash
# Backup
./scripts/backup_db.sh

# Restore
./scripts/restore_db.sh
```

---

## Migrations e Schema Changes

### Problema Comum: Flask-Migrate

**Erro típico**: `sqlalchemy.exc.OperationalError: password authentication failed`

**Causa**: Configuração de porta incorreta ou ambiente não configurado

**Solução Alternativa** (quando migrate falha):

1. **ALTER TABLE direto** (para mudanças simples):
   ```bash
   podman exec -it exitus-db psql -U exitus -d exitusdb -c "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS meta_patrimonio VARCHAR(20) DEFAULT '500000.00' NOT NULL;"
   ```

2. **Atualizar modelo SQLAlchemy**:
   ```python
   # backend/app/models/usuario.py
   class Usuario(db.Model):
       # ... outros campos
       meta_patrimonio = db.Column(db.String(20), nullable=False, default='500000.00')
   ```

3. **Atualizar documentação**:
   ```bash
   ./scripts/update_db_structure.sh
   ```

### Fluxo Migration Ideal

```bash
# 1. Inicializar migrations (se não existir)
cd backend
python -c "from app import create_app; app = create_app(); app.app_context().push(); from flask_migrate import init; init()"

# 2. Criar migration
python -m flask db migrate -m "Descrição da mudança"

# 3. Aplicar migration
python -m flask db upgrade

# 4. Atualizar documentação
cd .. && ./scripts/update_db_structure.sh
```

---

## Troubleshooting

### Erros Comuns e Soluções

#### 1. `connection refused` na porta 5433
```bash
# Verificar se container está rodando
podman ps | grep exitus-db

# Verificar mapeamento de porta
podman port exitus-db

# Se não houver porta mapeada, recriar container
podman stop exitus-db
podman rm exitus-db
podman run -d --name exitus-db -e POSTGRES_USER=exitus -e POSTGRES_PASSWORD=exitus123 -e POSTGRES_DB=exitusdb -p 5433:5432 docker.io/library/postgres:16
```

#### 2. `password authentication failed`
```bash
# Verificar credenciais no config.py
grep -A5 "POSTGRES_" backend/app/config.py

# Testar conexão direta
podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT 1;"
```

#### 3. `database "exitusdb" does not exist`
```bash
# Criar database
podman exec -it exitus-db psql -U exitus -d postgres -c "CREATE DATABASE exitusdb;"

# Verificar databases disponíveis
podman exec -it exitus-db psql -U exitus -d postgres -c "\l"
```

#### 4. `relation "usuario" does not exist`
```bash
# Criar tabelas via Flask
cd backend && python -c "
from app import create_app
from app.database import db

app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas')
"
```

#### 5. `invalid input value for enum`
```bash
# Verificar ENUMs existentes
podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipomovimentacao');"

# Criar ENUMs ausentes
podman exec -it exitus-db psql -U exitus -d exitusdb -c "CREATE TYPE tipomovimentacao AS ENUM ('aporte', 'resgate', 'transferencia_enviada', 'transferencia_recebida', 'credito_provento');"
```

---

## Investigation Checklist

### Antes de Qualquer Operação no Database

- [ ] **Verificar container status**: `podman ps | grep exitus-db`
- [ ] **Consultar `EXITUS_DB_STRUCTURE.txt`** para estrutura atual
- [ ] **Verificar `OPERATIONS_RUNBOOK.md`** para procedimentos
- [ ] **Confirmar porta**: 5433 (não 5432!)
- [ ] **Testar conexão**: `podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT 1;"`

### Durante Schema Changes

- [ ] **Backup atual**: `./scripts/backup_db.sh`
- [ ] **Documentar mudança** no modelo SQLAlchemy
- [ ] **Aplicar mudança** (via migration ou ALTER direto)
- [ ] **Atualizar documentação**: `./scripts/update_db_structure.sh`
- [ ] **Testar aplicação** com novas colunas/tabelas

### Pós-Operação

- [ ] **Verificar integridade**: Testar queries críticas
- [ ] **Validar constraints**: Inserir dados de teste
- [ ] **Atualizar `AUDITORIA_FUNCIONAL*.md`** com registro
- [ ] **Commit das mudanças** com documentação atualizada

---

## Documentação Relacionada

### Essencial (Sempre consultar)

1. **`docs/EXITUS_DB_STRUCTURE.txt`** - Schema completo
2. **`docs/OPERATIONS_RUNBOOK.md`** - Scripts e procedimentos
3. **`backend/app/config.py`** - Configurações de conexão
4. **`backend/app/models/`** - Modelos SQLAlchemy

### Complementar

- **`docs/SEEDS.md`** - Dados de teste e usuários padrão
- **`docs/ENUMS.md`** - Mapeamento de ENUMs
- **`backend/migrations/`** - Histórico de alterações
- **`scripts/`** - Scripts operacionais

---

## Lições Aprendidas (Registrar em `docs/LESSONS_LEARNED.md`)

### L-DB-001: Porta PostgreSQL
- **Erro**: Assumir porta 5432
- **Correto**: Sempre usar 5433 (host) → 5432 (container)
- **Impacto**: Perda de tempo em troubleshooting de conexão

### L-DB-002: Flask-Migrate vs ALTER Direto
- **Problema**: `flask db migrate` falha com erros de conexão
- **Solução**: Usar ALTER TABLE direto via psql para mudanças simples
- **Quando usar migrate**: Mudanças complexas com múltiplas tabelas

### L-DB-003: ENUMs Pré-requisitos
- **Erro**: Esquecer de criar ENUMs antes das tabelas
- **Solução**: Sempre verificar/criar ENUMs antes de `db.create_all()`
- **Checklist**: Verificar pg_enum antes de criar tabelas

### L-DB-004: Documentação Sincronizada
- **Regra**: Atualizar `EXITUS_DB_STRUCTURE.txt` SEMPRE após mudanças
- **Comando**: `./scripts/update_db_structure.sh`
- **Impacto**: Evita investigações repetitivas

---

## Registro de Atividades

### Template para `AUDITORIA_FUNCIONAL*.md`

```markdown
#### Database Investigation - [Data]

**Objetivo**: [Descrição da atividade]

**Fontes Consultadas**:
- ✅ EXITUS_DB_STRUCTURE.txt
- ✅ OPERATIONS_RUNBOOK.md
- ✅ config.py (porta 5433)

**Problemas Encontrados**:
1. [Problema 1] - [Solução aplicada]
2. [Problema 2] - [Solução aplicada]

**Comandos Executados**:
```bash
# Comando 1
# Comando 2
```

**Resultado**:
- ✅ [Resultado 1]
- ✅ [Resultado 2]

**Lições Aprendidas**:
- L-DB-XXX: [Nova lição]

**Próximos Passos**:
- [ ] [Ação 1]
- [ ] [Ação 2]
```

---

## Conclusão

Este guia deve ser atualizado continuamente com novas lições aprendidas e padrões operacionais. **Sempre** registrar atividades de database no documento de auditoria funcional para construir conhecimento acumulado.

**Regra de Ouro**: Se uma operação de database demorou mais de 5 minutos para investigar, documente o padrão aqui para evitar repetição futura.
