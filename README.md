# Exitus - Sistema de Controle e Análise de Investimentos

Sistema multiusuário enterprise para gestão de portfólio, suportando múltiplos mercados, classes de ativos e corretoras com abstração de caixa unificado.

## Arquitetura

- **Database**: PostgreSQL 15 (container Podman)
- **Backend**: Flask + SQLAlchemy + APIs RESTful (container Podman)
- **Frontend**: Flask + HTMX + Alpine.js (container Podman)
- **Infraestrutura**: Ubuntu + Podman

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

## Quick Start


# Configurar ambiente (Módulo 0)
./scripts/setup_containers.sh

# Iniciar serviços
./scripts/start_services.sh

# Acessar aplicação
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000


## Tecnologias

- Python 3.11+
- Flask 3.x
- PostgreSQL 15
- SQLAlchemy 2.x
- Podman
- HTMX, Alpine.js
