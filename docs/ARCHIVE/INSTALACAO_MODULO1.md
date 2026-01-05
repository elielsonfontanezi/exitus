# Exitus - Módulo 1: Database Backend
## Guia Completo de Instalação e Configuração

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Instalação dos Containers](#instalação-dos-containers)
5. [Configuração do Backend](#configuração-do-backend)
6. [Migrations e Schema](#migrations-e-schema)
7. [Seeds de Dados](#seeds-de-dados)
8. [Validação da Instalação](#validação-da-instalação)
9. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Sistema Operacional
- Ubuntu 22.04+ (WSL2 ou nativo)
- Podman instalado e configurado

### Verificar Instalação
```bash
# Verificar versão do Podman
podman --version
# Saída esperada: podman version 4.x.x ou superior

# Verificar se Podman está rodando
podman ps
```

---

## 📁 Estrutura do Projeto

```
exitus/
├── backend/
│   ├── alembic/              # Migrations do banco de dados
│   │   ├── versions/         # Arquivos de migration
│   │   └── env.py           # Configuração do Alembic
│   ├── app/
│   │   ├── __init__.py      # Inicialização da aplicação Flask
│   │   ├── config.py        # Configurações da aplicação
│   │   ├── database.py      # Configuração do SQLAlchemy
│   │   ├── models/          # Models do sistema (12 arquivos)
│   │   │   ├── usuario.py
│   │   │   ├── corretora.py
│   │   │   ├── ativo.py
│   │   │   ├── posicao.py
│   │   │   ├── transacao.py
│   │   │   ├── provento.py
│   │   │   ├── movimentacao_caixa.py
│   │   │   ├── evento_corporativo.py
│   │   │   ├── fonte_dados.py
│   │   │   ├── regra_fiscal.py
│   │   │   ├── feriado_mercado.py
│   │   │   └── log_auditoria.py
│   │   └── seeds/           # Scripts de população de dados
│   │       ├── seed_usuarios.py
│   │       ├── seed_ativos_br.py
│   │       ├── seed_regras_fiscais_br.py
│   │       ├── seed_feriados_b3.py
│   │       ├── seed_fontes_dados.py
│   │       └── run_all_seeds.py
│   ├── Dockerfile           # Imagem Docker do backend
│   ├── requirements.txt     # Dependências Python
│   ├── alembic.ini         # Configuração do Alembic
│   └── run.py              # Entry point da aplicação
├── docs/                    # Documentação
│   ├── INSTALACAO_MODULO1.md
│   └── modulo1_database.md
├── scripts/
│   └── setup_containers.sh  # Script de setup dos containers
└── tests/                   # Scripts de validação
    ├── mod1_validacao_final_fase1.sh
    ├── mod1_validacao_final_fase2.sh
    ├── mod1_validacao_final_fase3.sh
    ├── mod1_validacao_final_fase4.sh
    └── mod1_validacao_final_fase5.sh
```

---

## ⚙️ Configuração do Ambiente

### 1. Criar Diretórios do Projeto

```bash
mkdir -p ~/exitus/{backend,docs,scripts,tests}
cd ~/exitus
```

### 2. Criar Rede Podman

```bash
podman network create exitus-network
```

**Verificar:**
```bash
podman network ls
# Deve mostrar: exitus-network
```

---

## 🐳 Instalação dos Containers

### 1. Container PostgreSQL

```bash
podman run -d \
  --name exitus-db \
  --network exitus-network \
  -e POSTGRES_USER=exitus \
  -e POSTGRES_PASSWORD=exitus_pass \
  -e POSTGRES_DB=exitusdb \
  -v exitus-db-data:/var/lib/postgresql/data \
  postgres:15-alpine
```

**Verificar:**
```bash
podman logs exitus-db
# Deve mostrar: "database system is ready to accept connections"
```

### 2. Preparar Backend

**Criar requirements.txt:**
```bash
nano backend/requirements.txt
```

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
psycopg2-binary==2.9.9
python-dotenv==1.0.0
alembic==1.13.0
gunicorn==21.2.0
```

**Criar Dockerfile:**
```bash
nano backend/Dockerfile
```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "--timeout", "120", "run:app"]
```

### 3. Container Backend

**Build da imagem:**
```bash
cd backend
podman build -t exitus-backend:latest .
```

**Executar container:**
```bash
podman run -d \
  --name exitus-backend \
  --network exitus-network \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  -e DATABASE_URL=postgresql://exitus:exitus_pass@exitus-db:5432/exitusdb \
  -v $(pwd):/app:Z \
  exitus-backend:latest
```

**Verificar:**
```bash
curl http://localhost:5000/health
# Deve retornar: {"status":"ok","service":"exitus-backend","env":"development"}
```

---

## 🔧 Configuração do Backend

### 1. Estrutura de Arquivos

Todos os arquivos do backend já devem estar criados conforme a estrutura mostrada acima.

### 2. Arquivo de Configuração Principal

**backend/app/__init__.py:**
```python
from flask import Flask
from app.config import Config
from app.database import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar banco de dados
    init_db(app)

    # Registrar blueprints (será feito no Módulo 2)

    # Rota de health check
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-backend',
            'env': app.config['ENV']
        }

    return app

app = create_app()
```

### 3. Configuração do Banco de Dados

**backend/app/database.py:**
```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Importar todos os models
        from app.models import (
            Usuario, Corretora, Ativo, Posicao, Transacao,
            Provento, MovimentacaoCaixa, EventoCorporativo,
            FonteDados, RegraFiscal, FeriadoMercado, LogAuditoria
        )

    return db
```

---

## 🗃️ Migrations e Schema

### 1. Configurar Alembic

**backend/alembic/env.py** (já deve estar configurado corretamente)

### 2. Gerar Migration Inicial

```bash
# Entrar no container
podman exec -it exitus-backend bash

# Dentro do container:
cd /app
alembic revision --autogenerate -m "Initial schema - 12 models"
```

**Saída esperada:**
```
INFO  [alembic.autogenerate.compare] Detected added table 'usuario'
INFO  [alembic.autogenerate.compare] Detected added table 'ativo'
...
Generating /app/alembic/versions/XXXXX_initial_schema_12_models.py ... done
```

### 3. Aplicar Migration

```bash
# Dentro do container:
alembic upgrade head
```

**Saída esperada:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> XXXXX, Initial schema - 12 models
```

### 4. Validar Schema Criado

```bash
# No host:
podman exec exitus-db psql -U exitus -d exitusdb -c "\dt"
```

**Deve listar 13 tabelas:**
- alembic_version
- ativo
- corretora
- evento_corporativo
- feriado_mercado
- fonte_dados
- log_auditoria
- movimentacao_caixa
- posicao
- provento
- regra_fiscal
- transacao
- usuario

---

## 🌱 Seeds de Dados

### Executar Seeds Individuais

```bash
# Dentro do container backend:
python3 -m app.seeds.seed_usuarios
python3 -m app.seeds.seed_ativos_br
python3 -m app.seeds.seed_regras_fiscais_br
python3 -m app.seeds.seed_feriados_b3
python3 -m app.seeds.seed_fontes_dados
```

### Ou Executar Todos de Uma Vez

```bash
# Dentro do container backend:
python3 -m app.seeds.run_all_seeds
```

### Dados Populados

Após executar os seeds, o banco terá:
- **4 usuários** (admin, 2 users, 1 readonly)
- **25 ativos BR** (15 ações + 10 FIIs)
- **6 regras fiscais** brasileiras
- **30 feriados** B3 (2025-2026)
- **7 fontes de dados** (APIs)

**Credenciais de acesso:**
```
Username: admin       | Senha: admin123
Username: joao.silva  | Senha: user123
Username: maria.santos| Senha: user123
Username: viewer      | Senha: viewer123
```

⚠️ **ATENÇÃO:** Altere as senhas em produção!

---

## ✅ Validação da Instalação

### Scripts de Validação Automática

```bash
# No host, executar cada fase:
./tests/mod1_validacao_final_fase1.sh
./tests/mod1_validacao_final_fase2.sh
./tests/mod1_validacao_final_fase3.sh
./tests/mod1_validacao_final_fase4.sh
./tests/mod1_validacao_final_fase5.sh
```

### Validação Manual

**1. Verificar containers:**
```bash
podman ps
# Deve mostrar 3 containers rodando: exitus-db, exitus-backend, exitus-frontend
```

**2. Testar conexão com banco:**
```bash
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT COUNT(*) FROM usuario;"
# Deve retornar: 4
```

**3. Testar API backend:**
```bash
curl http://localhost:5000/health
# Deve retornar JSON com status ok
```

**4. Verificar logs:**
```bash
podman logs exitus-backend --tail 20
# Não deve ter erros críticos
```

---

## 🔍 Troubleshooting

### Container não inicia

**Problema:** Container exitus-backend não sobe
```bash
podman logs exitus-backend
# Ver erros específicos
```

**Soluções comuns:**
- Verificar se porta 5000 não está em uso: `netstat -tulpn | grep 5000`
- Verificar variáveis de ambiente: `podman exec exitus-backend env | grep DATABASE`
- Reconstruir imagem: `podman build --no-cache -t exitus-backend:latest .`

### Erro de conexão com banco

**Problema:** Backend não conecta no PostgreSQL

**Soluções:**
```bash
# Verificar se containers estão na mesma rede
podman network inspect exitus-network

# Testar conexão manualmente
podman exec exitus-backend ping exitus-db

# Verificar se PostgreSQL está aceitando conexões
podman exec exitus-db pg_isready -U exitus
```

### Migration falha

**Problema:** `alembic upgrade head` retorna erro

**Soluções:**
```bash
# Ver histórico de migrations
alembic history

# Ver versão atual
alembic current

# Reverter migration (cuidado!)
alembic downgrade -1

# Gerar nova migration
alembic revision --autogenerate -m "Fix: descrição"
```

### Seed falha

**Problema:** Seed retorna erro de constraint ou duplicate

**Soluções:**
```bash
# Limpar tabela específica (exemplo: usuario)
podman exec exitus-db psql -U exitus -d exitusdb -c "DELETE FROM usuario;"

# Resetar banco (CUIDADO - apaga tudo!)
podman exec exitus-db psql -U exitus -d exitusdb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
alembic upgrade head
```

---

## 📊 Resumo da Instalação

Ao final deste guia, você terá:

✅ 3 containers rodando (PostgreSQL, Backend, Frontend)  
✅ 13 tabelas criadas no banco de dados  
✅ 11 enums personalizados  
✅ 15 foreign keys configuradas  
✅ 86 índices otimizados  
✅ 72 registros de dados iniciais  
✅ 5 scripts de validação funcionando  

**Tempo estimado de instalação:** 45-60 minutos

---

## 🎯 Próximos Passos

Com o Módulo 1 instalado, você pode:

1. **Módulo 2:** Desenvolver API REST com endpoints CRUD
2. **Módulo 3:** Criar interface frontend
3. **Testes:** Implementar testes unitários e de integração
4. **Deploy:** Preparar ambiente de produção

---

## 📚 Referências

- [Documentação do PostgreSQL](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Podman Documentation](https://docs.podman.io/)

---

**Versão:** 1.0  
**Data:** Novembro 2025  
**Autor:** Equipe Exitus
