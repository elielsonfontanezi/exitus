# 🚀 Exitus - Sistema de Controle e Análise de Investimentos

Sistema **multiusuário enterprise** para gestão completa de portfólio. Oferece suporte a **múltiplos mercados, classes de ativos e corretoras**, todos unificados por uma poderosa **abstração de caixa centralizado**.

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

| Módulo | Título | Link |
| :--- | :--- | :--- |
| **Módulo 0** | Preparação do Ambiente | [docs/docs\_modulo0.md](https://www.google.com/search?q=docs/docs_modulo0.md) |
| **Módulo 1** | Estrutura do Banco de Dados | [docs/docs\_modulo1.md](https://www.google.com/search?q=docs/docs_modulo1.md) |
| **Módulo 2** | Backend - Autenticação e Usuários | [docs/docs\_modulo2.md](https://www.google.com/search?q=docs/docs_modulo2.md) |
| **Módulo 3** | Backend - Gestão de Ativos | [docs/docs\_modulo3.md](https://www.google.com/search?q=docs/docs_modulo3.md) |
| **Módulo 4** | Backend - Transações e Portfólio | [docs/docs\_modulo4.md](https://www.google.com/search?q=docs/docs_modulo4.md) |
| **Módulo 5** | Backend - APIs de Integração | [docs/docs\_modulo5.md](https://www.google.com/search?q=docs/docs_modulo5.md) |
| **Módulo 6** | Frontend - Interface do Usuário | [docs/docs\_modulo6.md](https://www.google.com/search?q=docs/docs_modulo6.md) |
| **Módulo 7** | Testes e Validação | [docs/docs\_modulo7.md](https://www.google.com/search?q=docs/docs_modulo7.md) |
| **Módulo 8** | Deploy e Monitoramento | [docs/docs\_modulo8.md](https://www.google.com/search?q=docs/docs_modulo8.md) |

-----

## ▶️ Guia de Início Rápido (Quick Start)

1.  **Configuração do Ambiente** (Veja o [Módulo 0](https://www.google.com/search?q=docs/docs_modulo0.md)):
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
