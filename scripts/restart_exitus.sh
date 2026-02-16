#!/bin/bash
# Reinicia todos os serviços do Exitus chamando os scripts existentes

# Define o diretório onde os scripts estão (mesmo diretório deste arquivo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "    RESTARTING EXITUS SERVICES          "
echo "========================================"
echo ""

# 1. Parar os serviços
bash "$SCRIPT_DIR/stop_exitus.sh"

echo ""
echo "Aguardando 5 segundos para limpeza de sockets..."
sleep 5
echo ""

# 2. Iniciar os serviços
bash "$SCRIPT_DIR/start_exitus.sh"

echo ""
echo "Aguardando 10 segundos para termino das inicializações..."
sleep 10
echo ""

echo ""
echo "========================================"
echo "    RESTART CONCLUÍDO COM SUCESSO!      "
echo "========================================"