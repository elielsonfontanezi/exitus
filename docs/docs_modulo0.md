# Exitus - Módulo 0: Preparação do Ambiente (Podman)

## Introdução

Este documento detalha o passo a passo para a preparação do ambiente computacional do Sistema Exitus, iniciando pela criação da estrutura de projeto, seguida pela instalação do Podman, configuração de rede, volumes, criação dos containers e garantia da comunicação entre eles para a arquitetura proposta: PostgreSQL (DB), Flask Backend (API) e Flask Frontend (UI).

## 1. Estrutura do Projeto

Crie o diretório raiz e a estrutura base do projeto:

```bash
mkdir -p exitus/{docs,scripts,backend,frontend,tests,backups}
cd exitus
```

### Estrutura de Diretórios

```
exitus/
├── README.md                    # Introdução ao sistema e links para módulos
├── docs/                        # Documentação modular
│   ├── docs_modulo0.md         # Este documento
│   ├── docs_modulo1.md         # Será criado no Módulo 1
│   └── ...
├── scripts/                     # Scripts de gerenciamento
│   ├── setup_containers.sh     # Configuração inicial dos containers
│   ├── start_services.sh       # Iniciar todos os serviços
│   ├── stop_services.sh        # Parar todos os serviços
│   └── backup_db.sh            # Backup do banco de dados
├── backend/                     # Código do Backend Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── routes/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── run.py
├── frontend/                    # Código do Frontend Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── routes/
│   │   ├── templates/
│   │   └── static/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── run.py
├── tests/                       # Testes automatizados
│   ├── test_backend.py
│   └── test_frontend.py
└── backups/                     # Backups do banco de dados
```

### .gitignore
Crie o arquivo `exitus/.gitignore`:

```bash
cd exitus
cat << EOF > .gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.env
*.venv
.env*
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

EOF
```
### README.md Principal

Crie o arquivo `exitus/README.md`:

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

- [Módulo 0: Preparação do Ambiente](docs/docs_modulo0.md)
- [Módulo 1: Estrutura do Banco de Dados](docs/docs_modulo1.md)
- [Módulo 2: Backend - Autenticação e Usuários](docs/docs_modulo2.md)
- [Módulo 3: Backend - Gestão de Ativos](docs/docs_modulo3.md)
- [Módulo 4: Backend - Transações e Portfólio](docs/docs_modulo4.md)
- [Módulo 5: Backend - APIs de Integração](docs/docs_modulo5.md)
- [Módulo 6: Frontend - Interface do Usuário](docs/docs_modulo6.md)
- [Módulo 7: Testes e Validação](docs/docs_modulo7.md)
- [Módulo 8: Deploy e Monitoramento](docs/docs_modulo8.md)

-----

## ▶️ Guia de Início Rápido (Quick Start)

1.  **Configuração do Ambiente** (Veja o [Módulo 0](docs/docs_modulo0.md)):
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
```

### 2.3 backend/.env.example

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
SECRET_KEY=your-secret-key-change-in-production

# Timezone
TZ=America/Sao_Paulo
```

### 2.4 backend/run.py

