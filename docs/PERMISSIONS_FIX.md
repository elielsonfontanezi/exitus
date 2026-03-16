# 🔧 Guia de Correção de Permissões - Exitus

## 🎯 Problema

Ao editar arquivos no Windsurf (Windows) através do WSL, os arquivos são criados com UID/GID diferentes do usuário dentro dos containers Podman, causando erros de permissão.

### Sintomas:
- Arquivos criados/editados no Windsurf têm owner `100999` (Windows UID)
- Container espera owner `exitus` (UID 1000)
- Erros: "Permission denied", "Operation not permitted"
- Containers não conseguem ler/escrever arquivos montados

## 🔧 Solução Implementada

### 1. **UID/GID Dinâmico no Container**
- Dockerfile modificado para aceitar `USER_UID` e `USER_GID` como environment variables
- Script `docker-entrypoint.sh` ajusta o usuário do container em runtime
- Containers criados com UID/GID do usuário host

### 2. **Scripts Atualizados**
- `setup_containers.sh`: Passa UID/GID do usuário para os containers
- `fix_permissions.sh`: Script único para corrigir tudo

### 3. **Como Funciona**
```bash
# No setup_containers.sh
USER_UID=$(id -u)  # Pega UID do usuário WSL
USER_GID=$(id -g)  # Pega GID do usuário WSL

# No container
podman run -e USER_UID=$USER_UID -e USER_GID=$USER_GID ...

# No docker-entrypoint.sh (dentro do container)
usermod -u $USER_UID exitus  # Ajusta UID do usuário exitus
groupmod -g $USER_GID exitus  # Ajusta GID do usuário exitus
```

## 🚀 Como Usar

### Para Novas Instalações:
```bash
./scripts/setup_containers.sh
```
O script já configura UID/GID automaticamente.

### Para Corrigir Instalação Existente:
```bash
./scripts/fix_permissions.sh
```
Este script:
1. Para e remove containers existentes
2. Reconstrói as imagens com novo Dockerfile
3. Recria containers com UID/GID corretos
4. Mantém dados do PostgreSQL

## 📁 Arquivos Modificados

1. **backend/Dockerfile**
   - Adicionado suporte a UID/GID dinâmico
   - Entrypoint configurado para `docker-entrypoint.sh`

2. **backend/docker-entrypoint.sh** (novo)
   - Ajusta UID/GID em runtime
   - Corrige permissões dos volumes

3. **scripts/setup_containers.sh**
   - Passa UID/GID do usuário como environment variables

4. **scripts/fix_permissions.sh** (novo)
   - Script completo para corrigir permissões

## 🎯 Benefícios

- ✅ **Sem mais erros de permissão** ao editar no Windsurf
- ✅ **UID/GID automático** - não precisa configurar manualmente
- ✅ **Volumes funcionam** corretamente
- ✅ **Desenvolvimento fluido** entre Windows e containers

## 🔍 Verificação

Para verificar se está funcionando:
```bash
# Verificar UID/GID no host
id -u && id -g

# Verificar UID/GID no container
podman exec exitus-backend id -u exitus
podman exec exitus-backend id -g exitus

# Verificar permissões dos arquivos
podman exec exitus-backend ls -la /app/app/models/
```

Os valores devem ser iguais!

## 📝 Notas Técnicas

- O problema ocorre porque WSL mapeia usuários Windows com UIDs altos (ex: 100999)
- Por padrão, containers usam UID 1000 para o usuário não-root
- A solução ajusta o usuário do container para match com o host
- Volume mount `:Z` mantido para SELinux/AppArmor

## 🔄 Manutenção

- Ao adicionar novos containers, replicar o pattern de `USER_UID`/`USER_GID`
- O `fix_permissions.sh` pode ser executado sempre que necessário
- Não é necessário executar toda vez, apenas quando houver problemas de permissão

---

*Última atualização: 16/03/2026*  
*Problema resolvido: UID/GID mismatch entre Windows WSL e containers Podman*
