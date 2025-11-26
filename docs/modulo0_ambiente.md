
# Exitus - Módulo 0: Preparação do Ambiente (Podman)

## Introdução

Este documento detalha o passo a passo para a preparação do ambiente computacional do Sistema Exitus, iniciando pela criação da estrutura de projeto, configuração de variáveis de ambiente em estilo produção (.env), instalação do Podman, configuração de rede e volumes, build das imagens, criação dos containers e testes de comunicação para a arquitetura proposta: PostgreSQL (DB), Flask Backend (API) e Flask Frontend (UI).

O próprio conteúdo deste arquivo deve ser salvo em `exitus/docs/docs_modulo0.md` e servirá como documentação oficial do Módulo 0.

## 1. Estrutura do Projeto

Crie o diretório raiz e a estrutura base do projeto:

```bash
mkdir -p exitus/{docs,scripts,backend,frontend,tests,backups}
cd exitus
```

### Estrutura de Diretórios

```text
exitus/
├── README.md                    # Introdução ao sistema e links para módulos
├── docs/                        # Documentação modular
│   ├── docs_modulo0.md          # Este documento (Módulo 0)
│   ├── docs_modulo1.md          # Será criado no Módulo 1
│   └── ...
├── scripts/                     # Scripts de gerenciamento e automação
│   ├── setup_env.sh            # Seleção de ambiente (dev/staging/prod)
│   ├── setup_containers.sh     # Configuração inicial dos containers
│   ├── start_services.sh       # Iniciar todos os serviços
│   ├── stop_services.sh        # Parar todos os serviços
│   ├── backup_db.sh            # Backup do banco de dados
│   └── cleanup_containers.sh   # Limpeza de containers e recursos
├── backend/                     # Código do Backend Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── routes/             # (será detalhado em módulos futuros)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── .env.development.example
│   ├── .env.staging.example
│   ├── .env.production.example
│   └── run.py
├── frontend/                    # Código do Frontend Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── routes/             # (será detalhado em módulos futuros)
│   │   ├── templates/
│   │   └── static/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── .env.development.example
│   ├── .env.staging.example
│   ├── .env.production.example
│   └── run.py
├── tests/                       # Testes automatizados
│   ├── test_backend.py
│   └── test_frontend.py
└── backups/                     # Backups do banco de dados
```

### README.md Principal

Crie o arquivo `exitus/README.md` com visão geral do sistema e links para os módulos:

```markdown
-----

## 🏗️ Arquitetura Técnica

Para máxima portabilidade e desempenho, o **Exitus** adota uma arquitetura em contêineres:

| Componente | Tecnologia Principal | Descrição/Detalhes |
| :--- | :--- | :--- |
| **Banco de Dados** | **PostgreSQL 15** | Armazenamento robusto e transacional (em container Podman). |
| **Backend** | **Flask + SQLAlchemy** | APIs RESTful de alto desempenho para lógica de negócios (em container Podman). |
| **Frontend** | **Flask + HTMX + Alpine.js** | Interface de usuário moderna, leve e reativa (em container Podman). |
| **Infraestrutura** | **Ubuntu + Podman** | Sistema operacional base e runtime de contêineres. |

-----

## 🛠️ Tecnologias Chave

  * 🐍 **Python 3.11+** (Linguagem de Backend)
  * 🌐 **Flask 3.x** (Framework Web)
  * 💾 **PostgreSQL 15** (Base de Dados)
  * ⚙️ **SQLAlchemy 2.x** (ORM)
  * 🐳 **Podman** (Containerização)
  * ✨ **HTMX, Alpine.js** (Interatividade de Frontend)

-----

## 📚 Documentação Detalhada dos Módulos

Nossa documentação está organizada para guiar você desde a configuração inicial até o deploy:

## Documentação dos Módulos

- [Módulo 0: Preparação do Ambiente](docs/modulo0_ambiente.md)
- [Módulo 1: Estrutura do Banco de Dados](docs/modulo1_database.md)
- [Módulo 2: Backend - Autenticação e Usuários](docs/modulo2_backend_auth.md)
- [Módulo 3: Backend - Gestão de Ativos](docs/modulo3_backend_financeiro.md)
- [Módulo 4: Backend - Transações e Portfólio](docs/modulo4_backend_integracoes.md)
- [Módulo 5: Backend - APIs de Integração](docs/modulo5_frontend_base.md)
- [Módulo 6: Frontend - Interface do Usuário](docs/modulo6_frontend_dashboards.md)
- [Módulo 7: Testes e Validação](docs/modulo7_relatorios.md)
- [Módulo 8: Deploy e Monitoramento](docs/modulo8_deploy.md)

-----

## ▶️ Guia de Início Rápido (Quick Start)

1.  **Configuração do Ambiente** (Veja o [Módulo 0]((docs/modulo0_ambiente.md)):
    ```bash
    ./scripts/setup_containers.sh
    ```
2.  **Iniciar Serviços:**
    ```bash
    ./scripts/start_services.sh
    ```
3.  **Acessar a Aplicação:**
      * **Frontend (Interface Web):** `http://localhost:8080`
      * **Backend (API RESTful):** `http://localhost:5000`
