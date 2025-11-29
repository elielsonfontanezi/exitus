#!/bin/bash

# --- Configurações ---
DB_CONTAINER="exitus-db"
APP_CONTAINERS=("exitus-backend" "exitus-frontend")
DB_NAME="exitusdb"
DB_USER="exitus"
POSTGRES_MASTER_DB="postgres" # Banco de dados para se conectar e executar DROP/CREATE


## --- FUNÇÕES AUXILIARES ---

# Função para checar o status de um container
check_container_status() {
    local container_name=$1
    if podman inspect --format '{{.State.Running}}' "$container_name" 2>/dev/null | grep -q "true"; then
        echo "✅ $container_name está ONLINE."
        return 0
    else
        echo "❌ $container_name está OFFLINE."
        return 1
    fi
}

# Função para parar containers da aplicação
stop_app_containers() {
    echo "--- 🛑 Parando containers da aplicação... ---"
    for container in "${APP_CONTAINERS[@]}"; do
        if check_container_status "$container"; then
            echo "Parando $container..."
            podman stop "$container"
        fi
    done
    echo "Containers da aplicação parados."
}

# Função para iniciar containers da aplicação
start_app_containers() {
    echo "--- 🚀 Iniciando containers da aplicação... ---"
    for container in "${APP_CONTAINERS[@]}"; do
        echo "Iniciando $container..."
        podman start "$container"
    done
}


## --- LÓGICA PRINCIPAL DO SCRIPT ---

# 1. Checa o argumento de entrada
if [ -z "$1" ]; then
    echo "ERRO: O nome do arquivo de dump é obrigatório."
    echo "Uso: $0 <caminho/para/arquivo.sql>"
    exit 1
fi

DUMP_FILE="$1"

if [ ! -f "$DUMP_FILE" ]; then
    echo "ERRO: Arquivo de dump não encontrado: $DUMP_FILE"
    exit 1
fi

echo "Arquivo de Dump Selecionado: $DUMP_FILE"

# 2. Para os containers da aplicação
stop_app_containers

# 3. Verifica o status do container do banco de dados
echo "--- 🔎 Verificando status do container do banco de dados ($DB_CONTAINER)... ---"
if ! check_container_status "$DB_CONTAINER"; then
    echo "ERRO: O container do banco de dados ($DB_CONTAINER) não está rodando. Por favor, inicie-o primeiro."
    exit 1
fi


# 4. Drop e Create do Banco de Dados
echo "--- 🗑️ Limpando e recriando o banco de dados ($DB_NAME)... ---"

# Drop do banco de dados
echo "Deletando banco de dados existente ($DB_NAME)..."
# Conecta ao master DB para manipular o DB alvo
podman exec -it "$DB_CONTAINER" psql -U "$DB_USER" -d "$POSTGRES_MASTER_DB" -c "DROP DATABASE IF EXISTS $DB_NAME WITH (FORCE);"

if [ $? -ne 0 ]; then
    echo "ERRO ao deletar o banco de dados $DB_NAME."
    exit 1
fi

# Criação do novo banco de dados
echo "Criando novo banco de dados ($DB_NAME)..."
podman exec -it "$DB_CONTAINER" psql -U "$DB_USER" -d "$POSTGRES_MASTER_DB" -c "CREATE DATABASE $DB_NAME;"

if [ $? -ne 0 ]; then
    echo "ERRO ao criar o banco de dados $DB_NAME."
    exit 1
fi

echo "Banco de dados $DB_NAME limpo e recriado com sucesso."


# 5. Execução do Restore
echo "--- 📥 Iniciando o Restore do arquivo $DUMP_FILE... ---"
cat "$DUMP_FILE" | podman exec -i "$DB_CONTAINER" psql -U "$DB_USER" "$DB_NAME"

if [ $? -eq 0 ]; then
    echo "✅ RESTORE CONCLUÍDO COM SUCESSO!"
else
    echo "❌ ERRO DURANTE O RESTORE. Verifique os logs."
fi


# 6. Lista a tabela 'usuario'
echo "--- 📝 Conteúdo da Tabela 'usuario' após o Restore ---"
podman exec -it "$DB_CONTAINER" psql -U "$DB_USER" "$DB_NAME" -c "SELECT id, username, email FROM usuario LIMIT 10;"


# 7. Inicia os containers da aplicação
start_app_containers

# 8. Lista o status de todos os containers
echo "--- 📊 Status de Todos os Containers ---"
podman ps -a

echo
echo

cat << 'EOF'
# ========================================================
# GARANTA QUE AS SEEDS ESTEJAM POPULADAS NA BASE DE DADOS:
# 
# EXECUTE: exitus/scirpts/populate_seeds.sh
# ========================================================
EOF
