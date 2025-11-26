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

1.  **Configuração do Ambiente** (Veja o [Módulo 0](docs/modulo0_ambiente.md)):
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