```

## 2. Criação da Estrutura Backend

### 2.1 Criar Estrutura de Diretórios

```bash
mkdir -p backend/app/routes
mkdir -p backend/logs
```

### 2.2 backend/requirements.txt

Crie o arquivo `backend/requirements.txt`:

```text
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
pytest==7.4.3
gunicorn==21.2.0
```

### 2.3 backend/.env.example (template base)

Crie o arquivo `backend/.env.example`:

```bash
# Database Configuration
POSTGRES_HOST=exitus-db
POSTGRES_USER=exitus
POSTGRES_PASSWORD=exitus123
POSTGRES_DB=exitusdb
POSTGRES_PORT=5432

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=change-me-in-env

# Timezone
TZ=America/Sao_Paulo
```

Opcionalmente, crie variações específicas por ambiente apenas como exemplos (staging/production):

```bash
cp backend/.env.example backend/.env.development.example
cp backend/.env.example backend/.env.staging.example
cp backend/.env.example backend/.env.production.example
```

### 2.4 backend/run.py

Crie o arquivo `backend/run.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exitus Backend - Entry Point"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.getenv('FLASK_ENV') == 'development'))
```

### 2.5 backend/app/config.py

Crie o arquivo `backend/app/config.py` para carregar variáveis de ambiente em estilo produção:

```python
# -*- coding: utf-8 -*-
"""Exitus Backend - Configuration"""

import os
from dotenv import load_dotenv

# Carrega .env se existir
load_dotenv()

class Config:
    """Configurações da aplicação"""

    # Database
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'exitus')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'exitus123')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'exitusdb')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 2.6 backend/app/\_\_init\_\_.py

Crie/atualize o arquivo `backend/app/__init__.py`:

```python
# -*- coding: utf-8 -*-
"""Exitus Backend - Application Factory"""

from flask import Flask
from flask_cors import CORS
from .config import Config


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Habilita CORS
    CORS(app)

    # Health check route
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-backend',
            'env': app.config.get('FLASK_ENV', 'unknown')
        }, 200

    return app
```

### 2.7 backend/Dockerfile

Atualize ou crie o arquivo `backend/Dockerfile` com boas práticas de produção (imagem slim, dependências mínimas e ferramentas de diagnóstico):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema (incluindo ping e curl para diagnóstico)
RUN apt-get update && apt-get install -y     gcc     postgresql-client     iputils-ping     curl     && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Se não existir .env dentro da imagem, cria a partir do exemplo (útil para dev)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Expõe porta
EXPOSE 5000

# Comando anterior
# CMD ["python", "run.py"]

