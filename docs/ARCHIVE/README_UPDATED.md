# 🚀 SISTEMA EXITUS - Gestão Inteligente de Investimentos

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-green?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Podman](https://img.shields.io/badge/Podman-Containers-purple?logo=podman)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Sistema completo de análise e gestão de portfolio de investimentos**  
*Multi-mercado (BR/US) • Multi-ativo (Ações, FIIs, ETFs, REITs) • Multi-corretora*

[Instalação](#-guia-de-início-rápido) • [Documentação](#-documentação) • [Arquitetura](#-arquitetura-técnica)

</div>

---

## 📋 Sobre o Projeto

O **Exitus** é uma plataforma completa para gestão de investimentos que permite:

- 📊 **Consolidação de Portfolio**: Visualize todos seus investimentos em um único lugar
- 💰 **Controle de Transações**: Registre compras, vendas e acompanhe histórico
- 🎯 **Buy Signals**: Análise fundamentalista automática (Graham, Gordon, Z-Score)
- 💵 **Gestão de Caixa**: Controle de aportes, resgates e proventos
- 📈 **Cotações em Tempo Real**: Integração com múltiplas APIs (15min delay)
- 🔔 **Alertas Personalizados**: Notificações de metas e eventos importantes
- 📑 **Relatórios Avançados**: Performance, rentabilidade, análise de risco

---

## 🏗️ Arquitetura Técnica

Para máxima portabilidade e desempenho, o **Exitus** adota uma arquitetura em contêineres:

| Componente | Tecnologia | Descrição |
|:-----------|:-----------|:----------|
| **Banco de Dados** | PostgreSQL 15 | 18 tabelas normalizadas, 86+ índices |
| **Backend API** | Flask 3.x + SQLAlchemy | 60+ endpoints RESTful, autenticação JWT |
| **Frontend** | Flask + HTMX + Alpine.js | Interface reativa, SSR, Tailwind CSS |
| **Infraestrutura** | Ubuntu + Podman | Containerização rootless, rede isolada |

---

## 🛠️ Stack Tecnológico

### Backend
- 🐍 **Python 3.11+**
- 🌐 **Flask 3.x** (Web Framework)
- 💾 **SQLAlchemy 2.x** (ORM)
- 🔄 **Alembic** (Migrations)
- 🔐 **JWT** (Autenticação)
- 📊 **Pandas** (Análise de dados)

### Frontend
- ⚡ **HTMX** (Interatividade)
- 🎨 **Tailwind CSS** (Estilização)
- 🔧 **Alpine.js** (JavaScript reativo)
- 📈 **Chart.js** (Gráficos)

### Infraestrutura
- 🐳 **Podman** (Containers)
- 🗄️ **PostgreSQL 15** (Banco de Dados)
- 🚀 **Gunicorn** (WSGI Server)

---

## 📚 Documentação

### 🎯 Checklists de Implementação
- [Módulo 0: Ambiente e Containers](docs/MODULO0_CHECKLIST.md) ✅
- [Módulo 1: Banco de Dados](docs/MODULO1_CHECKLIST.md) ✅
- [Módulo 2: Backend CRUD e Auth](docs/MODULO2_CHECKLIST.md) ✅
- [Módulo 3: Posições e Portfolio](docs/MODULO3_CHECKLIST.md) ✅
- [Módulo 4: Buy Signals](docs/MODULO4_CHECKLIST.md) ✅
- [Módulo 5: Frontend Base](docs/MODULO5_CHECKLIST.md) ✅
- [Módulo 6: Dashboards](docs/MODULO6_CHECKLIST.md) ✅
- [Módulo 7: Relatórios Avançados](docs/MODULO7_ANALISE_ESTRATEGICA.md) 🚧
- [Módulo 7.5: Cotações em Tempo Real](docs/MODULO7.5_CHECKLIST.md) ✅

### 📖 Documentação Técnica
- [Estrutura do Banco de Dados](docs/EXITUS_DB_STRUCTURE.txt) - 18 tabelas, relacionamentos
- [API Reference Completa](docs/API_REFERENCE_COMPLETE.md) - 60+ endpoints documentados
- [Guia de Troubleshooting](docs/TROUBLESHOOTING_GUIDE.md) - Soluções para erros comuns
- [Validação Manual M3](docs/VALIDACAO_M3_MANUAL.md) - Testes de API

### 🛠️ Scripts de Automação
Veja [`scripts/`](scripts/) para todos os scripts disponíveis:
- `setup_containers.sh` - Setup inicial completo
- `start_services.sh` / `stop_services.sh` - Controle de serviços
- `rebuild_restart_exitus-backend.sh` - Rebuild + restart backend
- `exitus_db_doc.sh` - Gerar documentação do banco
- `get_backend_token.sh` - Obter token JWT rapidamente

---

## ▶️ Guia de Início Rápido

### 📋 Pré-requisitos

- Ubuntu 20.04+ (ou Debian/Fedora)
- Podman 4.0+
- Git
- 4GB RAM mínimo
- 10GB espaço em disco

### 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/exitus.git
cd exitus

# 2. Configure os containers
./scripts/setup_containers.sh

# 3. Inicie os serviços
./scripts/start_services.sh

# 4. Popular banco com dados iniciais (opcional)
./scripts/populate_seeds.sh
```

### 🌐 Acessar a Aplicação

- **Frontend (Interface Web)**: http://localhost:3000
- **Backend (API RESTful)**: http://localhost:5000
- **PostgreSQL**: localhost:5432

**Credenciais Padrão:**
- Usuário: `admin`
- Senha: `admin123`

---

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
exitus/
├── backend/               # API Flask + SQLAlchemy
│   ├── app/
│   │   ├── blueprints/   # Endpoints REST (60+)
│   │   ├── models/       # Models SQLAlchemy (18)
│   │   ├── schemas/      # Schemas Marshmallow
│   │   └── services/     # Lógica de negócio
│   ├── alembic/          # Migrations
│   └── tests/            # Testes unitários
│
├── frontend/             # Interface HTMX
│   └── app/
│       ├── routes/       # Rotas Flask
│       ├── templates/    # Templates Jinja2
│       └── static/       # CSS/JS
│
├── scripts/              # Automação (16 scripts)
└── docs/                 # Documentação (22 arquivos)
```

### Comandos Úteis

```bash
# Backend - Logs
podman logs -f exitus-backend

# Backend - Acessar container
podman exec -it exitus-backend bash

# Banco - Conectar ao PostgreSQL
podman exec -it exitus-db psql -U exitus -d exitusdb

# Backend - Criar migration
podman exec -it exitus-backend bash -c "cd /app && alembic revision --autogenerate -m 'Mensagem'"

# Backend - Aplicar migrations
podman exec -it exitus-backend bash -c "cd /app && alembic upgrade head"

# Gerar token JWT
./scripts/get_backend_token.sh
```

---

## 🧪 Testes

```bash
# Testes unitários
podman exec -it exitus-backend bash -c "cd /app && pytest tests/ -v"

# Teste de endpoint específico
podman exec -it exitus-backend bash -c "cd /app && pytest tests/test_posicao.py -v"

# Testes com coverage
podman exec -it exitus-backend bash -c "cd /app && pytest --cov=app tests/"
```

---

## 📊 Funcionalidades Principais

### ✅ Implementado

#### M0 - Ambiente ✅
- [x] Rede Podman isolada
- [x] Container PostgreSQL 15
- [x] Containers Backend/Frontend
- [x] Scripts de automação

#### M1 - Banco de Dados ✅
- [x] 18 tabelas normalizadas
- [x] 86+ índices de performance
- [x] Migrations Alembic
- [x] Seeds com dados iniciais

#### M2 - Backend CRUD ✅
- [x] Autenticação JWT
- [x] CRUD Usuários
- [x] CRUD Corretoras
- [x] CRUD Ativos
- [x] CRUD Transações

#### M3 - Portfolio ✅
- [x] Cálculo de posições
- [x] Movimentações de caixa
- [x] Proventos (dividendos, JCP)
- [x] Eventos corporativos (splits, bonificações)
- [x] Dashboard consolidado

#### M4 - Buy Signals ✅
- [x] Análise fundamentalista
- [x] Margem de segurança (Graham)
- [x] Preço justo (Gordon)
- [x] Z-Score financeiro
- [x] Buy Score ponderado

#### M5 - Frontend Base ✅
- [x] Autenticação web
- [x] Dashboard principal
- [x] Navegação HTMX
- [x] Componentes Alpine.js

#### M6 - Dashboards ✅
- [x] Dashboard de Buy Signals
- [x] Dashboard de Portfolio
- [x] Dashboard de Transações
- [x] Dashboard de Proventos

#### M7.5 - Cotações ✅
- [x] Multi-provider (brapi.dev, yfinance, Alpha Vantage)
- [x] Fallback automático
- [x] Cache PostgreSQL
- [x] Batch requests

### 🚧 Em Desenvolvimento

#### M7 - Relatórios Avançados 🚧
- [ ] Relatórios de performance
- [ ] Análise de risco (Sharpe, Sortino)
- [ ] Projeções de renda passiva
- [ ] Alertas configuráveis
- [ ] Export PDF/Excel

#### M8 - Testes Integrados 📅
- [ ] Testes E2E
- [ ] CI/CD pipeline
- [ ] Testes de carga

#### M9 - Deploy 📅
- [ ] Docker Compose
- [ ] Deploy AWS/Azure
- [ ] Monitoramento (Prometheus/Grafana)

---

## 🔐 Segurança

- ✅ Containers rootless (não-root)
- ✅ Autenticação JWT
- ✅ Passwords hash (bcrypt)
- ✅ Validação de inputs (Marshmallow)
- ✅ CORS configurável
- ✅ SQL Injection protegido (SQLAlchemy)
- ✅ Healthchecks em containers

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adicionar NovaFuncionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Suporte

- **Documentação**: [docs/](docs/)
- **Troubleshooting**: [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md)
- **API Reference**: [docs/API_REFERENCE_COMPLETE.md](docs/API_REFERENCE_COMPLETE.md)
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/exitus/issues)

---

## 🎯 Roadmap

| Fase | Status | Prazo |
|------|--------|-------|
| M0-M6 | ✅ Completo | - |
| M7.5 | ✅ Completo | - |
| M7 | 🚧 Em desenvolvimento | Dez/2025 |
| M8 | 📅 Planejado | Jan/2026 |
| M9 | 📅 Planejado | Fev/2026 |

---

<div align="center">

**Desenvolvido com ❤️ por Elielson**

[![Python](https://img.shields.io/badge/Made%20with-Python-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Powered%20by-Flask-green?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?logo=postgresql)](https://www.postgresql.org/)

</div>
