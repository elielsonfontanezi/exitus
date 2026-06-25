# Exitus - Sistema de Gestão de Investimentos

**Exitus** é uma plataforma multi-usuário de gestão e análise de investimentos, suportando múltiplos mercados (Brasil, EUA, Europa, Ásia), múltiplas classes de ativos (ações, FIIs, REITs, renda fixa) e múltiplas corretoras com controle unificado de caixa.

##  Quick Start

### Pré-requisitos

- Ubuntu 22.04 LTS (ou similar)
- Podman 4.x instalado
- Git
- 8GB RAM mínimo
- 10GB de espaço em disco

### Instalação

```bash
# Clone o repositório
git clone https://github.com/elielsonfontanezi/exitus.git
cd exitus

# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Edite o .env com suas credenciais (opcional para desenvolvimento)
nano .env
```

### Executar o Sistema

```bash
# Subir os 3 containers
./scripts/start_exitus.sh

# Aguarde ~30 segundos para inicialização completa
```

### Acessar

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000/api
- **Credenciais padrão**: admin / senha123

## � Documentação

Para documentação completa (arquitetura, APIs, roadmap, operações), ver [docs/INDEX.md](docs/INDEX.md).

## � Stack

- **Backend**: Python + Flask + SQLAlchemy
- **Frontend**: Alpine.js + exitus-components.css
- **Database**: PostgreSQL 16
- **Containers**: Podman (rootless)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

---

**Versão**: v0.9.25 | **Atualização**: 25/06/2026