# Novo comando
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app", "--reload"]
```

## 3. Criação da Estrutura Frontend

### 3.1 Criar Estrutura de Diretórios

```bash
mkdir -p frontend/app/{routes,templates,static/{css,js}}
mkdir -p frontend/logs
```

### 3.2 frontend/requirements.txt

Crie o arquivo `frontend/requirements.txt`:

```text
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
gunicorn==21.2.0
```

### 3.3 frontend/.env.example

Crie o arquivo `frontend/.env.example`:

```bash
# Backend API Configuration
BACKEND_API_URL=http://exitus-backend:5000

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=change-me-in-env

# Timezone
TZ=America/Sao_Paulo
```

Opcionalmente, crie variações por ambiente (apenas templates):

```bash
cp frontend/.env.example frontend/.env.development.example
cp frontend/.env.example frontend/.env.staging.example
cp frontend/.env.example frontend/.env.production.example
```

### 3.4 frontend/run.py

Crie o arquivo `frontend/run.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exitus Frontend - Entry Point"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=(os.getenv('FLASK_ENV') == 'development'))
```

### 3.5 frontend/app/config.py

Crie o arquivo `frontend/app/config.py`:

```python
# -*- coding: utf-8 -*-
"""Exitus Frontend - Configuration"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações da aplicação"""

    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
```

### 3.6 frontend/app/\_\_init\_\_.py

Crie/atualize o arquivo `frontend/app/__init__.py`:

```python
# -*- coding: utf-8 -*-
"""Exitus Frontend - Application Factory"""

from flask import Flask, render_template_string
from .config import Config


