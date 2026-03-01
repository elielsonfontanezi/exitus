# Scripts do Sistema Exitus

> **Versão:** 1.0  
> **Data:** 28 de Fevereiro de 2026  
> **Status:** Documentação em andamento

---

## 📋 Visão Geral

Esta pasta contém scripts utilitários para operação, desenvolvimento e manutenção do Sistema Exitus.

### 🗂️ Estrutura Atual
```
scripts/
├── backup_db.sh                    # Backup do banco PostgreSQL
├── cleanup_containers.sh           # Limpeza de containers
├── exitus_db_doc.sh                 # Gera documentação do DB
├── generate_api_docs.sh             # Gera documentação da API
├── get_backend_token.sh            # Obtém token JWT
├── populate_seeds.sh               # Popula dados iniciais
├── rebuild_restart_exitus-backend.sh    # Rebuild + restart backend
├── rebuild_restart_exitus-frontend.sh   # Rebuild + restart frontend
├── restart_backend.sh               # Restart rápido backend
├── restart_exitus.sh               # Restart todos serviços
├── restart_frontend.sh              # Restart rápido frontend
├── restore_db.sh                    # Restore do banco
├── setup_containers.sh              # Setup inicial containers
├── setup_env.sh                     # Configura ambiente
├── start_exitus.sh                  # Inicia todos serviços
├── startexitus-local.sh             # Start local
├── stop_exitus.sh                   # Para todos serviços
└── exitus.sh                        # Script unificado (NOVO)

# 🗑️ Scripts Removidos
├── cleanup_duplicates.sh           # REMOVIDO: complexidade desnecessária
├── restore_complete.sh              # REMOVIDO: função crítica mal implementada
├── validate_docs.sh                 # REMOVIDO: intenção obsoleta
```

---

## 🚀 Scripts Principais

### Container Management

#### `rebuild_restart_exitus-backend.sh` ⭐
**Rebuild completo + restart do backend**
```bash
./scripts/rebuild_restart_exitus-backend.sh
```
- ✅ Libera porta 5000
- ✅ Build sem cache
- ✅ Remove container antigo
- ✅ Inicia com volumes e env
- ✅ Health check automático

#### `rebuild_restart_exitus-frontend.sh` ⭐
**Rebuild completo + restart do frontend**
```bash
./scripts/rebuild_restart_exitus-frontend.sh
```
- ✅ Stop e remove container
- ✅ Rebuild da imagem
- ✅ Inicia com configuração correta
- ✅ Valida funcionamento

#### `setup_containers.sh` ⭐
**Setup inicial do ambiente**
```bash
./scripts/setup_containers.sh
```
- ✅ Remove containers antigos
- ✅ Cria network exitus-net
- ✅ Setup volumes
- ✅ Inicia todos containers

### Operações Simples (Podem ser melhoradas)

#### `start_exitus.sh` 
**Inicia todos serviços**
```bash
./scripts/start_exitus.sh
```
❌ **Problemas:** Sem validação, sem health check

#### `stop_exitus.sh`
**Para todos serviços**
```bash
./scripts/stop_exitus.sh
```
❌ **Problemas:** Sem validação, sem confirmação

#### `restart_backend.sh`
**Restart rápido backend**
```bash
./scripts/restart_backend.sh
```
❌ **Problemas:** Apenas restart, sem rebuild

---

## 🗄️ Scripts de Banco de Dados

### `exitus_db_doc.sh` ⭐
**Gera documentação completa do DB**
```bash
./scripts/exitus_db_doc.sh
```
- ✅ Conecta no container exitus-db
- ✅ Extrai estrutura completa (tabelas, colunas, PKs, FKs, constraints)
- ✅ Gera arquivo `EXITUS_DB_STRUCTURE.txt`
- ✅ Valida se container está rodando

**Output:** `exitus_db_structure_YYYYMMDD_HHMMSS.txt`

### `backup_db.sh` ⭐
**Backup do banco PostgreSQL**
```bash
./scripts/backup_db.sh
```
- ✅ Dump completo do banco
- ✅ Compressão gzip
- ✅ Timestamp no nome