Crie o arquivo `backend/run.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exitus Backend - Entry Point
Inicia o servidor Flask do backend
"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 2.5 backend/app/__init__.py

Crie o arquivo `backend/app/__init__.py`:

```python
# -*- coding: utf-8 -*-
"""
Exitus Backend - Application Factory
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Habilita CORS
    CORS(app)

    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'exitus-backend'}, 200

    return app
```

### 2.6 backend/Dockerfile

Crie o arquivo `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
# Instala dependências do sistema (incluindo ping e curl)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Expõe porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "run.py"]
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
```

### 3.3 frontend/.env.example

Crie o arquivo `frontend/.env.example`:

```bash
# Backend API Configuration
BACKEND_API_URL=http://exitus-backend:5000

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Timezone
TZ=America/Sao_Paulo
```

### 3.4 frontend/run.py

Crie o arquivo `frontend/run.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exitus Frontend - Entry Point
Inicia o servidor Flask do frontend
"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 3.5 frontend/app/__init__.py

Crie o arquivo `frontend/app/__init__.py`:

```python
# -*- coding: utf-8 -*-
"""
Exitus Frontend - Application Factory
"""

from flask import Flask, render_template_string

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'dev-secret-key'

    # Rota inicial
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

    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'exitus-frontend'}, 200

    return app
```

### 3.6 frontend/Dockerfile

Crie o arquivo `frontend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Expõe porta
EXPOSE 8080

# Comando de inicialização
CMD ["python", "run.py"]
```

## 4. Instalação do Podman

Instale o Podman no Ubuntu:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install podman -y
podman --version
```

Configure subuid/subgid para execução rootless (recomendado):

```bash
echo "$USER:100000:65536" | sudo tee -a /etc/subuid
echo "$USER:100000:65536" | sudo tee -a /etc/subgid
```

## 5. Network e Volumes

Crie a rede dedicada e volumes persistentes:

```bash
# Network
podman network create exitus-net

# Volumes
podman volume create exitus-pgdata
podman volume create exitus-backend-logs
podman volume create exitus-frontend-logs
```

## 6. Build das Imagens Docker

### 6.1 Build Backend
Sempre execute primeiro o build da imagem na pasta backend.
```bash
cd backend
podman build -t exitus-backend:latest .
cd ..
```

### 6.2 Build Frontend
Sempre execute primeiro o build da imagem na pasta frontend.
```bash
cd frontend
podman build -t exitus-frontend:latest .
cd ..
```

## 7. Criação dos 3 Containers

### Container PostgreSQL

```bash
podman run -d --name exitus-db   --network exitus-net   -v exitus-pgdata:/var/lib/postgresql/data   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   docker.io/postgres:15
```

### Container Backend Flask

```bash
podman run -d --name exitus-backend   --network exitus-net   -p 5000:5000   -v ./backend:/app:Z   -v exitus-backend-logs:/app/logs:Z   -e POSTGRES_HOST=exitus-db   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   exitus-backend:latest
```

### Container Frontend Flask

```bash
podman run -d --name exitus-frontend   --network exitus-net   -p 8080:8080   -v ./frontend:/app:Z   -v exitus-frontend-logs:/app/logs:Z   -e BACKEND_API_URL=http://exitus-backend:5000   -e TZ=America/Sao_Paulo   exitus-frontend:latest
```

## 8. Scripts de Gerenciamento

### scripts/setup_containers.sh

```bash
#!/bin/bash
# Configuração inicial dos containers do Exitus

set -e

# Remove todos os containers e volumes do Exitus

echo "=== Cleanup Exitus ==="

echo "Parando containers..."
podman stop exitus-frontend 2>/dev/null || true
podman stop exitus-backend 2>/dev/null || true
podman stop exitus-db 2>/dev/null || true

echo "Removendo containers..."
podman rm exitus-frontend 2>/dev/null || true
podman rm exitus-backend 2>/dev/null || true
podman rm exitus-db 2>/dev/null || true

echo "Containers removidos!"
echo ""
echo "Para remover também volumes e network, execute:"
echo "  podman volume rm exitus-pgdata exitus-backend-logs exitus-frontend-logs"
echo "  podman network rm exitus-net"

echo "=== Setup Exitus - Módulo 0 ==="

# Criar network
echo "Criando network..."
podman network create exitus-net 2>/dev/null || echo "Network já existe"

# Criar volumes
echo "Criando volumes..."
podman volume create exitus-pgdata 2>/dev/null || echo "Volume pgdata já existe"
podman volume create exitus-backend-logs 2>/dev/null || echo "Volume backend-logs já existe"
podman volume create exitus-frontend-logs 2>/dev/null || echo "Volume frontend-logs já existe"

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

# Criar container Backend
echo "Criando container Backend..."
podman run -d --name exitus-backend   --network exitus-net   -p 5000:5000   -v ./backend:/app:Z   -v exitus-backend-logs:/app/logs:Z   -e POSTGRES_HOST=exitus-db   -e POSTGRES_USER=exitus   -e POSTGRES_PASSWORD=exitus123   -e POSTGRES_DB=exitusdb   -e TZ=America/Sao_Paulo   exitus-backend:latest

# Criar container Frontend
echo "Criando container Frontend..."
podman run -d --name exitus-frontend   --network exitus-net   -p 8080:8080   -v ./frontend:/app:Z   -v exitus-frontend-logs:/app/logs:Z   -e BACKEND_API_URL=http://exitus-backend:5000   -e TZ=America/Sao_Paulo   exitus-frontend:latest

echo ""
echo "=== Setup concluído! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
```

### scripts/start_services.sh

```bash
#!/bin/bash
# Inicia todos os serviços do Exitus

echo "Iniciando serviços Exitus..."

podman start exitus-db
echo "PostgreSQL iniciado"
sleep 5

podman start exitus-backend
echo "Backend iniciado"

podman start exitus-frontend
echo "Frontend iniciado"

echo ""
echo "=== Serviços iniciados! ==="
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo ""
podman ps
```

### scripts/stop_services.sh

```bash
#!/bin/bash
# Para todos os serviços do Exitus

echo "Parando serviços Exitus..."

podman stop exitus-frontend exitus-backend exitus-db

echo "=== Serviços parados! ==="
```

### scripts/backup_db.sh

```bash
#!/bin/bash
# Backup do banco de dados PostgreSQL

BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Criando backup do banco de dados..."

podman exec exitus-db pg_dump -U exitus exitusdb > "$BACKUP_DIR/exitusdb_$TIMESTAMP.sql"

echo "Backup criado: $BACKUP_DIR/exitusdb_$TIMESTAMP.sql"
```

Torne os scripts executáveis:

```bash
chmod +x scripts/*.sh
```

## 9. Testes de Comunicação

### Teste 1: PostgreSQL

```bash
podman exec -it exitus-db psql -U exitus -d exitusdb -c "SELECT version();"
```

### Teste 2: Backend Health Check

```bash
curl http://localhost:5000/health
```

### Teste 3: Frontend Health Check

```bash
curl http://localhost:8080/health
```

### Teste 4: Conectividade Backend → Database

```bash
# Se houver ping na imaagem slim
podman exec exitus-backend ping -c 3 exitus-db

# Caso contrário, do container do banco, testar se está respondendo
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT 'PostgreSQL OK' as status;"
```

### Teste 5: Conectividade Frontend → Backend

```bash
# Se houver curl na imagem slim
podman exec exitus-frontend curl http://exitus-backend:5000/health

# Caso contrario, faça:
podman exec exitus-frontend python -c "import requests; r = requests.get('http://exitus-backend:5000/health'); print(r.json())"
```

### Teste 6: Logs dos Containers

```bash
podman logs exitus-db
podman logs exitus-backend
podman logs exitus-frontend
```

### Teste 7: Script completo de tests

```bash
cat > tests/test_module0.sh << 'EOF'
#!/bin/bash
echo "======================================"
echo "  EXITUS - TESTES DO MÓDULO 0"
echo "======================================"
echo ""

echo "1. Backend Health Check (host):"
curl -s http://localhost:5000/health | python3 -m json.tool
echo ""

echo "2. Frontend Health Check (host):"
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""

echo "3. Frontend → Backend (interno):"
podman exec exitus-frontend python -c "import requests; r = requests.get('http://exitus-backend:5000/health'); print(r.json())"
echo ""

echo "4. Backend → Database (conexão):"
podman exec exitus-backend python -c "import socket; socket.create_connection(('exitus-db', 5432), timeout=5); print('✓ Conexão OK')"
echo ""

echo "5. PostgreSQL Query:"
podman exec exitus-db psql -U exitus -d exitusdb -c "SELECT version();" | head -3
echo ""

echo "6. Containers rodando:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "======================================"
echo "  TODOS OS TESTES CONCLUÍDOS!"
echo "======================================"
EOF

chmod +x tests/test_module0.sh
./tests/test_module0.sh
```

## 10. Documentação do Módulo

Este arquivo deve ser salvo como `exitus/docs/docs_modulo0.md` e serve como referência permanente para:

- Recriação do ambiente de desenvolvimento
- Onboarding de novos desenvolvedores
- Auditoria técnica da infraestrutura
- Troubleshooting de problemas de conectividade

### Próximos Passos

Após concluir o Módulo 0, prossiga para o Módulo 1 (Estrutura do Banco de Dados), que detalhará o schema PostgreSQL, migrações e seeds iniciais.

---
