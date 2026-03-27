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
├── update_db_structure.sh           # Atualiza docs/EXITUS_DB_STRUCTURE.txt
├── generate_api_docs.sh             # Gera documentação da API
├── get_backend_token.sh            # Obtém token JWT
├── populate_seeds.sh               # Popula dados iniciais
├── rebuild_restart_exitus-backend.sh    # Rebuild + restart backend
├── rebuild_restart_exitus-frontend.sh   # Rebuild + restart frontend
├── restart_backend.sh               # Restart rápido backend
├── restart_exitus.sh               # Restart todos serviços
├── reset_and_seed.sh              # Reset e seed controlado (wrapper para reset_and_seed.py)
├── restore_db.sh                    # Restore do banco
├── setup_containers.sh              # Setup inicial containers
├── setup_env.sh                     # Configura ambiente
├── start_exitus.sh                  # Inicia todos serviços
├── repair_containers.sh             # Health check + repair containers
├── stop_exitus.sh                   # Para todos serviços
├── exitus.sh                        # Script unificado (NOVO)
├── recovery_manager.sh              # Orquestrador de recovery (NOVO)
├── validate_recovery.sh             # Validações pós-operação (NOVO)
├── rollback_recovery.sh             # Rollback automático (NOVO)
└── recovery_dashboard.sh            # Interface TUI interativa (NOVO)

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
- ✅ Recria com volumes padrão (`./backend:/app:Z`)
- ✅ Health check automático

#### `rebuild_restart_exitus-frontend.sh` ⭐
**Rebuild completo + restart do frontend**
```bash
./scripts/rebuild_restart_exitus-frontend.sh
```
- ✅ Stop e remove container
- ✅ Rebuild da imagem
- ✅ Inicia com volumes padrão (`./frontend:/app:Z`)
- ✅ Health check automático
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

#### `repair_containers.sh` ⭐
**Health check + repair dos containers**
```bash
./scripts/repair_containers.sh
```
- ✅ Verifica status de cada container (DB, Backend, Frontend)
- ✅ Health checks específicos (psql, /health endpoints)
- ✅ Reinicia automaticamente se health falhar
- ✅ Aguarda container ficar saudável (timeout 40s)
- ✅ Robusto com `set -euo pipefail`

**Diferença de `start_exitus.sh`:**
- `start_exitus.sh`: Apenas inicia containers parados
- `repair_containers.sh`: Analisa + corrige + garante funcionamento

---

## 🗄️ Scripts de Banco de Dados

### `update_db_structure.sh` ⭐
**Atualiza `docs/EXITUS_DB_STRUCTURE.txt` com o schema atual do banco**
```bash
./scripts/update_db_structure.sh
```
- ✅ Conecta no container exitus-db
- ✅ Extrai estrutura completa (tabelas, colunas, PKs, FKs, constraints)
- ✅ Gera arquivo `EXITUS_DB_STRUCTURE.txt`
- ✅ Valida se container está rodando

**Output:** sobrescreve diretamente `docs/EXITUS_DB_STRUCTURE.txt` (sem cópia com timestamp)

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

## � Scripts de Recovery (NOVO - EXITUS-RECOVERY-001)

### `recovery_manager.sh` ⭐⭐⭐
**Orquestrador principal do sistema de recovery**
```bash
./scripts/recovery_manager.sh [modo] [opções]

# Exemplos:
./scripts/recovery_manager.sh backup --type=full
./scripts/recovery_manager.sh restore --from=backup_20260301.sql
./scripts/recovery_manager.sh reset --mode=full
./scripts/recovery_manager.sh validate --check=integrity
./scripts/recovery_manager.sh dashboard
```
- ✅ **Backup:** Full, incremental, agendado
- ✅ **Restore:** Com validação e rollback automático
- ✅ **Reset:** Full, minimal, custom
- ✅ **Validate:** Integridade, health, performance
- ✅ **Dashboard:** Interface TUI interativa
- ✅ **Enterprise:** Compressão, checksum, metadados

### `validate_recovery.sh` ⭐⭐
**Validações pós-operação do sistema**
```bash
./scripts/validate_recovery.sh [tipo]

# Tipos:
./scripts/validate_recovery.sh full      # Validação completa
./scripts/validate_recovery.sh database  # Integridade do DB
./scripts/validate_recovery.sh health    # Health checks
./scripts/validate_recovery.sh endpoints # Endpoints críticos
```
- ✅ **Integridade do banco:** Tabelas, constraints, dados
- ✅ **Health checks:** Database, backend, frontend
- ✅ **Endpoints:** API críticas funcionando
- ✅ **Consistência:** Dados órfãos, saldos
- ✅ **Performance:** Tempos de resposta, memória
- ✅ **Relatórios:** JSON com métricas detalhadas

### `rollback_recovery.sh` ⭐⭐
**Rollback automático de operações**
```bash
./scripts/rollback_recovery.sh [operação]

# Operações:
./scripts/rollback_recovery.sh list                    # Listar pontos
./scripts/rollback_recovery.sh rollback --to=rollback_id
./scripts/rollback_recovery.sh auto                     # Última operação
./scripts/rollback_recovery.sh cleanup --days=7        # Limpar antigos
```
- ✅ **Pontos de rollback:** Automáticos pré-operação
- ✅ **Validação:** Checksum, integridade
- ✅ **Segurança:** Backup pré-rollback
- ✅ **Recuperação:** Auto-recuperação em falhas
- ✅ **Gerenciamento:** Limpeza automática

### `recovery_dashboard.sh` ⭐⭐⭐
**Interface TUI interativa para operações**
```bash
./scripts/recovery_dashboard.sh
```
- ✅ **Interface amigável:** Menu visual intuitivo
- ✅ **Status em tempo real:** Containers, backups, disco
- ✅ **Operações guiadas:** Backup, restore, reset, validate
- ✅ **Logs integrados:** Visualização de logs
- ✅ **Configurações:** Preferências do sistema
- ✅ **Navegação:** Teclas de atalho, help integrado

---

## �🔧 Scripts de Desenvolvimento

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