### `restore_db.sh` ⭐
**Restore do banco PostgreSQL**
```bash
./scripts/restore_db.sh [arquivo_backup]
```
- ✅ Valida arquivo de backup
- ✅ Stop containers
- ✅ Restore completo
- ✅ Restart serviços

### `populate_seeds.sh` ⭐
**Popula dados iniciais**
```bash
./scripts/populate_seeds.sh
```
- ✅ Usuários seed
- ✅ Ativos básicos
- ✅ Dados de teste

---

## 🔧 Scripts de Desenvolvimento

### `get_backend_token.sh` ⭐
**Obtém token JWT para testes**
```bash
./scripts/get_backend_token.sh
```
- ✅ Login automático
- ✅ Retorna token Bearer
- ✅ Pronto para usar em APIs

### `generate_api_docs.sh` ⭐
**Gera documentação da API**
```bash
./scripts/generate_api_docs.sh
```
- ✅ Varre endpoints
- ✅ Gera documentação
- ✅ Formato estruturado

### `cleanup_duplicates.sh`
**Remove duplicatas do DB**
```bash
./scripts/cleanup_duplicates.sh
```
- ⚠️ **Cuidado:** Operação destrutiva
- ✅ Remove registros duplicados
- ✅ Mantém mais recente

---

## 📊 Scripts de Manutenção

### `cleanup_containers.sh`
**Limpeza de containers**
```bash
./scripts/cleanup_containers.sh
```
- ✅ Remove containers parados
- ✅ Limpa imagens órfãs
- ✅ Libera espaço

### `validate_docs.sh`
**Valida documentação**
```bash
./scripts/validate_docs.sh
```
- ✅ Verifica links
- ✅ Valida estrutura
- ✅ Reporta erros

---

## 🔄 Scripts Redundantes (Melhorar)

### Problemas Identificados
1. **Múltiplos scripts para mesma função:**
   - `start_exitus.sh` + `startexitus-local.sh`
   - `restart_backend.sh` + `restart_exitus.sh`
   - `stop_exitus.sh` + parciais individuais

2. **Scripts sem validação:**
   - Sem checar se containers existem
   - Sem tratamento de erros
   - Sem health checks

3. **Inconsistência:**
   - Alguns com cores, outros sem
   - Formatos diferentes de output
   - Códigos de retorno inconsistentes

---

## 🎯 Proposta de Reorganização

### Novo Script Unificado
```bash
# Substituir vários por um único
scripts/exitus.sh [comando] [alvo]

# Exemplos:
./scripts/exitus.sh start all          # Inicia tudo
./scripts/exitus.sh rebuild backend    # Rebuild backend
./scripts/exitus.sh restart frontend  # Restart frontend
./scripts/exitus.sh stop all           # Para tudo
./scripts/exitus.sh status             # Status completo
./scripts/exitus.sh logs backend       # Logs do backend
```

### Estrutura Proposta
```
scripts/
├── exitus.sh                    # Script unificado principal
├── db/                          # Scripts de banco
│   ├── backup.sh
│   ├── restore.sh
│   ├── doc.sh
│   └── seed.sh
├── dev/                         # Scripts de desenvolvimento
│   ├── token.sh
│   ├── logs.sh
│   └── health.sh
└── maintenance/                 # Scripts de manutenção
    ├── cleanup.sh
    └── validate.sh
```

---

## 📋 Próximos Passos

1. ✅ **Documentação completa** (este arquivo)
2. 📋 **Criar script unificado** `exitus.sh`
3. 📋 **Reorganizar subdiretórios**
4. 📋 **Melhorar scripts existentes**
5. 📋 **Adicionar help integrado**
6. 📋 **Testar todos os scripts**

---

## 🚨 Notas Importantes

- **Sempre** verificar se containers estão rodando antes de operações
- **Backup** antes de operações destrutivas
- **Logs** são essenciais para debug
- **Health checks** garantem funcionamento

---

*Última atualização: 28/02/2026*