def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Rota inicial simples (será substituída em módulos futuros)
    @app.route('/')
    def index():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Exitus - Sistema de Investimentos</title>
        </head>
        <body>
            <h1>Exitus - Sistema de Controle e Análise de Investimentos</h1>
            <p>Frontend funcionando corretamente!</p>
        </body>
        </html>
        """
        return render_template_string(html)

    # Health check
    @app.route('/health')
    def health():
        return {
            'status': 'ok',
            'service': 'exitus-frontend',
            'env': app.config.get('FLASK_ENV', 'unknown')
        }, 200

    return app
```

### 3.7 frontend/Dockerfile

Atualize ou crie o arquivo `frontend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala ferramentas úteis de diagnóstico
RUN apt-get update && apt-get install -y     curl     && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Se não existir .env dentro da imagem, cria a partir do exemplo (útil para dev)
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Expõe porta
EXPOSE 8080

# Comando anterior
# CMD ["python", "run.py"]

# Novo comando
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app", "--reload"]

```

## 4. Instalação do Podman (Ubuntu)

No host Ubuntu, instale e prepare o Podman para uso rootless:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y podman

# Verificar instalação
podman --version

# Configurar subuid/subgid para rootless (se ainda não configurado)
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid
```

## 5. Network e Volumes

Crie a rede dedicada e volumes persistentes (pode ser feito manualmente ou pelo script):

```bash
# Network
podman network create exitus-net

# Volumes
podman volume create exitus-pgdata
podman volume create exitus-backend-logs
podman volume create exitus-frontend-logs
```

## 6. Build das Imagens

Em ambiente de desenvolvimento, o build será automatizado pelo script `scripts/setup_containers.sh`, mas os comandos manuais são:

```bash
# Backend
cd backend
podman build -t exitus-backend:latest .
cd ..

# Frontend
cd frontend
podman build -t exitus-frontend:latest .
cd ..
```

## 7. Scripts de Ambiente e Containers

### 7.1 scripts/setup_env.sh

Crie o arquivo `scripts/setup_env.sh` para selecionar o ambiente (development/staging/production):

```bash
#!/bin/bash
# Configura ambiente (development, staging, production)

ENV=${1:-development}

echo "Configurando ambiente: $ENV"

case $ENV in
  development)
    echo "Usando configurações de desenvolvimento..."
    cp backend/.env.example backend/.env
    cp frontend/.env.example frontend/.env
    ;;

  staging)
    echo "Usando configurações de staging..."
    if [ -f backend/.env.staging ]; then
      cp backend/.env.staging backend/.env
    else
      echo "ERRO: backend/.env.staging não encontrado"; exit 1
    fi
    if [ -f frontend/.env.staging ]; then
      cp frontend/.env.staging frontend/.env
    else
      echo "ERRO: frontend/.env.staging não encontrado"; exit 1
    fi
    ;;

  production)
    echo "Usando configurações de produção..."
    if [ -f backend/.env.production ]; then
      cp backend/.env.production backend/.env
    else
      echo "ERRO: backend/.env.production não encontrado"; exit 1
    fi
    if [ -f frontend/.env.production ]; then
      cp frontend/.env.production frontend/.env
    else
      echo "ERRO: frontend/.env.production não encontrado"; exit 1
    fi
    ;;

  *)
    echo "Ambiente inválido. Use: development, staging ou production"; exit 1;;
esac

echo "Ambiente $ENV configurado com sucesso!"
```

Torne executável:

```bash
chmod +x scripts/setup_env.sh
```

### 7.2 scripts/setup_containers.sh

Atualize `scripts/setup_containers.sh` para operar de forma idempotente e usar `.env`:

```bash
#!/bin/bash
# Configuração inicial dos containers do Exitus

set -e

# Remover containers existentes
echo "Removendo containers antigos (se existirem)..."
podman stop exitus-db  2>/dev/null || true
podman stop exitus-backend 2>/dev/null || true
podman stop exitus-frontend 2>/dev/null || true

podman rm exitus-db 2>/dev/null || true
podman rm exitus-backend 2>/dev/null || true
podman rm exitus-frontend 2>/dev/null || true
pkill -9 containers-rootlessport || true

echo "=== Setup Exitus - Módulo 0 ==="

# Criar network
echo "Criando network..."
podman network create exitus-net 2>/dev/null || echo "Network já existe"

# Criar volumes
echo "Criando volumes..."
podman volume create exitus-pgdata 2>/dev/null || echo "Volume pgdata já existe"
podman volume create exitus-backend-logs 2>/dev/null || echo "Volume backend-logs já existe"
podman volume create exitus-frontend-logs 2>/dev/null || echo "Volume frontend-logs já existe"

# Criar arquivos .env a partir dos exemplos (se não existirem)
echo "Criando arquivos .env..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ backend/.env criado a partir do .env.example"
else
    echo "✓ backend/.env já existe"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✓ frontend/.env criado a partir do .env.example"
else
    echo "✓ frontend/.env já existe"
fi

# Build das imagens
echo "Building backend image..."
cd backend
podman build -t exitus-backend:latest .
cd ..

echo "Building frontend image..."
cd frontend
podman build -t exitus-frontend:latest .
cd ..

# Criar container PostgreSQL
echo "Criando container PostgreSQL..."
podman run -d --name exitus-db   --network exitus-net   -v exitus-pgdata:/var/lib/postgresql/data   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   docker.io/postgres:15

echo "Aguardando PostgreSQL inicializar..."
sleep 10

# Criar container Backend (usando .env)
echo "Criando container Backend..."
podman run -d --name exitus-backend   --network exitus-net   -p 5000:5000   -v ./backend:/app:Z   -v exitus-backend-logs:/app/logs:Z   --env-file ./backend/.env   exitus-backend:latest

# Criar container Frontend (usando .env)
echo "Criando container Frontend..."
podman run -d --name exitus-frontend   --network exitus-net   -p 8080:8080   -v ./frontend:/app:Z   -v exitus-frontend-logs:/app/logs:Z   --env-file ./frontend/.env   exitus-frontend:latest

echo ""
echo "=== Setup concluído! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
```

### 7.3 scripts/start_services.sh

```bash
#!/bin/bash
# Inicia todos os serviços do Exitus

echo "Iniciando serviços Exitus..."

podman start exitus-db || true
echo "PostgreSQL iniciado"
sleep 5

podman start exitus-backend || true
echo "Backend iniciado"

podman start exitus-frontend || true
echo "Frontend iniciado"

echo ""
echo "=== Serviços iniciados! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
```

### 7.4 scripts/stop_services.sh

```bash
#!/bin/bash
# Para todos os serviços do Exitus

echo "Parando serviços Exitus..."

podman stop exitus-frontend exitus-backend exitus-db 2>/dev/null || true

echo "=== Serviços parados! ==="
```

### 7.5 scripts/cleanup_containers.sh

```bash
#!/bin/bash
# Remove todos os containers do Exitus

echo "=== Cleanup Exitus ==="

echo "Parando containers..."
podman stop exitus-frontend exitus-backend exitus-db 2>/dev/null || true

echo "Removendo containers..."
podman rm exitus-frontend exitus-backend exitus-db 2>/dev/null || true

echo "Containers removidos!"

echo "Para remover também volumes e network, execute manualmente (cuidado!):"
echo "  podman volume rm exitus-pgdata exitus-backend-logs exitus-frontend-logs"
echo "  podman network rm exitus-net"
```

### 7.6 scripts/backup_db.sh

```bash
#!/bin/bash
# Backup do banco de dados PostgreSQL

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Criando backup do banco de dados..."

podman exec exitus-db pg_dump -U exitus exitusdb > "$BACKUP_DIR/exitusdb_$TIMESTAMP.sql"

echo "Backup criado: $BACKUP_DIR/exitusdb_$TIMESTAMP.sql"
```

Torne todos os scripts executáveis:

```bash
chmod +x scripts/*.sh
```

## 8. Testes de Comunicação e Saúde

### 8.1 Testes a partir do host

```bash
# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:8080/health
```

### 8.2 Testes dentro dos containers

```bash
# Frontend → Backend (via curl)
podman exec exitus-frontend curl http://exitus-backend:5000/health

# Backend → Database (TCP via Python)
podman exec exitus-backend python -c "import socket; socket.create_connection(('exitus-db', 5432), timeout=5); print('Conexao OK com PostgreSQL')"

# Database respondendo
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 'PostgreSQL OK' as status;"
```

### 8.3 Verificação de logs e status

```bash
# Status dos containers
podman ps

# Logs
podman logs exitus-db --tail 50
podman logs exitus-backend --tail 50
podman logs exitus-frontend --tail 50
```

## 9. Boas Práticas

### .gitignore

Crie o arquivo `exitus/.gitignore` para evitar versionar artefatos sensíveis ou gerados:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.env
.env
.env.*
!.env.example    # Permite apenas .env.example
instance/
db.sqlite3
# logs
logs/
*.log
# Docker
*.pid
*.db
backups/

# IDEs/editors
.vscode/
.idea/
*.swp

# Test files
*.coverage
htmlcov/
.tox/
*.cache
pytest_cache/
.mypy_cache/
coverage.xml

# Container artifacts
exitus-backend/
exitus-frontend/
exitus-db/

# OS files
.DS_Store
Thumbs.db
```

### 9.2 Template dotenv.

Segue exemplo de uso dos dotenv para preparação do ambiente.

```bash
# Desenvolvimento (padrão)
./scripts/setup_env.sh development
./scripts/setup_containers.sh

# Staging
./scripts/setup_env.sh staging
./scripts/setup_containers.sh

# Produção
./scripts/setup_env.sh production
./scripts/setup_containers.sh
```

## 10. Documentação do Módulo

Este documento deve ser salvo como `exitus/docs/docs_modulo0.md` e terá as seguintes finalidades:

- Referência oficial para recriação do ambiente de desenvolvimento e homologação.
- Base para onboarding de novos desenvolvedores no projeto Exitus.
- Guia de troubleshooting inicial envolvendo containers, rede, volumes e variáveis de ambiente.
- Ponto de partida para ajustes específicos de ambientes (staging/production) em módulos posteriores.

Após concluir todos os passos deste módulo e validar os testes de comunicação, prossiga para o **Módulo 1**, que tratará da modelagem e implementação da estrutura de banco de dados PostgreSQL do sistema Exitus.
